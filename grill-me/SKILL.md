---
name: grill-me
description: Stress-test a plan, decision, or idea through question waves saved to Markdown files and opened for the user to answer. Use when the user asks to be grilled, invokes grill-me or grilling, or requests a wave-based design interview. Do not use for ordinary factual questions or silently start an interview during implementation.
---

# Grilling in Markdown waves

Build shared understanding by exposing consequential decisions and challenging assumptions. Organize the discussion as a decision tree: ask together all useful questions whose prerequisites are already settled. Dependent questions belong in a later wave, after their prerequisites have answers.

Adapted from [Matt Pocock's grilling skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md). This version uses editable files and a three-wave default limit.

## Start a wave

1. Read the relevant conversation, existing answers, and readily available project facts. Research facts yourself; ask the user about preferences and decisions. Reuse established requirements without asking the user to confirm them again.
2. Choose a unique interview directory in the user's current project or workspace, such as `interviews/<date>_<topic>/`. Keep private interview answers outside a shared skill repository.
3. Write the entire current wave into `wave-1.md`, then `wave-2.md` and `wave-3.md` as needed. Use the user's language, stable question IDs, plain wording, and a recommended answer for each question. Keep the wave focused on consequential uncertainties; do not invent questions to fill a quota. State recommendations so a simple “yes” accepts them.
4. Open the Markdown file with the system's default application. On macOS use a clean environment: `env -i HOME="$HOME" USER="$USER" PATH=/usr/bin:/bin /usr/bin/open "<absolute-file-path>"`. Opening the requested document is the only UI action; do not click, screenshot, or manipulate the editor. If opening is unavailable or fails, provide the absolute file link and say so.
5. Tell the user where the file is and to save their answers and explicitly say when this wave is finished. End the turn. File changes alone do not mean the user has finished; do not poll the file or advance automatically.

## Answer-file format

```markdown
# <Topic> — Wave 1 / 3

Status: awaiting answers
Goal: <what this interview should resolve>
Known decisions: <brief facts already settled>
Instructions: Write beneath each Answer label, save, then tell the agent “wave 1 answered”. “Yes” accepts the recommendation; “skip” leaves a decision open. Blank fields are unanswered.

## W1-Q1 — <one decision>
<Question with enough context to answer. Include concrete alternatives when useful.>

Recommendation: <specific choice, with a short tradeoff if needed>

Answer:


## W1-Q2 — <next independent decision>
<Question>

Recommendation: <specific choice>

Answer:

```

## Resume and finish

When the user explicitly reports completion, read the saved file again and incorporate any answers given in chat. Preserve the user's wording. Do not overwrite an answer file with a regenerated questionnaire; use a new wave file for follow-ups. If file and chat answers conflict and neither clearly supersedes the other, identify that conflict for resolution.

Summarize settled decisions, unresolved points, and assumptions in `summary.md`, referencing question IDs. Distinguish user decisions from agent recommendations. Blank or skipped answers are not consent. Ask follow-ups only when answers expose consequential new questions or leave necessary decisions unresolved; stop early when there are no useful questions left.

The default maximum is three question waves for the same interview. After wave 3, produce the summary and stop asking questions. Additional waves require explicit permission from the user during wave 3 or later. Record the scope of that permission in the summary; a generic “continue” or “answers saved” is not permission to exceed the limit. Do not reset the counter or rename the topic to bypass it. If an extension has no explicit length, add one wave and stop again.

The closing summary should state the resulting design, tradeoffs, open decisions, and the next concrete step. Interview answers are not blanket permission for deployment, spending, configuration changes, or other execution; apply existing authorization and the user's stated scope.
