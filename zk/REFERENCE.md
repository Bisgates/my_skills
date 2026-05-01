# zk — full design reference

Companion to [`SKILL.md`](SKILL.md). Read SKILL.md first for the operational picture; this file is the authority on **why** each rule exists and the corner cases.

## 1. Design axioms

1. **zk holds project-specific *living* knowledge**: concepts, decisions, gotchas, findings. Not code maps, not API references, not runbooks.
2. **Four types only** (extensible if a recurring need appears, but not until then).
3. **Agent is primary writer**, human is occasional editor.
4. **Additions autonomous, deletions deliberate.** "为道日损" — but not lightly.
5. **Each doc change = one git commit.** `git log -- zk/` becomes the cognitive evolution history.
6. **Quality over coverage.** When in doubt, don't write.

## 2. Physical layout

```
zk/
  .zk-config.yaml             # version, limits, slug pattern, type list
  README.md                   # 1-line pointer to AGENTS.md > zk
  index.md                    # auto-generated, ≤ 200 lines
  notes/
    concepts/
    decisions/
    gotchas/
    findings/
  MOC/                        # human-curated maps of content (optional)
  sources/                    # undistilled raw blobs; cite-only, no [[]]
```

`.zk-config.yaml` is the system marker. Tools detecting "is this project zk-enabled?" check for its existence.

## 3. Note specification

### 3.1 Filename and slug

- Kebab-case ASCII (config: `slug_pattern: '^[a-z0-9]+(-[a-z0-9]+)*$'`).
- File extension `.md`.
- Stem == frontmatter `slug` field (verified by lint).
- **Globally unique under `zk/notes/**`.** On collision, refine the slug to be more semantically precise — e.g. `experiment-naming` vs `experiment-naming-for-batches`. Never use `-2` / `-v2` / `-new` style suffixes; those signal the author hasn't sharpened the meaning.

### 3.2 Frontmatter schema

| Field | Required | Type | Constraint |
|---|---|---|---|
| `slug` | yes | string | matches `slug_pattern`; matches filename stem |
| `title` | yes | string | free-form; any language |
| `type` | yes | enum | one of `concept` / `decision` / `gotcha` / `finding`; must match parent folder |
| `summary` | yes | string | one sentence; ≤ 80 chars; per-type template (§3.4) |
| `aliases` | yes | list[string] | search synonyms (see §3.3); **not** categories; can be empty `[]` |
| `supersedes` | yes | list[slug] | other slugs this note replaces; can be empty |
| `contradicts` | yes | list[slug] | other slugs this note is in tension with; can be empty |
| `superseded_by` | auto | list[slug] | maintained automatically as the inverse of `supersedes` |

Notes in `sources/` may use `type: source` and are exempt from the line cap; they are **not linkable** with `[[]]`.

### 3.3 `aliases` semantics

A correct alias answers: "If a future reader searches for *X* trying to find *this specific note*, what would they type?" Includes Chinese/English variants, abbreviations, alternate phrasings.

A wrong alias is a category many notes might share (e.g. `data`, `experiment`). That belongs in folder + MOC, not in `aliases`.

If you ever feel the urge to add a real category field, that's a signal to add `tags:` — but resist: try to express it through MOC first.

### 3.4 `summary` writing templates

| Type | Template | Example |
|---|---|---|
| `concept` | "X 是 Y 的 Z。" | "Batch window 是策略每天回看的天数窗口。" |
| `decision` | "选 X 不选 Y，因为 Z。" | "选 parquet 不选 csv，因为列存查询快 100x。" |
| `gotcha` | "在 X 条件下 Y 会失败，需 Z 规避。" | "macOS 上 zsh 对 symlink tab-complete 会展开真路径，需用 cd -P 规避。" |
| `finding` | "在 X 上观察到 Y，但仅限 Z 条件。" | "OOS 上 batch 加 X 因子仅 +0.5% Sharpe，远低于 IS 的 +3%。" |

