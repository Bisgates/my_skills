---
name: arc
description: Task isolation and handoff protocol. Work happens inside `arcs/<id>_*/` so the main project stays untouched, and each arc carries enough context (objective, plan, live state, log) that a fresh agent can take over cold. Use when the user invokes /arc-new, /arc-objective, /arc-plan, /arc-execute, /arc-resume, /arc-spawn, /arc-finalize, /arc-delete, or any `arc <subcmd>` CLI — and when they say "立个 arc" / "新立项" / "这个事建个任务" / "把这个挂到 arc 上" / "继续 <id>" / "收尾这个 arc". Do NOT enter at session start, and do not read `arcs/index.md` unless asked.
---

# Arc — Task isolation and handoff protocol

## Why this exists

Two lines, and every rule below serves one of them:

- **A · Isolation.** The arc directory is the only surface the agent writes to. The main project stays read-only for the whole task, so N parallel experiments neither bloat the project nor collide with each other. Promotion (落盘) is the one reverse channel, and the **user** performs it.
- **B · Self-sufficiency.** The arc directory holds enough context that an agent with zero conversation history can pick the task up and continue — objective, plan, current state, and the log of how we got here.

Concretely: (1) don't pollute the project, (2) pin down the objective, (3) pin down the plan, (4) leave a complete context trail in the arc, (5) hand back only what's worth keeping.

Anything in this skill that serves neither line is dead weight — delete it rather than work around it.

## Core invariants (violations are bugs)

- **The main project is read-only during an arc.** Every file the agent creates or edits while working a task lives under the arc dir (`arcs/<id>_<slug>/` or `arcs/<track>/<id>_<slug>/`). This holds for `/arc-execute` as much as for `/arc-finalize` — finalize *suggests* promotions and never performs them. If you find yourself editing a project file, stop and tell the user.
- **Single physical path:** `arcs/<id>_<slug>/`, or `arcs/<track>/<id>_<slug>/` when created with `track <name>`. Track is only a folder name — same ID space, same resume/status/log. No `all/` layer, no state subfolders, no view symlinks. Every cwd / log / cross-arc reference points at the arc dir.
- **Authoritative status:** the `status` field in `0_meta.md` (`active | paused | done | abandoned`), surfaced in `index.md`.
- **Status transitions go through the CLI** (`arc pause/resume/status/abandon`). **Agents never hand-edit `0_meta.md`** — `arc log` is the only writer of its `## log` section.
- **`done` hard gate:** `arc status <id> done` requires a non-empty `9_handoff.md`.
- **`abandoned` hard gate:** `--reason "..."` is required. An abandoned arc is still valuable context ("this road is closed"), which is why it keeps its trace.
- **ID references:** users say the 7-char `YYMMDDx` form; the CLI also accepts the full `<id>_<slug>` form for tab-completion.
- **Multiple `active` arcs are allowed:** each terminal's cwd expresses its own focus; `resume` does not auto-pause anything else.
- **Historical arcs are immutable.** A finished arc is a frozen trace: read it freely, never write into it. To reuse an old arc's code, copy it into the current arc and edit the copy — or promote it into the main project and reference that. Reaching into another arc to "fix" or repoint it is a bug, not a shortcut.

## File layout

```
<project_root>/arcs/
  <id>_<slug>/               # default placement
  <track>/<id>_<slug>/       # optional: same arc, grouped by track
  index.md                   # auto-generated status view
```

Inside one arc — five numbered files, one per requirement:

```
arcs/<id>_<slug>/
  0_meta.md        status + ## history + ## log      written by the CLI only
  1_objective.md   goal + acceptance     (req 2)     locked once by /arc-objective
  2_plan.md        route + spec          (req 3)     locked once by /arc-plan
  3_state.md       live state snapshot   (req 4)     OVERWRITTEN as work proceeds
  9_handoff.md     result + 落盘清单     (req 5)     written once at wrap-up
  4_*.md ~ 6_*.md  free slots (pivot / eval / blocker / decision_*)
  doc/             freeform notes worth keeping
  utils/           code that might deserve promotion
  scripts/         one-shot code, not promoted
  output/<YYMMDD_HHMM>_<name>/   experiment outputs (created by `arc output`)
  _tmp/            agent-internal scratch; never promoted
```

