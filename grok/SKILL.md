---
name: grok
description: Convert a target folder — paper PDF, book chapter, concept note, codebase entry-point — into a single-file interactive learning HTML. Default = two-tab HTML, bird (top-down, Hamming) + frog (bottom-up, Karpathy + Ng). Both tabs render under the new "simple" visual default — macOS system fonts, warm-paper palette, zero external CDN. Magazine longread (Google Fonts + KaTeX) opt-in via `--visual magazine`; Jupyter notebook via `--visual notebook`. Same scope on both tabs, shared slugs so deep links resolve across tabs; ship one tab if the source has nothing for the other lens. Opens with "begin with why", walks each new concept through a concrete worked example, 80% of the page to core insights. HTML is Chinese; the skill spec stays English. Use when the user runs `/grok <folder>`, asks to "学习/讲解/拆解/搞懂 X 文件夹里的 paper/书/概念/代码" inside `learn_with_agent`, or asks for a bird / frog / Hamming / Karpathy / Ng / SICP / notebook / magazine / simple explainer.
---

# grok

> **Languages.** This skill spec is written in English. The artifact it produces — the interactive HTML — has Chinese natural-language content (chapter titles, prose, callouts, captions). Treat this asymmetry as load-bearing: instructions, comments, and reasoning happen in English; everything the human reader sees in the rendered page is in Chinese.

