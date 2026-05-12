---
name: problem-first-teach
description: Problem-first teaching loop. Teach a concept by inverting the usual order — design a minimal problem whose solution would prove the user understands, let the user attempt, diagnose the conceptual gap from the attempt, dispatch the grok skill to produce a targeted explanation of just that gap, then pose the next problem. Loop until the user solves correctly. Default to delegating heavy work (problem design, gap diagnosis, grok generation) to subagents so the main conversation window stays free for live dialogue. Use when the user invokes /problem-first-teach, asks "用 problem-first 教我 X", hands you a concrete exercise and says "teach me until I can solve this", or asks for "题目先行 / 先出题再讲 / 解出来才算懂" style teaching. Do NOT trigger for plain explanation requests (use grok), Socratic clarification of vague thinking (use qa), or pure quiz generation with no diagnosis loop.
dependencies:
  - grok
---

# /problem-first-teach — 题目先行的教学环

## Quick start

```
/problem-first-teach 什么是泊松分布
/problem-first-teach @/path/to/exercise.md
/problem-first-teach score matching 的核心
```

Natural-language equivalents that should fire the same skill:

- "用 problem-first 教我 attention"
- "帮我 problem-first 这个概念：rope positional encoding"
- "我做不出这一题，用 problem-first 带我"
- "先出题再讲，教教我 Jacobian"

## Why this skill exists

Standard pedagogy is *explain → practice*. For a CS-PhD-level reader who already follows exposition fluently, that path lies — they nod along to lectures whose ideas they couldn't actually *use*. Inverting to *problem → attempt → diagnose → explain → retry* converts comprehension from self-reported to **empirically demonstrated**. The grok explanation is then targeted at the exposed gap, not the textbook from the start.

The skill exists to operationalize that inversion as a multi-round loop, with the heavy thinking pushed out of the main conversation window so the user can keep talking naturally.

## Agent team (default on)

The main conversation window's role is **dialogue with the user** — receiving the concept, posting problems, collecting answers, posting explanation paths, marking done. All analytical / generative work is dispatched to subagents:

| Subagent | When | Inputs | Outputs |
|---|---|---|---|
| problem-designer | Round 0 (concept → first problem); rounds N≥1 when a new problem is needed | concept text, last diagnosis (if any) | `round_N_problem.md` (shown to user) + `round_N_expected.md` (hidden, sketch for the diagnostician) |
| diagnostician | After each user answer arrives | problem + expected sketch + user's raw answer | `round_N_diagnosis.md` — one of `solved` / `partial` / `stuck`, plus the specific gap |
| grok-explainer | When verdict is `partial` or `stuck` | `round_N_gap.md` written from the diagnosis | absolute path of the generated HTML |

Each subagent is spawned per-round via the Agent tool; do not maintain long-lived personas. Pass the parent's model explicitly (Opus parent → Opus child; Sonnet → Sonnet) — pedagogy degrades when problems and diagnoses are written by a smaller model.

Subagents may invoke the Skill tool (the grok-explainer does this to call `/grok`). The main window does not call grok directly — that pulls grok's chapter-fan-out into the user-facing context.

If the user hands in a concrete problem at invocation time (round 0 is "here is the problem"), skip problem-designer for round 0 — that problem **is** the test.

## Session state

Each invocation opens or resumes a session at:

```
~/.problem_first_teach/<YYMMDD>_<topic-slug>/
```

`<topic-slug>` is a 2–5 word kebab-case slug derived from the concept (`poisson-distribution`, `rope-positional-encoding`, `attention-softmax-temperature`). For a user-supplied exercise rather than a named concept, slug from the exercise's most distinctive phrase.

Layout:

```
~/.problem_first_teach/260512_poisson-distribution/
├── 0_concept.md          # original user request, verbatim
├── state.md              # current round, status, pointer to active artifact
├── transcript.md         # running log of problem + answer + verdict per round
├── round_0_problem.md    # shown to user
├── round_0_expected.md   # hidden — solution sketch for the diagnostician
├── round_0_answer.md     # user's attempt, verbatim
├── round_0_diagnosis.md  # verdict + specific gap
├── round_0_gap.md        # focused source handed to grok (only when not solved)
├── round_0_gap.html      # grok output (sits next to its source)
├── round_1_problem.md
└── …
```

`state.md` is the single source of truth for "where are we":

