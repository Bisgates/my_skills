---
name: arc-resume
description: Resume an arc with a full context load and a "where are we" report. Use when the user says "/arc-resume 260430c" or "继续 260430c".
---

# /arc-resume — Restore task context

The test this flow has to pass: an agent with zero conversation history reads the arc directory and can continue the work. `3_state.md` exists so that costs three files, not a whole log.

## Steps for the agent

1. **Flip status via the CLI:**
   ```bash
   arc resume <id>
   ```
   stdout is the canonical path (`arcs/<id>_<slug>`); stderr is the status-change message.

2. **Tell the user how to cd in** (don't cd for them):
   ```
   To work on it: cd $(arc cd <id>)
   ```

3. **Load context, in this order:**
   - `3_state.md` — where we are, how to re-run, settled facts, promotion candidates. This is the primary source.
   - `1_objective.md` — goal (§01) and acceptance (§03).
   - `2_plan.md` — the remaining steps.
   - `0_meta.md` — frontmatter (brief / parent / status history). Read the `## log` **only if `3_state.md` is stale or empty** (e.g. an arc from before `3_state.md` existed, or one abandoned mid-step); then read just the trailing 40 lines.

4. **Print a restart report:**
   ```
   ## Arc 260430c — <brief>
   - status: <prev_status> -> active
   - parent: <parent_id or none>
   - last_active: <ISO>

   ## Goal (1_objective.md)
   <one sentence>  ·  acceptance: <L1 metric + L2 evidence>

   ## Where we are (3_state.md)
   <one or two sentences>

   ## How to re-run
   <the commands from 3_state.md, verbatim>

   ## Settled facts
   <bullets from 3_state.md, distilled to ~5 lines>

   ## Next-step candidates
   - A: ...
   - B: ...
   ```

5. **Wait for the user to pick a next step.** Do not unilaterally enter `/arc-execute`.

## Don't

- Do not read the full `## log` — that is what `3_state.md` exists to prevent. When you genuinely need older detail, `grep` for it.
- Do not trust a stale `3_state.md` silently: if it contradicts the last log entries, say so in the report and ask which is right.
- Do not auto-pause other active arcs. Multiple active arcs are allowed.
- If status is `done`, warn first: "this arc is done; resuming sets it back to active" — and let the user confirm.
