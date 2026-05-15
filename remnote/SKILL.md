---
name: remnote
description: Read RemNote rems and append children, create new top-level docs, insert clickable [[references]], set a RemNote tag on a rem (write `tp` directly — e.g. tag a doc with `[[7a1 -- person]]`), or load a Linear board view snapshot into a new RemNote summary doc linked from today's daily note (auto-numbered `YYMMDD<letter>_<slug>` titles, section auto-picked by hour), via the sync_server+plugin bridge at /Users/han/project/life/notes on this machine. Use when the user wants to read / dump / search a RemNote rem (IDs often look like '6s3c - grok skill'), append a child rem, create a new RemNote doc, insert a [[link]] in a daily-note section, tag a rem with another rem (RemNote-native tag chip, distinct from a reference child), or load today's Linear board into RemNote. Do NOT trigger for the Flomo→RemNote or RemNote→Todoist batch sync CLIs, for plugin source work (webpack/TypeScript), or for non-RemNote note systems (Obsidian/Apple Notes/Bear/flomo/markdown).
---

# Remnote

Programmatic read/write against the user's RemNote knowledge base on this Mac. RemNote stores everything as `quanta` rows in a local SQLite DB; you read SQLite directly (read-only mode works while RemNote runs) and write through a polling bridge: a Python `sync_server` queues commands and a RemNote plugin (loaded in-app) executes them via the RemNote SDK.

The bridge exists because direct SQLite writes bypass RemNote's frontend state and produce rems missing the `f` fractional-index field — they appear in the wrong place or not at all until restart. Going through the plugin lets the SDK assign `f` correctly and refresh the UI live.

**Host pins.** Paths in this skill are concrete because this is the user's machine; do not parameterize them on the fly.

- Repo: `/Users/han/project/life/notes`
- DB: `/Users/han/remnote/remnote-62403c0f38b1150016221e9d/remnote.db`
- Owner ID: `62403c0f38b1150016221e9d`
- Sync server: `http://127.0.0.1:9321`
- Plugin dev server (webpack): `http://localhost:8080`
- Edit Later powerup ID: `bh4pQnTdKTZkEQmWk`

## Quick start

**Read** (no setup needed — RemNote can be running):

```python
import sys; sys.path.insert(0, '/Users/han/project/life/notes')
from remnote.reader_live import RemNoteReaderLive

r = RemNoteReaderLive('/Users/han/remnote/remnote-62403c0f38b1150016221e9d/remnote.db')
try:
    hits = r.search_rem_by_name('6s3c - grok skill')
    target = hits[0]['id']
    for c in sorted(r.get_rem_children(target), key=lambda c: c['doc'].get('f') or ''):
        print(r.format_key(c['doc'].get('key', [])))
finally:
    r.close()
```

**Write** (requires sync_server up + plugin polling — see preflight below):

```python
import sys; sys.path.insert(0, '/Users/han/project/life/notes/remnote-sync-plugin')
from sync_client import RemNoteSyncClient

c = RemNoteSyncClient()
assert c.is_server_running()
c.create_rem('hello from opus', parent_id='bL44huKGMvOetgVEk')   # append child
c.create_rem('hello from opus')                                  # new top-level doc (auto Edit Later)
```

After enqueueing, poll `GET /pending` until the queue is empty — that is the plugin's ACK. ≤2 s under normal conditions.

## Workflows

### 1. Preflight (before any write)

The bridge has two moving parts that must both be live:

```bash
curl -sS --max-time 2 http://127.0.0.1:9321/health    # sync_server (should return {"status":"ok"})
curl -sS --max-time 2 -o /dev/null -w "%{http_code}\n" http://localhost:8080   # plugin dev server (200 if up)
```

If either is down, **do not use launchctl** — the bundled `remnote-service.sh install` plists point to a stale path (`/Users/han/project/notes/...` without `life/`) and exit 78. Start manually:

```bash
cd /Users/han/project/life/notes/remnote-sync-plugin
nohup /Users/han/miniconda3/bin/python3 sync_server.py \
    > /tmp/remnote-sync-server.log 2> /tmp/remnote-sync-server.error.log &
nohup /usr/local/bin/npm run dev \
    > /tmp/remnote-plugin-dev.log 2> /tmp/remnote-plugin-dev.error.log &
```

Webpack takes ~10–15 s to listen. After it does, the plugin **already loaded in RemNote** may need to be toggled (Settings → Plugins → Disable then Enable) to repull the bundle. If commands sit in `/pending` past ~3 s, ask the user to toggle.

