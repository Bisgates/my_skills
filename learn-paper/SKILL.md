---
name: learn-paper
description: Convert a paper PDF in a target folder into a same-folder, single-file, CDN-self-contained editorial-grade interactive learning HTML — warm paper background, serif body, mono eyebrow labels, chapter-level color coding; opens with "begin with why", deconstructs from first principles, walks every new concept through a concrete minimal worked example, 80% of the page goes to the core insights; supports color-coded variables, multi-semantic callouts, lab blocks, and a historical timeline. The generated HTML's natural-language content is in Chinese (the user's reading language); only the skill spec itself is in English. Use when the user runs `/learn-paper <folder>` or asks to "学习 / 讲解 / 拆解 X 文件夹里的 paper" inside the `learn_with_agent` project.
---

# learn-paper

> **Languages.** This skill spec is written in English. The artifact it produces — the interactive HTML — has Chinese natural-language content (chapter titles, prose, callouts, captions). Treat this asymmetry as load-bearing: instructions, comments, and reasoning happen in English; everything the human reader sees in the rendered page is in Chinese.

## Quick start

```
/learn-paper "260506_Coding Agents_alphazero"
/learn-paper "260506_Coding Agents_alphazero" --align
```

Output: `<folder>/<paper-name>.html` (same name as the PDF, same folder, single file, all dependencies via CDN).

## Trigger discipline

Enter this skill **only** on explicit user invocation: `/learn-paper <folder>`, or natural-language "学习 / 讲解 / 拆解 X 文件夹里的 paper". Seeing a PDF in the workspace is **not** a trigger — don't proactively start writing.

## Workflow

1. **Locate the input.**
   - Resolve `<folder>` (relative to project root or absolute path).
   - Find `*.pdf` inside the folder. If multiple PDFs exist, **ask the user** which one — do not silently pick the first.
   - If `<folder>/_drafts/paper.md` exists, **read it first** (often a richer pre-extracted note); otherwise `Read` the PDF directly.
   - **Do not read other topic folders.** Strict isolation.

2. **Branch on mode.**
   - Default (no `--align`): jump to step 4.
   - With `--align`: run the alignment checkpoint in step 3 first.

3. **Alignment checkpoint (only with `--align`).**
   Output the following in chat **and** write to `<folder>/_drafts/outline.md`. The natural-language content of these items is **in Chinese** because they preview the HTML's content:
   1. **Begin-with-why paragraph.** What was the whole field stuck on before this paper? What's the obvious approach? Why doesn't it work? This is chapter 0, not chapter 1.
   2. **One-paragraph thesis.** The paper's key insight, and what fundamentally separates it from prior solutions.
   3. **Chapter outline.** Per chapter: title (with one `<strong>` emphasis word), one-line italic hook, percent of page budget.
   4. **80% allocation.** Name the 1–3 core concepts that consume 80% of the page. Justify why everything else collapses to 20% (cite reader background — see `AGENTS.md`).
   5. **Color-code plan.** Enumerate the recurring key variables / objects in the paper (e.g. score function, noisy point vs. clean point, column vectors, target b…). Assign a fixed color to each (red / blue / green / purple / orange). Reuse it in every formula, SVG, and inline `<span>`.
   6. **Per-topic accent (optional).** If the paper has 2–3 parallel core concepts (PSNR/SSIM/LPIPS-style), assign each section an accent stripe color.
   7. **Worked-example plan.** For each new concept introduced, name the smallest concrete instance you'll walk the reader through (e.g. "score function: 1D standard normal, x=2"). See § Writing principle 3.
   8. **Interactive module list.** Each lab block: what insight it reveals + the visualization form + the corresponding paper section.

   Wait for user confirmation or revision before proceeding to step 4.

4. **Generate the HTML.**
   - Output filename = PDF filename with `.pdf` → `.html`, same folder.
   - Start from the HTML skeleton below.
   - Follow the writing principles and hard constraints below.
   - Intermediate notes and external references go in `<folder>/_drafts/`.

## Writing principles

> Not writing a paper digest. Writing a magazine-grade longread. The reader should close the page feeling "someone took the time to make this make sense to me."

### 1 · Begin with why (chapter 0 is non-negotiable)

The first chapter the reader sees is **never** "overview of our method." It must be a **field-level predicament**:

- Before this paper landed, what were people stuck on?
- What's the obvious thing to try? Why does it fail? (Make this explicit with a `.danger` callout titled "致命问题".)
- Ground the predicament in a concrete physical scenario ("假设你有一万张猫的图片"), then translate it to math.
- Drop a comparison table of how prior families dodge the issue (VAE / GAN / Flow / this paper).
- Close with one Feynman-grade meta-line: "如果不能直接解决，先问我真正需要的是什么——也许我需要的比我以为的少得多。"

Chapter 1 then introduces the paper's actual key insight. Reference template (Diffusion):
`ch0 根本困境 → ch1 天才洞察 (Score Function) → ch2 怎么用 (Langevin) → ch3 怎么学 (Score Matching) → …`.

**Banned**: "Section 1 介绍 / Section 2 相关工作 / Section 3 方法" — that's the structure of the source paper, not of pedagogy.

### 2 · First principles: naive → fatal flaw → insight → design

Each core concept is unfolded in this exact sequence. First describe the obvious idea any smart reader would think of, so they nod along. Then expose the hidden flaw. Then let the paper's insight emerge as the rescue. **Forbidden**: working backward from "the paper proposes X."

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