```yaml
session: 260512_poisson-distribution
round: 0
status: waiting_for_answer   # or: waiting_for_grok, ready_for_next, done
last_artifact: round_0_problem.md
```

**Resume rule.** If a session for the same `<YYMMDD>_<slug>` already exists when the skill is invoked, resume from `state.md` instead of overwriting. If the user invokes with the same concept on a later day, ask whether to start fresh or continue the prior session by path.

## The loop

For each round N starting at 0:

1. **Get a problem.**
   - If round 0 *and* the user provided a concrete exercise, copy verbatim into `round_0_problem.md`. The "expected" sketch may still be useful — have problem-designer produce just `round_0_expected.md` from the given problem.
   - Otherwise dispatch problem-designer. The brief is: *"smallest concrete problem whose correct solution would prove the user understands `<concept>` (or the specific sub-concept named in the prior diagnosis). Tiny numbers, one operation per step, answer holdable on a napkin. The user solving this counts as understanding."* See "Problem design rules" below.

2. **Present and wait.** Main window posts `round_N_problem.md` to the user as chat text (or as a path if the problem is long). Updates `state.md` → `waiting_for_answer`. Returns control. The next user message in this conversation is the answer.

3. **On the user's reply**, save it verbatim to `round_N_answer.md`. Dispatch diagnostician with `(problem, expected, answer)`. The diagnostician returns one verdict in `round_N_diagnosis.md`:
   - `solved` — the conceptual moves are right. Surface arithmetic / notation slips are tolerated; the question is whether they did the *right thing*.
   - `partial` — most of the structure is there but a specific sub-step or sub-concept is off. Diagnosis names the gap precisely.
   - `stuck` — they couldn't make meaningful progress. The gap is upstream of the problem.

4. **Branch on verdict.**
   - `solved` → go to **Termination**.
   - `partial` / `stuck` → continue to step 5.

5. **Write the gap target, then call grok.** Write `round_N_gap.md` framing what grok must explain:
   - The exact gap from the diagnosis (one sentence).
   - One concrete worked-example seed the explanation should land on.
   - A scope fence: "do NOT recap the entire concept; only explain this gap."

   Dispatch grok-explainer. The subagent invokes `/grok <session-folder>` and tells grok the source for this round is `round_N_gap.md`. Skip grok's `--align` step — the source is already scoped tight. Returns the HTML path. Main window posts the path to the user with one line of framing ("Round N gap explanation: `<path>`. Open, read, then your next problem is below.").

6. **Pose round N+1.** Dispatch problem-designer again with the diagnosis as input:
   - For `partial`: default to retrying the same problem; only design a smaller bridging problem if the gap was structural.
   - For `stuck`: design a smaller upstream problem on the prerequisite the user is missing. After they solve the prerequisite, the original problem comes back.

   Loop to step 1 with N+1.

**Termination.** When the diagnostician returns `solved`, append a `## done` marker to `transcript.md`, post a short congratulations to the user that names *what concept moved* (one sentence — not a summary of the whole session), and stop. No grand wrap-up. The artifact is the transcript.

## Within-conversation continuity

Once the skill has been invoked in a conversation, the **next user replies are answers to the current round** by default. The agent should:

- Check `~/.problem_first_teach/<active-session>/state.md` before responding to a user message that came in after a problem was posted.
- If `status: waiting_for_answer`, treat the user's reply as `round_N_answer.md` and dispatch the diagnostician.
- If the user clearly wants out — "停了 / 我先放放 / 不玩了 / 换个话题" — write `status: paused` to `state.md` and stop. Don't drag them back into the loop.

## Problem design rules (Karpathy-grade)

These are the standards problem-designer must hit. Inline them in the subagent brief.

- **Tiny dimensions.** 1D, 2D, or 2×2. Never 7D when 2D exercises the same concept.
- **Tiny numbers.** `0, 1, 2, ½, π/4`. Never `0.7234`.
- **One operation per step.** The solution should run in 3–5 lines, each line a single move. If you can't extract a one-line takeaway from solving it, the problem was too large.
- **Concrete before abstract.** The problem instantiates the concept; the user is computing, not just stating.
- **One concept per problem.** Don't bundle two ideas into one test.
- **The expected sketch is honest.** `round_N_expected.md` records the actual minimal solution path so the diagnostician can compare against the user's answer line-by-line. Not "the answer is 5"; the full move sequence.

