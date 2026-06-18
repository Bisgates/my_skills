---
name: spell-out
description: Turn a technical concept / paper / project into ONE runnable LearnHub notebook page teaching its single core point by re-creating it from scratch at toy scale on the LOCAL Mac (MPS) — Karpathy spell-out + Feynman "what I cannot create, I do not understand". A real notebook: editable Python cells run live against a local Jupyter kernel, plus genuinely-computed distill-style client labs and KaTeX term-by-term equation cards, in Chinese. Pipeline: distill to ≤3 core points → design toy data + minimal experiment → a critic agent challenges the design before any code → build + verify. Research/spec English; artifact Chinese. Use when the user runs /spell-out <topic>, asks to "讲透 / spell out / 从零跑通 X" as a runnable notebook in learn_with_agent, or wants a laptop-runnable from-scratch explainer with live cells. Distinct from grok and distill_v2 (static/offline single-file HTML) — spell-out's soul is a REAL running kernel, blackboard+chalk.
dependencies: []
---

# spell-out

Artifact language: **Chinese**. Spec, research, agent prompts, code comments-for-self: **English**. Same asymmetry as `grok` / `distill_v2`.

spell-out is grok's **frog** view taken to its conclusion: the bottom-up worked example is not a static figure — it is a **real experiment that runs on a local kernel**, plus distill-style client-side labs. One page = one notebook = one core point, re-created from scratch and executed on the reader's own laptop.

## Philosophy — blackboard + chalk

1. **Run on the laptop, from scratch.** Every experiment must train + sample on the local Mac (MPS/CPU) in interactive time (seconds, not minutes). This is not a compromise — the laptop constraint is the **forcing function** that distills a concept to its irreducible core (MIT teaches with blackboard + chalk for the same reason). When something is too slow, the answer is **always "shrink the experiment further"** — drop dimensions, samples, steps, network width — **never "use a bigger GPU."** Do not reach for gpu7.
2. **Feynman gate.** "What I cannot create, I do not understand." Success = after the page the reader can, on a blank sheet, write the governing equations and run the loop in their head. Every page ends with a 白纸复述 (blank-sheet recap) + self-test.
3. **One core point.** Distill to **1** core point (≤3 max), then **2–3 secondary lifts**. If you can't name the single thing the page proves, you haven't understood it yet. Cut ruthlessly — the critic gate exists to enforce this.
4. **Re-create the mechanism, not the model.** Never run the full pretrained model (SD, real ControlNet weights). Rebuild the *core mechanism* at toy scale (a 4-layer MLP on 2D data) so it fits the laptop and the reader's head.

## Where it runs — LearnHub (local Mac)

The artifact is a page served by **LearnHub** at `~/project/learn_with_agent/_hub` (FastAPI :8900 → local Jupyter :8888). The hub injects a self-contained kernel client into every page (CodeMirror editor + direct Jupyter-WS exec + inline png/text/html rendering + jupyter-style keys) — **not Thebe**. You only author the page body; the runtime is injected at serve time.

```bash
bash ~/project/learn_with_agent/_hub/start-mac.sh    # local python, MPS kernel, no tunnel
open http://localhost:8900/                          # hub index (auto-discovers pages/)
open http://localhost:8900/page/<name>               # your page
```

Two Mac gotchas, both already handled by `start-mac.sh` / `server.py` (documented in `_hub/README.md`):
- **clashon proxy → 502.** A global proxy routes loopback through clash. `start-mac.sh` exports `no_proxy=127.0.0.1,localhost,::1`. Prefix any hand-run smoke/verify the same way.
- **websockets version skew.** `server.py` picks `extra_headers` (v12) vs `additional_headers` (v14+) by signature.

Env: the Mac `base` conda already has torch(MPS) / diffusers / numpy / sklearn / matplotlib / jupyter_server / ipykernel — do not assume a fresh env is needed; probe first.

## Pipeline (the spell-out loop)