1–3 core insights consume 80% of the page; everything else collapses to a single sentence or a footnote. If a paper has 5 contributions, pick the deepest 1–3 and go deep. **Do not** transcribe full ablation tables.

### 5 · Audience-aware (reader profile lives in `AGENTS.md`)

The reader is a CS PhD with 8 years in vision/DL. **Mention briefly or skip:**

- Standard backprop / Adam / SGD / LayerNorm
- Vanilla self-attention / multi-head attention
- ResNet / U-Net / ViT basics
- Plain cross-entropy / KL divergence

**Spend the page budget on what's actually new**: the paper's key insight, the new mechanism, why only this design works.

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

Every lab block leads with a single line: **"此 lab 揭示：…（对应 paper §X）"**. Useless interactions (input box → display number, slider that only changes a color) are banned. Useful forms include:

- Vector field / manifold visualization (click to drop particles, watch them follow the score).
- Parameter slider → geometric object morphs (two lines' intersection, planes' intersection line, singular vs. non-singular).
- Annealed sequence: from large noise to small noise, frame by frame.
- Multi-step algorithm with step-dot indicator: prev/next buttons, current step highlighted.
- Tab group when there are multiple methods to compare (column method vs. row method = same computation, two perspectives).

### 10 · Editorial-grade webpage feel

The artifact should read like a magazine longread or a freshly redesigned graduate textbook — **not Markdown rendered to HTML**.

- **Warm paper background** (not `#ffffff`): `#fafaf9` / `#f5f0e8` / `#fdfcf9`. Dark hero contrasts with light body.
- **Serif body** (Source Serif 4 / Iowan Old Style / Georgia) **plus mono eyebrow labels** (JetBrains Mono / Courier New, used for eyebrows / labels / code).
- **Chapter pattern**: eyebrow `CH 03` → big title (with one `<strong>` keyword) → one-line italic hook → `.lead` 1.15rem opening paragraph → body.
- **Callout matrix** of at least 3 semantic colors: `.insight` (blue) / `.danger` (red) / `.success` (green) / `.warning` (orange) / `.definition` (light blue) / `.feynman` (dark, white text, big quote).
- **Math box triple**: mono label ("能量模型 Energy-Based Model") + LaTeX + plain-Chinese math-note.
- **Per-topic accent stripe** (when the paper has 2–3 parallel concepts): each section / formula-card gets a `:before` color stripe; same color used end-to-end.
- **Chapter divider**: `· · ·`, never `<hr>`.
- **Forbidden**: a single 760px column of `<p>` with the occasional `<pre>` — that's a Markdown render, not an editorial page.

## Hard constraints

- **Single HTML file.** All CSS/JS inlined or via CDN. **No** project-root, `_lib/`, or local-asset references. Double-click to view.
- **Same name, same folder.** HTML lives next to the PDF, only the extension swaps.
- **Math.** KaTeX (CDN, auto-render).
- **Code.** Prism or highlight.js (CDN).
- **Style.** Tailwind CDN or hand-written CSS — **Bootstrap is banned**.
- **Fonts.** Google Fonts loads the serif body + mono. **Do not** ship a `system-ui`-only default.
- **No build step.** No npm / vite / webpack.
- **Topic isolation.** Do not read other topic folders.
- **Online research is allowed.** When the agent enriches with external material, mark it explicitly using `aside.external` (paper-original vs. agent-added must be visually distinguishable).
- **When unsure**, search the web first. If still uncertain, write the section anyway and mark the spot with `<div class="uncertain">⚠ 此处未充分消化：[原因]</div>`. **Do not interrupt the user with questions.**
- **HTML already exists.** **Overwrite** (re-running learn-paper on the same paper means the user wants to replace). Don't touch `_drafts/`.
- **Pin CDN versions** (`katex@0.16.11`, `prismjs@1.29.0`). **No `@latest`.**

### Interactive correctness (don't ship a blank canvas)

The two failure modes that show up most often: **blank canvas** (lab block renders, canvas inside is empty) and **blurry / stretched canvas** (draws fine on the agent's screenshot, looks wrong on the user's retina screen). Guard both:

1. **Render on init.** Every lab IIFE must end with one bare `draw()` call. Never leave the canvas waiting for a first input event — if the user doesn't touch a slider, they see nothing. Wrap each lab in `(function(){ const c = document.getElementById('…'); if (!c) return; … draw(); })();` so a missing element doesn't break the rest of the page.
2. **DPR-scale every canvas.** After `getContext('2d')`, set `c.style.width = cssW + 'px'; c.style.height = cssH + 'px'; c.width = cssW * dpr; c.height = cssH * dpr; ctx.scale(dpr, dpr);`. Drawing then uses CSS pixels but stays sharp on retina.
3. **Lab-prefixed ids.** Two labs cannot share `r1` / `canvas-1`. Prefix every control with the lab name (`lab2-yaw`, `rsc-step`) so a copy-paste doesn't silently cross-wire.
4. **Run the page locally before declaring done.** `open <folder>/<name>.html`, scroll to each lab, drag every slider, click every button. If a canvas is blank or a control does nothing, fix before shipping.

## Required component checklist

Every HTML must include the following — missing any of them and the artifact regresses to "text on a page":

