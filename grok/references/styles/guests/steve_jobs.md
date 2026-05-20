# Guest pack · steve_jobs (overlay on bird)

> Experimental guest lens. Loaded only when the user passes `--style guest:steve_jobs` or says "用 steve_jobs 视角讲" / "Steve Jobs 风格" / etc. Single-tab only; never enters the dual-tab rotation. See parent SKILL.md § Guest packs for the lifecycle contract — guests are a lab, not a permanent fixture.

## Lineage and posture

**Steve Jobs, keynote-driven product vision.** Reads the source through two anchoring questions: *"What does this enable that wasn't possible before?"* and *"Where's the user?"* Opens with the demo, not the predicament. Strips everything that isn't load-bearing for the central enabled experience. Closes with one unexpected implication that wasn't claimed in the paper but follows from its insight.

The base altitude is top-down (closer to bird than frog), but the *spine* is different — bird derives the method from the goal, then closes with the principle worth remembering. Jobs shows the outcome first, then explains it backward from "look at what this lets you do." Both move from abstraction → mechanism, but they pick different anchors.

## Base

- **Layered on top of [`../bird.md`](../bird.md)** — inherits the section-rule opener, the worked-example block, the callout matrix, the math box, the lab block, the warm-paper palette.
- **Base skeleton: [`../../../templates/simple-bird-skeleton.html`](../../../templates/simple-bird-skeleton.html).** No separate guest skeleton ships — the page is the simple-bird skeleton with the overrides below applied inline.
- **Inherits from bird:** `section.branch[data-accent]` openers, `.lede` drop-cap paragraphs, `.worked-example`, the 6-color callout matrix (`.insight` / `.danger` / `.success` / `.warning` / `.definition`), `.math-box`, `.compare`, `.lab`, tables, color-coded variables.
- **Overrides:** the cold open, the per-section opening element, the page-end close. New CSS components for the Jobs-flavored moves.
- **Drops from bird:** cross-domain transfer beat, asymptotic / extreme-case lever beat, the "principle worth remembering when details fade" close, the `.feynman` meta-insight card (used in bird for the Hamming reflection), the `.afterword` ink-bordered kicker (replaced).

## Voice deltas vs. bird

- **Demo first, predicament second.** The cold open shows the working outcome — a generated image, a one-line `code → output` pair, a polished screenshot, a single result number on a hero card — before any "the field was stuck on X" framing. The reader feels the result in the first 200ms; the explanation arrives afterward.
- **The user is always present.** Every concept introduction names *who feels this change*. Not "the model achieves N% PSNR" but "the person who couldn't get a clean photo from their phone now gets one." For pure-theory sources with no obvious end user, say so honestly in the editor-note and pick a proxy reader (a future practitioner, a downstream researcher).
- **One-sentence keynote-slide line per section.** Each section opens with a single italic line in the accent color (`.kn-slide`), positioned between the section-rule and the `.lede`. This is the line that would go on Jobs's slide #N if he were presenting this section. If you can't extract that line, the section isn't earning its place — cut, merge, or rethink.
- **"It just works" judgment.** When the source proudly describes a knob the user has to tune (a hyperparameter, a manual threshold, a per-dataset config), flag it with a `.failure-of-taste` callout. "Three hyperparameters? That's three places the user fails." This is the page's critical voice — used sparingly, never as a license to dunk.
- **First-person plural conviction.** "我们做了 X / 我们相信 Y / 我们认为 Z" — Apple's voice. Once or twice per major section, not every paragraph. The point is conviction, not bravado.
- **Drops:** asymptotic-case lever ("push N to ∞ and see what the algorithm degenerates to"), cross-domain transfer ("this also shows up in coding theory"), Hamming's "principle to remember when details fade." These are bird signatures and don't translate to the Jobs register.
- **Still banned (from shared principles):** paper-boilerplate phrases (本文 / 综上 / 显然地), the lowercase conversational frog openers ("okay 接下来"), the "不是 X，而是 Y" parallel-construction tic. Jobs is declarative and short, not chatty.

## The "one more thing" close (replaces bird's meta-reflection)

Every page ends with a centered italic block in the accent color, marked above by a tiny mono-uppercase eyebrow reading `ONE MORE THING.` and below by white space. Two sentences max, ≤ 80 Chinese characters total. The content is **a small unexpected implication that follows from the source's insight but isn't claimed in the source itself** — not a summary, not a moral, not a "what I excluded." If you can't surface a one-more-thing, you haven't internalized the source.

