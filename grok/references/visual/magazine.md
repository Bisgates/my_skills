# Visual · magazine (opt-in via `--visual magazine`)

Sunday-magazine longread on warm paper. Google Fonts + KaTeX + Prism are part of the identity — without them the layer reverts to a blog post.

Default skeleton: [`templates/bird-skeleton.html`](../../templates/bird-skeleton.html). Copy verbatim and fill placeholders.

The magazine visual is bird-pedagogy's classic rendering; pre-2026-05 it was the bird default. The `.feynman` class for the dark plum meta-insight callout is preserved (every prior generated HTML uses it).

## Identity tokens

- **Background:** warm paper (`#f4ecdd`) with a subtle dotted texture (two layered radial-gradients, 3px / 7px). Body sits on paper, never `#ffffff`.
- **Type stack:** Playfair Display 800 (display headings, body headings, drop caps, Roman numerals) + Cormorant Garamond italic (decorative italics, ampersand, signoff, sublines, hooks) + Inter (sans eyebrows, labels, metadata) + JetBrains Mono (math-box label, code, lab eyebrow). Don't substitute Source Serif 4 or Space Grotesk.

## Required components

Missing any of these and the artifact regresses to "text on a page."

1. **Masthead** — thin black-ruled top bar: italic Playfair logo left ("A Deep Understanding — Private Edition") + uppercase letterspaced volume info right.
2. **Hero on warm paper** (no dark gradient) — kicker → Playfair `<h1>` with one italic `<em>` and a warm-red `.ampersand` → italic Cormorant `.subline` → `.editor-note` framed by `border-top: 4px double` + `border-bottom: 1px` ink, with mono uppercase `.label` and italic Cormorant `.signoff` → optional `.hero-stats` row → `.meta-line` with black `.pill` chip and warm-red links.
3. **Top progress bar** — `position: fixed; top: 0; height: 2px;` ink color, fills as the reader scrolls.
4. **Right-fixed nav-dot rail** — hover reveals chapter label. Hidden under 1100px.
5. **Section opener per chapter** — `<section class="branch" data-accent="…">` with `<hr class="section-rule">` → `.section-head` (giant Roman numeral `I.`–`X.` 88px + `<h2>` with `<strong>` accent keyword + tiny mono `.branchcode`) → `<hr class="section-rule thin">` → `.ornament` glyph row (`§ · § · §` / `◊ · ◊ · ◊` / `¶ · ¶ · ¶`) → `.ch-hook` italic one-liner → `.lede` opening paragraph (drop cap fires automatically).
6. **Per-section accent rotation.** Each section carries `data-accent="red|indigo|forest|amber|plum|slate"`. Pick semantically — `red` for problem/results/limits, `indigo` for the core insight and joint-training math, `forest`/`amber`/`plum`/`slate` for parallel topical chapters. When the source has color-coded variables, match the chapter accent to the dominant variable's color. Don't run two consecutive sections with the same accent.
7. **Callout matrix** — at least 3 of: `.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`. At least one `.feynman` (the meta-reflection beat).
8. **Math box triple** — `<div class="math-box"><div class="math-label">…</div>$$…$$<div class="math-note">…</div></div>`.
9. **Worked example** — `.worked-example` block per new concept (`we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`).
10. **Naive vs. insight `.compare`** — two-column grid, naive left, source solution right. At least one per HTML.
11. **Figures** — 1–2 SVG / CSS / emoji conceptual diagrams. Source figures embedded as base64 when relevant. "Figure missing" is not acceptable.
12. **Lab block** — `.lab` container with `Field Study · Lab N · <name>` title in Inter caps + reveal line + DPR-scaled canvas + `.ctrl-row` + `.btn-row` + `.lab-note`.
13. **Timeline** (when source sits in a clear lineage) — historical chain with latest item flagged `.tl-item.highlight`.
14. **Comparison table** — paper-soft body + ink header bar; mark the source's own row with `tr.ours-row`.
15. **`aside.external`** — every agent-sourced external addition, marked.
16. **Pull quote `.pullquote`** — at least one distilled punch-line, attributed via `.who`.
17. **Editorial divider `· · ·`** — chapter end, accent-colored at 0.6 opacity. Never `<hr>`.
18. **Afterword** — ink-bordered paper-soft kicker box near the end, with Inter mono `.label`, italic Playfair h4, short bullet list of "what I chose / what I excluded" (and, under bird voice, the page-wide meta-reflection).
19. **Colophon footer** — three columns (Citation / Resources / Colophon), italic Cormorant body, tiny Inter-mono uppercase `<h5>` headers.

## Component vocabulary

