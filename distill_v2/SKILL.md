---
name: distill_v2
description: Turn a technical topic — a concept, paper, GitHub project, or tech survey — into ONE self-contained interactive HTML explainer in CHINESE at distill.pub quality: the genuine Distill web-component framework (d-article/d-cite/d-math/d-appendix) vendored offline into a single file, KaTeX math, reader-driven labs whose numbers are really computed, and distill's intuition-first teaching rendered in natural Chinese prose. Built adversarially — fan out one generator per section, judge with 3 strict anchor-gated discriminators, harmonize until it reads as distill-grade. Use when the user runs /distill_v2, asks for a 中文 distill 质量/distill 风格 interactive explainer (讲透/详解 X 像 distill 那样), an interactive deep-dive, or a single-file offline explainer with real computed interactions. The Chinese-output successor to the `distill` skill; distinct from grok (warm-paper dual-tab cards). Spec and build process stay in English; only the produced artifact is Chinese.
---

# distill_v2

**Artifact language: Chinese (default). Spec + build process: English.** The produced HTML is a Chinese-language artifact; this spec and every intermediate step (build plan, agent prompts, discriminator reasoning) stay in English for portability — the same asymmetry as the sibling `grok` / `distill` skills. (An English artifact is available on explicit request; pass the language through the build plan.)

Produce a single-file interactive HTML explainer that carries distill.pub's framework, visual system, interaction density, and intuition-first teaching — rendered in natural, high-quality Chinese — and that leaves the reader deeply understanding the topic. The bar is distill-*grade*: a knowledgeable reader should judge it as good as a real distill article, not catch it as machine-made or as translationese.

Three reference files carry the detail (read them before building):
- [`references/corpus_dna.md`](references/corpus_dna.md) — the reverse-engineered DNA of real distill articles (spine, visual system, interactions, voice, AI-tell blacklist). The style bible.
- [`references/discriminator_rubric.md`](references/discriminator_rubric.md) — the strict, evidence-forced, anchor-gated judge (5 dimensions). The quality bar and the acceptance test.
- [`references/generator_playbook.md`](references/generator_playbook.md) — how a section agent writes a part (authoring API, the 5-part spine, voice, cross-part consistency).
- [`references/lab_authoring.md`](references/lab_authoring.md) — lab layout/perf rules (canvas sizing via the `so.*` harness, no clipping, no drag-freeze, training loops that progress). A hard QA gate.
- [`references/build_pipeline.md`](references/build_pipeline.md) — the proven adversarial assembly loop, stage by stage.

## What makes it distill-grade

Real distill articles are not a *look*, they are the **Distill web-component framework**: `<d-article>/<d-title>/<d-byline>/<d-cite>/<d-math>/<d-footnote>/<d-appendix>/<d-bibliography>`, the prerendered stylesheet, a DOI, the fixed appendix tail. distill_v2 renders through the **actual `template.v2.js`** (vendored in `vendor/`, patched so KaTeX loads offline), so the framework markup, visual system, and layout are authentic by construction — and these are **language-agnostic**, so a Chinese article inherits them unchanged. Effort then goes where a template can't help: **interaction authenticity, pedagogy, and Chinese prose voice.**

## Output

One self-contained `.html`, **Chinese-language artifact** — the distill template, KaTeX (js + css + woff2 fonts) all base64-inlined, zero external requests, works offline. Chinese applies to all reader-facing text (title, prose, section headings, figcaptions, control labels, readouts); math (LaTeX), code, and BibTeX keys stay as-is; a technical term may carry its English original in parentheses on first use. Save beside its source (or under `/Users/han/project/learn_with_agent/<YYMMDD>/<slug>.html` when there's no source). Build with `bin/build.py`; QA with `bin/qa.py`.

## The interactions must compute

Every lab computes the quantity it shows — a slider re-runs the solver, a drag re-conditions the posterior, a Monte-Carlo estimate is overlaid on a closed-form truth. No GIFs, no pre-rendered "results", no perturbed stand-ins (these are discriminator tells). When something genuinely can't run live, ship a clearly-labeled static figure. Aim ≥6 reader-driven interactions with ≥1 break-it/failure-mode demo. Canvases are DPR-safe.

## Build pipeline (always run in order — see build_pipeline.md)

1. **Build plan** (1 agent) → `build_plan.json`: title, dek, ONE running example, entity→color map, the five parts each with content brief + lab compute specs, citations.
2. **Fan out generation** (5 parallel agents, one per part P1–P5) → `p{N}_sections.html` + `p{N}_labs.js` + `p{N}_refs.bib`. Each verifies its lab math before returning. Inherit the parent (Opus) model.
3. **Assemble** (`bin/build.py`) → single self-contained `.html`.
4. **Headless QA** (`bin/qa.py`) → fails on any KaTeX error, JS error, external request, or undrawn canvas. Fix and re-run to PASS.
5. **Adversarial discrimination** (3 parallel strict agents, distinct lenses) → per-dim scores + per-part fixes. Each is anchor-gated, evidence-forced, defaults-to-generated (per the rubric — this defeats lenient judging).
6. **Harmonize + polish** (1 agent — MANDATORY): fan-out leaves cross-part seams (inconsistent section markers, notation drift, mixed canvas idioms, duplicated restatements) that a strict prose judge catches. Unify them and apply the discriminators' fixes.
7. **Re-assemble + re-QA + re-score** the weak dimensions; iterate per-part until every dimension sits within the real-distill band.

## The 5-part spine (the adversarial unit is one part)

P1 cold open + roadmap · P2 problem framing + intuition (state the naive view, subvert it) · P3 mechanism derived + headline lab · P4 worked example + secondary labs + break-it + honest caveats · P5 context / why-not-X + honest open-problem close + appendix. One running example threaded through all five.

## Acceptance (distill-grade, in Chinese)

The artifact is Chinese, so a literal "can't tell it from English distill.pub" test does not apply. Split the bar by what is language-agnostic vs language-bound:

- **Stage 1 — machine.** 3 strict anchor-gated discriminators score against the real distill corpus. **D1 framework / D2 visual / D3 interaction / D4 pedagogy are language-agnostic** — each must land within the real-distill [min,max] band. **D5 is judged as Chinese prose** (see discriminator_rubric.md): natural high-quality Chinese technical writing in distill's spirit — intuition-first, hedge-honest, derive-not-assert — with **no translationese and no AI-tells**, anchored against strong Chinese technical writing rather than English distill.
- **Stage 2 — human:** the reader judges the article as good as a real distill piece (not machine-made, not translated), and after reading deeply understands the topic.

## KaTeX constraint

The vendored KaTeX is distill's v2.4.0 — `\operatorname`, `\substack`, `\boldsymbol`, `\xrightarrow` throw parse errors. Use `\mathrm{}`/`\text{}` for operators. `bin/qa.py` catches any parse error.

## Scope

v1 is calibrated for **technical concepts** (where distill's corpus lives). Paper / GitHub-project / tech-survey inputs reuse the same pipeline (build plan → 5 parts → adversarial loop) with an input-specific build-plan brief; the framework, assembler, QA, and discriminator are input-agnostic.

## Borrowed from the `distill` skill

The assemble-don't-hand-write build idea and the interaction-as-insight / derive-don't-assert principles are taken from the sibling `distill` skill; distill_v2 diverges by reproducing the real distill.pub framework offline and adding the adversarial discriminate→harmonize loop calibrated against a real corpus.
