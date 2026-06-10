# Generation templates & budgets

Contents: [Token budgets](#token-budgets) · [Extraction report](#extraction-report-mode-2) · [Chapter file](#chapter-file) · [glossary.md](#glossarymd) · [patterns.md](#patternsmd) · [cheatsheet.md](#cheatsheetmd) · [Master SKILL.md](#master-skillmd) · [Fold-in merge rules](#fold-in-merge-rules-mode-4)

## Token budgets

Per-chapter target by `BOOK_TYPE` × `DEPTH` (targets, not hard caps — a dense chapter may run over, a thin one under; never pad):

| | `DEPTH=reference` | `DEPTH=study` |
|---|---|---|
| `BOOK_TYPE=text` | 800–1,200 | 1,000–1,800 |
| `BOOK_TYPE=technical` | 1,200–1,800 | 2,000–3,000 |

`study` depth is earned with content, not a bigger number. The standard sections naturally land ~700–900 tokens; reach the study budget honestly by adding (a) one **Worked Example** reconstructed from the chapter — the single biggest lever, (b) explicit steps/criteria in each framework's "How", (c) a "why it works / failure mode" note on the top 1–2 frameworks. A chapter with no worked example lands below the floor; note that it is thin instead of padding.

Supporting files: glossary ≤ 1,500 · patterns ≤ 2,000 · cheatsheet ≤ 1,200 · master SKILL.md body ≤ 4,000.

## Extraction report (Mode 2)

```markdown
## Extraction Report — <Title>

### Author's Core Frameworks
- **<Framework Name>**: <what it is and when to apply>

### Key Principles
- <Principle>: <actionable rule>

### Techniques & Methods
- <Technique>: <step-by-step or how-to>

### Anti-patterns
- <What to avoid>: <why>

### Suggested Skill Name
`<author-lastname>-<core-concept>` — e.g. `cialdini-influence`

### Chapters Detected
| # | Title | Main Frameworks |
```

## Chapter file

`wisdom/<slug>/chapters/ch<NN>-<slug>.md`. Emphasis by type: `technical` → prioritize Code Examples / Reference Tables, preserve exact syntax; `text` → prioritize Frameworks / Mental Models / Takeaways, omit the technical sections.

```markdown
# Chapter N: <Full Title>

## Core Idea
<1–2 sentences: the single most important thing this chapter teaches>

## Frameworks Introduced
- **<Framework Name>**: <exact formulation — preserve the author's naming>
  - When to use: <specific situation>
  - How: <steps or criteria>

## Key Concepts
- **<Term>**: <precise one-sentence definition>
(5–10 terms)

## Mental Models
<2–4 thinking tools, written as "Use X when Y" or "Think of X as Y">

## Anti-patterns
- **<What to avoid>**: <why it fails>

## Code Examples            *(technical only)*
```<language>
<the most instructive snippet, indentation preserved>
```
- **What it demonstrates**: <one line>

## Reference Tables          *(technical only)*
<comparison matrices / parameter tables / decision tables, as markdown>

## Worked Example            *(DEPTH=study only)*
<one concrete example the author works through — a sample document, dialogue,
filled-in template, before/after, or a decision walked end-to-end. Reconstruct
compactly; never copy long raw passages.>

## Key Takeaways
1. <actionable insight>  (3–7 total)

## Connects To
- **Ch N**: <why related> / **<external concept>**: <connection>
```

## glossary.md

Every significant term, alphabetical. Format: `**Term** — definition (Ch N)`.

## patterns.md

All concrete techniques / design patterns / algorithms:

```markdown
## <Pattern Name>
**When to use**: ...
**How**: ...
**Trade-offs**: ...
```

## cheatsheet.md

The most differentiated layer — it captures the author's **judgment**, not their vocabulary. Anyone can grep the glossary; the cheatsheet is what turns "I know the words" into "I'd act the way the author would". Every line must help the reader *decide* something. Prioritize, in order:

1. **Decision rules** — "When X, do Y, because Z."
2. **Decision trees** (nested bullets or a small table) for >2-branch choices.
3. **Trade-off matrices** — options scored on the dimensions the author cares about.
4. **Thresholds & defaults** — specific numbers the author commits to.
5. **Tells & smells** — fast situation-recognition heuristics.

Avoid term→definition rows (glossary's job) and prose paragraphs (chapters' job). Think: the single printed page you'd keep beside you while working.

## Master SKILL.md

Front-load: compaction truncates from the end, so Core Frameworks come before the indexes.

```markdown
---
name: <slug>
description: "Knowledge base from \"<Full Title>\" by <Author(s)>. Use when applying <author>'s frameworks for <3–6 key topics>, studying the book, or referencing its concepts."
allowed-tools:
  - Read
  - Grep
argument-hint: [topic, framework name, or chapter number]
---

# <Full Title>
**Author**: <Author(s)> | **Pages**: ~<N> | **Chapters**: <N> | **Generated**: <YYYY-MM-DD>

## How to Use This Skill
- No arguments → load the core frameworks below
- A topic → consult the Topic Index, read the relevant chapter file, answer from it
- `ch<N>` → load that chapter file
- "what chapters do you have?" → show the Chapter Index

## Core Frameworks & Mental Models
<~2,000 tokens: the author's most important named frameworks and principles.
Exact names. "Use X when Y", "Prefer X over Y because Z". A toolkit, not a summary.>

## Chapter Index
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-<slug>.md) | <Title> | <fw1>, <fw2> |

## Topic Index
- **<Term>** → ch<N>[, ch<M>]   (alphabetical; every major term)

## Supporting Files
- [glossary.md](glossary.md) · [patterns.md](patterns.md) · [cheatsheet.md](cheatsheet.md)

## Scope & Limits
Covers the source content only; for anything beyond it, say so rather than extrapolating in the author's name.
```

## Fold-in merge rules (Mode 4)

1. **Read the existing skill**: master SKILL.md (chapter/topic indexes, metadata, core frameworks), highest `ch<NN>` in `chapters/`, and the three supporting files.
2. **Classify new content**: revision of an existing chapter's topic → merge into that chapter file and rewrite it; genuinely new material → new `ch<NN>` files numbered after the current highest.
3. **Merge supporting files**: glossary — combine, alphabetize, append chapter refs to existing terms (`(Ch 4, Ch 13)`); patterns — append new ones, keep ≤ ~2,500 tokens; cheatsheet — integrate new decision rules/tables into the existing structure.
4. **Regenerate master SKILL.md**: bump chapter count and Generated date, add new sources, fold the highest-impact new models into Core Frameworks (body stays ≤ 4k tokens), append to Chapter Index, merge Topic Index alphabetically.
5. Then validate / install / commit / report as in Steps 7–9.
