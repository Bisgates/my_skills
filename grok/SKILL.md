---
name: grok
description: Convert a target folder — paper PDF, book chapter, concept note, codebase entry-point — into a single-file CDN-self-contained interactive learning HTML. Default output is a two-tab HTML: the MIT tab (top-down, abstraction-first, derived from first principles, magazine longread) and the Stanford tab (bottom-up, worked-example-driven a la Karpathy & Andrew Ng, Jupyter notebook). Same scope on both tabs, cross-anchor jumps between matching concepts; ship only one tab if the source genuinely has nothing for the other lens. Opens with "begin with why", walks every new concept through a concrete minimal worked example, 80% of the page goes to the core insights. Generated HTML is in Chinese; the skill spec stays English. Use when the user runs `/grok <folder>`, asks to "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码" inside `learn_with_agent`, or explicitly asks for an MIT / Stanford / Karpathy / Andrew Ng / SICP / notebook / magazine-style explainer.
---

# grok

> **Languages.** This skill spec is written in English. The artifact it produces — the interactive HTML — has Chinese natural-language content (chapter titles, prose, callouts, captions). Treat this asymmetry as load-bearing: instructions, comments, and reasoning happen in English; everything the human reader sees in the rendered page is in Chinese.

## Quick start

```
/grok "260506_Coding Agents_alphazero"                       # default: dual-tab (MIT + Stanford)
/grok "260506_Coding Agents_alphazero" --style mit           # MIT only (magazine longread)
/grok "260506_Coding Agents_alphazero" --style stanford      # Stanford only (notebook walkthrough)
/grok "260506_Coding Agents_alphazero" --align               # alignment checkpoint first
```

Natural-language equivalents: "用 MIT/SICP 风格讲" / "自顶向下" / "杂志风" all select MIT; "用 Karpathy 风格" / "Andrew Ng 风格" / "notebook 形式" / "spelled out from scratch" / "自底向上" all select Stanford; saying nothing keeps the dual-tab default. Legacy aliases `--style feynman` and `--style karpathy` still resolve (to MIT and Stanford respectively) without warnings. See **Style selection** below.

Output:
- **Default** (no folder argument, or source path lives outside `learn_with_agent/`): `/Users/han/project/learn_with_agent/<YYMMDD>/<source-name>.html` — today's date folder under `learn_with_agent`, in `YYMMDD` form. Created on demand with `mkdir -p`.
- **Override** (folder argument given, e.g. `/grok "260506_Coding Agents_alphazero"`): `<folder>/<source-name>.html` — lives next to the source.

Filename always = source stem with extension swapped to `.html`. Single file, all dependencies via CDN.

## Dual-tab default — why the default is two halves

The default `/grok <folder>` is **one HTML with two tabs**, not a single-style page. This is load-bearing: the reader gets MIT and Stanford as two complete lenses on the same source and picks whichever entry point fits their current cognitive state, switching mid-read when stuck. The pattern echoes how a careful learner already works — book in one hand (MIT: SICP / Strang, top-down, abstraction-first, "here is the interface we wish we had, now we'll implement it"), notebook on the desk (Stanford: Karpathy + Andrew Ng, bottom-up, "let's compute the smallest case by hand and watch the abstraction emerge").

**Three principles govern the dual-tab assembly. They are not negotiable defaults that fade after Quick start; they're the contract.**

