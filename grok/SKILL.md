---
name: grok
description: Convert a target folder — paper PDF, book chapter, concept note, codebase entry-point — into a single-file interactive learning HTML (Chinese artifact). Default = two-tab page; bird (top-down, Feynman-style) + frog (bottom-up, Karpathy / Ng-style) on the same source. Single-tab via `--style bird` / `--style frog`; add a third guest tab via `with guest <name>`; visual variants via `--visual simple|magazine|notebook`. Use when the user runs `/grok <folder>`, asks to "学习/讲解/拆解/搞懂 X 文件夹里的 paper / 书 / 概念 / 代码" inside `learn_with_agent`, or asks for a bird / frog / Hamming / Karpathy / Ng / SICP / notebook / magazine / simple / guest explainer.
---

# grok

Artifact language: Chinese. Spec language: English.

## Quick start

```
/grok "260506_Coding Agents_alphazero"                                 # default: dual-tab, both tabs under 'simple' visual
/grok "260506_Coding Agents_alphazero" --style bird                    # bird only, still 'simple' visual
/grok "260506_Coding Agents_alphazero" --style frog                    # frog only, still 'simple' visual
/grok "260506_Coding Agents_alphazero" --visual magazine               # bird tab uses magazine + KaTeX
/grok "260506_Coding Agents_alphazero" --visual magazine,notebook      # pre-2026-05 default (bird=magazine, frog=notebook)
/grok "260506_Coding Agents_alphazero" --style bird --visual magazine  # bird-only, magazine visual
/grok "260506_Coding Agents_alphazero" --style frog --visual notebook  # frog-only, notebook visual
/grok 讲讲佛教里无常的概念 with guest steve_jobs                        # triple-tab (concept, not folder)
/grok "260506_Coding Agents_alphazero" with guest steve_jobs            # triple-tab: bird + frog + guest
/grok "260506_Coding Agents_alphazero" --math                          # any visual + KaTeX added back
/grok "260506_Coding Agents_alphazero" --align                         # alignment checkpoint first
```

Natural-language equivalents: "用 bird 风格 / 费曼风格 / Feynman 风格 / 自顶向下 / 抽象先行" → bird. "用 frog / Karpathy / Andrew Ng 风格 / spelled out from scratch / 自底向上 / 例子先行" → frog. "杂志风 / magazine / longread" → magazine visual. "notebook 形式 / jupyter 风格" → notebook visual. "调研报告 / 简洁版 / 不要 google fonts" or saying nothing about visual → simple.

Legacy aliases (silent): `--style mit` / `--style feynman` → bird. `--style stanford` / `--style karpathy` → frog.

Output:
- **No folder argument**, or source outside `learn_with_agent/` → `/Users/han/project/learn_with_agent/<YYMMDD>/<source-name>.html`. `mkdir -p` on demand.
- **Folder argument given** → `<folder>/<source-name>.html`.

Filename = source stem with extension swapped to `.html`. Single file.

## Trigger discipline

Enter this skill **only** on explicit user invocation. Seeing a PDF, Markdown note, e-book, or unfamiliar source folder in the workspace is not a trigger.

## Pedagogy × Visual axes

Two orthogonal axes. `--style` picks pedagogy (primary identity); `--visual` picks visual (rendering). Either omitted → default below.

### Pedagogy packs

| Pack | Posture | Lineage | Spec |
|---|---|---|---|
| **bird** 🐦 | Top-down conceptual narrative; predicament → insight → mechanism, with worked examples inline | Feynman lectures + Karpathy long-form essays | [`references/pedagogy/bird.md`](references/pedagogy/bird.md) |
| **frog** 🐸 | Bottom-up, worked-example first; abstraction emerges | Karpathy "zero to hero" + Andrew Ng CS229 | [`references/pedagogy/frog.md`](references/pedagogy/frog.md) |

**Pedagogy default:** no `--style` flag → dual-tab (both packs). See § Dual-tab contract.

### Guest packs (additive third pedagogy)

A guest is a third pedagogy that runs in parallel with bird and frog — same altitude class, written by its own dedicated sub-agent, rendered as its own tab. Experimental lab; moves that earn their keep get folded back into bird or frog.

| Persona | Lens | Spec |
|---|---|---|
| **steve_jobs** | Product-vision: demo first, brutal simplicity audit, "one more thing" close | [`references/pedagogy/guests/steve_jobs.md`](references/pedagogy/guests/steve_jobs.md) |

