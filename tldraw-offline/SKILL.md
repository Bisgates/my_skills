---
name: tldraw-offline
description: Operate open tldraw offline canvases through the app's authenticated local HTTP API. Use when a task involves creating, editing, arranging, connecting, validating, saving, or scripting an open .tldraw/.tldr desktop document. Do not use GUI automation or edit an open .tldraw archive directly.
---

# tldraw offline canvas operator

tldraw offline provides a local API for its live editor. Use it instead of UI automation so every edit can target one explicit document, use real bindings, and be verified from the document records.

## Connection

Keep tldraw offline and the intended document open. The app writes a per-launch port and bearer token to:

```text
~/Library/Application Support/tldraw/server.json
```

Read that file at the start of every shell call: tool shells do not share exported variables. Prefer the bundled helper, which does this without exposing the token in output:

```bash
sh /Users/han/project/agent/skills/tldraw-offline/scripts/tq POST /api/search \
  '{"code":"return await api.getDocs()"}'
```

The meaningful endpoints are:

| Endpoint | Purpose |
| --- | --- |
| `POST /api/search` | Discover documents, read shapes/bindings, screenshots, API recipes. |
| `POST /api/docs/create` | Create and save a new named local `.tldraw` document. |
| `POST /api/doc/:id/exec` | Run async JavaScript against exactly one live editor. |
| `GET /api/doc/:id/script-status` | Check durable document-script state. |

Use `GET /readme` only when a needed endpoint or helper is unclear.

## Static canvas workflow

Normal board work has one persistent destination:

```text
/Users/han/project/learn_with_agent/tldraw/agent.tldraw
```

Create each new board as a page in that document. Its name is exactly `YYMMDD_board-name`: use the local date and a short lower-case board name, for example `260825_encoder`. A separately named `.tldraw` file is an explicit user override, not the default.

1. Discover documents with `api.getDocs()` and select `agent.tldraw` by its `filePath`. Do not treat a different sole open document as a replacement. If the file exists but is closed, open it non-activating with `open -gj /Users/han/project/learn_with_agent/tldraw/agent.tldraw`, then query again.
2. Only if that file is genuinely absent, create it through `/api/docs/create` with `name: "agent.tldraw"` and `directory: "/Users/han/project/learn_with_agent/tldraw"`. Never create or overwrite a `.tldraw` archive through filesystem tools.
3. At the beginning of a new board, create and select its dated page before adding shapes. If the exact page name already exists, inspect it and stop for an explicit continuation instruction; do not clear, replace, or silently suffix it.
4. Read `api.getShapes(doc.id)` before changing an existing canvas. If it holds unrelated content, stop rather than clearing it.
5. Use `/exec` to create or change shapes. Import SDK primitives dynamically: `const { createShapeId, toRichText } = await import('tldraw')`.
6. Use `helpers.createArrowBetweenShapes(fromId, toId, options)` for semantic diagram edges so endpoints stay bound when nodes move. Reserve raw arrows for explicitly decorative marks.
7. Run `helpers.getLints()` and repair actionable output. For a locally owned doc, call `await helpers.saveDoc()` after the mutation; do not save a remote/shared board.
8. Verify once with `api.getShapes()`, `api.getBindings()`, and a canvas screenshot only when layout needs visual confirmation. Report the document name/id, page name, created IDs, binding/lint result, and saved path.

### Initialize the default document only when missing

```bash
sh /Users/han/project/agent/skills/tldraw-offline/scripts/tq POST /api/docs/create \
  '{"name":"agent.tldraw","directory":"/Users/han/project/learn_with_agent/tldraw"}'
```

Use the returned `id` verbatim in later `/exec` requests. The create endpoint returns `409` rather than overwriting an existing file; re-query the documents instead of bypassing it.

### Prepare a dated board page

Run this as the first `/exec` transaction for a new board, replacing `260825_encoder` with the required `YYMMDD_board-name` value:

