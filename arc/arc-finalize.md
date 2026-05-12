---
name: arc-finalize
description: Two-stage finalization — first draft 8_handoff_plan.md (no project changes), then after user "approved", actually promote code/docs and write 9_summary.md. Use when the user says "/arc-finalize" or "/arc-finalize 260430c".
---

# /arc-finalize — Two-stage wrap-up

**Stage 1 only drafts; the main project is not touched.** Move to Stage 2 only after the user replies `approved` (or `approved with changes: ...`).

## Stage 1 — Draft `8_handoff_plan.md`

1. **Resolve the arc** — id or cwd.
2. **Full sweep — default to parallel sub-agents (agent teams ON).** The four scan units below are independent (different files, different outputs, no shared mutable state), so dispatch them to `general-purpose` sub-agents in **one** Agent tool call (no explicit `model` parameter — let them inherit the parent). Each sub-agent reports its findings back as a structured block; the main agent then collates everything into a single `8_handoff_plan.md`. **Sub-agents do not write `8_handoff_plan.md` themselves and do not call `arc log`** — single writer rule, same as `/arc-execute`.
   - **Unit A — `utils/*.py`.** For each file, assess promotion value: worth reusing? pure functions? does it conflict with existing code in the main project? Report a row per file.
   - **Unit B — `scripts/*.py`.** Skip by default, but list them and explicitly mark as skipped. Report a list.
   - **Unit C — `doc/*.md`.** Decide whether each is worth lifting up into the main project's `docs/`. Report `[NEW]` / `[UPDATE]` / `[STALE?]` recommendations.
   - **Unit D — `0_meta.md ## log`.** Full scan for "stuck >15 min", "naming convention decided", "read a paper", "made a significant decision" → trigger `[NEW]` proposals (follows the workspace AGENTS.md "new-knowledge triggers"). Also cross-check `1_objective.md` acceptance: has it been met? → draft the Verification section.

   **When to skip parallelism:** if `utils/`, `scripts/`, and `doc/` are all empty (or only have 1-2 trivial files), do the sweep inline serially — fan-out has overhead that is not worth it for tiny arcs. Default for normal arcs is parallel.
3. **Generate `8_handoff_plan.md`** using `~/.claude/skills/arc/templates/8_handoff_plan.md`. **All four sections must be filled:**
   - Code promote plan (every `utils/*.py` must appear in either the promote table or the skip list, exactly once).
   - Doc proposals — `[NEW]` / `[UPDATE]` / `[STALE?]`.
   - Skipped items (explicitly not promoted).
   - Risks / outstanding TODOs.
4. Call `arc touch <id>`.
5. Report: "Draft is at `8_handoff_plan.md`, please review and reply `approved` or `approved with changes: ...`."
6. **Stop and wait.** **Do not** enter Stage 2.

## Stage 2 — Execute (only after the user says "approved")

Start only when the user explicitly says `approved` or equivalent. If they say `approved with changes: ...`, edit `8_handoff_plan.md` per the changes first, then continue.

1. **Code promote.** Follow the `8_*` table.
   - After each file: `arc log "[promote] utils/<x>.py -> <project>/<path>/<x>.py (<modtype>, <N> lines)"`.
   - Match the main project's local style conventions for that subproject (see workspace AGENTS.md "Code Style").

2. **Doc changes:**
   - `[NEW]` — create the file with the required YAML front-matter (`id / type / domain / summary / status / last_verified / related_code / related_docs`).
   - `[UPDATE]` — apply precise edits; preserve the original YAML front-matter; bump `last_verified` to today.
   - `[STALE?]` — **flag only, do not touch the file**; surface it in the `9_summary.md` "for the user to decide" section.

3. **Do not run a git commit** (the project has no git wired up yet; once it does, this skill needs to extend).

4. **Write `9_summary.md`** using `~/.claude/skills/arc/templates/9_summary.md`. **All six fields must be filled:**
   - TL;DR (≤ 3 lines).
   - Promoted Code (write "none" if applicable).
   - Doc Changes (including unhandled `STALE?` items).
   - Verification (L1 + L2, against `1_objective.md` acceptance).
   - Follow-ups.
   - Doc Suggestions.

5. **Flip status:**
   ```bash
   arc status <id> done
   ```
   If `9_summary.md` does not exist or is empty, the CLI rejects this — you missed step 4.

6. **Report:** done + summary of what changed + any `STALE?` items left for the user.

## On failure mid-Stage-2

- If a promote step errors out:
  - **Do not** call `arc status done` (the arc stays `active`).
  - `arc log "[finalize-failed] <what broke> <what was done so far>"`.
  - Report to the user and wait for instructions (fix / roll back / skip).

## Don't

- Do not touch any main-project file during Stage 1.
- Do not skip `9_summary.md` and call `arc status done` directly in Stage 2 — the CLI rejects it.
- Do not promote anything from `output/` to the main project (gitignored by default — temporary experiment artifacts).
- Do not promote anything from `_tmp/` to the main project, and do not surface `_tmp/` contents in `8_handoff_plan.md` or `9_summary.md`. It is agent-internal scratch by definition.
- Do not leave `8_*` / `9_*` sections empty — write "none" rather than omitting.