Replaces both bird's `.afterword` kicker and bird's per-section meta-reflection beat. (The page does not get both; choose `.one-more-thing` and let bird's afterword stay dropped.)

## Required components — checklist

Every guest:steve_jobs HTML must include (in addition to the shared base in SKILL.md and the bird-inherited components):

1. **Hero with demo.** The hero's primary element is *the demo* — a base64-inlined screenshot of the source's headline result, a one-line code → output pair, a generated artifact, or a single dominant number — not just an editor-note. The editor-note shrinks to one line or is dropped.
2. **Per-section `.kn-slide` line.** Italic, accent color, ~28–36px, sits between the `.section-rule` and the `.lede`. Replaces bird's `.ch-hook` italic one-liner. Every section has exactly one.
3. **At least one `.failure-of-taste` callout** when the source has any user-facing knob the user has to tune. (If the source genuinely has none — a closed-form result, a hyperparameter-free method — drop the requirement and note the absence in the editor-note.)
4. **`.one-more-thing` close** at the very end of the page, after the last section and before the colophon.
5. **At least one declarative pull quote** in `.pullquote` form, shaped as a Jobs-flavored conviction ("X 是我们相信的事情。" / "我们的目标只有一个：Y。"). Placed roughly mid-page. Attributed via `.who` to the source's authors, or unattributed when the line is the page's own editorial voice.
6. **At least 1 hero image / demo screenshot / signature SVG per major section.** Visual texture is load-bearing in this voice. If the source has no figures worth embedding, the agent generates a clean SVG conceptual diagram per section — minimal, sharp, lots of white space, single accent color.

## Drops from bird's required components

- **`.feynman` meta-insight card** — Hamming's signature, not Jobs's. If you need an emphasis box, use `.insight` or `.definition` instead.
- **`.afterword` ink-bordered kicker box** — replaced by `.one-more-thing`.
- **Asymptotic-case observation per page** — drop entirely.
- **Cross-domain transfer observation per page** — drop entirely. (If the connection is genuinely load-bearing, allow it as a one-line aside in the body, not a paragraph beat.)
- **Timeline section** — demoted from "strongly recommended" to "optional." Include it only when the source's lineage is part of the user-facing story (e.g. iterations of a product, generations of a model family).

## CSS additions over simple-bird

Drop the following block into the page's inline `<style>` after the simple-bird base:

```css
.kn-slide {
  font-family: "Iowan Old Style", Charter, "Hoefler Text", Georgia, serif;
  font-style: italic;
  font-size: clamp(22px, 2.6vw, 34px);
  color: var(--accent);
  line-height: 1.28;
  margin: 14px 0 22px;
  text-wrap: balance;
  letter-spacing: 0.005em;
}
.failure-of-taste {
  border-left: 4px solid var(--accent-2);
  background: var(--paper-2);
  padding: 14px 18px;
  margin: 20px 0;
  font-size: 14.5px;
  line-height: 1.55;
}
.failure-of-taste::before {
  content: "失之品味 · FAILURE OF TASTE";
  display: block;
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--accent-2);
  margin-bottom: 8px;
}
.one-more-thing {
  border-top: 1px solid var(--rule);
  margin: 64px auto 32px;
  padding-top: 28px;
  max-width: 620px;
  text-align: center;
  font-family: "Iowan Old Style", Charter, "Hoefler Text", Georgia, serif;
  font-style: italic;
  font-size: 21px;
  color: var(--accent);
  line-height: 1.55;
  text-wrap: balance;
}
.one-more-thing::before {
  content: "ONE MORE THING.";
  display: block;
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  font-size: 11px;
  font-style: normal;
  letter-spacing: 0.22em;
  color: var(--ink-soft);
  margin-bottom: 16px;
}
```

The variable tokens (`--accent`, `--accent-2`, `--paper-2`, `--rule`, `--ink-soft`) all already exist in `simple-bird-skeleton.html`'s `:root` block — don't redefine them.

## Style-specific self-audit (run alongside the shared base and the bird base, minus the dropped items)

**Voice / writing**
- [ ] Cold open is the **demo / outcome**, not the predicament. The reader sees the result in the first paragraph (or hero image), before any "the field was stuck on…" framing.
- [ ] Every section opens with a single italic **`.kn-slide`** line in accent color, between the section-rule and the `.lede`.
- [ ] The **user is named** in every concept introduction — who feels this change, what was their friction before, what is it now. If the source has no obvious user, the editor-note explicitly identifies a proxy reader.
- [ ] Page closes with a **`.one-more-thing` block** — two sentences max, an unexpected implication that follows from the source but isn't claimed by it.
- [ ] **First-person plural ("我们" / "我相信" / "我们认为")** appears at least once per major section. Not every paragraph.
- [ ] **No Hamming beats leaked in**: no cross-domain transfer, no asymptotic / extreme-case lever, no "principle worth remembering when details fade." If you wrote one, that section is bird-voice, not Jobs-voice.

**Components**
- [ ] Hero contains the **demo** (image / generated artifact / one-line code+output / single hero number). The editor-note is one line or dropped.
- [ ] At least one **`.failure-of-taste`** callout (or an explicit editor-note line explaining why the source has no user-facing knobs).
- [ ] At least one declarative **`.pullquote`** shaped as a Jobs-flavored conviction.
- [ ] No `.feynman` blocks on the page.
- [ ] No `.afterword` ink-bordered box on the page (replaced by `.one-more-thing`).
- [ ] At least one hero-level image / demo / signature SVG per major section.

## Style-specific gotchas

- **Don't drift into Hamming reflexes.** Cross-domain transfer ("this same trick shows up in digital filters") is a *bird* signature; under the Jobs lens it reads as a name-dropping detour. If the connection is genuinely load-bearing, surface it as a one-line aside, not a paragraph beat.
- **Don't make every paragraph sound like a press release.** "我们认为 / 我相信 / 我们的目标只有一个" lands once or twice per section. Beyond that the voice tips into parody.
- **Don't fake a user when there isn't one.** For pure-theory papers (existence proofs, complexity bounds, mathematical structure results), be honest in the editor-note: "本篇没有直接的终端用户 — 我们以 *未来的从业者* 作为代理读者". Inventing fake user stories is worse than acknowledging the gap.
- **`.failure-of-taste` is not a "criticize the paper" license.** It flags *design choices the source left to the user* — knobs, hyperparameters, manual configuration the user has to figure out. Not architectural decisions the source had no degree of freedom over, and not implementation details that are orthogonal to user experience.
- **One demo, not a gallery.** The hero shows *one* image — a gallery defeats the keynote's "look at this" focus. If the source has multiple striking outputs, pick the strongest one for the hero and reference the rest later in a `.compare` block or a small grid.
- **"One more thing." has to actually be unexpected.** If the line just restates the source's contribution, that's an afterword, not a one-more-thing. Either find a real implication the paper didn't claim, or drop the block and admit the source's footprint is fully bounded.

## Promotion candidates — moves to consider merging back into bird if this guest earns its keep

The user's stated workflow is to iterate on guests and **fold the moves that earn their keep back into bird (or frog)**. After several runs of `--style guest:steve_jobs`, the high-signal candidates to promote are:

- **`.kn-slide` per-section line.** Forcing one italic-sentence section thesis is useful in any top-down voice, not just Jobs. Could land in bird as an optional element between `.section-rule` and `.lede`, replacing or supplementing the `.ch-hook`.
- **`.failure-of-taste` callout.** A "design knob left to the user" critique is a legitimate addition to bird's callout matrix — useful for any methods-paper review. Could be renamed (`.knob-flag` / `.手感缺失` / similar) when merged so it doesn't carry the Jobs branding.
- **Hero-with-demo opening pattern.** When the source has a striking outcome image, leading the hero with the artifact (rather than only the editor-note) is a strong move. Could become an optional bird hero variant.

Low-signal (probably stays guest-only):
- **`.one-more-thing` close.** Too persona-bound — "One more thing." carries Jobs's specific keynote cadence.
- **First-person plural conviction voice.** Reads as Apple-press-release outside the Jobs frame.
- **The full "demo first, predicament second" structural inversion.** Jobs-specific; bird's predicament-first opening is correct for the top-down altitude in general.

When the user is ready to promote, the merge target lines live in: `bird.md` § "Voice (the bird delta)" for any inherited voice beats, § "Required components — checklist" for new components, § "CSS class quick reference" for new classes, and the `simple-bird-skeleton.html` template for any baked-in CSS additions.
