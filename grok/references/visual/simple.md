# Visual · simple (default)

The default for both bird and frog. Warm-paper palette + macOS system fonts + zero external CDN.

Pick simple for investigative reports, technical explainers, codebase walkthroughs, anything that has to read on flaky network — single file, double-click open, no external assets. Pick [magazine](magazine.md) when the source is a paper with formulas worth typesetting as math. Pick [notebook](notebook.md) when the source is code-heavy and the page's spine is `In/Out` cells.

Default skeletons:
- bird-flavored: [`templates/simple-bird-skeleton.html`](../../templates/simple-bird-skeleton.html)
- frog-flavored: [`templates/simple-frog-skeleton.html`](../../templates/simple-frog-skeleton.html)
- dual-tab shell: [`templates/simple-dual-tab-skeleton.html`](../../templates/simple-dual-tab-skeleton.html)

## Hard constraints

- **No Google Fonts.** Body = macOS system serif. Mono = macOS system mono. Zero external font URLs.
- **No external CDN at all by default.** No KaTeX, no Prism, no Tailwind, no highlight.js. Code blocks plain `<pre>` styled by inline CSS; math as plain Unicode + sub/superscript, or skipped.
- **KaTeX is opt-in via `--math`.** If the source has heavy LaTeX, pass `--math` or rerun with `--visual magazine`. No silent CDN loads.
- **All CSS inline** in one `<style>` block. **All JS inline** in one `<script>` block before `</body>`.
- **Warm paper color tokens** declared in `:root` — don't strip them, they're the visual identity.

## Color tokens (copy verbatim into `:root`)

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
  --accent-2:  #2c5340;   /* deep green — frog code-cell border, stop-and-think */
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

Frog-simple uses the same serif for prose (reads better in serif on macOS than sans on retina). Cell prompts, code, labels go mono. If a sans is needed for a meta label, fall back to `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` — never load Inter from a CDN.

## bird-flavored simple — required components

Scoped under `.tab-bird` when inside the dual-tab shell.

| Component | DOM shape | Purpose |
|---|---|---|
| `.masthead` | `<header class="masthead">` with `.kicker` (small-caps accent), `<h1>` (system serif 44px), `.deck` (italic ink-soft), `.byline` (uppercase letterspaced 12px ink-faint) | Hero. Border-top 4px double `--rule`, border-bottom 1px `--rule`. Replaces magazine's editor-note. |
| `.chapter-rule` | `<div class="chapter-rule"><span class="roman">I · <name></span></div>` | Roman-numeral chapter opener. Center-aligned, small-caps, accent color, padded between two 1px rules. Replaces magazine's section-rule + numeral block. |
| `.chapter-title` | `<h2 class="chapter-title" id="bird-<slug>">…</h2>` | Italic system serif, 26px, ink color. Sits under chapter-rule. |
| `.lede` | `<p class="lede">…</p>` (first paragraph after chapter-title) | Drop cap. `::first-letter` floats left, 4.4em, accent color. |
| `h3` | Small-caps system serif, letter-spaced 0.08em, ink-soft, with 1px bottom hairline | Sub-heads inside chapters. |
| `.callout` | `<div class="callout"><div class="ctitle">…</div><p>…</p></div>` | 3px accent left-border, paper-2 tint. `ctitle` small-caps accent 12px. |
| `.pull` | `<div class="pull">…</div>` | Centered italic pull-quote, accent-2 color, top + bottom 1px rule-soft hairlines. |
| `.matrix` | `<div class="matrix"><div class="cell"><div class="h">…</div>body</div>…</div>` | 2-column grid of comparison cards. Each cell 1px `--rule` border, paper-2 bg. |
| `pre code` | `<pre><code>…</code></pre>` | `--code-bg` background, 3px gold left-border. No Prism. |
| `table` | Thin `--rule-soft` row borders, accent small-caps `th` | Body cells in serif, numerics in mono. |

Optional: `.afterword`, `.timeline`. Both inherit the simple palette.

The drop cap and Roman-numeral chapter openers are non-negotiable in bird-simple — without them the page reverts to "blog post on system fonts."

## frog-flavored simple — required components

Scoped under `.tab-frog` when inside the dual-tab shell.

