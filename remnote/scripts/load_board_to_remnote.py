#!/usr/bin/env python3
"""Load today's active Linear board view into a new RemNote summary doc and
reference it from today's daily note.

Defaults
--------
- Source board: working_on view marked active in
    /Users/han/project/life/linear_board_view/public/data/working_on/views.json
- Doc title: <YYMMDD><next-letter>_<slug>
    * YYMMDD = today, local time
    * next-letter = a / b / c / ... — first unused among top-level rems whose
      key matches  ^YYMMDD[a-z]_   (so two runs on the same day don't collide)
    * slug default 'task_board'
- Destination: today's daily note. Section auto-picked by current hour:
    * < 12       -> 早
    * 12 - 17    -> 下午
    * >= 18      -> 晚上
    Falls back to the daily-note root if the section rem isn't found.

Usage
-----
    python3 load_board_to_remnote.py
    python3 load_board_to_remnote.py --slug grok_review --section 早

Requires sync_server (9321) up + plugin polling. See `remnote` SKILL.md preflight.
"""

import argparse
import json
import re
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# `sync_client` sets NO_PROXY=* on import — without that, requests/urllib calls
# to 127.0.0.1 traverse the system HTTP proxy and 502.
sys.path.insert(0, '/Users/han/project/life/notes')
sys.path.insert(0, '/Users/han/project/life/notes/remnote-sync-plugin')
import requests  # noqa: E402
import sync_client  # noqa: E402,F401  side-effect-sets NO_PROXY

DB = '/Users/han/remnote/remnote-62403c0f38b1150016221e9d/remnote.db'
SERVER = 'http://127.0.0.1:9321'
BOARD_DIR = Path('/Users/han/project/life/linear_board_view/public/data')


# ----- bridge ---------------------------------------------------------------

def wait_drained(timeout=15):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if not requests.get(SERVER + '/pending', timeout=2).json()['commands']:
            return
        time.sleep(0.3)
    raise TimeoutError('/pending did not drain')


