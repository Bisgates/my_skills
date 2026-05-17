# Visual layer · simple (default)

**Note.** `bird.md` and `frog.md` describe **pedagogical postures** (how the page reasons). This file describes a **visual layer** (how the page looks). The two axes are orthogonal: a bird page can render under simple *or* magazine; a frog page can render under simple *or* notebook. Pedagogy is the primary identity. The visual is its rendering.

The `simple` visual is the new default for both `bird` and `frog`. Magazine (Google-Fonts-rich, paper-learning) is opt-in via `--visual magazine`. Notebook (Jupyter, code-walkthrough) is opt-in via `--visual notebook`.

## When to use simple (and when not)

- **Pick simple** for investigative reports, technical explainers, codebase walkthroughs, any source where the reader's value is the prose + the worked examples, not typographic richness. Simple is the right choice when you'd rather the reader notice the reasoning than the page.
- **Pick simple** when the artifact will be read on flaky network — a CDN-free single file double-clicks open in 0 ms forever.
- **Pick magazine** when the source is a paper with formulas worth rendering, the audience expects a Sunday-magazine longread feel, and the math identity is part of the artifact's value. KaTeX + Playfair + Cormorant are baked into magazine; they aren't decoration there, they're the layer.
- **Pick notebook** when the source is code-heavy and the page's spine is `In [N]:` / `Out[N]:` cells — Karpathy spelled-out-from-scratch register specifically.
- For dual-tab default (no `--visual`), both tabs render under simple — the bird tab gets bird's simple sub-style (magazine-flavored components, warm paper, system serif), the frog tab gets frog's simple sub-style (notebook cells, warm paper, system mono).

## Pedagogical posture

The simple visual does **not** override the pedagogy. A bird page under simple still opens with the meta-question, derives the method from the goal, closes with the principle to remember. A frog page under simple still leads with a code cell + output cell, stops to think, builds bottom-up. The simple layer carries those moves with a different visual register — quieter typography, no external assets — but it keeps the same teaching arc.

## Hard constraints — what makes simple "simple"

- **No Google Fonts.** Body type is the macOS system serif stack. Mono is the macOS system mono stack. The CSS contains exactly zero external font URLs.
- **No external CDN at all by default.** No KaTeX, no Prism, no Tailwind, no highlight.js. Code blocks render as plain `<pre>` styled by the inline CSS; math is rendered as plain Unicode + sub/superscript HTML, or skipped.
- **KaTeX is opt-in.** If the source has heavy LaTeX (`$$ ... $$` or `\(...\)`), pass `--math` or rerun with `--visual magazine`. Simple will not auto-load KaTeX silently — silent CDN dependency defeats the layer's value.
- **All CSS inline** in one `<style>` block in `<head>`. All JS inline in one `<script>` block before `</body>`.
- **Warm paper color tokens** (see below) — not white, not slate. The palette is the visual identity; don't strip it.

## Color tokens (CSS custom properties)

Copy these into the `:root` block verbatim. Both bird-simple and frog-simple share the same tokens — only their component styles differ.

```css
:root {
  --paper:     #fbf6e9;   /* page background, warm pulp */
  --paper-2:   #f3ebd6;   /* tab bar / secondary surface */
  --ink:       #1f1a14;   /* body text */
  --ink-soft:  #3b332a;   /* headings, decks */
  --ink-faint: #6b6052;   /* meta, captions, footers */
  --rule:      #b8a583;   /* solid rules */
  --rule-soft: #d8c9a2;   /* hairlines, table rows */
  --accent:    #8c2f1c;   /* warm-red — bird chapter numerals, drop caps, active tab */
  --accent-2:  #2c5340;   /* deep green — frog code-cell border, stop-and-think callout */
  --gold:      #a37c2a;   /* amber — frog output-cell border, magazine ornaments */
  --quote-bg:  #f0e6cd;   /* pull-quote tint */
  --code-bg:   #efe6ce;   /* inline code, pre */
  --code-fg:   #1a140d;   /* code text */
}
```

## Font stacks

```css
/* serif body — bird and most prose */
font-family: -apple-system, "Iowan Old Style", "Charter", "Cormorant Garamond", "Playfair Display", Georgia, "Times New Roman", serif;

/* mono — code, cell prompts, labels */
font-family: ui-monospace, "SF Mono", Menlo, Monaco, "Cascadia Mono", Consolas, "Liberation Mono", "Courier New", monospace;
```

Frog-simple keeps the same serif stack for body prose (notebook narration reads better in serif on macOS than in sans on retina). Cell prompts, code, and labels go mono. If a sans is needed for a meta label in either sub-style, fall back to `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` — never load Inter from a CDN.

