---
name: skill-mgmt
description: Manage user-authored agent skills in the my_skills repo (single-source-of-truth + symlinks to ~/.claude/skills, ~/.codex/skills, and ~/.gemini/antigravity/skills). Use ONLY when the user explicitly says install/sync/adopt/new/create a skill, sync skills across machines, or asks how to set up the skills repo on a new machine. Do not trigger for general questions about what a particular skill does.
dependencies:
  - write-a-skill
---

# skill-mgmt — Self-managing skill operations

This skill lives at `<repo>/skill-mgmt/` where `<repo>` is the my_skills git repo (`~/project/agent/skills/` on Mac, `~/my_skills/` on the company server). It manages skills via four idempotent shell scripts under `bin/`.

## Architecture (read this first)

- `<repo>/<name>/SKILL.md` is the **only** physical source of truth for any user-authored skill.
- `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, and `~/.gemini/antigravity/skills/<name>` are **symlinks** pointing into the repo ([Antigravity global skills](https://antigravity.google/docs/skills)).
- `<repo>/manifest.txt` lists every top-level skill the user owns. **Line 1 must be `skill-mgmt`** (self-management).
- A skill may declare runtime dependencies in `SKILL.md` frontmatter with `dependencies:` (also accepted: `depends_on:` or `requires:`). Installing a skill installs its recursive dependency closure first.
- Editing a `SKILL.md` in the repo is picked up by every linked agent runtime on the next session — no copy step.
- Cross-machine sync = standard `git push` / `git pull --rebase` against `github.com/Bisgates/my_skills`.

## Conventions

- **Skill body language defaults to English.** Frontmatter (`name` / `description`) and the body of `SKILL.md` are written in English by default — this keeps skills portable across runtimes and consistent with upstream agent-tooling docs. Exceptions: trigger-phrase examples and quoted user utterances may include Chinese verbatim (so trigger matching works); a skill whose *artifact* is intentionally Chinese (e.g. `learn-paper` produces a Chinese HTML) still keeps the spec itself in English and notes the asymmetry explicitly.

## When to invoke (strict triggers)

Trigger this skill when the user says any of:

- "新建 / 创建一个 skill 叫 X"  /  "create a skill X"  /  "scaffold a skill X"
- "同步一下 skills"  /  "sync my skills"  /  "pull skill updates"
- "把 ~/.claude/skills/X 收编 / 纳入 / adopt"  /  "adopt skill X"
- "在这台机器装 / 安装 my skills"  /  "install my skills here"  /  "bootstrap skills on this machine"
- "安装 skill X" / "install skill X" / "rebuild links for X"

Do NOT trigger for:
- Asking what a particular skill does (read that skill's SKILL.md instead)
- Asking only to edit the content of an existing skill can be done by directly editing `<repo>/<name>/SKILL.md`; after the edit, commit + push by default unless the user says not to.
- General git operations on the repo

## Operations

### Op 1 — Install (bootstrap a machine OR rebuild symlinks)

```bash
<repo>/skill-mgmt/bin/install              # install every manifest skill + dependencies
<repo>/skill-mgmt/bin/install <name> [...] # install named skill(s) + dependencies
```

Reads `<repo>/manifest.txt` when no names are passed. When names are passed, treats those names as the requested install set. In both modes it resolves recursive dependencies declared in each skill's frontmatter before linking.

For every resolved skill name, ensures `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, and `~/.gemini/antigravity/skills/<name>` are symlinks → `<repo>/<name>`. Idempotent: existing correct symlinks are skipped; conflicts (real dirs at the target) are warned, not overwritten — the user must run `bin/adopt` or manually move them.

### Op 2 — Sync (pull remote, refresh symlinks)

```bash
<repo>/skill-mgmt/bin/sync
```

Equivalent to `git -C <repo> pull --rebase && <repo>/skill-mgmt/bin/install`. Run on the second machine after pushing changes from the first. Dependency closure is handled by `install`.

### Op 3 — Adopt (move an existing scattered skill into the repo)

```bash
<repo>/skill-mgmt/bin/adopt <name>
```

