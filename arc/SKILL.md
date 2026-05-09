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
- **`done` hard gate:** `arc status <id> done` requires `9_*.md` to exist and be non-empty.
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
  1_objective.md            # required; produced by /arc-objective
  2_plan.md                 # required; produced by /arc-plan
  4_*.md ~ 7_*.md           # free slots, free naming (pivot/eval/blocker/decision_*)
  8_handoff_plan.md         # generated only by finalize when triggered
  9_summary.md              # required for `done` state
  doc/                      # freeform notes (create on demand)
  utils/                    # candidate code worth promoting to the main project (on demand)
  scripts/                  # one-shot scripts, not promoted (on demand)
  output/<YYMMDD_HHMM>_<name>/   # experiment outputs (created by `arc output`)
```

`0_meta.md` carries three things at once: the frontmatter (id / status / parent / last_active_at / ...), `## history` (status-transition trace), and `## log` (execution stream, appended by `arc log`). **`arc log` only writes here**; no separate `3_process_log.md` is maintained any more. Legacy arcs that still have a `3_process_log.md` get auto-migrated into `0_meta.md` on the next CLI touch and the old file is deleted.

**All subdirs are created lazily.** `arc new` / `arc spawn` only writes `0_meta.md`; the agent creates subdirs with `mkdir -p` as it writes files, and `arc output` creates output dirs.

**No loose `.py / .html / .json / .ply` at the arc root.** All code goes under `utils/` or `scripts/`; all artifacts go under `output/`.

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

## CLI cheatsheet (for direct agent use)

```bash
arc init                              # one-time bootstrap; auto-writes the AGENTS.md hook
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
- **Prefer parallelism during execution.** During `/arc-execute`, identify steps with no data dependency between them and **default to dispatching multiple `general-purpose` sub-agents in parallel within a single message** (do not pass `model`; inherit the parent model so behavior stays consistent). Sub-agents do not write logs themselves; the main agent collects results and calls `arc log` once. See `arc-execute.md`.
- **When the plan does not anticipate the situation**, stop and ask the user. Do not silently rewrite the objective or plan.
- **When boundary instincts fire, suggest a spawn.** If a chunk of work has its own objective and its own acceptance criteria, suggest the user run `/arc-spawn <brief>` — but never spawn unilaterally.
- **Mid-session**: when the user says `pause / abandon / ...`, call the CLI directly. Do not attempt to write status into `0_meta.md` yourself.