Summaries above 80 chars indicate insufficient distillation — split or compress.

### 3.5 Body structure

Body has no required structure beyond what's natural. The per-type templates in `templates/note-*.md` give a recommended layout but are advisory. The hard rules are size (≤ 600 lines) and link form (`[[slug]]` only).

## 4. Linking semantics

### 4.1 Plain `[[slug]]` (in body prose)

Free associative weaving. Use whenever you reference another concept. Resolution: `slug` looked up across `zk/notes/**`. Slugs are globally unique, so no path qualification.

### 4.2 Typed relations (in frontmatter)

Only two relations are typed; all others stay inline.

- **`supersedes` / `superseded_by`**: explicit replacement. Reader behavior: when the agent encounters a note with non-empty `superseded_by`, it should default to reading the newer note unless the task specifically wants the historical version. Maintained bidirectionally — writing `supersedes: [a]` on B requires writing `superseded_by: [b]` on A in the **same commit**.
- **`contradicts`**: open tension, symmetric. Reader behavior: agent must read both notes and surface the contradiction in any output that draws on either side; never silently choose.

### 4.3 What's intentionally *not* a typed relation

- `refines` — too easy to abuse; "B refines A" usually collapses into either supersedes (full replacement) or just an inline `[[]]` reference. Skip until a concrete recurring need appears.
- `related` — equivalent to "the body mentions `[[]]`"; the backlink graph already encodes this. Adding a frontmatter field would be redundant.
- `implements` / `tested-by` / etc. — these belong in code, not zk.

## 5. Lifecycle

There is **no `status` field**. The lifecycle states are:

| State | Implementation |
|---|---|
| Active | default — note exists, no `superseded_by` |
| Replaced | has `superseded_by: [...]` (auto-maintained) |
| Contested | has `contradicts: [...]` |
| Removed | the file is `git rm`-ed (history preserved in git) |

That's the entire taxonomy. No `draft`, no `stub`, no `archived`. If you need to express "this is shaky", say so in prose. If you need to hide something, supersede or delete it.

### 5.1 Why no `stub`

An earlier draft of zk had a stub workflow (placeholder notes for unclear concepts, with structured "known / unclear" body sections). It was rejected as over-structured: the same outcome (capture an uncertainty) is achievable with either (a) skipping the note entirely or (b) writing what you do know plus a prose disclaimer. The stub state added a third location for "things to clarify later" with no proportionate benefit.

## 6. Read protocol

Agent's read flow during a task:

1. **Task start** → read `zk/index.md` (≤ 200 lines, slug + summary per note, grouped by type). This is the project knowledge map.
2. **Project term encountered** → `rg <term> zk/notes/`. The grep hits frontmatter (`slug`/`title`/`aliases`/`summary`) plus body text. Open the matched file.
3. **No grep hit** → check `zk/MOC/` for a relevant map and follow its `[[]]` links.
4. **Still nothing** → don't fabricate. Ask the user, or state the uncertainty in your output.

Do not embed the full `zk/notes/**` corpus into context; rely on the targeted grep + read flow.

## 7. Write protocol

### 7.1 Trigger taxonomy

| Trigger | Description | Default behavior |
|---|---|---|
| T1. Mid-task realization | While doing X, agent sees something doc-worthy. | Auto: small detour, write or edit the note in the same flow. |
| T2. Task end / /arc finalize | At end of work session, distill what was learned. | Run `zk:from-context`: surface candidate list, user reviews, accepted ones become commits. |
| T3. Explicit user request | "Write a note about X." | Auto: just write it. |
| T4. Read-time fix | Reading an existing note, agent spots an error. | Auto: fix in the same edit window, separate commit. |
| T5. Periodic maintenance | Standalone "clean up zk/" session. | `zk audit` proposes a batch; user reviews; agent executes accepted items. |

