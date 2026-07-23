---
name: arc-delete
description: Hard-delete an arc (no trace preserved). Use when the user says "/arc-delete <id>", "删除 <id>", "/arc delete <id>", or otherwise explicitly asks to fully remove an arc from disk. For "preserve trace" semantics use /arc-abandon instead.
---

# /arc-delete — Hard-delete an arc

Difference vs. `arc abandon`: `abandon` keeps the arc dir at `arcs/<id>_*` (status flips to `abandoned` in `0_meta.md`) as a trace; `delete` runs `rm -rf` on the arc dir and rebuilds the index — **no trace preserved**.

## When to delete vs. abandon

- **delete** — accidentally created arc / leftover test arc / user explicitly says "wipe it, leave no trace".
- **abandon** — `1_objective.html` / `2_plan.md` was written, experiments were run, but the decision is to stop. Trace is preserved for future review.

## Steps for the agent

1. **Parse the id.** Either the 7-char `YYMMDDx` form or the full `<id>_<slug>`.

2. **Call the CLI:**
   ```bash
   arc delete <id>
   ```

3. **Confirm briefly** after the command prints `arc: deleted <name>.`:
   ```
   ✓ Deleted 260502g_data_dir_inventory_cleanup.
   ```

## Important

- **The CLI has no gate.** It will not refuse just because the arc has `1_objective.html`, `output/`, etc. Intent confirmation is on the user / agent.
- **If user intent is unclear** — e.g. you see the arc already has objective/plan/log — pause first and ask: "delete → no trace; abandon → trace kept as an `abandoned` arc. Which one?" Do not default to deleting.
- **Do not `rm -rf arcs/<id>*` yourself.** Bypassing the CLI skips the `index.md` refresh.
- **No `--reason` accepted.** The trace is being deleted, so there is nowhere to record a reason. If the user supplies a reason or wants to preserve one, suggest they use `arc abandon` instead.
