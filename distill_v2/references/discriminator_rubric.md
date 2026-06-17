# Discriminator rubric — "is this real distill?" (arc 260616a)

Purpose: a **strict, evidence-forced** judge used in the adversarial loop and at acceptance. Calibrated against the corpus DNA (`corpus_dna.md`). Designed to defeat the #1 failure mode of past adversarial-learning runs: **lenient judges that rubber-stamp "passed" when it hadn't.**

## Strictness mechanisms (non-negotiable, enforce on every run)

1. **Calibration anchor (sanity gate).** Before judging any candidate, the discriminator is shown 1 known-real distill article + 1 known-generic-AI explainer and must correctly classify both with cited evidence. If it cannot, its verdict on the candidate is discarded and the agent is re-run. A judge that can't tell anchors apart cannot judge candidates.
2. **Evidence-or-it-didn't-happen.** Every dimension score must cite ≥2 concrete artifacts from the HTML: a CSS selector, a tag name, a quoted sentence, a `grep` hit, or "ABSENT: searched for X, not found". A score with empty `tells` is invalid → re-run.
3. **Default-to-generated.** Uncertainty resolves *against* the candidate. Benefit of the doubt is forbidden. If a framework marker is missing, you may not assume "they chose to omit it" — score it as a tell.
4. **Hard caps.** A missing distill-framework signature (no `d-*` elements OR no `distill-prerendered-styles` OR no DOI/appendix) **caps D1 ≤ 30 and caps the overall verdict at "generated"** regardless of other dimensions. Pretty ≠ distill.
5. **Three independent agents, distinct lenses, no shared context.** Each runs blind to the others; majority + score-distribution decides. Diversity catches what redundancy misses.
6. **Adversarial framing.** Each agent is told: "Your job is to CATCH the fake. Assume it is fake until the evidence forces otherwise."

## Dimensions (score each 0–100; cite evidence)

### D1 — Framework & markup fidelity (weight 30, the hardest tell)
Checks for the literal distill template signature. Tests:
- `d-article / d-title / d-byline / d-cite / d-footnote / d-math / d-figure / d-appendix / d-bibliography` present? (or era-correct `dt-*`)
- `<style id="distill-prerendered-styles">` with the Apache "Distill Template Authors" header? `<body distill-prerendered>`?
- Named-line 8-col grid (`[screen-start]…[page-start kicker-start text-start gutter-start]…`) + `.l-body/.l-page/.l-gutter/.l-screen` classes?
- Real `10.23915/distill.*` DOI, ISSN 2476-0757, `citation_*` meta, `d-front-matter` JSON?
- Appendix tail present (Acknowledgments → Discussion and Review → References → Reuse CC-BY → Citation BibTeX)?
- Anchors: 90+ = all signatures present and well-formed; ≤30 = any core signature absent.

### D2 — Visual system fidelity (weight 20)
- Era-consistent typography (v1 Georgia/Hoefler OR v2 system-sans 14→16px)?
- Restrained 3–4 color palette: link `#004276`, captions `rgba(0,0,0,0.6)` 12–13px, teal `#009688`, warm figure bg? No gradients/neon/drop-shadows?
- Width tiers used meaningfully (full-bleed `l-screen` teaser, `l-body` column, `l-gutter` asides)?
- 90+ = palette + typography + layout all match the era; ≤40 = generic Tailwind/Bootstrap look, card shadows, rainbow.

### D3 — Interaction authenticity (weight 20)
- ≥6 reader-driven interactions? Each *recomputes* the quantity it shows (open the JS and verify the on-screen number derives from the formula)?
- ≥1 break-it / failure-mode demo? Figure-is-argument (not decorative)?
- No GIF/CSS-anim/pre-rendered "results" masquerading as live?
- 90+ = solver/data-bound recompute verified in source; ≤40 = sliders that don't compute, or static figures dressed as interactive.

### D4 — Pedagogical structure (weight 15)
- Cold-open hook (no "Introduction" boilerplate)? Problem-first (naive view stated then subverted)? Intuition-before-formalism?
- Results derived not asserted (annotated equations, staged)? Worked example with napkin numbers? Honest-limitation/open-problem section?
- 90+ = full begin-with-why spine + derived mechanism + honest coda; ≤40 = listicle / assertion-dump / no limitations.

### D5 — Prose voice (weight 15) — judged as CHINESE (artifact language)
The artifact is Chinese, so D5 is **not** anchored on English distill prose; judge it as native high-quality Chinese technical writing carrying distill's spirit, the way a sharp Chinese researcher would.
- 第一人称复数"我们"承载推导，交互提示用"你"；语气平实、像老师、诚实不夸大？
- 新概念：大白话+具体例子 → 点出术语 → 才形式化（绝不形式先行）？直觉先于公式？
- **无 AI 腔 / 套话**：无"在本文中我们将探讨 / 让我们深入了解 / 综上所述 / 值得一提的是 / 首先…其次…最后"、无 emoji、无 listicle 注水、无每节金句收尾？
- **无翻译腔（关键）**：读起来像原生中文而非英译中——没有英式长定语从句、堆叠被动、"X 是一个能够 Y 的 Z"式定义、1:1 直译习语？
- 90+ = 像中文母语高手原写、且有 distill 的教学气质；≤40 = 明显翻译腔、AI 套话、或形式先行。
- (D1–D4 stay language-agnostic and are still anchored on the real distill corpus; only D5 switches to a Chinese standard.)

## Output contract (each agent, JSON)
```json
{
  "anchor_check": {"real_correct": true, "fake_correct": true, "evidence": ["…","…"]},
  "article_id": "…",
  "dims": {
    "D1_framework":   {"score": 0-100, "tells": ["…","ABSENT: …"]},
    "D2_visual":      {"score": 0-100, "tells": ["…"]},
    "D3_interaction": {"score": 0-100, "tells": ["…"]},
    "D4_pedagogy":    {"score": 0-100, "tells": ["…"]},
    "D5_prose":       {"score": 0-100, "tells": ["…"]}
  },
  "weighted_score": 0-100,
  "source_guess": "distill" | "generated",
  "confidence": 0.0-1.0,
  "top_3_giveaways": ["the 3 features that most drove the verdict"]
}
```

## Acceptance arithmetic (Step 6) — Chinese artifact
The artifact is Chinese, so the literal English `source_guess` blind test does not apply. Split the bar:
- **D1–D4 (language-agnostic):** score the distill_v2 output against the real distill corpus; each must fall **within the [min, max] band of the real-distill set** (not below the real floor on any dimension). The framework/visual/interaction/pedagogy must be genuinely distill-grade.
- **D5 (Chinese prose):** ≥ the real-distill band's equivalent (target ≥ ~80/100) judged as native Chinese technical writing — explicitly checked for **translationese and AI-tells**; anchor the judge on a strong Chinese technical article, not on English distill.
- **Human A/B (Stage 2):** the reader judges the article as good as a real distill piece (not machine-made, not translated) and, after reading, deeply understands the topic.
- A run where any agent fails its anchor check is void and re-run. (For D5 the anchor pair is a strong real Chinese technical article + a translationese/AI-generated Chinese explainer.)
