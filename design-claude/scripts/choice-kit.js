/* choice-kit — let a reviewer pick options in a design page and submit them.
 * Inline this file in a <script> at the end of <body>. Markup:
 *   <section data-choice-group="scrollbar" data-choice-title="右侧滚动栏" [data-choice-multi]>
 *     <div data-choice="1a" [data-choice-label="1a 缩略图即滚动条"]>…</div>
 *   </section>
 * Submissions go to choice_server.py (127.0.0.1:47321), which writes
 * <page>.choices.json next to the html. Offline it copies the JSON to the clipboard. */
(function () {
  var SERVER = "http://127.0.0.1:47321";
  var base = location.protocol === "file:" ? SERVER : "";
  var page = decodeURIComponent(location.pathname);
  var groups = [].slice.call(document.querySelectorAll("[data-choice-group]"));
  if (!groups.length) return;

  var css = document.createElement("style");
  css.textContent =
    "[data-choice]{cursor:pointer;position:relative;transition:box-shadow .15s}" +
    "[data-choice]:hover{box-shadow:0 0 0 2px rgba(37,99,235,.35)}" +
    "[data-choice].dc-picked{box-shadow:0 0 0 2.5px #2563eb}" +
    "[data-choice].dc-picked::after{content:'✓';position:absolute;top:-9px;right:-9px;width:20px;height:20px;" +
    "border-radius:50%;background:#2563eb;color:#fff;font:600 12px/20px -apple-system,sans-serif;text-align:center;z-index:5}" +
    ".dc-panel{position:fixed;right:16px;bottom:16px;z-index:99999;width:280px;max-width:calc(100vw - 32px);" +
    "background:#fff;color:#1f2328;border:1px solid rgba(0,0,0,.1);border-radius:12px;" +
    "box-shadow:0 8px 28px rgba(0,0,0,.12);font:13px/1.45 -apple-system,'PingFang SC',sans-serif;padding:12px}" +
    ".dc-panel h4{margin:0 0 8px;font-size:13px;font-weight:600;cursor:pointer;padding-right:24px}" +
    ".dc-panel h4 span{font-weight:400;color:#8c959f;margin-left:6px}" +
    ".dc-rows{max-height:45vh;overflow:auto}" +
    ".dc-panel.dc-shut{width:auto;padding:8px 12px}.dc-panel.dc-shut h4{margin:0;display:inline-block}" +
    ".dc-panel.dc-shut .dc-rows,.dc-panel.dc-shut textarea,.dc-panel.dc-shut .dc-msg{display:none}" +
    ".dc-panel.dc-shut .dc-foot{display:inline-flex;margin-left:10px}" +
    ".dc-row{display:flex;justify-content:space-between;gap:8px;padding:3px 0;color:#57606a}" +
    ".dc-row b{color:#1f2328;font-weight:500;text-align:right}" +
    ".dc-panel textarea{width:100%;box-sizing:border-box;margin:8px 0;min-height:52px;resize:vertical;" +
    "border:1px solid rgba(0,0,0,.14);border-radius:8px;padding:6px 8px;font:inherit}" +
    ".dc-foot{display:flex;align-items:center;justify-content:space-between;gap:8px}" +
    ".dc-msg{font-size:12px;color:#57606a}" +
    ".dc-panel button{border:0;border-radius:8px;background:#2563eb;color:#fff;padding:6px 14px;font:600 13px inherit;cursor:pointer}" +
    ".dc-panel button:disabled{background:#c7d2e3;cursor:default}" +
    ".dc-min{position:absolute;top:8px;right:10px;background:none!important;color:#8c959f!important;padding:0 4px!important}";
  document.head.appendChild(css);

  var state = {};
  function title(g) { return g.getAttribute("data-choice-title") || g.getAttribute("data-choice-group"); }
  function label(o) { return o.getAttribute("data-choice-label") || o.getAttribute("data-choice"); }

  var panel = document.createElement("div");
  // starts folded to one line (title, count, submit) so it never covers the draft
  panel.className = "dc-panel dc-shut";
  panel.innerHTML = '<h4>你的选择</h4><button class="dc-min" title="收起">–</button><div class="dc-rows"></div>' +
    '<textarea placeholder="补充意见（可选）"></textarea>' +
    '<div class="dc-foot"><span class="dc-msg"></span><button class="dc-send">提交</button></div>';
  document.body.appendChild(panel);
  var rows = panel.querySelector(".dc-rows"), note = panel.querySelector("textarea"),
      msg = panel.querySelector(".dc-msg"), send = panel.querySelector(".dc-send");
  var head = panel.querySelector("h4"), min = panel.querySelector(".dc-min");
  function fold() { panel.classList.toggle("dc-shut"); min.textContent = panel.classList.contains("dc-shut") ? "+" : "–"; }
  min.textContent = "+";
  min.onclick = fold;
  head.onclick = fold;

  function render() {
    rows.innerHTML = "";
    var done = groups.filter(function (g) { return (state[g.getAttribute("data-choice-group")] || []).length; }).length;
    head.innerHTML = "你的选择<span>" + done + " / " + groups.length + "</span>";
    groups.forEach(function (g) {
      var id = g.getAttribute("data-choice-group"), picked = state[id] || [];
      [].forEach.call(g.querySelectorAll("[data-choice]"), function (o) {
        o.classList.toggle("dc-picked", picked.indexOf(o.getAttribute("data-choice")) >= 0);
      });
      var names = [].filter.call(g.querySelectorAll("[data-choice]"), function (o) {
        return picked.indexOf(o.getAttribute("data-choice")) >= 0;
      }).map(label);
      var r = document.createElement("div");
      r.className = "dc-row";
      r.innerHTML = "<span></span><b></b>";
      r.firstChild.textContent = title(g);
      r.lastChild.textContent = names.length ? names.join("、") : "未选";
      rows.appendChild(r);
    });
  }

  groups.forEach(function (g) {
    var id = g.getAttribute("data-choice-group"), multi = g.hasAttribute("data-choice-multi");
    g.addEventListener("click", function (e) {
      var o = e.target.closest("[data-choice]");
      if (!o || o.closest("[data-choice-group]") !== g) return;
      var v = o.getAttribute("data-choice"), cur = state[id] || [];
      if (cur.indexOf(v) >= 0) cur = cur.filter(function (x) { return x !== v; });
      else cur = multi ? cur.concat(v) : [v];
      state[id] = cur;
      msg.textContent = "";
      render();
    });
  });

  function payload() {
    var choices = {};
    groups.forEach(function (g) {
      var id = g.getAttribute("data-choice-group");
      choices[id] = { title: title(g), picked: state[id] || [] };
    });
    return { page: page, choices: choices, note: note.value };
  }

  send.onclick = function () {
    var body = JSON.stringify(payload());
    send.disabled = true;
    msg.textContent = "提交中…";
    fetch(base + "/submit", { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j.ok) throw new Error(j.error);
        msg.textContent = "已提交 ✓ " + new Date().toTimeString().slice(0, 5);
        if (window.parent !== window) {
          try { window.parent.postMessage({ type: "dc-choices-submitted", page: page }, "*"); } catch (e) {}
        }
      })
      .catch(function () {
        (navigator.clipboard ? navigator.clipboard.writeText(body) : Promise.reject())
          .then(function () { msg.textContent = "服务未启动，已复制到剪贴板"; },
                function () { msg.textContent = "服务未启动，提交失败"; });
      })
      .then(function () { send.disabled = false; });
  };

  render();
  fetch(base + "/choices?page=" + encodeURIComponent(page))
    .then(function (r) { return r.json(); })
    .then(function (last) {
      if (!last || !last.choices) return;
      Object.keys(last.choices).forEach(function (id) { state[id] = last.choices[id].picked || []; });
      note.value = last.note || "";
      msg.textContent = "已载入上次提交";
      render();
    })
    .catch(function () {});
})();
