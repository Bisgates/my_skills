---
name: spark
description: Pre-implementation design dialogue — turn a fresh idea into a user-approved written design doc before any code is written. Use when the user says "I want to build X", "help me design Y", "let's spec out Z", "brainstorm with me", "/spark", "先把这个想清楚", or is about to start a new feature / component / script / behavior change without an explicit design. Workflow — explore project context, ask one question at a time, propose 2-3 approaches, present the design in sections, write the spec to docs/specs/YYYY-MM-DD-<topic>.md, user reviews, then hand off to planning. Gate before that is done — no implementation code, no scaffolding, no project bootstrap. Distinct from grill-me / grill-with-docs (stress-test an existing plan).
---

# Spark — design before code

A fresh idea ("I want to build X") rarely arrives as a buildable spec. Spark is the gate between "I have an idea" and "I'm writing code": a short, structured dialogue that converts the idea into a written, user-approved design doc.

Extracted and adapted from [obra/superpowers · skills/brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming). The visual-companion browser mode from upstream is intentionally not bundled — see [See also](#see-also).

## Why this exists

When the agent jumps straight to code on an under-specified idea, two failure modes recur:

- The user spends the rest of the session steering after the fact, rolling back assumptions that should have been surfaced upfront.
- The agent ships features no one asked for (YAGNI violations) because it filled the spec gap with its own guesses.

A 5–10 minute spec-first dialogue removes both. The "simple" projects — a todo list, a single utility, a config change — are exactly where unexamined assumptions cause the most waste, so the gate applies even when the idea looks trivial. For genuinely simple ideas, the spec is three sentences; the constraint is *written and approved*, not *long*.

## The gate

Until the user has signed off on a written design doc, hold these:

- No implementation code, no scaffolding, no `npm init` / `cargo new` / equivalent project bootstrap.
- No invoking implementation skills (`frontend-design`, `3dgs_exp_report`, etc.).
- No CI configs, build files, or test scaffolding that presupposes the design.

The terminal state of spark is handing the spec off to a planning step — not to an implementation skill. The next step is usually `grill-me` / `grill-with-docs` (stress-test the spec) or `gsd:plan-phase` (turn it into an executable plan), depending on the project's workflow.

If the user pushes back ("this is too simple for a spec"), agree on a short one rather than skipping. The dialogue is what catches the bad assumption; the document is what survives session resets.

## Workflow

1. **Explore project context first.** Read relevant files, docs, recent commits before asking anything. A question you can answer from the codebase wastes the user's turn.
2. **Scope check.** If the request describes multiple independent subsystems ("a platform with chat, billing, and analytics"), flag this immediately and help decompose. Each sub-piece gets its own spark cycle.
3. **Ask one question at a time.** Prefer multiple-choice over open-ended (easier to answer). Focus on purpose, constraints, success criteria.
4. **Propose 2–3 approaches** with trade-offs. Lead with your recommendation and the reasoning behind it.
5. **Present the design in sections.** Scale each section to its complexity — a few sentences if straightforward, up to ~200 words if nuanced. After each section, confirm it landed before moving on.
6. **Write the spec** to `docs/specs/YYYY-MM-DD-<topic>.md` (user / project conventions override). Commit it.
7. **Self-review the spec** for placeholders, contradictions, ambiguity, scope creep. Fix inline. See [Spec self-review](#spec-self-review).
8. **Hand the spec to the user for review.** Wait for explicit approval; iterate if they request changes.
9. **Hand off to planning** once approved.

### One question per message

Don't bundle three questions in one message. The user answers one and the others get lost or answered shallowly. If a topic needs sub-questions, ask the first, hear the answer, then ask the next.

### Multiple choice beats open-ended

"Should errors be (a) fail-fast with typed exceptions, (b) log-and-continue with sentinels, or (c) something else?" gets a sharper signal than "How do you want errors handled?". Open-ended is fine when the choice space is genuinely unknown; otherwise propose options.

### Design for isolation

When proposing components, each unit should answer three questions cleanly: what does it do, how do you use it, what does it depend on? If consumers must know a unit's internals to use it, the boundary is wrong. Small, well-bounded units are also easier for the agent itself to edit reliably — focused files produce better diffs than tangled ones.

### Working in an existing codebase

Read the current structure before proposing changes; follow existing patterns. When existing code has problems that affect the work in scope (a file that's grown too large, tangled responsibilities), fold targeted improvements into the design — the way a good developer improves code they're already touching. Don't propose unrelated refactors. Stay focused on what serves the current goal.

## Writing the spec

Default path: `docs/specs/YYYY-MM-DD-<topic>.md`. Follow project conventions if they differ (`.planning/specs/`, `docs/rfcs/`, etc.).

Cover these, scaling each section to actual complexity:

- **Problem & goal** — what we're building, why, success criteria
- **Approach** — chosen direction with brief rationale; alternatives considered (and why not)
- **Architecture** — components, data flow, boundaries
- **Error handling** — failure modes that matter
- **Testing** — how we'll know it works
- **Out of scope** — explicit YAGNI calls

Commit the spec immediately so it survives session resets and can be referenced from later planning / implementation work.

## Spec self-review

After writing, re-read the spec with fresh eyes:

1. **Placeholders** — any "TBD", "TODO", incomplete sections, vague requirements?
2. **Internal consistency** — do sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope** — focused enough for a single implementation plan, or does it need further decomposition?
4. **Ambiguity** — could any requirement be read two different ways? If so, pick one and make it explicit.

Fix issues inline; no need to re-run the loop. For large or high-stakes specs, dispatch a `general-purpose` subagent with the prompt at [references/spec-reviewer-prompt.md](references/spec-reviewer-prompt.md).

## User review gate

After the self-review pass, hand the spec to the user with something like:

> "Spec written and committed to `<path>`. Take a look and let me know if anything needs to change before we move to planning."

Wait for an explicit response. If they request changes, edit, re-run the self-review, then re-ask. Only proceed once they approve.

## After approval — hand-off

Spark's job ends at user approval. The next step depends on the project:

- `grill-me` / `grill-with-docs` — optional: stress-test the spec before committing to a plan.
- `gsd:plan-phase` — convert the spec into an executable phase plan (gsd workflow).
- Inline planning — for small specs, write a TODO list directly in the spec doc and start.

Do not invoke implementation skills (`frontend-design`, `3dgs_exp_report`, etc.) directly from spark.

## Anti-patterns

- **"Too simple to need a design."** Every project goes through spark — even three-sentence specs catch bad assumptions. Skipping the gate is where wasted sessions begin.
- **Asking questions the codebase already answers.** Explore first; ask only what reading code can't reveal.
- **Three questions in one message.** One per turn keeps the dialogue tractable and the answers complete.
- **Sliding into implementation mid-dialogue.** Until the spec is written and approved, hold the gate — even if the next step feels obvious.
- **Treating "approve the design" as approval to skip the written spec.** Verbal approval is not the artifact. The committed file is.

## How spark differs from sibling skills

- `grill-me` / `grill-with-docs` stress-test an *existing* plan or design. Spark produces the design that those skills can later challenge. Order: `spark` → spec → (optional) `grill-me` → plan → code.
- `gsd:discuss-phase` is the gsd-workflow equivalent for a phase already on the roadmap. Spark is upstream of that — it produces the spec that becomes the phase.
- `grill-with-docs` already incorporates project docs (CONTEXT.md, ADRs); spark assumes you don't yet have a stable enough idea for those docs to apply.

## See also

- `references/spec-reviewer-prompt.md` — subagent prompt for deeper spec review (optional escalation).
- Upstream source: [obra/superpowers · skills/brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) — the full original, including the visual-companion browser mode. The visual companion requires a local Node.js server (`server.cjs`, `start-server.sh`, etc.) and is not bundled here; if you ever want it, port [`visual-companion.md`](https://github.com/obra/superpowers/blob/main/skills/brainstorming/visual-companion.md) and the `scripts/` directory together — they're tightly coupled.
- `../write-a-skill/SKILL.md` — authoring rules this skill follows.
- `../grill-me/SKILL.md` — what to do *after* a spec exists.