> **Why "bird" and "frog".** Naming follows Freeman Dyson's *Birds and Frogs* essay (Notices of the AMS, 2009). A bird flies high and surveys broad vistas; a frog sits in the mud and sees flowers up close. Neither is superior — Dyson's whole point is that healthy work needs both. The two tabs of the dual-tab default are exactly these two altitudes on the same source. Earlier names (MIT / Stanford) were factually messy (Feynman ≠ MIT; Strang's MIT 18.06 is bottom-up) and carried a prestige connotation the packs don't actually have. `bird` and `frog` are precise about *altitude*, neutral about *institution*.

## Quick start

```
/grok "260506_Coding Agents_alphazero"                                 # default: dual-tab, both tabs under 'simple' visual
/grok "260506_Coding Agents_alphazero" --style bird                    # bird only, still 'simple' visual
/grok "260506_Coding Agents_alphazero" --style frog                    # frog only, still 'simple' visual
/grok "260506_Coding Agents_alphazero" --visual magazine               # dual-tab, but bird tab uses classic magazine + KaTeX
/grok "260506_Coding Agents_alphazero" --visual magazine,notebook      # restore the pre-2026-05 default (bird=magazine, frog=notebook)
/grok "260506_Coding Agents_alphazero" --style bird --visual magazine  # bird-only, magazine visual (paper learning with formulas)
/grok "260506_Coding Agents_alphazero" --style frog --visual notebook  # frog-only, Jupyter notebook visual
/grok "260506_Coding Agents_alphazero" --math                          # any visual + KaTeX added back (when source has LaTeX)
/grok "260506_Coding Agents_alphazero" --align                         # alignment checkpoint first
```

Natural-language equivalents: "用 bird 风格 / Hamming 风格 / 自顶向下 / 抽象先行" all select bird pedagogy; "用 frog 风格 / Karpathy 风格 / Andrew Ng 风格 / spelled out from scratch / 自底向上 / 例子先行" all select frog pedagogy; "杂志风 / magazine 风格 / longread" requests the magazine visual; "notebook 形式 / jupyter 风格" requests the notebook visual; "调研报告 / 简洁版 / 不要 google fonts" or saying nothing about visual keeps the simple default.

**Legacy aliases (kept silently for backward compatibility):** `--style mit` / `--style feynman` resolve to `bird`; `--style stanford` / `--style karpathy` resolve to `frog`. All Chinese phrases like "MIT 风格 / SICP 风格 / 费曼风格 / Stanford 风格" still trigger the right pack. See **Style selection** below.

Output:
- **Default** (no folder argument, or source path lives outside `learn_with_agent/`): `/Users/han/project/learn_with_agent/<YYMMDD>/<source-name>.html` — today's date folder under `learn_with_agent`, in `YYMMDD` form. Created on demand with `mkdir -p`.
- **Override** (folder argument given, e.g. `/grok "260506_Coding Agents_alphazero"`): `<folder>/<source-name>.html` — lives next to the source.

Filename always = source stem with extension swapped to `.html`. Single file, all dependencies via CDN.

## Dual-tab default — why the default is two halves

The default `/grok <folder>` is **one HTML with two tabs**, not a single-style page. This is load-bearing: the reader gets bird and frog as two complete lenses on the same source and picks whichever entry point fits their current cognitive state, switching mid-read when stuck. The pattern echoes how a careful learner already works — book in one hand (bird: Hamming, top-down, "what's the question behind the question, and what does the method look like once we strip everything away?"), notebook on the desk (frog: Karpathy + Ng, bottom-up, "let's compute the smallest case by hand and watch the abstraction emerge").

**Three principles govern the dual-tab assembly. They are not negotiable defaults that fade after Quick start; they're the contract.**

1. **Same scope, different lens.** Both tabs cover the **entire source**. Reading either tab alone must be a complete artifact — never split coverage between tabs ("tab A covers framework, tab B covers implementation" is forbidden, that's a single-tab book with two chapters). The other tab is "switch when stuck," not "read next."
2. **Matching slugs across tabs (planning aid + deep-link plumbing, not body UI).** Each top-level concept gets parallel anchors on both sides — convention is `id="bird-<slug>"` on the bird side and `id="frog-<slug>"` on the frog side, with the `<slug>` shared. This serves two purposes: (a) during alignment, the shared slug forces the bird and frog drafts to actually cover the same scope (if you can't agree on a slug, the two halves have drifted); (b) at runtime, the hash-routing JS picks up `#frog-densify` shared in chat and switches tabs + scrolls automatically. **Do NOT add per-section "↔ 另一视角" jump buttons to the body** — they clutter every heading for a use case the global tab bar already handles. The tab bar at the top is the only cross-tab affordance; readers switch when they're stuck on the *current* tab, not when they want to footnote-hop.
3. **Don't force-fill — ship one tab if the other lens has nothing.** Most ML/CV papers have both clean abstract structure (good for bird) and concrete worked examples (good for frog), and the dual-tab pays off. But a pure complexity result, a pure mathematical existence theorem, or a code-only refactor may have no real bird story (no question worth lifting above the method) or no real frog story (no numerical example to compute). When one tab would be force-filled, **drop it**: emit a single-style HTML with no tab bar and note in the editor-note / `.nb-foot` that the other lens didn't apply (one sentence, e.g. "frog 视角因没有可手算的例子被略去"). Forcing a half-empty tab is worse than honest absence.

The tab assembly itself is implemented by one of two outer shells. **Default (no `--visual` flag)**: [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) — warm-paper palette, macOS system fonts, zero external assets, sticky tab bar with accent-underline active state. **Pre-2026-05 default (opt-in via `--visual magazine,notebook`)**: [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) — Google-Fonts-rich, KaTeX + Prism shared deps, magazine bird + notebook frog. Both shells provide the tab bar, hash routing, namespaced CSS scopes, and legacy `mit-` / `stanford-` anchor remapping. The bird and frog bodies inside each tab are built from their respective skeletons under `templates/` (the `simple-*` skeletons for the new default; the legacy `bird-skeleton.html` / `frog-skeleton.html` for the pre-2026-05 default). See **Workflow step 5**.

## Trigger discipline

Enter this skill **only** on explicit user invocation: `/grok <folder>`, or natural-language "学习 / 讲解 / 拆解 / 搞懂 X 文件夹里的 paper / 书 / 概念 / 代码", or an explicit style request ("用 bird / frog / Hamming / Karpathy 风格…", "自顶向下讲一下…", "spelled out from scratch…"). Seeing a PDF, Markdown note, e-book, or unfamiliar source folder in the workspace is **not** a trigger — don't proactively start writing.

## Style selection

A grok artifact has **two orthogonal axes**: a **pedagogical posture** (how the page reasons — bird vs. frog) and a **visual layer** (how the page looks — simple vs. magazine vs. notebook). Pedagogy is the primary identity; visual is the rendering. `--style` picks the pedagogy; `--visual` picks the rendering. Either can be omitted, in which case the defaults below apply.

### Pedagogy packs

| Style | Pedagogical posture | Lineage / exemplars | Spec |
|---|---|---|---|
| **bird** 🐦 | Top-down, abstraction-first, derived from first principles; lift the meta-question, strip the details, derive the method from the goal, close with the principle to remember | Richard Hamming, *The Art of Doing Science and Engineering* | [`references/styles/bird.md`](references/styles/bird.md) |
| **frog** 🐸 | Bottom-up, worked-example first; build / compute / observe, abstraction emerges | Karpathy "zero to hero" + Andrew Ng CS229 | [`references/styles/frog.md`](references/styles/frog.md) |

**Pedagogy default.** No `--style` flag → **dual-tab** (both packs). See § Dual-tab default for the contract.

### Visual layers

| Visual | Look | Required components per pedagogy | Spec | Skeleton |
|---|---|---|---|---|
| **simple** (new default) | macOS system font stack + warm-paper palette + zero external CDN | bird-flavored: Roman-numeral chapter openers, drop-cap lede, callout / pull / matrix. frog-flavored: cell.md / cell.code / cell.out, mono section headings, stop-and-think | [`references/styles/visual-simple.md`](references/styles/visual-simple.md) | [`templates/simple-bird-skeleton.html`](templates/simple-bird-skeleton.html) · [`templates/simple-frog-skeleton.html`](templates/simple-frog-skeleton.html) · [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) |
| **magazine** (opt-in) | Sunday-magazine longread on warm paper — Playfair Display + Cormorant Garamond via Google Fonts, KaTeX, Prism, drop caps, ornament glyph rows, pull quotes, ink-bordered afterword, three-column colophon | bird only (see bird.md component checklist) | section in [`references/styles/bird.md`](references/styles/bird.md) | [`templates/bird-skeleton.html`](templates/bird-skeleton.html) |
| **notebook** (opt-in) | Jupyter notebook on off-white — Inter + JetBrains Mono via Google Fonts, KaTeX, Prism light theme, In/Out cell pairs, chalk block, mono caps section numbers `§N` | frog only (see frog.md component checklist) | section in [`references/styles/frog.md`](references/styles/frog.md) | [`templates/frog-skeleton.html`](templates/frog-skeleton.html) |

**Visual default.** No `--visual` flag → **simple** for both halves. The pre-2026-05 default (bird=magazine, frog=notebook) is preserved as `--visual magazine,notebook`.

### Picking a visual

- **simple** (default) for investigative reports, codebase walkthroughs, technical explainers, anything that has to read fine offline. Single file, double-click open, no network. The warm-paper / accent-red / accent-green tokens are the visual identity.
- **magazine** when the source is a paper with formulas worth rendering as actual math (KaTeX), the audience expects a Sunday-magazine longread feel, and the typographic richness is part of the artifact's value. Implies `--math` (KaTeX is loaded).
- **notebook** when the source is code-heavy and the page's spine is `In [N]:` / `Out[N]:` cells in the Karpathy spelled-out-from-scratch register. Implies `--math` (KaTeX is loaded).
- **`--math` flag** can be combined with `--visual simple` to load KaTeX for one specific page without giving up the rest of the simple visual's identity. Use it when the source has more than ~2 formulas worth typesetting.

**Trigger phrases that select bird pedagogy** (`--style bird`):
- Explicit: `--style bird` · "bird 风格" · "鸟瞰视角"
- Lineage: "Hamming 风格" · "*Art of Doing Science and Engineering*" style
- Direction: "自顶向下" / "top-down" / "抽象先行" / "interface-first"
- Method-from-goal: "第一性原理讲解" / "first-principles walkthrough" / "meta-question first"
- **Legacy aliases (silently honored):** `--style mit` · `--style feynman` · "MIT 风格" · "SICP 风格" · "费曼风格" · "Strang 风格"

**Trigger phrases that select frog pedagogy** (`--style frog`):
- Explicit: `--style frog` · "frog 风格" · "青蛙视角"
- Lineage: "Karpathy 风格" · "Karpathy zero to hero" · "Andrew Ng 风格 / Ng 风格" · "CS229 风格"
- Direction: "自底向上" / "bottom-up" / "例子先行" / "example-first" / "worked-example-driven"
- Code-first: "spelled out from scratch" / "代码为核心" / "代码主导讲解" / "code-first walkthrough"

**Trigger phrases that select a visual** (`--visual …`):
- `--visual simple` · "简洁版" / "调研报告 风格" / "不要 google fonts" / "纯系统字体" / "零外部依赖"
- `--visual magazine` · "杂志风" / "magazine 风格" / "longread" / "纸质感杂志排版" / "Playfair 字体"
- `--visual notebook` · "notebook 风格" / "jupyter 风格" / "notebook 形式" / "In/Out 单元格"
- `--math` · "渲染公式" / "有公式要 KaTeX" / "math identity matters" — keeps the current visual but loads KaTeX

### Resolving the visual

When the user names a pedagogy without naming a visual, **the visual defaults to simple** for both bird and frog. When the user names a visual without naming a pedagogy, the pedagogy defaults to dual-tab (and the visual applies to both halves — magazine-rendered frog still keeps the frog *voice*, just on warm paper with Cormorant body; this is rare but allowed). When the user names both, both stick.

**Single-style + visual mixes** that come up in practice:
- `bird + simple` (no flags from a single-style request) — the new default for bird-only output.
- `bird + magazine` (`--style bird --visual magazine`) — the **pre-2026-05 default** for bird-only, kept for paper-learning with formulas.
- `frog + simple` — the new default for frog-only output.
- `frog + notebook` (`--style frog --visual notebook`) — the **pre-2026-05 default** for frog-only, kept for code-heavy Karpathy walkthroughs.
- `bird + notebook` or `frog + magazine` — pedagogically rare but allowed; the voice stays under the named pedagogy, the visual switches.

**Dual-tab + visual mixes:**
- Default (no flags) = both tabs under simple. The tab bar's accent-underline + the warm-paper palette unify the two tabs visually; the cell-vs-magazine-marker delta still differentiates them.
- `--visual magazine,notebook` restores the pre-2026-05 default — bird tab in magazine, frog tab in notebook. Useful when both halves want their classic identity (paper learning + code walkthrough).
- `--visual magazine` (single value) applies magazine to whichever tab is bird-pedagogy and leaves the frog tab on simple — and vice versa for `--visual notebook`. Mixed-pair output.
- A visual that doesn't match a pedagogy (e.g. `--visual notebook` applied to the bird tab when also `--style bird`) falls back: simple takes its place. Don't force a notebook-rendered bird.

When the user asks for a single pedagogy but is ambiguous which one, ask once — *bird (top-down) or frog (bottom-up)?* — before generating. Don't silently default to dual-tab if the user clearly wanted a single style.

### Adding a new pedagogy or a new visual

**New pedagogy** (rare — bird and frog cover most of the altitude space):
1. Add `references/styles/<NewStyle>.md` with pedagogical posture, lineage, voice deltas, required components per visual, CSS class quick reference, style-specific self-audit, gotchas.
2. Add `templates/<NewStyle>-skeleton.html` (default visual = simple) plus optional `templates/<visual>-<NewStyle>-skeleton.html` variants if the pedagogy needs a non-simple look as well.
3. Register the pedagogy in the **Pedagogy packs** table and its trigger phrases. Decide whether it joins the dual-tab rotation (rare — defaults expand slowly).

**New visual** (also rare — three should cover most needs):
1. Add `references/styles/visual-<X>.md` describing the palette, font policy, required components per pedagogy, self-audit. The visual must work for both bird and frog (or explicitly opt out of one half — say so in the spec).
2. Add `templates/<X>-bird-skeleton.html` and `templates/<X>-frog-skeleton.html` and a `templates/<X>-dual-tab-skeleton.html`. Re-use one of the existing visuals as a starting pattern; do not invent palette + components from scratch.
3. Register the visual in the **Visual layers** table and its `--visual <X>` trigger phrase. Decide whether it should become the new default (very rare — defaults move when the prior default has a structural problem, not because the new one is nicer).

Keep packs **mutually distinguishable**. If a "new style" is "magazine but with two columns," don't make it a new style or a new visual — propose an extension to the existing one. Packs earn their place by being meaningfully different.

## Parallel sub-agents (default on for fan-out work)

Paper-grokking is naturally chunked: independent chapter / section drafts, separate worked-example research, several lab-visualization sketches, multiple external-source lookups. Fan those units out into sub-agents — one Agent tool call per unit, fired in a single message so they run concurrently. Cuts wall-clock time roughly proportional to the number of independent units; the reader still receives one HTML.

**Top-level fan-out for the dual-tab default.** The bird half and the frog half are independent learning artifacts that happen to share scope. Treat them as **two parallel agent groups**: one group drafts the bird magazine body, one group drafts the frog notebook body. Both groups can run concurrently after the alignment outline is locked. Inside each group, sections / labs / external supplements fan out as the next concurrent layer. The parent assembles all returned bodies into the dual-tab shell after both groups complete. Single-style mode is one group instead of two.

**Concrete fan-out units in this skill:**

- **Top level (dual-tab only):** bird-half agent group + frog-half agent group. Each receives the shared alignment outline + the cross-anchor slug map (so anchors line up between halves).
- Prior-work research for chapter 0 / cold open — one agent per family (VAE / GAN / Flow / …). Run once at the top level; both halves consume the same research output.
- Section drafting after the outline is locked — one agent per section per half, each with its spec + the writing principles + the relevant source excerpts + **the style pack's voice and component contract** + **the assigned cross-anchor slug**.
- External supplements (`aside.external` in magazine, `aside.external` or external-callout in notebook) — one agent per topic per half (or shared across halves when the supplement is identical, e.g. an author bio).
- Lab visualizations — one agent per lab to write the IIFE + DPR-scaled canvas code. Labs typically appear in only one half (notebooks lean lab-heavy; magazine labs are more selective), so most lab agents fan out under one group.
- Worked examples across distinct concepts — one agent per concept per half. The bird worked example is "the principle, instantiated on the smallest case that exercises it"; the frog worked example is "compute it by hand and read off the answer."

**Don't parallelize the linear spine.** Anything with a sequential dependency stays serial: chapter 0 / cold open must be drafted before later sections can reference its predicament; the `--align` outline must be confirmed before drafts begin; the cross-anchor slug map must be agreed between bird and frog halves before their section agents fan out; the master HTML stitch-together happens once on the parent after both groups return.

**Pass the style choice — and the tab assignment — to every child.** When you delegate a section, the prompt to the child must include: the style pack name (bird / frog), a pointer to the corresponding `references/styles/<X>.md`, the visual layer to use, and (in dual-tab mode) which tab this section belongs to so the child writes the correct `id="bird-<slug>"` or `id="frog-<slug>"` anchor. A child that doesn't know its tab will write in a generic register that breaks the cross-anchor map.

**Match the parent's model and reasoning depth.** A child on a smaller model writes shallower prose and breaks the voice — same reader (CS PhD, 8 years vision/DL — see `AGENTS.md`), same bar. Pass the parent's `model` explicitly to the Agent tool (Opus stays Opus, Sonnet stays Sonnet); never omit and let the runtime auto-pick a cheaper one. If the parent is in extended-thinking mode, the child should be too. Mismatch is a regression, not an optimization.

## Workflow

1. **Locate the input and resolve the output directory.**
   - **Input.** Resolve `<folder>` (relative to project root or absolute path) when one is given. The user names the source — in the invocation, in chat, or via an obviously-named file inside `<folder>`. Read that source. Don't auto-detect: don't glob for `*.pdf` and silently pick one, don't assume a particular file extension. You may also read other files inside the same source folder (pre-extracted notes under `_drafts/`, related figures, supplementary code, sibling source files) when they help you understand. The user-named source is primary; everything else is supplementary. **Do not read other topic folders.** Strict isolation.
   - **Scan for embeddable imagery while you read.** Note any source figures that pass the writing-principle "the figure carries information the diagram + worked-example can't easily replace" trigger. Extract them in step 5 with `pdfimages` / `pdftoppm` and inline as base64; don't leave the decision until the HTML is mostly written.
   - **Output directory** (referred to below as `<output-dir>`):
     - **Explicit folder argument** (e.g. `/grok "260506_Coding Agents_alphazero"` or `/grok ~/project/learn_with_agent/260507_OmniRe`) → `<output-dir>` = that folder. HTML lives next to the source.
     - **No folder argument**, or a bare source path that lives outside `learn_with_agent/` → `<output-dir>` = `/Users/han/project/learn_with_agent/<YYMMDD>/`, where `<YYMMDD>` is today's date (`date +%y%m%d`). Run `mkdir -p` on it; it may not exist yet.

2. **Resolve the pedagogy, the visual, and the mode.** Pick the pedagogy pack(s) and the visual as described in **Style selection** above.

   **Pedagogy:**
   - **Dual-tab (default, no `--style` flag):** load **both** `references/styles/bird.md` and `references/styles/frog.md` into context. Plan for two parallel agent groups in step 5.
   - **Single bird** (`--style bird` or any bird trigger phrase, or any legacy alias like `--style mit` / `--style feynman`): load only `references/styles/bird.md`.
   - **Single frog** (`--style frog` or any frog trigger phrase, or any legacy alias like `--style stanford` / `--style karpathy`): load only `references/styles/frog.md`.

   **Visual:**
   - **simple** (default, no `--visual` flag): load `references/styles/visual-simple.md`. This is the new default for both bird and frog.
   - **magazine** (`--visual magazine`): load the visual contract section of `references/styles/bird.md`. Implies KaTeX is loaded.
   - **notebook** (`--visual notebook`): load the visual contract section of `references/styles/frog.md`. Implies KaTeX is loaded.
   - **`--math`** flag combined with `--visual simple`: load `references/styles/visual-simple.md` AND plan to add the KaTeX CDN block back at document level.
   - **mixed dual-tab** (`--visual magazine,notebook` or other comma-separated pairs): each tab uses its named visual; load both relevant spec files.

   Each pack owns the voice (pedagogy) or the look (visual) — do not paraphrase from memory.

3. **Branch on mode.**
   - Default (no `--align`): jump to step 5.
   - With `--align`: run the alignment checkpoint in step 4 first.

4. **Alignment checkpoint (only with `--align`).**
   Output the following in chat **and** write to `<output-dir>/_drafts/outline.md`. The natural-language content of these items is **in Chinese** because they preview the HTML's content:
   1. **Begin-with-why paragraph.** What was the whole field stuck on before this source? What's the obvious approach? Why doesn't it work? (Shared across both tabs in dual-tab mode — the predicament is the same; only the *voice* differs in the two halves.)
   2. **One-paragraph thesis.** The source's key insight, and what fundamentally separates it from prior solutions.
   3. **Mode + style plan.** Whether the output is dual-tab, single bird, or single frog. In dual-tab mode, one or two sentences per half explaining how each voice will land (e.g. bird: "open with the meta-question — what does score-based generation actually try to solve once we strip away the network choices? — then derive the score-function interface as the unique answer"; frog: "open with the actual training command + Out cell, then unfold the 8 actions of the train loop").
   4. **Cross-anchor slug map (dual-tab only).** A table of `<slug> · bird section title · frog section title`. The slug is the shared id across both tabs (the bird side becomes `id="bird-<slug>"`, the frog side `id="frog-<slug>"`). Most sections should have a matching slug on both sides; if a section exists only on one side, mark it explicitly (e.g. `frog-only` for a pure lab walkthrough that has no bird counterpart).
   5. **Tab-pruning decision (dual-tab only).** Audit each tab: is one of the two halves going to be force-filled? If yes, drop it now — switch to single-style mode and note the omitted lens. This is the place to act on **Dual-tab principle 3 (don't force-fill)**, before any drafting starts.
   6. **Section / chapter outline.** Per section per active tab: title (with one `<strong>` emphasis word in magazine, or a mono-cap section number in notebook), one-line italic-feel hook, percent of page budget.
   7. **80% allocation.** Name the 1–3 core concepts that consume 80% of the page. Justify why everything else collapses to 20% (cite reader background — see `AGENTS.md`).
   8. **Color-code plan.** Enumerate the recurring key variables / objects in the source. Assign a fixed color to each (red / blue / green / purple / orange). Reuse it in every formula, SVG, code highlight, and inline `<span>` — **including across both tabs** so a reader switching tabs keys the variables without relearning.
   9. **Per-topic accent (magazine only, optional).** If the source has 2–3 parallel core concepts, assign each section an accent stripe color.
   10. **Worked-example plan.** For each new concept introduced, name the smallest concrete instance you'll walk the reader through. See § Writing principle 3. In dual-tab mode, the bird and frog worked examples for the same concept should ideally share the numbers / setup so a reader switching tabs sees the same example through different lenses.
   11. **Interactive module list.** Each lab block: what insight it reveals + the visualization form + the corresponding source section + which tab it lives on.

   Wait for user confirmation or revision before proceeding to step 5.

5. **Generate the HTML.**
   - Output path = `<output-dir>/<source-stem>.html` (source filename with extension swapped to `.html`).
   - Intermediate notes and external references go in `<output-dir>/_drafts/`. In dual-tab mode, drafts go in `_drafts/bird/` and `_drafts/frog/` so the two halves don't trample each other.
   - **Pick the skeleton by (pedagogy, visual) pair.** Use the table below; copy verbatim and fill placeholders. Do not hand-roll a new skeleton — every template already bakes in the layout, type policy, lab IIFE / DPR-scaling pattern, and required components.

     | Mode | Default skeleton | Pre-2026-05 / opt-in skeleton |
     |---|---|---|
     | Single bird | [`templates/simple-bird-skeleton.html`](templates/simple-bird-skeleton.html) | [`templates/bird-skeleton.html`](templates/bird-skeleton.html) (with `--visual magazine`) |
     | Single frog | [`templates/simple-frog-skeleton.html`](templates/simple-frog-skeleton.html) | [`templates/frog-skeleton.html`](templates/frog-skeleton.html) (with `--visual notebook`) |
     | Dual-tab | [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) | [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) (with `--visual magazine,notebook`) |

   - **Single-style mode:** copy the chosen skeleton, fill the placeholders.
   - **Dual-tab mode:** fan out two parallel agent groups (see § Parallel sub-agents — top-level fan-out). Each group generates the body of its half against its own bird / frog skeleton at the chosen visual, *without* the outer `<html>/<head>/<body>` boilerplate (return only the inner content). Then the parent merges both bodies into the dual-tab shell — the wrapper provides the tab bar, hash routing, namespaced CSS scopes (`.tab-bird { … }` and `.tab-frog { … }`), and any shared CDN deps. Each tab's body content gets dropped inside the corresponding `<section id="tab-bird">` / `<section id="tab-frog">` container; the per-skeleton CSS is wrapped in its scope selector so the two tabs' type policies don't collide.
   - **`--math` with simple:** when the source has formulas worth typesetting, add the KaTeX CDN block (the same one that lives in the magazine shells) back to the document `<head>` and a `DOMContentLoaded` auto-render call before `</body>`. Don't auto-load KaTeX without the flag — silent CDN dependency defeats simple's identity.
   - In all modes: follow the **shared pedagogical principles** below, the **hard constraints** below, **and** the relevant style + visual specs.

6. **Open and hand off.**
   - Run `open "<absolute-output-path>"` to launch the HTML in the user's default browser. This is also the moment to walk the lab QA in "Interactive correctness" § item 4 — don't `open` twice.
   - Then print the absolute path **on a line by itself** in the final message (e.g. `/Users/han/project/learn_with_agent/260514/<name>.html`) so the user can `cmd+click` to reopen or copy it cleanly. No surrounding markdown, no trailing punctuation.

## Shared pedagogical principles (apply to every style)

> Not writing a source summary. Writing a learning artifact. The reader should close the page feeling "someone took the time to make this make sense to me."

### 1 · Begin with why (chapter 0 / cold open is non-negotiable)

The first thing the reader sees is **never** "overview of our method." It must be a **field-level predicament**:

- Before this work landed, what were people stuck on?
- What's the obvious thing to try? Why does it fail?
- Ground the predicament in a concrete physical scenario ("假设你有一万张猫的图片"), then translate it to math, code, or data.
- Drop a comparison of how prior families dodge the issue (VAE / GAN / Flow / this work). In magazine: a `.compare` block or a comparison table. In notebook: a markdown cell with a table or a `.diff` two-pane.

In bird style, this is a full chapter 0 with a `.danger` callout titled "致命问题" and a closing meta-line. In frog style, this is a markdown cell + a code cell showing the *actual failure* (the dispatch hell, the broken loop, the wrong output) before the rescue. The form differs; the move is the same. In dual-tab mode, the predicament is shared (same field-level stuck-point) but each tab uses its own callout / cell form to land it.

**Banned**: "Section 1 介绍 / Section 2 相关工作 / Section 3 方法" — that's the structure of the source, not of pedagogy.

### 2 · First principles: naive → fatal flaw → insight → design

Each core concept is unfolded in this exact sequence. First describe the obvious idea any smart reader would think of, so they nod along. Then expose the hidden flaw. Then let the source's insight emerge as the rescue. **Forbidden**: working backward from "the source proposes X."

### 3 · A concrete minimal worked example for every new concept

> Karpathy's lectures live on this pattern. Without it, every formula becomes a ritual symbol.

Every time you introduce a new concept — a definition, a formula, an algorithm step, a function — pause and walk the reader through the smallest concrete instance that exercises it. Pick numbers a reader can hold in their head. Compute by hand, line by line. Land on a specific result the reader can verify. Then state the takeaway: *what does the example reveal about the abstract form?*

This is not "here is an illustrative figure." This is "here is the same calculation, with numbers you could redo on a napkin."

**Concrete formats:**

- **Score function.** Don't just write `s(x) = ∇log p(x)`. Take a 1D standard normal: `p(x) = (1/√2π) e^(−x²/2)`. Then `log p(x) = −x²/2 − const`, so `s(x) = −x`. At `x = 2`, score = `−2`: points back toward the origin with magnitude equal to distance. Now the abstract symbol is anchored.
- **Linear combination of columns.** Don't just write `Ax = x_1·col_1 + x_2·col_2`. Take `A = I_2`, `x = [2,3]`. Compute: `2·[1,0] + 3·[0,1] = [2,3]`. Then change `x = [1,1]`, recompute. Now "linear combination" is not a phrase, it's an act.
- **Attention.** Don't just write `softmax(QK^T)V`. Take 2 tokens of dim 2, set `Q = K = V = I_2`. Compute `QK^T = I_2`, softmax row-wise, multiply with V. Result: identity attention (each token attends to itself). Then perturb `Q[0]` to `[0.5, 0.5]` and watch the row mix.

**Rendering depends on style:**
- **bird**: a `.worked-example` block with `we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`. The example follows a "method-from-goal → simplest input that exercises it → observe the goal is met" arc.
- **frog**: a code cell (`In [N]:`) that computes the example + an output cell (`Out[N]:`) showing the result, then a markdown cell naming the takeaway. Or, for Ng-style derivations, a `.chalk` block tracing the steps by hand from likelihood → gradient → update rule.

**Constraints on the example:**
- Smallest dimension that's not degenerate (1D or 2D, not 7D).
- Numbers that make arithmetic trivial (`1, 2, 0, ½, π/4` — not `0.7234`).
- One step per line; never make the reader factor what you just did.
- End with a punchline, not "and so on." If you can't extract a punchline, the example was too large.
- Show the example **before** generalizing. Concrete first, abstract second.

### 4 · 80% to the core, as a budget

1–3 core insights consume 80% of the page; everything else collapses to a single sentence or a footnote. If the source has 5 contributions, pick the deepest 1–3 and go deep. **Do not** transcribe full ablation tables.

### 5 · Audience-aware (reader profile lives in `AGENTS.md`)

The reader is a CS PhD with 8 years in vision/DL. **Mention briefly or skip:** standard backprop / Adam / SGD / LayerNorm; vanilla self-attention / multi-head attention; ResNet / U-Net / ViT basics; plain cross-entropy / KL divergence.

**Spend the page budget on what's actually new**: the source's key insight, the new mechanism, why only this design works.

### 6 · No paper-boilerplate language (反论文腔)

The HTML's content is Chinese. **Banned template phrases** (search and remove before shipping): 本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得注意的是 / 显然地 / 与此同时 / 据此可知 / 由上可见.

**Pacing.** Long and short sentences alternate. Allow short sentences, rhetorical questions, metaphors, colloquial pivots ("换句话说" / "问题来了" / "听起来很玄, 其实……" / "注意一个微妙的点"). No paragraph longer than 5–6 lines. After a dense reasoning paragraph, give the reader a breath.

**Intuition before formalism.** Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.

**First and second person allowed.** "我们" / "你会发现" / "试着想一下" beats wall-to-wall passive voice.

**Don't pad.** One clear sentence beats three subordinate clauses cosplaying rigor.

**去 AI 味。** 读着要像一个语言天赋极强的人写的——自然、通顺、悦耳。**少用**"不是 X，而是 Y"这种工整对仗句式；其他被反复吐槽的模型腔（机械三段排比、空洞的"值得深思 / 综合来看 / 让我们一起"、整齐到僵硬的并列、过度收尾总结）一并避开。

**Voice differences across styles** (the actual delta — see each style's spec for the long form):
- **bird** is *the meta-question first* — "what are we really trying to accomplish here?", strip the noise, derive the method from the goal, close with the principle to remember when details fade; long-form magazine pacing; warm-paper layout; cross-domain transfer and asymptotic-case observations are signature beats (Hamming).
- **frog** is *spelled-out from the example up* — "okay 接下来 / 好我们直接看一下"; code-cell ↔ output-cell as the page's spine (Karpathy); or likelihood → gradient → algorithm derivation (Ng); "stop & think" pauses; analogies to things the reader has already written; lowercase conversational openers.

### 7 · Color-coded variables (define once, reuse everywhere)

Recurring key variables / objects across math, SVG, prose, and code highlights **all share a single color palette**:

```html
<span class="v-x">x</span>      <!-- red -->
<span class="v-y">y</span>      <!-- blue -->
<span class="v-z">z</span>      <!-- green -->
<span class="v-b">b</span>      <!-- purple (target) -->
```

In LaTeX: `\(\textcolor{#dc2626}{x}\)`. In SVG: stroke/fill with the same hex. In prose: inline `<span class="v-x">`. The reader calibrates the palette once; from then on, every formula and figure is parsable without mental relabeling.

Reference: MIT 18.06's `vec-col1/2/3/b` keeps three column vectors and the target the same colors from the row picture → column picture → matrix form → n-dim abstraction.

### 8 · Revealing interactivity (not knob-pushing demos)

Every lab block leads with a single line: **"此 lab 揭示：…（对应来源章节）"** (or its frog notebook equivalent under the `.lab-sub` text). Useless interactions (input box → display number, slider that only changes a color) are banned. Useful forms include:

- Vector field / manifold visualization (click to drop particles, watch them follow the score).
- Parameter slider → geometric object morphs (two lines' intersection, planes' intersection line, singular vs. non-singular).
- Annealed sequence: from large noise to small noise, frame by frame.
- Multi-step algorithm with step-dot or step-trace indicator: prev/next buttons, current step highlighted.
- Tab group when there are multiple methods to compare.

### 9 · Source figures when they earn it

When the source has imagery that's **clearly relevant** — generated samples, key result figures, dataset examples, physical-apparatus photos, named-people portraits a timeline references — embed it. Visual texture grounds the prose and gives the reader something to look at other than paragraphs and SVGs.

**Trigger**: the figure carries information the worked-example + diagram can't easily replace. If you'd struggle to write a one-line caption that explains *why this image is here*, skip it.

**Embedding** (single-file double-click rule still holds):
- **PDF-source figures**: extract with `pdfimages` or `pdftoppm`, then inline as `<img src="data:image/png;base64,…">`. Quality > size; downscale to ≤ 1200px on the long edge so the file stays manageable.
- **Web images**: only from stable pinned URLs (Wikipedia Commons, arXiv-hosted, paper supplementary, the author's project page). Anything not from the source itself goes inside a clearly-labeled "external" aside.
- **No AI-generated stock filler.** Decorative slop is worse than no image. Generic "abstract neural network" art especially — banned.

This is **opt-in**, not a checklist requirement. If the source genuinely has nothing photogenic worth keeping, the SVG + worked-example spine carries the page on its own.

## Hard constraints (apply to every style)

- **Single HTML file.** All CSS/JS inlined or via CDN (when the visual permits CDN at all — see Fonts below); images either inlined as base64 data URIs or loaded from pinned public CDNs. **No** project-root, `_lib/`, or local-asset references. Double-click to view.
- **Same stem; folder per resolution rule.** Filename always swaps the source extension to `.html`. The folder follows step 1 of the workflow.
- **Fonts.** **Choosing the visual implies the font policy — do not mix.**
  - **Simple visual (default): macOS system font stack — no Google Fonts, no external font CDN.** Body = `-apple-system, "Iowan Old Style", "Charter", … serif`. Mono = `ui-monospace, "SF Mono", Menlo, … monospace`. The `<head>` contains zero `fonts.googleapis.com` URLs.
  - **Magazine visual:** Google Fonts loaded via CDN — Playfair Display + Cormorant Garamond + Inter + JetBrains Mono. The display serif + decorative italic + sans labels + mono code stack is the magazine identity; don't substitute.
  - **Notebook visual:** Google Fonts loaded via CDN — Inter + JetBrains Mono.
  - **Do not** ship a `system-ui`-only stack as a fallback for magazine or notebook — those visuals depend on the named typefaces for their identity. If you don't want Google Fonts, use simple.
- **Math.** **Math support follows the visual.**
  - **Simple visual:** KaTeX is **off by default**. Loaded only when `--math` is passed or when the source's body contains `$$ … $$` / `\[ … \]` after extraction (in which case treat the source as math-bearing and warn the user if KaTeX wasn't requested — don't silently load it). When loaded, use the same CDN-deferred + `DOMContentLoaded` pattern as the magazine shell.
  - **Magazine visual:** KaTeX loaded by default (paper-learning use case). CDN-deferred + `DOMContentLoaded` auto-render.
  - **Notebook visual:** KaTeX loaded by default. CDN-deferred + `DOMContentLoaded` auto-render.
  - **Never** call `renderMathInElement` from `<script ... onload="...">` — see Gotchas.
- **Code.**
  - **Simple visual:** plain `<pre><code>` styled by inline CSS — no Prism, no highlight.js. The warm-paper code background + gold left-border is the simple visual's code identity.
  - **Magazine / notebook visuals:** Prism (light theme `prism.css`) or highlight.js via CDN. Pin the version.
- **Style sheets.** Inline `<style>` or (for magazine / notebook) Tailwind CDN — **Bootstrap is banned**. The simple visual has no Tailwind either; the `<style>` block carries every rule the page needs.
- **No build step.** No npm / vite / webpack.
- **Topic isolation.** Do not read other topic folders.
- **Online research is allowed.** When the agent enriches with external material, mark it explicitly (in magazine: `aside.external`; in notebook: a clearly labeled callout) — source-original vs. agent-added must be visually distinguishable.
- **When unsure**, search the web first. If still uncertain, write the section anyway and mark the spot with `<div class="uncertain">⚠ 此处未充分消化：[原因]</div>`. **Do not interrupt the user with questions.**
- **HTML already exists.** **Overwrite** (re-running grok on the same source means the user wants to replace). Don't touch `_drafts/`.
- **Pin CDN versions** (`katex@0.16.11`, `prismjs@1.29.0`). **No `@latest`.**
- **Dual-tab slug contract.** Every concept that exists on both tabs gets an anchor pair: `id="bird-<slug>"` on the bird side and `id="frog-<slug>"` on the frog side, with `<slug>` shared. **No per-section UI affordance** — the only cross-tab control is the top tab bar; do not add `↔ 另一视角`-style jump buttons next to headings. The slug pair earns its keep through (a) the hash-routing JS in `templates/dual-tab-skeleton.html`, which switches tabs and scrolls when someone shares `#frog-densify` in chat — and silently remaps legacy `mit-` / `stanford-` hashes so old links keep working — and (b) forcing both halves to agree on what scope each section covers. Single-style mode has no `bird-` / `frog-` prefix on anchors — just `<slug>`.
- **Dual-tab CSS namespacing.** When merging the two halves into the dual-tab shell, all CSS rules from the bird skeleton must be scoped under `.tab-bird { … }` and all rules from the frog skeleton under `.tab-frog { … }`. The two skeletons share class names (`.lab`, `.callout`, `.cell`, etc.) but mean different things — un-namespaced rules will cross-wire. Shared CDN deps (KaTeX, Prism, fonts) load once at the document level, outside both tab scopes.
- **Mobile / narrow-screen rules.** Every template's `<style>` block carries `@media (max-width:720px)` + `@media (max-width:480px)` blocks. Hard rules: (a) **the tab bar must NOT wrap character-by-character** — labels stay `white-space:nowrap; flex-shrink:0;` and the bar itself becomes `overflow-x:auto` with hidden scrollbars rather than letting "鸟/瞰" split across two lines; meta info hides on narrow screens; (b) **code blocks (`pre`, `.cell.code pre`, `.chalk`, `pre[class*="language-"]`) get `overflow-x:auto` + `-webkit-overflow-scrolling:touch`** and a shrunk font, so long lines scroll horizontally instead of bleeding past the viewport; (c) **section padding tightens to ≤14px** at 720px and ≤12px at 480px (`main`/`.page`/`.nb` containers); (d) tables get `display:block; overflow-x:auto` so wide tables scroll instead of pushing the page wider; (e) lab controls stack vertically and `.lab canvas` becomes `max-width:100%; height:auto`. When adding new components to a template, add their narrow-screen rule to the same `@media` blocks — don't ship a component that only works on desktop.

### Interactive correctness (don't ship a blank canvas)

The two failure modes that show up most often: **blank canvas** (lab block renders, canvas inside is empty) and **blurry / stretched canvas** (draws fine on the agent's screenshot, looks wrong on the user's retina screen). Guard both — both skeletons already bake these fixes in; if you hand-roll a lab, copy the same pattern:

1. **Render on init.** Every lab IIFE must end with one bare `draw()` call. Never leave the canvas waiting for a first input event. Wrap each lab in `(function(){ const c = document.getElementById('…'); if (!c) return; … draw(); })();` so a missing element doesn't break the rest of the page.
2. **DPR-scale every canvas.** After `getContext('2d')`, set `c.style.width = cssW + 'px'; c.style.height = cssH + 'px'; c.width = cssW * dpr; c.height = cssH * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);`. Drawing then uses CSS pixels but stays sharp on retina.
3. **Lab-prefixed ids.** Two labs cannot share `r1` / `canvas-1`. Prefix every control with the lab name (`lab2-yaw`, `rsc-step`) so a copy-paste doesn't silently cross-wire.
4. **Run the page locally before declaring done.** `open <output-dir>/<name>.html`, scroll to each lab, drag every slider, click every button. If a canvas is blank or a control does nothing, fix before shipping.

## Self-audit checklist (shared base — run alongside the style-specific checklist)

**Writing / content (style-agnostic)**
- [ ] **Cold open is begin-with-why**: predicament + naive + fatal flaw + prior-family comparison. Not "overview of our method."
- [ ] **Every new concept has a worked example** with concrete numbers a reader could redo on a napkin. The example precedes the abstraction.
- [ ] No paper-boilerplate phrases left in the prose: 本文 / 综上 / 基于此 / 不失一般性 / 值得注意的是 / 显然地 — search and replace.
- [ ] **AI 味自检**: "不是 X，而是 Y" 的对仗句式不超过 1–2 处；没有"值得深思 / 综合来看 / 让我们一起 / 总而言之"这类模型口头禅。
- [ ] No paragraph runs longer than 5–6 lines. Dense reasoning paragraphs are interrupted with short sentences, rhetorical questions, or metaphors.
- [ ] Every new term, on first appearance, gets a one-line intuition anchor before its definition or formula.
- [ ] Recurring key variables are color-coded; the same hex appears in formulas, SVG strokes / code highlights, and inline prose.

**Technical (visual-agnostic)**
- [ ] Single HTML file. Every external dependency (when any) is pinned to a stable version. No local-asset references.
- [ ] Every `<section>` / `<h2>` has an `id`. Every internal link's `data-target` / `href="#…"` resolves.
- [ ] Every agent-added external content is marked (style-specific marker — see each style's spec).
- [ ] Every not-fully-digested spot is marked with `<div class="uncertain">⚠ …</div>`. No silent TODOs.
- [ ] **Every lab IIFE ends with `draw()`** — no blank canvas on first paint.
- [ ] **Every canvas is DPR-scaled**. Lab control ids are lab-prefixed; no collisions across labs.

**Technical (visual-specific)**
- [ ] **If visual = simple:** the HTML contains **no `fonts.googleapis.com`** URL, **no `katex`** / **`prismjs`** / **`tailwindcss`** / **`highlight.js`** CDN reference (unless `--math` was passed, in which case KaTeX is allowed and only KaTeX). All CSS is in one inline `<style>` block; all JS is in one inline `<script>` block.
- [ ] **If visual = simple:** `:root` declares the warm-paper tokens (`--paper` / `--paper-2` / `--ink` / `--ink-soft` / `--ink-faint` / `--rule` / `--rule-soft` / `--accent` / `--accent-2` / `--gold`). Don't strip them — they're the visual identity.
- [ ] **If visual = magazine:** Google Fonts URL loads Playfair + Cormorant + Inter + JetBrains Mono. KaTeX + Prism light theme are present and pinned.
- [ ] **If visual = notebook:** Google Fonts URL loads Inter + JetBrains Mono. KaTeX + Prism light theme are present and pinned.

**Dual-tab specific (only when the output is dual-tab)**
- [ ] Both tabs cover the **full source scope** — neither is a fragment that requires the other to make sense.
- [ ] Every cross-tab pair shares a `<slug>`; bird side is `id="bird-<slug>"`, frog side is `id="frog-<slug>"`. Mismatches break deep-link hash routing.
- [ ] **No per-section "↔ 另一视角" jump buttons** in either tab body — the global tab bar is the only cross-tab control.
- [ ] Hash routing works: pasting `#frog-<slug>` into the URL switches to the frog tab and scrolls to the matching section.
- [ ] CSS rules from both skeletons are namespaced under `.tab-bird` / `.tab-frog` — no un-scoped rule leaks across tabs.
- [ ] If one tab was force-filled (principle 3 violation), it was dropped in step 4 and the page is now single-style with an editor-note explaining the omitted lens. The page does **not** ship a half-empty tab.
- [ ] Color-code palette is consistent across both tabs — a variable's hex on the bird side equals its hex on the frog side.

Run the **style-specific** half of the audit from `references/styles/<Style>.md` before declaring done.

## Gotchas

- **Multiple PDFs in the folder** — ask the user; never default to the first.
- **Mac font fallback** — the CSS stacks in both skeletons include fallbacks (Playfair → Cormorant → Georgia → Times; Inter → system-ui → Helvetica Neue → Arial; JetBrains Mono → Fira Code → Courier New). Don't strip them.
- **KaTeX + color-coded variables** — inside LaTeX use `\textcolor{#c0392b}{x}`; in prose use `<span class="v-x">x</span>`. The hex must match on both sides.
- **KaTeX activation must use `DOMContentLoaded`, never `<script ... onload="renderMathInElement(...)">`** — `onload` fires the moment the auto-render script *file* finishes downloading, which can land mid-parse on a long body (a dual-tab page in particular). Everything still being parsed at that instant — typically the entire second tab — gets skipped, and only some formulas render. All three skeletons now load KaTeX deferred and call `renderMathInElement` from a `DOMContentLoaded` listener with `ignoredTags: ['pre','code',...]` and `throwOnError: false`. If you tweak the delimiter set or `ignoredTags` in one skeleton, mirror it across all three so single-style and dual-tab outputs behave identically.
- **`@latest` is forbidden** — every CDN URL pins a stable version so loads stay reproducible across months.
- **Don't leave silent TODO placeholders** — fully write the section, or mark it explicitly with `.uncertain`.
- **Worked-example pitfalls** — if the example takes more than ~5 steps, it's too big. If you can't extract a one-line takeaway, the example wasn't well-chosen. If the numbers aren't tiny (1, 2, 0, ½, π/4), pick smaller ones. The whole point is "the reader could redo this on a napkin."
- **Self-audit "text on a page"** — if the page is mostly `<p>` and a few `<pre>`, with none of the style's required components, that's not a delivery. Go back to the style pack's checklist.
- **Wrong-style trap** — if you find yourself wanting a Roman numeral inside a frog-style page, or a code-cell-and-output pair inside a bird-style page, you're rendering the wrong style. Re-check the user's request, and if uncertain, ask before continuing.
- **Don't mix style components silently** — magazine's `section.branch[data-accent]` and notebook's `.cell` / `.chalk` / `.nums` are not interchangeable. The two CSS systems use different fonts, different page backgrounds, different spacing. If you need a hybrid, write it down in the alignment outline and confirm with the user first.
- **Blank canvas / blurry canvas** — see "Interactive correctness" above. Both skeleton templates already bake the fixes in; copy them verbatim instead of hand-rolling a new lab from scratch.
- **Dual-tab principle violations** — the two most common slips: (a) splitting coverage across tabs ("bird tab covers theory, frog tab covers the implementation") — that's one book in two chapters, not two lenses; revert to single-style or rewrite both halves to be standalone; (b) shipping a half-empty frog tab on a pure mathematical-existence-theorem paper "because the default is dual-tab" — that's exactly the case principle 3 says to drop; emit single-tab bird with an editor-note.
- **Slug drift** — if the bird side renames a section heading mid-draft, the frog side's `id="frog-<slug>"` must update too. The slug map from the alignment outline is the source of truth; revisit it whenever a section title changes. Without matching slugs, deep links like `#frog-<slug>` shared in chat won't land where the linker expected.
- **Dual-tab CSS bleed** — without proper `.tab-bird` / `.tab-frog` scoping, magazine's body background (warm paper) will bleed into frog's notebook surface, or notebook's blue cell stripe will appear behind magazine pull-quotes. The dual-tab skeleton's namespacing is structural — do not strip it.
- **Legacy aliases are honored, not deprecated** — `--style mit` / `--style stanford` / `--style feynman` / `--style karpathy` keep working silently. Don't print warnings; don't try to "correct" the user. The aliases exist because old project notes / chat history / cross-skill references (e.g. `3dgs_exp_report`) sometimes still use the old names, and we want those to keep working without a flag-day migration.
- **Mixing simple with paper-learning + LaTeX math** — KaTeX is off in the simple visual by default. If the source has formulas worth typesetting (more than a couple of `$$ … $$` blocks), either pass `--math` to add KaTeX back to the simple shell, or rerun with `--visual magazine` for the full paper-learning identity. Don't render LaTeX as raw text on the page silently.
- **Don't strip the warm-paper CSS variables** — `--paper` / `--ink` / `--rule` / `--accent` / `--accent-2` etc. in the `:root` block are the simple visual's identity. The page reverts to "blog post on system fonts" the moment they're removed.
- **Don't sneak Google Fonts into the simple visual** — `fonts.googleapis.com` is forbidden in simple, even via a "harmless" extra import for a "nicer" italic. If you want a Playfair italic, switch to `--visual magazine`. Mixed identity is worse than either pure identity.
- **Don't render Roman-numeral chapter openers under the notebook visual** or `In [N]:` cells under the magazine visual — those are pedagogy markers tied to their visual. The simple visual lets bird-pedagogy and frog-pedagogy each keep their markers (Roman numerals on bird-simple, In/Out cells on frog-simple) while sharing the warm-paper palette — that's the point of having a third visual.

## See also

**Pedagogy packs**
- [`references/styles/bird.md`](references/styles/bird.md) — bird style pack; top-down, Hamming lineage. Owns the bird voice contract and the magazine visual (its default rendering).
- [`references/styles/frog.md`](references/styles/frog.md) — frog style pack; bottom-up, Karpathy + Andrew Ng lineage. Owns the frog voice contract and the notebook visual (its default rendering).

**Visual layer**
- [`references/styles/visual-simple.md`](references/styles/visual-simple.md) — simple visual layer (new default); macOS system fonts, warm-paper palette, zero external CDN. Hosts both bird-flavored and frog-flavored sub-styles.

**Skeletons**
- [`templates/simple-bird-skeleton.html`](templates/simple-bird-skeleton.html) — bird body under simple visual (new default for single bird).
- [`templates/simple-frog-skeleton.html`](templates/simple-frog-skeleton.html) — frog body under simple visual (new default for single frog).
- [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) — outer shell for the new dual-tab default: sticky tab bar, hash routing, both halves under simple.
- [`templates/bird-skeleton.html`](templates/bird-skeleton.html) — bird body under magazine visual (opt-in via `--visual magazine`).
- [`templates/frog-skeleton.html`](templates/frog-skeleton.html) — frog body under notebook visual (opt-in via `--visual notebook`).
- [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) — outer shell for the pre-2026-05 default (bird=magazine, frog=notebook); opt-in via `--visual magazine,notebook`.

**External**
- Project-root `AGENTS.md` — reader profile, project-level hard constraints, trigger protocol.
- `write-a-skill/SKILL.md` — authoring rules for editing this skill or adding new style packs.
- Freeman Dyson, "Birds and Frogs," *Notices of the AMS* 56(2), 2009 — the essay this skill's pack names lift from.
