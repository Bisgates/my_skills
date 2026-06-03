---
name: arc
description: Task management protocol with file-based traces. Use when the user explicitly invokes any /arc-* skill or `arc <subcmd>` CLI. Captures objective, plan, execution log, and finalization for tasks that may run in parallel, pause/resume, or be abandoned with traces preserved.
---

# Arc — Task Management Protocol

## When to use this skill

- The user explicitly invokes `/arc-new <brief>`, `/arc-resume 260430c`, or any `arc <subcmd>` CLI.
- The user describes work worth "filing" — multi-step, needs a paper trail, may span sessions, may be coordinated across multiple agents / terminals.

Common natural-language triggers (Chinese verbatim, kept here so trigger matching works): "新立项 / 立个 arc / 这个事建个任务 / 把这个挂到 arc 上".

**Do not auto-trigger.** This skill is never entered at session start; only when the user explicitly speaks the arc protocol.

## Core invariants (must hold; violations are bugs)

- **Single physical path:** `arcs/all/<id>_<slug>/`. Every cwd / log / cross-task reference must point at this canonical path.
- **Authoritative status:** the `status` field in `0_meta.md` (`active | paused | done | abandoned`). The `arcs/{active,paused,done,abandoned}/` symlink folders are derived views, not data.
- **Status transitions go through the CLI** (`arc pause/resume/status/abandon`). **Agents must never hand-edit `0_meta.md`, never hand-create `ln -s`.**
- **ID references:** users say the 7-char `YYMMDDx` form; the CLI also accepts the full `<id>_<slug>` form for tab-completion.
- **`done` hard gate:** `arc status <id> done` requires `9_summary.html` to exist and be non-empty. This file is always written by the reporter sub-agent — agents never hand-craft it.
- **`abandoned` hard gate:** `--reason "..."` is required.
- **`delete` is a hard delete (no trace preserved):** `arc delete <id>` runs `rm -rf` on the canonical dir, removes every view symlink, and rebuilds the index — no confirmation, no gate. If you want to preserve a paper trail, use `arc abandon`; if you want it gone entirely, use `arc delete`.
- **Multiple `active` arcs are allowed:** each terminal's cwd expresses its own focus; `resume` does not auto-pause anything else.

## File layout

### Project root

```
<project_root>/arcs/
  all/<id>_<slug>/                 # canonical physical location
  paused/   done/   abandoned/     # symlink views (these three states only)
  <id>_<slug>                      # active-state symlinks live directly under arcs/
  index.md                         # auto-generated
```

`active` has no dedicated subdirectory; active symlinks sit directly at `arcs/<id>_<slug>`.

### Inside a single arc

```
arcs/all/<id>_<slug>/
  0_meta.md                 # required; script-managed. frontmatter + ## history + ## log
  1_objective.html          # required; produced by /arc-objective (HTML, grok-simple visual; auto-opens on lock)
  2_plan.md                 # required; produced by /arc-plan (may be 1-3 lines for trivial tasks)
  4_*.md ~ 6_*.md           # free slots, free naming (pivot/eval/blocker/decision_*)
  9_summary.html            # required for `done` state — written by reporter sub-agent (see reporter.md). Auto-opens.
  _tmp/                     # agent-internal scratch — notes for self, dotfiles, intermediate JSON / images. Includes _tmp/report_notes.md (reporter in-flight staging). Never promoted; agents read freely.
  doc/                      # freeform notes (create on demand)
  utils/                    # candidate code worth promoting to the main project (on demand)
  scripts/                  # one-shot scripts, not promoted (on demand)
  output/<YYMMDD_HHMM>_<name>/   # experiment outputs (created by `arc output`)
```

`0_meta.md` carries three things at once: the frontmatter (id / status / parent / last_active_at / ...), `## history` (status-transition trace), and `## log` (execution stream, appended by `arc log`). **`arc log` only writes here**; no separate `3_process_log.md` is maintained any more. Legacy arcs that still have a `3_process_log.md` get auto-migrated into `0_meta.md` on the next CLI touch and the old file is deleted.

**All subdirs are created lazily.** `arc new` / `arc spawn` only writes `0_meta.md`; the agent creates subdirs with `mkdir -p` as it writes files, and `arc output` creates output dirs.

**No loose `.py / .html / .json / .ply` at the arc root.** Keep the root readable to a human glancing in. The routing rule:

- **Code:** potentially reusable → `utils/`; one-shot → `scripts/`.
- **Experiment outputs the user might inspect:** `output/<YYMMDD_HHMM>_<name>/` (created via `arc output <name>`).
- **User-readable freeform notes:** `doc/<name>.md` (literature notes, design docs).
- **Agent-internal scratch:** `_tmp/`. Anything the agent writes for *itself* — its own working notes (`_tmp/report_notes.md`), dotfiles (`_tmp/.cache.jpg`), intermediate JSONs not worth surfacing, throwaway screenshots — goes here. Freeform layout, no schema, never promoted by `/arc-finalize`. The contract: if a file is "for me to read later, not for the user", it lives under `_tmp/`. Keeps the root clean.

**One root-level exemption:** `9_summary.html` is the reporter's single-file HTML output and lives at the arc root by design — it is also the gate file for `done`.

## Phase commands (entry points and sub-skills)

