---
name: use_codex
description: Delegate work to Codex CLI / GPT-5 — code review, design challenge, stuck-bug rescue, ad-hoc research, or one-shot non-code Q&A — through the Claude Code `codex` plugin slash commands (`/codex:review`, `/codex:adversarial-review`, `/codex:rescue`, `/codex:status`, `/codex:result`, `/codex:cancel`) or by calling `codex exec "<prompt>"` directly. Use when the user asks to "ask codex / 让 codex 跑一下 / second opinion / 第二意见 / 对抗式 review / adversarial review", says Claude is stuck and wants another model to retry, requests work that needs Codex's tools (e.g. "到 reddit 搜搜最近有什么好看的电影", "查一下 X 论文最新进展"), or names GPT-5 / Codex explicitly. Do NOT trigger for plain code review or bug fix with no Codex framing (Claude does those), for plugin install or login (let `/codex:setup` handle it), or for tasks Claude's native WebSearch already handles cleanly.
---

# Use Codex

This skill is the agent-side decision guide for handing work off to Codex / GPT-5. It does not implement anything itself; it points you at the right tool for the situation and at the patterns that don't show up in `--help`.

## Quick decision

| Situation | Use |
|---|---|
| Code review of current diff | `/codex:review` |
| Challenge the chosen design / approach | `/codex:adversarial-review` |
| Hard bug, stuck, want Codex to investigate or fix | `/codex:rescue "<problem>"` (or `Agent` with `codex:codex-rescue`) |
| Check on background Codex jobs | `/codex:status` |
| Show stored final output of a finished job | `/codex:result [job-id]` |
| Cancel a background job | `/codex:cancel [job-id]` |
| Ad-hoc question, research, non-code Q&A, anything else | `codex exec "<prompt>"` |

The slash commands only resolve in **Claude Code** with the `openai/codex-plugin-cc` plugin installed. In other runtimes (raw Codex CLI, Gemini Antigravity), only the `codex exec` path works — fall back to it.

## Plugin commands (Claude Code only)

Don't reimplement these by hand — invoke the slash command. The plugin's `codex-companion.mjs` runtime gives the user `status` / `result` / `cancel` ergonomics for free, and uses a shared session so reviews and rescues see consistent context.

- `/codex:review` and `/codex:adversarial-review` accept `[--wait|--background] [--base <ref>] [--scope auto|working-tree|branch]`. The plugin auto-picks foreground vs background based on diff size when the flag is missing. Adversarial is for "is this the right approach?"; normal is for "are there bugs in this code?".
- `/codex:rescue` accepts `[--background|--wait] [--resume|--fresh] [--model <model|spark>] [--effort <none|minimal|low|medium|high|xhigh>]` and routes through the `codex:codex-rescue` subagent. Use when Claude is stuck, when the user wants a second implementation pass, or when handing a substantial coding task to Codex makes more sense than continuing in this session.
- `/codex:status`, `/codex:result`, `/codex:cancel` — manage jobs the plugin started in this repo. `status` shows the table; `result` prints stored output verbatim; `cancel` kills a running job.
- `/codex:setup` is the install / login / review-gate command. It belongs to the plugin, not to this skill — don't trigger this skill for setup requests.

The plugin also exposes a `codex:codex-rescue` subagent for the `Agent` tool. Call it directly when you want subagent routing rather than a slash command — same machinery underneath.

## Raw `codex exec` (any runtime)

For everything outside the plugin's scope — ad-hoc research, "ask Codex what it thinks of X", web lookups, scratch experiments — call the CLI directly:

```bash
codex exec "<one-shot prompt>"                 # blocks, streams to stdout
codex exec -o last.md "<prompt>"               # also write final assistant message to last.md
codex exec --json "<prompt>"                   # NDJSON event stream for programmatic use
codex exec -s read-only "<prompt>"             # default sandbox
codex exec -s workspace-write "<prompt>"       # let Codex write files in cwd
codex exec -m gpt-5-codex "<prompt>"           # override model
codex exec -C /some/repo "<prompt>"            # run from a specific working dir
codex exec --output-schema schema.json "<p>"   # force JSON shape on final response
```

The prompt is plain natural language — speak to Codex the way you'd speak to ChatGPT. Example: `codex exec "到 reddit 上搜搜最近有什么好看的电影，给我列三部并说为什么"` works *if* the user's Codex install has web tools enabled; otherwise it'll say so. Don't promise capabilities the local install may not have — just run it and surface what happens.

Patterns worth knowing:

- **Capture the final message, not stdout.** `codex exec -o /tmp/codex.md "..."` writes only the final assistant message to the file. Read that file back; don't try to parse the chain-of-thought trace on stdout.
- **Background work in Claude Code goes through `/codex:rescue --background`**, not `codex exec ... &`. The plugin gives you `status` / `result` / `cancel`; bare `&` strands the job and the user has no handle on it.
- **Stdin or prompt arg — not both.** If both are present, stdin is appended as a `<stdin>` block in the prompt. Usually that's fine, but be deliberate about which carries what.
- **Structured output via `--output-schema`** is useful when you want the result to feed back into the next tool call.

## Choosing between plugin and raw CLI

- In **Claude Code**, code-development tasks (review, design challenge, fix a hard bug) → plugin first. It is wired into Claude's tool surface and the user can manage the job through familiar `/codex:*` commands.
- In **Claude Code**, non-code research or ad-hoc Q&A → raw `codex exec`. The plugin commands are review/rescue-shaped; using them for "search reddit for me" is awkward and the output rendering assumes code-review structure.
- In **Codex CLI itself**, you are already Codex; don't recursively call `codex exec`. Do the task directly.
- In **Gemini Antigravity** or any other runtime, raw `codex exec` is the only option — the plugin's slash commands don't resolve there.

## Gotchas

- ChatGPT / OpenAI subscription quota applies and contributes to the user's Codex usage limits. A failed `codex exec` with a quota message is the user's account state, not a code bug — surface it and stop.
- `codex exec` defaults to sandbox `read-only`. Tasks that need to write files in the cwd need `-s workspace-write`. Never use `--dangerously-bypass-approvals-and-sandbox` without the user's explicit say-so — it gives Codex full write access with no approvals.
- Plugin presence is per-runtime, not per-skill. This skill is symlinked into Claude / Codex / Antigravity by `skill-mgmt`, but the `/codex:*` slash commands only resolve in Claude Code with the plugin installed. If they don't, fall back to raw `codex exec`.
- `/codex:review` is review-only. Even if Codex spots a bug, the plugin command refuses to apply patches — use `/codex:rescue` for that.
- The `codex` CLI requires Node ≥ 18.18 and a logged-in ChatGPT / API account. `/codex:setup` (not this skill) verifies both.

## See also

- `<plugin>/skills/codex-cli-runtime/SKILL.md` — internal contract for the codex-companion runtime (loaded by Claude Code when plugin commands fire).
- `<plugin>/skills/gpt-5-4-prompting/SKILL.md` — guidance for composing Codex / GPT-5 prompts well.
- `<plugin>/skills/codex-result-handling/SKILL.md` — how the plugin presents Codex output back to the user.
- `<repo>/skill-mgmt/SKILL.md` — how this skill is linked into all three runtimes.
