---
name: write-a-skill
description: Authoring guide for new and existing agent skills. Covers description writing, progressive disclosure, file organization, bundled scripts, anti-overfitting, and edit-time refactor escalation. Use when creating, writing, building, or substantially editing a skill.
---

# Writing a skill

This skill is the canonical reference an agent should read before scaffolding a new skill OR before making non-trivial edits to an existing one. Most rules are distilled from Anthropic's upstream [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator); the deltas worth knowing are noted inline.

A skill is three layers of progressive disclosure:

1. **Frontmatter** (`name` + `description`) — always loaded into every session. Budget ≈ 100 words. This is the *only* thing the agent sees when deciding whether to invoke the skill.
2. **SKILL.md body** — loaded only when the agent invokes the skill. Aim for under 500 lines.
3. **Bundled resources** (`scripts/`, `references/`, `templates/`, `assets/`) — loaded by the agent on demand.

Every rule below exists to keep these layers lean and high-signal.

## 1. Description: the only triggering surface

The description is **the only signal** the agent has when picking which skill to load. Write it for triggering, not for documentation.

- Be **pushy**: actively name the situations where this skill should fire, including phrases the user is unlikely to say literally ("when working with PDFs", "when the user mentions onboarding flows"). Don't be passive.
- First sentence: *what the skill does*. Second sentence: *Use when…* with concrete triggers (keywords, file types, contexts, tools, project shapes).
- If a sibling skill is easy to confuse with this one, name the discriminator ("Use ONLY when… Do NOT trigger for…").
- Third person, imperative voice. Max 1024 chars.
- No time-sensitive content (dates, "currently", "this week") — descriptions live forever.

**Good**

```
Extract text and tables from PDF files, fill forms, merge documents.
Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad**

```
Helps with documents.
```

The bad version gives the agent no way to choose between this and any other doc-adjacent skill.

## 2. Body: explain the *why*, not the rules

Today's models are smart. Rigid `ALWAYS` / `NEVER` / `MUST` lines in caps are a yellow flag — they tell the agent *what* without *why*, so the agent can't generalize when reality diverges.

- Lead with reasoning ("we keep timing data in `timing.json` because it's only available at completion time"), then the directive falls out naturally.
- Prefer imperative voice in instructions ("Write…", "Run…") over passive or suggestive voice.
- Define output formats with a concrete template or example, not a prose description.
- Don't write weight-bearing redundancies. If a sentence isn't doing work for the agent's behaviour, delete it.

## 3. File organization & progressive disclosure

- SKILL.md should stay readable end-to-end. **At ~500 lines stop adding content; refactor instead** — promote sections to `references/`, add an in-body table of contents, and leave clear pointers ("for X, see references/x.md").
- Split by domain, not by chronology: one file per framework / cloud / variant rather than `references/part-1.md`, `part-2.md`. This way the agent loads only the relevant one.
- Any reference file over ~300 lines deserves its own table of contents at the top.
- Keep cross-references **one hop deep**. If the agent needs to chain through three files to find an answer, restructure.

## 4. Bundled scripts & assets

Add a script to `scripts/` when:

- The operation is **deterministic** (validation, formatting, parsing, packaging) — saves tokens and removes "did the model regenerate it correctly?" risk.
- You notice the agent generating roughly the same helper across multiple invocations — that's a signal the helper should be sunk into the skill.
- Errors must be handled explicitly and identically every time.

Don't bundle a script just because it *could* exist. If the agent only writes that code once a year, the script is dead weight in the discoverability budget.

`assets/` are user-facing artifacts (HTML viewers, templates, fixtures). `templates/` are scaffolds for new files the skill produces.

## 5. Test cases: write 2-3 realistic prompts

You don't need an automated eval harness to benefit from the eval mindset.

- Draft 2-3 prompts that **real users would actually type** to invoke this skill — including the messy under-specified ones, not just the textbook example. Save them somewhere (commit message, `EVALS.md`, or a sibling note).
- For each, write down what a *good* output looks like — ideally as objective bullet points ("must produce a single HTML file", "must reference Inter font"). Subjective design/writing skills can stay qualitative.
- Mentally run each prompt against the draft skill. Anywhere the skill underspecifies the agent's behavior, fix the skill — not the test.
- For trigger accuracy: imagine 5 *should-trigger* prompts and 5 *should-NOT-trigger near-misses* (prompts that share keywords but actually need a different skill). If your description doesn't cleanly separate them, rewrite the description.

## 6. Anti-overfitting: write for a million invocations

The single biggest authorship trap is tuning the skill until it nails today's three test prompts and then shipping it.

- Every change should generalize to **a million future varied calls**, not these three.
- If you find yourself adding a clause like "when the file is named `foo.csv`, do X" — stop. Either generalize the rule, or move the special case to a reference file.
- After iterating, audit the skill: which lines fire only on your specific test cases? Delete or generalize them.

## 7. Principle of lack of surprise

A skill's behavior must align with what its description promises. Specifically:

- No hidden side effects (writes, network calls, deletions) the description doesn't mention.
- No malware, exploits, or credential exfiltration — even as "examples".
- No agenda smuggling — if the skill's body pushes a worldview the description doesn't disclose, that's a surprise.

## 8. Editing existing skills

The same principles apply to edits. Two extra rules:

- **Audit before adding.** Before tacking on a new section, scan the existing body for instructions that are no longer earning their keep — usage has shifted, the model got better, or a sibling skill now owns that responsibility. Delete first, then add.
- **Refactor escalation.** If a "small change" reveals that the skill is structurally drifting (e.g. SKILL.md crossed 500 lines, two responsibilities are tangled, the description no longer matches the body, three near-duplicate sections exist) — **stop the small change and surface a refactor proposal to the user before continuing**. Don't quietly enlarge a skill that already wants to be split. Examples of refactor proposals: "split this skill into A and B", "promote section X to `references/`", "rewrite the description because the trigger surface changed".

## 9. Authoring checklist

Before considering a skill done:

- [ ] Description names what + when, third person, with concrete triggers
- [ ] Description distinguishes this skill from confusable siblings
- [ ] No `ALWAYS`/`NEVER`/`MUST` in caps without a "because…" attached
- [ ] SKILL.md body under ~500 lines; references split by domain
- [ ] Reference files over ~300 lines have a top-of-file ToC
- [ ] Cross-references are one hop deep
- [ ] No time-sensitive content anywhere
- [ ] 2-3 realistic test prompts run mentally; output expectations written down
- [ ] 5 should / 5 should-not-trigger near-misses imagined; description disambiguates
- [ ] No instructions that only earn their keep on a single test case
- [ ] No undisclosed side effects; behavior matches description

## See also

- Upstream reference: [anthropics/skills · skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — the source of most rules above, plus an automated eval harness we don't currently mirror.
- `<repo>/skill-mgmt/SKILL.md` — lifecycle (install / sync / adopt / new) and the edit-time refactor escalation rule operationalized.
