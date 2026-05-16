---
name: tester
description: Spawn a parallel background tester subagent that validates the main agent's implementation without blocking the user. Tester reads context and drafts a test plan in parallel with implementation, then runs best-effort validation (existing test suites, code-path tracing, small integration scripts) after main signals done via a marker file. On success the tester is silent; on failure it returns issues to main, which silently fixes and re-verifies (max 2 rounds total), then briefly tells the user "tester 发现 X 已修". Use ONLY when the user appends `/tester` to an implementation request — e.g. "帮我实现 X 功能 /tester", "add feature Y /tester", "refactor module Z /tester". Do NOT trigger for plain code review (use `/codex:review` or `/review`), bug debugging (use `/gsd:debug`), test-suite generation (use `/gsd:add-tests`), or when `/tester` is not explicitly in the user message.
---

# Tester — parallel background validation subagent

Validates an implementation in a background subagent so the user gets their answer fast and the validation never interrupts implementation. On success the tester stays silent; on failure it pings the implementing agent (main) to fix.

## Quick start

User: `帮我实现 X 功能 /tester`

Main agent does, in this order:

1. Pick a unique task id, e.g. `T-$(date +%s)-$$`.
2. Spawn the tester subagent in the **background** with the prompt template below.
3. Implement the feature normally.
4. Write the marker file at `/tmp/tester_done_<TASK_ID>` containing a 1–3 line summary plus `git diff --stat` output.
5. Reply to the user. Do **not** wait for the tester.
6. When tester's completion notification arrives, branch on its message — see [Handling tester output](#handling-tester-output).

The single marker file is the only synchronization primitive. Main writes it; tester polls for it. No inter-agent messaging needed.

## Spawn call

Use the `Agent` tool. The shape is:

