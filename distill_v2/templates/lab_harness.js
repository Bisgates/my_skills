/* distill_v2 lab harness — injected before all author labs by bin/build.py.
   Fixes the recurring lab-layout failures:
   - canvases that are far taller than their drawn content (height was hardcoded)
   - content drawn past the canvas bottom (clipped)
   - drags that freeze the page (heavy recompute on every pointermove)
   Authors MUST size every canvas with so.fit() and drive heavy redraws through
   so.raf() / so.drag(). See references/lab_authoring.md. */
(function () {
  var so = (window.so = window.so || {});

  // DPR-safe sizing. Height is DERIVED from the live width via `aspect`
  // (width:height, >1 = wider than tall) and clamped, so a canvas is never
  // arbitrarily tall. Returns CSS-pixel drawing context + dims; draw in CSS px.
  //   so.fit(canvas, {aspect:2.6, maxH:420, minH:120, height:<explicit>})
  so.fit = function (canvas, opts) {
    opts = opts || {};
    var dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2));
    var parentW = canvas.parentNode ? canvas.parentNode.clientWidth : 0;
    var cssW = canvas.clientWidth || parentW || 600;
    var cssH;
    if (opts.height) cssH = opts.height;
    else {
      var aspect = opts.aspect || 2.6;
      cssH = Math.round(cssW / aspect);
      cssH = Math.max(opts.minH || 100, Math.min(opts.maxH || 420, cssH));
    }
    canvas.style.width = "100%";
    canvas.style.height = cssH + "px";
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);
    return { ctx: ctx, W: cssW, H: cssH, dpr: dpr };
  };

  // Coalesce repeated calls into at most one per animation frame — wrap any
  // heavy redraw so dragging/among slider input cannot pile up and freeze.
  so.raf = function (fn) {
    var pending = false, lastArgs;
    return function () {
      lastArgs = arguments;
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; fn.apply(null, lastArgs); });
    };
  };

  // Pointer-drag helper with rAF-coalesced moves (never blocks the main thread).
  // handler({x,y,down}) receives CSS-pixel coords relative to the canvas.
  so.drag = function (canvas, handler) {
    var active = false, last = null;
    var flush = so.raf(function () { if (last) handler(last); });
    function pt(e, down) {
      var r = canvas.getBoundingClientRect();
      var t = (e.touches && e.touches[0]) ? e.touches[0] : e;
      return { x: t.clientX - r.left, y: t.clientY - r.top, down: down };
    }
    canvas.style.touchAction = "none";
    canvas.addEventListener("pointerdown", function (e) {
      active = true; last = pt(e, true); handler(last);
      if (canvas.setPointerCapture) try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
    });
    canvas.addEventListener("pointermove", function (e) {
      if (!active) return; last = pt(e, true); flush();
      if (e.cancelable) e.preventDefault();
    });
    window.addEventListener("pointerup", function () { active = false; last = null; });
    return canvas;
  };

  // Debounce expensive work (e.g. a 300-trial Monte-Carlo) to fire after the
  // user pauses, while a cheap preview redraws live. ms default 90.
  so.debounce = function (fn, ms) {
    var t; return function () { var a = arguments; clearTimeout(t); t = setTimeout(function () { fn.apply(null, a); }, ms || 90); };
  };

  // Re-fit + redraw all registered labs on resize (coalesced). Labs register
  // their draw fn so canvases stay correctly proportioned across widths.
  so._draws = [];
  so.onResize = function (draw) { so._draws.push(draw); };
  window.addEventListener("resize", so.raf(function () { so._draws.forEach(function (d) { try { d(); } catch (_) {} }); }));
})();