## Communication contract with the user

- **Main window writes no teaching prose.** Its messages are routing: "Round N problem ↓", "Got it, diagnosing…", "Explanation at `<path>` — when you're ready, round N+1 below", "Solved — that one needed `<the move>`. Done."
- **No spoilers.** Never reveal `expected.md` or `diagnosis.md` content in chat. The user sees the problem, then either the grok HTML or the success signal. Diagnostic details stay on disk.
- **One round at a time.** Don't pre-queue multiple problems. Round N+1 is designed only after round N is diagnosed.
- **Don't lecture between rounds.** If the user asks a question between rounds ("是不是该用 X？"), redirect gently: "试试看，你的解答就是数据点。" The diagnosis comes from their attempt, not from a chat exchange.

## Test prompts (mental eval before shipping)

**Should trigger:**
1. `/problem-first-teach 什么是泊松分布`
2. "用 problem-first 教我 score matching"
3. "我做不出这道题（attached），problem-first 带我一遍"
4. "先出题再讲，教教我 RoPE 位置编码"
5. "帮我搞懂 KL divergence，但我要解出题目才信"

**Should NOT trigger (near-misses):**
1. "解释一下 attention" → plain explanation; grok if heavy
2. "给我出 5 道关于 attention 的题" → quiz only, no diagnosis loop
3. "我想搞懂这篇 paper" → grok (paper-learning HTML)
4. "苏格拉底式问我几个问题" → qa
5. "wwxd 这个概念怎么样" → multi-expert analysis, not test-driven

If a prompt sits ambiguously between this and grok or qa, the discriminator is: **does the user expect to be tested before being explained to?** If yes → this skill. If no → grok or qa.

## Gotchas

- **grok is overkill for a 1-point gap.** When the diagnosis is "user forgot the factorial in the denominator", a 6-chapter magazine HTML is silly. Write `round_N_gap.md` to be scoped tight — 1 idea, 1 worked example needed. Grok's `--align` step is normally skipped here because the source is already narrow. If the same gap recurs across multiple rounds, the next gap.md should escalate to "*why does this keep slipping?*" instead of re-running the same explanation.
- **Don't auto-rerun a same-day session.** If the slug matches an existing session for today, resume from `state.md`. If the user explicitly wants a fresh start, they will say so (or use a more specific concept slug).
- **Subagent model parity is load-bearing.** Pass the parent's model to every Agent tool call. An Opus parent dispatching to default-Sonnet subagents produces shallower problems and weaker diagnoses; the loop converges slower (or stalls).
- **Don't conflate sloppy formatting with not-understanding.** The diagnostician should look for the right *conceptual moves* in the answer (did they compute the log-density? did they take the gradient? did they substitute x=2?). Karpathy-grade arithmetic-on-a-napkin counts. A messy-but-correct answer is `solved`.
- **Don't pose two problems back-to-back.** The loop's claim is empirical; queuing problems before diagnosing the previous answer breaks that claim.
- **The HTML is the explanation; chat isn't.** Resist the urge to "also explain a bit in chat after sending the grok path." If the chat can explain it, the explanation didn't need grok in the first place — and the user will feel double-handled.
- **Side effects to disclose:** this skill creates files under `~/.problem_first_teach/`. It does not write anywhere else by default. grok, when invoked, writes its HTML to the same session folder.

## Anti-overfitting

This skill applies broadly: math (Poisson, attention, Jacobians, score matching), algorithms (Dijkstra, beam search, Viterbi), programming constructs (closures, async, generics), physics / stats / ML intuition, or a specific exercise the user is stuck on. The triggering surface is: *"the user wants to truly understand X, and accepts being tested before being lectured."* Nothing in the loop is specific to a single domain. If a rule below this line ever reads "when concept is `<specific-thing>`, do `<special-thing>`" — generalize it or delete it.

## See also

- `grok` — the explanation step delegates here. Read its trigger discipline before invoking from inside this loop; calls from this skill are explicit and intentional.
- `qa` — for Socratic clarification when the user is fuzzy *about what they want*, not stuck on a known concept. Route there when there's nothing concrete to test against yet.
- `wwxd` — for multi-expert analysis of a topic. Different shape; this skill is one-on-one pedagogy.
- `write-a-skill` — authoring conventions if this skill itself needs edits.
