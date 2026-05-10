---
name: grok
description: Convert a target folder — containing a paper PDF, book chapter, concept note, codebase entry-point, or any other thing the user is trying to understand — into a same-folder, single-file, CDN-self-contained magazine-style interactive learning HTML — warm-paper background with dotted texture, Playfair Display + Cormorant Garamond + Inter typography, italic-em hero, ruled-section openers with giant Roman numerals, drop caps colored per chapter accent; opens with "begin with why", deconstructs from first principles, walks every new concept through a concrete minimal worked example, 80% of the page goes to the core insights; supports color-coded variables, multi-semantic callouts, lab blocks, and a historical timeline. The generated HTML's natural-language content is in Chinese (the user's reading language); only the skill spec itself is in English. Use when the user runs `/grok <folder>` or asks to "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码" inside the `learn_with_agent` project.
---

# grok

> **Languages.** This skill spec is written in English. The artifact it produces — the interactive HTML — has Chinese natural-language content (chapter titles, prose, callouts, captions). Treat this asymmetry as load-bearing: instructions, comments, and reasoning happen in English; everything the human reader sees in the rendered page is in Chinese.

## Quick start

```
/grok "260506_Coding Agents_alphazero"
/grok "260506_Coding Agents_alphazero" --align
```

Output: `<folder>/<source-name>.html` (same stem as the source file or folder, same folder, single file, all dependencies via CDN).

## Trigger discipline

Enter this skill **only** on explicit user invocation: `/grok <folder>`, or natural-language "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码". Seeing a PDF, Markdown note, e-book, or unfamiliar source folder in the workspace is **not** a trigger — don't proactively start writing.

## Workflow

1. **Locate the input.**
   - Resolve `<folder>` (relative to project root or absolute path).
   - The user names the source — in the invocation, in chat, or via an obviously-named file inside `<folder>`. Read that source. Don't auto-detect: don't glob for `*.pdf` and silently pick one, don't assume a particular file extension.
   - You may also read other files inside the same `<folder>` (pre-extracted notes under `_drafts/`, related figures, supplementary code, sibling source files) when they help you understand. The user-named source is primary; everything else is supplementary.
   - **Do not read other topic folders.** Strict isolation.

2. **Branch on mode.**
   - Default (no `--align`): jump to step 4.
   - With `--align`: run the alignment checkpoint in step 3 first.

3. **Alignment checkpoint (only with `--align`).**
   Output the following in chat **and** write to `<folder>/_drafts/outline.md`. The natural-language content of these items is **in Chinese** because they preview the HTML's content:
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
   - Output filename = PDF filename with `.pdf` → `.html`, same folder.
   - Start from the HTML skeleton below.
   - Follow the writing principles and hard constraints below.
   - Intermediate notes and external references go in `<folder>/_drafts/`.

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

## Hard constraints

- **Single HTML file.** All CSS/JS inlined or via CDN. **No** project-root, `_lib/`, or local-asset references. Double-click to view.
- **Same name, same folder.** HTML lives next to the source, only the extension swaps.
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
4. **Run the page locally before declaring done.** `open <folder>/<name>.html`, scroll to each lab, drag every slider, click every button. If a canvas is blank or a control does nothing, fix before shipping.

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
10. **Figures** — at least 1–2 SVG / CSS / emoji-composed conceptual diagrams. "Figure missing" is not acceptable.
11. **Lab block** — `.lab` container with `Field Study · Lab N · <name>` title in Inter caps + reveal line + canvas (DPR-scaled) + `.ctrl-row` + `.btn-row` + `.lab-note`.
12. **Timeline** (strongly recommended when the source sits in a clear lineage) — historical chain with the latest item flagged `.tl-item.highlight`.
13. **Comparison table** — paper-soft body + ink header bar; mark the source's own row with `tr.ours-row`.
14. **`aside.external`** — every agent-sourced external addition, marked.
15. **Pull quote `.pullquote`** — at least one distilled punch-line, attributed via `.who`.
16. **Editorial divider `· · ·`** — chapter end, accent-colored at 0.6 opacity.
17. **Afterword** — ink-bordered paper-soft kicker box near the article end, with Inter mono `.label`, italic Playfair h4, and a short bullet list of "what I chose / what I excluded".
18. **Colophon footer** — three columns (Citation / Resources / Colophon) on warm paper, italic Cormorant body, tiny Inter-mono uppercase `<h5>` headers.

## HTML skeleton — 杂志风默认主题

Start from this skeleton; expand as needed. It already contains masthead + warm-paper hero with editor-note + progress bar + right-rail nav + ruled-section openers with Roman numerals + drop-cap lede + callout matrix + math-box + worked-example + naive/insight compare + lab block (DPR-scaled) + table + feynman + timeline + pullquote + afterword + colophon. **Do not regress to a single 760px Markdown column or a dark-gradient hero.**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><!-- title (Chinese) --></title>

<!-- Fonts: Playfair (display serif) + Cormorant (decorative italic) + Inter (sans labels) + JetBrains Mono -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;0,900;1,400;1,600&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'\\[',right:'\\]',display:true},
    {left:'$',right:'$',display:false},
    {left:'\\(',right:'\\)',display:false}],throwOnError:false})"></script>

