---
name: arc-resume
description: Resume an arc with full context load and a "where are we" report. Use when the user says "/arc-resume 260430c" or "继续 260430c".
---

# /arc-resume — Restore task context

## Steps for the agent

1. **Flip status via the CLI** (mechanical layer):
   ```bash
   arc resume <id>
   ```
   stdout is the canonical path (`arcs/<id>_<slug>`). stderr is the status-change message.

2. **Tell the user how to cd in** (don't cd for them):
   ```
   To work on it: cd $(arc cd <id>)
   ```

3. **Load context** (read each file only if it exists):
   - `0_meta.md` — pull brief / status history / parent. **Read only the trailing 40 lines** of the `## log` section (use `tail` or `grep` — do not read the whole thing).
   - `1_objective.md` — pull the goal from §01 目标 and acceptance from §03 验收 (L1 metrics + L2 evidence list). Arcs from before the markdown switch may carry `1_objective.html` instead — read whichever exists, stripping tags. If neither is present, the hint is `needs 1_objective.md`.
   - `2_plan.md` — if present.

4. **Print a "restart report"** with this structure:
   ```
   ## Arc 260430c — <brief>
   - status: <prev_status> -> active
   - parent: <parent_id or none>
   - last_active: <ISO>

   ## Goal (from 1_objective.md)
   <one sentence>

   ## Plan summary (from 2_plan.md)
   <bulleted steps, one per line>

   ## Recent activity (last 40 entries of 0_meta.md `## log`)
   <distilled to ~10 lines of key events>

   ## Where we are
   <one sentence: where we got stuck last / how far we got>

   ## Next-step candidates
   - A: ...
   - B: ...
   - C: ...
   ```

5. **Wait for the user to pick a next step.** Do not unilaterally enter `/arc-execute`.

## Don't

- Do not read the full `## log` (it can be long). When deeper context is needed, use `grep` / `Read --offset` to fetch on demand.
- Do not auto-pause other active arcs. Multiple active arcs are allowed.
- If status is `done`, warn the user: "this arc is done; resuming will set it back to active" — and let the user confirm intent.
