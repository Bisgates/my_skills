---
name: extract-wisdom-to-skill
description: Convert books and documents the user owns (PDF, EPUB, DOCX, HTML, Markdown, RTF, MOBI/AZW via Calibre) into a structured knowledge skill — named frameworks, principles, techniques, anti-patterns, per-chapter reference files — written to the my_skills repo under wisdom/<slug>/ and symlinked into every agent runtime. Use when the user runs /extract-wisdom-to-skill <paths> [slug], says "turn this book / doc folder into a skill" / "把这本书提炼成 skill", wants a queryable knowledge base built from documents, or wants to fold new material into an existing wisdom skill. Do NOT trigger for one-off paper-learning HTML (grok / distill), for authoring ordinary skills (write-a-skill / skill-mgmt), or for simply reading or summarizing a document.
dependencies:
  - skill-mgmt
---

# extract-wisdom-to-skill

Turn written knowledge into an agent skill by extracting **structure, not summaries**. A generated skill is not a book report — it is a toolkit of named frameworks (with exact author formulations: "The 5 Whys" ≠ "ask why multiple times"), actionable principles, step-by-step techniques, and anti-patterns, organized so an agent loads only the slice it needs.

Adapted from [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) (MIT — see `scripts/LICENSE.md`). The extraction engine under `scripts/` is vendored from that project.

## Where things live (delta vs upstream — read first)

Upstream writes generated skills to `~/.claude/skills/<slug>/`. **We do not.** Generated skills are first-class citizens of the my_skills git repo, under the `wisdom/` category:

```bash
# Resolve the my_skills repo root from this skill's own symlink
# (works on every machine; never hardcode the repo path):
REPO="$(dirname "$(readlink -f "$HOME/.claude/skills/extract-wisdom-to-skill")")"
# (if running under codex, substitute ~/.codex/skills in the path above)
```

- This converter: `$REPO/extract-wisdom-to-skill/` (repo root, manifest-listed, like any skill).
- Generated skills: `$REPO/wisdom/<slug>/` — **never** directly into `~/.claude/skills/`, never the repo root, never `manifest.txt`.
- Discovery: `$REPO/skill-mgmt/bin/install <slug>` symlinks `~/.claude/skills/<slug>` (and codex / antigravity equivalents) → `$REPO/wisdom/<slug>`. Other machines get the skill via plain `git pull` + `bin/sync`.

This layout keeps generated knowledge versioned, synced across machines, and separable from hand-authored skills.

## Modes

Route on what the user asks:

1. **Full conversion** (default) — paths given, no special instruction → all steps below.
2. **Analyze only** — user says "analyze" / "先看看提取出什么" / "I want to review before generating" → Steps 1–5, emit the extraction report (template in `references/templates.md`), stop. No files generated.
3. **Generate from prior analysis** — an extraction report already exists → skip Steps 3–5, generate from it.
4. **Update / fold-in** — new sources target an existing `wisdom/<slug>` (user names it, or an input path is an existing generated skill) → extract new sources, then merge per the fold-in rules in `references/templates.md`.

## Workflow

### Step 1 — Parse arguments & validate

`<paths>... [slug]`: every argument that is an existing file / directory / glob is an input; a trailing non-path that looks like a slug (lowercase, hyphens) is `SKILL_NAME`. Expand directories and globs to supported files: `.pdf .epub .docx .txt .md .markdown .rst .adoc .html .htm .rtf .mobi .azw .azw3`. No supported files → stop with a clear error. If `$REPO/wisdom/$SKILL_NAME` already exists, this is Mode 4 unless the user says overwrite.

### Step 2 — Ask once

One combined question covering everything interactive, skipping anything the invocation already answered:

1. **Content type** → `BOOK_TYPE`: `technical` (code, tables, formulas — extracted with Docling, ~1.5 s/page) or `text` (prose — pdftotext-class extractors, instant). Unsure → `text`.
2. **Purpose** → `DEPTH`: reference-lookup only → `reference` (lean chapters); applying frameworks / thinking with the author's models → `study` (worked examples, expanded "how"). Default `study`.
3. **Slug**, if not given: propose author-concept (`cialdini-influence`) and title-based (`designing-data-intensive-apps`) candidates; author-concept wins when the book has a strong methodological identity. Must not collide with `$REPO/<slug>` or `$REPO/wisdom/<slug>`.

### Step 3 — Extract text

```bash
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" "$REPO/extract-wisdom-to-skill/scripts/extract.py" \
  <INPUT_PATHS...> --mode <BOOK_TYPE> --install-missing ask
```