The `tp` field carries powerups; for the parent rem of a fresh top-level doc you'll see `bh4pQnTdKTZkEQmWk` — that's RemNote's "Edit Later" tag, auto-attached by `sync_client.create_rem(text)` when no `parent_id` is given. Child rems do not get it.

### 2. Read & dump a doc

Use `RemNoteReaderLive` from `remnote/reader_live.py` (read-only opens with `mode=ro` URI, safe while RemNote is running). Walk children recursively, sort by **`f`** (string lex). Filter empty `key` for human display:

```python
def render(rid, depth=0):
    rem = r.get_rem_by_id(rid)
    text = r.format_key(rem.get('key', [])).strip()
    if not text:  # empty key — chip / portal / value-only rem; usually skip
        return
    print('  ' * depth + f'- {text}')
    for c in sorted(r.get_rem_children(rid, limit=500),
                    key=lambda c: c['doc'].get('f') or ''):
        render(c['id'], depth + 1)
```

`format_key` resolves `{"i":"q","_id":...}` reference items to `[[Name]]` recursively.

### 3. Find a rem by name

Two paths:

```python
# Fast (indexed but fuzzy LIKE on remsSearchInfos — may miss recent edits, may return substring false positives)
hits = r.search_rem_by_name('6s3c - grok skill')

# Authoritative (direct quanta scan — slower but exact, and tolerates the search index being behind)
r.cursor.execute("SELECT _id, doc FROM quanta WHERE doc LIKE ?", (f'%{name}%',))
```

If the search index returns suspicious matches (e.g. searching `6L1a` returns rems under a Daily Note id `zgescglIjyL9D6l1a`), confirm by re-checking `key` of each hit and discarding substring-only matches.

### 4. Append a child to an existing rem

```python
client.create_rem('hello from opus', parent_id='bL44huKGMvOetgVEk')
```

The plugin assigns `f` larger than every existing sibling's `f`, so the new rem appears at the bottom. To place it elsewhere, pass `position=N` (0 = top, integer index among siblings).

### 5. Create a new top-level doc

```python
client.create_rem('hello from opus')                                    # parent doc
client.create_rem('hello', parent_id='<id printed from previous call>') # child
```

`sync_client.create_rem` returns a command ID, not the new Rem ID. Recover the Rem ID by querying SQLite for `(parent, key[0])` after the queue drains, **with a poll loop** — RemNote uses WAL and a fresh read-only connection may not see the write for 1–3 s after the plugin ACKs (see Gotchas).

```python
import time, sqlite3
def find_new_id(parent_id, text, timeout=10):
    q = ("SELECT _id FROM quanta WHERE json_extract(doc,'$.parent') IS ? "
         "AND json_extract(doc,'$.key[0]') = ? "
         "ORDER BY json_extract(doc,'$.m') DESC LIMIT 1")
    t0 = time.time()
    while time.time() - t0 < timeout:
        conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
        row = conn.execute(q, (parent_id, text)).fetchone()
        conn.close()
        if row: return row[0]
        time.sleep(0.4)
    raise TimeoutError(f'lost create: {text!r}')
```

### 6. Insert a clickable `[[ref]]` (not literal `[[…]]` text)

The plugin's `create` handler does `await rem.setText([cmd.text])` — it wraps the incoming `text` field into a single-element richText array. A string makes a text rem; **a richText reference element makes a real link**:

```python
import requests, sync_client  # sync_client import side-effect-sets NO_PROXY=*
requests.post('http://127.0.0.1:9321/create', json={
    'text': {'i': 'q', '_id': '<target_rem_id>'},   # ← dict, NOT a string
    'parentId': '<where to place the link>',
})
```

Sending `'text': '[[Some Doc]]'` (a plain string) stores the literal characters and renders as un-linked text. Sending the dict produces an actual `[[Some Doc]]` reference that resolves to whatever `<target_rem_id>` currently names — survives renames.

### 7. Load a Linear board view into today's daily note (auto-numbered title)

Use the bundled script `scripts/load_board_to_remnote.py`. It reads the active view from `/Users/han/project/life/linear_board_view/public/data/working_on/views.json`, summarizes the node tree (separating done items into "今日已完成"), creates a new top-level RemNote doc, and inserts `[[<title>]]` into today's daily note.

```bash
python3 ~/.claude/skills/remnote/scripts/load_board_to_remnote.py
python3 ~/.claude/skills/remnote/scripts/load_board_to_remnote.py --slug grok_review --section 早
```

**Title scheme**: `YYMMDD<letter>_<slug>` where the letter is the first unused one today (a, b, c…). Reasoning: lets you call this multiple times per day without collision, and keeps the doc-name prefix sortable. The "next unused letter" is found by scanning top-level rems whose `key[0]` matches `^YYMMDD[a-z]_`. Reusable primitive if you need it elsewhere:

