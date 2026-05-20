# Visual · notebook (opt-in via `--visual notebook`)

Jupyter notebook rendered to HTML on plain off-white. Google Fonts (Inter + JetBrains Mono) + KaTeX + Prism light theme are part of the identity.

Default skeleton: [`templates/frog-skeleton.html`](../../templates/frog-skeleton.html). Copy verbatim and fill placeholders.

The notebook visual is frog-pedagogy's classic rendering; pre-2026-05 it was the frog default.

## Identity tokens

- **Page:** off-white (`#fafafa`), white cells (`#ffffff`), tinted-blue output cells (`#f9fbfd`), soft-paper sidebars (`#f5f5f5`). No warm-paper texture.
- **Type stack:** Inter (body, narration, headings) + JetBrains Mono (every code cell, every prompt, every output, every label). Optional Playfair for the page title only. No Cormorant, no drop caps, no Roman numerals.
- **Width:** max ~920px, single column. Padding 56px top, 32px sides on desktop; collapses on mobile.

## Required components

Missing any of these and the artifact regresses to "wall of text."

1. **Title block** — kicker in mono caps ("notebook · X · spelled out from scratch") + Inter 30px h1 + `.sub` one-liner + `in [1]:` meta line + 1px bottom rule.
2. **Cold-open code cell** — first content under the title is `In [1]:` showing the *actual* code or command. Not a TOC, not an abstract, not background. Code first.
3. **Cold-open `Out[1]:` cell** — output of the cold-open cell, byte-for-byte if from a real run.
4. **Punchline `.nums` grid** — 4–6 num-boxes near the top summarizing the result.
5. **Markdown explainer cell right after cold open** — "okay 接下来我们从零开始把这个拆开看一遍 …" + a `.toc` list of the sections.
6. **Section headings** — `<h2 id="sec-…"><span class="num">§N</span>section name</h2>` + a `<div class="lede">` one-line summary directly under. Sections numbered §1 through §N. Not Roman numerals.
7. **Code-cell + output-cell pairs** — almost every section opens with code (`In [N]:`) and output (`Out[N]:`). Narration between as `markdown` cells.
8. **At least one chalk block** — dark slate rendering of a key formula, trace, or punchline.
9. **At least 3 callouts** spread through the page — mix of `default` (stop & think), `green` (类比), `warn` (gotcha), `red` (致命问题). Mono caps tags.
10. **At least one lab block** — DPR-scaled canvas + control row + panel; lab-prefixed control ids; final IIFE `draw()` call.
11. **At least one worked example** — inline (`In [N]:` cell + `Out[N]:`) or as a chalk trace block stepping through the calculation.
12. **Diff or compare block** when there's "naive vs. insight" — `.diff` two-column or two adjacent code cells with comments.
13. **Footer `.nb-foot`** — mono caps, lists source files and numbers-source notes ("numbers verbatim from `uv run python demo.py`").
14. **Source figures inline when they earn it** — base64-inline when the figure carries information the worked-example + diagram can't replace. `<figure>` + mono caps caption.

## Cell variants

| Variant | DOM | Notes |
|---|---|---|
| `cell` | `<div class="cell"><div class="prompt">In [N]:</div><div class="body">…</div></div>` | Input. Blue prompt (`#4b78cc`), 2px blue left-border, white fill. Code in `<pre><code class="language-python">` with Prism. |
| `cell out` | Same shape, `Out[N]:` red prompt | Tinted-blue body, mono pre, no syntax highlight, `white-space: pre`. |
| `cell markdown` | Faint prompt `md`, transparent body | Narration only, no border. |

## Component vocabulary

