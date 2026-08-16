---
name: app-design
description: House visual-design principles for app and frontend UI — icon systems, typography, spacing rhythm, and color derivation, distilled from real polish sessions. Use when designing, restyling, or polishing any interface (sidebars, toolbars, navigation, settings pages, web pages), redrawing UI icons, or when the user says the UI 质感/texture feels off or worse than a reference app (ChatGPT, Notion, Things). Also load before generating brand-new app/frontend UI so output follows these principles from the start. Strong defaults, not law — deviate deliberately when the product's character demands it. Do NOT trigger for chart/data-viz styling (use dataviz) or functional/bug work with no visual change.
---

# App Design

House principles for interface visual quality. They came out of screenshot-vs-reference
iteration on real apps (the recurring gap was against ChatGPT / Things 3 / Craft-class
polish), so each rule states the *mechanism* — apply the mechanism, not just the number.

These are important references, not hard law. A product with a deliberate character
(a book-like "Folio" style, a terminal aesthetic) may override any of them — but the
override should be a chosen deviation, never an accident of defaults.

## The core recipe: fine strokes, dark ink

Perceived refinement is the pairing of stroke weight and ink darkness:

- **fine + dark = precise** (instrument feel: ChatGPT, Apple apps)
- **thick + light = crude** (sticker/cartoon feel — the most common failure)

The two must move together. Thinning strokes without darkening ink makes the UI weaker,
so a "make it thinner" request is really a "thinner AND darker AND slightly larger" change.

## Icon systems

- **Unify physical stroke width, not nominal.** Icons rendered at different sizes must
  share on-screen stroke weight (~1.2px is the refined default). Compute per icon:
  `stroke-width = target_px × viewBox / display_px`. A shared nominal stroke across
  mixed sizes is how sets end up visually uneven.
- **Icon : text size ratio ≈ 1.3.** Quality references run ~18–20px icons against
  ~14px text. A big canvas carrying thin lines reads precise; a small canvas carrying
  thick lines reads clumsy. Never shrink the canvas to "make room" — thin the stroke.
- **Icon inherits the row's text color.** One ink per row; a separate lighter gray for
  icons adds a second gray layer that muddies the row. Secondary/hover-revealed buttons
  may stay lighter — that's a different layer by design.
- **Metaphor first, then geometry.** Before drawing, name what the glyph must read as,
  then hunt misreads at target size: two offset squares read "copy", never "cards"
  (make cards landscape); a grid of squares reads "apps", never "scan" (use viewfinder
  + line); a bag shape reads "shopping", never "later" (use a clock). If a shape keeps
  misreading, steal proven geometry (Lucide, SF Symbols) and rescale — e.g. an arrowhead
  on an arc is famously fiddly; Lucide's rotate-cw solves it.
- **Consistent language across the set**: same grid (16 or 24), same cap/join, same
  corner-radius family, ~2px breathing room to the box edge, equal optical weight
  (a detail-dense glyph like a calendar will read darker — simplify it, don't thicken
  neighbors).

## Layout rhythm: count the left edges

A panel earns calm by collapsing to **two left edges**: an icon column and a text column.
Row labels, item titles, empty-state text, "load more" — all sit on the text column;
group/section labels hang on the icon column like margin annotations (Things 3 pattern).
Three or more ragged left edges is the most common cause of "something feels off".

Compute alignment arithmetically per style variant (`pad + icon + gap = text column`),
and re-derive every guard when any term changes — a style layer that hides icons
(text column = left edge) needs its own pinned values, or a base-layer change will
silently break it.

## Typography

- **One size, one rhythm.** All primary rows share one size (14px/400 is the refined
  default). Hierarchy comes from position, color, and case — never from bolding rows.
  Small + bold + mid-gray reads cramped and muddy; regular weight + darker ink reads calm.
- **Labels are annotations**: ~11px / 600 / +0.08em tracking / uppercase, in a light
  ink (~45%). Counts: 11px, `tabular-nums`, lighter still (~38%).
- **No weight change between states.** Hover/active/selected differentiate via
  background wash and ink darkness; a font-weight flip makes text physically shift.

## Color: derive, never hardcode

Hardcoded grays (`#8a8a8e`-style) go cold on warm themes and warm on cool ones. Derive
every gray from the theme's ink token: `color-mix(in srgb, var(--ink) N%, transparent)`
(or mix toward the surface color to stay anchored to the background). Working ladder:
content text ~90% ink, icons = content, section labels ~45%, counts ~38%. Contrast is a
big part of "texture" — a UI where everything is mid-gray reads flat regardless of layout.

## Evaluation loop

Judge from rendered screenshots, never from code:

1. Render the real app headlessly (or open it), capture at 2x.
2. Inspect at **both 1:1 and ~4x zoom** — 1:1 catches rhythm and contrast, zoom catches
   stroke quality and icon misreads.
3. Put a named quality reference (ChatGPT, Things, Craft, Bear) side by side and diff
   the gap in words before changing anything: which of stroke/ink/ratio/edges/scale is off?
4. One round = spec with exact values → implement → screenshot → misread hunt. Iterate;
   two focused rounds usually beat one big one.

## Gotchas

- Fractional strokes (1.15px nominal) render fine on 2x displays; only worry at 1x.
- `text-transform: uppercase` + tracking is safe with CJK labels (CJK ignores case,
  tracking reads intentional).
- When adding today-dots or fills inside stroked icons, scale them down as strokes thin.

## See also

- `frontend-design` — generates full creative interfaces; load this skill alongside it
  as the house constraint layer.
- `dataviz` — owns chart/graph styling; these principles still govern the page chrome
  around charts.
