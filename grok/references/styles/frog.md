# Style pack · frog (default visual: Jupyter notebook)

Pedagogical posture: **bottom-up, worked-example first; build / compute / observe, abstraction emerges**. The lineage is **Karpathy** + **Andrew Ng**. Two exemplars, two valid spines:

- **Karpathy "zero to hero" — code-as-spine.** Open with a code cell of the actual artifact (the command, the function, the data). Each cell takes the smallest next step. The reader watches the abstraction get built in front of them, and every claim is backed by a concrete computation they could redo themselves. Notebook rhythm: `In [N]:` / `Out[N]:` pairs with markdown narration between.
- **Andrew Ng CS229 — math-as-spine.** Start from the simplest concrete problem (one-feature linear regression on a tiny dataset). Derive: likelihood → log-likelihood → gradient → update rule → algorithm. Each line of math is a small next step the reader could have taken. Generalize only after the simplest case is fully chewed. In this style the page leans more on `.chalk` blocks tracing the derivation, less on `In [N]:` cells running code — but the same bottom-up spine.

A page can lean fully Karpathy (code-only, no derivation), fully Ng (derivation-only, no runnable code), or mix the two (derive then run, or run then derive). The notebook visual layer hosts both. The reader closes the page feeling they *could write this themselves now*.

The name "frog" follows Freeman Dyson's *Birds and Frogs*: a frog sits in the mud, sees the flowers up close, and solves problems one at a time. This is the page voice — close-range, example-by-example, comfortable across many domains because it always grounds in a specific computation first.

Default skeleton: [`templates/frog-skeleton.html`](../../templates/frog-skeleton.html). Copy verbatim and fill placeholders; do not hand-roll.

## Voice (the frog delta)

- **Example before abstraction.** Open with a concrete instance — either a code cell of the actual artifact (Karpathy mode) or the smallest numerical problem the algorithm solves (Ng mode). The narration explains what just happened, not what's about to happen. The abstraction emerges, it is not declared upfront.
- **Spelled out.** "Let's just write this from scratch and see" (Karpathy) / "Let's derive this from the likelihood" (Ng). Each cell or each line of math takes the smallest next step. Never reference unwritten future cells / derivations; build forward.
- **Stop-and-think pauses.** Every few cells, an explicit pause — "okay, take a moment to notice…", "stop — what would happen if…", "here's the part that confuses people." These pauses are short, conversational, and they earn their keep by surfacing a non-obvious insight.
- **Analogies to things the reader already wrote.** "This is the same pattern as PyTorch autograd's backward pass." "If you've written `__radd__`, you've already done this." Map the new idea onto something concrete in the reader's head.
- **Lowercase, conversational.** "okay 接下来", "好我们直接看一下这段代码", "等等 — 你可能想…". *Not* magazine register. *Not* paper register.
- **Numbers verbatim.** When showing a real demo's stdout, paste it byte-for-byte — no rounding, no rephrasing — and label it `Out[N]:`. The fidelity is the credibility.

## Visual contract — notebook on plain off-white

Reads like a Jupyter notebook rendered to HTML, not a magazine spread.