| Class / element | Purpose | Notes |
|---|---|---|
| `.nb` | Page shell | max-width 920px, padded |
| `.nb-title` `.kicker` `h1` `.sub` `.meta` | Top title block | Mono kicker, Inter h1, mono meta |
| `.cell` `.cell .prompt` | One notebook cell | 64–70px prompt col, right-aligned mono |
| `.cell.out` | Output cell | Red prompt stripe, tinted-blue body, mono pre |
| `.cell.markdown` | Narration cell | Transparent body, faint prompt `md` |
| `.chalk` `.label` | Dark slate code-board | Sparingly. `#1c2330` bg, `#e7eef8` body, `#88c0ff` accents, `#ffd97a` highlights |
| `.callout` `.tag` `.text` (+ `.green` / `.warn` / `.red`) | Inline boxed aside | One paragraph; mono tag |
| `.toc` `.toc-h` `ol` | Mini TOC in a cell | Mono ordered list |
| `.nums` `.num-box .k .v` | Punchline numeric grid | Auto-fit; big mono value + tiny label |
| `table.tbl` `td.num` `.hl-bad` `.hl-good` | Notebook tables | Minimal rules, mono numerics |
| `.diff .pane .pane-head .badge` `pre code .hl` | Before/after diff | Two-column; inline `<span class="hl">` |
| `.modtree` `.root` `.leaf` `.pram` `.ann` | nn.Module tree | ASCII tree; param blue, annotation gray |
| `.lab` `.lab-head` `.lab-title` `.lab-sub` `.row` `.panel` | Interactive sandbox | Mono-uppercase purple title; DPR-scaled canvas |
| `.lab .btn` `.btn.primary` | Lab buttons | Flat mono; primary solid blue |
| `.lab .step-trace .step.active/.done` | Stepper-style demo | `.pc` / `.ret` / `.err` markers |
| `.expander .stage.active` | Macro-expand walker | Borderless stages, active highlighted |
| `.nb-foot` | Footer | Mono 12px, top-rule |

## Visual self-audit

- [ ] Body type is **Inter**; all code, prompts, labels, num-boxes, tags in **JetBrains Mono**. No Playfair body, no Cormorant, no drop caps.
- [ ] Google Fonts URL loads Inter + JetBrains Mono. KaTeX + Prism light theme present and pinned.
- [ ] **Title block** present — kicker + h1 + `.sub` + `in [1]:` meta + bottom rule.
- [ ] **Cold open is a code cell + output cell pair**, not a TOC or abstract.
- [ ] **Numeric punchline grid** summarizes the result early.
- [ ] **Every section starts with `<h2 id="sec-…"><span class="num">§N</span> …</h2>` + `.lede`**. No Roman numerals.
- [ ] **At least one `.chalk` block** for a signature formula / trace / punchline.
- [ ] **At least 3 distinct callout tags** — mix of stop & think / 类比 / gotcha / 致命问题.
- [ ] **Code cell ↔ output cell pairing** is the page's spine.
- [ ] **No magazine elements**: no `section.branch[data-accent]`, no `.section-rule`, no `.ornament`, no `.pullquote`, no `.editor-note`, no `.afterword`, no `.colophon`.

## Gotchas

- **Don't paint a magazine in notebook clothes.** Roman numeral / ornament glyph row / drop cap / warm-paper background → wrong style. Go back to magazine.
- **Don't fake output cells.** No real stdout → mark synthesized ("typical" / "illustrative") in surrounding narration.
- **Don't pile cells without narration.** Every 2–3 code cells need a `cell markdown` between them. Wall of code without commentary is a script dump.
- **Lab control ids must be lab-prefixed.** Use `lab2-yaw`, `lab3-gt`. Never `r1` / `slider`.
- **Keep callouts to one paragraph.** Punctuation, not paragraphs. Five paragraphs → markdown cell or new section.
- **Don't number sections with `I. II. III.`** Those belong to magazine. Notebook uses `§1`, `§2`, … in mono.

## Reference exemplars

- `/Users/han/project/alpha/alpha_second_v1/arcs/all/260513a_kernel_v2_lisp_pro_3/output/A_macros/A_macros_karpathy.html` — canonical notebook exemplar (sexp + macros, spelled out from scratch). Cell rhythm, chalk usage, lab IIFE structure, footer copy.
- `/Users/han/project/learn_with_agent/260514/fabu_clip_drivestudio_karpathy.html` — 11-section codebase walkthrough, 19 input cells, 12 output cells, 3 labs.
