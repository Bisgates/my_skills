# reporter — internal protocol (not user-invocable)

> Internal sub-protocol referenced by `arc-plan.md`, `arc-execute.md`, and `SKILL.md`.
> There is no `/arc-reporter` command. The reporter is a role the main agent dispatches
> on the user's behalf at the end of `/arc-execute`.

## Why a reporter exists

The arc protocol already records *what happened* (`0_meta.md ## log`, `1_objective.md`,
`2_plan.md`, `output/`). What it does not produce is a **reader-facing artifact** that
shows *the result first, the journey second, and a few honest after-thoughts* in a form
the user can hand to a teammate or revisit cold a month later. The reporter fills that
gap as a single-file, CDN-self-contained HTML — light, one-pager-ish, results-led.

## Hard rule: reporter never blocks the main flow

The reporter is dispatched **in the background** (`run_in_background: true` on the Agent
tool call). The main agent does **not** wait for it. The user's next instruction (e.g.
`/arc-finalize`) must be responsive immediately, even if the reporter is still drafting
the HTML. When the background sub-agent completes (often minutes later), the main agent
gets an automatic completion notification on its next turn — that is when `open` and
`arc log` happen.

**Do not** use a foreground Agent call for the reporter. A foreground call freezes the
main agent for the full reporter runtime (commonly 3-8 minutes), which is exactly the
behavior this protocol is designed to avoid.

## Two phases

### Phase A — In-flight curation (cheap, by the main agent)

During `/arc-plan` and `/arc-execute`, the main agent appends short bullet jots to
`_tmp/report_notes.md` inside the canonical arc folder. This is **note-taking, not
report-writing** — it pre-stages the raw material so the Phase B sub-agent does not
have to re-derive everything from `0_meta.md ## log`.

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

If `_tmp/` does not exist yet, create it on first append (`mkdir -p`).

### Phase B — Background final emit (one general-purpose sub-agent)

After the main agent writes `arc log "[done] all plan steps complete; ready for /arc-finalize"`,
it dispatches a single general-purpose sub-agent **with `run_in_background: true`**. The
main agent does not wait. The sub-agent's prompt must be self-contained — it has none
of the current conversation context.

**Dispatch prompt skeleton** (the main agent fills in `<...>`):

```
You are the arc reporter for arc <id> at canonical path <arcs/all/<id>_<slug>/>.

Goal: produce a single-file, CDN-self-contained HTML report at
<arcs/all/<id>_<slug>/7_task_report.html> that lets a teammate (or the user a month
from now) understand — in order — (a) what we ended up with, (b) how we got there,
and (c) any honest after-thoughts worth keeping. Light, one-pager-ish.

Step 1 — Copy the template.
Read ~/.claude/skills/arc/templates/7_task_report.html. That file is the SKELETON:
all CSS, layout, section comments, and FILL markers are already in place. Copy its
full contents to <arc>/7_task_report.html, then edit *that copy* — do not start from
scratch and do not invent your own CSS. The template is intentionally light (one
column, serif body, magazine-light vibe); preserve that feel.

Step 2 — Read the source material.
1. <arc>/1_objective.md — goal, boundary, acceptance criteria.
2. <arc>/2_plan.md — the route map.
3. <arc>/_tmp/report_notes.md — pre-staged notes (skim once for narrative).
4. <arc>/0_meta.md — frontmatter (id/brief/parent/dates) and the trailing 60 lines
   of `## log` for the journey.
5. <arc>/output/ — list directory contents to know which artifacts exist; reference
   them by relative path. Do not inline binary outputs; link to them.
6. <arc>/utils/ and <arc>/scripts/ — list filenames and one-line summaries of intent
   (read top docstrings only); do not paste full source.

Step 3 — Fill the template.
Replace tokens ({{TITLE}} {{SUBTITLE}} {{ID}} {{DATE}}) and the FILL blocks. The
template's section comments are explicit about what each section wants.

