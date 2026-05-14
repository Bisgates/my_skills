# Style pack · bird (default visual: magazine longread)

Pedagogical posture: **top-down, abstraction-first, derived from first principles**. The single lineage is Richard Hamming — *The Art of Doing Science and Engineering* (a 30-lecture series, transcribed) is the canonical reference. Hamming's signature move: **open with the question behind the question, strip away the details, derive the method from the goal, then close with the principle worth remembering when the details fade**.

The name "bird" follows Freeman Dyson's *Birds and Frogs*: a bird flies high, sees broad patterns, and unifies ideas across the landscape. This is the page voice — broad reach, top-down framing, comfortable across many domains because it always lifts the question first.

The visual is a Sunday magazine feature — a long-form essay where a careful editor walks the reader from "why the field was stuck" to "and here is the structural move that unstuck it," in a single seven-thousand-word arc.

Default skeleton: [`templates/bird-skeleton.html`](../../templates/bird-skeleton.html) (~710 lines, magazine layout). Copy verbatim and fill placeholders; do not hand-roll.

> The `.feynman` CSS class for the dark plum meta-insight callout card is **preserved** for backward compatibility (every prior generated HTML uses it). It names a UI element, not the pedagogical posture — the class is fine to keep using under the bird pack for any "step-back-and-reflect" beat.

## Voice (the bird delta)

- **Question-first.** Before showing how a method works, surface the question the method actually answers. "What are we really trying to accomplish here?" / "What's the question behind the question?" is the canonical opening beat. Hamming spent the first ten minutes of most of his lectures here; the page does the same.
- **Top-down decomposition.** State the goal → state the constraints → derive the method as the unique (or near-unique) thing that satisfies them. The reader watches the method *fall out of* the constraints, not get *announced* as a clever idea someone had.
- **Asymptotic / extreme-case lever.** Push a parameter to 0 or ∞ and see what the algorithm degenerates to. The shape of the limit reveals the structure of the general case. This is a Hamming reflex (digital filters → 0-bandwidth, error codes → 0 noise, neural nets → 1 example) and it earns its place in any bird-style chapter.
- **Cross-domain transfer.** "The same trick appears in [other field] because [abstract reason]." Hamming's hallmark — he constantly mapped coding theory ↔ digital filters ↔ probability ↔ early neural nets to one underlying principle. Use it sparingly but use it; nothing else makes a bird page feel as expansive.
- **Physical / mechanical intuition anchors.** Every abstract symbol gets a concrete metaphor before its formula. "Score function = uphill direction." "Z = volume integral over all of space." "Channel capacity = the rate at which surprise can pass through a pipe."
- **Meta-reflection close.** Each major section ends with a short "what's the principle to remember when the details fade?" beat — a pull-quote, an italic afterword paragraph, or a final `.feynman` block. This is the move that makes a Hamming lecture *rewatchable*.
- **Long-form rhythm.** Magazine pacing — alternate long reasoning paragraphs with one-line breath punches. Pull-quotes interrupt the body. The drop cap and the editor-note set the contract.

## Visual contract — warm-paper magazine

Reads like a Sunday-magazine longread typeset, not Markdown rendered to HTML.