1. **Hero / cover** — dark or gradient background; paper title (with `<em>` for the subtitle phrase) + one-line thesis + meta (authors, year, venue, link to original PDF) + reading-time estimate + eyebrow tag (e.g. "第一性原理 · Karpathy 讲法").
2. **Top progress bar** — `position: fixed; top: 0; height: 3px;`, fills as the reader scrolls.
3. **Navigation** (one or both):
   - Left sticky TOC list (academic feel, useful for many chapters).
   - Right fixed nav-dot rail (hover reveals chapter label, narrative-style longread).
4. **Chapter pattern** — every chapter has `.ch-num` + `.ch-title` (with `<strong>` keyword) + `.ch-hook` (italic one-liner) + opening paragraph as `.lead`.
5. **Callout matrix** — at least 3 of: `.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`.
6. **Math box triple** — `<div class="math-box"><div class="math-label">…</div>$$…$$<div class="math-note">…</div></div>`.
7. **Worked example** — a `.worked-example` block per new concept (`we-label` + `we-setup` + numbered `we-steps` + `we-takeaway`).
8. **Naive vs. Insight comparison** — two-column grid, naive on left, paper's solution on right; at least one per HTML.
9. **Figures** — at least 1–2 SVG / CSS / emoji-composed conceptual diagrams. "Figure missing" is not acceptable.
10. **Lab block** — `.lab` container + `.lab-title` (with `⚗`-style icon) + reveal line + canvas + `.ctrl-row` + `.btn-row` + `.lab-note`.
11. **Timeline** (strongly recommended when the paper sits in a clear lineage) — historical chain (Hyvärinen 2005 → Vincent 2011 → Sohl-Dickstein 2015 → DDPM 2020 …).
12. **Comparison table** — model × how-it-dodges × cost, etc.
13. **`aside.external`** — every agent-sourced external addition, marked.
14. **Pull quote / `.feynman`** — at least one distilled punch-line or Feynman-style meta-insight.
15. **Editorial divider `· · ·`** — chapter end.
16. **Footer** — citations, references, generation timestamp, summary of all `uncertain` spots.

## HTML skeleton

Start from this skeleton; expand as needed. It already contains hero + progress bar + right-rail nav + chapter pattern + full callout matrix + math-box + worked-example + lab block + timeline + footer. **Do not regress to a single 760px Markdown column.**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><!-- paper title (Chinese) --></title>

<!-- Fonts: serif body + mono eyebrow + optional display serif -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'\\[',right:'\\]',display:true},
    {left:'$',right:'$',display:false},
    {left:'\\(',right:'\\)',display:false}]})"></script>

<!-- Prism (code highlighting) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.css">
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>

