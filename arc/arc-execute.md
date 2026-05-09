---
name: arc-execute
description: Execute the arc's plan from current state, logging progress, until the plan is complete or an unexpected situation arises. Use when the user says "/arc-execute" or "/arc-execute 260430c".
---

# /arc-execute — Execute the plan and leave a trace

## Steps for the agent

1. **Resolve the arc** — id or cwd.
2. **Read context.** `0_meta.md` (frontmatter + history + the `## log` section; only the trailing ~40 lines of log, not the whole thing), `1_objective.md`, `2_plan.md`.
3. **Locate current progress.**
   - What is the last step in `## log` that has a conclusion?
   - Per the plan, what should the next step be?
4. **Identify parallelizable steps and dispatch sub-agents by default.** Scan the next wave of pending steps in the plan and decide which steps have **no data dependency** between them (independent inputs, independent outputs, no shared mutable intermediate state).
   - **Default behavior:** dispatch independent steps **in parallel** to multiple sub-agents to speed things up. **Issue all Agent tool calls in a single message** (this is a hard requirement for concurrency — splitting them across messages serializes them).
   - **Sub-agent selection:** use `general-purpose`, **do not pass an explicit `model` parameter**. `general-purpose` inherits the parent agent's model by default, which keeps "sub-agent model = main model".
   - **Each sub-agent prompt must be self-contained:** arc id and canonical path, the literal text of the step it owns, input file paths, output directory (**the main agent calls `arc output <step_name>` ahead of time and passes the path in**), what numbers / paths to report back, and a word cap (~200 words is good). Sub-agents have none of the current conversation context — give them the background up front.
   - **Single log writer:** sub-agents **do not call `arc log`**. After all parallel results come back, the main agent **uniformly** calls `arc log "[<step>] <one-line conclusion>"` once per completed step. This avoids concurrent writes shredding `## log`.
   - **Cases that must be serial** (do not parallelize): step A's output is step B's input; multiple steps rewrite the same file (e.g. the same `utils/foo.py`, the same plan annotation); a step needs an interactive user decision; everything before the smoke test has run green; long-running steps (>10 min) are usually run separately too, for easier failure localization.
   - **When in doubt, serialize.** The cost of getting parallelism wrong (poisoning downstream steps, overwriting artifacts) far exceeds the cost of running serially.
5. **Default to driving all the way through to the end of the plan.** Every time you complete an action that has a conclusion (ran a script, got a number, made a decision), call:
   ```bash
   arc log "[<phase>] <one-line conclusion>"
   ```
   (`arc log` appends to the `## log` section of `0_meta.md` — don't hand-edit the file.)
6. **File code and artifacts in the right place** (subdirs are created lazily — `mkdir -p` before the first write, or use a Write tool that auto-creates parent dirs):
   - One-shot script → `scripts/` (with `argparse` and an entry block).
   - Possibly reusable → `utils/` (pure functions + docstring; no `__main__`).
   - Experiment output → `out=$(arc output <name>)` auto-creates the directory and echoes the path; everything goes under `$out`.
   - Freeform notes → `doc/<name>.md`.
7. **When the plan does not anticipate the situation** (errors, contradictions, decisions needed, the objective wants to change): **stop and ask the user.** For example:
   - "Step 3 came back with RMSE worse than baseline. The plan does not specify what to do when the threshold is missed — how would you like to handle it?"
8. After driving the last step:
   - Call `arc log "[done] all plan steps complete; ready for /arc-finalize"`.
   - Tell the user: "plan complete — suggest `/arc-finalize`."

## Don't

- Do not stop and ask "continue?" after every step (unless the plan failed to anticipate the situation).
- Do not scatter `.py / .html / .json` at the arc root (violates the layout invariant).
- Do not silently rewrite `1_objective.md` or `2_plan.md` — if a change is needed, stop and ask.
- Do not start a long run (>10 min) before the smoke run is green.
- Do not commit binaries (images, ply, ckpt) to git; they go under `output/`, which is gitignored.
- Do not parallelize steps that share a data dependency (A's output is B's input → serial; concurrent writes to the same file → serial).
- Do not pass an explicit `model` parameter to parallel sub-agents — let `general-purpose` inherit the parent model so the model stays consistent.
- Do not let multiple sub-agents each call `arc log` (concurrent appends shred `## log`; the main agent is the sole writer).
