# distill.pub DNA — corpus analysis (arc 260616a, Step 1)

Source: 16 cached interactive concept explainers, deep-read by 7 parallel agents. This is the **style bible** for the distill_v2 generator AND the reference for the discriminator. Every claim below was observed in ≥2 articles unless marked (single).

## 0. The decisive finding: distill is a *framework*, not a look

Real distill articles render through the **Distill web-component template** (`distill.pub/template.v2.js` + `webcomponents-loader.js`), shipped as **prerendered** static HTML (`<body distill-prerendered>`). The rendered output carries markers no generic AI explainer emits:

- Custom elements: `<d-front-matter> <d-title> <d-byline> <d-article> <d-cite key="…"> <d-footnote> <d-math> <d-figure> <d-appendix> <d-bibliography> <d-citation-list> <distill-header> <distill-appendix> <distill-footer>`. (2016–2017 era used the `dt-*` prefix: `dt-article`, `dt-cite`, `dt-byline`.)
- `<style id="distill-prerendered-styles">` carrying the verbatim Apache-2.0 *"Copyright 2018 The Distill Template Authors"* header.
- A real DOI `10.23915/distill.000NN`, `ISSN 2476-0757`, `<meta name="citation_*">` Google-Scholar tags, and a `<script id="distill-front-matter" type="text/json">` block.

**Implication for distill_v2:** to pass a strict markup-level discriminator, the output must reproduce this framework (prerendered `d-*` markup + the distill stylesheet + the appendix scaffold + front-matter), not merely imitate the visual look. This is the central Step-2 design decision (vendor/inline the template vs. emit prerendered-equivalent markup).

## 1. Spine (functional section archetypes, in order)

1. **Front matter** — `d-title` (title + one-sentence dek), `d-byline` (Authors / Affiliations / Published date / DOI as `<h3>` cells), optional `d-contents` TOC. No `<d-abstract>` rendered in most.
2. **Cold open** — a vivid real-world hook or concrete scenario, *no* "Introduction" heading, citation sometimes in the first sentence. Often an `l-screen` full-bleed teaser figure *before* prose. ("Consider speech recognition…"; "Most multicellular organisms begin life as a single egg cell"; "If you are in the business of training neural networks…")
3. **Roadmap** — one short paragraph naming the parts ("We divide this work into four parts").
4. **Problem-first framing** — state the naive view, then subvert it ("the popular story… but the truth is the other way round"). Why the obvious approach fails.
5. **Intuition before formalism** — plain-language / analogy / concrete instance first; the formal term italicized on first use; *then* the equation.
6. **Mechanism, derived not asserted** — equations staged incrementally (notation list → numbered `\begin{align}` with `\eqref` cross-refs → closed form). Annotated with `\overbrace{}^{\text{label}}` / `\underbrace`. Custom operators are introduced *and justified* (e.g. the `\hookleftarrow` "updates toward" operator explained in a footnote).
7. **Interactive figure payoff** — the reader-driven lab that *computes* the just-derived quantity (see §3).
8. **Worked example** — napkin numbers on a concrete instance.
9. **Properties / caveats / "how trustworthy?"** — honest reflection.
10. **X in context / related work** — alternatives, why this view wins.
11. **Close** — "Conclusion" / "Final thoughts", typically an *honest open-problem coda* ("blind men feeling an elephant… perspectives will converge").
12. **Appendix tail (fixed order, each an `<h3>`):** Acknowledgments → Author Contributions → Discussion and Review (links to GitHub `distillpub/post--…/issues`) → References (`d-citation-list`/`d-bibliography`) → Updates and Corrections → Reuse (CC-BY) → Citation (dual `pre.citation short` + BibTeX `long`).

One idea per `<h2>` (kicker `.marker` in the kicker column, H2 has a bottom-rule); sub-mechanisms as `<h3>`.

## 2. Visual system

**Two eras — pick one and be internally consistent:**
- **v1 (2016–2017):** body `font-family: Georgia, serif`; headings `HoeflerText-Regular, Cochin, Georgia, serif`; body 17px → 20px ≥1024px; h1 40→56px.
- **v2 (2018+):** body system stack `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto…` (`"Libre Franklin"` commented out in template); `html{font-size:14px; line-height:1.6em}` → 16px at `min-width:768px`; h2 24→36px, weight 600, `border-bottom` rule. Figure captions still often `font-family: georgia` italic.

**The signature layout — named-line 8-column CSS grid** applied to `d-title, d-byline, d-article, d-appendix`:
```
grid-template-columns:
  [screen-start] 8px
  [page-start kicker-start text-start gutter-start middle-start] 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr
  [text-end gutter-start-row2] ... [page-end] 8px [screen-end];
```
Width tiers (classes): `.l-body` (~648px, default reading column) · `.l-middle` (~816px) · `.l-page` (~984px) · `.l-body-outset` · `.l-page-outset` · `.l-screen` (full-bleed) · `.l-gutter` (right margin column for asides/footnotes). `d-article > * { grid-column: text }`. Captions can sit `grid-column: kicker` or `.l-gutter`.