Looks for a real directory (not symlink) at `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, or `~/.gemini/antigravity/skills/<name>`. When several exist and contents differ, refuses until `diff -rq`; rerun with `--from claude`, `--from codex`, or `--from antigravity`. When identical, adopts using preference claude → codex → antigravity. Otherwise: `mv` the chosen source into `<repo>/<name>`, append `<name>` to `manifest.txt`, then run `install` to refresh symlinks everywhere.

After adopt, the script auto-commits and pushes by default if the repo was clean when the script started.

### Op 4 — New (scaffold a fresh skill)

```bash
<repo>/skill-mgmt/bin/new <name> [<one-line description>]
```

Creates `<repo>/<name>/SKILL.md` from `<repo>/skill-mgmt/templates/SKILL.md.template`. The template follows the [write-a-skill](../write-a-skill/SKILL.md) authoring conventions (frontmatter with strict trigger, optional dependencies, Quick start, Workflows). Appends `<name>` to `manifest.txt`, runs `install`.

After scaffolding, **read `<repo>/write-a-skill/SKILL.md` for full authoring guidance** and finish writing the skill. The script auto-commits and pushes the scaffold by default if the repo was clean when the script started; set `SKILL_MGMT_AUTOCOMMIT=0` when you want to author first and commit once later.

## Dependency format

Declare dependencies only when another skill must be installed for this skill to work correctly at runtime. Keep the list to skill directory names.

```md
---
name: example-skill
description: ...
dependencies:
  - write-a-skill
  - zk
---
```

Supported keys are `dependencies:`, `depends_on:`, and `requires:`. Supported values are a YAML list or a simple comma-separated inline list, for example `dependencies: [zk, arc]`. Missing dependencies are errors; cyclic dependencies are errors.

## Git automation

After successful modifying operations (`new`, `adopt`, and any direct skill edits performed by an agent), commit and push by default. The scripts implement this rule safely:

- If the repo was clean when the script started and the operation created repo changes, run `git add -A`, `git commit -m "..."`, `git pull --rebase`, then `git push`.
- If the repo was already dirty when the script started, skip auto-commit to avoid mixing unrelated edits; report `git status --short` for manual review.
- Set `SKILL_MGMT_AUTOCOMMIT=0` to disable automatic commits.
- Set `SKILL_MGMT_AUTOPUSH=0` to commit locally but skip push.
- `install` usually changes only symlinks outside the repo, so its auto-commit step is normally a no-op.

## Manifest format

`<repo>/manifest.txt`:
- One skill name per line (= subdirectory name in `<repo>`)
- Blank lines and `# comments` are ignored
- **Line 1 must be `skill-mgmt`** — enforces self-management invariant
- Same manifest is shared across all machines; per-machine subsetting is a non-goal

## Gotchas

- **Do not hardcode paths**: all scripts resolve `<repo>` via `$(cd "$(dirname "$0")/../.." && pwd)`. Mac repo lives at `~/project/agent/skills/`, server at `~/my_skills/` — both work.
- **Antigravity + symlinks**: some Antigravity builds have been reported not to traverse symlinked skill folders during discovery ([discussion](https://github.com/vercel-labs/skills/issues/633)). If listed skills never appear after `install`, check the app version/docs or keep a copy under project `.agents/skills/` until symlink support is reliable.
- **Editor atomic-write**: vim/cursor with `write-temp + rename` save mode can replace a symlink with a real file. If `~/.claude/skills/<name>` (or Codex/Antigravity paths) becomes a real dir unexpectedly, an editor wrote through the symlink incorrectly. Recover: `bin/install` will warn; manually `rm` the bad path and re-run install. Set `vim: :set backupcopy=yes` to avoid.
- **Conflict on adopt**: if multiple agent dirs contain diverged copies, adopt refuses until you pick `bin/adopt <name> --from claude|codex|antigravity`.
- **arcs/ is not synced**: `arcs/` (arc task tracking) is in `.gitignore`. Per-machine task state, not shared.

## See also

- `<repo>/write-a-skill/SKILL.md` — how to author a good skill
- `<repo>/README.md` — repo overview and bootstrap instructions
