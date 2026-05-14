---
name: 3dgs_exp_report
description: Generate one single-file, self-contained HTML experiment report for an arc in `~/project/work/3dgs`. Style is grok's magazine reportage — warm-paper Playfair/Cormorant body, section-rule Roman-numeral openers, drop-cap lede, callout matrix. Mandatory 3-chapter spine — (1) SOTA现状 + 实验目标 + 实验配置介绍, (2) N 组实验各自结果（loss 曲线 / 图片对比 / 必须嵌入所有存在的视频, 一个都不能漏）, (3) 综合对比及结论. Optional supplementary chapters can follow. Output is always `<arc>/exp_report.html`, one consolidated report per arc, overwrites prior version. Images base64-inlined; videos via `video2html` all-intra + base64. Use when the user runs `/3dgs_exp_report`, or asks for an "实验报告 / 实验对比 HTML / pivot report" after a 3DGS / DA3 / SAM3 / DriveStudio / multi-agent / multi-clip / depth-alignment run — especially when an arc id under `arcs/all/<id>/` is referenced. Do NOT trigger for paper-learning (use `grok`), standalone video embedding (use `video2html`), or generic landing-page work (use `frontend-design`).
dependencies:
  - grok
  - video2html
---

# 3dgs_exp_report

One HTML per arc that an engineer (or their boss) can double-click open, scroll end-to-end, and walk away knowing *what was tried, what changed, what the numbers say, what the pictures show, and what to do next*. It is **not** a paper-learning artifact (that's `grok`) and **not** a single-video player (that's `video2html`). It is a magazine-style longread of experiments that already ran in an arc.

## Quick start

```
/3dgs_exp_report 260512b
/3dgs_exp_report arcs/all/260512b_boost_fabu_static_sota
```

Output: **always** `<arc>/exp_report.html` — fixed filename, one canonical report per arc. Re-running overwrites the prior version. The file is self-contained: every image is base64-inlined, every video is re-encoded all-intra + base64-inlined, the skeleton ships Google-Fonts (Playfair Display / Cormorant Garamond / Inter / JetBrains Mono) and pinned-CDN KaTeX / Prism. Movable across machines by `cp` / email / Airdrop.

Hand off by running `open <abs path>`, then printing the absolute path on its own line in the final assistant message so the user can `cmd+click` to reopen.

## Trigger discipline

Enter this skill **only** on explicit invocation:

- `/3dgs_exp_report …`
- Natural-language asks inside the 3dgs workspace: "实验报告 / 出个 report / 实验对比 HTML / pivot 报告 / 把 260512b 做成 HTML / 把刚才那组实验整理成 magazine 风格的 html"

Do **not** trigger from:

- A `.html` already existing in an arc folder — don't proactively rewrite it.
- A user asking for "summary" — that means `9_summary.md`, not HTML.
- A `grok` / `frontend-design` / `video2html` invocation.

## Inputs you need before writing