```python
import re, sqlite3
from datetime import datetime
def next_letter_today(db):
    yymmdd = datetime.now().strftime('%y%m%d')
    conn = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    rows = conn.execute(
        "SELECT json_extract(doc,'$.key[0]') FROM quanta "
        "WHERE json_extract(doc,'$.parent') IS NULL "
        "AND json_extract(doc,'$.key[0]') LIKE ?", (f'{yymmdd}%',)).fetchall()
    conn.close()
    used = {m.group(1) for (k,) in rows for m in [re.match(rf'^{yymmdd}([a-z])_', k or '')] if m}
    return yymmdd, next(c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in used)
```

**Destination section**: argument `--section` is one of `auto | 早 | 下午 | 晚上 | root`. `auto` picks by current hour (<12 → 早, 12-17 → 下午, ≥18 → 晚上). The daily note for `YYYY-MM-DD` is the rem whose `key[0]` equals today's ISO date — sync_server's `get_today_daily_doc_id()` helper does this lookup.

### 8. Verify a write landed

```python
import requests  # via sync_client → NO_PROXY=* is set; or pass proxies={'http':None,'https':None}
assert not requests.get('http://127.0.0.1:9321/pending').json()['commands']
# Then read back via SQLite and confirm: new rem exists with expected parent and largest f.
```

If `/pending` stays non-empty past ~5 s, the plugin isn't polling — see Preflight.

### 9. Tag a rem with another rem (write `tp`)

A RemNote-native tag (the chip RemNote shows at the top of a rem, e.g. `[[Dario Amodei]]` tagged with `[[7a1 -- person]]`) lives in the target rem's `tp` field as `{<tag_rem_id>: {"t": true, ",u": <ms>}}`. Removing a tag via the UI flips `"t"` to `false` rather than deleting the entry, so the soft-deleted history is preserved.

The bridge plugin can't write this — its `addPowerup` handler maps a few built-in shortcodes (`editLater → 'e'`) and otherwise calls SDK `rem.addPowerup(code)`, which expects a powerup code, not a rem ID. Passing a tag rem ID returns successfully but writes nothing. So tag-writing goes direct to SQLite. Tags don't involve `f` (no ordering implication), so the only consequence vs. the plugin path is the user needs **Cmd+R** in RemNote to see the new chip:

```python
import sqlite3, json, time
DB = '/Users/han/remnote/remnote-62403c0f38b1150016221e9d/remnote.db'

def set_tag(target_id, tag_id, on=True):
    """Add (on=True) or soft-remove (on=False) a tag, mirroring RemNote's
    own convention of flipping `t` rather than deleting the entry."""
    now_ms = int(time.time() * 1000)
    conn = sqlite3.connect(DB)
    try:
        d = json.loads(conn.execute(
            "SELECT doc FROM quanta WHERE _id = ?", (target_id,)).fetchone()[0])
        tp = d.get('tp', {})
        tp[tag_id] = {'t': on, ',u': now_ms}
        d['tp'] = tp
        d['m'] = now_ms
        d['u'] = now_ms
        conn.execute("UPDATE quanta SET doc = ? WHERE _id = ?",
                     (json.dumps(d, ensure_ascii=False), target_id))
        conn.commit()
    finally:
        conn.close()
```

A **tag** (this workflow) is structurally distinct from a **reference child** (Workflow 6). Both can render as chips at the top of a doc, but a tag lives in the parent's `tp` field and survives reordering of children, while a reference child is a real child rem holding its own bullet identity. If the user says "tag this doc with X", they mean `tp` — use this workflow, not Workflow 6.

## Gotchas

- **Display order = `f`, not `o`/`p`/`y`.** `o`/`p`/`y` are creation-time timestamps; RemNote updates only `f` (a base-94 fractional-index string like `a0P`, `a2h`, `a2}`) when the user reorders blocks in the UI. Sort children by `f` string lex order to match what the user sees. `writer.py` and `live_api.py` don't set `f` at all, which is why their writes can land in unexpected positions — prefer the sync_client path.

- **launchd plists are broken on this machine.** `com.han.remnote-sync-server.plist` and `com.han.remnote-plugin-dev.plist` reference `/Users/han/project/notes/...` (missing `life/`), so `launchctl` exits 78 silently. Manual `nohup` start works. Offer to fix the plists permanently only if the user asks — don't quietly rewrite them.

- **Plugin must be loaded AND polling.** The sync_server can queue commands forever; if the plugin in RemNote isn't loaded (bundle 404 because webpack dev server is down) or paused (the "Stop Live Sync" command was used), nothing happens. Test path before relying on `is_server_running()`: enqueue a no-op and poll `/pending` for ACK.