1. **Distill (English research).** Read the source. Name the **ONE** core point + 2–3 secondary lifts. Pick the toy that makes the math cleanest (prefer a distribution with closed-form structure — e.g. a Gaussian mixture over two-moons — so analytic checks are possible).
2. **Design doc** → `doc/<topic>_design.md`: core point, the minimal equation set, toy data, kernel-cell list, distill-lab list, color code, and an explicit "open questions for the critic".
3. **Critic gate (mandatory, before any page code).** Dispatch one adversarial critic sub-agent (see `references/critic_prompt.md`). It challenges the spine, the equation set (minimal AND complete?), the toy, lab honesty, and scope. Save its verdict to `doc/<topic>_critic.md`. Adopt or consciously reject each edit; record decisions. **Do not write page code until the design has passed the critic.**
4. **Smoke first.** Write `scripts/smoke_<topic>.py` and run the real experiment on MPS. Confirm it trains + samples in interactive time and the result is correct (eyeball + any analytic cross-check). This validates the exact code the kernel cells will use. If slow → shrink, never escalate hardware.
5. **Build the page** → `_hub/pages/<name>.html` (see `references/page_authoring.md`). Kernel cells reuse the smoke-validated code, split into a clean cell sequence; client JS labs compute the same math live.
6. **Verify (QA gate).** Run `python _hub/verify_page.py <name>` (with the proxy bypass). It runs every `<pre data-executable>` cell in order on the local kernel and asserts 0 errors + expected image output. Open the page, drag every lab slider, click every Run. Fix until green.
7. **Open + hand off.** `open http://localhost:8900/page/<name>`.

## Output convention

- Page: `~/project/learn_with_agent/_hub/pages/<name>.html` — single file, auto-discovered by the hub. One page per topic.
- Skill source: this repo, `spell-out/`.
- Working artifacts during a build (when run inside an arc): design + critic records in `doc/`, smokes in `scripts/`, smoke images via `arc output`.

## Page authoring — the rules that earn the look

Full spec in [`references/page_authoring.md`](references/page_authoring.md). The load-bearing ones:

