# reporter — internal protocol (not user-invocable)

> Internal sub-protocol referenced by `arc-plan.md`, `arc-execute.md`,
> `arc-finalize.md`, and `SKILL.md`.
> There is no `/arc-reporter` command. The reporter is a role the main agent
> dispatches on the user's behalf at the point where an arc is about to flip
> to `done`.

## Why a reporter exists

The arc protocol already records *what happened* (`0_meta.md ## log`,
`1_objective.md`, `2_plan.md`, `output/`). What it does not produce is a
**reader-facing artifact** that shows *the result first, the journey second,
and a few honest after-thoughts* in a form the user can hand to a teammate
or revisit cold a month later. The reporter fills that gap as a single-file HTML under grok's "simple"
visual (warm-paper palette, macOS system fonts, zero external CDN) — light,
one-pager-ish, results-led, double-clicks open offline forever.

`9_summary.html` doubles as the `done` gate: `arc status <id> done` requires
the file to exist and be non-empty. The reporter is the only thing that
writes it; agents must not hand-craft any `9_*.md` or `9_*.html` themselves.

## Hard rule: reporter never blocks the main flow

The reporter is dispatched **in the background** (`run_in_background: true`
on the Agent tool call). The main agent does **not** wait for it. The user's
next instruction must be responsive immediately, even if the reporter is
still drafting the HTML. When the background sub-agent completes (often
minutes later), the main agent gets an automatic completion notification on
its next turn — that is when `arc status done`, `open`, and `arc log` happen
(see Phase C).

**Do not** use a foreground Agent call for the reporter. A foreground call
freezes the main agent for the full reporter runtime (commonly 3-8 minutes),
which is exactly the behavior this protocol is designed to avoid.

## Two dispatch points (one reporter)

The reporter is dispatched **exactly once per arc**, at one of these points:

- **Fast-done path** — at the end of `/arc-execute`, after the user
  one-line-confirms a trivial arc is ready to mark done. No
  `8_handoff_plan.md` exists; nothing to promote.
- **Formal finalize path** — `/arc-finalize` Stage 2, after promotion
  completes. `8_handoff_plan.md` exists and the reporter folds promoted
  code / doc changes / surviving `STALE?` items into the report.

Same template (`templates/9_summary.html`), same Phase A staging, same
Phase B dispatch shape, same Phase C handler. The only difference between
routes is whether the reporter has `8_handoff_plan.md` in its input set.

## Three phases

### Phase A — In-flight curation (cheap, by the main agent)

During `/arc-plan` and `/arc-execute`, the main agent appends short bullet
jots to `_tmp/report_notes.md` inside the canonical arc folder. This is
**note-taking, not report-writing** — it pre-stages the raw material so the
Phase B sub-agent does not have to re-derive everything from `0_meta.md ## log`.

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

The notes file is freeform — the main agent does not need to obey a schema.
Any structure that lets the Phase B sub-agent quickly skim and reconstruct
the journey is fine. Keep each note ≤ 5 lines.

If `_tmp/` does not exist yet, create it on first append (`mkdir -p`).

### Phase B — Background final emit (one general-purpose sub-agent)

Dispatched from one of two places (see "Two dispatch points" above). The
sub-agent's prompt must be self-contained — it has none of the current
conversation context.

**Dispatch prompt skeleton** (the main agent fills in `<...>`; the route is
encoded by whether `8_handoff_plan.md` exists in the source list):

```
You are the arc reporter for arc <id> at canonical path <arcs/all/<id>_<slug>/>.

Goal: produce a single-file, fully self-contained HTML report (zero external
CDN — see Style section below) at
<arcs/all/<id>_<slug>/9_summary.html> that lets a teammate (or the user a
month from now) understand — in order — (a) what we ended up with, (b) how
we got there, and (c) any honest after-thoughts worth keeping. Light,
one-pager-ish. This file is also the `done` gate for the arc.

Step 1 — Copy the template.
Read ~/.claude/skills/arc/templates/9_summary.html. That file is the SKELETON:
all CSS, layout, section comments, and FILL markers are already in place. Copy
its full contents to <arc>/9_summary.html, then edit *that copy* — do not start
from scratch and do not invent your own CSS. The template is grok's "simple"
visual: warm-paper palette, macOS system serif body, Roman-numeral section
openers, ZERO external CDN. Preserve that contract — do not add Tailwind,
Google Fonts, KaTeX, Prism, or any other external asset. All CSS stays in the
one inline <style> block the template ships with.

Step 2 — Read the source material.
1. <arc>/1_objective.md — goal, boundary, acceptance criteria.
2. <arc>/2_plan.md — the route map.
3. <arc>/_tmp/report_notes.md — pre-staged notes (skim once for narrative).
4. <arc>/0_meta.md — frontmatter (id/brief/parent/dates) and the trailing 60 lines
   of `## log` for the journey.
5. <arc>/8_handoff_plan.md — **read only if it exists** (formal finalize route).
   When present, fold promoted-code rows / doc changes / STALE? items into the
   §3+ candidate sections (留下的产物 / 接下来 / 关键决策). When absent
   (fast-done route), draw 留下的产物 from <arc>/output/ alone and skip
   promotion content.