- **`search_rem_by_name` is substring-fuzzy.** It does `LIKE %x%` against the JSON-encoded search index. Searching `6L1a` matches the Daily Note id `zgescglIjyL9D6l1a` and returns its unrelated children. Verify each hit's `key` before trusting it.

- **Empty rems exist on purpose.** `key=[]` rems are common — they back chips/tags, portals, or rendering artifacts. They don't render as bullets in the UI but they do occupy `f` slots. Filter for display, never delete blindly.

- **`[[Status]]` and `query:` blocks render specially.** Children whose `key` is a single reference (e.g. `[{"i":"q","_id":"..."}]` resolving to `[[Status]]`) show up as header chips at the top of the doc, not as bullets. `query:` blocks render as their own portal section, often at the bottom. They're real children in SQLite; the UI just decorates them.

- **`f` is fractional-index, not opaque.** Append-at-bottom is "any string lex-greater than every existing sibling's `f`". The SDK does the math; if you ever construct `f` yourself, mirror that.

- **Don't mix write paths in one operation.** `sync_client` goes through the SDK; `live_api.py` writes the SQLite row directly (fast, but UI needs Cmd+R and skips `f`); `writer.py` requires RemNote closed. Picking the wrong one corrupts ordering.

- **The DB is the user's real notes.** Always read first when uncertain about a target rem, and prefer reversible operations. Don't `delete_rem` to "clean up" anything not explicitly requested.

- **WAL read-after-write visibility lag.** RemNote runs SQLite in WAL mode. After the plugin acks a create, a fresh `mode=ro` SQLite connection from a separate process may not see the new rem for 1–3 s. Always poll with retry (0.4 s × ~10 s budget) before declaring a write lost — never trust the first empty result. The bundled `scripts/load_board_to_remnote.py` carries a reference `find_rem(parent, text, timeout=10)` helper.

- **Localhost proxy interception.** The user runs an HTTP proxy via `HTTP_PROXY=http://121.4.45.119:31878`; raw `urllib`/`requests` calls to `http://127.0.0.1:9321` get routed through it and return 502. Two fixes: (a) `import sync_client` first — it sets `os.environ['NO_PROXY']='*'` at module load and that bypasses the proxy for all subsequent requests in this process; (b) pass `proxies={'http': None, 'https': None}` to each call. The `NO_PROXY=.fabu.ai,fabu.ai` envvar does NOT cover localhost.

- **References are stored as richText elements, not bracket text.** A clickable `[[Name]]` link in `key` is a dict `{"i": "q", "_id": "<target>"}`, not the literal characters `"[[Name]]"`. To create a reference rem via the bridge, POST `/create` with `text` set to that dict (see Workflow 6) — the plugin wraps it: `setText([{i:"q",_id:"..."}])`. Same trick works for `/update` with `newText`. Storing the literal bracket text won't auto-resolve later — RemNote only links via the SDK / autocomplete path.

- **`addPowerup` only accepts built-in shortcodes.** The plugin handler maps `editLater → 'e'` and passes anything else through to SDK `rem.addPowerup(code)`. The SDK expects a powerup *code* (a short identifier like `'e'`, `'m'`, …), not an arbitrary tag rem ID — so calling `addPowerup` with a tag rem like `AHBynZuyLFShjKeYZ` succeeds quietly but writes nothing. Tag-writing therefore goes direct-DB via Workflow 9.

## See also

- `scripts/load_board_to_remnote.py` (bundled) — end-to-end loader for the Linear board → RemNote daily-note flow. Reference implementation for `wait_drained`, `find_rem` (WAL-tolerant), `create_reference` (richText hack), and `next_letter_today`.
- `/Users/han/project/life/notes/CLAUDE.md` — same machine, deeper detail on the three access patterns, the `remnote_to_todoist.py` task sync, and the Flomo sync.
- `/Users/han/project/life/notes/remnote-sync-plugin/CLAUDE.md` — plugin internals (polling loop, command types, image compression).
- `/Users/han/project/life/notes/remnote-sync-plugin/src/widgets/index.tsx` — plugin source; see the `create`/`update` cases to understand exactly how `cmd.text` / `cmd.newText` get passed to `rem.setText`.
- `/Users/han/project/life/notes/remnote/{reader_live,writer,live_api}.py` — the three Python entry points.
- `/Users/han/project/life/linear_board_view/AGENTS.md` — board-view app schema (`SnapshotFile`, `noteNodes`, `edges`, `issueMembers`) consumed by the bundled loader.