- **Warm-paper visual**, reusing the LearnHub palette (`--paper / --ink / --accent #8c2f1c / --accent-2 #2c5340 / --gold #a37c2a`). **No skeuomorphic "blackboard"** — equations live on warm paper like everything else.
- **Equation cards (`.eq-card`) — the signature move.** Every formula is **decomposed term-by-term**: show the full equation, color each term, then list each term with a one-line intuition, and tie it to a lab. Color convention: signal/clean = green, noise/ε = red, schedule = gold, network = blue `#3a5a8c`. (User-validated: "非常棒".)
- **All math is KaTeX** — equations, **and** lab readouts, control labels, color legends, section titles, lab headers. **No plain-text math symbols** anywhere the reader sees (no literal `√ᾱ_t`, `ε_θ`). KaTeX CDN pinned (`katex@0.16.11`), auto-render on `DOMContentLoaded` with `ignoredTags:[...,"pre","code"]`, never `onload`.
- **Page default `html{zoom:1.18}`.**
- **Kernel cells:** `<pre data-executable="true" data-language="python">`. Reuse smoke-validated code. Must pass `verify_page.py`.
- **distill-style client labs: ≥3 per page**, genuinely computed (real closed-form / real solver, no GIFs, no fakes). DPR-safe canvas, IIFE per lab, no main-thread freeze on drag. Avoid the injected runtime's globals (`lh-*` classes, `NB`, `ws`, `window._lh*`). See distill_v2's `references/lab_authoring.md` for the canvas/perf discipline.
- **Function-explorer lab for every complex formula** (à la distill's Interactive GNN): the reader **drags the equation's variables** (a 2D point, a parameter) and the output/field responds live, making the formula touchable — e.g. drag $x_t$ and $t$ to watch the $\varepsilon$ / score arrows and $\hat x_0$ move. (User-requested standing rule.)
- **Prose: write like a cs231n course note** (the model: <https://cs231n.github.io/>, e.g. `optimization-1`). The reader must *understand*, not just receive a row of true statements — the reported failure "讲解我看不懂" came from telegraphic, jargon-stacked density. Reproduce the cs231n reading experience: **motivation-first** (recap where we are → name this piece's role → foreshadow, then introduce it); a conversational-but-authoritative **"我们"** voice that openly flags the subtle/odd points; **intuition before the math**, built from concrete numerical or code worked examples and — where it genuinely helps — a **pedagogical analogy** that grounds an abstract object in familiar intuition (cs231n's hiker-on-a-hill for the loss landscape; analogies are allowed and encouraged here — a deliberate exception to the user's global 叙事规范, set for teaching — as long as each ties back to the mechanism); **explicit signposting** (bold a 「核心思想：…」 before elaborating, name the principle, give short bullet recaps mid-section and at the end); **preempt the reader's likely confusion** (state the objection, then resolve it); show the connective reasoning (问题在于…/因此…/注意…/关键在于…) so each step follows from the last; varied sentence rhythm, paragraphs ≤5–6 sentences. Still banned: contentless filler — 元话语, 套话, slogans, "本页将讲…/在你的笔记本上跑通…". Density = information per sentence, not compression; a sentence may run as long as the reasoning needs. Reader is an expert — pitch accordingly. Full treatment in `references/page_authoring.md` § Prose. (User's standing rule.)
- **Explanation depth — teach, don't label** (load-bearing; thin one-liners fail — "讲解性内容太单薄" is an explicit failure). Every page carries, as real content (≳3× a terse baseline): a **core background** (begin-with-why: predicament → naive approaches & why they fail → what this method does differently → why it works, with lineage); a **derivation/intuition paragraph per equation** (where it comes from, why defined this way); a **phenomenon-reading paragraph per lab**; and a **"scale up to the real model" coda** (what changes vs what's identical). Depth comes from mechanism, derivation, and concrete worked examples, taught in the cs231n voice (§ Prose); dense because of information, never padded. Two failure poles: "讲解性内容太单薄" (too thin) and "讲解我看不懂" (dense-but-unreadable) — aim between them, rich and legible. This explains the *subject* (not the *page* — distinct from the banned meta-prose). See `references/page_authoring.md` § Explanation depth.
- **Close with 白纸复述** — the equations to reproduce + 2–3 self-test `<details>` questions (the Feynman gate).

## Critic gate

The mandatory adversarial design review before code. Template + dispatch contract in [`references/critic_prompt.md`](references/critic_prompt.md). It is a real gate: in both dogfood builds it changed the toy (→ closed-form GMM), added a missing equation (ε↔score bridge), killed a CFG-masquerading lab, and forced "trainable copy" to be a literal weight copy. Run it once per topic; save the record; act on it.

## Smoke first

Before any page code, the toy experiment must run green on MPS. `scripts/smoke_<topic>.py` is the proof and the source of the kernel-cell code. Validate correctness with an analytic cross-check when the toy allows (e.g. a GMM's true score is closed-form → overlay learned vs analytic). Record wall-time; if it isn't interactive, shrink.

## Hard constraints

- Local Mac only; never gpu7. Toy scale only; never full pretrained weights.
- Every kernel cell passes `verify_page.py` (0 errors). Every lab actually computes and doesn't freeze.
- All reader-facing math is KaTeX. Equations are decomposed in `.eq-card`s. No blackboard skeuomorph.
- Chinese artifact, English spec/research. No meta-prose.
- Critic gate before code; smoke before page; verify before open.

## See also

- [`references/page_authoring.md`](references/page_authoring.md) — the full page recipe (CSS tokens, eq-card, KaTeX, labs, cells, recap).
- [`references/critic_prompt.md`](references/critic_prompt.md) — adversarial critic template + dispatch.
- [`templates/page-skeleton.html`](templates/page-skeleton.html) — minimal warm-paper page (masthead, eq-card, lab, cell, recap, KaTeX, harness) to copy from.
- `~/project/learn_with_agent/_hub/{README.md, server.py, start-mac.sh, verify_page.py}` — the LearnHub runtime + QA gate.
- Reference builds: `_hub/pages/diffusion.html`, `_hub/pages/controlnet.html` (the two dogfood demos).
- `grok/SKILL.md` (frog pedagogy + warm-paper visual), `distill_v2/references/lab_authoring.md` (canvas/perf discipline).
