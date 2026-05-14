---
name: remnote
description: Read RemNote rems and append children or create new docs in the user's local RemNote DB on this machine, via the sync_server+plugin bridge under /Users/han/project/life/notes. Use when the user wants to read / dump / search a RemNote rem or document (often referenced by an ID-prefix like '6s3c - grok skill' or '6L1a - todo'), append a child rem under an existing one, or create a new top-level RemNote doc. Do NOT trigger for the Flomo→RemNote or RemNote→Todoist batch sync scripts (those have their own CLIs under scripts/ and remnote-sync-plugin/), for RemNote plugin development (webpack/TypeScript work on the sync_plugin source), or for non-RemNote note systems (Obsidian, Apple Notes, Bear, flomo, generic markdown). Reads use direct SQLite read-only mode (works while RemNote is running); writes route through sync_client → sync_server → RemNote plugin so the SDK assigns the fractional-index `f` field and the UI updates without a manual refresh.
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

`sync_client.create_rem` returns a command ID, not the new Rem ID. To recover the Rem ID, after the queue drains, query SQLite for rems where `parent IS NULL` and `key = [text]` and `m > <pre-call timestamp>`. Example:

```python
import time, json
cutoff = int(time.time() * 1000) - 60_000
r.cursor.execute(
    "SELECT _id FROM quanta WHERE json_extract(doc,'$.parent') IS NULL "
    "AND doc LIKE ? AND json_extract(doc,'$.m') > ?",
    (f'%{text}%', cutoff))
new_id = r.cursor.fetchone()[0]
```

### 6. Verify a write landed

```python
# 1. pending queue cleared
import urllib.request, json
assert json.load(urllib.request.urlopen('http://127.0.0.1:9321/pending'))['commands'] == []
# 2. new rem exists with the expected parent and f > all siblings
```

If `/pending` stays non-empty past ~5 s, the plugin isn't polling — see Preflight.

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

## See also

- `/Users/han/project/life/notes/CLAUDE.md` — same machine, deeper detail on the three access patterns, the `remnote_to_todoist.py` task sync, and the Flomo sync.
- `/Users/han/project/life/notes/remnote-sync-plugin/CLAUDE.md` — plugin internals (polling loop, command types, image compression).
- `/Users/han/project/life/notes/remnote/{reader_live,writer,live_api}.py` — the three Python entry points.
