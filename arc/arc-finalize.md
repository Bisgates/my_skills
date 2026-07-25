---
name: arc-finalize
description: Wrap up an arc — review the promotion candidates in 3_state.md, print the 落盘 suggestions in chat, write 9_handoff.md, and flip the arc to done. The agent never edits the main project; the user promotes whatever they want. Use when the user says "/arc-finalize" or "/arc-finalize 260430c", or when /arc-execute chains in.
---

# /arc-finalize — Hand back what's worth keeping

Finalize is the reverse channel of the arc: everything else in the protocol keeps work *inside* the arc directory, and this step decides what should leave it. The agent only *suggests* — the user promotes, on their own schedule.

There is no approval gate and no handoff-draft file. Because the agent makes no project changes, there is nothing to gate.

## Flow

1. **Resolve the arc** — id or cwd.

2. **Review the 落盘候选 table in `3_state.md`.** It was filled in during execute, when each judgment was freshest. Your job is to *review* it, not to rebuild it:
   - For each row: does it still hold? Is the suggested destination right? Does it collide with something already in the main project (read-only check — `grep` / `ls`, no edits)?
   - Then sweep for what the table missed: `utils/*.py` with no row, `doc/*.md` worth lifting into the project's docs, and knowledge worth recording (stuck > 15 min, a naming convention decided, a paper read, a significant decision) visible in `0_meta.md ## log`.
   - `scripts/` is skipped by default (one-shot). `output/` and `_tmp/` are never promoted.

3. **Print the 落盘 suggestions in chat.** This is the user-facing deliverable. Structure it so they can act directly:
   - **Code to promote** — source → suggested destination, type (new / merge / replace), one line why. Every `utils/*.py` appears exactly once, either here or in the skip list.
   - **Doc proposals** — `[NEW]` / `[UPDATE]` / `[STALE?]` with target paths.
   - **Skipped** — explicitly not worth promoting.
   - **Verification** — was acceptance met? Numbers and paths, not "probably".
   - **Outstanding** — known follow-ups, risks.

   Write "none" for an empty section rather than dropping it.

4. **Write `9_handoff.md`** using `~/.claude/skills/arc/templates/9_handoff.md` as the skeleton — three sections: 结论 / 落盘清单 / 未尽事项. The 落盘清单 is the same table you just printed. **Do not re-tell the process** — that lives in `0_meta.md ## log`, and duplicating it there means two versions to trust.

5. **Close the arc.** `arc log "[handoff] 9_handoff.md written"`, then `arc status <id> done` (the gate now passes). Tell the user one line with the path. Do not open the file.

## Don't

- **Do not edit, create, or move any main-project file.** Finalize suggests; the user promotes. This is the load-bearing invariant — if you find yourself writing into the project, stop.
- Do not rebuild the promotion list from scratch while ignoring `3_state.md` — the table is the point of having recorded it during execute.
- Do not restate the journey in `9_handoff.md`. Result, promotion list, loose ends. Nothing else.
- Do not suggest promoting anything from `output/` (experiment artifacts) or `_tmp/` (agent scratch). You may cite `output/` paths as evidence; never surface `_tmp/`.
- Do not finalize an arc whose acceptance you cannot point at — go back and ask the user instead.
