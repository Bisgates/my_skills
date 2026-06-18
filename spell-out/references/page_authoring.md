# Page authoring — spell-out LearnHub page

A page is one self-contained `.html` in `_hub/pages/`. The hub injects the kernel runtime + toolbar
right after `<body>`; you author everything else. Copy `templates/page-skeleton.html` and fill it.

## Visual system (warm paper — reuse LearnHub palette)

```css
:root{
  --paper:#ffffff; --paper-2:#faf7f0;
  --ink:#1f1a14; --ink-soft:#3b332a; --ink-faint:#6b6052;
  --rule:#b8a583; --rule-soft:#d8c9a2;
  --accent:#8c2f1c;   /* noise / ε / generated */
  --accent-2:#2c5340; /* signal / clean data / frozen */
  --gold:#a37c2a;     /* schedule / valve / analytic */
  --net:#3a5a8c;      /* network / learned */
  --code-bg:#efe6ce;
}
html{ zoom:1.18; }    /* page default size */
/* CSS zoom breaks the injected CodeMirror's cursor/selection hit-testing (it mixes zoom-free layout px
   with zoomed mouse coords). Counter-zoom the editor back to net 1.0 and bump its font: */
.lh-cell .CodeMirror, .lh-cell pre[data-executable]{ zoom:.847; font-size:12.6px !important; }
```

Serif body (Iowan/Charter/Cormorant), mono for code/tags. Masthead = double-rule top, kicker
(small-caps), italic-accent title span, italic deck. Sections opened by a centered Roman-numeral
`.chapter-rule` + italic `.chapter-title`. **No dark "blackboard" blocks** — everything on warm paper.

## Equation cards (`.eq-card`) — the signature move

Never dump a whole formula. Each card:
1. `.eq-tag` — mono small-caps label (`① 前向 · 闭式`).
2. `.eq-main` — the full equation, **each term wrapped in `\color{#hex}{…}`** matching the palette.
3. `.parts` — one row per term: the colored term (KaTeX) + a one-line **intuition** (`<b>信号项</b>：…`).
4. `.eq-note` — the load-bearing insight + a tie to a lab/cell ("拖 Lab Ⅱ 看这两项此消彼长").

```html
<div class="eq-card">
  <div class="eq-tag">① 前向 · 一步跳到任意 t（闭式）</div>
  <div class="eq-main">$$x_t=\color{#2c5340}{\sqrt{\bar\alpha_t}\,x_0}+\color{#8c2f1c}{\sqrt{1-\bar\alpha_t}\,\varepsilon}$$</div>
  <div class="parts">
    <div class="part"><span class="t">$\color{#2c5340}{\sqrt{\bar\alpha_t}\,x_0}$</span><span class="d"><b>信号项</b>：把干净样本按 $\sqrt{\bar\alpha_t}$ 缩小。</span></div>
    <div class="part"><span class="t">$\color{#8c2f1c}{\sqrt{1-\bar\alpha_t}\,\varepsilon}$</span><span class="d"><b>噪声项</b>：补上方差 $1-\bar\alpha_t$ 的高斯。</span></div>
  </div>
  <div class="eq-note">高斯套高斯仍是高斯 → <b>任意 t 一步直达</b>。</div>
</div>
```
Use `\underbrace{…}_{…}` for "three things are one" identities. CSS for `.eq-card` is in the skeleton.

## KaTeX everywhere — no plain-text math

Every math symbol the reader sees is KaTeX: equations, **lab readouts, control labels, color legends,
section titles, lab headers**. Never literal `√ᾱ_t` / `ε_θ` / `β_max`. Inside colored `<span class="y">`
the KaTeX glyphs inherit the span color, so `<span class="y">调度 $\bar\alpha$</span>` renders gold.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<!-- at end of body: -->
<script>document.addEventListener("DOMContentLoaded",function(){
  if(window.renderMathInElement) renderMathInElement(document.body,{
    delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],
    ignoredTags:["script","noscript","style","textarea","pre","code"], throwOnError:false });
});</script>
```
Lab readout: `<label>$\sqrt{\bar\alpha_t}$ = <span class="ro" id="lab1-sa">1.00</span></label>` — KaTeX
renders the label once; JS updates only the number span. Never use `onload` for KaTeX.

## Kernel cells

```html
<div class="cell-cap">cell 04 · 训练 ε_θ（公式 ②）</div>
<pre data-executable="true" data-language="python">...validated code...</pre>
```
- Reuse the smoke-validated code, split into a clean ordered sequence (cells share one kernel session,
  so later cells use earlier names). First cell picks device (`mps`→`cpu` fallback) + prints it.
- matplotlib inline: `matplotlib.use("module://matplotlib_inline.backend_inline")`, then `plt.show()` → PNG.
- Every cell must pass `verify_page.py <name>` (0 errors; image-producing cells emit `image/png`).
- Add ≥1 cell the reader is meant to edit + re-run (a knob: `T`, `steps`, a gain).
- **Annotate formula code, split one part per line.** Any line realizing an explained equation carries
  a `# 公式① …` comment, and dense expressions are broken into one-term-per-line so the code maps to
  the eq-card term-by-term — e.g. `signal = sqrt(ᾱ)·x0  # 公式① 信号项` / `noise = sqrt(1-ᾱ)·ε  # 公式①
  噪声项` / `xt = signal + noise`, then `eps_pred = net(xt,t)` / `loss = ‖eps - eps_pred‖²  # 公式②`.
  The reader should be able to point at each formula part in the running code. (User standing rule.)