**Trigger:** `with guest <name>` appended (or "用 steve_jobs 视角讲" / "Steve Jobs 风格"). Additive on top of the default:

| Invocation | Output |
|---|---|
| `/grok <topic>` | dual-tab: bird + frog |
| `/grok <topic> with guest steve_jobs` | **triple-tab: bird + frog + guest** |
| `/grok <topic> --style bird with guest steve_jobs` | dual-tab: bird + guest |
| `/grok <topic> --style frog with guest steve_jobs` | dual-tab: frog + guest |

Hard rules for guests:

1. **Parallel pedagogy, not an overlay.** Same role as bird/frog; covers the entire source scope.
2. **One sub-agent per guest tab.** Persona voice suffers when stitched from multiple agents; one agent owns the whole tab body.
3. **Slug coordination is best-effort.** Where a section parallels bird/frog, share the slug (`id="guest-<slug>"` alongside `id="bird-<slug>"` / `id="frog-<slug>"`). Guest-only sections use guest-only slugs. Color hex still shared across all three tabs.
4. **Each pack declares its base** for CSS / layout reuse (`simple-bird-skeleton.html` for top-down personas, `simple-frog-skeleton.html` for bottom-up). The guest tab body is built from that base's CSS scoped under `.tab-guest`.
5. **No tri-tab skeleton file yet.** Triple-tab is assembled inline by extending the dual-tab skeleton at output time. Promote to a real skeleton once the pattern stabilizes.
6. **Roster is not permanent.** Add → drop `references/pedagogy/guests/<name>.md` + add a row above. Remove → delete both. When a guest's moves earn their keep, fold into `bird.md` or `frog.md`.
7. **No legacy aliases for guests.** Addressed by declared name only.

### Visual layers

| Visual | Look | Spec | Skeleton |
|---|---|---|---|
| **simple** (default) | macOS system fonts + warm paper + zero external CDN | [`references/visual/simple.md`](references/visual/simple.md) | [`templates/simple-bird-skeleton.html`](templates/simple-bird-skeleton.html) · [`templates/simple-frog-skeleton.html`](templates/simple-frog-skeleton.html) · [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) |
| **magazine** (opt-in) | Sunday longread; Playfair + Cormorant via Google Fonts + KaTeX | [`references/visual/magazine.md`](references/visual/magazine.md) | [`templates/bird-skeleton.html`](templates/bird-skeleton.html) |
| **notebook** (opt-in) | Jupyter on off-white; Inter + JetBrains via Google Fonts + KaTeX | [`references/visual/notebook.md`](references/visual/notebook.md) | [`templates/frog-skeleton.html`](templates/frog-skeleton.html) |

**Visual default:** no `--visual` flag → simple for both halves. Pre-2026-05 default preserved as `--visual magazine,notebook`.

### Resolving the choice

- Pedagogy named, no visual → visual defaults to simple.
- Visual named, no pedagogy → pedagogy defaults to dual-tab (visual applies to both halves; magazine-rendered frog keeps the frog *voice* on warm paper with Cormorant body — rare but allowed).
- Both named → both stick.
- `--visual magazine,notebook` → mixed dual-tab (bird tab magazine, frog tab notebook).
- `--visual magazine` alone in dual-tab → magazine applies to whichever tab is bird-pedagogy; frog tab stays simple.
- Visual doesn't match pedagogy (e.g. notebook on bird-style) → fall back to simple. Don't force a notebook-rendered bird.
- `--math` adds KaTeX to whichever visual is active (always on for magazine / notebook; opt-in for simple).
- Guest tab follows its pack's declared visual policy regardless of `--visual` (the persona's visual identity is part of the persona). If the user wants the guest tab to track a non-default visual, they say so in chat; the agent passes the override to the guest sub-agent.

When the user asks for a single pedagogy but is ambiguous which one, ask once — *bird (top-down) or frog (bottom-up)?* — before generating.

### Adding a new pedagogy or visual

**New pedagogy** (rare): add `references/pedagogy/<name>.md` (voice only), add `templates/<name>-skeleton.html` if needed, register in the table above + its trigger phrases.

**New visual** (rare): add `references/visual/<name>.md` (components, CSS, audit) and `templates/<name>-{bird,frog,dual-tab}-skeleton.html`. Re-use one of the existing visuals as a starting pattern. Register in the table above.