1. **Same scope, different lens.** Both tabs cover the **entire source**. Reading either tab alone must be a complete artifact — never split coverage between tabs ("tab A covers framework, tab B covers implementation" is forbidden, that's a single-tab book with two chapters). The other tab is "switch when stuck," not "read next."
2. **Cross-tab anchor jumps between matching concepts.** Each top-level concept gets parallel anchors on both sides — convention is `id="mit-<slug>"` on the MIT side and `id="stanford-<slug>"` on the Stanford side, with the `<slug>` shared. Every major section heading carries a small "↔ 另一视角" affordance that jumps to the matching slug on the other tab (URL hash becomes `#mit-attention` or `#stanford-attention`, tab switches automatically, scroll lands on the anchor). One affordance per section is enough — don't over-engineer; this is for the reader who got stuck on the formula and wants the worked example, not for cross-referencing every paragraph.
3. **Don't force-fill — ship one tab if the other lens has nothing.** Most ML/CV papers have both clean abstract structure (good for MIT) and concrete worked examples (good for Stanford), and the dual-tab pays off. But a pure complexity result, a pure mathematical existence theorem, or a code-only refactor may have no real MIT story (no abstraction barrier to declare) or no real Stanford story (no numerical example to compute). When one tab would be force-filled, **drop it**: emit a single-style HTML with no tab bar and note in the editor-note / `.nb-foot` that the other lens didn't apply (one sentence, e.g. "Stanford 视角因没有可手算的例子被略去"). Forcing a half-empty tab is worse than honest absence.

The tab assembly itself is implemented by [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) (the outer shell — tab bar, hash routing, namespaced CSS scopes, shared CDN deps). The MIT and Stanford bodies inside each tab are still built from their respective skeletons under `templates/`. See **Workflow step 5**.

## Trigger discipline

Enter this skill **only** on explicit user invocation: `/grok <folder>`, or natural-language "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码", or an explicit style request ("用 MIT / Stanford 风格…", "Karpathy 风格的 walkthrough…", "自顶向下讲一下…"). Seeing a PDF, Markdown note, e-book, or unfamiliar source folder in the workspace is **not** a trigger — don't proactively start writing.

## Style selection

Each style pack is a pair: a **pedagogical posture** (how the page reasons) + a **default visual layer** (how it looks). The pedagogy is the primary identity; the visual is its default rendering. The two packs below are the inputs to the dual-tab default and the targets for the single-style `--style` flags.

| Style    | Pedagogical posture                          | Lineage / exemplars                  | Default visual          | Spec                                          | Skeleton                                        |
|----------|----------------------------------------------|--------------------------------------|-------------------------|-----------------------------------------------|-------------------------------------------------|
| MIT      | Top-down, abstraction-first, first principles; declare the interface, then derive | SICP (Abelson/Sussman), Strang, Feynman-style revelation | magazine longread       | [`references/styles/MIT.md`](references/styles/MIT.md)         | [`templates/MIT-skeleton.html`](templates/MIT-skeleton.html)           |
| Stanford | Bottom-up, worked-example first; build / compute / observe, abstraction emerges       | Karpathy "zero to hero", Andrew Ng CS229 | Jupyter notebook        | [`references/styles/Stanford.md`](references/styles/Stanford.md) | [`templates/Stanford-skeleton.html`](templates/Stanford-skeleton.html) |

**Default.** No `--style` flag → **dual-tab** (both packs, assembled via [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html)). See § Dual-tab default for the contract.

**Trigger phrases that select MIT only** (`--style mit`): explicit `--style mit`; "MIT 风格" / "SICP 风格" / "Strang 风格"; "杂志风 / magazine 风格 / longread"; "自顶向下 / top-down / 抽象先行 / interface-first"; "第一性原理讲解 / first-principles walkthrough". Legacy `--style feynman` and "费曼风格 / Feynman style" still resolve here without warnings (Feynman's revelation voice is the canonical MIT exemplar, so the alias is honest).

**Trigger phrases that select Stanford only** (`--style stanford`): explicit `--style stanford`; "Stanford 风格" / "Karpathy 风格" / "Andrew Ng 风格 / Ng 风格"; "notebook 风格 / jupyter 风格 / notebook 形式"; "spelled out from scratch"; "代码为核心 / 代码主导讲解 / code-first walkthrough"; "自底向上 / bottom-up / 例子先行 / example-first / worked-example-driven"; reference to a known notebook-style exemplar file. Legacy `--style karpathy` still resolves here without warnings.

**Resolving the visual** when the user mixes a pedagogy with a non-default visual:
- `MIT + notebook`: "MIT 风格但放进 notebook 排版" → top-down voice rendered as cells. Rare but allowed.
- `Stanford + magazine`: "Karpathy 风格写一篇杂志" → bottom-up voice rendered in warm-paper magazine layout. Rare but allowed.

For the dual-tab default, the MIT tab is always magazine and the Stanford tab is always notebook — mixing visuals across tabs defeats the "visual reinforces cognitive mode" point. Single-style mode is where mixing makes sense.

When the user asks for a single style but is ambiguous which one, ask once — *MIT (top-down) or Stanford (bottom-up)?* — before generating. Don't silently default to dual-tab if the user clearly wanted a single style.

**Adding a new style** (this is expected to happen often). Three things:
1. Add `references/styles/<NewStyle>.md` following the schema established by `MIT.md` and `Stanford.md` — pedagogical posture, lineage / exemplars, voice deltas, visual contract, required components, CSS class quick reference, style-specific self-audit, style-specific gotchas, reference exemplars.
2. Add `templates/<NewStyle>-skeleton.html` containing the full layout with placeholders. Use the existing skeletons as patterns; do not hand-roll a new aesthetic from scratch.
3. Register the style in the table above (pedagogical posture, lineage, default visual, plus the two file pointers) and add its trigger phrases under "Trigger phrases that select \<NewStyle\>". Decide whether it joins the dual-tab default rotation (rare — defaults expand slowly) or stays single-style-only.

Keep style packs **mutually distinguishable**. If a new style is "magazine but with two columns," don't make it a new style — propose an extension to MIT. New styles earn their place by having a *meaningfully different pedagogical posture*.

## Parallel sub-agents (default on for fan-out work)

Paper-grokking is naturally chunked: independent chapter / section drafts, separate worked-example research, several lab-visualization sketches, multiple external-source lookups. Fan those units out into sub-agents — one Agent tool call per unit, fired in a single message so they run concurrently. Cuts wall-clock time roughly proportional to the number of independent units; the reader still receives one HTML.

**Top-level fan-out for the dual-tab default.** The MIT half and the Stanford half are independent learning artifacts that happen to share scope. Treat them as **two parallel agent groups**: one group drafts the MIT magazine body, one group drafts the Stanford notebook body. Both groups can run concurrently after the alignment outline is locked. Inside each group, sections / labs / external supplements fan out as the next concurrent layer. The parent assembles all returned bodies into the dual-tab shell after both groups complete. Single-style mode is one group instead of two.

**Concrete fan-out units in this skill:**

- **Top level (dual-tab only):** MIT-half agent group + Stanford-half agent group. Each receives the shared alignment outline + the cross-anchor slug map (so anchors line up between halves).
- Prior-work research for chapter 0 / cold open — one agent per family (VAE / GAN / Flow / …). Run once at the top level; both halves consume the same research output.
- Section drafting after the outline is locked — one agent per section per half, each with its spec + the writing principles + the relevant source excerpts + **the style pack's voice and component contract** + **the assigned cross-anchor slug**.
- External supplements (`aside.external` in magazine, `aside.external` or external-callout in notebook) — one agent per topic per half (or shared across halves when the supplement is identical, e.g. an author bio).
- Lab visualizations — one agent per lab to write the IIFE + DPR-scaled canvas code. Labs typically appear in only one half (notebooks lean lab-heavy; magazine labs are more selective), so most lab agents fan out under one group.
- Worked examples across distinct concepts — one agent per concept per half. The MIT worked example is the "interface contract made concrete"; the Stanford worked example is the "compute it by hand and read off the answer."

**Don't parallelize the linear spine.** Anything with a sequential dependency stays serial: chapter 0 / cold open must be drafted before later sections can reference its predicament; the `--align` outline must be confirmed before drafts begin; the cross-anchor slug map must be agreed between MIT and Stanford halves before their section agents fan out; the master HTML stitch-together happens once on the parent after both groups return.

**Pass the style choice — and the tab assignment — to every child.** When you delegate a section, the prompt to the child must include: the style pack name (MIT / Stanford), a pointer to the corresponding `references/styles/<X>.md`, the visual layer to use, and (in dual-tab mode) which tab this section belongs to so the child writes the correct `id="mit-<slug>"` or `id="stanford-<slug>"` anchor. A child that doesn't know its tab will write in a generic register that breaks the cross-anchor map.

**Match the parent's model and reasoning depth.** A child on a smaller model writes shallower prose and breaks the voice — same reader (CS PhD, 8 years vision/DL — see `AGENTS.md`), same bar. Pass the parent's `model` explicitly to the Agent tool (Opus stays Opus, Sonnet stays Sonnet); never omit and let the runtime auto-pick a cheaper one. If the parent is in extended-thinking mode, the child should be too. Mismatch is a regression, not an optimization.

## Workflow

1. **Locate the input and resolve the output directory.**
   - **Input.** Resolve `<folder>` (relative to project root or absolute path) when one is given. The user names the source — in the invocation, in chat, or via an obviously-named file inside `<folder>`. Read that source. Don't auto-detect: don't glob for `*.pdf` and silently pick one, don't assume a particular file extension. You may also read other files inside the same source folder (pre-extracted notes under `_drafts/`, related figures, supplementary code, sibling source files) when they help you understand. The user-named source is primary; everything else is supplementary. **Do not read other topic folders.** Strict isolation.
   - **Scan for embeddable imagery while you read.** Note any source figures that pass the writing-principle "the figure carries information the diagram + worked-example can't easily replace" trigger. Extract them in step 5 with `pdfimages` / `pdftoppm` and inline as base64; don't leave the decision until the HTML is mostly written.
   - **Output directory** (referred to below as `<output-dir>`):
     - **Explicit folder argument** (e.g. `/grok "260506_Coding Agents_alphazero"` or `/grok ~/project/learn_with_agent/260507_OmniRe`) → `<output-dir>` = that folder. HTML lives next to the source.
     - **No folder argument**, or a bare source path that lives outside `learn_with_agent/` → `<output-dir>` = `/Users/han/project/learn_with_agent/<YYMMDD>/`, where `<YYMMDD>` is today's date (`date +%y%m%d`). Run `mkdir -p` on it; it may not exist yet.

2. **Resolve the style and mode.** Pick the style pack(s) as described in **Style selection** above. Three outcomes:
   - **Dual-tab (default, no `--style` flag):** load **both** `references/styles/MIT.md` and `references/styles/Stanford.md` into context. Plan for two parallel agent groups in step 5.
   - **Single MIT** (`--style mit` or any MIT trigger phrase): load only `references/styles/MIT.md`. Visual = magazine unless explicitly overridden.
   - **Single Stanford** (`--style stanford` or any Stanford trigger phrase): load only `references/styles/Stanford.md`. Visual = notebook unless explicitly overridden.

   Each style pack owns the voice, the component checklist, the CSS class reference, the style-specific self-audit, and the gotchas — do not paraphrase from memory.

3. **Branch on mode.**
   - Default (no `--align`): jump to step 5.
   - With `--align`: run the alignment checkpoint in step 4 first.

4. **Alignment checkpoint (only with `--align`).**
   Output the following in chat **and** write to `<output-dir>/_drafts/outline.md`. The natural-language content of these items is **in Chinese** because they preview the HTML's content:
   1. **Begin-with-why paragraph.** What was the whole field stuck on before this source? What's the obvious approach? Why doesn't it work? (Shared across both tabs in dual-tab mode — the predicament is the same; only the *voice* differs in the two halves.)
   2. **One-paragraph thesis.** The source's key insight, and what fundamentally separates it from prior solutions.
   3. **Mode + style plan.** Whether the output is dual-tab, single MIT, or single Stanford. In dual-tab mode, one or two sentences per half explaining how each voice will land (e.g. MIT: "open with the abstraction barrier — declare the score-function interface, then show why it must look the way it does"; Stanford: "open with the actual training command + Out cell, then unfold the 8 actions of the train loop").
   4. **Cross-anchor slug map (dual-tab only).** A table of `<slug> · MIT section title · Stanford section title`. The slug is the shared id across both tabs (the MIT side becomes `id="mit-<slug>"`, the Stanford side `id="stanford-<slug>"`). Most sections should have a matching slug on both sides; if a section exists only on one side, mark it explicitly (e.g. `stanford-only` for a pure lab walkthrough that has no MIT counterpart).
   5. **Tab-pruning decision (dual-tab only).** Audit each tab: is one of the two halves going to be force-filled? If yes, drop it now — switch to single-style mode and note the omitted lens. This is the place to act on **Dual-tab principle 3 (don't force-fill)**, before any drafting starts.
   6. **Section / chapter outline.** Per section per active tab: title (with one `<strong>` emphasis word in magazine, or a mono-cap section number in notebook), one-line italic-feel hook, percent of page budget.
   7. **80% allocation.** Name the 1–3 core concepts that consume 80% of the page. Justify why everything else collapses to 20% (cite reader background — see `AGENTS.md`).
   8. **Color-code plan.** Enumerate the recurring key variables / objects in the source. Assign a fixed color to each (red / blue / green / purple / orange). Reuse it in every formula, SVG, code highlight, and inline `<span>` — **including across both tabs** so a reader switching tabs keys the variables without relearning.
   9. **Per-topic accent (magazine only, optional).** If the source has 2–3 parallel core concepts, assign each section an accent stripe color.
   10. **Worked-example plan.** For each new concept introduced, name the smallest concrete instance you'll walk the reader through. See § Writing principle 3. In dual-tab mode, the MIT and Stanford worked examples for the same concept should ideally share the numbers / setup (so the cross-anchor jump lands on the *same* example seen through different lenses).
   11. **Interactive module list.** Each lab block: what insight it reveals + the visualization form + the corresponding source section + which tab it lives on.

   Wait for user confirmation or revision before proceeding to step 5.

5. **Generate the HTML.**
   - Output path = `<output-dir>/<source-stem>.html` (source filename with extension swapped to `.html`).
   - Intermediate notes and external references go in `<output-dir>/_drafts/`. In dual-tab mode, drafts go in `_drafts/mit/` and `_drafts/stanford/` so the two halves don't trample each other.
   - **Single-style mode:** start from a verbatim copy of the chosen skeleton (`templates/MIT-skeleton.html` or `templates/Stanford-skeleton.html`). Fill in the placeholders. Do not hand-roll a new skeleton — the templates already bake in the layout, type stack, lab IIFE / DPR-scaling pattern, and required components.
   - **Dual-tab mode:** fan out two parallel agent groups (see § Parallel sub-agents — top-level fan-out). Each group generates the body of its half against its own skeleton, *without* the outer `<html>/<head>/<body>` boilerplate (return only the inner content that lives inside `<body>`). Then the parent merges both bodies into [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) — the wrapper provides the tab bar, hash routing, namespaced CSS scopes (`.tab-mit { … }` and `.tab-stanford { … }`), and the shared CDN deps loaded once. Each tab's body content gets dropped inside the corresponding `<main id="tab-mit">` / `<main id="tab-stanford">` container; the per-skeleton CSS is wrapped in its scope selector so MIT's magazine type stack and Stanford's notebook type stack don't collide.
   - In all modes: follow the **shared pedagogical principles** below, the **hard constraints** below, **and** the style-specific contract in `references/styles/<Style>.md`.

6. **Open and hand off.**
   - Run `open "<absolute-output-path>"` to launch the HTML in the user's default browser. This is also the moment to walk the lab QA in "Interactive correctness" § item 4 — don't `open` twice.
   - Then print the absolute path **on a line by itself** in the final message (e.g. `/Users/han/project/learn_with_agent/260514/<name>.html`) so the user can `cmd+click` to reopen or copy it cleanly. No surrounding markdown, no trailing punctuation.

## Shared pedagogical principles (apply to every style)

> Not writing a source summary. Writing a learning artifact. The reader should close the page feeling "someone took the time to make this make sense to me."

### 1 · Begin with why (chapter 0 / cold open is non-negotiable)

The first thing the reader sees is **never** "overview of our method." It must be a **field-level predicament**:

- Before this work landed, what were people stuck on?
- What's the obvious thing to try? Why does it fail?
- Ground the predicament in a concrete physical scenario ("假设你有一万张猫的图片"), then translate it to math, code, or data.
- Drop a comparison of how prior families dodge the issue (VAE / GAN / Flow / this work). In magazine: a `.compare` block or a comparison table. In notebook: a markdown cell with a table or a `.diff` two-pane.

In MIT style, this is a full chapter 0 with a `.danger` callout titled "致命问题" and a closing meta-line. In Stanford style, this is a markdown cell + a code cell showing the *actual failure* (the dispatch hell, the broken loop, the wrong output) before the rescue. The form differs; the move is the same. In dual-tab mode, the predicament is shared (same field-level stuck-point) but each tab uses its own callout / cell form to land it.

**Banned**: "Section 1 介绍 / Section 2 相关工作 / Section 3 方法" — that's the structure of the source, not of pedagogy.

### 2 · First principles: naive → fatal flaw → insight → design

Each core concept is unfolded in this exact sequence. First describe the obvious idea any smart reader would think of, so they nod along. Then expose the hidden flaw. Then let the source's insight emerge as the rescue. **Forbidden**: working backward from "the source proposes X."

### 3 · A concrete minimal worked example for every new concept

> Karpathy's lectures live on this pattern. Without it, every formula becomes a ritual symbol.

Every time you introduce a new concept — a definition, a formula, an algorithm step, a function — pause and walk the reader through the smallest concrete instance that exercises it. Pick numbers a reader can hold in their head. Compute by hand, line by line. Land on a specific result the reader can verify. Then state the takeaway: *what does the example reveal about the abstract form?*

This is not "here is an illustrative figure." This is "here is the same calculation, with numbers you could redo on a napkin."

**Concrete formats:**

- **Score function.** Don't just write `s(x) = ∇log p(x)`. Take a 1D standard normal: `p(x) = (1/√2π) e^(−x²/2)`. Then `log p(x) = −x²/2 − const`, so `s(x) = −x`. At `x = 2`, score = `−2`: points back toward the origin with magnitude equal to distance. Now the abstract symbol is anchored.
- **Linear combination of columns.** Don't just write `Ax = x_1·col_1 + x_2·col_2`. Take `A = I_2`, `x = [2,3]`. Compute: `2·[1,0] + 3·[0,1] = [2,3]`. Then change `x = [1,1]`, recompute. Now "linear combination" is not a phrase, it's an act.
- **Attention.** Don't just write `softmax(QK^T)V`. Take 2 tokens of dim 2, set `Q = K = V = I_2`. Compute `QK^T = I_2`, softmax row-wise, multiply with V. Result: identity attention (each token attends to itself). Then perturb `Q[0]` to `[0.5, 0.5]` and watch the row mix.

**Rendering depends on style:**
- **MIT**: a `.worked-example` block with `we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`. The example follows an "interface contract → simplest input that exercises it → observe the contract holds" arc.
- **Stanford**: a code cell (`In [N]:`) that computes the example + an output cell (`Out[N]:`) showing the result, then a markdown cell naming the takeaway. Or, for Ng-style derivations, a `.chalk` block tracing the steps by hand from likelihood → gradient → update rule.

**Constraints on the example:**
- Smallest dimension that's not degenerate (1D or 2D, not 7D).
- Numbers that make arithmetic trivial (`1, 2, 0, ½, π/4` — not `0.7234`).
- One step per line; never make the reader factor what you just did.
- End with a punchline, not "and so on." If you can't extract a punchline, the example was too large.
- Show the example **before** generalizing. Concrete first, abstract second.

### 4 · 80% to the core, as a budget

1–3 core insights consume 80% of the page; everything else collapses to a single sentence or a footnote. If the source has 5 contributions, pick the deepest 1–3 and go deep. **Do not** transcribe full ablation tables.

### 5 · Audience-aware (reader profile lives in `AGENTS.md`)

The reader is a CS PhD with 8 years in vision/DL. **Mention briefly or skip:** standard backprop / Adam / SGD / LayerNorm; vanilla self-attention / multi-head attention; ResNet / U-Net / ViT basics; plain cross-entropy / KL divergence.

**Spend the page budget on what's actually new**: the source's key insight, the new mechanism, why only this design works.

### 6 · No paper-boilerplate language (反论文腔)

The HTML's content is Chinese. **Banned template phrases** (search and remove before shipping): 本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得注意的是 / 显然地 / 与此同时 / 据此可知 / 由上可见.

**Pacing.** Long and short sentences alternate. Allow short sentences, rhetorical questions, metaphors, colloquial pivots ("换句话说" / "问题来了" / "听起来很玄, 其实……" / "注意一个微妙的点"). No paragraph longer than 5–6 lines. After a dense reasoning paragraph, give the reader a breath.

**Intuition before formalism.** Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.

**First and second person allowed.** "我们" / "你会发现" / "试着想一下" beats wall-to-wall passive voice.

**Don't pad.** One clear sentence beats three subordinate clauses cosplaying rigor.

**去 AI 味。** 读着要像一个语言天赋极强的人写的——自然、通顺、悦耳。**少用**"不是 X，而是 Y"这种工整对仗句式；其他被反复吐槽的模型腔（机械三段排比、空洞的"值得深思 / 综合来看 / 让我们一起"、整齐到僵硬的并列、过度收尾总结）一并避开。

**Voice differences across styles** (the actual delta — see each style's spec for the long form):
- **MIT** is *revelation through abstraction* — "here is the interface we wish we had; now we'll show why it must look this way, because Z"; physical-intuition anchors; magazine register; pull-quotes; editor's note; SICP-style wishful thinking ("假装我们已经有了 `score(x)`, 它的契约是…").
- **Stanford** is *spelled-out from the example up* — "okay 接下来 / 好我们直接看一下"; code-cell ↔ output-cell as the page's spine (Karpathy); or likelihood → gradient → algorithm derivation (Ng); "stop & think" pauses; analogies to things the reader has already written; lowercase conversational openers.

### 7 · Color-coded variables (define once, reuse everywhere)

Recurring key variables / objects across math, SVG, prose, and code highlights **all share a single color palette**:

```html
<span class="v-x">x</span>      <!-- red -->
<span class="v-y">y</span>      <!-- blue -->
<span class="v-z">z</span>      <!-- green -->
<span class="v-b">b</span>      <!-- purple (target) -->
```

In LaTeX: `\(\textcolor{#dc2626}{x}\)`. In SVG: stroke/fill with the same hex. In prose: inline `<span class="v-x">`. The reader calibrates the palette once; from then on, every formula and figure is parsable without mental relabeling.

Reference: MIT 18.06's `vec-col1/2/3/b` keeps three column vectors and the target the same colors from the row picture → column picture → matrix form → n-dim abstraction.

### 8 · Revealing interactivity (not knob-pushing demos)

Every lab block leads with a single line: **"此 lab 揭示：…（对应来源章节）"** (or its Stanford notebook equivalent under the `.lab-sub` text). Useless interactions (input box → display number, slider that only changes a color) are banned. Useful forms include:

- Vector field / manifold visualization (click to drop particles, watch them follow the score).
- Parameter slider → geometric object morphs (two lines' intersection, planes' intersection line, singular vs. non-singular).
- Annealed sequence: from large noise to small noise, frame by frame.
- Multi-step algorithm with step-dot or step-trace indicator: prev/next buttons, current step highlighted.
- Tab group when there are multiple methods to compare.

### 9 · Source figures when they earn it

When the source has imagery that's **clearly relevant** — generated samples, key result figures, dataset examples, physical-apparatus photos, named-people portraits a timeline references — embed it. Visual texture grounds the prose and gives the reader something to look at other than paragraphs and SVGs.

**Trigger**: the figure carries information the worked-example + diagram can't easily replace. If you'd struggle to write a one-line caption that explains *why this image is here*, skip it.

**Embedding** (single-file double-click rule still holds):
- **PDF-source figures**: extract with `pdfimages` or `pdftoppm`, then inline as `<img src="data:image/png;base64,…">`. Quality > size; downscale to ≤ 1200px on the long edge so the file stays manageable.
- **Web images**: only from stable pinned URLs (Wikipedia Commons, arXiv-hosted, paper supplementary, the author's project page). Anything not from the source itself goes inside a clearly-labeled "external" aside.
- **No AI-generated stock filler.** Decorative slop is worse than no image. Generic "abstract neural network" art especially — banned.

This is **opt-in**, not a checklist requirement. If the source genuinely has nothing photogenic worth keeping, the SVG + worked-example spine carries the page on its own.

## Hard constraints (apply to every style)

- **Single HTML file.** All CSS/JS inlined or via CDN; images either inlined as base64 data URIs or loaded from pinned public CDNs. **No** project-root, `_lib/`, or local-asset references. Double-click to view.
- **Same stem; folder per resolution rule.** Filename always swaps the source extension to `.html`. The folder follows step 1 of the workflow.
- **Math.** KaTeX (CDN, auto-render).
- **Code.** Prism or highlight.js (CDN). The light Prism theme for notebook; for magazine, either theme works.
- **Style sheets.** Tailwind CDN or hand-written CSS — **Bootstrap is banned**.
- **Fonts.** Google Fonts loads the body + mono stack required by the chosen style. **Do not** ship a `system-ui`-only default.
- **No build step.** No npm / vite / webpack.
- **Topic isolation.** Do not read other topic folders.
- **Online research is allowed.** When the agent enriches with external material, mark it explicitly (in magazine: `aside.external`; in notebook: a clearly labeled callout) — source-original vs. agent-added must be visually distinguishable.
- **When unsure**, search the web first. If still uncertain, write the section anyway and mark the spot with `<div class="uncertain">⚠ 此处未充分消化：[原因]</div>`. **Do not interrupt the user with questions.**
- **HTML already exists.** **Overwrite** (re-running grok on the same source means the user wants to replace). Don't touch `_drafts/`.
- **Pin CDN versions** (`katex@0.16.11`, `prismjs@1.29.0`). **No `@latest`.**
- **Dual-tab cross-anchor contract.** Every concept that exists on both tabs gets an anchor pair: `id="mit-<slug>"` on the MIT side and `id="stanford-<slug>"` on the Stanford side, with `<slug>` shared. A small "↔ 另一视角" affordance on each major section heading jumps to the matching slug on the other tab; the hash-routing JS in `templates/dual-tab-skeleton.html` handles tab switching + scroll. Single-style mode has no `mit-` / `stanford-` prefix on anchors — just `<slug>`.
- **Dual-tab CSS namespacing.** When merging the two halves into the dual-tab shell, all CSS rules from the MIT skeleton must be scoped under `.tab-mit { … }` and all rules from the Stanford skeleton under `.tab-stanford { … }`. The two skeletons share class names (`.lab`, `.callout`, `.cell`, etc.) but mean different things — un-namespaced rules will cross-wire. Shared CDN deps (KaTeX, Prism, fonts) load once at the document level, outside both tab scopes.

### Interactive correctness (don't ship a blank canvas)

The two failure modes that show up most often: **blank canvas** (lab block renders, canvas inside is empty) and **blurry / stretched canvas** (draws fine on the agent's screenshot, looks wrong on the user's retina screen). Guard both — both skeletons already bake these fixes in; if you hand-roll a lab, copy the same pattern:

1. **Render on init.** Every lab IIFE must end with one bare `draw()` call. Never leave the canvas waiting for a first input event. Wrap each lab in `(function(){ const c = document.getElementById('…'); if (!c) return; … draw(); })();` so a missing element doesn't break the rest of the page.
2. **DPR-scale every canvas.** After `getContext('2d')`, set `c.style.width = cssW + 'px'; c.style.height = cssH + 'px'; c.width = cssW * dpr; c.height = cssH * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);`. Drawing then uses CSS pixels but stays sharp on retina.
3. **Lab-prefixed ids.** Two labs cannot share `r1` / `canvas-1`. Prefix every control with the lab name (`lab2-yaw`, `rsc-step`) so a copy-paste doesn't silently cross-wire.
4. **Run the page locally before declaring done.** `open <output-dir>/<name>.html`, scroll to each lab, drag every slider, click every button. If a canvas is blank or a control does nothing, fix before shipping.

## Self-audit checklist (shared base — run alongside the style-specific checklist)

**Writing / content (style-agnostic)**
- [ ] **Cold open is begin-with-why**: predicament + naive + fatal flaw + prior-family comparison. Not "overview of our method."
- [ ] **Every new concept has a worked example** with concrete numbers a reader could redo on a napkin. The example precedes the abstraction.
- [ ] No paper-boilerplate phrases left in the prose: 本文 / 综上 / 基于此 / 不失一般性 / 值得注意的是 / 显然地 — search and replace.
- [ ] **AI 味自检**: "不是 X，而是 Y" 的对仗句式不超过 1–2 处；没有"值得深思 / 综合来看 / 让我们一起 / 总而言之"这类模型口头禅。
- [ ] No paragraph runs longer than 5–6 lines. Dense reasoning paragraphs are interrupted with short sentences, rhetorical questions, or metaphors.
- [ ] Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.
- [ ] Recurring key variables are color-coded; the same hex appears in formulas, SVG strokes / code highlights, and inline prose.

**Technical (style-agnostic)**
- [ ] Single HTML file. All CDNs pinned to a stable version. No local-asset references.
- [ ] Every `<section>` / `<h2>` has an `id`. Every internal link's `data-target` / `href="#…"` resolves.
- [ ] Every agent-added external content is marked (style-specific marker — see each style's spec).
- [ ] Every not-fully-digested spot is marked with `<div class="uncertain">⚠ …</div>`. No silent TODOs.
- [ ] **Every lab IIFE ends with `draw()`** — no blank canvas on first paint.
- [ ] **Every canvas is DPR-scaled**. Lab control ids are lab-prefixed; no collisions across labs.

**Dual-tab specific (only when the output is dual-tab)**
- [ ] Both tabs cover the **full source scope** — neither is a fragment that requires the other to make sense.
- [ ] Every cross-tab pair shares a `<slug>`; MIT side is `id="mit-<slug>"`, Stanford side is `id="stanford-<slug>"`. Mismatches break the ↔ jump.
- [ ] Every major section heading carries the "↔ 另一视角" affordance (or its style-equivalent button); hash routing switches tabs correctly.
- [ ] CSS rules from both skeletons are namespaced under `.tab-mit` / `.tab-stanford` — no un-scoped rule leaks across tabs.
- [ ] If one tab was force-filled (principle 3 violation), it was dropped in step 4 and the page is now single-style with an editor-note explaining the omitted lens. The page does **not** ship a half-empty tab.
- [ ] Color-code palette is consistent across both tabs — a variable's hex on the MIT side equals its hex on the Stanford side.

Run the **style-specific** half of the audit from `references/styles/<Style>.md` before declaring done.

## Gotchas

- **Multiple PDFs in the folder** — ask the user; never default to the first.
- **Mac font fallback** — the CSS stacks in both skeletons include fallbacks (Playfair → Cormorant → Georgia → Times; Inter → system-ui → Helvetica Neue → Arial; JetBrains Mono → Fira Code → Courier New). Don't strip them.
- **KaTeX + color-coded variables** — inside LaTeX use `\textcolor{#c0392b}{x}`; in prose use `<span class="v-x">x</span>`. The hex must match on both sides.
- **`@latest` is forbidden** — every CDN URL pins a stable version so loads stay reproducible across months.
- **Don't leave silent TODO placeholders** — fully write the section, or mark it explicitly with `.uncertain`.
- **Worked-example pitfalls** — if the example takes more than ~5 steps, it's too big. If you can't extract a one-line takeaway, the example wasn't well-chosen. If the numbers aren't tiny (1, 2, 0, ½, π/4), pick smaller ones. The whole point is "the reader could redo this on a napkin."
- **Self-audit "text on a page"** — if the page is mostly `<p>` and a few `<pre>`, with none of the style's required components, that's not a delivery. Go back to the style pack's checklist.
- **Wrong-style trap** — if you find yourself wanting a Roman numeral inside a Stanford-style page, or a code-cell-and-output pair inside an MIT-style page, you're rendering the wrong style. Re-check the user's request, and if uncertain, ask before continuing.
- **Don't mix style components silently** — magazine's `section.branch[data-accent]` and notebook's `.cell` / `.chalk` / `.nums` are not interchangeable. The two CSS systems use different fonts, different page backgrounds, different spacing. If you need a hybrid, write it down in the alignment outline and confirm with the user first.
- **Blank canvas / blurry canvas** — see "Interactive correctness" above. Both skeleton templates already bake the fixes in; copy them verbatim instead of hand-rolling a new lab from scratch.
- **Dual-tab principle violations** — the three most common slips: (a) splitting coverage across tabs ("MIT tab covers theory, Stanford tab covers the implementation") — that's one book in two chapters, not two lenses; revert to single-style or rewrite both halves to be standalone; (b) over-engineering cross-anchors with one affordance per paragraph instead of one per section — the reader is switching to escape a stuck moment, not to chase footnotes; (c) shipping a half-empty Stanford tab on a pure mathematical-existence-theorem paper "because the default is dual-tab" — that's exactly the case principle 3 says to drop; emit single-tab MIT with an editor-note.
- **Cross-anchor slug drift** — if the MIT side renames a section heading mid-draft, the Stanford side's `id="stanford-<slug>"` must update too. The cross-anchor map from the alignment outline is the source of truth; revisit it whenever a section title changes.
- **Dual-tab CSS bleed** — without proper `.tab-mit` / `.tab-stanford` scoping, magazine's body background (warm paper) will bleed into Stanford's notebook surface, or notebook's blue cell stripe will appear behind magazine pull-quotes. The dual-tab skeleton's namespacing is structural — do not strip it.

## See also

- [`references/styles/MIT.md`](references/styles/MIT.md) — magazine-longread style pack (top-down, abstraction-first; SICP / Strang / Feynman exemplars).
- [`references/styles/Stanford.md`](references/styles/Stanford.md) — Jupyter-notebook style pack (bottom-up, example-first; Karpathy / Andrew Ng exemplars).
- [`templates/MIT-skeleton.html`](templates/MIT-skeleton.html) — magazine skeleton.
- [`templates/Stanford-skeleton.html`](templates/Stanford-skeleton.html) — notebook skeleton.
- [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) — outer shell for the dual-tab default: tab bar, hash routing, namespaced CSS scopes, shared CDN deps.
- Project-root `AGENTS.md` — reader profile, project-level hard constraints, trigger protocol.
- `write-a-skill/SKILL.md` — authoring rules for editing this skill or adding new style packs.