| Class / element | Purpose | Notes |
|---|---|---|
| `.masthead` `.logo` | Top thin-ruled magazine bar | Italic Playfair logo left, mono uppercase volume info right |
| `.hero` `.kicker` `h1 em` `h1 .ampersand` `.subline` | Editorial hero on warm paper | No dark gradient. Italic `<em>` + warm-red `.ampersand` separator |
| `.editor-note` `.label` `.signoff` | Hero contract block | `border-top: 4px double` + `border-bottom: 1px` ink rules |
| `.hero-stats` `.v` `.l` | Optional headline-number row | Big serif value + tiny mono caption |
| `.hero .meta-line` `.pill` | Authors / venue / links row | Black `pill` chip + warm-red `<a>` |
| `#progress` | Top 2px scroll progress bar | Fixed; width tracks scroll fraction; ink color |
| `#rail .dot` | Right-side nav-dot rail | Hover reveals uppercase mono label |
| `section.branch[data-accent]` | Editorial section opener | Accent ∈ {`red`,`indigo`,`forest`,`amber`,`plum`,`slate`} drives `--accent` |
| `.section-rule` `.section-rule.thin` | 7px top + 1px under-rule | Both colored by `--accent` |
| `.section-head .numeral` `.titles h2 strong/em` `.branchcode` | Big Roman numeral + h2 + tiny code | Numeral in 88px Playfair 900; branchcode in mono uppercase |
| `.ornament` | Italic glyph row | Rotate glyph between consecutive chapters |
| `.ch-hook` | Italic Cormorant one-liner under section opener | |
| `.lede` | Opening paragraph with drop cap | First letter floats at 80px, colored by `--accent` |
| `.branch h3` `.marker` | Sub-heads inside chapters | Playfair 700 + small mono `§ X.Y` marker |
| `.pullquote` `.who` | Inline italic punch-line | 6px accent left-border, paper-soft accent-tinted bg, attribution mono caps |
| `.math-box` `.math-label` `.math-note` | Math triple | Inter-caps label + LaTeX + italic Cormorant note |
| `.worked-example` `.we-label` `.we-setup` `.we-steps` `.we-takeaway` | Per new concept | `we-label` in Inter caps |
| `.insight` `.danger` `.success` `.warning` `.definition` | 5-color semantic callouts | Paper-soft fills; inner `<span class="label">` in Inter caps |
| `.feynman` `.attribution` | Dark plum-bordered meta-insight card | Hosts the bird pack's meta-reflection beat |
| `.compare > .naive` `.compare > .insight-card` | Naive vs. source-solution two-col | Sharp-corner paper-soft cards with mono `.label` eyebrow |
| `.lab` `.lab-title` `.lab-reveal` `.ctrl-row` `.btn-row` `.lab-note` | Interactive sandbox | Title `Field Study · Lab N · …`; reveal line mandatory |
| `.step-dots .d.active/.done` | Multi-step algorithm state indicator | |
| `table` `th` `td.num.win/.lose` `tr.ours-row` | Editorial table | Ink header bar + paper-soft body, mono numerics |
| `.timeline` `.tl-item.highlight` `.tl-dot` `.tl-year` `.tl-title` `.tl-desc` | Historical lineage | Highlight item turns warm-red |
| `aside.external` | Agent-sourced external addition | Self-labels "外部补充 · agent" + warm-red links |
| `.uncertain` | Not-fully-digested marker | Lead with `⚠` |
| `.v-x` `.v-y` `.v-z` `.v-b` | Color-coded variables | Same hex used in formulas / SVG / inline prose |
| `.topic-a/b/c` | Per-topic accent stripe | Only when source has 2–3 parallel concepts |
| `.ch-end` `· · ·` | Chapter divider | Accent-colored at 0.6 opacity; never `<hr>` |
| `.afterword` `.label` `h4` | End-of-article kicker box | Ink-bordered paper-soft frame |
| `.colophon` `.col` `h5` | Three-column footer | Italic Cormorant body + tiny Inter mono caps headers |

## Visual self-audit

- [ ] Body type is **Playfair Display + Cormorant Garamond**; callout / hero / branchcode labels in **Inter caps**; math-box / lab / code in **JetBrains Mono**. No Source Serif 4 or Space Grotesk leftovers.
- [ ] Google Fonts URL loads Playfair + Cormorant + Inter + JetBrains Mono. KaTeX + Prism (light theme) present and pinned.
- [ ] **Masthead** present (italic logo + uppercase letterspaced volume info).
- [ ] **Hero on warm paper** (no dark gradient), with all sub-elements.
- [ ] Each chapter is `<section class="branch" data-accent="…">` with section-rule → numeral → `<h2>` with `<strong>` keyword → `.branchcode` → section-rule.thin → ornament. No bare `.chapter` blocks.
- [ ] **`.lede`** opens each chapter with a drop cap colored by `--accent`.
- [ ] **At least one `.pullquote`** with `.who` attribution.
- [ ] **`.afterword`** and **`.colophon`** present.
- [ ] **At least 3 different callout types** in use.
- [ ] **At least one `.feynman`** hosts the meta-reflection beat.
- [ ] Chapter accents rotate semantically.
- [ ] Chapter dividers use `· · ·` accent-colored at 0.6 opacity. Never `<hr>`.

## Gotchas

- **Don't drift to the old `.chapter` pattern.** Magazine uses `section.branch[data-accent]` with section-rule openers. The IntersectionObserver observes `section.branch`.
- **Don't abuse callouts as paragraph wrappers.** One sentence or one proposition per callout, not five paragraphs.
- **Don't over-do cross-domain transfer** (one or two per page lands; five turns the page into name-dropping).
- **Per-topic accent stripes only with 2–3 parallel core concepts.** Otherwise a single `--accent` is enough.

## Reference exemplars

- `~/project/what_new/weekly/2026-19.html` — canonical masthead + hero + section-rule pattern.
- `~/project/learn_with_agent/260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — full 10-section long-read.
- `~/project/learn_with_agent/260514/fabu_clip_drivestudio_training.html` — 10-chapter codebase walkthrough.
