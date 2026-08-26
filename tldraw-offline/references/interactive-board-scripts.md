# Interactive board scripts

Patterns for `script/main.js` on a tldraw offline document, beyond the single-purpose recipes in
`api.recipes`. They come from one working instrument-style board: rectangles tagged with `meta`
become modules, labeled arrows wire them together, dragged circles act as knobs, and a tick loop
renders a few hundred marks into a frame.

Read `api.recipes` first for the mechanics of a given feature (`animation-simulation-loop`,
`clickable-card-or-button-ui`, `editable-furniture-with-anchored-internals`,
`connection-dependent-behavior`, `custom-shape-config-js`). This file covers what holds a script
together once several of those run at the same time.

- [Where the state lives](#where-the-state-lives)
- [Knobs built from stock shapes](#knobs-built-from-stock-shapes)
- [Surviving reruns and pauses](#surviving-reruns-and-pauses)
- [Clicks without a click event](#clicks-without-a-click-event)
- [Wires as a typed graph](#wires-as-a-typed-graph)
- [Freehand strokes as data](#freehand-strokes-as-data)
- [Rendering many marks](#rendering-many-marks)
- [Tick budget](#tick-budget)
- [Making the script inspectable from /exec](#making-the-script-inspectable-from-exec)

## Where the state lives

Split state by who owns it:

| State | Home | Why |
| --- | --- | --- |
| User-set parameters (a knob position, a module's kind) | Shape geometry and `meta` | Reloading the document restores them; the user can drag them |
| Per-frame simulation values (velocity, phase, history) | Plain script variables | Writing them to props floods the store and the undo stack |
| Derived caches (parsed paths, style of the last write) | `Map` keyed by shape id | Rebuild them on demand; never persist |

`meta` is the type registry. Tag a shape once at creation — `meta: { sketchModule: 'sine' }` — and
the script finds its own nodes with a filter over `editor.getCurrentPageShapes()`. The user can copy,
move, restyle, or delete that shape and the tag rides along.

## Knobs built from stock shapes

A slider is three plain shapes with derived ids: a locked track rectangle, a draggable ellipse
handle, and a locked text label. The value is read back out of the handle's position, so the canvas
itself stores it.

```js
const trackX = module.x + TRACK_X
const ratio = Math.max(0, Math.min(1, (handle.x + HANDLE_R - trackX) / TRACK_W))
const value = row.min + ratio * (row.max - row.min)
```

Four rules keep it feeling like a control instead of a shape:

- **Pin the handle every tick.** Snap `y` back to its row and clamp `x` to the track ends, so a drag
  can only travel along the track.
- **Lock the parts the user should not grab** (`isLocked: true` on track and label). `updateShapes`
  skips locked shapes, so the script's own writes to them need
  `editor.run(fn, { history: 'ignore', ignoreShapeLock: true })` — one transaction, no
  unlock/relock round trip that a concurrent read could catch mid-flight.
- **Drop the selection once the pointer lifts.** After a drag, tldraw leaves selection chrome on the
  handle. When `editor.inputs.isPointing` is false and every selected id belongs to furniture, call
  `editor.selectNone()`.
- **Throttle the label.** Re-rendering the value text every frame is invisible work; ~12 Hz reads the
  same. Skip the write entirely when the formatted string is unchanged.

Automation writes to the handle rather than to an internal variable, so a scripted value change
visibly moves the knob and `readParams` picks it up through the same path a human drag does.

## Surviving reruns and pauses

A script stops on every file save and on document close, and the board keeps changing while it is
down. Reconcile on startup and periodically after, rather than assuming the canvas matches memory.

- **Adopt, never redraw.** `helpers.createShapeIfMissing` / `createShapesIfMissing` with ids derived
  from the owner's id (`` `${key(moduleId)}-${param}-handle` ``) means a rerun re-attaches to what is
  already there.
- **Realign.** The user moved a module while the script was down, so `onShapeTranslate` never fired.
  Recompute each internal's expected position from its owner and correct any that drifted.
- **Sweep orphans.** The user deleted a module while the script was down, so the removal handler
  never ran. The derived id scheme pays off here: match internals by id pattern and delete those
  whose owner is gone.
- **Self-heal pools.** If a rendered shape is missing (the user deleted it, or an id was reused),
  recreate it in place instead of failing the frame.

Guard the whole startup patch on whether the board is fresh, so default wiring is created once:

```js
const fresh = !editor.getCurrentPageShapes().some((s) => s.meta?.sketchModule)
// ... createShapeIfMissing for every module ...
if (fresh) helpers.createArrowBetweenShapes(sineId, dotId, { richText: toRichText('radius') })
```

## Clicks without a click event

There is no click handler for a drawn shape. Selection is the event: check
`editor.getSelectedShapeIds()` each tick, and treat "this button id is the selection" as a press.

```js
const sel = editor.getSelectedShapeIds()
if (sel.length === 1 && sel[0] === buttonId) {
	doTheAction()
	editor.selectNone()   // consume the press so it fires once
	return
}
```

Contextual buttons follow from the same read: when the selection is one or more shapes carrying the
right `meta`, create a small labeled rectangle by their corner; when it is anything else, delete it.
The button exists only while it is relevant, and no stale chrome is left on the board.

## Wires as a typed graph

Arrows carry two things a script can read: real binding records, and a text label. Together they are
a typed edge list — the label says which parameter the connection drives.

```js
const edges = []
for (const arrow of shapes.filter((s) => s.type === 'arrow')) {
	const bindings = editor.getBindingsFromShape(arrow.id, 'arrow')
	const from = bindings.find((b) => b.props.terminal === 'start')?.toId
	const to = bindings.find((b) => b.props.terminal === 'end')?.toId
	if (!from || !to) continue
	edges.push({ from, to, label: helpers.richTextToPlainText(arrow.props.richText ?? toRichText('')).trim().toLowerCase() })
}
```

A dangling terminal yields no binding, so an arrow the user has not connected is skipped rather than
guessed at. Resolve each edge's meaning through the endpoints' `meta` kinds, and treat an unusable
edge (unknown label, wrong source kind) as absent — the user is mid-edit, and a thrown error stops
the whole loop.

Rebuild the graph on a cadence (every ~30 frames) instead of subscribing to store changes. A
store listener sees the script's own writes and invites feedback loops.

## Freehand strokes as data

`draw` shapes hold their points base64-encoded, and `b64Vecs` converts both ways. That makes a
user's squiggle an input, and lets the script emit stroke geometry as output.

```js
import { b64Vecs } from 'tldraw'

// read: a drawn curve becomes points
const pts = draw.props.segments.flatMap((seg) => b64Vecs.decodePoints(seg.path, seg.dim))

// write: a stroke shape the script will reshape each frame
editor.createShape({
	id, type: 'draw', parentId: frameId, x: 0, y: 0,
	props: {
		color: 'black', fill: 'none', dash: 'solid', size: 's',
		isComplete: true, isClosed: false,
		segments: [{ type: 'free', dim: 2, path: b64Vecs.encodePoints([{ x: 0, y: 0 }, { x: 1, y: 0 }], 2) }],
	},
})
```

Two uses worth knowing: sampling a drawn path by arc length (precompute cumulative segment lengths
once, then binary-search for position `s`) turns a squiggle into a layout; binning a left-to-right
drawing into a lookup table turns it into a curve over time.

## Rendering many marks

- **Pool the shapes.** Allocate ids like `` `${key(ownerId)}-d${i}` ``, then move and restyle them
  each frame. Grow and shrink the pool when the count changes; delete the pool when its owner goes.
  Creating and deleting shapes per frame is what makes a board stutter.
- **Cache the style.** Keep the last `{ color, opacity, geo }` written per id and emit an update only
  when it differs. Position changes every frame; color rarely does.
- **One write per frame.** Collect every change into an array and issue a single
  `editor.updateShapes(updates)` inside `editor.run(fn, { history: 'ignore' })`.
- **Cap the count.** A hard `MAX` on instances keeps a knob at its maximum from freezing the app.
- **Parent to a frame.** `parentId: frameId` clips output to a defined area and moves it with the
  frame; a background rectangle sent to back gives it a surface.

## Tick budget

`editor.on('tick', ...)` shares the editor's render loop, so the handler's cost is subtracted from
drawing. Stage the work by how often it needs to happen:

```js
function tick(elapsed) {
	try {
		t += elapsed / 1000
		frameCount++
		// idle: nobody has moved the pointer in 45s — drop to ~2fps
		if (t - lastActive > 45 && frameCount % 30 !== 0) return
		if (frameCount % 30 === 0) rebuild()      // graph + reconciliation
		pinHandles()                              // cheap, every frame
		if (t - lastTextUpdate > 0.08) updateValueTexts()
		if (frameCount % 2 === 0) render()        // half rate reads the same
	} catch (e) {
		globalThis.__sketchErr = String(e?.stack || e)
	}
}
```

The `try/catch` matters because an exception inside a tick handler is swallowed by the editor's loop
and the board just goes still. Stashing the stack on a global lets an `/exec` call read it.

## Making the script inspectable from /exec

The tick loop is a `requestAnimationFrame` loop, so it pauses whenever the window is hidden or
occluded — which is the normal state while an agent works. Expose two globals and the script becomes
testable without touching the window:

```js
const stepFn = (ms) => { lastActive = t; tick(ms) }
globalThis.__sketchStep = stepFn                    // advance frames on demand
globalThis.__sketchPatch = () => ({                 // current state as plain JSON
	modules: [...registry.entries()].map(([id, e]) => ({ id, kind: e.kind, params: readParams(id) })),
	wires: lastEdges.map((e) => ({ from: e.from, to: e.to, label: e.label })),
})
signal.addEventListener('abort', () => {
	editor.off('tick', tick)
	if (globalThis.__sketchStep === stepFn) delete globalThis.__sketchStep
})
```

Verification then reads as one `/exec` call: step a few frames, dump the state, and check the error
global.

```json
{"code": "for (let i = 0; i < 20; i++) globalThis.__sketchStep(16); return { patch: globalThis.__sketchPatch(), ok: globalThis.__sketchOk, err: globalThis.__sketchErr ?? null }"}
```

Name the globals after the script so two boards never collide, and delete them on `abort` so a
rerun's globals belong to the new instance. Everything installed on `globalThis` from a board script
is gone when the document closes, so nothing here leaks into the saved archive.