Produces `${BOOK_SKILL_WORKDIR:-$TMPDIR/book_skill_work}/full_text.txt` (all sources merged, with source markers) and `metadata.json` (per-source stats, word/page/token counts). The script probes optional Python deps per format and offers fallbacks; `extract.py --check` prints a per-format report of what's installed without processing anything — use it when extraction quality looks off. One bad source is skipped with a warning; the rest still process.

### Step 4 — Cost gate

Read `metadata.json`. Estimate: input ≈ `estimated_tokens` × 1.3; output ≈ chapters × per-chapter budget (matrix in `references/templates.md`) + ~8.5k for SKILL.md/glossary/patterns/cheatsheet. Print one line — sources, pages, tokens, estimated total. If extracted tokens exceed ~150k, pause and confirm before generating; below that, proceed (the user can always say "analyze only").

### Step 5 — Analyze structure

Identify title, author(s), chapter structure, core themes. For sources over ~50k tokens, treat `full_text.txt` as a queryable corpus instead of reading it whole — generation cost should be proportional to the output, not the source:

```bash
grep -n -E "^\s*(Chapter|CHAPTER|第.+章)" "$FULL_TEXT"   # chapter offsets
sed -n '<start>,<end>p' "$FULL_TEXT"                      # one chapter slice
grep -c -i "<framework name>" "$FULL_TEXT"                # verify a framework exists before claiming it
```

Mode 2 stops here with the extraction report.

### Step 6 — Generate the skill

Create `$REPO/wisdom/<slug>/chapters/` and write, following the templates and per-file token budgets in `references/templates.md`:

- `chapters/ch<NN>-<slug>.md` — one per chapter, loaded on demand
- `glossary.md`, `patterns.md`, `cheatsheet.md`
- `SKILL.md` — core frameworks + chapter/topic index, most important content first

Language: generated files default to English; when the source document is Chinese, write the generated skill in Chinese. Either way, preserve the author's exact framework names in their original language.

### Step 7 — Validate

```bash
"$PYTHON_BIN" "$REPO/extract-wisdom-to-skill/scripts/validate_skill.py" "$REPO/wisdom/<slug>/SKILL.md"
```

Fix any ERRORs. The generated `description:` must stay under 1024 chars or codex silently drops the skill.

### Step 8 — Install & commit

```bash
"$REPO/skill-mgmt/bin/install" <slug>          # symlinks into all runtimes
git -C "$REPO" add -- "wisdom/<slug>"
git -C "$REPO" commit -m "wisdom: add <slug> (<Title>, <Author>)"
git -C "$REPO" pull --rebase && git -C "$REPO" push
```

skill-mgmt's git automation rules apply: path-scoped staging only; skip the commit (and tell the user) if `wisdom/<slug>` had uncommitted changes before this run started or the repo is mid-merge/rebase; respect `SKILL_MGMT_AUTOCOMMIT=0` / `SKILL_MGMT_AUTOPUSH=0`. For Mode 4 use message `wisdom: update <slug> (+<what was folded in>)`.

### Step 9 — Cleanup & report

Remove the extraction workdir (`rm -rf "${BOOK_SKILL_WORKDIR:-$TMPDIR/book_skill_work}"`). Report in a few lines: skill path, sources, chapter count, approximate token sizes per file, and the usage pattern (`/<slug>` → core frameworks; `/<slug> <topic>` → relevant chapter; `/<slug> ch<N>` → that chapter).

## Quality rules

1. **Structure, not summaries** — named frameworks, exact formulations, anti-patterns; never chapter recaps.
2. **Author's precision** — keep exact naming and the specific numbers/thresholds the author commits to.
3. **Density over completeness** — a 1,000-token distillation beats a 10,000-token excerpt; never pad to hit a budget.
4. **Practitioner voice** — "Use X when Y", not "The book explains X".
5. **Front-load SKILL.md** — context compaction truncates from the end; most important content first, body under ~4k tokens.
6. **Never copy raw passages** — synthesize; the output is study notes, not a reproduction (also the copyright line: skills of copyrighted works stay in this private repo, never redistributed).
7. **Topic index is load-bearing** — it is how the agent navigates to the right chapter file; every major term maps to its chapter(s).

## See also

- `references/templates.md` — extraction report, chapter / glossary / patterns / cheatsheet / SKILL.md templates, token-budget matrix, fold-in merge rules
- `<repo>/skill-mgmt/SKILL.md` — wisdom/ category mechanics (install, sync, git automation)
