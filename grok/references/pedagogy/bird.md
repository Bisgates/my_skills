# Pedagogy · bird

Top-down conceptual narrative. The reader is walked through the field-level predicament, the naive-and-wrong instinct, the source's insight as rescue, and the mechanism that follows. Concrete worked examples and physical anchors are deployed *inline* at each new concept — the way every abstraction enters the reader's head, not collected at section end. Lineage: Feynman lectures + Karpathy long-form essays. Reference exemplar: `~/Library/Mobile Documents/com~apple~CloudDocs/Learn With Opus/佛教-无常.html`.

Default visual: [magazine](../visual/magazine.md). Alternate: [simple](../visual/simple.md) (bird-flavored sub-style).

## Voice (the bird delta)

The 9 shared principles in [`principles.md`](principles.md) cover what every grok page must do, and §6
fixes the shared **讲解 register (cs231n course-note)**. This section is bird's *altitude* delta on top of
that register — the top-down moves, not a different voice.

- **Reveal, don't state.** Not "X equals Y" but "why X must equal Y — because Z." Every claim earned by the prose around it; the reader watches each insight fall out of what came before, instead of being told it.
- **Intuition anchor before every formula.** §6 asks for intuition before formalism; bird makes it non-negotiable *per formula* — "score function = uphill direction", "normalization constant Z = volume integral over all of space" — the picture or number, then the symbol.
- **Predict-then-verify.** "If X were really true, we should see Y — and the source does show Y." Hypothesize the consequence first, then point at the evidence; belief is earned by the prediction landing, not by the author's authority.
- **Inline worked example, not appendix.** Principle 3 worked examples sit at the moment the abstraction enters, not at section end. Numbers stay napkin-redoable. The example is *how* the concept becomes real for the reader, not an "illustrative aside" the reader could skip.

## Voice self-audit

- [ ] Prose follows the **cs231n register** (principles §6): motivation-first, 「核心思想」 signpost, preempt confusion, section recap, no 论文腔 / AI 味.
- [ ] Every new concept has an **intuition anchor** stated *before* its formula.
- [ ] Every new concept's **worked example sits inline** at first introduction, not collected at section end.
- [ ] At least one **predict-then-verify** beat per page.

## Voice exemplars

- `~/Library/Mobile Documents/com~apple~CloudDocs/Learn With Opus/佛教-无常.html` — the reference page this voice is calibrated against. Top-down arc (实体观 → 事件流 → 三法印逻辑链) with concrete anchors (烛火粒子流, 一杯茶 4×10³⁸ 微观事件, 一次愤怒 60 秒分解) inline at every new concept.
- Richard Feynman, *The Feynman Lectures on Physics* — picture before equation; the reader sees the mechanism before the symbol.
- Andrej Karpathy long-form essays — "Yes you should understand backprop", "A Recipe for Training Neural Networks". Top-down narrative deploying concrete numerical examples inline.

## Legacy aliases

`--style mit` · `--style feynman` · `--style hamming` · `--style sicp` · "MIT 风格" · "SICP 风格" · "费曼风格" · "Hamming 风格" · "Strang 风格" silently resolve to bird. The Hamming / SICP routes are retained for backward addressability — bird is the only top-down pack we ship, so requests in that family land here even though the voice is now Feynman-flavored rather than Hamming-flavored. The `.feynman` CSS class names a UI element (dark plum meta-insight callout card), not a posture — keep using it.