```js
const pageName = '260825_encoder'
if (editor.getPages().some((page) => page.name === pageName)) {
  throw new Error(`Page already exists: ${pageName}. Inspect it and obtain explicit continuation authorization.`)
}
editor.createPage({ name: pageName })
const page = editor.getPages().find((candidate) => candidate.name === pageName)
if (!page) throw new Error(`Could not create page: ${pageName}`)
editor.setCurrentPage(page)
return { pageId: page.id, pageName: page.name }
```

Create the diagram in a following transaction after this page setup succeeds. This makes the page target unambiguous and prevents shapes from landing on whichever page happened to be active.

### Execute a focused edit

```bash
sh /Users/han/project/agent/skills/tldraw-offline/scripts/tq POST \
  "/api/doc/DOC_ID/exec" \
  '{"code":"const { createShapeId, toRichText } = await import(\"tldraw\"); const id = createShapeId(\"box\"); editor.createShape({ id, type: \"geo\", x: 100, y: 100, props: { geo: \"rectangle\", w: 240, h: 80, richText: toRichText(\"Label\") } }); await helpers.saveDoc(); return { id, lints: await helpers.getLints() }"}'
```

Write one coherent layout transaction rather than a succession of partial UI-like gestures. Give important shapes stable, readable IDs. Use the returned IDs for connections and verification.

## Document scripts

Static diagrams belong in `/exec`. Use document scripts only for behavior that must survive reopen, such as custom controls, interactions, animations, or reactive layouts.

Request `/api/doc/:id/script-workspace`, read existing `script/main.js` before changing it, and inspect `/script-status` after writing. Keep host-owned mutations behind the document's host guard for boards that may be shared. Scripts execute on every participant, so never clear and redraw a shared page on startup.

`main.js` runs on mount and reruns on save. Registering new shape types, bindings, or canvas overlays needs a sibling `script/config.js`, which rebuilds the editor when saved. Read the matching entry in `api.recipes` for the mechanics of the specific feature:

```json
{"code": "return Object.keys(api.recipes)"}
```

Read [references/interactive-board-scripts.md](references/interactive-board-scripts.md) when the script goes past a single recipe — draggable knobs or buttons made of ordinary shapes, arrows read as a wiring graph, pooled rendering of many marks, or a tick loop that has to stay cheap. It covers which state belongs in shape geometry versus script memory, and how to reconcile the board after a rerun.

### Verifying a script that animates

The editor's tick loop is tied to on-screen rendering, so it pauses while the app window is hidden or occluded — the usual state while an agent works. Give the script a global step function and a state dump, then drive both from one `/exec` call instead of asking the user to bring the window forward:

```js
globalThis.__myStep = (ms) => tick(ms)          // in script/main.js
globalThis.__myState = () => ({ /* plain JSON */ })
```

Wrap the tick body in `try/catch` and stash the stack on a global; the editor swallows handler exceptions, so a broken frame otherwise shows up only as a board that stopped moving.

## Safety boundaries

- Do not edit an open `.tldraw` archive, database, metadata, lock, or generated `.script-workspace` file directly; the live editor owns those state transitions.
- Treat `ownership: 'remote'` as a host-owned document: edits may sync, but do not call `helpers.saveDoc()` or claim the archive was saved.
- On a shared local board, inspect first and avoid bulk deletion or replacement of content not created for the requested task.
- The API token is local, per-launch authentication. Read and use it inside commands; do not print, embed, or transmit it.

## Validation prompts

- "Create a system architecture diagram" should create `YYMMDD_architecture` in `agent.tldraw`, bind arrows, lint, save, and report its path and page name.
- "Rearrange this open tldraw board" should inspect its shapes first and modify only the requested components.
- "Add an interactive play button to a tldraw file" should use the document script workspace, verify script status, and save the local document.
- "Make these boxes into knobs I can drag" should build controls from stock shapes whose values live in the canvas, and survive a script rerun without redrawing user-editable shapes.

Do not trigger this skill merely to explain tldraw concepts, browse tldraw.com, or edit a standalone SVG/PNG outside an open tldraw offline document.