- **Off-white page** (`#fafafa`), white cells (`#ffffff`), tinted-blue output cells (`#f9fbfd`), soft-paper sidebars (`#f5f5f5`). No warm-paper texture. Plain reading surface.
- **Type stack**: Inter (body, narration, headings) + JetBrains Mono (every code cell, every prompt, every output, every label). Optional Playfair only for one signature element — the page title — if you want a single typographic flourish; otherwise drop it. No Cormorant, no Playfair body, no drop caps.
- **Notebook width**: max-width ~920px, single column. Padding 56px top, 32px sides on desktop; collapses on mobile.
- **Title block**: a kicker in JetBrains Mono uppercase ("notebook · X · spelled out from scratch") → an Inter 30px h1 → one-line `.sub` in Inter 15px ink-soft → an `in [1]:` meta line in mono caps that quietly sets the "this is a notebook" frame. Border-bottom 1px rule under the whole block.
- **Cells** are the page's primary unit. Every cell has the structure: `<div class="cell"><div class="prompt">In [N]:</div><div class="body">…</div></div>`. The prompt column is 64–70px wide, mono, right-aligned, blue ink (`#4b78cc`). The body has a 2px left border in the same blue, white fill, slightly rounded right corners.
- **Three cell variants**: `cell` (in / input), `cell out` (red prompt `Out[N]:`, tinted-blue body with mono whitespace-pre output), `cell markdown` (faint prompt `md`, transparent body — narration only, no border).
- **Code in input cells**: `<pre><code class="language-python">` with Prism syntax highlighting (or `language-bash` / `language-yaml`). Keep tokens quiet — Prism's `prism.css` theme (light) not `prism-tomorrow`. Mono 13.5px.
- **Code in output cells**: raw text in monospace 13px, no syntax highlighting, `white-space: pre` so columns line up.
- **Chalk block** is the page's one dark surface. Use sparingly — once or twice per page — to render a KaTeX formula, a key trace, or a punchline. Dark slate background `#1c2330`, body text `#e7eef8`, accent labels `#88c0ff`, highlights `#ffd97a`. Mono body.
- **Callouts** (`.callout` default blue, `.callout.green`, `.callout.warn`, `.callout.red`) — 3px accent left-border, paper-soft tinted fill, a mono uppercase `.tag` ("stop & think" / "类比" / "trap" / "gotcha") then a `.text` body. Keep callouts tight: one paragraph, sometimes a short list.
- **Numeric punchline grid `.nums`** — a row of small white-cell `.num-box`es, each with a mono-uppercase `.k` label and a big mono `.v` number. Use to summarize a result ("test PSNR 30.6", "30 000 iters", "5 nodes"). Up to 6 boxes; auto-fits to grid.
- **TOC** — a single white-cell mono-13px list near the top, headed by a faint `.toc-h` label.
- **Tables** (`table.tbl`) — minimal: 1.5px header rule, 1px row rules, no fills. Mono numerics. Bad cells red, good cells green.
- **Diff panes** (`.diff` two-column) — for before/after code comparisons. Each pane has a header bar with a badge (`bad` red / `good` green). Inside, `<pre><code>` plus `<span class="hl">` / `<span class="hl-blue">` for inline highlights.
- **Lab block** — white card, rounded-10px corners, 1px hairline border. Title `lab · <name>` in mono uppercase purple. Subtitle one line in ink-faint. Then controls (sliders / select / text input / buttons) in a `.row`, canvas DPR-scaled, optional `.panel` for status text or `.step-trace` for stepper-style demos. Buttons are flat mono ink; primary button is solid blue.
- **Footer `.nb-foot`** — top-rule, mono 12px, ink-faint. Lists sources verbatim and one closing line.
- **Tree-of-nn.Module blocks** (optional) — mono pre-formatted with ASCII tree characters (`├── └──`), highlighting `nn.Parameter` in blue and inline comments in faint gray. Useful for showing module hierarchies.
- **Forbidden**: warm-paper background, Playfair body, drop caps, Roman numerals, section-rule magazine openers, ornament glyph rows, magazine-style hero with editor-note, pull-quotes, `aside.external` styled as a magazine kicker. None of those belong in a notebook.

## Required components — checklist

Every frog/notebook HTML must include the following — missing any of them and the artifact regresses to "wall of text":

1. **Title block** — kicker in mono caps + Inter h1 + `.sub` one-liner + `in [1]:` meta line + 1px bottom rule.
2. **Cold-open code cell** — the very first content under the title is `In [1]:` showing the *actual* code or command being explained. Not a TOC, not an abstract, not background. Code first.
3. **Cold-open `Out[1]:` cell** — output of the cold-open cell, byte-for-byte if from a real run.
4. **Punchline `.nums` grid** — 4–6 num-boxes near the top summarizing the result the page will explain.
5. **Markdown explainer cell right after cold open** — the agent-voice transition: "okay 接下来我们从零开始把这个拆开看一遍 …" + a `.toc` list of the sections.
6. **Section headings** `<h2 id="sec-…"><span class="num">§N</span>section name</h2>` + a `<div class="lede">` one-line italic-feel summary directly under. Sections are numbered §1 through §N. *Not* Roman numerals.
7. **Code-cell + output-cell pairs** — almost every section opens by showing code (`In [N]:`) and what it produces (`Out[N]:`). The narration is in between as `markdown` cells.
8. **At least one chalk block** — the dark slate render of a key formula, trace, or punchline.
9. **At least 3 callouts** spread through the page — mix of `default` (stop & think / observation), `green` (类比 / analogy), `warn` (gotcha / trap), `red` (致命问题). Tags are mono caps short.
10. **At least one lab block** — DPR-scaled canvas + control row + panel; lab-prefixed control ids; final IIFE call to `draw()` so the canvas renders on first paint.
11. **At least one worked example** — either inline (`In [N]:` cell computing the smallest concrete instance + `Out[N]:` showing the result) or as a chalk trace block stepping through the same calculation by hand.
12. **A diff or compare block** when there's a "naive vs. insight" or "before vs. after" to show (`.diff` two-column or two adjacent code cells with comments).
13. **Footer `.nb-foot`** — mono caps, lists the source files used and any numbers-source notes ("numbers verbatim from `uv run python demo.py`").
14. **Source figures inline when they earn it** — same rule as the bird pack: base64-inline a source figure when it carries information the worked-example + diagram can't replace. Render with a `<figure>` + mono caps caption.

## CSS class quick reference

