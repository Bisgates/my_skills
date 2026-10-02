---
name: parallel-drafts
description: Run one brief through several models in parallel (e.g. astra + opus + fable), save each model's draft under a fixed naming scheme, merge all drafts into one comparison page (HTML) or one combined PDF, and open it so the user can pick — then repeat the round with the user's feedback. Use when the user asks for the same design, mockup, deck, report page or copy to be made by multiple models side by side — "让 astra 和 opus 各出一版", "三个模型各出 3 版", "并行出几版我来挑", "多出几版设计合成一页", "把所有版本合成一个 PDF", "下一轮让选中的那个继续出" — or continues an earlier multi-model round. Do NOT trigger for a single model making a single draft (use design-claude or frontend-design), for dispatching one external model without comparison (use cross-agent-call), for visual principles alone (app-design), for long experiment campaigns with worker teams (fabu-agent-team), or for merging PDFs that were not drafted by models in parallel (pdf).
dependencies:
  - cross-agent-call
---

# Parallel drafts

One brief → N models in parallel → one file per model → one merged page → the user picks → next round. The work that repeats every round is the brief, the output contract, the file layout and the merge; this skill fixes those so each round is only "write the brief delta, dispatch, merge".

## Quick start

```bash
# after the drafts land in <design-dir>/<topic>_parts/[rN/]<model>.html
~/.claude/skills/parallel-drafts/scripts/merge_html.py \
  --title "Bot 头像 · 第一轮" --sub "astra-high / opus-high / fable-high 各 3 版" \
  --index rows.tsv --out <design-dir>/<YYMMDD>_<topic>.html \
  <topic>_parts/astra.html=astra-high <topic>_parts/opus.html=opus-high <topic>_parts/fable.html=fable-high
open <design-dir>/<YYMMDD>_<topic>.html
```

## Workflow

### 1. Write one brief with a `{MODEL}` placeholder

Write the brief once to the scratchpad, then `sed 's/{MODEL}/astra/g'` it into one copy per model. Every model must get the same brief; the only per-model difference is the output path. A good brief has these sections:

- **Context** — what the product/page is, where the thing appears, sizes that matter.
- **用户原话（照做）** — the user's request verbatim. Paraphrase loses the constraints the user actually cares about ("不要像素风", "think bold").
- **What to avoid** — the current design or rejected directions, so models don't drift back to them.
- **Requirements** — counts (N versions × M items), must-have dimensions, light/dark, sizes to show.
- **Output contract** — exact file path and the scoping rules below.
- **Report back** — one or two sentences: file path, version names, one-line concept each. No screenshots, no UI driving.

Round 2+: add the previous merged page path (read-only), the user's feedback verbatim, and which direction each model continues. When the user narrows to some directions, dispatch only the models that own them, each told "your rN `<dir>` was picked; expand only that".

### 2. Output contract (HTML drafts)

This is what makes merging mechanical. Put it in every brief:

> Write exactly one file: `<design-dir>/<topic>_parts/[rN/]{MODEL}.html`. It must open standalone, but all content sits inside a single `<section class="set-{MODEL}">` (round N: `set{N}-{MODEL}`). All CSS lives in one `<style>` inside that section and every selector starts with `.set-{MODEL}` — no `body` / `html` / `:root` / `*` rules. Prefix `@keyframes` names and SVG ids (gradient, filter, clipPath) with `{MODEL}-`. Any JS also lives inside the section and only touches it. Inline SVG/CSS only; no external images, fonts or libraries. Do not modify any other file.

`merge_html.py` inlines parts that obey this; a part that breaks it is embedded as an `<iframe srcdoc>` instead, so one sloppy draft never breaks the others. It prints which mode each part got and warns about duplicate ids.

For decks / PDFs the contract is a folder per version: `<out>/<Letter>_<variant>/` holding the source, the exported `.pdf` (and `.pptx` if asked), and `_src/` / `_qa/` working files. A change request that applies to every version goes in one shared `<out>/_修改要求_<topic>.md`, and each worker is pointed at it.

### 3. Lay out files

| What | Where |
|---|---|
| Design drafts | `~/project/build_with_opus/design/<project>/<topic>_parts/<model>.html` (round 1), `…/<topic>_parts/r2/<model>.html`, … |
| Reference images | `<topic>_parts/ref/` (screenshots the user pasted, current UI) |
| Merged design page | `~/project/build_with_opus/design/<project>/<YYMMDD>_<topic>.html`, later rounds `…_<topic>-r2.html` |
| Deck / doc versions | `<project-out>/<Letter>_<variant>/…` + `_merge_list.txt` + `<topic> · 全部版本.pdf` |

Part file names are the bare model id (`astra.html`), because `merge_html.py` uses the stem as the anchor and scope id. A draft that ran on the wrong model keeps its file under its true name (`luna_misrun.html`) and is merged as a labeled extra, never silently passed off as the requested model.

### 4. Dispatch in parallel

Default trio when the user says "各出一版" without naming models: astra-high, opus-high, fable-high. Otherwise use exactly the models named.

| Model | From Claude Code |
|---|---|
| opus | `Agent` (subagent `opus-high-worker`), `run_in_background: true` |
| fable | `Agent` (`general-purpose`, `model: fable`, "effort high" in the prompt), background |
| astra / sol / luna / grok | `cross-agent-call` `xagent codex exec -m <model> -c model_reasoning_effort=high … - < brief_<model>.md`, `run_in_background: true`, stdout/stderr to the scratchpad |

The agent prompt stays short: "Read and follow `<brief path>`. Write only the one file the brief names." Launch all of them in one message. Keep each codex `session=` id from the `[xagent]` stderr line — the next round can resume it so the model keeps its own context.

### 5. Check each part, then merge

Before merging, for each part: the file exists and is non-empty; the model that ran is the one requested (codex prints the model on stderr; on `exec resume` pass `-m` again and check — a resume has fallen back to a different model before); the report-back names match the file.

HTML: build `rows.tsv` (`model<TAB>version<TAB>one-line concept`) from the report-backs, run `merge_html.py` (Quick start), and add a `--note` for anything the user should know when comparing — two models landing on the same direction, a misrun kept as an extra.

PDF: append each accepted version's PDF path to `_merge_list.txt` (order = reading order) and run `scripts/merge_pdf.sh _merge_list.txt "<topic> · 全部版本.pdf"`. New versions accepted later: append a line, rerun.

### 6. Hand over and iterate

`open` the merged file, then report: merged file path, the index table (model / version / concept), anything that failed or was swapped, and — only if the user asks or the choice is clear-cut — a recommendation. The drafts were checked statically (scripts ran, files exist), not looked at; say so in one line. The user picks; their words verbatim become the next brief's feedback section.

After a pick goes to implementation, the implementation brief names the chosen part file and version as the design source (read-only).

## Gotchas

- **Parallel writers, shared folder.** Each worker may read siblings' earlier rounds but writes only its own path; say so in the prompt when two workers touch the same tree in one round.
- **Big merged pages.** Three models × several versions easily reaches 300–900 KB of inline SVG. That is fine for a local file; don't try to "optimize" drafts during merging — merging never edits a part.
- **Background notifications are not user turns.** A background worker finishing is not the user approving the result; deliver and wait for the pick.
- **Don't screenshot or click through the result** to verify it unless the user asked; build, open, hand over.

## See also

- `cross-agent-call` — exact CLI flags, model discovery, `xagent` session ids for non-native models.
- `app-design` — visual principles worth pointing design briefs at ("可先加载 app-design skill 参考原则").
- `design-claude` — single-draft local design canvas with the same `build_with_opus/design/<project>/` folder convention.
