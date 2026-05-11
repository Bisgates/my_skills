---
name: grok
description: Convert a target folder — paper PDF, book chapter, concept note, codebase entry-point, or anything the user is trying to understand — into a single-file, CDN-self-contained magazine-style interactive learning HTML (saved to `learn_with_agent/<YYMMDD>/` by default, or next to the source if a folder argument is passed). Opens with "begin with why", deconstructs from first principles, walks every new concept through a concrete minimal worked example; 80% of the page goes to the core insights. Generated HTML's natural-language content is in Chinese (the user's reading language); only the skill spec itself is in English. Use when the user runs `/grok <folder>` or asks to "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码" inside the `learn_with_agent` project.
---

# grok

> **Languages.** This skill spec is written in English. The artifact it produces — the interactive HTML — has Chinese natural-language content (chapter titles, prose, callouts, captions). Treat this asymmetry as load-bearing: instructions, comments, and reasoning happen in English; everything the human reader sees in the rendered page is in Chinese.

## Quick start

```
/grok "260506_Coding Agents_alphazero"
/grok "260506_Coding Agents_alphazero" --align
```

Output:
- **Default** (no folder argument, or source path lives outside `learn_with_agent/`): `/Users/han/project/learn_with_agent/<YYMMDD>/<source-name>.html` — today's date folder under `learn_with_agent`, in `YYMMDD` form (today = `260510`). Created on demand with `mkdir -p`.
- **Override** (folder argument given, e.g. `/grok "260506_Coding Agents_alphazero"`): `<folder>/<source-name>.html` — lives next to the source.

Filename always = source stem with extension swapped to `.html`. Single file, all dependencies via CDN.

## Trigger discipline

Enter this skill **only** on explicit user invocation: `/grok <folder>`, or natural-language "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码". Seeing a PDF, Markdown note, e-book, or unfamiliar source folder in the workspace is **not** a trigger — don't proactively start writing.

## Parallel sub-agents (default on for fan-out work)

Paper-grokking is naturally chunked: independent chapter drafts, separate worked-example research, several lab-visualization sketches, multiple external-source lookups. Fan those units out into sub-agents — one Agent tool call per unit, fired in a single message so they run concurrently. Cuts wall-clock time roughly proportional to the number of independent units; the reader still receives one HTML.

**Concrete fan-out units in this skill:**

- Prior-work research for chapter 0 — one agent per family (VAE / GAN / Flow / …).
- Chapter body drafting after the outline is locked — one agent per chapter, each with its chapter spec + the writing principles + the relevant source excerpts.
- External supplements (`aside.external`) — one agent per topic.
- Lab visualizations — one agent per lab to write the IIFE + DPR-scaled canvas code.
- Worked examples across distinct concepts — one agent per concept.

**Don't parallelize the linear spine.** Anything with a sequential dependency stays serial: chapter 0 must be drafted before chapter 1 can reference its predicament; the `--align` outline must be confirmed before chapter drafts begin; the master HTML stitch-together happens once on the parent after all chapter agents return.

**Match the parent's model and reasoning depth.** A child on a smaller model writes shallower prose and breaks the voice — same reader (CS PhD, 8 years vision/DL — see `AGENTS.md`), same bar. Pass the parent's `model` explicitly to the Agent tool (Opus stays Opus, Sonnet stays Sonnet); never omit and let the runtime auto-pick a cheaper one. If the parent is in extended-thinking mode, the child should be too. Mismatch is a regression, not an optimization.

## Workflow

1. **Locate the input and resolve the output directory.**
   - **Input.** Resolve `<folder>` (relative to project root or absolute path) when one is given. The user names the source — in the invocation, in chat, or via an obviously-named file inside `<folder>`. Read that source. Don't auto-detect: don't glob for `*.pdf` and silently pick one, don't assume a particular file extension. You may also read other files inside the same source folder (pre-extracted notes under `_drafts/`, related figures, supplementary code, sibling source files) when they help you understand. The user-named source is primary; everything else is supplementary. **Do not read other topic folders.** Strict isolation.
   - **Scan for embeddable imagery while you read.** Note any source figures that pass the writing-principle-11 trigger ("the figure carries information the SVG + worked-example can't easily replace"). Extract them in step 4 with `pdfimages` / `pdftoppm` and inline as base64; don't leave the decision until the HTML is mostly written.
   - **Output directory** (referred to below as `<output-dir>`):
     - **Explicit folder argument** (e.g. `/grok "260506_Coding Agents_alphazero"` or `/grok ~/project/learn_with_agent/260507_OmniRe`) → `<output-dir>` = that folder. HTML lives next to the source.
     - **No folder argument**, or a bare source path that lives outside `learn_with_agent/` → `<output-dir>` = `/Users/han/project/learn_with_agent/<YYMMDD>/`, where `<YYMMDD>` is today's date (`date +%y%m%d`, e.g. `260510`). Run `mkdir -p` on it; it may not exist yet.

2. **Branch on mode.**
   - Default (no `--align`): jump to step 4.
   - With `--align`: run the alignment checkpoint in step 3 first.