| Phase | Trigger | See |
|---|---|---|
| File a new task | `/arc-new <brief>` | `arc-new.md` |
| Lock the objective | `/arc-objective [<id>]` | `arc-objective.md` |
| Write the plan | `/arc-plan [<id>]` | `arc-plan.md` |
| Execute | `/arc-execute [<id>]` | `arc-execute.md` |
| Restore context | `/arc-resume <id>` | `arc-resume.md` |
| Spawn a child task | `/arc-spawn <brief>` | `arc-spawn.md` |
| Wrap up + promote | `/arc-finalize [<id>]` | `arc-finalize.md` |
| Hard delete (no trace) | `/arc-delete <id>` | `arc-delete.md` |

**Auto-chain after objective.** `/arc-objective` does not stop and ask "what next?".
Once `1_objective.html` is locked (and auto-opened), the agent estimates complexity and either (a) writes
a 1-3 line `2_plan.md` inline and chains directly into execute (trivial task), or
(b) chains into `/arc-plan` for the full plan flow (non-trivial task). User
confirmation is **not** required between phases. See `arc-objective.md` for the
complexity heuristic. The user can always interrupt with `/arc-pause` or by speaking
up — but the default is to keep moving.

**Fast-done after execute (trivial arcs).** When `/arc-execute` finishes a trivial
arc whose acceptance is unambiguously met and where there is **nothing to promote**
(no `utils/`, no `scripts/` worth surfacing, no `doc/`), the agent skips the formal
`/arc-finalize` flow. It tells the user one line, waits for a yes/ok confirmation
**only** (not a full review pass), then dispatches the reporter sub-agent to write
`9_summary.html` and, when that completes, flips the arc to `done` and auto-opens
the HTML. **When in doubt — anything substantive to promote, or acceptance unclear —
take the formal `/arc-finalize` route.** See `arc-execute.md` for the routing
heuristic.

## CLI cheatsheet (for direct agent use)

```bash
arc init                              # bootstrap or migrate; ensures CLAUDE.md (real) + AGENTS.md → CLAUDE.md, appends Arc Protocol hook
arc new <brief...>                    # create skeleton
arc spawn <brief...> [--parent <id>]  # child task
arc pause <id?> --note "..."
arc resume <id>                       # echoes canonical path
arc status <id> {active|paused|done|abandoned} [--note ...] [--reason ...]
arc abandon <id> --reason "..."
arc delete <id>                       # hard-delete canonical + symlinks + rebuild index (no gate)
arc touch <id?>
arc log [-i <id>] <text...>
arc output [-i <id>] <name>           # echoes canonical output dir
arc list                              # prints index.md
arc cd <id>                           # echoes canonical path; usage: cd $(arc cd 260430c)
arc rebuild                           # repair symlinks + index
```

## Agent behavior guidance

- **After every step that has a conclusion** — ran a script, got a number, made a decision — append one `arc log "..."` entry.
- **When writing code**, sort it: potentially reusable → `utils/`; one-shot → `scripts/`. When in doubt, drop it in `scripts/`.
- **For experiment outputs**, first grab a directory with `out=$(arc output <name>)`, then write everything under `$out`. Avoids stray files at the arc root.
- **Default-on agent teams (execute + finalize).** During `/arc-execute` and `/arc-finalize`, identify work units with no data dependency between them and **default to dispatching multiple `general-purpose` sub-agents in parallel within a single message** (do not pass `model`; inherit the parent model so behavior stays consistent). Sub-agents do not write logs themselves; the main agent collects results and calls `arc log` once. Serialize only when there is a real data dependency, a shared mutable file, or an interactive decision needed. See `arc-execute.md` and `arc-finalize.md`. Objective and plan stay single-agent because they are user-facing dialogue.
- **Reporter agent.** During `/arc-plan` and `/arc-execute`, the main agent maintains short notes in `_tmp/report_notes.md` (bullet jots — strategy, smoke result, key decisions, load-bearing artifacts). The reporter sub-agent is dispatched exactly once per arc, when the arc is about to flip to `done`. It fills `templates/9_summary.html` and writes `<arc>/9_summary.html` — the same file is also the `done` gate. There are two dispatch points (same reporter, same template):
  - **Fast-done path** — at the end of `/arc-execute`, after the user confirms with a one-line yes/ok.
  - **Finalize path** — `/arc-finalize` runs a single pass (sweep → print 落盘 suggestions in chat → dispatch reporter; the agent never edits the main project). Before dispatch it appends the suggestions as a `[finalize-suggestions]` block to `_tmp/report_notes.md`, which the reporter folds into the 留下的产物 / 接下来 candidate sections.

  Dispatch is **always** a single `general-purpose` sub-agent **in the background (`run_in_background: true`, non-negotiable)**. The reporter must never block the main flow. On the background completion notification, the main agent verifies the file, calls `arc status <id> done` (gate now passes), runs `open`, and tells the user one short line. Section spine: §1 结果 / §2 过程 (短) / §3+ 自由发挥 (轻 — pick 0-4 of the candidates the template ships with). The reporter is **not** user-invocable; full protocol in `reporter.md`.
- **When the plan does not anticipate the situation**, stop and ask the user. Do not silently rewrite the objective or plan.
- **When boundary instincts fire, suggest a spawn.** If a chunk of work has its own objective and its own acceptance criteria, suggest the user run `/arc-spawn <brief>` — but never spawn unilaterally.
- **Mid-session**: when the user says `pause / abandon / ...`, call the CLI directly. Do not attempt to write status into `0_meta.md` yourself.