| Component | DOM shape | Purpose |
|---|---|---|
| `.nb-head` | `<header class="nb-head"><div class="stamp">…</div><h1>…</h1><div class="sub">…</div></header>` | Notebook title block. `stamp` mono 12px ink-faint. `h1` 30px system serif. `sub` italic ink-soft. Border-bottom 2px ink-soft. |
| `h2.section` | `<h2 class="section" id="frog-<slug>"><span class="num">[N]</span> name</h2>` | Mono small-caps accent-2. `num` is `[1]` / `[2]` / … in mono 12px ink-faint. 1px `--rule` bottom border. Not Roman numerals. |
| `.cell.md` | `<div class="cell md"><div class="label">In [md]:</div><p>…</p></div>` | Markdown / narration cell. 4px `--rule` left-border. Label mono 11px ink-faint. |
| `.cell.code` | `<div class="cell code"><div class="label">In [N]:</div><pre><code>…</code></pre></div>` | Input cell. 4px `--accent-2` left-border. `<pre>` on `--code-bg`. |
| `.cell.out` | `<div class="cell out"><div class="label">Out [N]:</div><pre>…</pre></div>` | Output cell. 4px `--gold` left-border. `<pre>` transparent bg, ink-soft text. |
| `.stop` | `<div class="stop"><div class="h">stop &amp; think</div>…</div>` | Stop-and-think callout. 4px `--accent-2` left-border, accent-2 tinted bg. `h` small-caps accent-2 12px. |
| `.nb-foot` | `<div class="nb-foot">…</div>` | Footer. Top 1px `--rule`, mono 13px ink-faint italic. Source files / numbers provenance. |

Optional: `.callout` (default + `.green` + `.warn` + `.red`), `.nums` grid, `.toc`. Style on the same palette.

In/Out cell prompts and markdown-cell-as-narration are non-negotiable in frog-simple.

## Tab-bar (dual-tab mode)

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

Sticky-top, small-caps button text, active state = accent-colored underline + accent text. No accent fill behind the button.

## Hash routing

Identical to magazine dual-tab: `#bird-<slug>` activates bird tab and scrolls; `#frog-<slug>` activates frog tab and scrolls. See `templates/simple-dual-tab-skeleton.html`.

## Comparison to magazine / notebook

| Aspect | simple (default) | magazine (opt-in) | notebook (opt-in) |
|---|---|---|---|
| External assets | none | Google Fonts + KaTeX + Prism | Google Fonts + KaTeX + Prism |
| Body font | macOS system serif | Cormorant + Playfair Display | Inter |
| Mono | macOS system mono | JetBrains Mono | JetBrains Mono |
| Page background | `#fbf6e9` warm pulp | `#f4ecdd` warm paper + dotted texture | `#fafafa` off-white |
| Drop cap | yes (bird-flavored) | yes | no |
| Roman numerals | yes (bird-flavored) | yes | no |
| In/Out cells | yes (frog-flavored) | no | yes |
| KaTeX | off; `--math` opt-in | on | on |
| Best for | reports, explainers, codebase walkthroughs, offline reading | paper learning with math identity | code-first Karpathy walkthrough |

## Visual self-audit

**Dependencies**
- [ ] No `https://fonts.googleapis.com` URL anywhere.
- [ ] No CDN-loaded `katex` / `prismjs` / `tailwindcss` / `highlight.js` (unless `--math` was passed; then KaTeX only).
- [ ] All CSS in a single `<style>` block in `<head>`. All JS in a single `<script>` before `</body>`.
- [ ] `:root` declares the full warm-paper token set — none deleted from the palette.
- [ ] Body font stack starts with `-apple-system` then macOS serifs. Mono starts with `ui-monospace, "SF Mono"`.

**Bird-flavored** (if rendering bird under simple)
- [ ] `.masthead` with kicker + `<h1>` + `.deck` + `.byline`, framed by 4px double + 1px rules.
- [ ] Each chapter opens with `.chapter-rule` (Roman numeral, small-caps, accent) followed by `.chapter-title`.
- [ ] First paragraph after each `.chapter-title` is `.lede` with a drop cap colored by `--accent`.
- [ ] At least one `.callout`, one `.pull`, and (if applicable) one `.matrix` block.

**Frog-flavored** (if rendering frog under simple)
- [ ] `.nb-head` with `.stamp` + `<h1>` + `.sub`. 2px ink-soft bottom border.
- [ ] Sections use `<h2 class="section">[N] name</h2>` — not Roman numerals.
- [ ] Cold open is a `.cell.code` + `.cell.out` pair.
- [ ] At least 3 `.cell.md` narration cells spaced between code/output pairs.
- [ ] At least one `.stop` callout.
- [ ] `.nb-foot` present.

## Reference exemplar

`/Users/han/project/TARS/comm/.photo/memory_hermes.html` — visual ground truth. Both `.tab-bird` and `.tab-frog` scopes there are the contract `simple-bird-skeleton.html` and `simple-frog-skeleton.html` distill into reusable form.