Packs earn their place by being meaningfully different. If a "new style" is "magazine but with two columns," propose an extension to magazine.md, not a new pack.

## Dual-tab contract

Three principles. Not negotiable.

1. **Same scope, different lens.** Both tabs cover the entire source. Reading either alone must be a complete artifact. Splitting coverage ("tab A covers framework, tab B covers implementation") is forbidden.
2. **Matching slugs across tabs.** Each top-level concept gets parallel anchors: `id="bird-<slug>"` and `id="frog-<slug>"`, slug shared. Serves (a) planning aid — if you can't agree on a slug, the halves have drifted — and (b) hash routing — `#frog-densify` shared in chat switches tab + scrolls. **Do NOT add per-section "↔ 另一视角" jump buttons** — the global tab bar is the only cross-tab affordance.
3. **Don't force-fill — ship one tab if the other lens has nothing.** Pure complexity result / pure existence theorem / code-only refactor may have no real bird story (no question worth lifting) or no real frog story (no numerical example). Emit single-style with one-sentence note in editor-note ("frog 视角因没有可手算的例子被略去"). Forcing a half-empty tab is worse than honest absence.

The tab shell is one of: [`templates/simple-dual-tab-skeleton.html`](templates/simple-dual-tab-skeleton.html) (default) or [`templates/dual-tab-skeleton.html`](templates/dual-tab-skeleton.html) (pre-2026-05). Both provide the tab bar, hash routing, namespaced CSS scopes (`.tab-bird` / `.tab-frog`), and legacy `mit-` / `stanford-` anchor remapping. **Each tab keeps its own scroll position** — switching bird→frog lands frog where you last left it (top on first visit), and returning restores bird's spot; only a `#bird-<slug>`/`#frog-<slug>` deep link overrides this to scroll to the anchor.

Triple-tab (with guest) is assembled inline: add a third `<button class="tab-btn" data-tab="guest">`, a third `<section class="tab-pane tab-guest" id="tab-guest">`, the guest's CSS scoped under `.tab-guest`, and `#guest-<slug>` handling in the hash-router.

## Parallel sub-agents

Paper-grokking is naturally chunked. Fan independent units out as sub-agents — one Agent tool call per unit, fired in a single message so they run concurrently.

**Top-level fan-out:**
- **Dual-tab default:** bird-half agent group + frog-half agent group. Both run concurrently after the alignment outline is locked.
- **Triple-tab (with guest):** + one guest agent (single agent, never per-section — voice unity).
- Each group receives the shared alignment outline, the cross-anchor slug map, the style pack + visual spec, and the tab assignment.

**Inside each group:**
- Prior-work research for chapter 0 — one agent per family (VAE / GAN / Flow / …). Run once at top level; both halves consume.
- Section drafting after outline is locked — one agent per section per half.
- External supplements — one agent per topic per half (or shared when supplement is identical).
- Lab visualizations — one agent per lab (IIFE + DPR-scaled canvas).
- Worked examples — one agent per concept per half. Bird worked example is "the principle, instantiated on the smallest case that exercises it"; frog worked example is "compute it by hand and read off the answer."

**Don't parallelize the linear spine.** Chapter 0 must be drafted first; alignment outline confirmed first; slug map agreed first; master HTML stitch-together happens once on the parent.

**Model for text-producing agents.** When running inside Claude Code, set `model: "opus-4-6"` on all section-drafting and worked-example agents — 4.6's prose is more human-friendly than newer checkpoints. If the model flag is unavailable, omit it.

## Workflow