**Color discipline (restrained, 3–4 colors total):**
- link `#004276` (deep blue, often `border-bottom` only, no underline)
- body text `rgba(0,0,0,0.8)`; secondary `0.7/0.6/0.5` tiers; captions `rgba(0,0,0,0.6)` 12–13px
- accent/status teal `#009688` (+ `#80cbc4`); citation color `#668`
- dark header `hsl(200,60%,15%)`; warm figure backgrounds `#fdf6f2` / `#FFF1E7`; single control accent `steelblue`
- **no gradients, no rainbow, no drop-shadows.** Color appears as sparse semantic highlight (`<span style="background:#FFD5D5">cliff</span>`).

**Margin notes:** `aside { grid-column: gutter; font-size: 12px }`, `figcaption.l-gutter`, and `<d-footnote>` (hover popovers). Faint table rules `rgba(0,0,0,0.05)`. Figure spacing `margin: 1.5em 0 2.5em`.

## 3. Interactions (the soul)

- **Reader-driven dominates** (sliders, drag-a-point, hover-to-reveal, click-a-node, frame-scrubbers). Autoplay only for simulations the reader then perturbs (growing-ca: WebGL CA loop + click-to-erase).
- **Data-bound and recomputed, never faked.** t-SNE perplexity/ε sliders *re-run the solver* live with a step counter; momentum α/β sliders *re-solve* the optimizer trajectory; GP drag-an-observation *re-conditions* the posterior; RNN hover *re-derives* gradient connectivity `‖∂h_L/∂x‖₂`; CTC hover collapses real alignment paths. Bayes-opt uses `gif-slider` frame scrubbers across acquisition functions (PI ε=0.075/0.3/3, EI, UCB).
- **Tech:** d3 + SVG (most), Canvas/WebGL (sims), Observable runtime (gnn understanding), TensorFlow.js (live in-browser model in gnn-intro + growing-ca). KaTeX prerendered for math.
- **The figure IS the argument**, not decoration — the headline interactive often embodies the paper's whole point.
- **Cadence:** ~one substantial interactive per `<h2>` section / per 2–3 paragraphs. Gold-standard articles (gnn-intro, GP, t-SNE) have 6–12 reader-driven interactives.
- **Honest static fallback:** when something can't be computed live, a clearly-labeled static figure — never a live-looking fake.

## 4. Prose voice

> This section describes the voice of the **English** distill corpus. distill_v2's artifact is **Chinese** — port the *spirit* (intuition-first, hedge-honest, derive-not-assert, second-person only for interaction) into native Chinese technical prose; do not translate these English phrasings literally. See the Voice + anti-fingerprint sections of `generator_playbook.md` for the Chinese rules (incl. no-translationese).

- **First-person plural editorial "we" / "let's"**; **second-person "you"** for interaction prompts ("Edit the molecule…", "Hover over or tap the text").
- Calm, confident, teacherly; occasionally literary ("When the universe gives you quadratic speedups, you should start to pay attention"); **hedge-honest** ("Sadly, no"; "these observations may not generalize").
- **New concept introduction pattern:** plain-language framing → concrete example → italicized term on first use → formalism. Never formalism-first.
- **Short declarative takeaway** ends each section ("you cannot see relative sizes of clusters in a t-SNE plot").
- **Math staging:** inline `<d-math>` woven mid-sentence; display blocks *only after* intuition; KaTeX prerendered twin spans (`katex-mathml` + `katex-html`), never raw `$` or runtime MathJax.
- **Citations:** `<d-cite key="bibtexkey">` → numbered/superscript with hover-boxes; never inline `[1]` text. Asides in `<d-footnote>`.

## 5. AI-tells blacklist (what screams "generated", to be avoided)

These are inverse-tells — presence = instant discriminator flag:
- Plain `<section>/<div>/<figure>` instead of `d-*` elements; no `distill-prerendered-styles`; no DOI/appendix.
- Boilerplate openers: "In this article, we will explore…", "Let's dive in", "Welcome to…", "In this section, we'll discuss…", "In conclusion".
- GIF/CSS-animation or pre-rendered "results" masquerading as live computation; sliders that don't recompute.
- Decorative figures that don't carry an argument; emoji; gradient/neon palettes; drop-shadow cards.
- Rainbow/garish color; centered hero with a CTA button; bullet-list-heavy "listicle" structure instead of prose.
- Asserting results instead of deriving them; no honest-limitation section; no worked example.
- Math as images or raw LaTeX left on the page.