<style>
  :root {
    /* Warm paper surfaces + ink hierarchy */
    --paper:    #f8f5ee;          /* main background, warm paper */
    --paper-2:  #efeae0;          /* lab / aside secondary fill */
    --surface:  #ffffff;          /* card stock white */
    --ink:      #1a1a1a;          /* body ink */
    --ink-soft: #3f3a33;          /* heading dark brown */
    --muted:    #8a8278;          /* secondary text */
    --border:   #d8d2c4;          /* warm border */
    --hairline: #e6e0d2;          /* faintest divider */

    /* Primary accent + semantic palette */
    --accent:    #1e5a8a;         /* primary blue (insight) */
    --c-insight: #1e5a8a;
    --c-danger:  #b03a2e;
    --c-success: #2d7a4f;
    --c-warning: #c47a18;
    --c-feynman: #2d2842;         /* feynman dark-card background */

    /* Color-coded variables (rename to the paper's actual variables) */
    --v-x:  #c0392b;              /* red */
    --v-y:  #1e5a8a;              /* blue */
    --v-z:  #2d7a4f;              /* green */
    --v-b:  #6c3483;              /* purple (target) */

    /* Font stacks */
    --font-body:    'Source Serif 4', 'Iowan Old Style', Georgia, 'Times New Roman', serif;
    --font-display: 'Space Grotesk', 'Source Serif 4', Georgia, serif;
    --font-mono:    'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    --font-sans:    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

    --reading-w: 760px;           /* chapter body max width */
    --shell-w:   1180px;          /* full shell max width */
  }
  *,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--paper); color: var(--ink);
    font-family: var(--font-body); font-size: 17px; line-height: 1.78;
    -webkit-font-smoothing: antialiased;
  }
  code, pre, .mono { font-family: var(--font-mono); }

  /* Top progress bar */
  #progress { position: fixed; top: 0; left: 0; right: 0; height: 3px;
              background: rgba(0,0,0,0.06); z-index: 999; }
  #progress > div { height: 100%; width: 0; background: var(--accent); transition: width .1s; }

  /* Hero cover */
  .hero { background: linear-gradient(180deg,#1a1a2e 0%, #2d2842 100%);
          color: #e8e8f0; padding: 72px 24px 56px; text-align: center;
          border-bottom: 4px solid var(--accent); }
  .hero .eyebrow { font-family: var(--font-mono); font-size: .75rem;
                   letter-spacing: .15em; text-transform: uppercase;
                   color: #9999c0; margin-bottom: 12px; }
  .hero h1 { font-family: var(--font-display); font-size: clamp(2rem, 4vw, 3rem);
             font-weight: 600; line-height: 1.18; letter-spacing: -.01em; max-width: 800px; margin: 0 auto; }
  .hero h1 em { color: #aac4ff; font-style: normal; }
  .hero .thesis { color: #c8c2d8; font-size: 1.1rem; max-width: 60ch;
                  margin: 16px auto 0; font-style: italic; }
  .hero .meta { display: flex; gap: 18px; flex-wrap: wrap; justify-content: center;
                margin-top: 24px; font-family: var(--font-mono);
                font-size: .82rem; color: #8a8aaa; }
  .hero .meta a { color: #aac4ff; text-decoration: none; }
  .hero .meta a:hover { text-decoration: underline; }

  /* Right-side nav-dot rail */
  #rail { position: fixed; right: 22px; top: 50%; transform: translateY(-50%);
          display: flex; flex-direction: column; gap: 10px; z-index: 100; }
  .dot { width: 11px; height: 11px; border-radius: 50%;
         background: var(--border); cursor: pointer; position: relative;
         transition: all .2s; border: 2px solid transparent; }
  .dot:hover, .dot.active { background: var(--accent); transform: scale(1.3); }
  .dot .lbl { position: absolute; right: 18px; top: 50%; transform: translateY(-50%);
              background: var(--ink-soft); color: #f8f5ee;
              padding: 4px 9px; border-radius: 3px; font-family: var(--font-mono);
              font-size: .72rem; white-space: nowrap; opacity: 0;
              pointer-events: none; transition: opacity .2s; }
  .dot:hover .lbl { opacity: 1; }
  @media (max-width: 900px) { #rail { display: none; } }

  /* Chapter scaffold */
  .chapter { max-width: var(--reading-w); margin: 0 auto;
             padding: 72px 28px 24px; scroll-margin-top: 24px;
             border-bottom: 1px solid var(--hairline); }
  .chapter:last-of-type { border-bottom: 0; }
  .ch-num { font-family: var(--font-mono); font-size: .76rem;
            letter-spacing: .14em; text-transform: uppercase;
            color: var(--muted); margin-bottom: 8px; }
  .ch-title { font-family: var(--font-display); font-size: 1.95rem;
              font-weight: 600; color: var(--ink-soft); line-height: 1.22;
              letter-spacing: -.005em; }
  .ch-title strong { color: var(--accent); font-weight: 700; }
  .ch-hook { font-style: italic; color: var(--muted);
             font-size: 1.08rem; margin: 8px 0 22px;
             padding-bottom: 18px; border-bottom: 2px solid var(--border); }
  .lead { font-size: 1.18rem; color: var(--ink-soft); margin-bottom: 20px; }
  .chapter p { margin-bottom: 18px; }

  /* Per-topic accent stripes (when the paper has 2–3 parallel concepts) */
  .topic-a:before, .topic-b:before, .topic-c:before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; border-radius: 2px;
  }
  .topic-a { position: relative; padding-left: 20px; }
  .topic-a:before { background: var(--c-insight); }
  .topic-b { position: relative; padding-left: 20px; }
  .topic-b:before { background: var(--c-success); }
  .topic-c { position: relative; padding-left: 20px; }
  .topic-c:before { background: var(--c-danger); }

  /* Callout matrix */
  .insight, .danger, .success, .warning, .definition {
    border-left: 4px solid; background: #fff;
    padding: 16px 20px; margin: 22px 0; border-radius: 0 4px 4px 0;
  }
  .insight    { border-color: var(--c-insight); background: #eef3fb; }
  .danger     { border-color: var(--c-danger);  background: #fdf0ee; }
  .success    { border-color: var(--c-success); background: #eef8f0; }
  .warning    { border-color: var(--c-warning); background: #fdf5ee; }
  .definition { border-color: var(--c-insight); background: #eef3fb; }
  .insight .label, .danger .label, .success .label,
  .warning .label, .definition .label {
    font-family: var(--font-mono); font-size: .72rem;
    letter-spacing: .1em; text-transform: uppercase;
    font-weight: 700; margin-bottom: 6px; display: block;
  }
  .insight    .label { color: var(--c-insight); }
  .danger     .label { color: var(--c-danger); }
  .success    .label { color: var(--c-success); }
  .warning    .label { color: var(--c-warning); }
  .definition .label { color: var(--c-insight); }

  /* Feynman block (dark card with oversized opening quote) */
  .feynman { background: var(--c-feynman); color: #e8e8f0;
             padding: 22px 26px; margin: 28px 0; border-radius: 4px;
             position: relative; }
  .feynman::before { content: '"'; position: absolute; top: -10px; left: 18px;
                     font-size: 4rem; color: #4a4a7a; font-family: Georgia, serif;
                     line-height: 1; }
  .feynman p { font-style: italic; color: #d8d8f0; margin-bottom: 8px; }
  .feynman .attribution { color: #9090b0; font-size: .82rem; font-style: normal;
                          font-family: var(--font-mono); }

  /* Math box triple */
  .math-box { background: #fef9e7; border: 1px solid var(--border);
              border-radius: 4px; padding: 18px 22px; margin: 20px 0;
              overflow-x: auto; }
  .math-box .math-label { font-family: var(--font-mono); font-size: .72rem;
                          letter-spacing: .1em; text-transform: uppercase;
                          color: var(--muted); margin-bottom: 10px; }
  .math-box .math-note  { font-size: .9rem; color: var(--muted);
                          margin-top: 10px; font-style: italic; }

  /* Worked example: concrete numerical walkthrough */
  .worked-example { background: #fffbef; border-left: 6px double var(--accent);
                    padding: 18px 22px; margin: 22px 0;
                    border-radius: 0 4px 4px 0; }
  .worked-example .we-label { font-family: var(--font-mono); font-size: .72rem;
                              letter-spacing: .1em; text-transform: uppercase;
                              color: var(--accent); font-weight: 700;
                              margin-bottom: 10px; display: block; }
  .worked-example .we-setup { font-style: italic; color: var(--ink-soft);
                              margin-bottom: 10px; }
  .worked-example .we-steps { margin: 6px 0 6px 22px; padding: 0; }
  .worked-example .we-steps li { margin: 4px 0; }
  .worked-example .we-takeaway { margin-top: 12px; padding: 10px 14px;
                                 background: rgba(255,255,255,.7);
                                 border-radius: 4px; font-size: .94rem;
                                 color: var(--ink-soft); }
  .worked-example .we-takeaway::before { content: "📌 "; }

  /* Naive vs. Insight comparison cards */
  .compare { display: grid; grid-template-columns: 1fr 1fr;
             gap: 16px; margin: 24px 0; }
  @media (max-width: 700px) { .compare { grid-template-columns: 1fr; } }
  .compare > div { border: 1px solid var(--border); background: var(--surface);
                   border-radius: 6px; padding: 16px 18px; }
  .compare .naive       { border-top: 3px solid var(--muted); }
  .compare .insight-card{ border-top: 3px solid var(--accent); }
  .compare .label       { font-family: var(--font-mono); font-size: .72rem;
                          letter-spacing: .1em; text-transform: uppercase;
                          color: var(--muted); margin-bottom: 6px; display: block; }

  /* Lab block (interactive sandbox) */
  .lab { background: var(--paper-2); border: 1px solid var(--border);
         border-radius: 6px; padding: 22px; margin: 28px 0; }
  .lab-title { font-family: var(--font-mono); font-size: .8rem;
               letter-spacing: .1em; text-transform: uppercase;
               color: var(--ink-soft); margin-bottom: 8px;
               display: flex; align-items: center; gap: 8px; }
  .lab-reveal { font-size: .92rem; color: var(--muted);
                margin-bottom: 14px; font-style: italic; }
  .lab canvas, .lab svg { display: block; margin: 0 auto;
                          max-width: 100%; border-radius: 4px;
                          background: #fff; }
  .ctrl-row { display: flex; align-items: center; gap: 14px;
              margin-top: 14px; flex-wrap: wrap;
              font-family: var(--font-mono); font-size: .85rem; }
  .ctrl-row label { color: var(--muted); min-width: 70px; }
  .ctrl-row input[type=range] { flex: 1; min-width: 120px; accent-color: var(--accent); }
  .ctrl-val { color: var(--accent); min-width: 48px; text-align: right; }
  .btn-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
  .btn { padding: 6px 14px; background: var(--ink-soft); color: #f8f5ee;
         border: none; border-radius: 3px; cursor: pointer; font-size: .85rem;
         font-family: var(--font-mono); transition: opacity .15s; }
  .btn:hover { opacity: .8; }
  .btn.outline { background: transparent; border: 1px solid var(--ink-soft);
                 color: var(--ink-soft); }
  .lab-note { font-size: .82rem; color: var(--muted); margin-top: 12px;
              font-style: italic; }
  .step-dots { display: flex; gap: 6px; margin: 12px 0; align-items: center; }
  .step-dots .d { width: 9px; height: 9px; border-radius: 50%;
                  background: var(--border); transition: background .25s; }
  .step-dots .d.active { background: var(--accent); }
  .step-dots .d.done   { background: var(--c-success); }

  /* Timeline (historical lineage) */
  .timeline { position: relative; padding-left: 28px; margin: 24px 0; }
  .timeline::before { content: ''; position: absolute; left: 7px; top: 8px;
                      bottom: 8px; width: 2px; background: var(--border); }
  .tl-item { position: relative; margin-bottom: 22px; }
  .tl-dot { position: absolute; left: -24px; top: 6px;
            width: 12px; height: 12px; border-radius: 50%;
            background: var(--accent); border: 2px solid var(--paper);
            box-shadow: 0 0 0 2px var(--accent); }
  .tl-year { font-family: var(--font-mono); font-size: .78rem;
             color: var(--accent); font-weight: 700; margin-bottom: 2px; }
  .tl-title { font-weight: 600; margin-bottom: 2px; color: var(--ink-soft); }
  .tl-desc  { color: var(--muted); font-size: .92rem; }

  /* Pull quote */
  .pull-quote { font-family: var(--font-display); font-size: 1.32rem;
                line-height: 1.48; color: var(--ink-soft);
                border-left: 3px solid var(--ink-soft);
                padding: 6px 0 6px 18px; margin: 32px 0;
                font-style: italic; }

  /* Comparison table */
  table { width: 100%; border-collapse: collapse;
          margin: 22px 0; font-size: .92rem; }
  th { background: var(--ink-soft); color: #f8f5ee;
       padding: 10px 14px; text-align: left;
       font-weight: 500; font-family: var(--font-mono);
       font-size: .78rem; letter-spacing: .05em; }
  td { padding: 10px 14px; border-bottom: 1px solid var(--border);
       vertical-align: top; }
  tr:hover td { background: var(--paper-2); }

  /* External (agent-sourced supplementary content) */
  aside.external { display: block; background: #f1ede1;
                   border-left: 3px solid var(--muted);
                   padding: 12px 16px; margin: 18px 0;
                   border-radius: 0 4px 4px 0;
                   font-size: .92em; color: var(--ink-soft); }
  aside.external::before { content: "外部补充 · agent"; display: block;
                           font-family: var(--font-mono); font-size: .68rem;
                           letter-spacing: .12em; color: var(--muted);
                           margin-bottom: 6px; }

  /* Uncertain (not fully digested) */
  .uncertain { border-left: 4px solid #d97706; background: #fef3c7;
               padding: 12px 16px; border-radius: 0 4px 4px 0;
               margin: 16px 0; }

  /* Color-coded variables */
  .v-x { color: var(--v-x); font-weight: 600; }
  .v-y { color: var(--v-y); font-weight: 600; }
  .v-z { color: var(--v-z); font-weight: 600; }
  .v-b { color: var(--v-b); font-weight: 600; }

  /* Editorial divider */
  .ch-end { text-align: center; margin: 48px 0 12px;
            color: var(--border); font-size: 1.2rem;
            letter-spacing: .5em; }

  /* Code block: rounded with warm tone */
  pre[class*="language-"] { border-radius: 6px; padding: 14px 18px !important;
                            font-size: .88rem; }

  /* Footer */
  footer.page-foot { background: var(--ink-soft); color: #c8c2b8;
                     padding: 32px 24px; text-align: center;
                     font-family: var(--font-mono); font-size: .82rem;
                     line-height: 1.6; }
  footer.page-foot a { color: #e8d8b8; text-decoration: none; }

  @media (max-width: 700px) {
    body { font-size: 16px; }
    .chapter { padding: 48px 18px 18px; }
    .hero h1 { font-size: 1.7rem; }
    .hero { padding: 48px 16px 36px; }
  }
</style>
</head>
<body>

<div id="progress"><div></div></div>

<!-- Right-side nav-dot rail -->
<nav id="rail" aria-label="章节导航">
  <div class="dot active" data-target="ch0"><span class="lbl">困境</span></div>
  <div class="dot" data-target="ch1"><span class="lbl">关键 insight</span></div>
  <div class="dot" data-target="ch2"><span class="lbl">怎么训</span></div>
  <!-- add more as needed -->
</nav>

<!-- Hero -->
<header class="hero">
  <div class="eyebrow">Paper · 第一性原理 · Karpathy 风格</div>
  <h1><!-- paper main title (Chinese) --><br><em><!-- one-line subtitle (Chinese) --></em></h1>
  <p class="thesis"><!-- one sentence: what this paper solves and what the key insight is (Chinese) --></p>
  <div class="meta">
    <span><!-- authors · year · venue --></span>
    <span>预计阅读 ~XX 分钟</span>
    <a href="./<!-- same-name PDF -->">原 PDF</a>
  </div>
</header>

<!-- ═══ Chapter 0 — field-level predicament (begin with why) ═══ -->
<section class="chapter" id="ch0">
  <div class="ch-num">Chapter 0</div>
  <h2 class="ch-title">领域级<strong>根本困境</strong></h2>
  <p class="ch-hook">在理解这篇 paper 之前，我们必须先理解它在解决什么问题。</p>

  <p class="lead"><!-- concrete physical scenario in Chinese: assume you have X, you want Y, mathematically this means Z --></p>
  <p><!-- translate Y to math; first appearance of key variables — assign them colors via <span class="v-x">x</span> etc. --></p>

  <div class="insight">
    <span class="label">核心问题</span>
    <p><!-- one-sentence statement of the field-wide bottleneck --></p>
  </div>

  <p>最自然的想法：<!-- the naive idea --></p>

  <div class="math-box">
    <div class="math-label"><!-- e.g. 能量模型 Energy-Based Model --></div>
    \[ <!-- naive formula --> \]
    <div class="math-note"><!-- plain-Chinese explanation --></div>
  </div>

  <div class="danger">
    <span class="label">致命问题</span>
    <p><!-- why the naive idea is dead-on-arrival --></p>
  </div>

  <table>
    <tr><th>模型</th><th>如何绕开</th><th>代价</th></tr>
    <tr><td>VAE</td><td>用 ELBO 近似下界</td><td>样本质量受限</td></tr>
    <tr><td>GAN</td><td>不建模 p(x)，用判别器</td><td>训练不稳定</td></tr>
    <tr><td><strong>这篇 paper</strong></td><td><strong>…</strong></td><td><strong>…</strong></td></tr>
  </table>

  <div class="feynman">
    <p>如果你不能直接解决一个问题，先问：我真正需要的是什么？也许我需要的比我以为的少得多。</p>
    <div class="attribution">— Feynman 式思维</div>
  </div>

  <div class="ch-end">· · ·</div>
</section>

<!-- ═══ Chapter 1 — key insight ═══ -->
<section class="chapter" id="ch1">
  <div class="ch-num">Chapter 1</div>
  <h2 class="ch-title">天才洞察：<strong><!-- key concept (Chinese) --></strong></h2>
  <p class="ch-hook"><!-- italic one-line hook (Chinese) --></p>

  <p class="lead"><!-- physical intuition first: standing on a mountain, you want to reach the top --></p>
  <p><!-- translate the intuition to math; introduce new symbols --></p>

  <div class="math-box">
    <div class="math-label"><!-- e.g. Score Function --></div>
    \[ s(x) = \nabla_x \log p(x) \]
    <div class="math-note"><!-- plain Chinese: this is the gradient of log-density; at every point it points toward "uphill in probability" --></div>
  </div>

  <!-- Worked example for principle 3: smallest concrete instance -->
  <div class="worked-example">
    <span class="we-label">Worked example · 1D 标准正态</span>
    <div class="we-setup">取 <span class="v-x">p(x) = (1/√2π)·e^(−x²/2)</span>，求 <span class="v-y">s(x) = ∇log p(x)</span>。</div>
    <ol class="we-steps">
      <li>log p(x) = −x²/2 − log√(2π)</li>
      <li>∇ log p(x) = −x</li>
      <li>所以 <span class="v-y">s(x) = −x</span>。在 <span class="v-x">x = 2</span> 处，score = −2，长度等于距离，方向指回原点。</li>
    </ol>
    <div class="we-takeaway">"score" 对正态分布只是<strong>负的位置</strong>——每个点都被以"距离"为大小的力拉回零点。一旦换成混合分布、流形数据，这个"拉回最近高密度区"的图像就成了 Langevin 采样的物理基础。</div>
  </div>

  <div class="success">
    <span class="label">关键突破</span>
    <p><!-- why this insight dissolves the predicament --></p>
  </div>

  <div class="lab">
    <div class="lab-title">⚗ <!-- lab name (Chinese) --></div>
    <p class="lab-reveal">此 lab 揭示：<!-- specific insight --> · 对应 paper §X</p>
    <canvas id="lab1-canvas" width="760" height="320"></canvas>
    <div class="ctrl-row">
      <label>参数 σ</label>
      <input type="range" id="lab1-sigma" min="0" max="1" step=".01" value=".5">
      <span class="ctrl-val" id="lab1-sigmaV">0.50</span>
    </div>
    <div class="btn-row">
      <button class="btn" id="lab1-run">运行</button>
      <button class="btn outline" id="lab1-reset">重置</button>
    </div>
    <div class="lab-note"><!-- what to do + what to watch for --></div>
  </div>

  <div class="ch-end">· · ·</div>
</section>

<!-- ═══ Chapter N — historical lineage (when applicable) ═══ -->
<section class="chapter" id="chN">
  <div class="ch-num">Chapter N</div>
  <h2 class="ch-title">这条路是怎么走过来的：<strong>历史脉络</strong></h2>
  <p class="ch-hook">这篇 paper 不是凭空冒出来的。</p>

  <div class="timeline">
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2005 · Hyvärinen</div>
      <div class="tl-title">Score Matching</div>
      <div class="tl-desc">证明可以不用 Z 来学 score function，但计算代价高</div>
    </div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2011 · Vincent</div>
      <div class="tl-title">Denoising Score Matching</div>
      <div class="tl-desc">去噪 = 学 score，计算高效</div>
    </div>
    <!-- … -->
  </div>

  <div class="ch-end">· · ·</div>
</section>

<footer class="page-foot">
  <div>引用：<!-- inline BibTeX line --></div>
  <div>生成 <!-- ISO timestamp --> · 由 agent 基于原 PDF + 联网补充整理</div>
</footer>

<script>
  // Top progress bar — width tracks scroll fraction
  const prog = document.querySelector('#progress > div');
  window.addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = (h.scrollTop) / (h.scrollHeight - h.clientHeight);
    prog.style.width = (p * 100) + '%';
  }, { passive: true });

  // Right-rail dot highlight via IntersectionObserver
  const dots = document.querySelectorAll('#rail .dot');
  const sections = [...document.querySelectorAll('section.chapter')];
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
      // … paper-specific drawing, in CSS pixels, using `sigma` …
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

| Class | Purpose | Notes |
|---|---|---|
| `.hero` | Top cover | Dark background + display font + eyebrow + thesis + meta |
| `#progress` | Top 3px scroll progress bar | Fixed; width tracks scroll fraction |
| `#rail .dot` | Right-side nav-dot rail | Hover reveals chapter label |
| `.chapter` `.ch-num` `.ch-title` `.ch-hook` `.lead` | Chapter scaffold | Every chapter needs all four |
| `.insight` `.danger` `.success` `.warning` `.definition` | 5-color semantic callouts | Inner `<span class="label">` for the eyebrow |
| `.feynman` | Dark-card meta-insight block | Oversized opening quote glyph + attribution |
| `.math-box` `.math-label` `.math-note` | Math triple | Mono label + LaTeX + plain-Chinese note |
| `.worked-example` `.we-label` `.we-setup` `.we-steps` `.we-takeaway` | Concrete numerical walkthrough | Required per new concept |
| `.compare > .naive` `.compare > .insight-card` | Naive vs. paper-solution comparison | Two-column grid |
| `.lab` `.lab-title` `.lab-reveal` `.ctrl-row` `.btn-row` `.lab-note` | Interactive sandbox | Reveal line is mandatory |
| `.step-dots` `.d.active/.done` | Multi-step algorithm state indicator | For sequenced demos |
| `.timeline` `.tl-item` `.tl-dot` `.tl-year` `.tl-title` `.tl-desc` | Historical lineage | Strongly recommended for papers in a clear chain |
| `.pull-quote` | Inline punch-line | Display font + left rule |
| `aside.external` | Agent-sourced external addition | Self-labels with "外部补充 · agent" |
| `.uncertain` | Not-fully-digested marker | Lead with `⚠` |
| `.v-x` `.v-y` `.v-z` `.v-b` | Color-coded variables | Same hex used in formulas / SVG / inline prose |
| `.ch-end` `· · ·` | Chapter divider | Never use `<hr>` |
| `.topic-a/b/c` | Per-topic accent stripe | Only when paper has 2–3 parallel concepts |

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
- [ ] At least **3 different** callout types in use (not the entire page in `.insight`).
- [ ] At least **1** math-box triple (label + LaTeX + math-note).
- [ ] At least **1** worked example.
- [ ] At least **1** naive vs. insight `.compare` block.
- [ ] At least **1** lab block with the `lab-reveal` line filled in.
- [ ] At least **1** SVG / canvas figure (no "figure missing").
- [ ] If the paper sits in a clear lineage, a `.timeline` is present.
- [ ] Recurring key variables are color-coded; the same hex appears in formulas, SVG strokes, and inline prose.
- [ ] Background is warm paper (not `#ffffff`). Body font is serif. Eyebrow labels are mono.
- [ ] Chapter dividers use `· · ·`, not `<hr>`.
- [ ] Top progress bar and at least one nav (left TOC or right rail) are present and functional.

**Technical**
- [ ] Single HTML file. All CDNs pinned to a stable version. No local-asset references.
- [ ] Every `<section class="chapter">` has an `id`. Every rail dot's `data-target` resolves. IntersectionObserver actually highlights the active section.
- [ ] Every agent-added external content is wrapped in `aside.external`.
- [ ] Every not-fully-digested spot is marked with `<div class="uncertain">⚠ …</div>`. No silent TODOs.
- [ ] **Every lab IIFE ends with `draw()`** — no blank canvas on first paint. Verified by opening the file and looking at every lab without touching anything.
- [ ] **Every canvas is DPR-scaled** (CSS width set + `width *= dpr` + `ctx.scale(dpr, dpr)`) — sharp on retina, not stretched. Lab control ids are lab-prefixed; no collisions across labs.

## Gotchas

- **Multiple PDFs in the folder** — ask the user; never default to the first.
- **Mac font fallback** — when `Source Serif 4` fails to load, body falls back through Iowan Old Style → Georgia → Times New Roman; when `JetBrains Mono` fails, through Fira Code → Courier New. The CSS stack is set up — don't strip the fallbacks.
- **KaTeX + color-coded variables** — inside LaTeX use `\textcolor{#c0392b}{x}` (KaTeX supports it). In plain prose use `<span class="v-x">x</span>`. The hex must match on both sides.
- **`@latest` is forbidden** — every CDN URL pins a stable version (`katex@0.16.11`, `prismjs@1.29.0`) so loads stay reproducible across months.
- **Don't leave silent TODO placeholders** — fully write the section, or mark it explicitly with `.uncertain`.
- **Worked-example pitfalls** — if the example takes more than ~5 steps, it's too big. If you can't extract a one-line takeaway, the example wasn't well-chosen. If the numbers aren't tiny (1, 2, 0, ½, π/4), pick smaller ones. The whole point is "the reader could redo this on a napkin."
- **Self-audit "text on a page"** — if the page is mostly `<p>` and a few `<pre>`, with no hero, no nav, no chapter scaffold, no varied callouts, no SVG, no lab block, no worked example — go back and add components. That's not a delivery.
- **Don't abuse callouts as paragraph wrappers** — a callout is to highlight one sentence or one proposition, not to box up five paragraphs of body text.
- **TOC / rail must actually work** — every `<section>` needs a real `id`; every rail dot's `data-target` must resolve; the IntersectionObserver in the skeleton must remain wired up.
- **Per-topic accent stripes** — only use `topic-a/b/c` when the paper genuinely has 2–3 parallel core concepts (PSNR/SSIM/LPIPS, Score/Langevin/Denoising, …). Otherwise a single `--accent` is enough.
- **Blank canvas / blurry canvas** — the two most common interactive regressions. Blank: the lab's IIFE wires `slider.addEventListener('input', draw)` but never calls `draw()` once at the bottom, so the canvas is empty until someone wiggles the slider. Blurry / stretched: the agent set the canvas's HTML `width` attribute but never DPR-scaled, so on retina the bitmap is half-resolution and CSS stretches it. The skeleton's lab template now bakes both fixes in — copy it verbatim instead of hand-rolling a new lab from scratch.

## See also

- Project-root `AGENTS.md` — reader profile, project-level hard constraints, trigger protocol.
- Reference samples (visual + pedagogical ground truth):
  - `~/Documents/manus_out/3dgs/3DGS_Metrics_Interactive.html` — editorial / per-topic accent / oklch palette.
  - `~/Documents/manus_out/3dgs/Depth Anything 3 交互网页 (1).html` — serif + Space Grotesk modern feel.
  - `~/Documents/manus_out/other_reading/Diffusion Concepts Interactive Webpage (1).html` — begin-with-why pattern + multi-semantic callouts + timeline + right-rail nav.
  - `~/Documents/manus_out/other_reading/mit1806_lecture1.html` — clean typography + step animations + color-coded variables + tabbed method comparison.
