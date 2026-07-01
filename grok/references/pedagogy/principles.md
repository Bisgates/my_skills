# Pedagogical principles (shared base)

Nine rules. Apply to every page regardless of pedagogy pack or visual layer. Not a source summary — a learning artifact.

## 1 · Begin with why

First thing the reader sees is a **field-level predicament**, not "overview of our method":

- Before this work landed, what were people stuck on?
- What's the obvious thing to try? Why does it fail?
- Ground in a concrete physical scenario ("假设你有一万张猫的图片"), then translate to math, code, or data.
- Drop a comparison of how prior families dodge the issue. Magazine: `.compare` block or table. Notebook: markdown cell + table or `.diff`.

Form differs across packs; the move is the same. Dual-tab: predicament is shared, voices differ.

Banned: "Section 1 介绍 / Section 2 相关工作 / Section 3 方法" — that's source structure, not pedagogy.

## 2 · First principles: naive → fatal flaw → insight → design

Each core concept unfolds in this sequence. Describe the obvious idea any smart reader would think of (they nod along) → expose the hidden flaw → let the source's insight emerge as the rescue.

Forbidden: working backward from "the source proposes X."

## 3 · Concrete minimal worked example for every new concept

Every new concept (definition, formula, algorithm step, function) gets a worked example with numbers a reader could redo on a napkin.

Constraints:
- Smallest non-degenerate dimension (1D or 2D, not 7D).
- Trivial numbers (`1, 2, 0, ½, π/4` — not `0.7234`).
- One step per line; never make the reader factor what you just did.
- End with a punchline. If you can't extract one, the example was too large.
- Example before generalization. Concrete first, abstract second.

Concrete examples:
- **Score function.** `p(x) = (1/√2π) e^(−x²/2)` → `log p(x) = −x²/2 − const` → `s(x) = −x`. At `x=2`, score `= −2`: points toward origin, magnitude = distance.
- **Linear combination of columns.** `A = I_2`, `x = [2,3]` → `2·[1,0] + 3·[0,1] = [2,3]`. Change `x = [1,1]`, recompute. Now it's an act, not a phrase.
- **Attention.** 2 tokens of dim 2, `Q = K = V = I_2`. Compute `QK^T = I_2`, softmax row-wise, multiply V → identity attention. Perturb `Q[0]` to `[0.5, 0.5]` and watch the row mix.

Rendering:
- **bird:** `.worked-example` block (`we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`). Arc: method-from-goal → simplest input → observe goal met.
- **frog:** code cell (`In [N]:`) + output cell (`Out[N]:`) + markdown takeaway. Or Ng-style `.chalk` block tracing likelihood → gradient → update rule.

## 4 · 80% to the core

1–3 core insights consume 80% of the page; everything else collapses to a sentence or footnote. If the source has 5 contributions, pick the deepest 1–3. Do not transcribe full ablation tables.

## 5 · Audience-aware

Reader: CS PhD, 8 years vision/DL (see project `AGENTS.md`).

Skip or mention briefly: standard backprop / Adam / SGD / LayerNorm; vanilla self/multi-head attention; ResNet / U-Net / ViT basics; plain cross-entropy / KL divergence.

Spend the page on the source's key insight, the new mechanism, why only this design works.

## 6 · 讲解口吻 = cs231n course-note register

The shared teaching voice for every pack (bird / frog / guest), modeled on the cs231n course notes
(<https://cs231n.github.io/>, e.g. `optimization-1`). This is a **register, orthogonal to altitude** — it
does not change *what* bird (top-down) or frog (bottom-up) cover, only *how* the prose reads. Artifact
language: Chinese. The reader should be able to read a page top to bottom and *understand*, because the
prose teaches rather than states:

- **Motivation-first.** Open a unit by recapping where we are, naming the role this piece plays, and
  foreshadowing where it leads — then introduce it.
- **Conversational but authoritative.** Inclusive "我们" / "你会发现" / "试着想一下"; openly flag the
  subtle or odd points ("这里看起来奇怪，因为…") instead of hiding them.
- **Intuition before formalism.** Every new term/formula gets a one-line intuition before the symbol — a
  concrete instance, a number, or a pedagogical analogy (cs231n's hiker-on-a-hill is fair game; keep it
  tied to the mechanism, don't let it drift into literary flourish).
- **Signpost the core, recap the section.** Name the principle before the details (a 「核心思想：…」 line)
  and close a section with a short plain-Chinese recap of what shifted — not a 论文 "综上所述".
- **Preempt confusion.** Anticipate the reader's likely objection or terminology snag and resolve it in
  line ("你可能会问为什么…—…").
- **Reasoning glue.** Connect each step to the last (问题在于… / 因此… / 注意… / 关键在于… / 反过来看…);
  the glue carries the dependency between steps, so it is information, not filler.
- **Sentence rhythm.** Long and short alternate; no paragraph longer than 5–6 lines.

去 论文腔 / AI 味 (search and remove before shipping): 本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得
注意的是 / 显然地 / 据此可知; the "不是 X，而是 Y" 对仗 (≤1–2 处); 值得深思 / 综合来看 / 让我们一起 / 总而言
之; 僵硬并列与过度收尾; **自证式可信度表演** —— 只在向读者担保"作者没瞎编 / 这是真的 / 就写在那儿"、不携带任何关于主题的信息的句子（"这句话不是我编的，它就刻在 X 的权重名字里" / "答案就藏在名字里" / "这不是巧合" / "你没看错"），一律删；读者的信任靠内容本身赢得，不靠句子替自己作证。Density = information per sentence; let a sentence run as long as the reasoning needs.

## 7 · Color-coded variables

Recurring key variables share one palette across math, SVG, prose, code highlights.

```html
<span class="v-x">x</span>      <!-- red -->
<span class="v-y">y</span>      <!-- blue -->
<span class="v-z">z</span>      <!-- green -->
<span class="v-b">b</span>      <!-- purple (target) -->
```

LaTeX: `\(\textcolor{#dc2626}{x}\)`. SVG: stroke/fill with the same hex. Inline: `<span class="v-x">`. Reader calibrates once; every later formula and figure is parsable without mental relabeling.

In dual-tab mode the same variable shares its hex across both tabs.

## 8 · Revealing interactivity

Every lab leads with **"此 lab 揭示：…（对应来源章节）"** (or the frog `.lab-sub` equivalent).

Banned: input box → display number; slider that only changes a color.

Useful forms:
- Vector field / manifold (click to drop particles, watch them follow the score).
- Parameter slider → geometric object morphs.
- Annealed sequence: large noise → small noise, frame by frame.
- Multi-step algorithm with step-dot / step-trace indicator.
- Tab group for method comparison.

## 9 · Source figures when they earn it

Embed source imagery when it carries information the worked-example + diagram can't easily replace. If you can't write a one-line caption explaining *why this image is here*, skip it.

- **PDF figures:** `pdfimages` / `pdftoppm` → inline base64 `<img src="data:image/png;base64,…">`. Downscale to ≤1200px long edge.
- **Web images:** only from stable pinned URLs (Wikipedia Commons, arXiv-hosted, paper supplementary, author's project page). Anything not from the source goes inside an "external" aside.
- **No AI-generated stock filler.**

Opt-in, not a checklist requirement. SVG + worked-example spine carries the page when the source has nothing photogenic.