1. **Locate input + resolve output dir.**
   - Resolve `<folder>` (relative or absolute) when given. Read the source the user named. Don't auto-detect (don't glob for `*.pdf` and silently pick one). You may read supplementary files inside the same folder (`_drafts/`, related figures, sibling sources) when they help understanding. Strict topic isolation.
   - Scan for embeddable imagery while you read. Extract with `pdfimages` / `pdftoppm` in step 5; don't defer the decision.
   - **`<output-dir>`:** folder argument → that folder. Otherwise → `/Users/han/project/learn_with_agent/<YYMMDD>/` (today's date). `mkdir -p` if needed.

2. **Resolve pedagogy + visual + mode.** Load specs based on the table in § Pedagogy × Visual axes:
   - Dual-tab (default) → load `references/pedagogy/bird.md` + `references/pedagogy/frog.md`.
   - Single bird / single frog → load only that file.
   - With guest → additionally load `references/pedagogy/guests/<name>.md` + the spec of the base pack the guest declares.
   - Visual = simple (default) → load `references/visual/simple.md`.
   - Visual = magazine → load `references/visual/magazine.md`.
   - Visual = notebook → load `references/visual/notebook.md`.
   - Mixed dual-tab (e.g. `--visual magazine,notebook`) → load both relevant visual specs.
   - **Always load** [`references/pedagogy/principles.md`](references/pedagogy/principles.md) — the 9 shared pedagogical principles apply to every page.

3. **Branch on mode.** Default → step 5. `--align` → step 4 first.

4. **Alignment checkpoint (only with `--align`).** Output the following in chat **and** write to `<output-dir>/_drafts/outline.md`. Content is Chinese (it previews the HTML).
   1. **Begin-with-why paragraph.** What was the field stuck on? Obvious approach + why it fails. Shared across both tabs in dual-tab mode.
   2. **One-paragraph thesis.** Source's key insight; what fundamentally separates it from prior solutions.
   3. **Mode + style plan.** Dual-tab / single bird / single frog. In dual-tab, one or two sentences per half on how each voice will land.
   4. **Cross-anchor slug map (dual-tab only).** Table of `<slug> · bird title · frog title`. Mark `bird-only` / `frog-only` for sections that exist on only one side.
   5. **Tab-pruning decision (dual-tab only).** Is one half going to be force-filled? Drop it now — switch to single-style and note the omitted lens. Act on principle 3 before drafting starts.
   6. **Section outline.** Per section per active tab: title (with one `<strong>` keyword in magazine, or a mono-cap section number in notebook), one-line italic hook, percent of page budget.
   7. **80% allocation.** Name the 1–3 core concepts that consume 80% of the page.
   8. **Color-code plan.** Recurring variables / objects + their fixed colors. Same hex across both tabs.
   9. **Worked-example plan.** Per concept: the smallest concrete instance. Dual-tab: bird and frog examples for the same concept share the numbers.
   10. **Interactive module list.** Per lab: insight + visualization form + source section + which tab it lives on.

   Wait for user confirmation or revision.

5. **Generate the HTML.**
   - Output path = `<output-dir>/<source-stem>.html`. Drafts in `<output-dir>/_drafts/` (in dual-tab: `_drafts/bird/` + `_drafts/frog/`).
   - **Pick the skeleton by (pedagogy, visual) pair:**

     | Mode | Default | Pre-2026-05 / opt-in |
     |---|---|---|
     | Single bird | `simple-bird-skeleton.html` | `bird-skeleton.html` (with `--visual magazine`) |
     | Single frog | `simple-frog-skeleton.html` | `frog-skeleton.html` (with `--visual notebook`) |
     | Dual-tab | `simple-dual-tab-skeleton.html` | `dual-tab-skeleton.html` (with `--visual magazine,notebook`) |

   - **Single-style:** copy the skeleton, fill placeholders.
   - **Dual-tab:** fan out two parallel agent groups (see § Parallel sub-agents). Each group generates its half's body against its own skeleton, *without* the outer `<html>/<head>/<body>` boilerplate. The parent merges both bodies into the dual-tab shell — wrapper provides the tab bar, hash routing, namespaced CSS scopes, shared CDN deps.
   - **`--math` with simple:** add the KaTeX CDN block from the magazine shell to `<head>` and a `DOMContentLoaded` auto-render call before `</body>`.

6. **Open and hand off.** Run `open "<absolute-output-path>"`. Walk the lab QA (see § Interactive correctness). Print the absolute path on a line by itself in the final message.

## Hard constraints

- **Single HTML file.** All CSS/JS inlined or via CDN (when the visual permits); images base64 or pinned public CDN. No `_lib/` or local-asset references.
- **Fonts.** Simple → macOS system stack, zero external font URLs. Magazine → Google Fonts (Playfair + Cormorant + Inter + JetBrains Mono). Notebook → Google Fonts (Inter + JetBrains Mono). Don't mix.
- **Math.** Simple → KaTeX off by default; on with `--math` or when the source has `$$ … $$` (warn the user; don't silently load). Magazine / notebook → KaTeX on. Always CDN-deferred + `DOMContentLoaded` auto-render. **Never** use `<script ... onload="renderMathInElement(...)">`.
- **Code.** Simple → plain `<pre><code>` styled by inline CSS, no Prism. Magazine / notebook → Prism (light theme) or highlight.js via CDN. Pin the version.
- **Style sheets.** Inline `<style>` or (magazine / notebook) Tailwind CDN. **Bootstrap is banned.**
- **No build step.** No npm / vite / webpack.
- **Topic isolation.** Do not read other topic folders.
- **Online research is allowed.** Mark agent-added external content (magazine: `aside.external`; notebook / simple: clearly-labeled callout).
- **Pin CDN versions** (`katex@0.16.11`, `prismjs@1.29.0`). No `@latest`.
- **HTML already exists** → overwrite. Don't touch `_drafts/`.
- **Don't interrupt with questions.** When unsure, search web first. If still uncertain, write and mark with `<div class="uncertain">⚠ …</div>`.

**Dual-tab specifics:**
- **Slug contract.** Every cross-tab concept gets `id="bird-<slug>"` + `id="frog-<slug>"`. No per-section UI affordance — only the global tab bar.
- **CSS namespacing.** Rules from bird skeleton scoped under `.tab-bird`; frog skeleton under `.tab-frog`. Shared CDN deps load once at document level.
- **Narrow-screen rules.** Every template's `<style>` carries `@media (max-width:720px)` + `@media (max-width:480px)` blocks: (a) tab bar `white-space:nowrap; flex-shrink:0;` + `overflow-x:auto`; (b) code blocks `overflow-x:auto` + shrunk font; (c) section padding ≤14px at 720px, ≤12px at 480px; (d) tables `display:block; overflow-x:auto`; (e) lab controls stack vertically, `.lab canvas` `max-width:100%; height:auto`. Add narrow-screen rules for new components.

## Interactive correctness

Two failure modes show up: **blank canvas** and **blurry / stretched canvas**. Both skeletons bake the fixes in; if you hand-roll a lab, copy the same pattern.

1. **Render on init.** Every lab IIFE ends with one bare `draw()` call. Wrap each lab in `(function(){ const c = document.getElementById('…'); if (!c) return; … draw(); })();` so a missing element doesn't break the rest of the page.
2. **DPR-scale every canvas.** After `getContext('2d')`: `c.style.width = cssW + 'px'; c.style.height = cssH + 'px'; c.width = cssW * dpr; c.height = cssH * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);`.
3. **Lab-prefixed ids.** Two labs cannot share `r1` / `canvas-1`. Prefix with the lab name (`lab2-yaw`, `rsc-step`).
4. **Run the page locally before declaring done.** `open <output-dir>/<name>.html`, scroll to each lab, drag every slider, click every button. Fix blanks or dead controls before shipping.

## Self-audit (shared base)

Run alongside the style-specific checklist in the loaded pedagogy / visual specs.

**Writing**
- [ ] Cold open is **begin-with-why** (predicament + naive + fatal flaw + prior comparison). Not "overview of our method."
- [ ] Every new concept has a **worked example** with napkin-redoable numbers, preceding the abstraction.
- [ ] No paper-boilerplate phrases (本文 / 综上 / 不失一般性 / 显然地).
- [ ] AI 味自检: "不是 X，而是 Y" 对仗不超过 1–2 处; 没有"值得深思 / 综合来看 / 让我们一起 / 总而言之".
- [ ] No paragraph longer than 5–6 lines.
- [ ] Every new term gets a one-line intuition anchor before its definition.
- [ ] Recurring variables are color-coded; same hex across formulas, SVG, prose.

**Technical**
- [ ] Single HTML file. External deps pinned; no local-asset references.
- [ ] Every `<section>` / `<h2>` has an `id`. Internal links resolve.
- [ ] Every agent-added external content is marked.
- [ ] Every not-fully-digested spot has `<div class="uncertain">⚠ …</div>`.
- [ ] Every lab IIFE ends with `draw()`. Every canvas is DPR-scaled. Control ids are lab-prefixed.

**Visual-specific** (verify against the loaded visual spec)
- [ ] If `simple`: no `fonts.googleapis.com`; no `katex` / `prismjs` / `tailwindcss` / `highlight.js` (unless `--math`); warm-paper `:root` tokens present.
- [ ] If `magazine`: Google Fonts loads Playfair + Cormorant + Inter + JetBrains Mono; KaTeX + Prism present and pinned.
- [ ] If `notebook`: Google Fonts loads Inter + JetBrains Mono; KaTeX + Prism present and pinned.

**Dual-tab specific**
- [ ] Both tabs cover full source scope — neither is a fragment.
- [ ] Every cross-tab pair shares a `<slug>` with `bird-` / `frog-` prefix.
- [ ] No per-section "↔ 另一视角" jump buttons.
- [ ] Hash routing works: `#frog-<slug>` switches tab + scrolls.
- [ ] CSS scoped under `.tab-bird` / `.tab-frog`; no un-scoped rule leaks.
- [ ] If one half was force-filled, it was dropped in step 4. No half-empty tab shipped.
- [ ] Color-code palette consistent across tabs.

## Gotchas

- **Multiple PDFs in the folder** — ask the user; never default to the first.
- **KaTeX activation** — use `DOMContentLoaded`, never `<script ... onload="…">`. The latter fires mid-parse on long bodies and skips the still-being-parsed half of a dual-tab page. All three skeletons load KaTeX deferred and call `renderMathInElement` from `DOMContentLoaded` with `ignoredTags: ['pre','code',...]` and `throwOnError: false`.
- **`@latest` is forbidden.** Every CDN URL pins a stable version.
- **Don't leave silent TODO placeholders.** Fully write or mark `.uncertain`.
- **Worked-example pitfalls** — >5 steps = too big. No one-line takeaway = wrong example. Numbers not tiny (1, 2, 0, ½, π/4) = pick smaller.
- **Wrong-style trap** — Roman numeral inside frog or `In/Out` cell inside bird → re-check the user's request.
- **Don't mix style components silently** — magazine's `section.branch[data-accent]` and notebook's `.cell` / `.chalk` / `.nums` are not interchangeable.
- **Dual-tab principle violations** — (a) splitting coverage across tabs ("bird covers theory, frog covers implementation") = revert to single-style; (b) shipping a half-empty tab "because the default is dual-tab" = drop principle 3 violation, emit single-tab.
- **Slug drift** — if the bird side renames a section, the frog side's `id="frog-<slug>"` must update too. The slug map from the alignment outline is the source of truth.
- **Legacy aliases are honored.** Don't print warnings; don't try to "correct" the user. They exist for old project notes / chat history.
- **Mixing simple with paper-learning + LaTeX math** — simple has KaTeX off by default. Source with >2 `$$ … $$` blocks → pass `--math` or use `--visual magazine`.
- **Don't strip warm-paper CSS tokens.** They're the simple visual's identity.
- **Don't sneak Google Fonts into simple.** Even one "harmless" import for a "nicer" italic. Switch to magazine if you need Playfair.
- **Don't render Roman numerals under notebook** or `In [N]:` cells under magazine. Those markers are tied to their visuals.
- **Reading scale is 1.25×.** Every skeleton's `<style>` is pre-scaled — desktop column ≈1025px, body ≈21–22px, all paddings/headings/radii multiplied to match — so width and font grow together and chars-per-line is unchanged (this is why px values are fractional, e.g. `21.25px`; that's intentional, don't "round it back"). `@media` breakpoints stay at real-viewport px. Hand-rolled components must use the same scaled px (or `rem`/`em`/`%`) or they'll render small against the rest.

## See also

- [`references/pedagogy/principles.md`](references/pedagogy/principles.md) — 9 shared pedagogical principles. **Loaded on every invocation.**
- [`references/pedagogy/bird.md`](references/pedagogy/bird.md) · [`references/pedagogy/frog.md`](references/pedagogy/frog.md) — voice contracts.
- [`references/pedagogy/guests/`](references/pedagogy/guests/) — guest packs (active roster lives in § Guest packs above).
- [`references/visual/simple.md`](references/visual/simple.md) · [`references/visual/magazine.md`](references/visual/magazine.md) · [`references/visual/notebook.md`](references/visual/notebook.md) — visual contracts.
- [`templates/`](templates/) — six skeletons covering the (pedagogy, visual) matrix.
- Project-root `AGENTS.md` — reader profile, project-level hard constraints.
- `write-a-skill/SKILL.md` — authoring rules for editing this skill or adding new packs.
