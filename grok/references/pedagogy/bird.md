# Pedagogy · bird

Top-down conceptual narrative. The reader is walked through the field-level predicament, the naive-and-wrong instinct, the source's insight as rescue, and the mechanism that follows. Concrete worked examples and physical anchors are deployed *inline* at each new concept — the way every abstraction enters the reader's head, not collected at section end. Lineage: Feynman lectures + Karpathy long-form essays. Reference exemplar: `~/Library/Mobile Documents/com~apple~CloudDocs/Learn With Opus/佛教-无常.html`.

Default visual: [magazine](../visual/magazine.md). Alternate: [simple](../visual/simple.md) (bird-flavored sub-style).

## Voice (the bird delta)

The 9 shared principles in [`principles.md`](principles.md) cover what every grok page must do. This section is the *how* — the bird-specific register on top of those principles.

- **Reveal, don't state.** Not "X equals Y" but "why X must equal Y — because Z." Every claim earned by the prose around it; no asserted-without-shown facts. The reader watches each insight fall out of what came before, instead of being told it.
- **Physical / mechanical intuition anchor before every formula.** "Score function = uphill direction." "Adding noise = smearing the ridge." "Normalization constant Z = volume integral over all of space." One-line metaphor, then the symbol. Principle 6 makes this allowed; bird makes it non-negotiable per formula.
- **Predict-then-verify.** "If X were really true, we should see Y — and the source does show Y." Hypothesize the consequence first, then point at the evidence. Reader's belief is earned by the prediction landing, not by the author's authority.
- **Inline worked example, not appendix.** Principle 3 worked examples sit at the moment the abstraction enters, not at section end. Numbers stay napkin-redoable. The example is *how* the concept becomes real for the reader, not an "illustrative aside" the reader could skip.
- **Magazine pacing.** Long reasoning paragraphs interrupted by one-line breath punches. Rhetorical questions and colloquial pivots — "问题来了" / "等等 ——" / "注意一个微妙的点" / "听起来很玄, 其实……" / "换句话说". First and second person — "我们" / "你会发现" / "试着想一下". At least one `.pullquote` per page interrupting the body with an attributed punch-line.
- **Section close = one earned meta-line.** Plain Chinese; names what just shifted in the reader's worldview. Not "综上所述", not a textbook recap. Example from 无常 ch1: *"把'事物'换成'事件相续'之后，'无常'不再是一句感叹，它变成一个定义性命题。"* The line is allowed to be quiet — if it earns its place it does not need to be loud.

## Voice self-audit

- [ ] Every new concept has a **physical / mechanical intuition anchor** stated *before* its formula.
- [ ] Every new concept's **worked example sits inline** at first introduction, not collected at section end.
- [ ] At least one **predict-then-verify** beat per page.
- [ ] At least one **pull-quote** (`.pullquote` with `.who`) somewhere in the body.
- [ ] Every major section closes with one earned **meta-line** in plain Chinese — not a recap.
- [ ] Magazine pacing audit: long paragraphs are followed by short ones; at least one rhetorical question or colloquial pivot per chapter.
- [ ] No paper-boilerplate phrases. AI 味自检: "不是 X，而是 Y" 对仗 ≤ 1–2 处; 没有 "值得深思 / 综合来看 / 让我们一起 / 总而言之".

## Voice exemplars

- `~/Library/Mobile Documents/com~apple~CloudDocs/Learn With Opus/佛教-无常.html` — the reference page this voice is calibrated against. Top-down arc (实体观 → 事件流 → 三法印逻辑链) with concrete anchors (烛火粒子流, 一杯茶 4×10³⁸ 微观事件, 一次愤怒 60 秒分解) inline at every new concept.
- Richard Feynman, *The Feynman Lectures on Physics* — picture before equation; the reader sees the mechanism before the symbol.
- Andrej Karpathy long-form essays — "Yes you should understand backprop", "A Recipe for Training Neural Networks". Top-down narrative deploying concrete numerical examples inline.

## Legacy aliases

`--style mit` · `--style feynman` · `--style hamming` · `--style sicp` · "MIT 风格" · "SICP 风格" · "费曼风格" · "Hamming 风格" · "Strang 风格" silently resolve to bird. The Hamming / SICP routes are retained for backward addressability — bird is the only top-down pack we ship, so requests in that family land here even though the voice is now Feynman-flavored rather than Hamming-flavored. The `.feynman` CSS class names a UI element (dark plum meta-insight callout card), not a posture — keep using it.
