# Pedagogy · frog

Bottom-up, worked-example first; build / compute / observe, abstraction emerges. Two valid spines:

- **Karpathy "zero to hero" — code-as-spine.** Open with a code cell of the actual artifact (the command, the function, the data). Each cell takes the smallest next step. Reader watches the abstraction get built; every claim is backed by a concrete computation they could redo. `In [N]:` / `Out[N]:` rhythm with markdown narration.
- **Andrew Ng CS229 — math-as-spine.** Start from the simplest concrete problem (one-feature linear regression, tiny dataset). Derive: likelihood → log-likelihood → gradient → update rule → algorithm. Each line of math is the smallest next step. Generalize after the simplest case is chewed.

A page can lean fully Karpathy (code-only), fully Ng (derivation-only), or mix. The reader closes the page feeling *they could write this themselves now*.

Default visual: [notebook](../visual/notebook.md). Alternate: [simple](../visual/simple.md) (frog-flavored sub-style).

## Voice (the frog delta)

- **Example before abstraction.** Open with a concrete instance — code cell of the actual artifact (Karpathy) or the smallest numerical problem the algorithm solves (Ng). Narration explains what just happened, not what's about to happen.
- **Spelled out.** "Let's just write this from scratch and see" / "Let's derive this from the likelihood." Smallest next step per cell or line. Never reference unwritten future cells / derivations; build forward.
- **Stop-and-think pauses.** Every few cells: "okay, take a moment to notice…" / "stop — what would happen if…" / "here's the part that confuses people." Short, conversational, surfacing a non-obvious insight.
- **Analogies to things the reader already wrote.** "This is the same pattern as PyTorch autograd's backward pass." "If you've written `__radd__`, you've already done this."
- **Lowercase, conversational.** "okay 接下来", "好我们直接看一下这段代码", "等等 — 你可能想…". Not magazine register. Not paper register.
- **Numbers verbatim.** Real demo's stdout pastes byte-for-byte, labeled `Out[N]:`. Fidelity is the credibility.

## Voice self-audit

- [ ] Cold open is a code cell + output cell pair (Karpathy) or simplest derivation (Ng), not a TOC or abstract.
- [ ] Markdown cells use lowercase conversational openers.
- [ ] At least one explicit "stop & think" or "类比" callout per page.
- [ ] Numbers in `Out[N]:` cells are verbatim from real runs (or clearly marked "typical / illustrative").
- [ ] Every 2–3 code cells has a markdown cell between them.

## Voice exemplars

- Karpathy "Zero to Hero" series — code-as-spine cadence; `In/Out` rhythm with sparse but earned narration.
- Andrew Ng CS229 lecture notes — derivation-as-spine cadence; likelihood → gradient → algorithm with smallest-case grounding.

## Legacy aliases

`--style stanford` · `--style karpathy` · "Karpathy 风格" · "Stanford 风格" · "Ng 风格" · "CS229 风格" silently resolve to frog.
