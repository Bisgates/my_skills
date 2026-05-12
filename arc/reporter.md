# reporter — internal protocol (not user-invocable)

> Internal sub-protocol referenced by `arc-plan.md`, `arc-execute.md`, and `SKILL.md`.
> There is no `/arc-reporter` command. The reporter is a role the main agent dispatches
> on the user's behalf during plan + execute.

## Why a reporter exists

The arc protocol already records *what happened* (`0_meta.md ## log`, `1_objective.md`,
`2_plan.md`, `output/`). What it does not produce is a **reader-facing artifact** that
explains *why we did this, what we tried, what we learned, and where to look next* in a
form the user can hand to a teammate or revisit cold a month later. The reporter fills
that gap as a single-file, CDN-self-contained HTML — same writing principles as the
[grok skill](../grok/SKILL.md): begin-with-why, deconstruct from first principles, walk
new concepts through a concrete worked example, magazine-style layout.

## Two phases

### Phase A — In-flight curation (cheap, by the main agent)

During `/arc-plan` and `/arc-execute`, the main agent appends short bullet jots to
`_drafts/report_notes.md` inside the canonical arc folder. This is **note-taking, not
report-writing** — the goal is to pre-stage the raw material so the final HTML
generation in Phase B does not have to re-derive everything from `0_meta.md ## log`.

**When to append a note:**
- Plan locked → one bullet block summarizing strategy + step list.
- Smoke test passed (or failed and was diagnosed) → one bullet with the key numbers.
- A non-obvious decision was made → one bullet with the decision and the reason.
- A step produced a load-bearing artifact (figure, table, model) → one bullet with the
  path under `output/<...>/` and one line of why it matters.
- All plan steps complete → one bullet with the final outcome vs. acceptance.

**What a note looks like** (terse, agent-readable):

```md
## 260512_1430 [smoke]
- ran scripts/smoke_render.py on 8 frames
- mean PSNR 31.4 (target ≥ 30) → smoke green, proceeding to full run
- output/260512_1430_smoke/

## 260512_1612 [decision]
- chose flow-warp over feature-warp for occlusion handling
- reason: feature-warp on the smoke set produced ghosting at frame edges (see output/260512_1455_feature_warp/)
```

The notes file is freeform — the main agent does not need to obey a schema. Any
structure that lets the Phase B sub-agent quickly skim and reconstruct the journey is
fine. Keep each note ≤ 5 lines.

If `_drafts/` does not exist yet, create it on first append (`mkdir -p`).

### Phase B — Final emit (one general-purpose sub-agent at end of /arc-execute)

After the main agent writes `arc log "[done] all plan steps complete; ready for /arc-finalize"`,
it dispatches a single general-purpose sub-agent in **one** Agent tool call. The sub-agent's
prompt must be self-contained — the sub-agent has none of the current conversation context.

**Dispatch prompt skeleton** (the main agent fills in `<...>`):

```
You are the arc reporter for arc <id> at canonical path <arcs/all/<id>_<slug>/>.

Goal: produce a single-file, CDN-self-contained, magazine-style HTML report at
<arcs/all/<id>_<slug>/7_task_report.html> that lets a teammate (or the user a month
from now) understand what this task was, why we did it, what we tried, what worked,
what did not, and where the artifacts live.

Read these files in order before writing anything:
1. ~/.claude/skills/grok/SKILL.md — adopt its writing principles (begin-with-why,
   first-principles deconstruction, concrete worked example, ~80% page budget on the
   core insights, single-file CDN HTML output). Do NOT literally invoke /grok; you are
   writing a different artifact (a task report, not a paper-grok).
2. <arc>/1_objective.md — the goal, boundary, acceptance criteria.
3. <arc>/2_plan.md — the route map.
4. <arc>/_drafts/report_notes.md — the pre-staged notes (skim once for narrative).
5. <arc>/0_meta.md — frontmatter (id/brief/parent/dates) and the trailing 60 lines of
   `## log` for the journey.
6. <arc>/output/ — list directory contents to know which artifacts exist; reference
   them by relative path. Do not inline binary outputs; link to them.
7. <arc>/utils/ and <arc>/scripts/ — list filenames and one-line summaries of intent
   (read top docstring); do not paste full source.

Produce 7_task_report.html with this section spine (Chinese natural-language content,
matching the user's reading language):
- Title + one-line subtitle (the brief).
- §1 Why (begin-with-why) — what was stuck, why this task happened now.
- §2 Goal & Acceptance — surfaced from 1_objective.md, plain language.
- §3 The Approach — the strategy we picked and why (from 2_plan.md + key decisions
  in the notes).
- §4 What Happened — narrative pass over the execution, anchored to log entries +
  notes; embed the 1-3 most load-bearing numbers prominently.
- §5 Artifacts — table of `output/<...>` dirs with what each contains and why.
- §6 What We Learned — non-obvious lessons (good for future-me / next task).
- §7 What's Next — open follow-ups and any [STALE?] flags worth chasing.

Style:
- Single .html file. All assets via CDN (Tailwind, Highlight.js if needed). No build
  step. Opens cleanly with `open` on macOS.
- Magazine layout: generous whitespace, strong typographic hierarchy, one accent color.
- Diagrams as inline SVG where they add clarity; do not invent diagrams that are not
  load-bearing.
- Code excerpts only when a specific snippet is the lesson; otherwise describe and
  link to `utils/<x>.py` or `scripts/<y>.py`.
- ~80% of page budget on §1, §3, §4, §6. §2/§5/§7 are scannable, not exhaustive.

Write the file, then report back: (a) absolute path written, (b) size in KB,
(c) one-line summary of the report's thesis. Do NOT call `arc log` yourself —
the main agent will log on your behalf.
```

After the sub-agent returns, the main agent:

1. Verifies `7_task_report.html` exists and is non-empty.
2. Calls `arc log "[report] 7_task_report.html generated by reporter sub-agent (<size>KB)"`.
3. Runs `open <arcs/all/<id>_<slug>/7_task_report.html>` from the shell so the user
   sees it in the default browser.
4. Tells the user one line: "Report generated and opened — see `7_task_report.html`."

## Failure handling

- Sub-agent fails to produce the file → `arc log "[report-failed] <reason>"`, tell the
  user, do **not** retry silently. The user decides whether to re-dispatch.
- `_drafts/report_notes.md` is missing or empty → the sub-agent reconstructs from
  `0_meta.md ## log` alone. The report will be thinner; that is acceptable.
- The arc was abandoned (not done) → reporter is **not** dispatched. Abandoned arcs
  stop at `arc abandon`; their trace lives in `0_meta.md` and that is enough.

## Don't

- Do not regenerate `7_task_report.html` after every step — that is what
  `_drafts/report_notes.md` is for. The HTML is emitted once, at the end.
- Do not let the reporter sub-agent write outside `<arc>/7_task_report.html`. No
  edits to `0_meta.md`, no `arc log` calls, no touching `utils/` or `scripts/`.
- Do not pass an explicit `model` parameter when dispatching — `general-purpose`
  inherits the parent model, keeping the writing voice consistent.
- Do not skip the `open` step. The point of "auto-open" is the user does not have to
  hunt for the file.
