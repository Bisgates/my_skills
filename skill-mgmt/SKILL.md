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

- **Skill body language defaults to English.** Frontmatter (`name` / `description`) and the body of `SKILL.md` are written in English by default — this keeps skills portable across runtimes and consistent with upstream agent-tooling docs. Exceptions: trigger-phrase examples and quoted user utterances may include Chinese verbatim (so trigger matching works); a skill whose *artifact* is intentionally Chinese (e.g. `grok` produces a Chinese HTML) still keeps the spec itself in English and notes the asymmetry explicitly.

## When to invoke (strict triggers)

Trigger this skill when the user says any of:

- "新建 / 创建一个 skill 叫 X"  /  "create a skill X"  /  "scaffold a skill X"
- "同步一下 skills"  /  "sync my skills"  /  "pull skill updates"
- "把 ~/.claude/skills/X 收编 / 纳入 / adopt"  /  "adopt skill X"
- "在这台机器装 / 安装 my skills"  /  "install my skills here"  /  "bootstrap skills on this machine"
- "安装 skill X" / "install skill X" / "rebuild links for X"

Do NOT trigger this skill's lifecycle ops for:
- Asking what a particular skill does (read that skill's SKILL.md instead)
- General git operations on the repo

Editing the content of an existing skill is in scope but takes the **Edit** path below, not a `bin/` script. Authoring rules still apply on edits — see Op 5.

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

**Authoring loop (mandatory):**

1. **Before drafting**, the agent reads `<repo>/write-a-skill/SKILL.md` end-to-end. The scaffold is empty on purpose — every section must be written under the principles in that guide (description writing, progressive disclosure, explain-the-why style, anti-overfitting, lack-of-surprise).
2. **While drafting**, mentally run the description against 5 should-trigger and 5 should-not-trigger near-miss prompts; rewrite the description until it disambiguates cleanly. Same for 2-3 realistic body-test prompts.
3. **Before finalizing**, walk the authoring checklist at the bottom of `write-a-skill/SKILL.md`.

The script auto-commits and pushes the scaffold by default if the repo was clean when the script started; set `SKILL_MGMT_AUTOCOMMIT=0` when you want to author first and commit once later.

### Op 5 — Edit (modify an existing skill)

There is no `bin/` script for edits. The agent edits `<repo>/<name>/SKILL.md` (and bundled resources) directly. Edits are still subject to the authoring rules in `<repo>/write-a-skill/SKILL.md` — the same principles apply whether the file is new or 18 months old.

**Pre-edit audit (mandatory before substantive changes):**

1. Read the full current `<repo>/<name>/SKILL.md` plus any referenced bundled files relevant to the change.
2. Re-read `<repo>/write-a-skill/SKILL.md` (or the section governing the area being changed).
3. Look for instructions that no longer earn their keep — model has improved, sibling skill now owns it, the use case died. Delete those before adding new content; an edit is a chance to shed weight, not just to grow.

**Refactor escalation (must follow):**

If a small change reveals that the skill is structurally drifting, **stop the small change and surface a refactor proposal to the user before continuing**. Do not quietly enlarge a skill that wants to be split. Concrete triggers:

- SKILL.md will cross ~500 lines after this edit
- The description no longer accurately describes what the body covers (responsibility creep)
- Two or more responsibilities are tangled in one skill
- Three or more near-duplicate sections exist
- A reference file will cross ~300 lines without a top-of-file ToC
- Cross-references would become more than one hop deep

The escalation looks like: "I started to make change X, but the skill has drifted — I think we should first do Y (split / promote to references / rewrite description). Do you want me to (a) just make the small change, (b) do the refactor first, (c) do both as separate commits?"

**After-edit:** the same auto-commit/push rule from "Git automation" applies. Frontmatter `description` changes always count as substantive — they alter the trigger surface across all runtimes.

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

- `<repo>/write-a-skill/SKILL.md` — authoring guide (mandatory read for Op 4 New and Op 5 Edit)
- Upstream reference: [anthropics/skills · skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — original source of most authoring rules; also ships an automated eval / description-optimization harness we don't currently mirror
- `<repo>/README.md` — repo overview and bootstrap instructions
