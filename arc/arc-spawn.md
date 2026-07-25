---
name: arc-spawn
description: Spawn a child arc when a separable task is discovered during another arc's execution. Use when the user says "/arc-spawn <brief>" or "把这块拆成新 arc".
---

# /arc-spawn — Spawn a child task

## Steps for the agent

1. **Resolve the parent.**
   - Current cwd is inside some arc? `parent` = that arc.
   - Not inside one? `--parent <id>` is required.
2. **Call the CLI:**
   ```bash
   arc spawn <brief words...>          # parent inferred from cwd
   # or
   arc spawn <brief words...> --parent 260430a
   ```
   Capture the new id from stdout.

3. **Do not chain into `/arc-objective` and do not switch focus.** The intended workflow is "open a new terminal and work on it there."

4. **Short report:**
   ```
   ✓ Spawned arc 260430b (child of 260430a).
   To start working on it: open a new terminal and run /arc-resume 260430b
   (or /arc-objective 260430b if you want to define its goal first).
   ```

5. **Leave one log line on the parent** so the spawn shows up in the parent's trace later:
   ```bash
   arc log -i <parent_id> "[spawn] new child arc 260430b: <brief>"
   ```

## When to suggest `/arc-spawn` vs. adding a step

- Refinement under the same objective → add a step in the current arc, do not spawn.
- A different objective with its own acceptance criteria → suggest spawning.
- Boundary unclear → ask the user "should we split this off?" and let them decide; do not spawn unilaterally.

## Don't

- Do not auto-write `1_objective.md` after spawning (violates the Q8 decision).
- Do not write the `parent` field anywhere other than the child's own meta — the index will show the reverse `children` relation automatically.
- Do not pause the parent on spawn; spawn does not switch focus.
