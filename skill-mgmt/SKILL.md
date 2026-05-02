---
name: skill-mgmt
description: Manage user-authored agent skills in the my_skills repo (single-source-of-truth + symlinks to ~/.claude/skills, ~/.codex/skills, and ~/.gemini/antigravity/skills). Use ONLY when the user explicitly says install/sync/adopt/new/create a skill, sync skills across machines, or asks how to set up the skills repo on a new machine. Do not trigger for general questions about what a particular skill does.
---

# skill-mgmt — Self-managing skill operations

This skill lives at `<repo>/skill-mgmt/` where `<repo>` is the my_skills git repo (`~/project/agent/skills/` on Mac, `~/my_skills/` on the company server). It manages skills via four idempotent shell scripts under `bin/`.

## Architecture (read this first)

- `<repo>/<name>/SKILL.md` is the **only** physical source of truth for any user-authored skill.
- `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, and `~/.gemini/antigravity/skills/<name>` are **symlinks** pointing into the repo ([Antigravity global skills](https://antigravity.google/docs/skills)).
- `<repo>/manifest.txt` lists every skill the user owns. **Line 1 must be `skill-mgmt`** (self-management).
- Editing a `SKILL.md` in the repo is picked up by every linked agent runtime on the next session — no copy step.
- Cross-machine sync = standard `git push` / `git pull --rebase` against `github.com/Bisgates/my_skills`.

## When to invoke (strict triggers)

Trigger this skill when the user says any of:

- "新建 / 创建一个 skill 叫 X"  /  "create a skill X"  /  "scaffold a skill X"
- "同步一下 skills"  /  "sync my skills"  /  "pull skill updates"
- "把 ~/.claude/skills/X 收编 / 纳入 / adopt"  /  "adopt skill X"
- "在这台机器装 / 安装 my skills"  /  "install my skills here"  /  "bootstrap skills on this machine"

Do NOT trigger for:
- Asking what a particular skill does (read that skill's SKILL.md instead)
- Editing the content of an existing skill (just edit the file in `<repo>/<name>/SKILL.md`)
- General git operations on the repo

## Operations

### Op 1 — Install (bootstrap a machine OR rebuild symlinks)

```bash
<repo>/skill-mgmt/bin/install
```

Reads `<repo>/manifest.txt`. For each skill name, ensures `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, and `~/.gemini/antigravity/skills/<name>` are symlinks → `<repo>/<name>`. Idempotent: existing correct symlinks are skipped; conflicts (real dirs at the target) are warned, not overwritten — the user must run `bin/adopt` or manually move them.

### Op 2 — Sync (pull remote, refresh symlinks)

```bash
<repo>/skill-mgmt/bin/sync
```

Equivalent to `git -C <repo> pull --rebase && <repo>/skill-mgmt/bin/install`. Run on the second machine after pushing changes from the first.

### Op 3 — Adopt (move an existing scattered skill into the repo)

```bash
<repo>/skill-mgmt/bin/adopt <name>
```

Looks for a real directory (not symlink) at `~/.claude/skills/<name>`, `~/.codex/skills/<name>`, or `~/.gemini/antigravity/skills/<name>`. When several exist and contents differ, refuses until `diff -rq`; rerun with `--from claude`, `--from codex`, or `--from antigravity`. When identical, adopts using preference claude → codex → antigravity. Otherwise: `mv` the chosen source into `<repo>/<name>`, append `<name>` to `manifest.txt`, then run `install` to refresh symlinks everywhere.

After adopt, prompt the user to `git add . && git commit -m "adopt <name>" && git push`.

### Op 4 — New (scaffold a fresh skill)

```bash
<repo>/skill-mgmt/bin/new <name> [<one-line description>]
```

Creates `<repo>/<name>/SKILL.md` from `<repo>/skill-mgmt/templates/SKILL.md.template`. The template follows the [write-a-skill](../write-a-skill/SKILL.md) authoring conventions (frontmatter with strict trigger, Quick start, Workflows). Appends `<name>` to `manifest.txt`, runs `install`.

After scaffolding, **read `<repo>/write-a-skill/SKILL.md` for full authoring guidance** and finish writing the skill before committing.

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