def find_rem_once(parent_id, text):
    """One-shot SQLite lookup for a rem by (parent, key[0])."""
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        if parent_id is None:
            q = ("SELECT _id FROM quanta WHERE json_extract(doc,'$.parent') IS NULL "
                 "AND json_extract(doc,'$.key[0]') = ? "
                 "ORDER BY json_extract(doc,'$.m') DESC LIMIT 1")
            row = conn.execute(q, (text,)).fetchone()
        else:
            q = ("SELECT _id FROM quanta WHERE json_extract(doc,'$.parent') = ? "
                 "AND json_extract(doc,'$.key[0]') = ? "
                 "ORDER BY json_extract(doc,'$.m') DESC LIMIT 1")
            row = conn.execute(q, (parent_id, text)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def find_rem(parent_id, text, timeout=10):
    """find_rem_once with retry — covers post-ack WAL visibility lag."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        rid = find_rem_once(parent_id, text)
        if rid:
            return rid
        time.sleep(0.4)
    return None


def post(endpoint, payload):
    return requests.post(SERVER + endpoint, json=payload, timeout=5).json()


def create_text(text, parent_id=None):
    """Idempotent: reuse an existing match under the same parent."""
    existing = find_rem_once(parent_id, text)
    if existing:
        return existing
    body = {'text': text}
    if parent_id is not None:
        body['parentId'] = parent_id
    post('/create', body)
    wait_drained()
    rid = find_rem(parent_id, text)
    if not rid:
        raise RuntimeError(f'lost create: text={text!r} parent={parent_id}')
    return rid


def create_reference(target_id, parent_id):
    """Create a child rem whose key is a single reference to target_id.

    The plugin does `setText([cmd.text])`; passing `text` as a richText element
    {i:'q',_id:'...'} produces a clickable [[…]] reference, not literal text.
    """
    post('/create', {'text': {'i': 'q', '_id': target_id}, 'parentId': parent_id})
    wait_drained()


# ----- auto-numbered YYMMDDx_ title -----------------------------------------

def today_yymmdd():
    return datetime.now().strftime('%y%m%d')


def next_letter_today(yymmdd):
    """First unused letter a-z among top-level rems whose key matches ^YYMMDD[a-z]_."""
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        rows = conn.execute(
            "SELECT json_extract(doc,'$.key[0]') FROM quanta "
            "WHERE json_extract(doc,'$.parent') IS NULL "
            "AND json_extract(doc,'$.key[0]') LIKE ?",
            (f'{yymmdd}%',)
        ).fetchall()
    finally:
        conn.close()
    used = set()
    pat = re.compile(rf'^{yymmdd}([a-z])_')
    for (k,) in rows:
        m = pat.match(k or '')
        if m:
            used.add(m.group(1))
    for c in 'abcdefghijklmnopqrstuvwxyz':
        if c not in used:
            return c
    raise RuntimeError(f'all 26 letters taken for {yymmdd} — switch slug or date')


# ----- daily note helpers ---------------------------------------------------

def find_today_daily_doc():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        row = conn.execute(
            "SELECT _id FROM quanta WHERE json_extract(doc,'$.key[0]') = ? LIMIT 1",
            (today,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def auto_section_name():
    h = datetime.now().hour
    if h < 12:
        return '早'
    if h < 18:
        return '下午'
    return '晚上'


# ----- board parsing --------------------------------------------------------

def load_active_board():
    views = json.loads((BOARD_DIR / 'working_on' / 'views.json').read_text())
    active = views['activeId']
    path = BOARD_DIR / 'working_on' / f'{active}.json'
    return json.loads(path.read_text()), views


def load_issues_snapshot():
    return json.loads((BOARD_DIR / 'issues.json').read_text())


def summarize_board(board, snapshot):
    """Return (todo_tree, done_list).

    todo_tree: nested list  [(title, [(title, [...]), ...]), ...]
    done_list: flat list of done-marked node texts (Linear "Done"/"Cancelled"
               state types also collapse here).
    """
    notes = {n['id']: n for n in board['noteNodes']}
    issues = {i['id']: i for i in snapshot.get('issues', [])}
    children = defaultdict(list)
    parents = {}
    for e in board.get('edges', []):
        children[e['source']].append(e['target'])
        parents[e['target']] = e['source']
    all_ids = list(notes) + list(board.get('issueMembers', {}))
    roots = [nid for nid in all_ids if nid not in parents]

    def label(nid):
        if nid in notes:
            body = (notes[nid].get('body') or '').strip()
            return body, bool(notes[nid].get('done'))
        if nid in issues:
            i = issues[nid]
            state = (i.get('state') or {}).get('name', '?')
            t = f"[{i.get('identifier')}] {i.get('title')}"
            return t, state in ('Done', 'Cancelled')
        return '', False

    def flatten(text):
        if not text:
            return ''
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return ''
        if len(lines) == 1:
            return lines[0]
        return lines[0] + ' — ' + ' / '.join(lines[1:])

    done_list = []
    todo_tree = []

    def collect_done(nid):
        text, _ = label(nid)
        flat = flatten(text)
        if flat:
            done_list.append(flat)
        for c in children.get(nid, []):
            collect_done(c)

    def walk(nid, into):
        text, done = label(nid)
        if done:
            collect_done(nid)
            return
        flat = flatten(text)
        if not flat:
            # empty body — flatten its children into the same level
            for c in children.get(nid, []):
                walk(c, into)
            return
        sub = []
        for c in children.get(nid, []):
            walk(c, sub)
        into.append((flat, sub))

    for r in roots:
        walk(r, todo_tree)

    return todo_tree, done_list


# ----- main -----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--slug', default='task_board',
                    help="slug after the YYMMDD<letter>_ prefix (default: task_board)")
    ap.add_argument('--section', default='auto',
                    choices=['auto', '早', '下午', '晚上', 'root'],
                    help='daily-note section for the [[ref]] (default: auto by hour)')
    ap.add_argument('--board',
                    help='explicit board view JSON path (default: working_on active)')
    args = ap.parse_args()

    if requests.get(SERVER + '/health', timeout=2).json().get('status') != 'ok':
        sys.exit(f'sync_server not reachable at {SERVER}')

    yymmdd = today_yymmdd()
    letter = next_letter_today(yymmdd)
    title = f'{yymmdd}{letter}_{args.slug}'
    print(f'doc title: {title}')

    if args.board:
        board = json.loads(Path(args.board).read_text())
        view_label = args.board
    else:
        board, views = load_active_board()
        active = next(v for v in views['views'] if v['id'] == views['activeId'])
        view_label = active['name']
    snapshot = load_issues_snapshot()
    todo_tree, done_list = summarize_board(board, snapshot)
    print(f'board: {view_label}  |  todo branches: {len(todo_tree)}  '
          f'|  done items: {len(done_list)}')

    root_id = create_text(title)
    print(f'root id = {root_id}')

    def write_tree(tree, parent_id):
        for parent_text, kids in tree:
            pid = create_text(parent_text, parent_id=parent_id)
            write_tree(kids, pid)

    write_tree(todo_tree, root_id)
    if done_list:
        done_pid = create_text('今日已完成', parent_id=root_id)
        for d in done_list:
            create_text(d, parent_id=done_pid)

    daily_id = find_today_daily_doc()
    if not daily_id:
        print("WARN: today's daily note not found — skipping reference insertion")
        return
    if args.section == 'auto':
        section_name = auto_section_name()
    elif args.section == 'root':
        section_name = None
    else:
        section_name = args.section
    target = daily_id
    if section_name:
        sid = find_rem_once(daily_id, section_name)
        if sid:
            target = sid
        else:
            print(f'WARN: section {section_name!r} not found — referencing under daily-note root')

    create_reference(root_id, target)
    print(f'[[{title}]] inserted under rem {target}')


if __name__ == '__main__':
    main()