3. **Alignment checkpoint (only with `--align`).**
   Output the following in chat **and** write to `<output-dir>/_drafts/outline.md` (using the `<output-dir>` resolved in step 1). The natural-language content of these items is **in Chinese** because they preview the HTML's content:
   1. **Begin-with-why paragraph.** What was the whole field stuck on before this source? What's the obvious approach? Why doesn't it work? This is chapter 0, not chapter 1.
   2. **One-paragraph thesis.** The source's key insight, and what fundamentally separates it from prior solutions.
   3. **Chapter outline.** Per chapter: title (with one `<strong>` emphasis word), one-line italic hook, percent of page budget.
   4. **80% allocation.** Name the 1–3 core concepts that consume 80% of the page. Justify why everything else collapses to 20% (cite reader background — see `AGENTS.md`).
   5. **Color-code plan.** Enumerate the recurring key variables / objects in the source (e.g. score function, noisy point vs. clean point, column vectors, target b…). Assign a fixed color to each (red / blue / green / purple / orange). Reuse it in every formula, SVG, and inline `<span>`.
   6. **Per-topic accent (optional).** If the source has 2–3 parallel core concepts (PSNR/SSIM/LPIPS-style), assign each section an accent stripe color.
   7. **Worked-example plan.** For each new concept introduced, name the smallest concrete instance you'll walk the reader through (e.g. "score function: 1D standard normal, x=2"). See § Writing principle 3.
   8. **Interactive module list.** Each lab block: what insight it reveals + the visualization form + the corresponding source section.

   Wait for user confirmation or revision before proceeding to step 4.

4. **Generate the HTML.**
   - Output path = `<output-dir>/<source-stem>.html` (source filename with extension swapped to `.html`), where `<output-dir>` is the directory resolved in step 1.
   - Intermediate notes and external references go in `<output-dir>/_drafts/`.
   - Start from a verbatim copy of [`templates/skeleton.html`](templates/skeleton.html); fill in the placeholders. Do not hand-roll a new skeleton — the template already bakes in the masthead + warm-paper hero + progress bar + nav rail + section openers + drop-cap lede + callout matrix + math-box + worked-example + naive/insight compare + DPR-scaled lab + timeline + afterword + colophon.
   - Follow the writing principles and hard constraints below.

## Writing principles

> Not writing a source summary. Writing a magazine-grade longread. The reader should close the page feeling "someone took the time to make this make sense to me."

### 1 · Begin with why (chapter 0 is non-negotiable)

The first chapter the reader sees is **never** "overview of our method." It must be a **field-level predicament**:

- Before this work landed, what were people stuck on?
- What's the obvious thing to try? Why does it fail? (Make this explicit with a `.danger` callout titled "致命问题".)
- Ground the predicament in a concrete physical scenario ("假设你有一万张猫的图片"), then translate it to math.
- Drop a comparison table of how prior families dodge the issue (VAE / GAN / Flow / this work).
- Close with one Feynman-grade meta-line: "如果不能直接解决，先问我真正需要的是什么——也许我需要的比我以为的少得多。"

Chapter 1 then introduces the source's actual key insight. Reference template (Diffusion):
`ch0 根本困境 → ch1 天才洞察 (Score Function) → ch2 怎么用 (Langevin) → ch3 怎么学 (Score Matching) → …`.

**Banned**: "Section 1 介绍 / Section 2 相关工作 / Section 3 方法" — that's the structure of the source, not of pedagogy.

### 2 · First principles: naive → fatal flaw → insight → design

Each core concept is unfolded in this exact sequence. First describe the obvious idea any smart reader would think of, so they nod along. Then expose the hidden flaw. Then let the source's insight emerge as the rescue. **Forbidden**: working backward from "the source proposes X."

### 3 · A concrete minimal worked example for every new concept

> Karpathy's lectures live on this pattern. Without it, every formula becomes a ritual symbol.

Every time you introduce a new concept — a definition, a formula, an algorithm step — pause and walk the reader through the smallest concrete instance that exercises it. Pick numbers a reader can hold in their head. Compute by hand, line by line. Land on a specific result the reader can verify. Then state the takeaway: *what does the example reveal about the abstract form?*

This is not "here is an illustrative figure." This is "here is the same calculation, with numbers you could redo on a napkin."

**Concrete formats:**

- **Score function.** Don't just write `s(x) = ∇log p(x)`. Take a 1D standard normal: `p(x) = (1/√2π) e^(−x²/2)`. Then `log p(x) = −x²/2 − const`, so `s(x) = −x`. At `x = 2`, score = `−2`: points back toward the origin with magnitude equal to distance. Now the abstract symbol is anchored.
- **Langevin sampling.** Don't just write the SDE. Take `p(x) = N(0,1)`, `ε = 0.1`, start at `x_0 = 3`. Compute three steps by hand: `x_1 = 3 + 0.1·(−3) + √0.2·z_1`, etc. Show the sequence drifting toward 0 plus jitter. Now "drift + noise" has a shape.
- **Linear combination of columns.** Don't just write `Ax = x_1·col_1 + x_2·col_2`. Take `A = I_2`, `x = [2,3]`. Compute: `2·[1,0] + 3·[0,1] = [2,3]`. Then change `x = [1,1]`, recompute. Now "linear combination" is not a phrase, it's an act.
- **Attention.** Don't just write `softmax(QK^T)V`. Take 2 tokens of dim 2, set `Q = K = V = I_2`. Compute `QK^T = I_2`, softmax row-wise, multiply with V. Result: identity attention (each token attends to itself). Then perturb `Q[0]` to `[0.5, 0.5]` and watch the row mix.

