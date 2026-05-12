---
name: arc-plan
description: Generate 2_plan.md based on locked 1_objective.md. Use when the user says "/arc-plan" or "/arc-plan 260430c".
---

# /arc-plan — Write the execution plan

## Steps for the agent

1. **Resolve the arc** — same as `/arc-objective` (id or cwd).
2. **Read `1_objective.md`.** If it does not exist or is still the bare skeleton, stop and tell the user to run `/arc-objective` first.
3. **Pull parent context.** From `0_meta.md`, if `parent` is non-null, read the parent's `2_plan.md` / `9_summary.md` as reference.
4. **Ask 1–3 clarifying questions** (only if needed), each with a recommended answer. If `1_objective.md` is already clear enough, write the plan directly.
5. **Write `2_plan.md`** using `~/.claude/skills/arc/templates/2_plan.md` as the skeleton. Key requirements:
   - **The "Smoke Test First" section is required.** Validate the plan on tiny data first, then run the real experiment. This matches the workspace AGENTS.md emphasis on "data contract / preprocessing first + smoke train".
   - **The "Out-of-Scope" section is required.** "None" is acceptable, but it has to be a considered "none".
   - **Steps are free-form**, not forced into checkboxes; numbered headings with sub-items are fine.
6. **Stage a reporter note.** Append one block to `_drafts/report_notes.md` (`mkdir -p _drafts` on first use):
   ```md
   ## <YYMMDD_HHMM> [plan]
   - strategy: <one line from the Strategy section>
   - steps: <comma-separated step verbs>
   - smoke: <one line from the Smoke Test First section>
   ```
   This pre-stages context for the reporter sub-agent at the end of execute (see `reporter.md`).
7. **Auto-chain into `/arc-execute`.** After `arc touch <id>`, tell the user one line — `Plan ready; entering execute.` — then chain straight into the execute flow per `arc-execute.md`. **Do not** stop and wait for "ready?". The user can interrupt if they want to review `2_plan.md` first.

## Don't

- Do not restate the objective inside the plan — the plan assumes the objective is locked.
- Do not write zero-output steps like "do some investigation". Every step must have an expected output.
- Do not bypass the smoke test and schedule a long run directly (unless the user explicitly says so).