The user usually points at an arc id (`260512b`) or an arc folder path. From there, gather (and ask **one** question if any of items 1–3 is missing — don't fabricate):

1. **Conclusion (one line).** "4 个并行 agent 在 PSNR 上都没追平 baseline，但 C 在两个场景的 SSIM/LPIPS 都稳定领先——细节锐度的视觉改善是肉眼可见的。" Without this the lede has no punch.
2. **Baseline + experiment goal.** What's the SOTA / failure-mode being attacked. Pull from `1_objective.md` "Goal" + the user.
3. **Per-variant metrics.** Tabular numbers per variant per scene. Pull from `agent_<X>/output/<ts>_*/metrics_eval/*.json` or whatever the scripts produced. Compute deltas vs. baseline. Color win green / lose red **only where direction has meaning**.
4. **Loss curves (if produced).** Most training runs dump `tensorboard` events or a `loss.csv`. If a per-variant curve image exists in the arc, embed it in chapter 2. Skip silently if it doesn't — don't fabricate a plot.
5. **Image comparisons.** Frame extracts from `output/agent_<X>_compare/` or `output/report_frames/` (often vstack baseline / variant / GT). Inline as base64 JPEG.
6. **Videos — embed every one that exists.** This is the spec's load-bearing rule: "只要有就都放进去". Glob `output/**/*.mp4`; if N videos exist, the report has N video embeds. Use `video2html`'s all-intra recipe (workflow § 5). If total embed bloat would push the HTML over ~80 MB, *warn the user* and ask whether to drop thumbnails-with-link instead — don't silently downsample.
7. **Interpretation.** Why the numbers / pictures look the way they do. Lives in chapter 3.
8. **Next steps.** Concrete, scoped follow-ups. Name the variant, the change, the expected signal. Not "investigate further".

## Workflow

1. **Resolve target.** Accept arc id (`260512b`) → expand to `arcs/all/260512b_*/`. Or accept relative/absolute folder. Reject if not inside `~/project/work/3dgs`. Output path = `<arc>/exp_report.html`.

2. **Collect artifacts.** Read `0_meta.md`, `1_objective.md`, `2_plan.md`, the latest `9_*.md` if present. List script outputs under `agent_<X>/output/<ts>_*/` and `output/<...>/`. Glob, don't guess.

3. **Start from grok's bird/magazine skeleton.** Copy `~/.claude/skills/grok/templates/bird-skeleton.html` to `<arc>/exp_report.html`. That file is the canonical magazine chrome — masthead, warm-paper hero with editor-note, top progress bar, right-rail nav dots, ruled section openers with Roman numerals + accent rotation, drop-cap lede, callout matrix, math-box, pull-quote, afterword, three-column colophon. Then **prune** what doesn't apply to an experiment report:
   - Remove `.lab` / `.canvas` / `.btn-row` blocks (no interactive sandboxes here).
   - Remove `.worked-example` / `.math-box` if there's no formula being walked through (usually there isn't).
   - Remove the IIFE-wrapped `<script>` for lab demos. Keep IntersectionObserver for the nav rail + the progress bar.
   - Keep masthead, hero, section-rule openers, callouts, tables, `.pullquote`, `.timeline` (use for "实验流程" if useful), `.afterword`, `.colophon`.

4. **Fill the mandatory 3-chapter spine.** See § Required spine below for exact markup pattern. `templates/chapter_spine.html` ships the fill-in stencil with all magazine classes pre-wired.

5. **Embed media.**
   - **Images.** Read file → base64 → `<img src="data:image/jpeg;base64,…">`. No relative paths in the final HTML — grep the file for `src="output/` / `src="./` / `src="agent_` and reject if any hit. Downscale > 1600px long-edge with `sips -Z 1600 <file>` and prefer JPEG for photographs (`-O format jpeg`) before encoding; keep depth maps PNG.
   - **Videos.** For every `*.mp4` you intend to embed:
     1. Run `~/.claude/skills/video2html/scripts/embed.py <video> --out /tmp/_v.html --keep-intermediate` → produces `/tmp/_v_allintra.mp4`.
     2. `base64 < /tmp/_v_allintra.mp4` → splice into `<video src="data:video/mp4;base64,…" controls preload="metadata">`.
     3. Copy the wheel-scrub `<script>` block from `~/.claude/skills/video2html/templates/page.html` into the report's `<head>` (once, deduped) so two-finger trackpad scrub matches QuickTime.
     4. Wrap each `<video>` in a paper-soft panel with a mono-uppercase eyebrow caption (`agent_C · scene 002 · baseline / variant / GT vstack`).

6. **Validate before declaring done.**
   - File opens at `file://...` with no broken images / no broken videos.
   - Grep the HTML for `src="output/`, `src="./`, `src="agent_` — must be zero hits.
   - All 3 required chapters present (search for the three `data-accent` anchors below).
   - Every video file present in the arc that the user wanted included is embedded (count `*.mp4` in arc vs. `<video` tags in HTML).
   - File size sanity: > 80 MB means warn the user and offer thumbnail-with-link mode.

7. **Hand off.** Run `open <abs path>`. Print **only the absolute path on its own line** in the final assistant message.

## Required spine (in this order)

Use grok's section-opener pattern for each chapter: `<section class="branch" data-accent="…">` followed by `<hr class="section-rule">` → `.section-head` (giant Roman numeral + `<h2>` with `<strong>` accent keyword + tiny `.branchcode`) → `<hr class="section-rule thin">` → `.ornament` glyph row → `.ch-hook` italic one-liner → `.lede` drop-cap paragraph. Accent rotation suggested below.

The fill-in stencil for all three chapters (with magazine markup pre-wired) is at [`templates/chapter_spine.html`](templates/chapter_spine.html). Copy it into the pruned grok skeleton; do not hand-roll a new chapter pattern.

### Chapter 1 — SOTA 现状 / 实验目标 / 实验配置 (`data-accent="red"`)

