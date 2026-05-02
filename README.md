# my_skills

Personal AI agent skills, single source of truth.

This repo is the canonical home for every skill the owner authors. Each skill lives as a top-level subdirectory and is exposed to local agent runtimes via symlinks.

## Layout

```
my_skills/
├── skill-mgmt/        ← self-managing tool: install, sync, adopt, new
├── write-a-skill/     ← template/process for authoring new skills
├── arc/               ← task management protocol
├── grill-me/          ← clarification interview protocol
├── ...                ← other adopted skills
├── manifest.txt       ← list of skills (must include skill-mgmt as line 1)
└── README.md
```

## Bootstrap (any machine)

```bash
git clone git@github.com:Bisgates/my_skills.git ~/my_skills   # server: ~/my_skills
                                                              # mac:    ~/project/agent/skills
~/my_skills/skill-mgmt/bin/install
```

That's it. Every skill in `manifest.txt` is now symlinked into `~/.claude/skills/`, `~/.codex/skills/`, and `~/.gemini/antigravity/skills/` (Antigravity [global skills](https://antigravity.google/docs/skills)). Edit any `SKILL.md` in the repo → linked runtimes see the change on the next session (no copy step).

## Daily ops

In any agent session, ask the agent in plain language:

- "新建一个 skill 叫 X" → triggers `skill-mgmt` → scaffolds, links, manifests
- "同步一下 skills" → triggers `skill-mgmt` → `bin/sync`
- "把 ~/.claude/skills/foo 收编进 repo" → triggers `skill-mgmt` → `bin/adopt foo`

Outside an agent session, equivalent shell commands live under `skill-mgmt/bin/`.

## Iterating

Edit any `SKILL.md` directly in the repo (via cursor / vim / agent session). Then:

```bash
cd ~/my_skills
git add . && git commit -am "..." && git push
```

On the other machine: `~/my_skills/skill-mgmt/bin/sync`.

## Non-goals

- Multi-user / team distribution
- Plugin-installed skills (e.g. mem0) — managed by their installers, untouched here
- Runtimes outside Claude / Codex / Antigravity global skills paths — add another target directory in `skill-mgmt/bin/install` if you adopt another tool later
