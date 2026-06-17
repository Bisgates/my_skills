# Lab authoring rules (arc 260616a)

Real failures from the first builds, and the rules that prevent them. A shared harness (`templates/lab_harness.js`, injected before your labs as `window.so`) gives you the primitives. `bin/qa.py` fails the build if you violate the sizing/clip/freeze rules.

**Lab text is Chinese.** On-canvas labels, axis titles, control labels, figcaptions, and readouts are Chinese (artifact language); variable symbols, units, and numbers stay as-is. Watch CJK metrics: `ctx.measureText` widths differ from Latin, so re-check that Chinese labels don't overflow or overlap after sizing.

## 1. Size every canvas with `so.fit` — never hardcode height
The #1 bug was canvases far taller than their content (168px of empty space under `lab-fit`). Height must be DERIVED from the live width.

```js
document.addEventListener('DOMContentLoaded', function () {
  var c = document.getElementById('lab-x'); if (!c) return;
  function draw() {
    var f = so.fit(c, { aspect: 2.6 });   // width:height; pick so content FILLS
    var ctx = f.ctx, W = f.W, H = f.H;     // draw in CSS px within [0,W]x[0,H]
    /* ... compute + draw ... */
  }
  so.onResize(draw); draw();
});
```
- **Pick `aspect` so the drawn content fills the box.** Wide multi-panel labs: `aspect` 2.8–3.6. A single square-ish scatter/diagram: 1.5–2.0. Never leave >~60px empty below the ink; never exceed `maxH` (default 420). If a lab genuinely needs a set height, pass `{height: N}` — but then fill it.
- **Draw strictly within `[0,W]×[0,H]`.** Content past the bottom is clipped (caused the cut-off "forward contribution…" line). Lay panels by *fraction of W* (`var pw = W/3`), not fixed pixels, so they reflow at any width.

## 2. Never overlap text
- Rotated axis labels, readouts, and titles must not collide (the "value" axis label printed over "y=1.0999"). Reserve a left margin for a rotated y-label; keep numeric readouts in their own band; measure with `ctx.measureText` when in doubt.
- Prefer HTML readouts (a `<span id=...>` under the figure) over canvas-drawn numbers when several values change — easier to lay out and select.

## 3. Never block the main thread on drag / slider input
Dragging froze the page because every `pointermove` ran a full recompute (e.g. per-pixel compositing or a 300-trial Monte-Carlo).
- Drag through `so.drag(canvas, handler)` — moves are rAF-coalesced.
- Wrap heavy redraws in `so.raf(draw)`; bind it to slider `input`.
- For genuinely expensive recompute (large-N Monte-Carlo, image fitting), keep a **cheap live preview** on `input` and run the heavy version via `so.debounce(heavy, 90)` (fires when the user pauses) or on the `change` event. Never run thousands of trials synchronously per move.
- Cap per-frame work: an image-fit lab redraws a small grid, not a megapixel buffer, each frame.

## 4. Animation / training loops must actually progress and be bounded
The image-fit loss panel showed `max == min` (loss never moved) and an empty plot.
- A "fit"/"train" lab must run real gradient steps that reduce the loss; **plot the loss history as a polyline that auto-scales** to [min,max] of the history (guard the degenerate min==max case by padding the range). A panel that only prints max/min with no curve is a bug.
- Drive loops with `requestAnimationFrame` gated on a running flag; provide play/pause + reset; stop at convergence or a step cap so it can't spin forever.

## 5. Multi-panel labs fit the reading column
Three side-by-side panels (render / target / loss) share one canvas: compute panel widths as fractions of `W`, leave a small gutter, and give each a short caption inside its panel. Don't let one panel (the loss box) balloon to full height with nothing in it.

## QA gate (`bin/qa.py`)
Fails on: empty-below-ink > 80px (too tall), ink drawn outside the canvas (clipped), and a synthetic drag/slider stress that blocks the main thread > ~250ms (freeze). Run it on every build; fix until PASS.
