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

1. Discover documents with `api.getDocs()` and select by the requested name or explicit focused target. Do not treat a different sole open document as a replacement for one that closed.
2. For a fresh deliverable, call `/api/docs/create` with a clear name and optional existing output directory. Never create or overwrite a `.tldraw` archive through filesystem tools.
3. Read `api.getShapes(doc.id)` before changing an existing canvas. If it holds unrelated content, stop rather than clearing it.
4. Use `/exec` to create or change shapes. Import SDK primitives dynamically: `const { createShapeId, toRichText } = await import('tldraw')`.
5. Use `helpers.createArrowBetweenShapes(fromId, toId, options)` for semantic diagram edges so endpoints stay bound when nodes move. Reserve raw arrows for explicitly decorative marks.
6. Run `helpers.getLints()` and repair actionable output. For a locally owned doc, call `await helpers.saveDoc()` after the mutation; do not save a remote/shared board.
7. Verify once with `api.getShapes()`, `api.getBindings()`, and a canvas screenshot only when layout needs visual confirmation. Report the document name/id, created IDs, binding/lint result, and saved path.

### Create a fresh document

```bash
sh /Users/han/project/agent/skills/tldraw-offline/scripts/tq POST /api/docs/create \
  '{"name":"Transformer Encoder Demo","directory":"/absolute/existing/output/folder"}'
```

Use the returned `id` verbatim in later `/exec` requests. The create endpoint returns `409` rather than overwriting an existing file; choose another name instead of bypassing it.

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

## Safety boundaries

- Do not edit an open `.tldraw` archive, database, metadata, lock, or generated `.script-workspace` file directly; the live editor owns those state transitions.
- Treat `ownership: 'remote'` as a host-owned document: edits may sync, but do not call `helpers.saveDoc()` or claim the archive was saved.
- On a shared local board, inspect first and avoid bulk deletion or replacement of content not created for the requested task.
- The API token is local, per-launch authentication. Read and use it inside commands; do not print, embed, or transmit it.

## Validation prompts

- "Create a system architecture diagram in a new tldraw file" should create a named local file, bind arrows, lint, save, and report its path.
- "Rearrange this open tldraw board" should inspect its shapes first and modify only the requested components.
- "Add an interactive play button to a tldraw file" should use the document script workspace, verify script status, and save the local document.

Do not trigger this skill merely to explain tldraw concepts, browse tldraw.com, or edit a standalone SVG/PNG outside an open tldraw offline document.