### 7.2 Autonomy / surface matrix

See [SKILL.md §Autonomy rules](SKILL.md#autonomy-rules) for the operational table. The principle: additions and reversible single-step structural ops are autonomous (git is the safety net); deletions and batch ops require explicit user confirmation.

Operations that touch invariants (slug uniqueness, link integrity, frontmatter schema) **must** go through skill-mediated atomic commits. Plain prose editing can be done directly with the file editor.

### 7.3 Commit discipline

- One logical doc change → one commit.
- Message format: `zk(<type>): <verb> <slug> — <one-line description>`
  - `zk(finding): new batch-x-factor-lifts-sharpe-v2 — OOS only +0.5% Sharpe vs +3% IS`
  - `zk(concept): edit experiment-naming — clarify rolling vs anchored window`
  - `zk(decision): supersede csv-as-trade-format by parquet-as-trade-format`
- Never co-mingle with code changes. If you need to commit code while a doc edit is open, stash one side.

## 8. /arc integration (loose, via AGENTS.md)

**zk does not register hooks into /arc or any other skill.** Instead:

1. `zk-init` writes a `<!-- zk:start --> ... <!-- zk:end -->` block into the project's `AGENTS.md`. The block describes zk's existence, structure, and write rules.
2. Any agent reading `AGENTS.md` (which they do at session start) naturally learns about zk.
3. /arc finalize, by reading `AGENTS.md`, sees the instruction "at task end, consider distilling the task into zk via `zk:from-context`" and runs the workflow if the user is interested.

This is a soft contract, not a hard hook. If compliance turns out to be insufficient (agent often forgets), a hard hook can be added later — but until then, soft is enough and avoids coupling.

The block is idempotent: re-running `zk-init` strips the old block and writes a fresh one between the markers. User-edited content outside the markers is preserved.

## 9. Multi-system dispatch (future-proofing)

A project may host multiple doc systems (e.g. zk plus a separate research notebook). The discovery mechanism is "look at `AGENTS.md`": each system writes its own marker-wrapped section. Agents read all of them and follow the instructions in each. No central registry, no path scanning beyond `AGENTS.md`.

## 10. Bootstrap (Gap D — "完全空" mode)

`zk-init` creates an empty system. The first notes appear organically as tasks happen.

Specifically rejected: scanning existing `docs/` to seed candidates. The whole point of zk is to be a clean, atomic, agent-curated layer; importing an unaudited legacy `docs/` would just relocate the wiki dumping ground.

If you later want to migrate something from legacy docs, do it deliberately one note at a time, distilling rather than copying.

## 11. Obsidian compatibility

- `[[slug]]` and frontmatter are Obsidian-native.
- Slug-only resolution requires Obsidian's "unique note name" link mode (default for new vaults).
- `supersedes` / `contradicts` are not natively rendered by Obsidian, but show up as plain frontmatter — non-destructive.
- Open `zk/` as an Obsidian vault if you want graph view; nothing in the design forces it.

Compatibility is not a hard requirement and won't be defended at the cost of agent ergonomics.

## 12. Currently deferred (the `zk` skill v0 surface)

Implemented:
- `zk-init` script (bootstrap a project)
- Note templates per type
- Default `.zk-config.yaml`, `index.md`, `README.md`
- AGENTS.md injection snippet

**Not yet implemented** — agent does these by following the workflow inline, until the friction justifies a script:
- `zk new <type> <slug>` — create note from template
- `zk lint` — verify invariants
- `zk index` — regenerate `zk/index.md`
- `zk rename` / `zk move` / `zk supersede` / `zk split` / `zk merge` / `zk delete`
- `zk audit` — full-corpus health report
- `zk recent [N]` — recent doc commits
- `zk from-context` — task → candidate distillation

When a recurring inline operation becomes painful, write the script for it. Add it to `bin/`, document in SKILL.md, and remove the manual workflow.
