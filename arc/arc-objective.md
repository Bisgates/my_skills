---
name: arc-objective
description: Run grill-me to define the arc objective with crisp boundary and acceptance criteria. Use when the user says "/arc-objective", "/arc-objective 260430c", or right after /arc-new chains in.
---

# /arc-objective — Lock the objective with grill-me

## Steps for the agent

1. **Resolve the arc.**
   - User gave an id? Run `arc cd <id>` to get the path.
   - No id? Use cwd (should be `arcs/all/<id>_*/`). If not, error out and ask for an id.

2. **Read `0_meta.md`** for context (brief / parent). If `parent` is non-null, also read the parent's `1_objective.html` and `9_summary.html` (if present) to use as constraint context.

3. **Estimate complexity, then choose interrogation depth.** grill-me inside arc is **adaptive**, not a fixed question count:
   - **Simple task** (single goal, narrow scope, acceptance readable straight off the brief, no ambiguous branches): **ask less**. Clarify only the 0–2 points that are genuinely missing; the moment you can write a crisp goal + checkable acceptance, **commit it to disk**. Do not pad questions just to "follow the flow".
   - **Complex task** (multiple goals / stakeholders, fuzzy success criteria, cross-system or wide scope, strong dependencies or high risk): **ask more**. Walk the branches patiently and align core goal, acceptance, boundary, constraints, dependencies, and risks one at a time. Still follow "one question at a time, with a recommended answer", but **do not skip the questions that need asking**.
   - **Anti-patterns:** running a full questionnaire on a simple task just to tick boxes; cutting a complex task off after one or two questions to save effort.
   - If you cannot tell whether the task is simple or complex, **ask one question first** to surface the user's own self-assessment of effort, then decide whether to extend into a longer conversation.

4. **Enter the grill-me loop** (the user's preferred "one question at a time, with a recommended answer" style):
   - Every question comes with a recommended answer.
   - Lock one branch before moving to the next.
   - Do not rapid-fire five questions; do not omit recommended answers.
   - **Ask in priority order: core first, boundary second.** What is being done, why now, and what success looks like — these are first-class. Boundary / constraints / risks matter, but they are guardrails to tighten *after* the core is locked. Do not invert this and start by chasing scope / non-goals / risks; the user will feel the conversation has drifted.
   - The branches below are a **menu**, used in priority order. **For simple tasks, only touch the items still unclear in the first two sections**; for the rest, either omit them entirely (delete the corresponding 04 / 06 section from the HTML — the template wraps them in HTML comments precisely so they can be dropped) or close them inside `1_objective.html` with a single line. Do not interrogate item by item.
     1. **Core goal:** what problem to solve, why now (motivation / trigger), what success looks like. Verbs must be concrete — no "研究 / 探索 / 看看" / "investigate / explore / take a look".
     2. **Acceptance criteria:** L1 quantitative metric + L2 visualization (follow the workspace AGENTS.md rules), so "done" is checkable.
     3. **In-scope vs. non-goals** (boundary).
     4. **Known constraints / assumptions.**
     5. **Upstream dependencies** (data / upstream arc / main-project code).
     6. **Primary risks** (do not invent risks if there are none — write only the genuine ones).

5. Once everything is locked, **compress** the conversation into `1_objective.html`, using `~/.claude/skills/arc/templates/1_objective.html` as the skeleton. Copy the template verbatim, then replace the four tokens — `{{ARC_NAME}}` (prose-cleaned brief, also used as `<h1>`), `{{BRIEF}}` (one-line problem statement, ≤ 18 字, the masthead deck), `{{ID}}` (7-char arc id), `{{DATE}}` (lock date, `YYYY-MM-DD`) — and fill the `<!-- FILL: ... -->` blocks. Delete any optional section (04 约束 / 假设, 06 风险) whose entire block is wrapped in HTML comments in the template if it doesn't earn its space; do not leave empty-bulleted sections — and do **not** renumber the remaining sections (numbering is fixed to the spine). **Write decisions only, not the dialogue transcript.** Preserve the inline `<style>` block as-is — light product-doc theme, zero CDN (same theme as `9_summary.html`). After locking, avoid repeated edits; goal changes are expressed via `4_pivot.md` or a new arc.

6. After writing, call `arc touch <id>` (the script updates `last_active_at` and rebuilds the index), then `open <arcs/all/<id>_<slug>/1_objective.html>` so the user immediately sees the locked artifact in the browser. Silent open — don't prompt.

7. **Auto-chain — do not stop and ask "what next?".** Estimate complexity from the locked objective and route accordingly. The user gets a one-line status, not a "pick A or B" prompt.

   **Trivial route** (single concrete step, no smoke needed, no risky dependencies, acceptance is one number on one input):
   - Skip the formal `/arc-plan` flow.
   - Write a 1-3 line `2_plan.md` directly — numbered steps only, no `Strategy / Smoke Test First / Risks` sections required, just enough that `/arc-execute` knows what to run. (`2_plan.md` must exist for `/arc-finalize` to work; this is the minimum form.)
   - Append one short note to `_tmp/report_notes.md` (mkdir on first use): `## <YYMMDD_HHMM> [plan]` + the step list.
   - Tell the user one line: `Objective locked; task is small — wrote a minimal plan and starting execute.` Then chain into the `/arc-execute` flow per `arc-execute.md`.

   **Non-trivial route** (multiple goals, fuzzy acceptance, cross-system, real dependencies, risk):
   - Tell the user one line: `Objective locked; entering plan phase.` Then chain into `/arc-plan` per `arc-plan.md`.

   **When in doubt, take the non-trivial route.** The cost of writing a fuller plan you did not need is small; the cost of skipping a plan that was actually needed is large (downstream rework, missing smoke test, sub-agents fanning out blind).

   The user can always interrupt ("hold on, let me look at the objective first") — but the default is to keep moving.

## Don't

- **No zero-alignment fabrication.** When the brief is vague or acceptance is missing, do not just write a self-styled `1_objective.html`. If the brief is already clear enough, an extremely short confirmation (e.g. restating goal + acceptance and asking "OK to write this into the objective?") is allowed before committing — **do not** add loops just to inflate question count.
- Do not write fuzzy acceptance ("works well", "roughly aligned"). Each L1 metric card needs a concrete target number plus, where it exists, a baseline.
- Do not embed execution details in `1_objective.html` — those belong to the plan.
- Do not introduce external CSS, Tailwind, Google Fonts, or any CDN asset into the HTML. The template ships the entire visual system inline; preserve it.
