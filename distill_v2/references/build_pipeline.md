# distill_v2 build pipeline (the proven path)

The adversarial assembly loop, validated on calibration (reparameterization trick → D1 86 / D2 83 / D3 90 / D4 92 / D5 88, all three strict judges classified "distill"). Run it in order. Parallelize the fan-out stages.

## Stages

1. **Lock the build plan** (1 agent). From the topic, produce `build_plan.json`: `title, dek, authors, running_example, entities[{name,symbol,color}], parts[P1..P5 {h2, brief, labs[{id,teaches,inputs,computes,draws}], cites}], interaction_count, breakit`. Settle ONE running example and the entity→color map here so every part stays consistent. **Reader-facing fields (title, dek, each part's `h2`, and the `brief`) are written in Chinese** (the artifact language) unless the user asked for English; the JSON keys and the plan's own notes stay English. (See `generator_playbook.md` for the 5-part spine + Chinese voice.)

2. **Fan out generation** (5 parallel agents, one per part). Each reads `build_plan.json` + `generator_playbook.md` + `corpus_dna.md`, writes `p{N}_sections.html`, `p{N}_labs.js`, `p{N}_refs.bib` (P5 also `p5_appendix.html`). Each agent must VERIFY its lab math (Monte-Carlo means converge to the closed-form truth) before returning. Inherit the parent model (Opus) — prose quality matters.

3. **Assemble** (`bin/build.py`). Concatenate P1..P5 sections → `content.html`, all labs → `labs.js`, dedup all bibs by key → `refs.bib`, front-matter JSON from the plan. Produces a single self-contained `.html` (distill template + KaTeX + woff2 all inlined).

4. **Headless QA** (`bin/qa.py`). Fails on any KaTeX parse error, JS error, external request, or undrawn canvas. Fix and re-run until PASS. (KaTeX is distill's v2.4.0 — `\operatorname`/`\substack` throw; see playbook.)

5. **Adversarial discrimination** (3 parallel strict agents, distinct lenses: A=framework/visual/interaction, B=pedagogy, C=prose+AI-tells). Each is anchor-gated (must classify a known-real and known-fake correctly first), evidence-forced (≥2 cited tells per score), and defaults-to-generated. See `discriminator_rubric.md`. Collect per-dim scores + per-part fix recommendations.

6. **Harmonize + polish** (1 agent — MANDATORY, do not skip). Multi-agent fan-out leaves **cross-part seams**: notation drift (loss symbol, `\varepsilon` vs `\epsilon`), duplicated cross-part restatements, mixed canvas/DPR idioms, repeated transition phrasings. Unify *notation and mechanics*, dedup repeats, apply the discriminators' per-part fixes — **without weakening prose or breaking lab math, and without flattening structure into a uniform stamp.** WARNING: do NOT impose identical Roman-numeral I–V markers or a single section-title template — uniformity across sections (and across articles) is itself a detectable fingerprint (a blind panel caught it at 100%). Harmonize *consistency of notation*, preserve *variety of structure*. Also strip any self-referential rigor-bragging the generators slipped in (see anti-fingerprint in the playbook).

7. **Re-assemble + re-QA + re-score** the weak dims to confirm improvement. Iterate per-part where a dimension still sits below the real-distill band.

## Acceptance (per discriminator_rubric.md)
- 3 strict anchor-gated agents: source-guess accuracy on distill_v2 outputs ≤ 60% (≈ chance); every per-dim score within the real-distill [min,max] band.
- Human A/B: the reader cannot reliably pick the distill_v2 article.

## Cost note
A full part-level adversarial loop is cheap (calibration ran for well under $20 of the $300 budget). Spend freely on the harmonize + re-score iterations; they are the difference between "looks right" and "passes a strict judge".