| Class / element | Purpose | Notes |
|---|---|---|
| `.nb` | Page shell | max-width 920px, padded; mobile collapses |
| `.nb-title` `.kicker` `h1` `.sub` `.meta` | Top title block | Mono kicker, Inter h1, mono meta |
| `.cell` | One notebook cell (grid prompt + body) | Default = input style (blue stripe) |
| `.cell .prompt` | Left mono prompt (`In [N]:` / `Out[N]:` / `md`) | 64–70px col, right-aligned mono |
| `.cell.out` | Output cell | Red prompt stripe, tinted-blue body, mono pre |
| `.cell.markdown` | Narration cell | Transparent body, faint prompt `md` |
| `.chalk` `.label` | Dark slate code-board | Sparingly; key formulas / traces / punchlines |
| `.callout` `.tag` `.text` (+ `.green` / `.warn` / `.red`) | Inline boxed aside | One paragraph; mono tag |
| `.toc` `.toc-h` `ol` | Mini TOC in a cell | Mono ordered list |
| `.nums` `.num-box .k .v` | Punchline numeric grid | Auto-fit; big mono value + tiny label |
| `table.tbl` `td.num` `.hl-bad` `.hl-good` | Notebook tables | Minimal rules, mono numerics |
| `.diff .pane .pane-head .badge` `pre code .hl` | Before/after diff | Two-column; inline `<span class="hl">` |
| `.modtree` `.root` `.leaf` `.pram` `.ann` | nn.Module tree | ASCII tree; param blue, annotation gray |
| `.lab` `.lab-head` `.lab-title` `.lab-sub` `.row` `.panel` | Interactive sandbox | Mono-uppercase purple title; DPR-scaled canvas |
| `.lab .btn` `.btn.primary` | Lab buttons | Flat mono; primary is solid blue |
| `.lab .step-trace .step.active/.done` | Stepper-style demo | Highlights current step; uses `.pc` / `.ret` / `.err` markers |
| `.expander .stage.active` | Macro-expand walker | Borderless stages, active one highlighted |
| `.nb-foot` | Footer | Mono 12px, top-rule |

## Style-specific self-audit (run with the shared base in SKILL.md)

**Visual / components**
- [ ] **Title block** present — kicker (mono caps) + h1 (Inter 30) + `.sub` + `in [1]:` meta + bottom rule.
- [ ] **Cold open is a code cell + output cell pair**, not a TOC or abstract. Code goes first.
- [ ] **Numeric punchline grid** (`.nums` + 4–6 `.num-box`) summarizes the result early.
- [ ] **Every section starts with `<h2 id="sec-…"><span class="num">§N</span> …</h2>` + `.lede`**. No Roman numerals, no section-rule openers.
- [ ] **At least one `.chalk` block** for a signature formula / trace / punchline.
- [ ] **At least 3 distinct callout tags** in use — mix of stop & think / 类比 / gotcha / 致命问题.
- [ ] **Code cell ↔ output cell pairing** is the page's spine — every concept is anchored to a `In [N]: …` followed by an `Out[N]: …`.
- [ ] **Body type is Inter; all code, prompts, labels, num-boxes, tags use JetBrains Mono.** No Playfair body, no Cormorant, no drop caps.
- [ ] **No magazine elements**: no `section.branch[data-accent]`, no `.section-rule`, no `.ornament`, no `.pullquote`, no `.editor-note`, no `.afterword` ink-bordered kicker, no `.colophon` three-column footer.

**Voice / writing**
- [ ] Markdown cells use lowercase conversational openers ("okay 接下来", "好，我们直接看一下", "等等 — 你可能想…"). *Not* magazine register.
- [ ] At least one explicit "stop & think" or "类比" callout makes the reader pause.
- [ ] Numbers in `Out[N]:` cells are verbatim if they come from a real run; clearly marked "typical / illustrative" if synthesized.

## Style-specific gotchas

- **Don't paint a magazine in notebook clothes** — if you find yourself wanting a Roman numeral, an ornament glyph row, a drop cap, or a warm-paper background, the user asked for the wrong style. Go back to the bird pack.
- **Don't fake the output cells** — if you don't have real stdout, make it clearly synthesized ("typical" / "illustrative") in the surrounding narration. Don't paste numbers that look real but aren't.
- **Don't pile cells without narration** — every 2–3 code cells need a `cell markdown` between them explaining what just happened or setting up the next step. Wall of code without commentary is *not* the frog notebook style — that's a script dump.
- **Lab control ids must be lab-prefixed** — frog notebook pages typically have 2–4 labs; control ids collide easily. Use `lab2-yaw`, `lab3-gt`, never `r1` / `slider`.
- **Keep callouts to one paragraph** — they're punctuation, not paragraphs. If you have 5 paragraphs to say, that's a markdown cell or a new section, not a callout.
- **Don't number sections with `I. II. III.`** — those belong to magazine. Notebook uses `§1`, `§2`, … in mono.

## Reference exemplars

- `/Users/han/project/alpha/alpha_second_v1/arcs/all/260513a_kernel_v2_lisp_pro_3/output/A_macros/A_macros_karpathy.html` — the canonical notebook-style exemplar (sexp + macros, spelled out from scratch). Cell rhythm, chalk block usage, lab IIFE structure, footer copy — all inherit from this file.
- `/Users/han/project/learn_with_agent/260514/fabu_clip_drivestudio_karpathy.html` — recent example: 11-section codebase walkthrough on FABU/DriveStudio, 19 input cells, 12 output cells, 3 labs.
