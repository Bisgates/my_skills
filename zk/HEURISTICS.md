# zk — doc-worthy detection heuristics

Used by `zk:from-context` (and any agent at task end) to decide which moments from a task should become zk notes. **This is the heart of the "越用越好用" loop and is expected to evolve.** v0 is intentionally simple; tighten over time as you observe false positives / negatives.

## The core question

> Has this task produced a piece of project-specific knowledge that a future task would benefit from finding pre-distilled?

If yes — write a note. If no — don't.

## Stage 1: type-shaped triggers

Walk through the task transcript and look for these surface patterns, one type at a time. Each pattern tends to map cleanly to one note type.

### concept

Surface signals:
- The user explained what a project-specific term *means* (especially correcting a wrong assumption you made).
- You had to reverse-engineer the meaning of an identifier from code (function name, table column, env var) and the meaning is non-obvious.
- The same term appears with two different meanings in different parts of the codebase, and one is canonical.
- A glossary-style sentence appears: "X is the … in our system."

Anti-signal: the term has a standard industry meaning the same as in this project. (No need for a project-local note; general knowledge suffices.)

### decision

Surface signals:
- "We decided to do X instead of Y because Z."
- A non-trivial trade-off was made and the rationale is implicit in code but explicit in conversation.
- A constraint shaped a design choice and would re-shape future choices unless captured.
- The user explicitly says "remember why we chose this" / "记一下原因".

Anti-signal: the decision is local to one PR / one feature with no cross-project impact, *and* a code comment captures it. (Code comment is enough.)

### gotcha

Surface signals:
- A bug took disproportionately long to find because of a non-obvious environment / tool interaction.
- The user said "watch out for X" / "注意 X 会 …".
- An error message that was misleading and the real cause was elsewhere.
- A workaround had to be applied that no future reader would guess.

Anti-signal: the gotcha is generic to a tool/language (not project-specific). (External docs / Stack Overflow handles it.)

### finding

Surface signals:
- An experiment was run and produced a quantitative result with non-trivial implications.
- A measurement contradicted a prior expectation.
- The user said "this is the conclusion" / "结论是 …".
- An empirical fact was established that the project's strategy / direction depends on.

Anti-signal: the result was a sanity check that confirmed the expected. (Adds no information.)

## Stage 2: cost-of-rediscovery filter

For each candidate from Stage 1, ask:

> If a future task encountered this same situation cold, how long would it take to rediscover this knowledge?

- < 5 minutes → **don't write**. Cheap to re-derive.
- 5–60 minutes → **probably write**. Saves real time.
- \> 60 minutes → **definitely write**. Major value.

This filter prevents overpopulating zk with trivia.

## Stage 3: specificity filter

> Is this knowledge **specific to this project** or its data, or could a generally competent agent figure it out from public information?

- Project-specific → keep candidate.
- General knowledge → drop.

zk is for the irreducibly local; everything else, agent can re-derive from training + docs.

## Stage 4: candidate output format

After Stages 1–3, produce a list. **Do not write any files yet.**

```
proposed zk additions:

1. type=concept   slug=batch-window
   summary: alpha 策略中"批次窗口"是回看 N 个交易日的滚动窗口。
   evidence: user clarified at line 47; used in process/batcher.py.

2. type=finding   slug=x-factor-oos-attenuation
   summary: X 因子在 OOS 上 Sharpe 提升从 +3% 衰减到 +0.5%。
   evidence: experiment exps/2026-04-29-x-factor-oos.

(skip for now: ...)
```

User reviews, accepts/edits/drops. Each accepted candidate becomes one note + one commit.

## Negative heuristics — what *not* to write

- **Status updates** ("today I implemented X"). Not a finding, not project knowledge — git log already has it.
- **TODO lists**. zk is not an issue tracker.
- **Code that should be commented**. If a function needs explanation, the explanation goes near the function.
- **Restatements of the obvious from official docs.**
- **Speculation / things you're not confident about.** Wait until clarified.
- **Single-shot context** (e.g. "I helped the user debug this specific run"). Unless it surfaced a reusable gotcha, skip.

## Update / supersede vs. create

Before creating a new note, always check whether an existing one should be edited or superseded instead:

1. `rg <relevant-term> zk/notes/` — any hits?
2. If a hit covers the same concept and is **roughly correct** → edit in place.
3. If a hit covers the same concept but is **substantially wrong/outdated** → write the new note, set `supersedes: [old-slug]`, mirror `superseded_by` on the old.
4. If a hit covers an **adjacent** concept → write a new note, link with `[[]]`, possibly add to a relevant MOC.
5. If no hit → write fresh.

## Calibration

This file is v0. As you use zk:

- Note when you (the agent) created something that the user later deleted as "not worth a note" → the heuristic was too loose.
- Note when the user said "why didn't you write this down?" → too tight.
- Adjust this file accordingly. Treat it as a living artifact, the same way a zk note itself is.
