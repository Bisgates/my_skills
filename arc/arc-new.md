---
name: arc-new
description: Create a new arc (task) and immediately run /arc-objective. Use when the user says "/arc-new <brief>", "新建任务 ...", or similar.
---

# /arc-new — Create a task and lock the objective

A two-step chain: (1) `arc new` builds the skeleton, (2) automatically enter `/arc-objective` to run grill-me.

## Steps for the agent

1. **Parse the brief.** Distill what the user said into a snake-friendly phrase of ≤ 5 English words for the brief. If the user's description is vague ("do something about alignment"), ask one clarifying question first — don't fill in the gap yourself.

2. **Call the CLI:**
   ```bash
   arc new <brief words...>
   # if the user said `track <name>`, pass those two words through:
   arc new <brief words...> track <name>
   ```
   stdout's first line is the 7-char id (e.g. `260430c`); stderr carries the human-readable message. Capture the id from stdout. The command writes `0_meta.md` and seeds `3_state.md`; everything else is created lazily. `track <name>` only changes the parent folder to `arcs/<name>/` — IDs, resume, and the rest stay the same.

3. **Tell the user how to cd in** (don't cd yourself — that pollutes the agent's cwd; let the user decide):
   ```
   ✓ Created arc 260430c.
   To start: cd $(arc cd 260430c)
   ```

4. **Chain into `/arc-objective`.** Run the grill-me flow and write the result into `1_objective.md`, using `~/.claude/skills/arc/templates/1_objective.md` as the skeleton.

## Important

- Do not write `1_objective.md` yourself right after `arc new`. Chain into `/arc-objective` (grill-me style; **how many questions to ask is adaptive to task complexity** — see `arc-objective.md`).
- Do not call `arc touch` after `arc new` — `arc new` already sets `last_active_at`.
- If the user declines to continue with grill-me ("leave it, I'll write the objective later"), stop at step 3 and remind them that "`arc list` will show a `needs 1_objective.md` hint".