## distill-style client labs (≥3 per page)

Genuinely computed — real closed-form / solver, never a GIF or pre-rendered fake. Prefer toys with
closed-form structure so a lab can show the *true* quantity (e.g. a GMM's analytic score). Per lab:
- DPR-safe canvas via a tiny `fit()` helper (set `style.width/height` in CSS px, `canvas.width/height`
  × dpr, `ctx.setTransform(dpr,…)`); derive height from width, don't hardcode. **`fit()` must resize the
  backing store ONLY when the width truly changes (cache `c.__w`, tolerance >1px) — re-fitting every
  frame writes `style.height` each draw → layout thrash, and under `zoom:1.18` `clientWidth` oscillates
  ±1px → the canvas jitters violently on slider drag. The skeleton's `fit()` already does this.**
- IIFE per lab; lab-prefixed element ids; bail if the canvas is missing.
- Slider `input` → `raf`-coalesced redraw; never run a heavy loop synchronously per move.
- Animations (sampling/training) gated on `requestAnimationFrame`, bounded, with a Run/▶ button.
- **Do not** touch the injected runtime's namespace: classes `lh-*`, globals `NB`/`ws`/`window._lh*`.
- Lab text is Chinese; math labels are KaTeX.

**Function-explorer labs for complex formulas (à la distill's Interactive GNN).** Any abstract/complex
equation should get a lab where the reader **drags the formula's variables** (a 2D point, a parameter)
and the output/field responds live — turning the equation into something touchable. Example (diffusion
`lab4`): drag the probe $x_t$ and the noise level $t$; the page draws the $\varepsilon$ arrow, the
equivalent score arrow, and the one-step denoised $\hat x_0$, all computed analytically from the toy's
closed form. The reader *feels* "near a mode ε is small, far away ε is large" — which is exactly the
function the network learns. Use a draggable canvas handle (`pointerdown/move/up`, clamp to bounds,
rAF-coalesced redraw); show the live readout via KaTeX-labelled spans. Prefer toys with closed-form
structure so the dragged field is the *true* function, not a fake.

See `distill_v2/references/lab_authoring.md` for the full canvas/perf/no-freeze discipline.

## Prose — write like a cs231n course note

The model is the cs231n course notes (<https://cs231n.github.io/>, e.g. `optimization-1`): a domain
expert reads them top to bottom and *understands*, because they teach rather than just state. The failure
to avoid (reported explicitly — "讲解我看不懂"): correct-but-dense, jargon-stacked, telegraphic prose that
lists true facts with the motivation and reasoning stripped out. Reproduce the cs231n reading experience:

- **Motivation-first opening.** Open each unit by recapping where we are, naming the role this piece
  plays, and foreshadowing where it leads — then introduce it. (cs231n opens optimization by recapping
  score + loss and announcing optimization as "the third and last key component".)
- **Conversational-but-authoritative voice.** Inclusive "我们", direct address, plain natural Chinese.
  Openly flag the subtle or odd points instead of hiding them ("这里看起来奇怪，因为…"). Accessible
  without condescension.
- **Intuition before / around the math.** Build the idea before the formula, through a concrete numerical
  worked example (real numbers, stepped output), code shown before the equation, and — where it genuinely
  helps — a **pedagogical analogy** grounding an abstract object in familiar intuition (cs231n's
  hiker-on-a-hill for the loss landscape). Analogies are allowed and encouraged in this artifact (a
  deliberate exception to the user's global 叙事规范, set for teaching); keep each tied back to the
  mechanism, don't let it drift into literary flourish for its own sake.
- **Explicit signposting & recaps.** Bold a 「核心思想：…」 line before elaborating; name the principle
  ("沿负梯度方向更新") before the details; drop a short bullet recap mid-section and a summary bullet list
  at the end.
- **Preempt confusion.** Anticipate the reader's likely objection or terminology snag and resolve it in
  line ("你可能会问为什么预测 $\varepsilon$ 而不是 $x_0$ —…"). Footnote genuine technicalities rather
  than dropping them silently.
- **Introduce notation incrementally and name it.** Define a symbol in words as it first appears, with
  parenthetical clarifications; never drop an unexplained symbol on the reader. (Pairs with the term-by-
  term eq-card decomposition above.)
- **Show the reasoning glue.** Connect each step to the last with explicit connectives (问题在于… / 因此…
  / 注意… / 关键在于… / 反过来看…); the glue carries the dependency between steps, so it is information.
- **Sentence rhythm.** Vary short and long — short imperatives for emphasis next to longer explanatory
  clauses. Paragraphs ≤5–6 sentences to keep cognitive load down.

Still banned: contentless filler only — 元话语, 套话, slogans, "本页将讲… / 在你的笔记本上跑通…". Density
= information per sentence, not telegraphic compression; a sentence may run as long as the reasoning needs.

**Calibration (forward-process example).** Telegraphic failure: *"前向过程对 $x_0$ 加高斯噪声，闭式解
一步跳到任意 $t$；训练目标预测 $\varepsilon$。"* — all true, unreadable. cs231n voice:

> 要让模型学会去噪，得先有带噪样本——而且最好能直接造出任意噪声档位 $t$ 的样本，不必从 $x_0$ 逐步加噪 $t$
> 次。**核心结论：可以。** 因为每一步加的都是独立高斯，叠加 $t$ 步仍是一个高斯，于是有闭式解
> $x_t=\sqrt{\bar\alpha_t}\,x_0+\sqrt{1-\bar\alpha_t}\,\varepsilon$：给定 $x_0$ 和一个随机 $\varepsilon$，
> 任意 $t$ 一步直达。注意 $\bar\alpha_t$ 从 1 单调降到 0，所以 $t$ 越大、信号被压得越小、噪声占比越大——
> 这正是训练要逆转的过程。

Color legend at the top of the equation section maps color→meaning. Reader is an expert.

## Explanation depth — teach, don't just label (load-bearing)

The eq-cards and labs are the skeleton; the **prose is the teaching**. Thin one-line descs fail the
brief ("讲解性内容太单薄" is an explicit failure). Every page carries, as real explanatory content
(rule of thumb: ≳3× a terse-label baseline):

- **Core background before the formulas (begin-with-why).** The field's predicament → the naive /
  prior approaches and why each fails → what this method does differently → why it works; name the lineage
  (papers/years). 3–4 dense paragraphs, written to be *read and followed* (see § Prose), not a terse
  list. (diffusion: generative problem → GAN/VAE/flow limits → the destroy-then-reverse approach →
  score-matching connection.)
- **Per equation: a derivation / "why defined this way" paragraph** beside each eq-card — where the
  formula comes from and the load-bearing step, not just what each term is ("why predict ε not x₀",
  "why this closed form holds", "where the reverse step comes from", "why the three are one thing").
- **Per lab: a phenomenon-reading paragraph** — which regimes to watch, what each tells you, how it
  ties to the math. Not just "drag the slider".
- **A "scale up to the real model" coda** — map the toy to the production system: what changes
  (architecture / data / conditioning), what is identical (the core equations).

**This is NOT the banned meta-prose.** Banned = talking about the *page* ("本页将讲…"). Required =
talking about the *subject*: derivation, intuition, background, consequence. 篇幅与信息量成正比 — long
because dense, never padded. Deliver that depth in the cs231n voice (§ Prose): motivation-first, concrete
worked examples, named core ideas, preempted confusion, with the reasoning connected step-to-step.
"讲解性内容太单薄" and "讲解我看不懂" are both failures — the first too thin, the second dense-but-
unreadable. Aim between them: rich *and* legible.

## Close — 白纸复述 (Feynman gate)

A `.takeaway` listing the equations to reproduce, then 2–3 `<details class="q">` self-test questions
(question in `<summary>`, answer in `.a`). This is the page's reason to exist: can the reader recreate it?

## Coexistence with the injected runtime

The hub inserts its toolbar + CodeMirror + kernel client after `<body>`. Your KaTeX/lab scripts run on
`DOMContentLoaded`; the runtime converts `pre[data-executable]` to live cells. No conflict if you keep
your own ids/classes and don't redefine `pre[data-executable]` styling (the hub owns it).
