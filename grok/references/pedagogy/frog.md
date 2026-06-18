# Pedagogy · frog

Bottom-up, worked-example first; build / compute / observe, abstraction emerges. Two valid spines:

- **Karpathy "zero to hero" — code-as-spine.** Open with a code cell of the actual artifact (the command, the function, the data). Each cell takes the smallest next step. Reader watches the abstraction get built; every claim is backed by a concrete computation they could redo. `In [N]:` / `Out[N]:` rhythm with markdown narration.
- **Andrew Ng CS229 — math-as-spine.** Start from the simplest concrete problem (one-feature linear regression, tiny dataset). Derive: likelihood → log-likelihood → gradient → update rule → algorithm. Each line of math is the smallest next step. Generalize after the simplest case is chewed.

A page can lean fully Karpathy (code-only), fully Ng (derivation-only), or mix. The reader closes the page feeling *they could write this themselves now*.

Default visual: [notebook](../visual/notebook.md). Alternate: [simple](../visual/simple.md) (frog-flavored sub-style).

## Voice (the frog delta)

§6 fixes the shared **讲解 register (cs231n course-note)**. This section is frog's *altitude / spine* delta
on top of that register — bottom-up moves, not a different voice.

- **Example before abstraction.** Open with a concrete instance — code cell of the actual artifact (Karpathy) or the smallest numerical problem the algorithm solves (Ng). Narration explains what just happened, not what's about to happen.
- **Spelled out.** "Let's just write this from scratch and see" / "Let's derive this from the likelihood." Smallest next step per cell or line. Never reference unwritten future cells / derivations; build forward.
- **Stop-and-think pauses.** Every few cells: "停一下，注意…" / "如果改成… 会怎样？" / "这里是大家容易卡住的地方。" Short, surfacing a non-obvious insight — §6's preempt-confusion move in frog's cadence.
- **Analogies to things the reader already wrote.** "This is the same pattern as PyTorch autograd's backward pass." "If you've written `__radd__`, you've already done this."
- **Numbers verbatim.** Real demo's stdout pastes byte-for-byte, labeled `Out[N]:`. Fidelity is the credibility.

## Voice self-audit

- [ ] Prose follows the **cs231n register** (principles §6): motivation-first, conversational 我们, preempt confusion, no 论文腔 / AI 味.
- [ ] Cold open is a code cell + output cell pair (Karpathy) or simplest derivation (Ng), not a TOC or abstract.
- [ ] At least one explicit "stop & think" or "类比" callout per page.
- [ ] Numbers in `Out[N]:` cells are verbatim from real runs (or clearly marked "typical / illustrative").
- [ ] Every 2–3 code cells has a markdown cell between them.

## Voice exemplars

- Karpathy "Zero to Hero" series — code-as-spine cadence; `In/Out` rhythm with sparse but earned narration.
- Andrew Ng CS229 lecture notes — derivation-as-spine cadence; likelihood → gradient → algorithm with smallest-case grounding.

## Legacy aliases

`--style stanford` · `--style karpathy` · "Karpathy 风格" · "Stanford 风格" · "Ng 风格" · "CS229 风格" silently resolve to frog.
