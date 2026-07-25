---
name: arc-execute
description: Execute the arc's plan from current state, logging progress and keeping 3_state.md current, until the plan is complete or an unexpected situation arises. Use when the user says "/arc-execute" or "/arc-execute 260430c".
---

# /arc-execute — Execute the plan and leave a resumable trace

Two things happen in parallel here: the work, and the trace that lets someone else pick the work up. The trace is not overhead — it is half the point of the arc.

## Steps for the agent

1. **Resolve the arc** — id or cwd.
2. **Read context.** `3_state.md` first (it says where we are), then `1_objective.md` and `2_plan.md`. Read `0_meta.md ## log` only when `3_state.md` leaves something unexplained — the log is history, and it can be long.
3. **Drive the plan to the end.** Do not stop and ask "continue?" after every step. After each action that has a conclusion (ran a script, got a number, made a decision):
   ```bash
   arc log "[<phase>] <one-line conclusion>"
   ```
4. **After each completed plan step, overwrite `3_state.md`.** Keep the four sections; replace their contents, do not append:
   - **现在在哪** — which step, what's next, what's blocking.
   - **怎么重跑** — env, data paths, smoke command, full command. Update whenever any of them changes.
   - **已确定的事实** — decisions that won't be revisited, options ruled out, data problems found. One line of reasoning each.
   - **落盘候选** — anything you just wrote that might belong in the main project, with a suggested destination. Record it *now*, while you know why it matters.
5. **File code and artifacts by destination** (`mkdir -p` before first write):
   - One-shot script → `scripts/` (argparse + entry block).
   - Possibly reusable → `utils/` (pure functions + docstring, no `__main__`) — and add a 落盘候选 line.
   - Experiment output → `out=$(arc output <name>)`, everything under `$out`.
   - Freeform notes → `doc/<name>.md`.
   - Notes for yourself → `_tmp/`.
6. **When the plan does not anticipate the situation** (errors, contradictions, a decision that changes the objective): **stop and ask the user.** Example: "Step 3 came back with RMSE worse than baseline. The plan doesn't say what to do when the threshold is missed — how do you want to handle it?"
7. **After the last step:**
   - `arc log "[done] all plan steps complete"`.
   - Final overwrite of `3_state.md` (现在在哪 = 计划已跑完，等待收尾).
   - **Check acceptance** against `1_objective.md` §03 验收 — both the L1 metrics and the L2 evidence, using numbers and paths already in the log, not "probably fine".
     - **Met** → chain into `/arc-finalize` per `arc-finalize.md`. Tell the user one line first: `Plan complete; acceptance met — wrapping up.`
     - **Not met, or ambiguous** → stop and ask. Do not finalize an arc whose acceptance you cannot point at.

## Don't

- **Do not create or edit any file outside the arc directory.** The main project is read-only for the whole task; promotion is the user's move, after `/arc-finalize`.
- Do not silently rewrite `1_objective.md` or `2_plan.md` — if a change is needed, stop and ask.
- Do not turn `3_state.md` into a second log. It is a snapshot: what is true *now*.
- Do not start a long run (>10 min) before the smoke run is green.
- Do not commit binaries (images, ply, ckpt) to git; they live under `output/`, which is gitignored.
- Do not let sub-agents call `arc log` or write `3_state.md` — concurrent appends shred both. Collect their results, then write once yourself.