The skeleton ships a `.worked-example` block. Format:
- `we-label` — one-line setup tag in mono caps, e.g. "Worked example · 1D 标准正态".
- `we-setup` — italic one-liner with the concrete inputs.
- `we-steps` — numbered `<ol>`, one operation per line.
- `we-takeaway` — `📌` punchline that names what the example reveals about the general form.

**Constraints on the example:**
- Smallest dimension that's not degenerate (1D or 2D, not 7D).
- Numbers that make arithmetic trivial (`1, 2, 0, ½, π/4` — not `0.7234`).
- One step per line; never make the reader factor what you just did.
- End with a punchline, not "and so on." If you can't extract a punchline, the example was too large.
- Show the example **before** generalizing. Concrete first, abstract second.

### 4 · 80% to the core, as a budget

1–3 core insights consume 80% of the page; everything else collapses to a single sentence or a footnote. If the source has 5 contributions, pick the deepest 1–3 and go deep. **Do not** transcribe full ablation tables.

### 5 · Audience-aware (reader profile lives in `AGENTS.md`)

The reader is a CS PhD with 8 years in vision/DL. **Mention briefly or skip:**

- Standard backprop / Adam / SGD / LayerNorm
- Vanilla self-attention / multi-head attention
- ResNet / U-Net / ViT basics
- Plain cross-entropy / KL divergence

**Spend the page budget on what's actually new**: the source's key insight, the new mechanism, why only this design works.

### 6 · Feynman / Karpathy voice

- **Example-driven.** Concrete first, abstract second. (See principle 3.)
- **Predict-then-verify.** "If X were really true, we should see Y — and the experiments do show Y."
- **Reveal, don't state.** Not "X equals Y" but "why X must equal Y — because Z."
- **Physical intuition anchors.** Score function = "uphill direction." Adding noise = "smearing the ridge." Normalization constant Z = "volume integral over all of space."

### 7 · No paper-boilerplate language (反论文腔)

The HTML's content is Chinese. **Banned template phrases** (search and remove before shipping): 本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得注意的是 / 显然地 / 与此同时 / 据此可知 / 由上可见.

**Pacing.** Long and short sentences alternate. Allow short sentences, rhetorical questions, metaphors, colloquial pivots ("换句话说" / "问题来了" / "听起来很玄, 其实……" / "注意一个微妙的点"). No paragraph longer than 5–6 lines. After a dense reasoning paragraph, give the reader a breath.

**Intuition before formalism.** Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.

**First and second person allowed.** "我们" / "你会发现" / "试着想一下" beats wall-to-wall passive voice.

**Don't pad.** One clear sentence beats three subordinate clauses cosplaying rigor.

**去 AI 味。** 读着要像一个语言天赋极强的人写的——自然、通顺、悦耳。**少用**"不是 X，而是 Y"这种工整对仗句式；其他被反复吐槽的模型腔（机械三段排比、空洞的"值得深思 / 综合来看 / 让我们一起"、整齐到僵硬的并列、过度收尾总结）一并避开。

### 8 · Color-coded variables (define once, reuse everywhere)

Recurring key variables / objects across math, SVG, and prose **all share a single color palette**:

```html
<span class="v-x">x</span>      <!-- red -->
<span class="v-y">y</span>      <!-- blue -->
<span class="v-z">z</span>      <!-- green -->
<span class="v-b">b</span>      <!-- purple (target) -->
```

In LaTeX: `\(\textcolor{#dc2626}{x}\)`. In SVG: stroke/fill with the same hex. In prose: inline `<span class="v-x">`. The reader calibrates the palette once; from then on, every formula and figure is parsable without mental relabeling.

Reference: MIT 18.06's `vec-col1/2/3/b` keeps three column vectors and the target the same colors from the row picture → column picture → matrix form → n-dim abstraction.

### 9 · Revealing interactivity (not knob-pushing demos)

Every lab block leads with a single line: **"此 lab 揭示：…（对应来源章节）"**. Useless interactions (input box → display number, slider that only changes a color) are banned. Useful forms include:

- Vector field / manifold visualization (click to drop particles, watch them follow the score).
- Parameter slider → geometric object morphs (two lines' intersection, planes' intersection line, singular vs. non-singular).
- Annealed sequence: from large noise to small noise, frame by frame.
- Multi-step algorithm with step-dot indicator: prev/next buttons, current step highlighted.
- Tab group when there are multiple methods to compare (column method vs. row method = same computation, two perspectives).

### 10 · Editorial-grade webpage feel — 杂志风默认主题

The artifact reads like a Sunday-magazine longread typeset, not Markdown rendered to HTML.

