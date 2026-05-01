<!-- zk:start -->
## zk — project knowledge base

This project uses **zk** (agent-first Zettelkasten) to maintain project-specific concepts, decisions, gotchas, and experiment findings. Both human and agent edit it; agent does most edits.

- **Entry point**: read `zk/index.md` at task start (≤200 lines, auto-generated).
- **Four note types**, each in its own folder under `zk/notes/`:
  - `concepts/` — definitions (e.g. "what 'session' means in this project")
  - `decisions/` — choices + rationale (e.g. "why parquet over csv")
  - `gotchas/` — non-obvious traps (e.g. "macOS symlink + zsh tab-complete")
  - `findings/` — empirical results (e.g. "X factor lifts Sharpe by 0.5% OOS")
- **Linking**: write `[[slug]]`. Slugs are kebab-case, globally unique under `zk/notes/**`.
- **When to write a note** (during task or at task end): if you encountered a
  project-specific concept you had to figure out, a non-obvious gotcha, a
  decision with a rationale worth keeping, or an experiment finding worth
  remembering — write it. If information is insufficient, prefer not to write
  rather than write a vague note.
- **Editing existing notes is free**: improve them as your understanding sharpens.
- **Structural changes** (new note, rename, type change, supersede, split, merge,
  delete) follow the rules in the zk skill — see `~/.claude/skills/zk/SKILL.md`
  (Mac) or `~/.codex/skills/zk/SKILL.md`.
- **Commits**: every doc change is its own commit, prefixed `zk(<type>): ...`.
- **Don't put** code maps, API references, or operation runbooks here — those
  live elsewhere (`docs/`, scripts, READMEs).

Full rules and command reference: read the zk skill's `SKILL.md` and `REFERENCE.md`.
<!-- zk:end -->
