---
name: zk
description: agent-first Zettelkasten knowledge base for code projects. Use when the user asks to set up zk in a project, run `zk init`, sink task learnings into project knowledge, write/edit project-specific concepts/decisions/gotchas/findings, or asks how the zk system works. Do NOT use for code-level documentation (READMEs, API docs, runbooks) — those live elsewhere.
---

# zk — agent-first Zettelkasten

zk maintains **project-specific living knowledge** that an agent ramps up on every session: concepts, decisions, gotchas, experiment findings. Agent edits most of the time; human edits occasionally.

Full design: [REFERENCE.md](REFERENCE.md). Doc-worthy detection heuristics: [HEURISTICS.md](HEURISTICS.md).

## When to invoke (strict triggers)

- "在这个项目里初始化 zk" / "zk init" / "set up project knowledge"
- "把刚才学到的写成 zk note" / "sink this to zk" / "zk this"
- "更新一下 zk 里的 X" / "zk new concept ..."
- "review zk 的 stub / 重复 / 断链" → run `zk audit` or lint workflow
- /arc finalize when AGENTS.md mentions zk → consider distilling task into doc candidates

Do NOT trigger for: code documentation, API references, generated docs, runbooks (those go in `docs/`, READMEs, or scripts).

## Quick start

In a project root:

```bash
~/.claude/skills/zk/bin/zk-init      # idempotent: scaffolds zk/ + injects AGENTS.md section
```

After init, open `zk/index.md` (auto-generated) and start sinking knowledge as it surfaces during tasks.

## Core invariants

These rules govern every operation. Violating them silently corrupts the system.

- **One file per atomic note.** Hard cap **600 lines** (target 50–300). Exception: notes with `type: source` in `zk/sources/` may be longer but **cannot** be `[[]]`-linked, only cited.
- **Four note types**: `concept | decision | gotcha | finding`. Each lives in `zk/notes/<type>/`.
- **Frontmatter is required**, all of these fields:
  - `slug` (= filename stem; kebab-case; **globally unique** under `zk/notes/**`)
  - `title` (free-form, any language)
  - `type` (must match folder)
  - `summary` (≤ 80 chars; one sentence; per-type template — see REFERENCE.md §3.4)
  - `aliases` (search synonyms; **not** cross-cutting categories)
  - `supersedes` / `contradicts` (slug lists; both maintained bidirectionally — see below)
- **Linking is slug-only**: `[[experiment-naming]]`, never `[[concepts/experiment-naming]]`.
- **Reverse relations are auto-maintained.** Writing `supersedes: [old]` on note B must also add `superseded_by: [B]` to note `old`. Same for `contradicts` (symmetric). Always do both sides in the same commit.
- **One doc change = one commit.** Message: `zk(<type>): <op> <slug> — <summary>`. Never bundle with code commits.

## Workflows

### Bootstrap a project

1. `cd <project-root>`
2. `~/.claude/skills/zk/bin/zk-init`
3. Verify: `zk/` exists, `AGENTS.md` has a `<!-- zk:start -->` block.
4. Commit: `git add zk AGENTS.md && git commit -m "zk: init"`.

### Create a new note (no `zk-new` script yet — do it inline)

1. Pick a slug. Verify uniqueness: `rg -l 'slug: <candidate>' zk/notes/`. If hit, refine the slug semantically (don't `-2`).
2. Copy the matching template from `templates/note-<type>.md` into `zk/notes/<type>/<slug>.md`.
3. Fill frontmatter; write summary first (forces clarity).
4. Write body. Use `[[other-slug]]` freely.
5. Lint (see below).
6. Commit alone.

### Edit an existing note

Just edit. No ceremony for body content. If you change `slug` / `type` / `supersedes` / `contradicts`, see the structural-change workflow.

### Structural changes

Operations that can break invariants — do them carefully, in **one atomic commit** each:

| Op | What to do |
|---|---|
| `rename slug` | `git mv` the file, edit frontmatter `slug:`, rewrite all `[[old]]` → `[[new]]` across `zk/**`. |
| `change type` | `git mv` to new type folder, edit frontmatter `type:`. (Slug doesn't change → no link rewrite.) |
| `supersede` | Create or edit the new note with `supersedes: [old]`; **also** add `superseded_by: [new]` to the old note. |
| `contradict` | Add `contradicts: [other]` to both notes. |
| `split` | Create N new notes; in the original, either `supersedes`-mark each new one (if old is fully replaced) OR rewrite the old to be a thin index linking to the new ones. |
| `merge` | Pick a winner; the loser gets `superseded_by: [winner]`; move any unique content into winner. |
| `delete` | **Requires user confirmation.** Then `git rm`; rewrite/remove dangling `[[]]` links. |

### Lint (manual — no `zk-lint` script yet)

Before each commit, sanity-check:
- All `[[xx]]` resolve to a file under `zk/notes/`.
- frontmatter has all required fields.
- `summary` ≤ 80 chars.
- File ≤ 600 lines.
- `slug` is globally unique.
- `supersedes` / `contradicts` are mirrored on the counterpart note.

### Sink current task to zk (`zk:from-context`)

When user says "把刚才学到的写成 zk note" or at /arc finalize:

1. Re-read the conversation/trace; apply the heuristics in [HEURISTICS.md](HEURISTICS.md) to identify candidates.
2. Present a candidate list: `(type, proposed slug, one-line summary)`. **No files written yet.**
3. User accepts/edits/drops per candidate.
4. For each accepted candidate, run "Create a new note" workflow. One commit per note.

## Autonomy rules

| Operation | Autonomy |
|---|---|
| Edit body / non-structural frontmatter | **Auto** |
| New note | **Auto** |
| `supersedes` / `contradicts` (incl. mirroring) | **Auto** (git is the safety net) |
| `rename slug` / change `type` | **Auto** (single atomic commit) |
| `split` / `merge` | **Auto** (single atomic commit) |
| MOC reorganization | **Auto** |
| `delete` | **Confirm with user** |
| Batch operations from `zk audit` | **Confirm** (review batch before executing) |

## Gotchas

- **Don't bundle doc commits with code commits.** `git log -- zk/` should be a clean cognitive history. Stash code work, do the doc commit, unstash.
- **Don't write a vague note just to fill a gap.** If you don't have enough information, leave a `[[]]` to a slug that doesn't yet exist (creates a "wanted link" you can find later via lint) or just note the uncertainty in prose. Quality over coverage.
- **Don't create cross-cutting `tags`** — we only have `aliases` (synonyms for *this* note). Cross-cutting structure goes through folder + `MOC/`.
- **`sources/` is a holding pen, not a destination.** Material there is undistilled. Reference it with citations, not `[[]]`.
- **600-line cap is hard.** When approaching, split rather than negotiate. The cap exists to keep agent-side reading cost bounded.

## See also

- [REFERENCE.md](REFERENCE.md) — full design, frontmatter spec, write protocols, /arc integration model
- [HEURISTICS.md](HEURISTICS.md) — doc-worthy detection (used by `zk:from-context`)
- [`templates/`](templates/) — note templates per type, default config, AGENTS.md snippet
- [`bin/zk-init`](bin/zk-init) — bootstrap script
