# Principles: what makes an interactive technical report teach

Task-agnostic craft principles behind `distill`. Distilled from auditing many AI-generated interactive explainers — what genuinely teaches versus what only looks impressive on a skim. Read this to understand *why* the rules in `SKILL.md` exist; they apply to any topic.

## 1. Compute the real thing

An interactive figure earns its place when manipulating it reveals something true. The quiet failure is an interaction that looks live but isn't — a "diffusion" slider that blends toward a pre-drawn noise cloud, an "attention map" that's a fixed gradient, a "calibration" that perturbs the known answer instead of solving, a chart of hardcoded paper numbers. They give the reader a confident wrong intuition, because people trust what they can drag.

So run the actual update rule, solver, or training loop. When the full method is too heavy for a browser, build the smallest version that still exercises the idea — a 1-D toy, a 2×2 system, a 16-unit net, forty diffusion steps. A small real thing beats a large fake one. If a step truly can't be computed live, show it as a labeled static illustration. A useful check: could a skeptical reader open the JS and see that the number on screen came from the formula above it?

## 2. Interaction = insight, not decoration

A control should let the reader drive a cause and see its effect. A slider that only scrubs a pre-scripted playback is decoration. The most valuable interactions let the reader *break* the mechanism — turn off the Langevin noise and watch samples collapse, shrink σ until the density develops holes, make three columns coplanar and watch the solution degenerate. Understanding a mechanism includes knowing what it protects against, so include at least one break-it demo.

## 3. Derive, don't assert

Depth is the difference between stating a result and showing where it comes from: merge the two Gaussians for the closed-form forward process, complete the square for the reverse posterior, show why the normalizer cancels. One honest derivation of the load-bearing step beats ten cited results. Cover the degenerate case — that's where the understanding is.

## 4. Begin with why, and put the example before the abstraction

Open on the predicament: what was the field stuck on, what's the naive thing to try, why does it fail? That tension makes the mechanism land. For each new concept, give a napkin-sized worked example with tiny concrete numbers before the general formula, so the reader anchors on the instance then generalizes. Chain it: end each section by creating the problem the next one solves.

## 5. Reading scaffolding makes it feel complete (and is cheap)

The layer that separates a polished report from a wall of text: a scroll-progress bar, a scroll-spy chapter nav, a comfortable reading column (~760–820px), semantic callouts, numbered equations each with a one-line plain-language gloss, clean math rendering. None of it is hard; together it reads as care. A self-test quiz turns passive reading into a checkpoint.

## 6. A running example threaded through the report

Reusing one concrete object — a single toy distribution, one matrix, one scene — across every section gives the reader a stable anchor; each new idea becomes a new lens on the same thing rather than a fresh setup to absorb.

## 7. Quiet consistency

Give each recurring entity one color and keep it everywhere — prose, formulas, canvas — so color means the same actor throughout. Name algorithms for what the code actually does. Distinguish illustrative values from measured ones. These are correctness habits, not features to spotlight — and the report itself shouldn't narrate them or advertise its own rigor. Let the work speak.