## bird-flavored simple — required components

The bird pedagogy lands through a magazine-influenced but plain-paper layout. Required components (all CSS class names live under `.tab-bird` when used inside the dual-tab shell):

| Component | DOM shape | Purpose |
|---|---|---|
| `.masthead` | `<header class="masthead">` with `.kicker` (small-caps, accent color), `<h1>` (system serif, 44px), `.deck` (italic, ink-soft), `.byline` (uppercase letterspaced, 12px ink-faint) | Hero. Border-top 4px double `--rule`, border-bottom 1px `--rule`. Replaces magazine's editor-note. |
| `.chapter-rule` | `<div class="chapter-rule"><span class="roman">I · <chapter name></span></div>` | Roman-numeral chapter opener. Center-aligned, small-caps, accent color, padded between two 1px rules. Replaces magazine's section-rule + numeral block. |
| `.chapter-title` | `<h2 class="chapter-title" id="bird-<slug>">…</h2>` | Italic system serif, 26px, ink color. Sits directly under chapter-rule. |
| `.lede` | `<p class="lede">…</p>` (first paragraph after chapter-title) | Carries the drop cap. `::first-letter` floats left, 4.4em, accent color. |
| `h3` | small-caps system serif, letter-spaced 0.08em, ink-soft, with 1px bottom hairline | Sub-heads inside chapters. |
| `.callout` | `<div class="callout"><div class="ctitle">…</div><p>…</p></div>` | 3px accent left-border, paper-2 tint background. ctitle is small-caps accent 12px. |
| `.pull` | `<div class="pull">…</div>` (optionally with attribution below) | Centered italic pull-quote, accent-2 color, top + bottom 1px rule-soft hairlines. |
| `.matrix` | `<div class="matrix"><div class="cell"><div class="h">…</div>body</div>…</div>` | 2-column grid of comparison cards. Each cell has 1px `--rule` border, paper-2 background. |
| `pre code` | `<pre><code>…</code></pre>` | `--code-bg` background, 3px gold left-border. No Prism. |
| `table` | thin top/bottom `--rule-soft` row borders, accent-color small-caps `th` | Body cells in serif, numerics in mono. |

Optional: `.afterword` (ink-bordered paper-2 kicker), `.timeline` (dotted hairline rail, accent-color discs). Both inherit the simple palette.

**The drop cap and the Roman-numeral chapter openers are non-negotiable in bird-simple.** Without them the page reverts to "blog post on system fonts" and loses the magazine pedagogy markers.

## frog-flavored simple — required components

The frog pedagogy lands through notebook-influenced cells but on the same warm paper, with system fonts. Required components (under `.tab-frog` when in the dual-tab shell):

| Component | DOM shape | Purpose |
|---|---|---|
| `.nb-head` | `<header class="nb-head"><div class="stamp">…</div><h1>…</h1><div class="sub">…</div></header>` | Notebook title block. `stamp` is mono 12px ink-faint. `h1` 30px system serif. `sub` italic ink-soft. Border-bottom 2px ink-soft. |
| `h2.section` | `<h2 class="section" id="frog-<slug>"><span class="num">[N]</span> section name</h2>` | Mono small-caps accent-2. `num` is `[1]` / `[2]` / etc in mono 12px ink-faint. 1px `--rule` bottom border. NOT Roman numerals (those belong to bird). |
| `.cell.md` | `<div class="cell md"><div class="label">In [md]:</div><p>…</p></div>` | Markdown / narration cell. 4px `--rule` left-border. Label mono 11px ink-faint. |
| `.cell.code` | `<div class="cell code"><div class="label">In [N]:</div><pre><code>…</code></pre></div>` | Input cell. 4px `--accent-2` left-border. `<pre>` on `--code-bg` background. |
| `.cell.out` | `<div class="cell out"><div class="label">Out [N]:</div><pre>…</pre></div>` | Output cell. 4px `--gold` left-border. `<pre>` transparent background, ink-soft text. |
| `.stop` | `<div class="stop"><div class="h">stop &amp; think</div>…</div>` | Stop-and-think callout. 4px `--accent-2` left-border, accent-2 tinted background. `h` small-caps accent-2 12px. |
| `.nb-foot` | `<div class="nb-foot">…</div>` | Footer. Top 1px `--rule`, mono 13px ink-faint italic. Lists source files / numbers provenance. |

Optional: `.callout` (default + `.green` + `.warn` + `.red` variants), `.nums` grid (numeric punchline), `.toc`. Style them on the same palette.

**The In/Out cell prompts and the markdown-cell-as-narration pattern are non-negotiable in frog-simple.** Without them the page reverts to "blog post that quotes some code" and loses the notebook pedagogy markers.

