# Pedagogy · bird

Top-down, abstraction-first, derived from first principles. Lineage: Richard Hamming, *The Art of Doing Science and Engineering* (30 lectures, 1995). Signature arc: open with the question behind the question → strip details → derive method from goal → close with the principle to remember when details fade.

Default visual: [magazine](../visual/magazine.md). Alternate: [simple](../visual/simple.md) (bird-flavored sub-style).

## Voice (the bird delta)

- **Question-first.** Surface the meta-question before the method. "What are we really trying to accomplish here?" / "What's the question behind the question?" is the canonical opening beat.
- **Top-down decomposition.** Goal → constraints → method falls out as the unique (or near-unique) thing that satisfies them. Reader watches the method *fall out of* the constraints, not get *announced*.
- **Asymptotic / extreme-case lever.** Push a parameter to 0 or ∞ and see what the algorithm degenerates to. Shape of the limit reveals structure of the general case. Hamming reflex: digital filters → 0-bandwidth, error codes → 0 noise, neural nets → 1 example.
- **Cross-domain transfer.** "The same trick appears in [other field] because [abstract reason]." One or two per page lands; five turns the page into name-dropping. Each transfer carries the *abstract reason* the trick reappears, not just the fact that it does.
- **Physical / mechanical intuition anchors.** Every abstract symbol gets a concrete metaphor before its formula. "Score function = uphill direction." "Z = volume integral over all of space." "Channel capacity = the rate at which surprise can pass through a pipe."
- **Meta-reflection close.** Each major section ends with a short "principle to remember when details fade" beat — pull-quote, italic afterword, or `.feynman` block.
- **Long-form rhythm.** Magazine pacing — long reasoning paragraphs interrupted by one-line breath punches. Pull-quotes interrupt the body.

## Voice self-audit

- [ ] Cold open lifts to the **meta-question** before any method is shown.
- [ ] Method is **derived from goal + constraints**, not announced as a clever idea.
- [ ] At least one **asymptotic / extreme-case** observation per page.
- [ ] At least one **cross-domain transfer**, even briefly.
- [ ] Each major section closes with a **meta-reflection** beat.
- [ ] Page closes with a page-wide meta-reflection (final afterword or `.feynman`).
- [ ] No paper-boilerplate ("本文 / 综上 / 不失一般性 / 显然地").

## Voice exemplar

Hamming, *The Art of Doing Science and Engineering: Learning to Learn* — 30 lectures at the Naval Postgraduate School, 1995. The arc is taken from it directly. When in doubt how to open or close a section, re-read one of: "Coding Theory," "Digital Filters," "Simulation," "You and Your Research."

## Legacy aliases

`--style mit` · `--style feynman` · "MIT 风格" · "SICP 风格" · "费曼风格" · "Strang 风格" silently resolve to bird. The `.feynman` CSS class names a UI element (dark plum meta-insight callout card), not a posture — keep using it.