- **Warm paper background** (`#f4ecdd`) with a subtle dotted texture (two layered radial-gradients, 3px / 7px). Body type sits on the paper, never on `#ffffff`. Hero is **not** a dark gradient — it sits on the same paper as the body, just with bigger typography.
- **Type stack**: Playfair Display 800 (display headings, body headings, drop caps, Roman numerals) + Cormorant Garamond italic (decorative italics, ampersand, signoff, sublines, hooks) + Inter (sans eyebrows / labels / metadata) + JetBrains Mono (math-box label, code, lab eyebrow). The display serif stays italic-leaning; do not substitute Space Grotesk or Source Serif 4.
- **Masthead**: a thin black-ruled bar at the top. Left = italic logo ("A Deep Understanding — Private Edition") in Playfair italic; right = volume info in uppercase letterspaced Inter (`letter-spacing: 0.18em`).
- **Hero**: kicker (warm-red, uppercase letterspaced Inter, 12px) → big Playfair `<h1>` 72px with one italic `<em>` for the subtitle phrase and an italic warm-red ampersand for separation → `.subline` (italic Cormorant, 22px) → `.editor-note` framed by `border-top: 4px double` + `border-bottom: 1px` of ink, with a mono uppercase `.label` and an italic Cormorant `.signoff` (e.g. "— 编于周日 22:30，配茶"). Optional `.hero-stats` row + `.meta-line` with a black `.pill` chip and a couple of warm-red links.
- **Section opener (`section.branch`)** is the magazine's signature element. Each section carries `data-accent="red|indigo|forest|amber|plum|slate"`. The accent drives a 7px-thick `<hr class="section-rule">`, the giant Playfair Roman numeral (`I.`–`X.`, 88px), an `<h2>` with one `<strong>` keyword in the accent color, a tiny mono `.branchcode` (e.g. `chapter_3 · articulated humans`), a 1px `<hr class="section-rule thin">`, and an `.ornament` row of glyphs (`§ · § · §` / `◊ · ◊ · ◊` / `¶ · ¶ · ¶`) centered in italic Playfair. Rotate the ornament glyph between consecutive chapters to keep rhythm.
- **Per-section accent rotation**: pick the chapter accent semantically — `red` for problem / results / limits, `indigo` for the core insight chapter and joint-training math, `forest`/`amber`/`plum`/`slate` for parallel topical chapters (when the source has color-coded variables, match the chapter accent to the dominant variable's color so a reader keys both at once). Don't run two consecutive sections with the same accent unless deliberate.
- **Body**: `.lede` first paragraph in Playfair 21px with a giant accent-colored drop cap (80px, floats left). Subsequent paragraphs return to serif reading at 17px / 1.74. Sub-heads `<h3>` use Playfair 700, 23px, with a small mono `.marker` (e.g. `§ 3.2`) prepended.
- **Pull quote `.pullquote`**: paper-soft accent-tinted background, 6px left-border in the accent color, Playfair italic 26–28px. Attribution lives in `.who` (Inter uppercase 12px, letterspaced).
- **Callout matrix** (`.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`) keeps its 6 semantic colors but moves to paper-soft fills (no white surfaces); labels are uppercase letterspaced **Inter**, not mono — eyebrows in the body switch font systematically (sans for callout labels, mono for math/lab/eyebrow). The Feynman block stays a dark plum-bordered card with white italic Cormorant text and an oversized `"` glyph.
- **Math box**: paper-soft fill with a 3px accent left-border. Label in Inter uppercase letterspaced. Math-note in italic Cormorant 15px.
- **Worked example**: paper-soft fill with a 6px **double**-style accent left-border. `we-label` in Inter uppercase. `we-setup` in italic Cormorant. `we-takeaway` keeps the 📌 prefix on a small white pill.
- **Compare cards `.compare > .naive` / `.compare > .insight-card`**: paper-soft fills, no rounded corners, 3px top-border in muted vs. accent. Labels in Inter caps; titles in Playfair 18 700.
- **Tables**: ink-black header bar + paper-soft body. Header text in Inter caps 11px letterspaced. Body cells in Cormorant 15. Numerics in JetBrains Mono right-aligned. `.num.win` in forest, `.num.lose` in muted. `tr.ours-row` gets a forest-tinted highlight.
- **Lab block**: paper-soft container with a 3px accent top-border. `.lab-title` reads `Field Study · Lab N · <name>` in Inter caps. The reveal line stays mandatory. Buttons are flat ink-on-paper, sharp corners, Inter caps. `.btn.toggle.on` flips to the section's accent.
- **Timeline**: dotted hairline rail; dots are accent-colored discs ringed by `box-shadow: 0 0 0 2px var(--accent)`. Year in mono caps, title in Playfair 700, desc in Cormorant.
- **Aside.external**: paper-soft fill with mono uppercase eyebrow ("外部补充 · agent") and warm-red links.
- **Afterword**: an ink-bordered paper-soft "kicker box" near the end of the article — Inter mono label, Playfair italic h4, serif body. Use it for "what I chose / what I excluded".
- **Colophon footer**: italic Cormorant on warm paper, three columns (Citation / Resources / Colophon), each with a tiny Inter-mono uppercase `<h5>`.
- **Chapter divider**: `· · ·` centered, accent-colored at 0.6 opacity.
- **Forbidden**: dark gradient hero, bootstrap-feeling rounded cards, single-column Markdown renders, sans-serif body type, `#ffffff` page background, Source Serif 4 / Space Grotesk substitutions.

Reference exemplars (visual ground truth):
- `~/project/what_new/weekly/2026-19.html` — canonical typography & hero & section-rule pattern.
- `260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — long-read application of the system to a 9-chapter long-read with all components in use.

### 11 · Source figures when they earn it

A magazine runs photographs and plate reproductions next to its illustrations. When the source has imagery that's **clearly relevant** — generated samples, key result figures, dataset examples, physical-apparatus photos, named-people portraits a timeline references — embed it. Visual texture grounds the prose and gives the reader something to look at other than paragraphs and SVGs (增加趣味性).

**Trigger**: the figure carries information the worked-example + SVG diagram can't easily replace. If you'd struggle to write a one-line caption that explains *why this image is here*, skip it.

**Embedding** (the single-file double-click rule still holds):
- **PDF-source figures**: extract with `pdfimages` or `pdftoppm`, then inline as `<img src="data:image/png;base64,…">`. Never reference a local file path. Quality > size; downscale to ≤ 1200px on the long edge so the file stays manageable.
- **Web images**: only from stable pinned URLs (Wikipedia Commons, arXiv-hosted, paper supplementary, the author's project page). Anything not from the source itself goes inside `aside.external`.
- **No AI-generated stock filler.** Decorative slop is worse than no image. Generic "abstract neural network" art especially — banned.
- Every figure gets a `<figcaption>` (italic Cormorant 14–15px) with a mono-uppercase eyebrow like `Figure · 来源 p.7` or `External · Wikipedia`. Constrain width via CSS (`max-width: 100%; height: auto`).

This is **opt-in**, not a checklist requirement. If the source genuinely has nothing photogenic worth keeping, the SVG + worked-example spine carries the page on its own — don't manufacture imagery to fill space. The bar is *clear relevance*, not *image count*.

## Hard constraints

- **Single HTML file.** All CSS/JS inlined or via CDN; images either inlined as base64 data URIs or loaded from pinned public CDNs (see writing principle 11). **No** project-root, `_lib/`, or local-asset references. Double-click to view.
- **Same stem; folder per resolution rule.** Filename always swaps the source extension to `.html`. The folder follows step 1 of the workflow: explicit `<folder>` argument → that folder; otherwise → `/Users/han/project/learn_with_agent/<YYMMDD>/` (today's date, e.g. `260510`).
- **Math.** KaTeX (CDN, auto-render).
- **Code.** Prism or highlight.js (CDN).
- **Style.** Tailwind CDN or hand-written CSS — **Bootstrap is banned**.
- **Fonts.** Google Fonts loads the serif body + mono. **Do not** ship a `system-ui`-only default.
- **No build step.** No npm / vite / webpack.
- **Topic isolation.** Do not read other topic folders.
- **Online research is allowed.** When the agent enriches with external material, mark it explicitly using `aside.external` (source-original vs. agent-added must be visually distinguishable).
- **When unsure**, search the web first. If still uncertain, write the section anyway and mark the spot with `<div class="uncertain">⚠ 此处未充分消化：[原因]</div>`. **Do not interrupt the user with questions.**
- **HTML already exists.** **Overwrite** (re-running grok on the same source means the user wants to replace). Don't touch `_drafts/`.
- **Pin CDN versions** (`katex@0.16.11`, `prismjs@1.29.0`). **No `@latest`.**

### Interactive correctness (don't ship a blank canvas)

The two failure modes that show up most often: **blank canvas** (lab block renders, canvas inside is empty) and **blurry / stretched canvas** (draws fine on the agent's screenshot, looks wrong on the user's retina screen). Guard both:

1. **Render on init.** Every lab IIFE must end with one bare `draw()` call. Never leave the canvas waiting for a first input event — if the user doesn't touch a slider, they see nothing. Wrap each lab in `(function(){ const c = document.getElementById('…'); if (!c) return; … draw(); })();` so a missing element doesn't break the rest of the page.
2. **DPR-scale every canvas.** After `getContext('2d')`, set `c.style.width = cssW + 'px'; c.style.height = cssH + 'px'; c.width = cssW * dpr; c.height = cssH * dpr; ctx.scale(dpr, dpr);`. Drawing then uses CSS pixels but stays sharp on retina.
3. **Lab-prefixed ids.** Two labs cannot share `r1` / `canvas-1`. Prefix every control with the lab name (`lab2-yaw`, `rsc-step`) so a copy-paste doesn't silently cross-wire.
4. **Run the page locally before declaring done.** `open <output-dir>/<name>.html`, scroll to each lab, drag every slider, click every button. If a canvas is blank or a control does nothing, fix before shipping.

## Required component checklist

Every HTML must include the following — missing any of them and the artifact regresses to "text on a page":

1. **Masthead** — thin black-ruled top bar: italic Playfair logo left ("A Deep Understanding — Private Edition") + uppercase letterspaced volume info right.
2. **Hero on warm paper** (no dark gradient) — kicker → big Playfair `<h1>` with one italic `<em>` and a warm-red ampersand → italic Cormorant `.subline` → `.editor-note` framed by double-rule + thin-rule with `.label` and `.signoff` → optional `.hero-stats` row → `.meta-line` with `.pill` chip and warm-red links.
3. **Top progress bar** — `position: fixed; top: 0; height: 2px;` ink color, fills as the reader scrolls.
4. **Right-fixed nav-dot rail** — hover reveals chapter label. Hidden under 1100px. (Sections use `section.branch`, not `section.chapter`.)
5. **Section opener per chapter** — `<section class="branch" data-accent="…">` followed by `<hr class="section-rule">` → `.section-head` (giant Roman numeral + `<h2>` with `<strong>` keyword + tiny `.branchcode`) → `<hr class="section-rule thin">` → `.ornament` glyph row → `.ch-hook` italic one-liner → `.lede` opening paragraph (drop cap fires automatically). Rotate `data-accent` per chapter; never run two consecutive sections with the same accent unless deliberate.
6. **Callout matrix** — at least 3 of: `.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`.
7. **Math box triple** — `<div class="math-box"><div class="math-label">…</div>$$…$$<div class="math-note">…</div></div>`.
8. **Worked example** — a `.worked-example` block per new concept (`we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`).
9. **Naive vs. Insight comparison** — `.compare` two-column grid, naive on left, the source's solution on right; at least one per HTML.
10. **Figures** — at least 1–2 SVG / CSS / emoji-composed conceptual diagrams. **Source figures embedded as base64 (or pinned-CDN external images wrapped in `aside.external`) when clearly relevant** — see writing principle 11. "Figure missing" is not acceptable.
11. **Lab block** — `.lab` container with `Field Study · Lab N · <name>` title in Inter caps + reveal line + canvas (DPR-scaled) + `.ctrl-row` + `.btn-row` + `.lab-note`.
12. **Timeline** (strongly recommended when the source sits in a clear lineage) — historical chain with the latest item flagged `.tl-item.highlight`.
13. **Comparison table** — paper-soft body + ink header bar; mark the source's own row with `tr.ours-row`.
14. **`aside.external`** — every agent-sourced external addition, marked.
15. **Pull quote `.pullquote`** — at least one distilled punch-line, attributed via `.who`.
16. **Editorial divider `· · ·`** — chapter end, accent-colored at 0.6 opacity.
17. **Afterword** — ink-bordered paper-soft kicker box near the article end, with Inter mono `.label`, italic Playfair h4, and a short bullet list of "what I chose / what I excluded".
18. **Colophon footer** — three columns (Citation / Resources / Colophon) on warm paper, italic Cormorant body, tiny Inter-mono uppercase `<h5>` headers.

## HTML skeleton — 杂志风默认主题

The full skeleton lives at [`templates/skeleton.html`](templates/skeleton.html) — a single ~710-line file that already bakes in masthead + warm-paper hero with editor-note + progress bar + right-rail nav + ruled-section openers with Roman numerals + drop-cap lede + callout matrix + math-box + worked-example + naive/insight compare + lab block (DPR-scaled, IIFE-wrapped) + table + feynman + timeline + pullquote + afterword + colophon. Copy it verbatim into the output directory and fill the placeholders. **Do not hand-roll a new skeleton or regress to a single 760px Markdown column or a dark-gradient hero.**

### CSS class quick reference

| Class / element | Purpose | Notes |
|---|---|---|
| `.masthead` `.logo` | Top thin-ruled magazine bar | Italic Playfair logo left, mono uppercase volume info right |
| `.hero` `.kicker` `h1 em` `h1 .ampersand` `.subline` | Editorial hero on warm paper | No dark gradient. `<em>` italic + warm-red `.ampersand` separator |
| `.editor-note` `.label` `.signoff` | Hero contract block | `border-top: 4px double` + `border-bottom: 1px` ink rules |
| `.hero-stats` `.v` `.l` | Optional headline-number row | Big serif value + tiny mono caption |
| `.hero .meta-line` `.pill` | Authors / venue / links row | Black `pill` chip + warm-red `<a>` |
| `#progress` | Top 2px scroll progress bar | Fixed; width tracks scroll fraction; ink color (low saturation) |
| `#rail .dot` | Right-side nav-dot rail | Hover reveals uppercase mono label |
| `section.branch[data-accent]` | Editorial section opener | Accent ∈ {`red`,`indigo`,`forest`,`amber`,`plum`,`slate`} drives `--accent` |
| `.section-rule` `.section-rule.thin` | 7px top + 1px under-rule | Both colored by `--accent` |
| `.section-head .numeral` `.titles h2 strong/em` `.branchcode` | Big Roman numeral + h2 + tiny code | Numeral in 88px Playfair 900; branchcode in mono uppercase |
| `.ornament` | Italic glyph row (`§ · § · §`) | Rotate glyph between consecutive chapters |
| `.ch-hook` | Italic Cormorant one-liner under section opener | Replaces the old `.ch-hook` border style |
| `.lede` | Opening paragraph with drop cap | First letter floats at 80px, colored by `--accent` |
| `.branch h3` `.marker` | Sub-heads inside chapters | Playfair 700 + small mono `§ X.Y` marker |
| `.pullquote` `.who` (also `.pull-quote`) | Inline italic punch-line | 6px accent left-border, paper-soft accent-tinted bg, attribution in mono caps |
| `.math-box` `.math-label` `.math-note` | Math triple | Inter-caps label + LaTeX + italic Cormorant note |
| `.worked-example` `.we-label` `.we-setup` `.we-steps` `.we-takeaway` | Concrete numerical walkthrough | Required per new concept; `we-label` in Inter caps |
| `.insight` `.danger` `.success` `.warning` `.definition` | 5-color semantic callouts | Paper-soft fills; inner `<span class="label">` in Inter caps |
| `.feynman` `.attribution` | Dark plum-bordered meta-insight card | Oversized `"` glyph + italic Cormorant body |
| `.compare > .naive` `.compare > .insight-card` | Naive vs. paper-solution two-col | Sharp-corner paper-soft cards with mono `.label` eyebrow |
| `.lab` `.lab-title` `.lab-reveal` `.ctrl-row` `.btn-row` `.lab-note` | Interactive sandbox | Title reads `Field Study · Lab N · …`; reveal line mandatory |
| `.step-dots .d.active/.done` | Multi-step algorithm state indicator | For sequenced demos |
| `table` `th` `td.num.win/.lose` `tr.ours-row` | Editorial table | Ink header bar + paper-soft body, mono numerics |
| `.timeline` `.tl-item.highlight` `.tl-dot` `.tl-year` `.tl-title` `.tl-desc` | Historical lineage | Highlight item turns warm-red |
| `aside.external` | Agent-sourced external addition | Self-labels with "外部补充 · agent" + warm-red links |
| `.uncertain` | Not-fully-digested marker | Lead with `⚠` |
| `.v-x` `.v-y` `.v-z` `.v-b` | Color-coded variables | Same hex used in formulas / SVG / inline prose |
| `.topic-a/b/c` | Per-topic accent stripe | Only when source has 2–3 parallel concepts |
| `.ch-end` `· · ·` | Chapter divider | Accent-colored at 0.6 opacity; never `<hr>` |
| `.afterword` `.label` `h4` | End-of-article kicker box | Ink-bordered paper-soft frame; for "what I chose / excluded" |
| `.colophon` `.col` `h5` | Three-column footer | Italic Cormorant body + tiny Inter mono caps headers |

## Self-audit checklist (run through every item before shipping)

**Writing / content**
- [ ] **Chapter 0 is begin-with-why**: predicament + naive + fatal flaw + prior-family comparison table + Feynman meta-line. Not "overview of our method."
- [ ] Every chapter has `ch-num` + `ch-title` (with `<strong>` keyword) + `ch-hook` (italic one-liner) + `.lead` opening paragraph.
- [ ] **Every new concept has a `.worked-example`** with `we-label` + `we-setup` + numbered `we-steps` + `we-takeaway`. Numbers are tiny (1, 2, 0, ½). The takeaway names what the example reveals about the abstract form.
- [ ] No paper-boilerplate phrases left in the prose: 本文 / 综上 / 基于此 / 不失一般性 / 值得注意的是 / 显然地 — search and replace.
- [ ] **AI 味自检**："不是 X，而是 Y" 的对仗句式不超过 1–2 处；没有"值得深思 / 综合来看 / 让我们一起 / 总而言之"这类模型口头禅。
- [ ] No paragraph runs longer than 5–6 lines. Dense reasoning paragraphs are interrupted with short sentences, rhetorical questions, or metaphors.
- [ ] Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.

**Visual / components**
- [ ] **Masthead** present (italic logo + uppercase letterspaced volume info, divided by 1px ink rule).
- [ ] **Hero on warm paper** (`#f4ecdd` body + dotted texture, no dark gradient): kicker + Playfair `<h1>` with `<em>` + ampersand + Cormorant `.subline` + `.editor-note` (with double-rule + thin-rule frame, `.label`, `.signoff`).
- [ ] Each chapter is `<section class="branch" data-accent="…">` with **section-rule (7px) → numeral (`I.`–`X.`) → `<h2>` with `<strong>` accent keyword → `.branchcode` → section-rule.thin → ornament**. No bare `.chapter` blocks left over from the old skeleton.
- [ ] **`.lede` opens each chapter** with a drop cap colored by `--accent`. Subsequent paragraphs in serif at 17 / 1.74.
- [ ] **At least one `.pullquote`** with `.who` attribution in the article.
- [ ] **`.afterword`** (ink-bordered kicker box) and **`.colophon`** (three-column italic footer) present.
- [ ] **At least 3 different** callout types in use (not the entire page in `.insight`).
- [ ] At least **1** math-box triple (label + LaTeX + math-note).
- [ ] At least **1** worked example.
- [ ] At least **1** naive vs. insight `.compare` block.
- [ ] At least **1** lab block with `Field Study · Lab N · …` title and the `lab-reveal` line filled in.
- [ ] At least **1** SVG / canvas figure (no "figure missing").
- [ ] If the source sits in a clear lineage, a `.timeline` is present (latest item flagged `.tl-item.highlight`).
- [ ] Recurring key variables are color-coded; the same hex appears in formulas, SVG strokes, and inline prose.
- [ ] Body type is **Playfair Display + Cormorant Garamond**; **callout / hero / branchcode labels in Inter caps**; **math-box / lab / progress / code in JetBrains Mono**. No Source Serif 4 or Space Grotesk leftovers.
- [ ] Chapter accents rotate semantically (red for problem/results/limits, indigo for core insight, forest/amber/plum/slate for parallel topics); no two consecutive sections share an accent unintentionally.
- [ ] Chapter dividers use `· · ·`, accent-colored at 0.6 opacity. Never `<hr>` for divider purposes.
- [ ] Top progress bar (2px ink) and right nav-dot rail are present and functional.

**Technical**
- [ ] Single HTML file. All CDNs pinned to a stable version. No local-asset references.
- [ ] Every `<section class="chapter">` has an `id`. Every rail dot's `data-target` resolves. IntersectionObserver actually highlights the active section.
- [ ] Every agent-added external content is wrapped in `aside.external`.
- [ ] Every not-fully-digested spot is marked with `<div class="uncertain">⚠ …</div>`. No silent TODOs.
- [ ] **Every lab IIFE ends with `draw()`** — no blank canvas on first paint. Verified by opening the file and looking at every lab without touching anything.
- [ ] **Every canvas is DPR-scaled** (CSS width set + `width *= dpr` + `ctx.scale(dpr, dpr)`) — sharp on retina, not stretched. Lab control ids are lab-prefixed; no collisions across labs.

## Gotchas

- **Multiple PDFs in the folder** — ask the user; never default to the first.
- **Mac font fallback** — when `Playfair Display` fails to load, body headings fall back through Cormorant Garamond → Georgia → Times New Roman; when `Inter` fails, through system-ui / Helvetica Neue / Arial; when `JetBrains Mono` fails, through Fira Code → Courier New. The CSS stack is already set up — don't strip the fallbacks.
- **KaTeX + color-coded variables** — inside LaTeX use `\textcolor{#c0392b}{x}` (KaTeX supports it). In plain prose use `<span class="v-x">x</span>`. The hex must match on both sides.
- **`@latest` is forbidden** — every CDN URL pins a stable version (`katex@0.16.11`, `prismjs@1.29.0`) so loads stay reproducible across months.
- **Don't leave silent TODO placeholders** — fully write the section, or mark it explicitly with `.uncertain`.
- **Worked-example pitfalls** — if the example takes more than ~5 steps, it's too big. If you can't extract a one-line takeaway, the example wasn't well-chosen. If the numbers aren't tiny (1, 2, 0, ½, π/4), pick smaller ones. The whole point is "the reader could redo this on a napkin."
- **Self-audit "text on a page"** — if the page is mostly `<p>` and a few `<pre>`, with no masthead, no editor-note hero, no `section-rule` + Roman-numeral openers, no drop-cap lede, no varied callouts, no SVG, no lab block, no worked example, no afterword, no colophon — go back and add components. That's not a delivery.
- **Don't drift back to the old `.chapter` pattern** — the magazine theme uses `section.branch[data-accent]` with section-rule openers. Old `<section class="chapter">` with `.ch-num` / `.ch-title` / `.lead` is deprecated. The IntersectionObserver in the skeleton observes `section.branch` — keep that selector.
- **Don't abuse callouts as paragraph wrappers** — a callout is to highlight one sentence or one proposition, not to box up five paragraphs of body text.
- **TOC / rail must actually work** — every `<section>` needs a real `id`; every rail dot's `data-target` must resolve; the IntersectionObserver in the skeleton must remain wired up.
- **Per-topic accent stripes** — only use `topic-a/b/c` when the source genuinely has 2–3 parallel core concepts (PSNR/SSIM/LPIPS, Score/Langevin/Denoising, …). Otherwise a single `--accent` is enough.
- **Blank canvas / blurry canvas** — the two most common interactive regressions. Blank: the lab's IIFE wires `slider.addEventListener('input', draw)` but never calls `draw()` once at the bottom, so the canvas is empty until someone wiggles the slider. Blurry / stretched: the agent set the canvas's HTML `width` attribute but never DPR-scaled, so on retina the bitmap is half-resolution and CSS stretches it. The skeleton's lab template now bakes both fixes in — copy it verbatim instead of hand-rolling a new lab from scratch.

## See also

- Project-root `AGENTS.md` — reader profile, project-level hard constraints, trigger protocol.
- Reference samples — visual ground truth for the 杂志风 default theme:
  - `~/project/what_new/weekly/2026-19.html` — **canonical** masthead + hero + section-rule pattern; this is the look grok imports.
  - `~/project/learn_with_agent/260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — full long-read application: 10-section long-read with accent rotation across red / indigo / slate / amber / plum / forest, three labs (DPR-scaled), afterword, colophon.
- Reference samples — pedagogical patterns (older visual theme, read for content not visuals):
  - `~/Documents/manus_out/other_reading/Diffusion Concepts Interactive Webpage (1).html` — begin-with-why + multi-semantic callouts + timeline.
  - `~/Documents/manus_out/other_reading/mit1806_lecture1.html` — step animations + color-coded variables + tabbed method comparison.
