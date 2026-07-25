---
name: arc-finalize
description: Single-pass wrap-up — sweep the arc for anything worth promoting to the main project (code, docs, new knowledge), print those as 落盘 suggestions in chat, then dispatch the reporter sub-agent to write 9_summary.md. The agent never edits the main project — the user promotes the suggestions themselves. The completion notification handler flips the arc to done. Use when the user says "/arc-finalize" or "/arc-finalize 260430c".
---

# /arc-finalize — Single-pass wrap-up

**The agent never touches the main project.** Finalize surveys the finished arc and hands the user a 落盘 (promotion) suggestion list — what code/docs/knowledge look worth lifting into the main project, and where. The **user** does the actual promoting themselves, on their own schedule.

There is **no approval gate** and **no `8_handoff_plan.md` file**. Because the agent makes no project changes, there is nothing to gate: finalize runs straight through — sweep → print suggestions → dispatch the reporter — and the arc auto-flips to `done` when `9_summary.md` is ready.

## Flow

1. **Resolve the arc** — id or cwd.

2. **Full sweep — default to parallel sub-agents (agent teams ON).** The four scan units below are independent (different files, different outputs, no shared mutable state), so dispatch them to `general-purpose` sub-agents in **one** Agent tool call (no explicit `model` parameter — let them inherit the parent). Each sub-agent reports its findings back as a structured block; the main agent collates them into the single suggestion list it prints in step 3. **Sub-agents do not write any file and do not call `arc log`** — single writer rule, same as `/arc-execute`.
   - **Unit A — `utils/*.py`.** For each file, assess promotion value: worth reusing? pure functions? does it conflict with existing code in the main project? Report a suggestion row per file: source → suggested dest path, modtype (new / merge / replace), one-line why.
   - **Unit B — `scripts/*.py`.** Skip by default; list them and explicitly mark as skipped (one-shot, not promoted).
   - **Unit C — `doc/*.md`.** Decide whether each is worth lifting into the main project's `docs/`. Report `[NEW]` / `[UPDATE]` / `[STALE?]` suggestions with the suggested target path.
   - **Unit D — `0_meta.md ## log`.** Full scan for "stuck >15 min", "naming convention decided", "read a paper", "made a significant decision" → `[NEW]` knowledge suggestions (follows the workspace AGENTS.md "new-knowledge triggers"). Also cross-check `1_objective.md` acceptance (§03 验收 — L1 metrics + L2 evidence bullets): was it met? → the Verification line.

   **When to skip parallelism:** if `utils/`, `scripts/`, and `doc/` are all empty (or only have 1-2 trivial files), do the sweep inline serially — fan-out has overhead not worth it for tiny arcs. Default for normal arcs is parallel.

3. **Print the 落盘 suggestions inline in the chat.** No file is written. Structure it so the user can act on it directly:
   - **Code to promote** — every `utils/*.py` appears exactly once, either as a promote suggestion (source → suggested dest, modtype, why) or in the skip list.
   - **Doc proposals** — `[NEW]` / `[UPDATE]` / `[STALE?]`, each with the suggested target path.
   - **Skipped** — explicitly not worth promoting (incl. `scripts/`).
   - **Verification** — was the acceptance met? (numbers / paths, not "probably").
   - **Risks / outstanding TODOs.**

   Write "none" for an empty section rather than omitting it. Then append the same content as one `## <ts> [finalize-suggestions]` block to `_tmp/report_notes.md` so the reporter folds it into the 留下的产物 / 接下来 sections of `9_summary.md`. (This note is internal reporter plumbing, not a user-facing deliverable — the user-facing surface is the chat.)

4. Call `arc touch <id>`.

5. **Dispatch the reporter sub-agent (background).** Per `reporter.md` Phase B — `general-purpose`, no explicit `model`, `run_in_background: true`. The reporter writes `<arc>/9_summary.md` from the canonical inputs (`1_objective.md`, `2_plan.md`, `_tmp/report_notes.md` incl. the `[finalize-suggestions]` block, `0_meta.md` log, `output/` listing).

6. **Do not flip status here.** The reporter is background. When the completion notification arrives (this turn, later, or mid-conversation), the shared handler in `reporter.md` Phase C verifies the file, calls `arc status <id> done` (gate now passes), and tells the user one line. If you call `arc status <id> done` here, the CLI rejects it because `9_summary.md` does not exist yet.

7. **Report to the user one short line:** "Promotion suggestions above — promote whatever you want into the main project yourself. Drafting `9_summary.md` in the background; will mark done when it lands." Then yield.

## On failure

- If the reporter sub-agent fails on the notification: see `reporter.md` Phase C failure path. The arc stays `active`; the user decides whether to re-dispatch.

## Don't

- **Do not edit, create, or move any main-project file.** Finalize only *suggests* 落盘; the user does it. This is the load-bearing invariant of the new flow — if you find yourself writing into the main project, stop.
- Do not create `8_handoff_plan.md` or any handoff/promotion file. Suggestions live in the chat (plus the internal reporter note). There is no draft to "approve".
- Do not wait for an `approved` reply — there is no approval gate any more. Run straight through to dispatching the reporter.
- Do not call `arc status done` inline — the CLI rejects it until `9_summary.md` exists, and the notification handler in `reporter.md` Phase C is the only place that flips it.
- Do not suggest promoting anything from `output/` (gitignored experiment artifacts) or `_tmp/` (agent-internal scratch). You may reference `output/` paths as evidence; never surface `_tmp/` contents.
- Do not hand-craft `9_summary.md` or any other `9_*` file. The reporter sub-agent owns that slot; hand-writing it defeats the single-writer contract in `reporter.md`.