6. <arc>/output/ — list directory contents to know which artifacts exist;
   reference them by relative path. Do not inline binary outputs; link to them.
7. <arc>/utils/ and <arc>/scripts/ — list filenames and one-line summaries of intent
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
                  For the formal finalize route, 留下的产物 (promoted code +
                  doc changes from 8_handoff_plan.md) and 接下来 (surviving
                  follow-ups / STALE? items) usually earn their space.

Style:
- Single .html file, **zero external CDN** — the template's inline <style>
  block is the entire visual system. Do not add Tailwind, Google Fonts, KaTeX,
  Prism, or any other external dependency. The whole file must double-click
  open offline forever.
- Visual = grok's "simple" theme: warm-paper palette (`--paper #fbf6e9`),
  macOS system serif body, mono code, Roman-numeral section openers
  (I · 结果 / II · 过程 / …). Keep the :root tokens — they are the visual
  identity.
- Natural-language content in **Chinese** (matches the user's reading language).
- Light. The whole report should read in 2-3 minutes.
- Diagrams as inline SVG only when load-bearing; do not invent decorative ones.
- Code excerpts only when a specific snippet is the lesson; otherwise describe and
  link to <code>utils/&lt;x&gt;.py</code> or <code>scripts/&lt;y&gt;.py</code>.

When done, report back: (a) absolute path written, (b) size in KB, (c) one-line
summary of the report's thesis. Do NOT call `arc log` yourself, do NOT call
`arc status` yourself, do NOT run `open` yourself — the main agent handles
all three in Phase C.
```

Dispatch parameters (Agent tool):

- `subagent_type: "general-purpose"`
- `run_in_background: true`  ← non-negotiable
- Do **not** pass an explicit `model` parameter — `general-purpose` inherits the
  parent model, keeping voice consistent.

### Phase C — Completion follow-up (the canonical done-flip handler)

This is the **single shared handler** that both `/arc-execute` (fast-done route)
and `/arc-finalize` (formal route) defer to. Do not duplicate this logic in
the entry-point sub-skills.

The main agent gets an automatic notification when the background sub-agent
completes — this can be in the next turn, several turns later, or in the
middle of unrelated conversation. On receiving the notification:

1. Verify `<arc>/9_summary.html` exists and is non-empty.
2. Call `arc log "[summary] 9_summary.html generated by reporter sub-agent (<size>KB)"`.
3. Call `arc status <id> done`. The CLI gate now passes (the file exists);
   if it rejects, something is wrong with the file — go to the failure path.
4. Run `open <arcs/all/<id>_<slug>/9_summary.html>` from the shell (silent —
   don't prompt; the user expects auto-open).
5. Tell the user one short line: "Arc <id> done — `9_summary.html` opened."
   Do this even if the user is mid-conversation about something else; one
   line is fine.
6. **Do not** otherwise re-orient the conversation around the summary. If
   the user is busy with other work, keep going — the line in step 5 is a
   notice, not a topic shift.

## Failure handling

- Sub-agent fails to produce the file → on the completion notification, call
  `arc log "[summary-failed] <reason>"`, tell the user one line, do **not**
  retry silently and do **not** flip status. The arc stays `active`. The
  user decides whether to re-dispatch.
- `arc status done` is rejected at Phase C step 3 even though the file exists
  (e.g. file is zero bytes despite sub-agent claiming success): treat as a
  reporter failure — `arc log "[summary-failed] empty file"` and stop. The
  user decides next action.
- `_tmp/report_notes.md` is missing or empty → the sub-agent reconstructs from
  `0_meta.md ## log` alone. The summary will be thinner; that is acceptable.
- The arc was abandoned (not done) → reporter is **not** dispatched. Abandoned
  arcs stop at `arc abandon`; their trace lives in `0_meta.md` and that is
  enough.

## Don't

- Do not regenerate `9_summary.html` mid-flight — the in-flight notes file
  is for that. The HTML is emitted once, at the point where the arc is about
  to flip to `done`.
- Do not let the reporter sub-agent write outside `<arc>/9_summary.html`. No
  edits to `0_meta.md`, no `arc log` calls, no `arc status` calls, no
  touching `utils/` / `scripts/` / `_tmp/`.
- Do not invent CSS or import additional libraries — the template is the
  visual contract. Editing the copy in `<arc>/9_summary.html` is fine;
  rewriting the skeleton is not.
- Do not pass an explicit `model` parameter when dispatching.
- Do not foreground-dispatch. The block-the-main-flow problem this protocol
  exists to prevent comes back the moment `run_in_background: true` is
  omitted.
- Do not duplicate Phase C in `arc-execute.md` or `arc-finalize.md` — both
  entry points reference this file's Phase C and let the shared handler flip
  the status.
- Do not skip the `open` or `arc status done` steps in Phase C. Auto-open is
  the point; the status flip is what closes the arc lifecycle.
- Do not write any other `9_*.md` or `9_*.html` file alongside `9_summary.html`
  — the gate is the single filename, by design.