<!-- Prism (code highlighting) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.css">
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>

<style>
  :root{
    /* Warm paper surfaces */
    --paper:      #f4ecdd;
    --paper-soft: #ede2cc;
    --paper-deep: #e6dcc4;
    --ink:        #1a1814;
    --ink-soft:   #4a4438;
    --muted:      #8b8170;
    --hairline:   rgba(26,24,20,0.18);

    /* Editorial accents (per-section --accent picks one) */
    --indigo:    #3b3a8a;
    --warm-red:  #b23a48;
    --forest:    #2f5c3f;
    --amber:     #a86810;
    --plum:      #6c3483;
    --slate:     #1e5a8a;

    /* Color-coded variables — rename to the source's actual variables */
    --v-x:  #c0392b;   /* red */
    --v-y:  #1e5a8a;   /* blue */
    --v-z:  #2d7a4f;   /* green */
    --v-b:  #6c3483;   /* purple (target) */

    /* Defaults; overridden per .branch[data-accent] */
    --accent:    #1a1814;
    --accent-bg: rgba(26,24,20,0.05);

    --serif:      "Playfair Display","Cormorant Garamond",Georgia,serif;
    --serif-text: "Cormorant Garamond","Source Serif 4",Georgia,serif;
    --sans:       "Inter",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
    --mono:       "JetBrains Mono","Fira Code","Courier New",monospace;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  html{scroll-behavior:smooth;}
  body{
    background:var(--paper); color:var(--ink);
    font-family:var(--sans); font-size:17px; line-height:1.62;
    -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
    background-image:
      radial-gradient(rgba(0,0,0,0.018) 1px,transparent 1px),
      radial-gradient(rgba(0,0,0,0.012) 1px,transparent 1px);
    background-size:3px 3px,7px 7px;
    background-position:0 0,1px 2px;
  }
  a{color:inherit;}
  code,pre,.mono{font-family:var(--mono);}

  /* Page shell */
  .page{max-width:1180px;margin:0 auto;padding:56px 64px 88px;}
  @media(max-width:800px){.page{padding:32px 22px 64px;}}

  /* Progress bar (low-saturation) */
  #progress{position:fixed;top:0;left:0;right:0;height:2px;
            background:rgba(0,0,0,0.06);z-index:999;}
  #progress > div{height:100%;width:0;background:var(--ink);transition:width .1s;}

  /* Right-side nav-dot rail */
  #rail{position:fixed;right:18px;top:50%;transform:translateY(-50%);
        display:flex;flex-direction:column;gap:8px;z-index:100;}
  #rail .dot{width:9px;height:9px;border-radius:50%;
       background:rgba(26,24,20,0.18);cursor:pointer;position:relative;
       transition:all .2s;}
  #rail .dot:hover,#rail .dot.active{background:var(--ink);transform:scale(1.4);}
  #rail .dot .lbl{position:absolute;right:18px;top:50%;transform:translateY(-50%);
            background:var(--ink);color:var(--paper);
            padding:4px 9px;font-family:var(--sans);font-size:.68rem;
            white-space:nowrap;opacity:0;letter-spacing:.08em;text-transform:uppercase;
            pointer-events:none;transition:opacity .2s;}
  #rail .dot:hover .lbl{opacity:1;}
  @media(max-width:1100px){#rail{display:none;}}

  /* Masthead (top thin-ruled bar) */
  .masthead{display:flex;justify-content:space-between;align-items:flex-end;
    border-bottom:1px solid var(--ink);padding-bottom:14px;margin-bottom:32px;
    font-family:var(--sans);text-transform:uppercase;letter-spacing:0.18em;
    font-size:11px;color:var(--ink-soft);}
  .masthead .logo{font-family:var(--serif);font-style:italic;font-weight:600;
    font-size:18px;letter-spacing:0.04em;text-transform:none;color:var(--ink);}

  /* Hero */
  .hero{margin:28px 0 56px;}
  .hero .kicker{font-family:var(--sans);font-size:12px;
    text-transform:uppercase;letter-spacing:0.32em;
    color:var(--warm-red);margin-bottom:18px;}
  .hero h1{font-family:var(--serif);font-weight:800;
    font-size:72px;line-height:0.98;letter-spacing:-0.012em;margin:0 0 14px;}
  .hero h1 em{font-family:"Cormorant Garamond",serif;
    font-style:italic;font-weight:600;color:var(--warm-red);}
  .hero h1 .ampersand{font-family:"Cormorant Garamond",serif;
    font-style:italic;font-weight:400;color:var(--warm-red);}
  .hero .subline{font-family:var(--serif);font-style:italic;
    font-size:22px;color:var(--ink-soft);margin:6px 0 26px;max-width:780px;}
  .editor-note{border-top:4px double var(--ink);border-bottom:1px solid var(--ink);
    padding:22px 0 24px;max-width:780px;
    font-family:var(--serif);font-size:19px;line-height:1.55;color:var(--ink);}
  .editor-note .label{display:block;font-family:var(--sans);font-size:11px;
    letter-spacing:0.28em;text-transform:uppercase;color:var(--warm-red);margin-bottom:10px;}
  .editor-note .signoff{display:block;margin-top:14px;font-style:italic;
    color:var(--ink-soft);font-size:16px;}
  .hero-stats{display:flex;flex-wrap:wrap;gap:30px;margin:30px 0 0;
    padding-top:18px;border-top:1px dotted var(--hairline);}
  .hero-stats .v{font-family:var(--serif);font-weight:800;font-size:30px;
    color:var(--warm-red);display:block;line-height:1;}
  .hero-stats .l{font-family:var(--sans);font-size:10.5px;letter-spacing:0.22em;
    color:var(--ink-soft);text-transform:uppercase;margin-top:4px;display:block;}
  .hero .meta-line{margin-top:24px;font-family:var(--sans);font-size:12px;
    letter-spacing:0.04em;color:var(--ink-soft);
    display:flex;flex-wrap:wrap;gap:18px;align-items:center;}
  .hero .meta-line .pill{font-family:var(--sans);font-size:10.5px;
    letter-spacing:0.18em;text-transform:uppercase;font-weight:600;
    background:var(--ink);color:var(--paper);padding:5px 11px;}
  .hero .meta-line a{color:var(--warm-red);text-decoration:none;
    border-bottom:1px solid var(--warm-red);}
  @media(max-width:800px){.hero h1{font-size:46px;}.hero .subline{font-size:18px;}
    .editor-note{font-size:17px;}}

  /* Section opener (.branch) — magazine signature */
  section.branch{margin:88px 0 0;}
  .section-rule{height:7px;border:0;background:var(--accent);margin:0 0 6px;}
  .section-rule.thin{height:1px;margin-top:6px;margin-bottom:28px;}
  .section-head{display:flex;align-items:baseline;justify-content:space-between;
    gap:24px;flex-wrap:wrap;margin:14px 0 8px;}
  .section-head .head-l{display:flex;align-items:baseline;}
  .section-head .numeral{font-family:var(--serif);font-weight:900;
    font-size:88px;line-height:1;letter-spacing:-0.02em;
    color:var(--accent);margin-right:18px;}
  .section-head .titles{flex:1 1 360px;}
  .section-head h2{font-family:var(--serif);font-weight:800;
    font-size:38px;line-height:1.05;margin:0 0 6px;letter-spacing:-0.005em;}
  .section-head h2 strong{color:var(--accent);font-weight:800;}
  .section-head h2 em{font-style:italic;font-family:"Cormorant Garamond",serif;
    font-weight:600;color:var(--accent);}
  .section-head .branchcode{font-family:var(--sans);font-size:11px;
    text-transform:uppercase;letter-spacing:0.28em;color:var(--ink-soft);}
  .ornament{font-family:var(--serif);font-style:italic;font-size:22px;
    color:var(--accent);text-align:center;letter-spacing:0.4em;
    opacity:0.85;margin:6px 0 4px;}
  .ch-hook{font-family:var(--serif);font-style:italic;color:var(--ink-soft);
    font-size:18px;margin:14px 0 4px;}

  /* Per-section accent palettes */
  .branch[data-accent="red"]    { --accent:var(--warm-red); --accent-bg:rgba(178,58,72,0.08); }
  .branch[data-accent="indigo"] { --accent:var(--indigo);   --accent-bg:rgba(59,58,138,0.08); }
  .branch[data-accent="forest"] { --accent:var(--forest);   --accent-bg:rgba(47,92,63,0.08); }
  .branch[data-accent="amber"]  { --accent:var(--amber);    --accent-bg:rgba(196,122,24,0.10); }
  .branch[data-accent="plum"]   { --accent:var(--plum);     --accent-bg:rgba(108,52,131,0.08); }
  .branch[data-accent="slate"]  { --accent:var(--slate);    --accent-bg:rgba(30,90,138,0.08); }

  /* Body / drop cap */
  .lede{font-family:var(--serif);font-size:21px;line-height:1.5;
    margin:22px 0 24px;max-width:780px;}
  .lede::first-letter{font-family:var(--serif);font-weight:800;
    font-size:80px;line-height:0.86;float:left;
    padding:6px 12px 0 0;margin-top:6px;color:var(--accent);}
  .branch p,.branch ul,.branch ol{max-width:780px;}
  .branch p{margin:0 0 16px;font-family:var(--serif);font-size:17px;line-height:1.74;}
  .branch ul,.branch ol{margin:0 0 16px;padding-left:22px;font-family:var(--serif);font-size:17px;line-height:1.7;}
  .branch li{margin-bottom:6px;}
  .branch h3{font-family:var(--serif);font-weight:700;font-size:23px;line-height:1.25;
    color:var(--ink);margin:36px 0 12px;letter-spacing:-0.005em;max-width:780px;}
  .branch h3 .marker{font-family:var(--mono);font-size:11px;
    color:var(--muted);font-weight:500;margin-right:10px;letter-spacing:0.1em;}

  /* Color-coded variables (define once, reuse everywhere) */
  .v-x{color:var(--v-x);font-weight:600;}
  .v-y{color:var(--v-y);font-weight:600;}
  .v-z{color:var(--v-z);font-weight:600;}
  .v-b{color:var(--v-b);font-weight:600;}

  /* Optional per-topic stripes (when source has 2-3 parallel topics) */
  .topic-a,.topic-b,.topic-c{position:relative;padding-left:18px;}
  .topic-a::before,.topic-b::before,.topic-c::before{
    content:"";position:absolute;left:0;top:.35em;bottom:.35em;width:3px;border-radius:2px;}
  .topic-a::before{background:var(--indigo);}
  .topic-b::before{background:var(--forest);}
  .topic-c::before{background:var(--warm-red);}

  /* Pull quote */
  .pullquote,.pull-quote{margin:34px 0;padding:22px 26px 22px 28px;
    border-left:6px solid var(--accent);background:var(--accent-bg);
    font-family:var(--serif);font-style:italic;
    font-size:26px;line-height:1.32;letter-spacing:-0.005em;
    max-width:880px;color:var(--accent);}
  .pullquote .who{display:block;margin-top:14px;font-style:normal;
    font-family:var(--sans);font-size:12px;letter-spacing:0.22em;
    text-transform:uppercase;color:var(--ink-soft);}

  /* Math box (KaTeX wrapper) */
  .math-box{background:var(--paper-soft);border:1px solid var(--hairline);
    border-left:3px solid var(--accent);padding:18px 22px;margin:22px 0;
    overflow-x:auto;max-width:880px;}
  .math-box .math-label{font-family:var(--sans);font-size:10.5px;
    letter-spacing:0.22em;text-transform:uppercase;
    color:var(--accent);font-weight:600;margin-bottom:10px;}
  .math-box .math-note{font-family:var(--serif);font-size:15px;
    color:var(--ink-soft);margin-top:12px;font-style:italic;line-height:1.6;}
  .math-box .math-note strong{font-style:normal;color:var(--ink);}

  /* Worked example */
  .worked-example{background:var(--paper-soft);border-left:6px double var(--accent);
    padding:18px 22px;margin:22px 0;max-width:880px;}
  .worked-example .we-label{font-family:var(--sans);font-size:11px;
    letter-spacing:0.22em;text-transform:uppercase;color:var(--accent);
    font-weight:700;margin-bottom:10px;display:block;}
  .worked-example .we-setup{font-family:var(--serif);font-style:italic;
    color:var(--ink-soft);margin-bottom:10px;}
  .worked-example .we-steps{margin:6px 0 6px 22px;padding:0;font-family:var(--serif);}
  .worked-example .we-steps li{margin:4px 0;}
  .worked-example .we-takeaway{margin-top:12px;padding:10px 14px;
    background:rgba(255,255,255,.7);font-size:.94rem;
    color:var(--ink-soft);font-family:var(--serif);}
  .worked-example .we-takeaway::before{content:"📌 ";}

  /* Callout matrix */
  .insight,.danger,.success,.warning,.definition{
    border-left:4px solid;background:var(--paper-soft);
    padding:16px 22px;margin:22px 0;max-width:880px;font-family:var(--serif);}
  .insight    {border-color:var(--indigo);   background:rgba(59,58,138,0.06);}
  .danger     {border-color:var(--warm-red); background:rgba(178,58,72,0.06);}
  .success    {border-color:var(--forest);   background:rgba(47,92,63,0.06);}
  .warning    {border-color:var(--amber);    background:rgba(168,104,16,0.08);}
  .definition {border-color:var(--plum);     background:rgba(108,52,131,0.06);}
  .insight .label,.danger .label,.success .label,
  .warning .label,.definition .label{
    font-family:var(--sans);font-size:10.5px;
    letter-spacing:0.22em;text-transform:uppercase;font-weight:700;
    margin-bottom:8px;display:block;}
  .insight    .label{color:var(--indigo);}
  .danger     .label{color:var(--warm-red);}
  .success    .label{color:var(--forest);}
  .warning    .label{color:var(--amber);}
  .definition .label{color:var(--plum);}
  .insight p,.danger p,.success p,.warning p,.definition p{margin:0 0 8px;font-size:16px;line-height:1.66;}

  /* Feynman block (dark plum-bordered card) */
  .feynman{background:#262432;color:#ece6f4;
    padding:24px 30px 22px;margin:30px 0;position:relative;
    max-width:880px;border-left:4px solid var(--plum);}
  .feynman::before{content:"\201C";position:absolute;top:-8px;left:18px;
    font-size:5rem;color:#5a4a8a;font-family:Georgia,serif;line-height:1;}
  .feynman p{font-family:var(--serif);font-style:italic;color:#dcd6f0;
    margin:0 0 8px;font-size:18px;line-height:1.55;}
  .feynman .attribution{color:#9890b8;font-size:11px;font-style:normal;
    font-family:var(--sans);letter-spacing:0.18em;text-transform:uppercase;}

  /* Compare cards */
  .compare{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:26px 0;max-width:880px;}
  @media(max-width:800px){.compare{grid-template-columns:1fr;}}
  .compare > div{border:1px solid var(--hairline);background:var(--paper-soft);
    padding:18px 20px;}
  .compare .naive       {border-top:3px solid var(--muted);}
  .compare .insight-card{border-top:3px solid var(--accent);}
  .compare .label{font-family:var(--sans);font-size:10.5px;
    letter-spacing:0.18em;text-transform:uppercase;color:var(--muted);
    margin-bottom:6px;display:block;font-weight:600;}
  .compare .insight-card .label{color:var(--accent);}
  .compare h4{font-family:var(--serif);font-size:18px;font-weight:700;
    color:var(--ink);margin:0 0 8px;}
  .compare ul{margin:6px 0 0 18px;font-size:15px;line-height:1.6;}
  .compare li{margin-bottom:4px;}

  /* Lab block (interactive sandbox) */
  .lab{background:var(--paper-soft);border:1px solid var(--hairline);
    border-top:3px solid var(--accent);padding:24px 26px;margin:32px 0;max-width:1000px;}
  .lab-title{font-family:var(--sans);font-size:11px;
    letter-spacing:0.22em;text-transform:uppercase;
    color:var(--accent);font-weight:700;
    margin-bottom:8px;display:flex;align-items:center;gap:8px;}
  .lab-reveal{font-family:var(--serif);font-style:italic;
    font-size:15px;color:var(--ink-soft);margin-bottom:16px;line-height:1.6;}
  .lab canvas,.lab svg{display:block;margin:0 auto;max-width:100%;
    background:#fff;border:1px solid var(--hairline);}
  .ctrl-row{display:flex;align-items:center;gap:14px;margin-top:14px;
    flex-wrap:wrap;font-family:var(--mono);font-size:13px;}
  .ctrl-row label{color:var(--muted);min-width:80px;}
  .ctrl-row input[type=range]{flex:1;min-width:140px;accent-color:var(--accent);}
  .ctrl-val{color:var(--accent);min-width:54px;text-align:right;font-weight:600;}
  .btn-row{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;}
  .btn{padding:7px 14px;background:var(--ink);color:var(--paper);
    border:none;cursor:pointer;font-size:12px;font-family:var(--sans);
    transition:opacity .15s;letter-spacing:0.1em;text-transform:uppercase;font-weight:600;}
  .btn:hover{opacity:.84;}
  .btn.outline{background:transparent;border:1px solid var(--ink);color:var(--ink);}
  .btn.toggle.on{background:var(--accent);}
  .btn.toggle{background:var(--muted);}
  .lab-note{font-family:var(--serif);font-style:italic;
    font-size:14px;color:var(--ink-soft);margin-top:14px;line-height:1.62;}
  .step-dots{display:flex;gap:6px;margin-top:12px;}
  .step-dots .d{width:8px;height:8px;border-radius:50%;background:rgba(26,24,20,0.18);}
  .step-dots .d.active{background:var(--accent);}
  .step-dots .d.done{background:var(--muted);}

  /* Tables */
  table{width:100%;max-width:880px;border-collapse:collapse;margin:24px 0;
    font-size:14.5px;background:var(--paper-soft);
    border-top:2px solid var(--ink);border-bottom:2px solid var(--ink);}
  th{background:var(--ink);color:var(--paper);
    padding:10px 14px;text-align:left;font-weight:600;
    font-family:var(--sans);font-size:11px;
    letter-spacing:0.14em;text-transform:uppercase;}
  td{padding:10px 14px;border-bottom:1px solid var(--hairline);
    vertical-align:top;font-family:var(--serif);font-size:15px;}
  tr:last-child td{border-bottom:0;}
  tr:hover td{background:var(--paper-deep);}
  .num{font-family:var(--mono);text-align:right;font-size:13.5px;}
  .num.win{color:var(--forest);font-weight:700;}
  .num.lose{color:var(--muted);}
  tr.ours-row td{background:rgba(47,92,63,0.10) !important;font-weight:600;}

  /* External (agent-sourced supplementary) */
  aside.external{display:block;background:var(--paper-soft);
    border-left:3px solid var(--muted);padding:14px 20px;margin:22px 0;max-width:880px;
    font-family:var(--serif);font-size:15px;color:var(--ink-soft);line-height:1.66;}
  aside.external::before{content:"外部补充 · agent";display:block;
    font-family:var(--sans);font-size:10.5px;letter-spacing:0.22em;
    color:var(--muted);margin-bottom:6px;text-transform:uppercase;font-weight:600;}
  aside.external a{color:var(--warm-red);text-decoration:none;
    border-bottom:1px solid var(--warm-red);}

  /* Uncertain marker */
  .uncertain{border-left:4px solid var(--amber);background:rgba(168,104,16,0.10);
    padding:12px 18px;margin:18px 0;font-size:15px;font-family:var(--serif);max-width:880px;}

  /* Timeline */
  .timeline{position:relative;padding-left:28px;margin:28px 0;max-width:880px;}
  .timeline::before{content:'';position:absolute;left:7px;top:8px;bottom:8px;
    width:2px;background:var(--hairline);}
  .tl-item{position:relative;margin-bottom:24px;}
  .tl-dot{position:absolute;left:-24px;top:7px;width:11px;height:11px;
    border-radius:50%;background:var(--accent);
    border:2px solid var(--paper);box-shadow:0 0 0 2px var(--accent);}
  .tl-item.highlight .tl-dot{background:var(--warm-red);box-shadow:0 0 0 2px var(--warm-red);}
  .tl-year{font-family:var(--mono);font-size:12px;color:var(--accent);
    font-weight:700;margin-bottom:2px;letter-spacing:0.04em;}
  .tl-title{font-family:var(--serif);font-weight:700;font-size:17.5px;
    color:var(--ink);margin-bottom:2px;}
  .tl-desc{font-family:var(--serif);color:var(--ink-soft);font-size:15.5px;line-height:1.6;}

  /* Editorial divider */
  .ch-end{text-align:center;margin:52px 0 12px;
    color:var(--accent);font-size:1.2rem;letter-spacing:.6em;opacity:0.6;}

  /* Code */
  pre[class*="language-"]{padding:14px 18px !important;font-size:.86rem;max-width:880px;}

  /* Afterword (kicker box near the end) */
  .afterword{margin-top:96px;padding:28px 32px 30px;
    border:1px solid var(--ink);background:var(--paper-soft);max-width:880px;}
  .afterword h4{font-family:var(--serif);font-style:italic;font-weight:600;
    font-size:22px;margin:0 0 12px;color:var(--ink-soft);}
  .afterword p,.afterword li{font-family:var(--serif);font-size:15px;line-height:1.66;}
  .afterword ul{margin:6px 0 0;padding-left:20px;}
  .afterword .label{display:inline-block;font-family:var(--sans);font-size:11px;
    letter-spacing:0.22em;text-transform:uppercase;
    color:var(--warm-red);margin-bottom:8px;font-weight:600;}

  /* Colophon footer */
  .colophon{margin-top:56px;padding-top:18px;border-top:1px solid var(--ink);
    display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px;
    font-family:var(--serif);font-style:italic;font-size:14px;color:var(--ink-soft);}
  .colophon .col{flex:1 1 220px;}
  .colophon h5{font-family:var(--sans);font-size:10.5px;letter-spacing:0.22em;
    color:var(--muted);margin:0 0 8px;font-weight:600;text-transform:uppercase;font-style:normal;}
  .colophon a{color:var(--ink-soft);}

  @media(max-width:800px){
    .section-head .numeral{font-size:64px;}
    .section-head h2{font-size:28px;}
    .lede{font-size:18px;}
    .lede::first-letter{font-size:60px;}
    .pullquote{font-size:20px;}
  }
</style>
</head>
<body>

<div id="progress"><div></div></div>

<nav id="rail" aria-label="章节导航">
  <div class="dot active" data-target="ch0"><span class="lbl">困境</span></div>
  <div class="dot" data-target="ch1"><span class="lbl">关键 insight</span></div>
  <div class="dot" data-target="chN"><span class="lbl">脉络</span></div>
  <!-- add more as needed -->
</nav>

<div class="page">

<!-- ============ MASTHEAD ============ -->
<header class="masthead">
  <div class="logo">A Deep Understanding &mdash; Private Edition</div>
  <div>Vol. <!-- year --> &middot; <!-- short source handle --> &middot; <!-- venue --></div>
</header>

<!-- ============ HERO ============ -->
<section class="hero">
  <div class="kicker">Paper Reading &middot; 第一性原理 &middot; Karpathy 风格 &middot; ~XX min</div>
  <h1><!-- main title (Chinese) --><span class="ampersand"> &mdash; </span><em><!-- subtitle phrase (Chinese) --></em></h1>
  <p class="subline"><!-- one-sentence thesis (Chinese): what this source solves and what the key insight is --></p>

  <div class="editor-note">
    <span class="label">Editor&rsquo;s Note &middot; 阅读契约</span>
    <!-- 2-3 sentences telling the reader the chapter map and what trade you're making with the page budget. -->
    <span class="signoff">&mdash; grok / <!-- ISO date -->，配茶</span>
  </div>

  <!-- optional hero stats -->
  <div class="hero-stats">
    <div><span class="v">+X.X</span><span class="l">headline metric</span></div>
    <div><span class="v">YY%</span><span class="l">improvement</span></div>
  </div>

  <div class="meta-line">
    <span class="pill"><!-- venue / year --></span>
    <span><!-- authors et al. --></span>
    <span><!-- affiliations --></span>
    <a href="./<!-- same-name PDF -->">原 PDF</a>
    <a href="https://arxiv.org/abs/XXXX.XXXXX">arXiv</a>
  </div>
</section>

<!-- ═══ Chapter 0 — field-level predicament (begin with why) ═══ -->
<section class="branch" data-accent="red" id="ch0">
  <hr class="section-rule" />
  <div class="section-head">
    <div class="head-l">
      <div class="numeral">I.</div>
      <div class="titles">
        <h2>领域级<strong>根本困境</strong></h2>
        <div class="branchcode">chapter_0 &middot; the diagnosis</div>
      </div>
    </div>
  </div>
  <hr class="section-rule thin" />
  <div class="ornament">&sect; &nbsp;&middot;&nbsp; &sect; &nbsp;&middot;&nbsp; &sect;</div>

  <p class="ch-hook">在欢呼&ldquo;<!-- new paradigm name -->&rdquo;之前，先看清这道题原本卡在哪。</p>

  <p class="lede"><!-- concrete physical scenario in Chinese: assume you have X, you want Y, mathematically this means Z. The drop cap appears on the first letter automatically. --></p>

  <p><!-- translate Y to math; first appearance of key variables — assign them colors via <span class="v-x">x</span> etc. --></p>

  <div class="insight">
    <span class="label">领域级硬题</span>
    <p><!-- one-sentence statement of the field-wide bottleneck --></p>
  </div>

  <h3><span class="marker">§ 0.1</span>最自然的做法 = <!-- naive approach --></h3>

  <div class="math-box">
    <div class="math-label"><!-- e.g. Naive · 直接建模 p(x) --></div>
    \[ <!-- naive formula --> \]
    <div class="math-note"><!-- plain-Chinese explanation. Use <strong> to mark the killer assumption. --></div>
  </div>

  <div class="danger">
    <span class="label">致命问题</span>
    <p><!-- why the naive idea is dead-on-arrival --></p>
  </div>

  <table>
    <tr><th>路线</th><th>怎么绕开</th><th>代价</th></tr>
    <tr><td><strong>VAE</strong></td><td>用 ELBO 近似下界</td><td>样本质量受限</td></tr>
    <tr><td><strong>GAN</strong></td><td>不建模 p(x)，用判别器</td><td>训练不稳定</td></tr>
    <tr class="ours-row"><td><strong>本作</strong></td><td><!-- … --></td><td><!-- … --></td></tr>
  </table>

  <div class="feynman">
    <p>如果你不能直接解决一个问题，先问：我真正需要的是什么？也许我需要的比我以为的少得多。</p>
    <div class="attribution">&mdash; 本作的元洞察，下一章展开</div>
  </div>

  <div class="ch-end">&middot; &middot; &middot;</div>
</section>

<!-- ═══ Chapter 1 — key insight ═══ -->
<section class="branch" data-accent="indigo" id="ch1">
  <hr class="section-rule" />
  <div class="section-head">
    <div class="head-l">
      <div class="numeral">II.</div>
      <div class="titles">
        <h2>天才洞察：<strong><!-- key concept (Chinese) --></strong></h2>
        <div class="branchcode">chapter_1 &middot; the key insight</div>
      </div>
    </div>
  </div>
  <hr class="section-rule thin" />
  <div class="ornament">&loz; &nbsp;&middot;&nbsp; &loz; &nbsp;&middot;&nbsp; &loz;</div>

  <p class="ch-hook"><!-- italic one-line hook (Chinese) --></p>

  <p class="lede"><!-- physical intuition first --></p>

  <p><!-- translate the intuition to math; introduce new symbols using v-x/y/z color spans --></p>

  <div class="math-box">
    <div class="math-label"><!-- e.g. Score Function --></div>
    \[ s(x) = \nabla_x \log p(x) \]
    <div class="math-note"><!-- plain Chinese: gradient of log-density; at every point it points "uphill in probability" --></div>
  </div>

  <!-- Worked example for principle 3: smallest concrete instance -->
  <div class="worked-example">
    <span class="we-label">Worked example &middot; 1D 标准正态</span>
    <div class="we-setup">取 <span class="v-x">p(x) = (1/&radic;2&pi;)&middot;e^(&minus;x&sup2;/2)</span>，求 <span class="v-y">s(x) = &nabla;log p(x)</span>。</div>
    <ol class="we-steps">
      <li>log p(x) = &minus;x&sup2;/2 &minus; log&radic;(2&pi;)</li>
      <li>&nabla; log p(x) = &minus;x</li>
      <li>所以 <span class="v-y">s(x) = &minus;x</span>。在 <span class="v-x">x = 2</span> 处，score = &minus;2，长度等于距离，方向指回原点。</li>
    </ol>
    <div class="we-takeaway">&ldquo;score&rdquo; 对正态分布只是<strong>负的位置</strong>&mdash;&mdash;每个点都被以&ldquo;距离&rdquo;为大小的力拉回零点。换成混合分布、流形数据后，这张&ldquo;拉回最近高密度区&rdquo;的图像就成了 Langevin 采样的物理基础。</div>
  </div>

  <div class="success">
    <span class="label">关键突破</span>
    <p><!-- why this insight dissolves the predicament --></p>
  </div>

  <blockquote class="pullquote">&ldquo;<!-- a one-line distillation of the chapter's punchline -->&rdquo;
    <span class="who">&mdash; 章节核心 &middot; <!-- short attribution --></span>
  </blockquote>

  <div class="lab" id="lab1">
    <div class="lab-title">Field Study &middot; Lab 1 &middot; <!-- lab name (Chinese) --></div>
    <p class="lab-reveal">此 lab 揭示：<!-- specific insight --> &middot; 对应来源章节</p>
    <canvas id="lab1-canvas" width="760" height="320"></canvas>
    <div class="ctrl-row">
      <label>参数 &sigma;</label>
      <input type="range" id="lab1-sigma" min="0" max="1" step=".01" value=".5">
      <span class="ctrl-val" id="lab1-sigmaV">0.50</span>
    </div>
    <div class="btn-row">
      <button class="btn" id="lab1-run">运行</button>
      <button class="btn outline" id="lab1-reset">重置</button>
    </div>
    <div class="lab-note"><!-- what to do + what to watch for --></div>
  </div>

  <div class="ch-end">&middot; &middot; &middot;</div>
</section>

<!-- ═══ Chapter N — historical lineage (when applicable) ═══ -->
<section class="branch" data-accent="slate" id="chN">
  <hr class="section-rule" />
  <div class="section-head">
    <div class="head-l">
      <div class="numeral">N.</div>
      <div class="titles">
        <h2>这条路是怎么走过来的：<strong>历史脉络</strong></h2>
        <div class="branchcode">chapter_N &middot; the lineage</div>
      </div>
    </div>
  </div>
  <hr class="section-rule thin" />
  <div class="ornament">&para; &nbsp;&middot;&nbsp; &para; &nbsp;&middot;&nbsp; &para;</div>

  <p class="ch-hook">本作不是凭空冒出来的。</p>

  <div class="timeline">
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2005 &middot; Hyv&auml;rinen</div>
      <div class="tl-title">Score Matching</div>
      <div class="tl-desc">证明可以不用 Z 来学 score function，但计算代价高</div>
    </div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2011 &middot; Vincent</div>
      <div class="tl-title">Denoising Score Matching</div>
      <div class="tl-desc">去噪 = 学 score，计算高效</div>
    </div>
    <div class="tl-item highlight">
      <div class="tl-dot"></div>
      <div class="tl-year"><!-- year · 本作 --></div>
      <div class="tl-title"><!-- 本作 title --></div>
      <div class="tl-desc"><!-- one-line distillation of how it builds on the prior step --></div>
    </div>
  </div>

  <div class="ch-end">&middot; &middot; &middot;</div>
</section>

<!-- ============ AFTERWORD ============ -->
<aside class="afterword">
  <span class="label">阅读说明 &middot; Afterword</span>
  <h4>关于这次整理我做了哪些选择</h4>
  <p><!-- 2-3 lines on what got 80% of the page budget and why; explicitly note any uncertain spots and any topics deliberately collapsed to a footnote --></p>
  <ul>
    <li><strong>章节配色</strong>：<!-- which accents map to which chapters and why --></li>
    <li><strong>变量颜色</strong>：<!-- which symbols share which colors --></li>
    <li><strong>未收</strong>：<!-- topics intentionally not covered --></li>
  </ul>
</aside>

<!-- ============ COLOPHON ============ -->
<footer class="colophon">
  <div class="col">
    <h5>Citation</h5>
    <!-- inline BibTeX line -->
  </div>
  <div class="col">
    <h5>Resources</h5>
    <a href="./<!-- same-name PDF -->">原 PDF</a><br/>
    <a href="https://arxiv.org/abs/XXXX.XXXXX">arXiv</a><br/>
    <!-- project page / code if any -->
  </div>
  <div class="col">
    <h5>Colophon</h5>
    Set in Playfair Display &amp; Cormorant Garamond &amp; Inter.<br/>
    Math by KaTeX, code by Prism.<br/>
    Single file &middot; CDN-self-contained.<br/>
    Generated <!-- ISO timestamp --> by grok.
  </div>
</footer>

</div>

<script>
  /* Top progress bar — width tracks scroll fraction */
  const prog = document.querySelector('#progress > div');
  window.addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = (h.scrollTop) / Math.max(1, h.scrollHeight - h.clientHeight);
    prog.style.width = (p * 100) + '%';
  }, { passive: true });

  /* Right-rail dot highlight via IntersectionObserver — sections use .branch now */
  const dots = document.querySelectorAll('#rail .dot');
  const sections = [...document.querySelectorAll('section.branch')];
  dots.forEach(d => d.addEventListener('click', () => {
    const t = document.getElementById(d.dataset.target);
    if (t) t.scrollIntoView({ behavior: 'smooth' });
  }));
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        dots.forEach(d => d.classList.toggle('active', d.dataset.target === e.target.id));
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach(s => io.observe(s));

  /* ─── Lab 1 wiring ─── template every lab MUST follow:
     1) IIFE so labs don't leak globals or collide on var names.
     2) `if (!c) return` so a missing element doesn't break the page.
     3) DPR scaling so canvas stays sharp on retina without stretching.
     4) Bottom-of-IIFE `draw()` so the canvas renders on first paint —
        do NOT rely on the user touching a slider for the first frame. */
  (function(){
    const c = document.getElementById('lab1-canvas');
    if (!c) return;
    const cssW = c.width, cssH = c.height;
    const dpr  = window.devicePixelRatio || 1;
    c.style.width  = cssW + 'px';
    c.style.height = cssH + 'px';
    c.width  = cssW * dpr;
    c.height = cssH * dpr;
    const ctx = c.getContext('2d');
    ctx.scale(dpr, dpr);

    const slider = document.getElementById('lab1-sigma');
    const valLbl = document.getElementById('lab1-sigmaV');
    const btnRun = document.getElementById('lab1-run');
    const btnRst = document.getElementById('lab1-reset');

    function draw(){
      const sigma = parseFloat(slider.value);
      valLbl.textContent = sigma.toFixed(2);
      ctx.clearRect(0, 0, cssW, cssH);
      // … source-specific drawing, in CSS pixels, using `sigma` …
    }

    slider.addEventListener('input', draw);
    btnRun.addEventListener('click', draw);
    btnRst.addEventListener('click', () => { slider.value = 0.5; draw(); });

    draw();   // render immediately — never ship a blank canvas
  })();
</script>

</body>
</html>
```

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