- `subagent_type`: `general-purpose` (needs Read + Bash + Edit tools to validate)
- `name`: `tester` (or `tester-r2` for round 2 — see [Re-verify loop](#re-verify-loop))
- `run_in_background`: `true` — non-negotiable; the whole point is to not block main
- `description`: one short phrase like `Validate /tester run`
- `prompt`: the template below with `<…>` placeholders filled in

## Tester prompt template

Substitute `<TASK_ID>`, `<USER_REQUEST>`, `<CWD>`. Pass the rest verbatim — the tester's behaviour depends on it.

```
You are a tester subagent spawned to validate that the main agent's
implementation meets the user's request. You run in parallel with main and
report only at the end.

User's request: <USER_REQUEST>
Working directory: <CWD>
Task id: <TASK_ID>
Done-marker file (main writes this when implementation is complete):
  /tmp/tester_done_<TASK_ID>

Phase 1 — Read context (start immediately, do not wait):
- Read CLAUDE.md / AGENTS.md if present at the repo root, then README,
  then the project manifest (package.json / pyproject.toml / Cargo.toml /
  go.mod — whatever exists).
- Identify the part of the codebase the user's request concerns. Read its
  entry-point files end-to-end. Skim test directories to learn the project's
  test conventions (framework, command, fixtures).
- Draft a test plan in your head: what observable behaviour would prove the
  feature works? What edge cases matter? What's already covered by existing
  tests vs. what needs a new check?

Phase 2 — Wait for main to signal completion:
Bash tool max runtime is 600000ms, so the wait must come in under that. Use:

  timeout 540 bash -c 'until [ -f /tmp/tester_done_<TASK_ID> ]; do sleep 10; done; cat /tmp/tester_done_<TASK_ID>'

If it prints the marker contents, proceed to Phase 3. If it times out (exit
124), retry the same command up to 9 more times (~90 min total wait). If still
no marker after that, complete with the single line:
  TIMEOUT: tester gave up waiting for main to signal done after 90 min.

Phase 3 — Validate (best-effort):
- Read `git diff` (or `git diff <base>...HEAD` if main was on a branch) to see
  exactly what changed.
- Run existing test suites if there are any: `npm test`, `pytest`,
  `cargo test`, `go test ./...`. Use the project's actual command if CLAUDE.md
  or scripts/ specify one.
- Trace the changed code paths by hand. Look for the kind of bugs a static
  reviewer would catch: null deref, off-by-one, wrong variable, missing await,
  type mismatch, unhandled error, race against a parallel write.
- If a tiny standalone script would prove the feature (call a new function
  with representative inputs and check the output), write it under /tmp/ and
  run it. Don't add it to the repo.
- Skip anything that needs user judgement: visual UI feel, copy tone, "is this
  the right product decision", click-through flows that need a logged-in
  browser. Note them as `untested: <reason>` — they are not failures.

Phase 4 — Report (your final completion message):
Output EXACTLY ONE of:

  OK: <one line summarizing what you verified>[. untested: <items>]

  ISSUES:
  - <file:line — what's wrong, suggested fix>
  - <file:line — …>

Hard constraints:
- Do NOT modify code. You validate; main fixes.
- Do NOT message or prompt the user. Your only output channel is this final
  completion message, which returns to main.
- Do NOT spawn further subagents. One level deep is enough.
- Best-effort: `untested:` is a pass with caveats, not a fail. Don't fabricate
  issues to look thorough.
```

## Handling tester output

When the background tester's completion notification arrives, look at the first token of its message:

- **`OK:`** — say nothing user-facing. The user explicitly asked not to be told about passes. Just continue (or end the turn cleanly if there's nothing else to do).
- **`ISSUES:`** — silently apply the smallest fixes that resolve each item, then run the [Re-verify loop](#re-verify-loop).
- **`TIMEOUT:`** — tester gave up. Tell the user once: `tester 等不到 done 信号超时，跳过验证。` Don't respawn — something is wrong with the marker plumbing.

## Re-verify loop

After applying fixes for round 1's `ISSUES:`:

1. Generate a fresh task id, e.g. `T-$(date +%s)-r2`.
2. Spawn a new background tester with `name: "tester-r2"`. Same prompt template, but prepend a one-line note in `<USER_REQUEST>` like `(Round 2 — round 1 reported: <one-line summary>; check those points specifically)`.
3. Write the new marker `/tmp/tester_done_<TASK_ID>` immediately — fixes are already done, no need for tester to wait.
4. On round-2 completion:
   - `OK:` — tell the user once: `tester 发现 <round-1 issues 摘要>，已修。`
   - `ISSUES:` — tell the user once: `tester 发现 <round-1 issues>，尝试修后仍有 <round-2 issues>，请人工确认。`

Stop after round 2. A third round risks chasing the tester's own tail and burning the user's tokens for diminishing returns.

## What tester can / can't / shouldn't do

| Bucket | Examples |
|---|---|
| Can | Run existing test suites; write throwaway integration scripts under `/tmp`; lint/typecheck if the project has them wired; trace code paths; check obvious correctness (return values, error paths, types). |
| Can't | Anything that needs a logged-in browser, real third-party API keys, manual UI judgement, or product decisions only the user can make. Note these as `untested:`. |
| Shouldn't | Modify code (main's job); spawn further subagents (depth explodes); ask the user anything (defeats the silent-validation purpose); fabricate issues to justify its existence. |

## When NOT to spawn tester

`/tester` is a hint from the user, not a hard mandate. Skip the spawn (and tell the user one short line about why) if any of these holds:

- The change is a one-line typo fix or pure rename — there's nothing meaningful to validate.
- The user's request is a question, not an implementation (e.g. `这段代码做什么 /tester`). Answer the question directly.
- The repo has no recognizable test infrastructure AND the change has no observable runtime behaviour (e.g. doc-only edits).
- `/tester` was clearly typo'd or carried over from a previous turn — confirm before spawning.

## Gotchas

- **`run_in_background: true` is non-negotiable.** A foreground spawn blocks main's response, which violates the user's "don't block notifying user" requirement. If the spawn isn't background, the skill is doing nothing useful.
- **Unique task id per spawn.** Reusing a marker filename across `/tester` invocations means an old stale marker triggers a new tester immediately. Use timestamp + something session-unique.
- **Marker contents matter.** Tester reads the marker to know what changed. Write at least: a 1–2 line summary of the user-visible change plus `git diff --stat` output. Without this, tester can only fall back to `git diff` from scratch.
- **Don't `TaskOutput(block=true)` the tester.** Synchronously waiting on tester defeats the design — let the completion notification arrive on its own schedule.
- **Silent on success means silent.** Don't append `✓ tester verified` to the user reply on success — the user asked not to hear about passes. They will hear if and only if a fix happened.
- **Best-effort is the contract.** When tester says `untested: needs manual UI verify`, don't respawn it to chase the untestable. Surface as part of the normal reply if relevant, otherwise stay silent.
- **`/tmp` assumption.** Marker files live in `/tmp`, which works on macOS and Linux. On Windows, swap for `%TEMP%` — but Claude Code is mostly Mac/Linux in practice.
- **One impl, max one round-2 retry.** Hard cap. Three+ rounds means either the issues are subjective or the fixes are wrong; either way, surface to the user.

## See also

- `<repo>/skill-mgmt/SKILL.md` — how this skill is linked into Claude / Codex / Antigravity.
- `<repo>/use_codex/SKILL.md` — different shape: external second-opinion from another model. Use that when you want a *fresh* perspective on the design; use this skill when you want *the same agent family* to verify its own work in parallel.
