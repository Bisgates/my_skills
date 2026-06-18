# Rubric: quality of an interactive technical report

A scoring instrument for `distill` output. Two uses: (1) self-audit your own report before shipping; (2) score reports blind, A/B, when comparing approaches. Dimensions and weights put genuine computation and depth first, so polish can't paper over an empty interaction.

## How to judge

You cannot run the page. For every interactive element, open its JavaScript and decide whether it actually computes the quantity it represents, or only looks live (a pre-rendered blend, a hardcoded result, a perturbed ground-truth stand-in). Score each dimension 1–5 with a one-line file:line justification. When comparing two reports, ignore which tool or author made each and don't reward a theme (dark vs light) — score the content.

## Dimensions (weights sum to 100)

### ① Correctness & genuine computation — 30
Does each interaction / figure / formula compute what it represents, and is the math right?
- **5** — every headline interaction is genuinely computed (real solve / train / project), derivations are correct, numbers reproduce.
- **3** — the main interactions are real, but one or two figures are decorative or hardcoded, or a derivation has a small slip.
- **1** — a flagship interaction is faked (pre-rendered blend, perturbed ground-truth, a demo labeled "solve/train" that doesn't), or there's a substantive math error.

### ② Depth — 22
- **5** — key results are derived, not asserted; degenerate/edge cases covered; connected to alternatives.
- **3** — mechanism is clear but the load-bearing step is hand-waved; little edge-case discussion.
- **1** — conclusions listed with no derivation, edges, or comparison.

### ③ Interaction density & pedagogy — 20
Count **and** quality: does each interaction let the reader drive a cause and see an effect (vs decorative playback)?
- **5** — ≥6 interactions, most reader-driven, including ≥1 break-it demo.
- **3** — several interactions but half are passive playback; weak cause→effect.
- **1** — few or only decorative interactions.

### ④ Teaching clarity — 16
- **5** — begin-with-why cold open; a napkin worked example before each abstraction; quiz/checkpoints; reads in the cs231n register (motivation-first, conversational, 「核心思想」 signposts, preempts confusion); no filler phrasing.
- **3** — clear but flat opening; examples occasional; no self-test.
- **1** — definition dump, no motivation, no examples.

### ⑤ Visual & information design — 12
- **5** — consistent entity colors carried into the canvas; reading furniture (scroll-spy / progress / sensible column); clean math; responsive + DPR + basic a11y.
- **3** — coherent but colors don't reach the canvas, or retina-blurry, or breaks on mobile.
- **1** — cluttered; no color system; ugly math; desktop-only.

## Veto

If a report's flagship interaction is faked (you score ① ≤2 with evidence), it cannot be rated top-tier overall, regardless of the other dimensions — a polished page built around an empty centerpiece misleads the reader.

## Aggregation

- Weighted score = Σ(dimension × weight) / 100.
- Comparing two reports: higher weighted score wins; within 0.2 is a tie. With a panel, take the majority; randomize and counterbalance A/B order to remove position bias.

## Output format (per judgment)

```json
{
  "scores": {"correctness": n, "depth": n, "interaction": n, "clarity": n, "visual": n},
  "evidence": {"correctness": "file:line …", "…": "…"},
  "weighted": x.x,
  "veto": false,
  "one_line": "…"
}
```
(When comparing two, emit one such block per report plus an `overall_winner` and `confidence`.)
