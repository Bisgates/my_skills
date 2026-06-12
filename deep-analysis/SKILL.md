---
name: deep-analysis
description: Produce a deep, data-dense analysis report on any topic — an event, a company, an industry, a policy — as one self-contained Chinese HTML file, built from live web research with strict source citation and a quality-rubric self-check. Use when the user runs /deep-analysis, asks for a 深度分析 / 分析报告 / 事件分析 / 公司分析 / 调研报告, or wants a data-heavy research report with cited sources. Do NOT trigger for technical paper/concept explainers (grok, distill), experiment write-ups (3dgs_exp_report), or UI work (frontend-design).
---

# deep-analysis — data-dense analysis reports

The artifact is intentionally Chinese (报告正文/图表/脚注全中文); this spec stays in English per repo convention.

Quality bar: the report must survive a blind pairwise comparison against flagship benchmarks (CSIS quantified war assessments, Hindenburg forensic reports). The rubric distilled from 22 such reports lives in `references/rubric.md` — it defines the 5 scoring dimensions, their 1/3/5 anchors, and the 10 craft moves. Both the writer and the self-check read it.

## Pipeline

### 0. Scope (main agent, no dispatch)

Pin down before any research: report type (`event | company | industry`), the one核心问题 the report answers, the data cutoff (today), expected章节骨架. If the user's ask is too vague to name the核心问题, ask one question first.

All dispatch goes through the **Agent tool (in-session sub-agents)**, never the headless `claude -p` CLI — headless calls bill the API separately instead of running on the session's subscription. Per-sub-agent effort cannot be set via the Agent tool; effort follows the session.

### 1. Research fan-out (sub-agents, `model: "sonnet"`)

Research is web-crawl work (dozens of fetch turns, page-laden contexts re-read every turn); it is the pipeline's token hog and the least model-tier-sensitive step, so it runs on sonnet: dispatch `general-purpose` sub-agents with `model: "sonnet"`.

Dispatch 3-4 agents in parallel **in a single message**, one per axis, prompts self-contained; each returns its notes as final text (they write no files — the main agent saves each result to `notes_<axis>.md`):

- **timeline+quant** — the event/financial timeline as numbers: daily/quarterly series, totals, peaks, deltas. Every number with source URL + 检索日期.
- **mechanism+actors** — causal mechanisms, stakeholders, incentives; expert/insider quotes with attribution.
- **counter-case** — the strongest opposing read of the same facts, competing hypotheses, base rates. This axis exists because the rubric's highest anchor requires steelmanning the best counter-argument before refuting it.
- **primary documents** (when type=company) — filings, transcripts, registry data; page-level citations.

Each agent returns structured claims: `claim | number | source URL | 检索日期 | primary/secondary`. Load-bearing numbers need ≥2 independent sources or an explicit single-source flag with a ±range.

### 2. Analysis: evidence sheet + outline (sub-agent, session model)

One analysis agent reads all research notes and produces two artifacts; this is where analytical judgment lives, so it runs on the session's own model: dispatch a `general-purpose` sub-agent with **no `model` param** (inherits the parent session). Output: one `evidence_and_outline.md`.

- **Evidence sheet** — merge notes into one sheet; build the pairs the rubric rewards: 声称值 vs 实测值, observed vs baseline (historical / peer / naive counterfactual). Discrepant sources → keep both numbers with the spread, never average silently. Anything uncited gets dropped here, not prose-laundered later. Cross-validation status (≥2 sources / 单源+区间) marked per claim.
- **Outline** — section titles are assertions, not labels (标题即论点). Default spine — adapt, don't pad: 核心结论 → 数据总览 → 时间序列/分布拆解 → 机制分析 → 横向对比 → 反方与检验 → 情景/展望 → 附录·来源. The 反方与检验 section is mandatory; a report with no steelmanned counter-argument caps at rubric ③=3. The outline names which evidence rows feed which section and what the falsification conditions of the main judgment are.

### 3. Draft (sub-agent type `report-writer-opus46` — pinned to opus-4.6 for its prose style)

Dispatch the Agent tool with `subagent_type: "report-writer-opus46"`. The Agent tool's `model` enum cannot pin versions, so the 4.6 pin lives in an agent definition file; if that agent type is missing in this runtime, create `~/.claude/agents/report-writer-opus46.md` with the snippet below (loads for new sessions) and meanwhile fall back to `model: "opus"` with an explicit notice — don't silently degrade:

```markdown
---
name: report-writer-opus46
description: Deep-analysis report drafting agent pinned to Opus 4.6. Not for research or judging.
model: claude-opus-4-6
---
You are a report-drafting agent. You write long-form analysis prose in Chinese exactly as instructed by the dispatch prompt. Do not invent facts not present in the provided research material.
```

The writer Writes the complete HTML directly to the target `report.html` path and replies only `DONE <bytes>` — returning an 80KB+ document as final text has hit single-turn timeouts in practice.

The writer prompt must inline: the evidence sheet path, the outline, `templates/report.html` as the skeleton (copy verbatim, fill tokens + FILL blocks), and the 10 craft moves from `references/rubric.md`. Hard rules the writer enforces:

- Every number traces to the evidence sheet; a number without a source line does not enter the report. Fabrication is the one unrecoverable failure.
- Key claims carry numbered footnotes (`sup.fn` → `ol.footnotes`): source name + direct URL + 检索日期 + what it supports.
- Charts are inline SVG authored in-document. Zero CDN, no external images — the file must open offline forever.
- 中文叙事规范: 结论先行、句句带新信息、形容词配基线数字、禁比喻/排比/设问。
- Uncertainty is stated as ranges with the sensitivity shown (脏数据给区间+敏感性), graded 独立可核 / 单源 / 有争议.

### 4. Self-check + one revision

Score the draft against `references/rubric.md` dimension by dimension. Any dimension < 4 → one targeted revision pass (same writer pin) fixing that dimension only. Also verify mechanically: all footnote anchors resolve, every metric card and table row has a source ref, file is a single self-contained HTML.

### 5. Deliver

Write `<topic_slug>.html` where the user asked (default: cwd), `open` it, and report: 核心结论 one-liner + file path + any single-source flags worth knowing.

## Gotchas

- WebFetch hits paywalls/bot walls (RAND, FT, 财新, muddywatersresearch…) — prefer mirrors, archives, or official S3/CDN endpoints; record when a load-bearing source was unreachable instead of substituting a weaker claim.
- Mainland network: external research needs the proxy up (`clashon`) before dispatching agents.
- pdftotext the long PDFs before handing them to sub-agents; raw 10MB PDFs blow their context.

## See also

- `references/rubric.md` — scoring dimensions, anchors, judging protocol, 10 craft moves
- `templates/report.html` — the single-file HTML skeleton (light product-doc theme, zero CDN)
