---
name: manus
description: Produce a Manus-grade report as ONE interactive HTML file (Chinese artifact, English research): agent-gathered real data, per-item sub-agent fan-out for uniform breadth, computed (never invented) chart data, sortable matrices, cited sources, and a provenance appendix. Handles both teaching explainers and arbitrary research reports. Use ONLY when the user explicitly invokes /manus or names the style — "manus 风格 / manus 质量 / 像 manus 那样" 出报告 / 讲解 / 调研. Do NOT trigger for questions about the Manus product itself, plain 调研报告 / 深度分析 with no manus framing (deep-analysis), paper/folder explainers in learn_with_agent (grok), interactive concept explainers (distill / distill_v2), or runnable notebooks (spell-out).
---

# manus — Manus-grade interactive HTML reports

Language split: thinking, research, sub-agent prompts, and intermediate notes are English, and English-language sources are preferred during gathering; the delivered HTML is Chinese (正文/图表/脚注全中文). This spec stays in English per repo convention.

## Why the skill is shaped this way

Manus reports read as high quality because of five stacked levers. Each pipeline step below exists to replicate one of them:

1. **Real work behind the numbers** — content comes from visiting sources, downloading data, and running code, never from model memory alone. → steps 2–3.
2. **Uniform breadth** — a 50-item comparison keeps equal depth on item 50 because each item gets its own fresh-context sub-agent. → per-item fan-out in step 2.
3. **Long-horizon coherence** — a plan file on disk, re-read and updated between steps, keeps hours of work in one structure. → step 1.
4. **The deliverable is an artifact** — interactive charts, sortable tables, styled layout; presentation carries most of the perceived quality. → step 4.
5. **Visible provenance** — every load-bearing number carries a source, and the report ends with a how-this-was-made appendix. → citation rules + step 5.

## Output contract

- ONE self-contained HTML file, opens by double-click. Default path: next to the subject (same folder as a target PDF/codebase), else `./<slug>_report.html` in cwd. Same name → overwrite; history lives in git.
- Libraries via CDN: ECharts for charts, KaTeX only when math appears, Prism/highlight.js only when code appears. No Bootstrap, no build step, no references to project-root or other local files.
- Chart data is inlined as JSON produced during steps 2–3. A series with no traceable origin in the notes does not ship.
- Intermediate files go to `<subject folder>/_drafts/` (or the session scratchpad when the subject has no folder).

## Modes

One pipeline, two section spines. Pick by task shape:

- **research** — the report answers a question about the world (market, product landscape, papers survey, event).
- **teaching** — the report makes the reader understand a concept / paper / system.

Mixed asks ("调研 X 领域并讲透核心原理") take the research spine and embed a teaching chapter.

## Pipeline

### 0. Scope (no dispatch)

Pin: mode, the one core question, the item list when the task is N-similar-items, target file path, section spine. If the ask cannot yield a core question, ask the user exactly one question first.

All dispatch uses the in-session Agent tool, never headless `claude -p` — headless calls bill the API separately instead of running on the session's subscription.

### 1. Plan file

Write `_drafts/plan.md` (English): core question, spine, item list, per-item schema for breadth tasks, done-criteria. Update it after every step — it is the memory that keeps a long run coherent and the first thing to re-read after any interruption or compaction.

### 2. Gather

Prefer English-language sources; fall back to Chinese sources for China-only subjects.

- **Breadth (≥8 similar items)**: one `general-purpose` sub-agent per item, `model: "sonnet"` (web-crawl work is the token hog and the least tier-sensitive step). Concurrency ≤2 — parallel sessions share one rate-limit pool; queue the rest. Every agent returns the SAME schema: `field | value | source URL | access date`. The uniform schema is what makes every row of the final matrix equally deep.
- **Depth (research mode, few items)**: 2–4 axis agents dispatched in one message — quant/timeline, mechanism/actors, counter-case. The counter-case axis is mandatory: a research report that never steelmans the opposing read caps its own credibility.
- **Teaching**: read the actual source (PDF, code, docs) directly; fetch 2–3 secondary sources for contrasts and concrete numbers. Basics the user already knows (backprop / Adam / plain attention) get one line; budget goes to what is genuinely new.

Save every agent's result to `_drafts/notes_*.md` before moving on — sub-agent output that lives only in conversation is lost to compaction.

### 3. Compute

Where the report needs derived numbers (rankings, deltas, distributions, toy-model curves), write a script under `_drafts/`, run it, save the output JSON. Charts read from these JSONs. This step separates real data from plausible-looking data; skipping it reintroduces the exact failure the skill exists to avoid.

### 4. Assemble

Write the full Chinese HTML in one pass from plan + notes + computed JSON.

- Research spine: 核心结论 → 全景矩阵（可排序表格）→ 分项深拆 → 机制与对比 → 反方与检验 → 展望 → 附录·来源与方法
- Teaching spine: 一句话核心 → 全景图 → 逐层拆解（因果链）→ 交互演示（数据来自 step 3）→ 误解与边界 → 自测 → 延伸阅读

Craft rules:

- 结论先行；标题即论点；句句带新信息；形容词必配基线数字。
- 零解码中文：禁比喻绰号、禁排比对仗、禁武侠/游戏隐喻 — the reader decodes nothing.
- Interactivity must earn its keep: sortable matrix, tooltips, series toggles. Interaction that shows the same information fancier gets cut.
- Key claims carry numbered footnotes: source name + direct URL + access date.
- 附录·来源与方法 states source count, which data was sub-agent-gathered, and what was computed vs quoted — this section is the trust lever.

### 5. Self-check

- Render check: load the file in headless Chrome via playwright with `channel: 'chrome'` (system Chrome; `playwright install` hangs on mainland networks) and screenshot; a broken CDN load or JS error gets fixed before delivery.
- Audit: every chart series traces to a `_drafts/` JSON or note; every footnote URL is well-formed; the breadth matrix has no thin rows — a row visibly thinner than its siblings goes back to step 2.
- Deliver: open the finished file in the user's default browser (`open <path>` on macOS, `xdg-open` on Linux) — the report is the deliverable, so hand it over already launched; this is the "build + launch, then let the user judge" handoff, not driving the UI. Skip the open only when the session is headless/remote or the user asked not to. Then give the single HTML path plus a 3-sentence summary of what was found. Findings, never a re-narration of the pipeline.

## Gotchas

- The skill name collides with a product name. "manus 的报告为什么好" is a question ABOUT Manus — answer it directly; do not build a report.
- CDN means the first open needs network. If the user requires fully-offline, inline the chart library instead and say so.
- Do not pad thin data with prose. A 6-item matrix with real numbers beats a 30-item matrix with 24 guessed rows — invented rows are the one unrecoverable failure.

## See also

- `deep-analysis` — 调研报告 asked without manus framing; zero-CDN, offline-forever, forensic-report rubric.
- `grok` / `distill_v2` / `spell-out` — the learn_with_agent explainer family.
- `dataviz` (harness skill) — read before authoring any chart code or choosing chart colors.
