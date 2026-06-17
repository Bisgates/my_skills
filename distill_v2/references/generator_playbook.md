# distill_v2 generator playbook (arc 260616a)

How a generation agent writes a part of a distill_v2 article. Output renders through the **real Distill template** (`bin/build.py` + `templates/skeleton.html`), so authentic markup is free — spend effort on interaction authenticity, pedagogy, and voice (the dimensions a template can't give you). Grounded in `corpus_dna.md`; judged by `discriminator_rubric.md`; assembled per `build_pipeline.md`.

## Output language: Chinese (default)
All reader-facing text is **Chinese** — title/dek, prose, `<h2>`/`<h3>` headings, figcaptions, control labels, on-canvas readouts, the appendix prose. Keep in their original form: math (LaTeX inside `<d-math>`), code, `<d-cite key>` BibTeX keys, and standard symbols. A technical term may carry its English original in parentheses on first mention (e.g. 重参数化技巧（reparameterization trick）) when that aids a reader who knows the English literature. Write **native Chinese technical prose, not translated English** — see the Voice section. (Your instructions, this playbook, and all build/QA steps stay English; only what the reader sees is Chinese. If the build plan explicitly sets English, follow it.)

## What a part agent returns
For its assigned part, three fragments:
1. **`sections.html`** — inner HTML of `<d-article>` for this part (one or more `<h2>`/`<h3>` + prose + figures).
2. **`labs.js`** — the lab IIFEs for this part's figures (may be empty).
3. **`refs.bib`** — BibTeX entries for any `<d-cite key="...">` it introduces.
Colors/entities/notation must stay consistent with the article's running example (settled in the build plan).

**Cross-part consistency (minimise the seams the harmonize pass must fix).** Use the build plan's exact symbols: ONE loss symbol (`L` for the toy objective; reserve `\mathcal{L}` only if the plan defines a distinct one), ONE noise symbol (`\varepsilon`, never `\epsilon`), the entity→color map verbatim, and the plan's section-marker scheme (`<span class="marker">` Roman numerals I–V) for every `<h2>`. Do not invent your own numbering or notation — a strict prose judge catches drift between parts.

## Authoring API (distill template, runtime mode)
- **Math:** inline `<d-math>e^{i\pi}+1=0</d-math>`; display `<d-math block>...</d-math>`. Never raw `$...$` in prose. Break wide display math with `\begin{aligned}...\\...\end{aligned}`. Never put a raw `<`/`>` inside math — use `\lt \gt \le \ge`.
  - **KaTeX is distill's vendored v2.4.0 (2016) — restricted macro set.** Supported: `\mathbb \mathrm \text \frac \overbrace \underbrace \boxed \big \Big \begin{aligned} \sum \prod \nabla \partial \cdot \odot \sim \mathcal`. **NOT supported (will throw a parse error): `\operatorname` (use `\mathrm{Var}`/`\mathrm{Cov}`), `\substack`, `\xrightarrow`, `\boldsymbol`.** QA every build with the headless KaTeX-error check — a parse error blanks the formula.
- **Citations:** `<d-cite key="bibtexkey"></d-cite>` → renders `[n]` + hover-box; add the entry to `refs.bib`. Never write `[1]` by hand.
- **Footnotes:** `<d-footnote>side remark</d-footnote>` → margin/hover aside.
- **Figures + labs:**
  ```html
  <figure class="l-body">           <!-- or l-page / l-page-outset / l-screen / l-gutter -->
    <canvas id="lab-NAME" width="..." height="..." style="width:100%"></canvas>
    <figcaption>What the reader controls and what recomputes.</figcaption>
  </figure>
  <p>controls: <input id="lab-NAME-x" type="range" ...></p>
  ```
  In `labs.js`, one IIFE per lab, wrapped so it runs after render:
  ```js
  document.addEventListener('DOMContentLoaded', function(){
    var c = document.getElementById('lab-NAME'); if(!c) return;
    /* compute the REAL quantity from inputs; redraw on 'input' */
  });
  ```
- **Layout widths:** `l-body` (default reading column ~648px) · `l-page`/`l-page-outset` (wide figures) · `l-screen` (full-bleed teaser) · `l-gutter` (margin asides). Section kicker: `<span class="marker">…</span>`.
- **Color discipline:** link `#004276`; entity highlight via `<span style="background:#FFD5D5">…</span>`; canvas colors restrained (deep blue `#004276`, teal `#009688`, grey `rgba(0,0,0,0.6)`). No gradients/neon/shadows.

## The 5-part spine — a GUIDE to vary, not a template to stamp
These are the *beats a good explainer hits*, not a fixed skeleton. Vary the section count (4–7), titles, and ordering per topic (see anti-fingerprint rule 3). The build plan assigns each generator a beat; the harmonize pass must NOT flatten them into an identical I–V stamp.
- **P1 — Front matter + cold open + roadmap.** `d-title` (auto from front-matter), then a vivid concrete hook (no "Introduction" heading), optional `l-screen` teaser figure, one roadmap sentence naming the parts.
- **P2 — Problem framing + intuition.** State the naive view, then subvert it; plain-language/analogy build-up; italicize each new term on first use; first small interactive that motivates the problem.
- **P3 — Mechanism derived + headline lab.** Stage the equations incrementally (notation → steps → closed form), annotate with `\overbrace{}^{\text{...}}`; the headline data-bound lab that *computes* the derived quantity live.
- **P4 — Worked example + secondary labs + caveats.** Napkin numbers on a concrete instance; a **break-it demo** (failure mode); an honest limitations paragraph.
- **P5 — Context / "why not X" + honest close + appendix.** Alternatives and why this view wins; open-problem coda; appendix tail (Acknowledgments → Discussion → References → Reuse → Citation — mostly template-generated).

## Voice — native Chinese, distill's spirit (corpus_dna §4)
Write the Chinese a sharp Chinese researcher writes, carrying distill's pedagogy — NOT translated English.
- 第一人称复数"我们"/"我们来"承载推导；交互提示用第二人称"你"（"拖动下面的滑块…"）。语气平实、像老师、诚实不夸大。
- 新概念：先用大白话和一个具体例子讲清直觉 → 再点出术语（中文术语，首次可括注英文原词）→ 最后才形式化。绝不形式先行。
- 数学夹在句中行文里；只有铺垫完直觉才上独立公式块。
- **段落收尾要有变化**：大多数小节顺着下一个想法自然停住；不要每节都用一句工整的金句收尾（这种节奏是头号机器痕迹）。
- **避免翻译腔**：不要"它是一个能做X的方法"、"这一事实"、英式长定语从句直译、被动句堆叠、"换句话说/值得注意的是"这类套话。句子长短交错，允许偶尔一句长的、口语化的旁白。
- 句末标点、术语、数字与单位按中文技术写作习惯。

## Interaction rules (corpus_dna §3)
≥1 substantial reader-driven interaction per major section; ≥1 failure-mode demo in the article; each interaction recomputes the real quantity (no GIF/pre-rendered/perturbed fakes); the headline figure *is* the argument. When something truly can't compute live, ship a clearly-labeled static figure. **Never tell the reader the interaction is real** — see anti-fingerprint below.

**Lab layout/perf is a hard gate — read [`lab_authoring.md`](lab_authoring.md).** Size every canvas with `so.fit(c,{aspect})` (height derived from width, never hardcoded-tall); draw within `[0,W]×[0,H]` (no clipping); drive drags via `so.drag` and heavy redraws via `so.raf`/`so.debounce` (never block the main thread); train/fit loops must reduce loss and plot an auto-scaled history curve. `bin/qa.py` fails the build on too-tall / clipped / freeze.

## Anti-fingerprint — the hard rules (blind judges caught earlier drafts at 100%)
A strict reader comparing several outputs spots a *template stamp* and *machine-even smoothness* even when each article is individually good. These are mandatory:

1. **Never advertise your own rigor.** HARD-BAN phrases like "computed live", "no frame is pre-rendered/cached", "no pre-baked data", "recomputed on every input event", "real Monte-Carlo", "genuinely computed". Let the reader discover it by dragging. (corpus_dna §0 gotcha: let the work speak.)
2. **No formulaic section titles.** Do NOT title sections "Break it", "What is still open", "Napkin numbers", "Now the honest part". Use natural, topic-specific headings a human would write. The failure-mode demo and the limitations belong in prose, not under a stock label.
3. **Vary the structure.** Do NOT stamp every article with an identical Roman-numeral I–V five-act arc. Vary the section *count* (4–7), their *titles*, and *where the lab lands*. Real distill articles do not share a skeleton. (Use plain descriptive `<h2>` titles; a kicker `<span class="marker">` is optional, not a mandatory I–V counter.)
4. **Break the smoothness.** Avoid relentless symmetry: no habitual tricolons / three-beat parallel lists, no "almost embarrassingly simple/literal", no section that resolves into a neat slogan. Let paragraph lengths vary; allow one or two longer, discursive sentences; an offhand aside or concrete reference is good.
6. **Plain by default; flourish is rare and earned.** This is the deepest tell — a blind panel still caught earlier drafts because the prose was *too good*: every section ended on a turned antithetical epigram ("Cancellation is noisy; carried slope is not"), sustained clever metaphors, not a single rough edge. Real distill is **plain and teacherly the vast majority of the time**, with a flourish only once or twice in a whole article. So: cap crafted metaphors at ~1–2 per article; let MOST sections end on the next plain idea, not a quotable line; let some passages be workmanlike and unclever; vary sentence quality (not every sentence is polished). Relentless wit and flawless evenness read as machine — aim for competent clarity that occasionally, not constantly, sparkles.
5. **Blacklist (English + Chinese):** openers/closers like "In this article we will explore" / "Let's dive in" / "In conclusion" and their Chinese套话 "在本文中我们将探讨"/"让我们深入了解"/"综上所述"/"总而言之"/"接下来，让我们"/"首先…其次…最后"/"值得一提的是"/"不难发现"; emoji; listicle padding; decorative figures; gradient/neon/card-shadow styling; asserting results instead of deriving; omitting limitations; math as images; sliders that don't recompute.
7. **No translationese (Chinese output).** The Chinese must read as originally-written, not machine-translated: avoid English-shaped long attributive clauses, stacked passives, "X 是一个能够 Y 的 Z" definitions, and 1:1 rendered idioms. Vary connectives; prefer short clear clauses. A blind Chinese reader should not feel an English skeleton underneath.
