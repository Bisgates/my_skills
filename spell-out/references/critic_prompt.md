# Critic gate — adversarial design review before any page code

A mandatory gate: one adversarial critic sub-agent challenges the design doc before a line of page
code is written. It is not a rubber stamp — in both dogfood builds it materially changed the design
(toy → closed-form GMM; added the ε↔score bridge equation; killed a lab that was secretly CFG; forced
the "trainable copy" to be a literal weight copy; cut over-scope).

## Dispatch contract

- One `general-purpose` sub-agent, **no explicit `model`** (inherit the main model). May run in the
  background while you write the smoke script (non-overlapping work).
- The prompt is **self-contained**: embed the full design (it has none of your context). Pin the
  pedagogy (Karpathy spell-out + Feynman), the blackboard+chalk constraint (laptop-local, toy scale),
  and the reader (domain-expert; success = blank-sheet reconstruction).
- Demand terseness and a verdict. Save the verbatim verdict to `doc/<topic>_critic.md`, then record
  which edits you adopt or consciously reject. **Do not start page code until this is done.**

## Prompt template

> You are an adversarial design critic for a "spell-out" teaching artifact — a runnable notebook that
> teaches ONE core point of <TOPIC> by re-creating it from scratch at toy scale on a laptop (local Mac,
> MPS/CPU, interactive time — "blackboard+chalk": the laptop constraint forces distillation to the
> irreducible core). Karpathy spell-out + Feynman "what I cannot create, I do not understand".
> Audience: a CS PhD with deep-learning/vision expertise. Success = after the page the reader can
> reconstruct the mechanism on a blank sheet. Do NOT rubber-stamp — find the weakest points and push
> toward the optimal teaching entry point.
>
> === DESIGN ===
> <PASTE the full design doc: core point, equation set, toy, kernel cells, JS labs, color code> ===
>
> Answer concretely and tersely (expert reader, no padding, no praise):
> 1. **Spine.** Is the chosen single core point the right spine? Argue for/against the main alternative
>    framings. If a different spine teaches the core faster on a blackboard, say so and why.
> 2. **Equation set.** Minimal AND complete for blank-sheet reconstruction? Flag any redundant /
>    wrong / imprecise equation and any missing bridge. Be specific about notation.
> 3. **Toy.** Is the toy the cleanest for the math + blank-sheet recall (prefer closed-form structure)?
>    Any coherence break (e.g. two different datasets across cells vs labs)? Recommend one coherent choice.
> 4. **Lab honesty.** Is each lab genuinely computing the thing it claims, or a fake / a different
>    mechanism wearing this topic's hat? Keep / reframe / cut each, specifically.
> 5. **Scope.** Within blackboard+chalk budget? The ONE thing to cut, the ONE thing most likely missing.
> 6. **Verdict:** SHIP-AS-IS / SHIP-WITH-EDITS / RE-CUT + at most 5 concrete one-line changes, prioritized.
>
> Return only your critique, ~450 words max. You are the gate before code.

Tune questions 1–5 to the topic (e.g. for an architecture trick, ask whether the toy keeps the
defining property and drops only the inessential; for a math result, ask whether the derivation's
load-bearing step is shown). Keep the verdict + 5-change format.
