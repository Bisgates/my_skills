---
name: arc-execute
description: Execute the arc's plan from current state, logging progress, until the plan is complete or an unexpected situation arises. Use when the user says "/arc-execute" or "/arc-execute 260430c".
---

# /arc-execute — Execute the plan and leave a trace

## Steps for the agent

1. **Resolve the arc** — id or cwd.
2. **Read context.** `0_meta.md` (frontmatter + history + the `## log` section; only the trailing ~40 lines of log, not the whole thing), `1_objective.html`, `2_plan.md`.
3. **Locate current progress.**
   - What is the last step in `## log` that has a conclusion?
   - Per the plan, what should the next step be?
4. **Default-on agent teams: dispatch parallel sub-agents whenever possible.** Scan the next wave of pending steps in the plan and decide which steps have **no data dependency** between them (independent inputs, independent outputs, no shared mutable intermediate state).
   - **Default is parallel, not serial.** Treat "single agent does this serially" as the exception that needs a reason. If two or more steps are independent, fan them out. **Issue all Agent tool calls in a single message** (this is a hard requirement for concurrency — splitting them across messages serializes them).
   - **Sub-agent selection:** use `general-purpose`, **do not pass an explicit `model` parameter**. `general-purpose` inherits the parent agent's model by default, which keeps "sub-agent model = main model".
   - **Each sub-agent prompt must be self-contained:** arc id and canonical path, the literal text of the step it owns, input file paths, output directory (**the main agent calls `arc output <step_name>` ahead of time and passes the path in**), what numbers / paths to report back, and a word cap (~200 words is good). Sub-agents have none of the current conversation context — give them the background up front.
   - **Single log writer:** sub-agents **do not call `arc log`** and **do not append to `_tmp/report_notes.md`**. After all parallel results come back, the main agent **uniformly** calls `arc log "[<step>] <one-line conclusion>"` once per completed step, and appends a reporter note (see step 5b). This avoids concurrent writes shredding `## log` or the notes file.
   - **Cases that must be serial** (do not parallelize): step A's output is step B's input; multiple steps rewrite the same file (e.g. the same `utils/foo.py`, the same plan annotation); a step needs an interactive user decision; everything before the smoke test has run green; long-running steps (>10 min) are usually run separately too, for easier failure localization.
   - **When in doubt about a specific step, serialize that step.** "Default parallel" applies to clearly independent steps; for genuinely ambiguous cases the cost of getting parallelism wrong (poisoning downstream steps, overwriting artifacts) still outweighs the speedup.
5. **Default to driving all the way through to the end of the plan.** Every time you complete an action that has a conclusion (ran a script, got a number, made a decision), call:
   ```bash
   arc log "[<phase>] <one-line conclusion>"
   ```
   (`arc log` appends to the `## log` section of `0_meta.md` — don't hand-edit the file.)

5b. **Append a reporter note when the step is load-bearing** (smoke pass/fail, key decision, an artifact under `output/` worth highlighting, all-steps-complete). Open `_tmp/report_notes.md` (`mkdir -p _tmp` on first use) and append a short block:
   ```md
   ## <YYMMDD_HHMM> [<tag>]
   - <2-4 bullets, ≤ 5 lines total — numbers, paths, the why>
   ```
   Tags: `smoke`, `decision`, `artifact`, `done`. Skip notes for routine steps that just produced expected outputs — the goal is to pre-stage the report's narrative, not to mirror the full log. See `reporter.md` for the contract the final reporter sub-agent expects.
6. **File code and artifacts in the right place** (subdirs are created lazily — `mkdir -p` before the first write, or use a Write tool that auto-creates parent dirs):
   - One-shot script → `scripts/` (with `argparse` and an entry block).
   - Possibly reusable → `utils/` (pure functions + docstring; no `__main__`).
   - Experiment output → `out=$(arc output <name>)` auto-creates the directory and echoes the path; everything goes under `$out`.
   - Freeform notes → `doc/<name>.md`.
7. **When the plan does not anticipate the situation** (errors, contradictions, decisions needed, the objective wants to change): **stop and ask the user.** For example:
   - "Step 3 came back with RMSE worse than baseline. The plan does not specify what to do when the threshold is missed — how would you like to handle it?"
8. After driving the last step:
   - Call `arc log "[done] all plan steps complete"`.
   - Append a `[done]` reporter note (per step 5b) summarizing the final outcome vs. acceptance.
   - **Route the arc.** Decide between two paths — when in doubt, take the formal `/arc-finalize` route. The cost of running a finalize you did not need is small; the cost of skipping one you needed is lost promotion work.

   **Fast-done route.** Eligible only when **all** of these hold:
   - `1_objective.html` acceptance (§III 验收 — both the L1 metric cards and the L2 evidence list) is unambiguously met by what is already logged in `0_meta.md` (numbers / paths visible, not "probably good").
   - `utils/` is empty or contains only files clearly not worth promoting.
   - `scripts/` is empty or one-shot only (skipped by default anyway).
   - `doc/` is empty.
   - No outstanding `STALE?` or follow-up items.

   On fast-done eligibility:
   - Tell the user one short line: "Plan complete; acceptance met. OK to mark this arc done? (I'll generate `9_summary.html` and auto-open.)"
   - **Wait for a one-line confirmation only** — `yes` / `ok` / `好` / `确认` / `approved`. Do **not** open a review pass; the point of fast-done is no further confirmation overhead beyond a yes.
   - If the user declines (`no, let me check first` / `let's finalize properly`), do **not** dispatch the reporter. Suggest `/arc-finalize` and yield.
   - On confirmation: dispatch the reporter per `reporter.md` Phase B (background, `general-purpose`, no explicit `model`, `run_in_background: true`). Tell the user one line: "Drafting `9_summary.html` in the background; will mark done and auto-open when ready." Then yield. The completion notification handler (`reporter.md` Phase C) flips the status and opens the file.

   **Finalize route.** Anything else — substantive code/docs to promote, acceptance ambiguous, the user prefers the formal flow.
   - Tell the user one short line: "Plan complete. Suggest `/arc-finalize` next." Yield.
   - **Do not** dispatch the reporter here. `/arc-finalize` will dispatch it after its sweep prints the 落盘 suggestions (`arc-finalize.md`).

9. **Reporter completion notification handling.** See `reporter.md` Phase C — single shared handler for both routes. The handler verifies the file, calls `arc status <id> done`, runs `open`, and tells the user one line. Do not duplicate the logic here.

## Don't

- Do not stop and ask "continue?" after every step (unless the plan failed to anticipate the situation).
- Do not scatter `.py / .html / .json` at the arc root (violates the layout invariant).
- Do not silently rewrite `1_objective.html` or `2_plan.md` — if a change is needed, stop and ask.
- Do not start a long run (>10 min) before the smoke run is green.
- Do not commit binaries (images, ply, ckpt) to git; they go under `output/`, which is gitignored.
- Do not parallelize steps that share a data dependency (A's output is B's input → serial; concurrent writes to the same file → serial).
- Do not pass an explicit `model` parameter to parallel sub-agents — let `general-purpose` inherit the parent model so the model stays consistent.
- Do not let multiple sub-agents each call `arc log` (concurrent appends shred `## log`; the main agent is the sole writer).