**`3_state.md` is the load-bearing addition.** `## log` is append-only history — it answers *what happened*. A resuming agent needs *where are we now*, and reconstructing that from a long log costs O(log length). `3_state.md` answers it in O(1): where we are in the plan, how to re-run things (env / data paths / commands), facts already settled, and promotion candidates spotted along the way. `arc new` seeds it; `/arc-execute` overwrites it after each plan step.

**No loose `.py / .json / .ply / .html` at the arc root.** Routing: reusable code → `utils/`; one-shot → `scripts/`; experiment output → `output/` (via `arc output <name>`); user-readable notes → `doc/`; anything the agent writes for *itself* → `_tmp/`.

**Subdirs are created lazily** — `arc new` writes only `0_meta.md` and `3_state.md`; `mkdir -p` the rest as you write.

## Phase commands

`/arc-*` are conventions this skill routes, not separately registered slash commands: when the user types one, read the matching file below and follow it.

| Phase | Trigger | See |
|---|---|---|
| File a new task | `/arc-new <brief>` | `arc-new.md` |
| Lock the objective | `/arc-objective [<id>]` | `arc-objective.md` |
| Write the plan | `/arc-plan [<id>]` | `arc-plan.md` |
| Execute | `/arc-execute [<id>]` | `arc-execute.md` |
| Restore context | `/arc-resume <id>` | `arc-resume.md` |
| Spawn a child task | `/arc-spawn <brief>` | `arc-spawn.md` |
| Wrap up + hand off | `/arc-finalize [<id>]` | `arc-finalize.md` |
| Hard delete (no trace) | `/arc-delete <id>` | `arc-delete.md` |

Pause / abandon have no sub-skill — call the CLI directly (`arc pause <id> --note "..."`, `arc abandon <id> --reason "..."`).

**The phases auto-chain.** objective → plan → execute → finalize runs without asking "what next?" between steps; the user gets a one-line status and can interrupt at any point. `/arc-objective` decides plan depth by complexity (trivial tasks get a 1-3 line `2_plan.md` written inline); `/arc-execute` chains into `/arc-finalize` once acceptance is met, and stops to ask when it isn't.

## CLI cheatsheet

```bash
arc init                              # bootstrap arcs/ here; ensures CLAUDE.md + AGENTS.md → CLAUDE.md, appends the protocol hook
arc new <brief...> [track <name>]     # create skeleton (0_meta.md + 3_state.md); echoes the 7-char id. `track <name>` places it under arcs/<name>/
arc spawn <brief...> [--parent <id>]  # child task
arc pause <id?> --note "..."
arc resume <id>                       # echoes canonical path
arc status <id> {active|paused|done|abandoned} [--note ...] [--reason ...]
arc abandon <id> --reason "..."
arc delete <id>                       # hard-delete arc dir + rebuild index (no gate, no trace)
arc touch <id?>
arc log [-i <id>] <text...>           # append one line to 0_meta.md ## log
arc output [-i <id>] <name>           # echoes canonical output dir
arc list                              # rebuilds and prints index.md
arc cd <id>                           # usage: cd $(arc cd 260430c)
arc rebuild                           # rebuild index.md
```

`arc init` operates on cwd only. Nesting an arc tree inside an existing one is a supported workflow: `new` / `spawn` walk up to the nearest root, so running `init` first is how you keep them local. Legacy `arcs/all/` trees flatten themselves on the next `arc init` / `arc new` in that project — never migrate by hand.

## Agent behavior guidance

- **After every step that has a conclusion** — ran a script, got a number, made a decision — append one `arc log "..."` entry.
- **After every completed plan step, overwrite `3_state.md`.** Not per action (that would just be a second log), and not only at the end (the value is being resumable *mid-task*).
- **Record promotion candidates when you create them**, in `3_state.md` 落盘候选. The judgment "this might be worth keeping" is sharpest the moment you write the file; `/arc-finalize` reviews that table instead of reconstructing it.
- **For experiment outputs**, grab a directory with `out=$(arc output <name>)` first, then write everything under `$out`.
- **When the plan does not anticipate the situation**, stop and ask the user. Do not silently rewrite the objective or plan.
- **When boundary instincts fire, suggest a spawn.** If a chunk of work has its own objective and its own acceptance criteria, suggest `/arc-spawn <brief>` — never spawn unilaterally.
- **Mid-session status words** (`pause` / `abandon` / …) go straight to the CLI.