Section spine (mirror the template):
  §1 结果         mandatory. The headline number(s) + did we hit acceptance.
                  Open with one tone-setting line, then 1-3 metric cards (or a
                  one-line + link if the acceptance was visual, not numeric),
                  then a 1-2 sentence conclusion. Don't talk about process here.
  §2 过程         mandatory but SHORT. 3-5 short paragraphs total. Distill from
                  log + notes; do not transcribe. Skip the bend-in-the-road
                  paragraph if there wasn't one.
  §3+            free-form, light. Pick 0-4 of the candidate sections in the
                  template (关键决策 / 留下的产物 / 学到的东西 / 接下来). Use only
                  the ones that genuinely earn space. Bias toward fewer, shorter
                  sections. Padding here makes the report worse, not better.

Style:
- Single .html file. All assets via CDN (template already has Tailwind + inline
  CSS; do not add other dependencies). No build step. Opens cleanly with `open`.
- Natural-language content in **Chinese** (matches the user's reading language).
- Light. The whole report should read in 2-3 minutes.
- Diagrams as inline SVG only when load-bearing; do not invent decorative ones.
- Code excerpts only when a specific snippet is the lesson; otherwise describe and
  link to <code>utils/&lt;x&gt;.py</code> or <code>scripts/&lt;y&gt;.py</code>.

When done, report back: (a) absolute path written, (b) size in KB, (c) one-line
summary of the report's thesis. Do NOT call `arc log` yourself, do NOT run `open`
yourself — the main agent handles both after you return.
```

Dispatch parameters (Agent tool):

- `subagent_type: "general-purpose"`
- `run_in_background: true`  ← non-negotiable
- Do **not** pass an explicit `model` parameter — `general-purpose` inherits the
  parent model, keeping voice consistent.

### Phase C — Completion follow-up (when the notification arrives)

The main agent gets an automatic notification when the background sub-agent completes
— this can be in the next turn, several turns later, or in the middle of `/arc-finalize`.
On receiving the notification:

1. Verify `<arc>/7_task_report.html` exists and is non-empty.
2. Call `arc log "[report] 7_task_report.html generated by reporter sub-agent (<size>KB)"`.
3. Run `open <arcs/all/<id>_<slug>/7_task_report.html>` from the shell (silent — don't
   prompt; the user expects auto-open).
4. Tell the user one short line: "Report ready and opened — `7_task_report.html`."
   Do this even if the user is mid-conversation about something else; one line is fine.
5. **Do not** otherwise re-orient the conversation around the report. If the user is
   busy with `/arc-finalize` or other work, keep going — the line in step 4 is a
   notice, not a topic shift.

## Failure handling

- Sub-agent fails to produce the file → on the completion notification, call
  `arc log "[report-failed] <reason>"`, tell the user one line, do **not** retry
  silently. The user decides whether to re-dispatch.
- `_tmp/report_notes.md` is missing or empty → the sub-agent reconstructs from
  `0_meta.md ## log` alone. The report will be thinner; that is acceptable.
- The arc was abandoned (not done) → reporter is **not** dispatched. Abandoned arcs
  stop at `arc abandon`; their trace lives in `0_meta.md` and that is enough.

## Don't

- Do not regenerate `7_task_report.html` after every step — the in-flight notes file
  is for that. The HTML is emitted once, at the end of execute.
- Do not let the reporter sub-agent write outside `<arc>/7_task_report.html`. No
  edits to `0_meta.md`, no `arc log` calls, no touching `utils/` / `scripts/` /
  `_tmp/`.
- Do not invent CSS or import additional libraries — the template is the visual
  contract. Editing the copy in `<arc>/7_task_report.html` is fine; rewriting the
  skeleton is not.
- Do not pass an explicit `model` parameter when dispatching.
- Do not foreground-dispatch. The block-the-main-flow problem this protocol exists
  to prevent comes back the moment `run_in_background: true` is omitted.
- Do not skip the `open` step in Phase C. Auto-open is the point.