- **Warm paper background** (`#f4ecdd`) with a subtle dotted texture (two layered radial-gradients, 3px / 7px). Body type sits on the paper, never on `#ffffff`. Hero is **not** a dark gradient — it sits on the same paper as the body, just with bigger typography.
- **Type stack**: Playfair Display 800 (display headings, body headings, drop caps, Roman numerals) + Cormorant Garamond italic (decorative italics, ampersand, signoff, sublines, hooks) + Inter (sans eyebrows / labels / metadata) + JetBrains Mono (math-box label, code, lab eyebrow). The display serif stays italic-leaning; do not substitute Space Grotesk or Source Serif 4.
- **Masthead**: a thin black-ruled bar at the top. Left = italic logo ("A Deep Understanding — Private Edition") in Playfair italic; right = volume info in uppercase letterspaced Inter (`letter-spacing: 0.18em`).
- **Hero**: kicker (warm-red, uppercase letterspaced Inter, 12px) → big Playfair `<h1>` 72px with one italic `<em>` for the subtitle phrase and an italic warm-red ampersand for separation → `.subline` (italic Cormorant, 22px) → `.editor-note` framed by `border-top: 4px double` + `border-bottom: 1px` of ink, with a mono uppercase `.label` and an italic Cormorant `.signoff` (e.g. "— 编于周日 22:30，配茶"). Optional `.hero-stats` row + `.meta-line` with a black `.pill` chip and a couple of warm-red links.
- **Section opener (`section.branch`)** is the magazine's signature element. Each section carries `data-accent="red|indigo|forest|amber|plum|slate"`. The accent drives a 7px-thick `<hr class="section-rule">`, the giant Playfair Roman numeral (`I.`–`X.`, 88px), an `<h2>` with one `<strong>` keyword in the accent color, a tiny mono `.branchcode` (e.g. `chapter_3 · articulated humans`), a 1px `<hr class="section-rule thin">`, and an `.ornament` row of glyphs (`§ · § · §` / `◊ · ◊ · ◊` / `¶ · ¶ · ¶`) centered in italic Playfair. Rotate the ornament glyph between consecutive chapters to keep rhythm.
- **Per-section accent rotation**: pick the chapter accent semantically — `red` for problem / results / limits, `indigo` for the core insight chapter and joint-training math, `forest`/`amber`/`plum`/`slate` for parallel topical chapters (when the source has color-coded variables, match the chapter accent to the dominant variable's color so a reader keys both at once). Don't run two consecutive sections with the same accent unless deliberate.
- **Body**: `.lede` first paragraph in Playfair 21px with a giant accent-colored drop cap (80px, floats left). Subsequent paragraphs return to serif reading at 17px / 1.74. Sub-heads `<h3>` use Playfair 700, 23px, with a small mono `.marker` (e.g. `§ 3.2`) prepended.
- **Pull quote `.pullquote`**: paper-soft accent-tinted background, 6px left-border in the accent color, Playfair italic 26–28px. Attribution lives in `.who` (Inter uppercase 12px, letterspaced).
- **Callout matrix** (`.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`) keeps its 6 semantic colors but moves to paper-soft fills (no white surfaces); labels are uppercase letterspaced **Inter**, not mono — eyebrows in the body switch font systematically (sans for callout labels, mono for math/lab/eyebrow). The `.feynman` block stays a dark plum-bordered card with white italic Cormorant text and an oversized `"` glyph; use it for the meta-reflection close described under Voice.
- **Math box**: paper-soft fill with a 3px accent left-border. Label in Inter uppercase letterspaced. Math-note in italic Cormorant 15px.
- **Worked example**: paper-soft fill with a 6px **double**-style accent left-border. `we-label` in Inter uppercase. `we-setup` in italic Cormorant. `we-takeaway` keeps the 📌 prefix on a small white pill.
- **Compare cards `.compare > .naive` / `.compare > .insight-card`**: paper-soft fills, no rounded corners, 3px top-border in muted vs. accent. Labels in Inter caps; titles in Playfair 18 700.
- **Tables**: ink-black header bar + paper-soft body. Header text in Inter caps 11px letterspaced. Body cells in Cormorant 15. Numerics in JetBrains Mono right-aligned. `.num.win` in forest, `.num.lose` in muted. `tr.ours-row` gets a forest-tinted highlight.
- **Lab block**: paper-soft container with a 3px accent top-border. `.lab-title` reads `Field Study · Lab N · <name>` in Inter caps. The reveal line stays mandatory. Buttons are flat ink-on-paper, sharp corners, Inter caps. `.btn.toggle.on` flips to the section's accent.
- **Timeline**: dotted hairline rail; dots are accent-colored discs ringed by `box-shadow: 0 0 0 2px var(--accent)`. Year in mono caps, title in Playfair 700, desc in Cormorant.
- **Aside.external**: paper-soft fill with mono uppercase eyebrow ("外部补充 · agent") and warm-red links.
- **Afterword**: an ink-bordered paper-soft "kicker box" near the end of the article — Inter mono label, Playfair italic h4, serif body. Use it for "what I chose / what I excluded" — and in the bird pack, also for the page-wide meta-reflection ("the principle worth remembering when the details fade").
- **Colophon footer**: italic Cormorant on warm paper, three columns (Citation / Resources / Colophon), each with a tiny Inter-mono uppercase `<h5>`.
- **Chapter divider**: `· · ·` centered, accent-colored at 0.6 opacity.
- **Forbidden**: dark gradient hero, bootstrap-feeling rounded cards, single-column Markdown renders, sans-serif body type, `#ffffff` page background, Source Serif 4 / Space Grotesk substitutions.

## Required components — checklist

Every bird/magazine HTML must include the following — missing any of them and the artifact regresses to "text on a page":

1. **Masthead** — thin black-ruled top bar: italic Playfair logo left ("A Deep Understanding — Private Edition") + uppercase letterspaced volume info right.
2. **Hero on warm paper** (no dark gradient) — kicker → big Playfair `<h1>` with one italic `<em>` and a warm-red ampersand → italic Cormorant `.subline` → `.editor-note` framed by double-rule + thin-rule with `.label` and `.signoff` → optional `.hero-stats` row → `.meta-line` with `.pill` chip and warm-red links.
3. **Top progress bar** — `position: fixed; top: 0; height: 2px;` ink color, fills as the reader scrolls.
4. **Right-fixed nav-dot rail** — hover reveals chapter label. Hidden under 1100px. (Sections use `section.branch`, not `section.chapter`.)
5. **Section opener per chapter** — `<section class="branch" data-accent="…">` followed by `<hr class="section-rule">` → `.section-head` (giant Roman numeral + `<h2>` with `<strong>` keyword + tiny `.branchcode`) → `<hr class="section-rule thin">` → `.ornament` glyph row → `.ch-hook` italic one-liner → `.lede` opening paragraph (drop cap fires automatically). Rotate `data-accent` per chapter; never run two consecutive sections with the same accent unless deliberate.
6. **Callout matrix** — at least 3 of: `.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`. At least one `.feynman` per page in the bird pack — that's where the meta-reflection beat lives.
7. **Math box triple** — `<div class="math-box"><div class="math-label">…</div>$$…$$<div class="math-note">…</div></div>`.
8. **Worked example** — a `.worked-example` block per new concept (`we-label` + `we-setup` + numbered `we-steps` + 📌 `we-takeaway`).
9. **Naive vs. Insight comparison** — `.compare` two-column grid, naive on left, the source's solution on right; at least one per HTML.
10. **Figures** — at least 1–2 SVG / CSS / emoji-composed conceptual diagrams. **Source figures embedded as base64 (or pinned-CDN external images wrapped in `aside.external`) when clearly relevant**. "Figure missing" is not acceptable.
11. **Lab block** — `.lab` container with `Field Study · Lab N · <name>` title in Inter caps + reveal line + canvas (DPR-scaled) + `.ctrl-row` + `.btn-row` + `.lab-note`.
12. **Timeline** (strongly recommended when the source sits in a clear lineage) — historical chain with the latest item flagged `.tl-item.highlight`.
13. **Comparison table** — paper-soft body + ink header bar; mark the source's own row with `tr.ours-row`.
14. **`aside.external`** — every agent-sourced external addition, marked.
15. **Pull quote `.pullquote`** — at least one distilled punch-line, attributed via `.who`.
16. **Editorial divider `· · ·`** — chapter end, accent-colored at 0.6 opacity.
17. **Afterword** — ink-bordered paper-soft kicker box near the article end, with Inter mono `.label`, italic Playfair h4, and a short bullet list of "what I chose / what I excluded" (and, in the bird pack, often the page's meta-reflection close).
18. **Colophon footer** — three columns (Citation / Resources / Colophon) on warm paper, italic Cormorant body, tiny Inter-mono uppercase `<h5>` headers.

## CSS class quick reference

| Class / element | Purpose | Notes |
|---|---|---|
| `.masthead` `.logo` | Top thin-ruled magazine bar | Italic Playfair logo left, mono uppercase volume info right |
| `.hero` `.kicker` `h1 em` `h1 .ampersand` `.subline` | Editorial hero on warm paper | No dark gradient. `<em>` italic + warm-red `.ampersand` separator |
| `.editor-note` `.label` `.signoff` | Hero contract block | `border-top: 4px double` + `border-bottom: 1px` ink rules |
| `.hero-stats` `.v` `.l` | Optional headline-number row | Big serif value + tiny mono caption |
| `.hero .meta-line` `.pill` | Authors / venue / links row | Black `pill` chip + warm-red `<a>` |
| `#progress` | Top 2px scroll progress bar | Fixed; width tracks scroll fraction; ink color (low saturation) |
| `#rail .dot` | Right-side nav-dot rail | Hover reveals uppercase mono label |
| `section.branch[data-accent]` | Editorial section opener | Accent ∈ {`red`,`indigo`,`forest`,`amber`,`plum`,`slate`} drives `--accent` |
| `.section-rule` `.section-rule.thin` | 7px top + 1px under-rule | Both colored by `--accent` |
| `.section-head .numeral` `.titles h2 strong/em` `.branchcode` | Big Roman numeral + h2 + tiny code | Numeral in 88px Playfair 900; branchcode in mono uppercase |
| `.ornament` | Italic glyph row (`§ · § · §`) | Rotate glyph between consecutive chapters |
| `.ch-hook` | Italic Cormorant one-liner under section opener | Replaces the old `.ch-hook` border style |
| `.lede` | Opening paragraph with drop cap | First letter floats at 80px, colored by `--accent` |
| `.branch h3` `.marker` | Sub-heads inside chapters | Playfair 700 + small mono `§ X.Y` marker |
| `.pullquote` `.who` | Inline italic punch-line | 6px accent left-border, paper-soft accent-tinted bg, attribution in mono caps |
| `.math-box` `.math-label` `.math-note` | Math triple | Inter-caps label + LaTeX + italic Cormorant note |
| `.worked-example` `.we-label` `.we-setup` `.we-steps` `.we-takeaway` | Concrete numerical walkthrough | Required per new concept; `we-label` in Inter caps |
| `.insight` `.danger` `.success` `.warning` `.definition` | 5-color semantic callouts | Paper-soft fills; inner `<span class="label">` in Inter caps |
| `.feynman` `.attribution` | Dark plum-bordered meta-insight card | Hosts the bird pack's meta-reflection beat — Hamming's "what's the principle worth remembering when the details fade" |
| `.compare > .naive` `.compare > .insight-card` | Naive vs. source-solution two-col | Sharp-corner paper-soft cards with mono `.label` eyebrow |
| `.lab` `.lab-title` `.lab-reveal` `.ctrl-row` `.btn-row` `.lab-note` | Interactive sandbox | Title reads `Field Study · Lab N · …`; reveal line mandatory |
| `.step-dots .d.active/.done` | Multi-step algorithm state indicator | For sequenced demos |
| `table` `th` `td.num.win/.lose` `tr.ours-row` | Editorial table | Ink header bar + paper-soft body, mono numerics |
| `.timeline` `.tl-item.highlight` `.tl-dot` `.tl-year` `.tl-title` `.tl-desc` | Historical lineage | Highlight item turns warm-red |
| `aside.external` | Agent-sourced external addition | Self-labels with "外部补充 · agent" + warm-red links |
| `.uncertain` | Not-fully-digested marker | Lead with `⚠` |
| `.v-x` `.v-y` `.v-z` `.v-b` | Color-coded variables | Same hex used in formulas / SVG / inline prose |
| `.topic-a/b/c` | Per-topic accent stripe | Only when source has 2–3 parallel concepts |
| `.ch-end` `· · ·` | Chapter divider | Accent-colored at 0.6 opacity; never `<hr>` |
| `.afterword` `.label` `h4` | End-of-article kicker box | Ink-bordered paper-soft frame; for "what I chose / excluded" + page-wide meta-reflection |
| `.colophon` `.col` `h5` | Three-column footer | Italic Cormorant body + tiny Inter mono caps headers |

## Style-specific self-audit (run with the shared base in SKILL.md)

**Voice / writing**
- [ ] Cold open lifts to the **meta-question** ("what are we really trying to accomplish?" / "what's the question behind the question?") before any method is shown.
- [ ] Method is **derived from goal + constraints**, not announced as someone's clever idea.
- [ ] At least one **asymptotic / extreme-case** observation per page (push a parameter to 0 or ∞ and read off what degenerates).
- [ ] At least one **cross-domain transfer** observation per page, even briefly ("this also shows up in X because Y").
- [ ] Each major section closes with a short **meta-reflection** beat — pull-quote, `.feynman` card, or italic afterword paragraph. The page's final `.afterword` carries the page-wide meta-reflection.
- [ ] No "本文 / 综上 / 不失一般性 / 显然地"-style paper-boilerplate phrases.

**Visual / components**
- [ ] **Masthead** present (italic logo + uppercase letterspaced volume info, divided by 1px ink rule).
- [ ] **Hero on warm paper** (`#f4ecdd` body + dotted texture, no dark gradient): kicker + Playfair `<h1>` with `<em>` + ampersand + Cormorant `.subline` + `.editor-note` (with double-rule + thin-rule frame, `.label`, `.signoff`).
- [ ] Each chapter is `<section class="branch" data-accent="…">` with **section-rule (7px) → numeral (`I.`–`X.`) → `<h2>` with `<strong>` accent keyword → `.branchcode` → section-rule.thin → ornament**. No bare `.chapter` blocks left over from the old skeleton.
- [ ] **`.lede` opens each chapter** with a drop cap colored by `--accent`. Subsequent paragraphs in serif at 17 / 1.74.
- [ ] **At least one `.pullquote`** with `.who` attribution.
- [ ] **`.afterword`** (ink-bordered kicker box) and **`.colophon`** (three-column italic footer) present.
- [ ] **At least 3 different** callout types in use (not the entire page in `.insight`).
- [ ] **At least one `.feynman` card** hosts the per-section or page-wide meta-reflection beat.
- [ ] If the source sits in a clear lineage, a `.timeline` is present (latest item flagged `.tl-item.highlight`).
- [ ] Body type is **Playfair Display + Cormorant Garamond**; **callout / hero / branchcode labels in Inter caps**; **math-box / lab / progress / code in JetBrains Mono**. No Source Serif 4 or Space Grotesk leftovers.
- [ ] Chapter accents rotate semantically; no two consecutive sections share an accent unintentionally.
- [ ] Chapter dividers use `· · ·`, accent-colored at 0.6 opacity. Never `<hr>` for divider purposes.

## Style-specific gotchas

- **Don't drift back to the old `.chapter` pattern** — the magazine theme uses `section.branch[data-accent]` with section-rule openers. Old `<section class="chapter">` with `.ch-num` / `.ch-title` / `.lead` is deprecated. The IntersectionObserver in the skeleton observes `section.branch` — keep that selector.
- **Don't abuse callouts as paragraph wrappers** — a callout is to highlight one sentence or one proposition, not to box up five paragraphs of body text.
- **Don't skip the meta-reflection close** — without it, the bird pack collapses back into "long magazine essay" and loses the Hamming signature. If you can't extract a one-line "principle worth remembering" for a section, the section is probably reporting facts rather than uncovering structure.
- **Don't over-do cross-domain transfer** — one or two per page lands; five turns the page into a name-dropping exercise. Each transfer must carry its weight with the *abstract reason* the same trick reappears, not just the fact that it does.
- **Per-topic accent stripes** — only use `topic-a/b/c` when the source genuinely has 2–3 parallel core concepts (PSNR/SSIM/LPIPS, Score/Langevin/Denoising, …). Otherwise a single `--accent` is enough.

## Reference exemplars (visual ground truth)

- `~/project/what_new/weekly/2026-19.html` — canonical masthead + hero + section-rule pattern; this is the look grok imports.
- `~/project/learn_with_agent/260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — full long-read application: 10-section long-read with accent rotation across red / indigo / slate / amber / plum / forest, three labs (DPR-scaled), afterword, colophon.
- `~/project/learn_with_agent/260514/fabu_clip_drivestudio_training.html` — recent example: 10-chapter codebase walkthrough on FABU/DriveStudio.

## Voice exemplar (Hamming, primary reference)

- Richard Hamming, *The Art of Doing Science and Engineering: Learning to Learn* — 30 lectures given at the Naval Postgraduate School, 1995. The book is the reference text for this pack's voice; the "meta-question first → strip the noise → derive the method from the goal → close with the principle to remember when details fade" arc is taken from it directly. When in doubt about how to open or close a section, re-read one of Hamming's chapters (any of "Coding Theory," "Digital Filters," "Simulation," or "You and Your Research" lands the cadence cleanly).