- **SOTA 现状.** Baseline 是什么（method + checkpoint path）、当前 metrics（PSNR/SSIM/LPIPS 表，paper-soft body + ink header bar）、肉眼可见的失效模式（栏杆 / floater / 糊面 / 远景空洞，配 2–3 张失效帧截图，`.compare > .naive` 左侧）。
- **实验目标.** One paragraph from `1_objective.md` Goal — what we want to fix and why this round of variants is worth running. End with a `.pullquote` if there's a one-line thesis ("anti-floater ≠ PSNR-max").
- **实验配置.** Method config path, dataset preset, scene ids, hardware (`gpu7` GPU layout if multi-agent), iter budget, scheduling rules. Render as a `<table>` of agent × dimension or as a `.pill` row of config tags.

### Chapter 2 — N 组实验各自结果 (`data-accent="indigo"`)

One sub-section per experiment / agent / variant (use `<h3>` with magazine `.marker` style `§ 2.A` / `§ 2.B` / …). Each sub-section in this exact order:

1. **方向说明** — 1–2 sentences: 攻击哪个失效模式 + 假设机制. Cite the relevant config diff inline (`cull_alpha_thresh 0.005→0.05` …).
2. **Loss 曲线** — if available, embed as a base64 PNG in a paper-soft panel with mono-uppercase eyebrow caption. If multiple losses (rgb / ssim / depth / lpips), prefer one composite multi-line plot over many small ones.
3. **图片对比** — `grid-2` (or `grid-3`) of `.panel`s, each panel is an `<img>` (base64) + `.panel-cap`. Pick representative frames (early / mid / late). Same panel layout across variants — consistency lets the reader compare without re-orienting.
4. **视频效果** — **embed every video that exists for this variant**. One paper-soft panel per video, eyebrow caption identifies (agent / scene / what's being shown). If no video exists for this variant, write one short sentence stating that — don't silently skip.
5. **本变体 metrics** — small `<table>` with rows `baseline / this variant` and columns `PSNR / SSIM / LPIPS / extras`. Delta cells colored `.num.win` / `.num.lose`.

### Chapter 3 — 综合对比及结论 (`data-accent="forest"`)

- **统一 metrics 大表.** All variants × all scenes in one `<table>`. Header bar ink-black; body paper-soft; numerics in JetBrains Mono right-aligned. Mark the winning row with `tr.ours-row` (or the best per-column cell with `.num.win`).
- **关键判断 (3–6 条).** `<ul>` of `<strong>`-led bullets, each one sentence of *mechanism* — what made the winner win, what made the loser lose. This is what the boss reads.
- **限制与陷阱.** Honest list of what's still broken or what the metric noise hides (dataset_cfg merge bugs, unfair eval splits, OOM probes, etc.). One `.danger` callout per substantive limitation.
- **下一步建议.** Numbered `<ol>`. Each item: the variant, the change, the expected signal. Don't write "investigate further".

### (Optional) Supplementary chapters

If the experiments produced material that doesn't fit chapters 1–3 (e.g. an alignment survey, a pose-refine no-op investigation, a reproducibility appendix, a "scripts I built" sub-section), add them as additional `<section class="branch" data-accent="…">` blocks after chapter 3. Rotate accents from the remaining palette (`amber` / `plum` / `slate`). Each supplementary chapter still follows the section-opener pattern (rule → numeral → h2 → branchcode → ornament → hook → lede).

End-of-article: `.afterword` (ink-bordered paper-soft kicker box, "what I chose / what I excluded") + `.colophon` (three-column italic footer: Citation / Resources / Colophon).

## Style — grok magazine, not reportage

The chrome and typography come from grok. Do not re-derive — copy and use:

- **Body type stack.** `Playfair Display` (display headings, drop caps, Roman numerals) + `Cormorant Garamond` italic (decorative italics, signoff, sublines, hooks) + `Inter` (sans eyebrows / labels / pills / branchcodes) + `JetBrains Mono` (math / lab / code / numerics). Do **not** substitute Source Serif 4, Space Grotesk, or system-ui-only.
- **Color tokens (paper theme).** Body sits on `#f4ecdd` warm-cream paper with the two-radial-gradient dotted texture from grok skeleton. No `#ffffff` body bg. Accent rotates per chapter via `data-accent="red|indigo|forest|amber|plum|slate"`.
- **Masthead.** Thin black-ruled top bar — italic Playfair logo left (`"3DGS Experiment Report — Private Edition"` or similar), uppercase letterspaced Inter volume info right (`arc 260512b · vol I · MAY 2026`).
- **Hero.** Kicker (warm-red, uppercase letterspaced Inter, 12px) → big Playfair `<h1>` 72px with **one** italic `<em>` subtitle phrase and a warm-red italic ampersand → italic Cormorant `.subline` (22px) → `.editor-note` framed by `border-top: 4px double` + `border-bottom: 1px` ink rules, with mono-uppercase `.label` and italic Cormorant `.signoff` ("— main agent · 23:24"). Optional `.hero-stats` row (PSNR / SSIM / LPIPS Δ at a glance). `.meta-line` with black `.pill` chip (`arc id · scenes · GPU layout`) and warm-red links.
- **Section openers.** 7px-thick `<hr class="section-rule">` in the accent color → giant 88px Playfair Roman numeral (`I.` / `II.` / `III.`) → `<h2>` with one `<strong>` keyword in accent → tiny mono `.branchcode` (`chapter_1 · sota + goal + config`) → 1px `<hr class="section-rule thin">` → `.ornament` row of italic Playfair glyphs (`§ · § · §` / `◊ · ◊ · ◊` / `¶ · ¶ · ¶`, rotate between chapters).
- **Drop-cap lede.** `.lede` first paragraph of each chapter in Playfair 21px with a giant accent-colored drop cap (80px, floats left). Subsequent paragraphs return to serif at 17 / 1.74.
- **Pull-quote.** `.pullquote` — paper-soft accent-tinted bg, 6px accent left-border, italic Playfair 26–28px. Attribution in `.who` (Inter uppercase 12px, letterspaced).
- **Callouts.** Paper-soft fills with uppercase Inter labels. Use `.danger` for failure modes / limitations / "test_image_stride bug"; `.success` for cleanly-won metrics; `.insight` for non-obvious mechanism explanations; `.warning` for caveats; `.definition` for term anchors.
- **Tables.** Ink-black header bar + paper-soft body. Header text Inter caps 11px letterspaced. Body cells Cormorant 15px. Numerics JetBrains Mono right-aligned with `.num.win` (forest) / `.num.lose` (muted). Winning variant row gets `tr.ours-row` forest-tinted highlight.
- **Panels (image / video plates).** Paper-soft fill, 3px accent top-border, 1px rule edge, sharp corners. `<img>` or `<video>` inside; below it a `.panel-cap` in italic Cormorant 14–15px with a mono-uppercase eyebrow (`Figure · agent_C · scene 002 · frame 105`).
- **Chapter divider.** `· · ·` centered, accent-colored at 0.6 opacity. Never `<hr>` for dividers.
- **Afterword.** Ink-bordered paper-soft kicker box near the end — Inter mono `.label`, Playfair italic h4, serif body bullets of "what I chose / what I excluded".
- **Colophon.** Three columns (Citation / Resources / Colophon) on warm paper, italic Cormorant body, tiny Inter-mono uppercase `<h5>` headers.

For the canonical visual ground truth, open `~/project/what_new/weekly/2026-19.html` and `~/project/learn_with_agent/260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — same theme this skill commits to.

## Hard constraints

- **Single HTML file.** All CSS inlined in `<style>`. Fonts via Google Fonts; KaTeX / Prism via pinned CDN (`katex@0.16.11`, `prismjs@1.29.0`). **No `@latest`. No build step.** No npm / vite / webpack.
- **All media inlined as base64.** No `src="output/..."`, no `src="./img/..."`. The file must survive being moved or emailed.
- **Embed every video.** "只要有就都放进去" is load-bearing. If a video file exists in the arc and is relevant to a variant, it must appear as a `<video>` embed in chapter 2 — not a link, not a thumbnail (unless the >80 MB warning fires and the user accepts thumbnail-with-link mode).
- **Three required chapters, in order.** SOTA现状+目标+配置 → 各变体结果 → 综合对比+结论. Supplementary chapters allowed *after* but never *instead of* these three.
- **Magazine, not reportage.** No reportage-style narrow `max-w-4xl` Tailwind container, no Tailwind-pill chips, no `.cmp` table class. Use grok's section-rule + Roman-numeral + drop-cap chrome. If you find yourself hand-rolling a `<style>` block from scratch, you're drifting — copy grok's skeleton instead.
- **Language.** Body content in Chinese (project CLAUDE.md). Technical terms / code identifiers / config keys / file paths stay in English. Chapter titles, ledes, prose, panel captions in Chinese; `.branchcode` / pill labels / eyebrow tags / table headers in English (they're identifiers, not prose).
- **Overwrite, don't append.** Re-running the skill on the same arc replaces the old `exp_report.html`. Don't preserve stale sections.

## Gotchas

- **Don't drift into reportage style.** The previous version of this skill produced a reportage-style HTML with `max-w-4xl` Tailwind layout. That's deprecated. If a tab named `.cmp` shows up in your CSS or a `max-w-4xl mx-auto px-6` shows up in your HTML, you're regenerating the old skeleton — stop and re-copy grok's.
- **Don't drift into `frontend-design` mode.** This is not a landing page. No marketing copy, no oversized gradients, no hero animations beyond the grok skeleton's scroll-driven progress bar and IntersectionObserver rail highlight.
- **Don't bury the conclusion.** It goes in the `.editor-note` / hero `.lede` — if the reader stops scrolling after the hero, they still know the result.
- **Don't gild the metrics.** `.num.win` / `.num.lose` color is enough. No emojis in cells, no traffic-light pills, no `+/−` arrows. The numbers and the delta in parens do the work.
- **Image bloat.** Base64 inflates ~33%. 32 panels × 1MB → 40MB HTML, multi-second cold open. Downscale first (`sips -Z 1600`); prefer JPEG for photographs; keep depth maps PNG to preserve palette.
- **Video bloat compounds.** All-intra mp4 is ~1.5–3× normal H.264; base64 adds another 33%. A 30 s screencast easily becomes a 20 MB embed. With 8 videos (4 agents × 2 scenes) you can hit 100 MB+ HTML. Check `du -h` after embedding; if the total HTML > 80 MB, surface the choice to the user explicitly: "8 videos = ~120 MB inlined; switch to thumbnail-with-link?".
- **`open` doesn't always reload.** If the user already had the HTML in a browser tab, `open <path>` brings focus but may reuse the cached `file://` version — mention "cmd+R to reload" in the hand-off when re-running.
- **Don't auto-commit the report.** Large base64 HTMLs blow up git. The 3dgs project gitignores arc symlink views but not `arcs/all/<id>/` — flag this to the user before any `git add` that would include the HTML.
- **Loss curves are optional, not invented.** If `agent_<X>/output/<ts>_*/` has no plotted loss image and no `loss.csv` you can plot in 5 s with matplotlib, skip the loss-curve sub-block. Don't fabricate a fake plot, and don't go off and run a long replot job.
- **One report per arc.** The filename is hard-coded `exp_report.html`. Re-running overwrites. If the user wants to compare report versions, they snapshot the file themselves before re-running.

## See also

- `~/.claude/skills/grok/templates/bird-skeleton.html` — **canonical magazine skeleton** (renamed across grok's style-pack iterations: `skeleton.html` → `Feynman-skeleton.html` → `MIT-skeleton.html` → `bird-skeleton.html`; current name follows Dyson's *Birds and Frogs*). Start every report from a copy of this file, then prune lab/math-box and fill the 3-chapter spine.
- `~/.claude/skills/grok/references/styles/bird.md` — full magazine style contract (component checklist, CSS class reference, visual gotchas) that this skill's chrome inherits. The voice contract is Hamming-style top-down — but for experiment reports the focus is on results / metrics / videos, so the visual is reused while the voice content is the report itself, not a Hamming-style essay.
- [`templates/chapter_spine.html`](templates/chapter_spine.html) — fill-in stencil for the 3 required chapters (and an optional supplementary chapter) in magazine markup.
- `~/.claude/skills/video2html/SKILL.md` — video embedding pipeline. Use its "video inside something bigger" workflow.
- `~/.claude/skills/grok/SKILL.md` — paper-learning HTML skill that defines the magazine theme this skill inherits. Different surface (it learns a source; we report an experiment); same chrome.
- `~/project/work/3dgs/CLAUDE.md` — arc protocol (canonical path `arcs/all/<id>_*/`, root-file conventions `0_meta` / `1_objective` / `2_plan` / …), Chinese-body language preference, no-auto-commit-of-generated-artifacts rule.
- Visual ground truth — open these before writing your first report:
  - `~/project/what_new/weekly/2026-19.html` — canonical masthead + hero + section-rule + drop-cap pattern.
  - `~/project/learn_with_agent/260507_OmniRe/OmniRe Urban Scene Reconstruction.html` — full long-read application of the magazine theme with accent rotation across 9 sections.