## Tab-bar (when in dual-tab mode)

```css
.tabbar {
  position: sticky; top: 0; z-index: 50;
  background: var(--paper-2);
  border-bottom: 1px solid var(--rule);
  padding: 0 24px;
  display: flex; gap: 0;
}
.tab-btn {
  appearance: none; background: transparent; border: 0;
  font-family: inherit; font-size: 14px;
  color: var(--ink-faint);
  padding: 14px 22px; cursor: pointer;
  border-bottom: 2px solid transparent;
  font-variant: small-caps; letter-spacing: 0.12em;
}
.tab-btn:hover { color: var(--ink); }
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
```

The default tab bar is sticky-top, small-caps button text, active state = accent-colored underline + accent text. No accent fill behind the button; the simple visual does not push that hard.

## Hash routing (same as the magazine dual-tab)

The hash routing JS is identical to magazine's dual-tab: `#bird-<slug>` activates bird tab and scrolls; `#frog-<slug>` activates frog tab and scrolls. Pasting it inline at the bottom of `<body>` is enough; no module system, no event emitters. See `templates/simple-dual-tab-skeleton.html`.

## Comparison to magazine and notebook

| Aspect | simple (default) | magazine (opt-in) | notebook (opt-in) |
|---|---|---|---|
| External assets | none | Google Fonts + KaTeX + Prism | Google Fonts + KaTeX + Prism |
| Body font | macOS system serif | Cormorant Garamond + Playfair Display | Inter |
| Mono | macOS system mono | JetBrains Mono | JetBrains Mono |
| Page background | `#fbf6e9` warm pulp (dotted texture optional) | `#f4ecdd` warm paper + dotted texture | `#fafafa` off-white |
| Drop cap | yes (bird-flavored) | yes | no |
| Roman numeral chapter openers | yes (bird-flavored) | yes | no |
| In/Out cells | yes (frog-flavored) | no | yes |
| KaTeX rendering | off by default; `--math` opt-in | on (auto) | on (auto) |
| Best for | reports, explainers, codebase walkthroughs, offline reading | paper learning with math identity | code-first Karpathy walkthrough |

## Self-audit (run with the shared SKILL.md base)

**Visual / dependencies**
- [ ] HTML has **no `https://fonts.googleapis.com`** URL anywhere.
- [ ] HTML has **no CDN-loaded** `katex` / `prismjs` / `tailwindcss` / `highlight.js` references (unless `--math` opted-in and KaTeX is therefore loaded).
- [ ] All CSS sits in a single `<style>` block in `<head>`. All JS sits in a single `<script>` block before `</body>`.
- [ ] `:root` block declares the warm-paper color tokens (`--paper` / `--paper-2` / `--ink` / `--ink-soft` / `--ink-faint` / `--rule` / `--rule-soft` / `--accent` / `--accent-2` / `--gold` / `--quote-bg` / `--code-bg` / `--code-fg`). No token has been deleted from the palette — they read together as the visual identity.
- [ ] Body font stack starts with `-apple-system` then macOS serifs (`Iowan Old Style`, `Charter`) before generic fallbacks. Mono stack starts with `ui-monospace, "SF Mono"`.

**Bird-flavored (only if rendering a bird page under simple)**
- [ ] `.masthead` is present with kicker + `<h1>` + `.deck` + `.byline`, framed by 4px double + 1px rules.
- [ ] Each chapter opens with `.chapter-rule` (Roman numeral, small-caps, accent color) followed by `.chapter-title`.
- [ ] The first paragraph after each `.chapter-title` is `.lede` and renders a drop cap on first letter, colored by `--accent`.
- [ ] At least one `.callout`, one `.pull`, and (if the source has a comparable structure) one `.matrix` block.

**Frog-flavored (only if rendering a frog page under simple)**
- [ ] `.nb-head` with `.stamp` (mono caps) + `<h1>` + `.sub`. 2px ink-soft bottom border.
- [ ] Sections use `<h2 class="section">[N] name</h2>` — not Roman numerals.
- [ ] Cold open is a `.cell.code` + `.cell.out` pair (frog principle: code before abstraction).
- [ ] At least 3 `.cell.md` narration cells across the page, spaced between code/output pairs.
- [ ] At least one `.stop` callout.
- [ ] `.nb-foot` present.

## Reference exemplar

`/Users/han/project/TARS/comm/.photo/memory_hermes.html` is the visual ground truth. Both tab-bird and tab-frog scopes there are the contract simple-bird-skeleton.html and simple-frog-skeleton.html distill into reusable form. When in doubt about a class, a hex, or a spacing — diff against that file.
