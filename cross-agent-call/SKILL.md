---
name: cross-agent-call
description: Dispatch a named model as a headless sub-agent by shelling out to its harness CLI (cursor-agent, grok, codex, or claude). Use whenever the user 派/用/让/问问 a model as a sub agent — sol, terra, luna, gpt-5.6, grok, grok-4.6, opus, sonnet, fable, codex, cursor — alone or as a pipeline like "用 opus 调研后派 luna 实现, 然后 grok 和 sol 并行测试", or wants a second opinion or cross-check from another model or vendor. Do NOT use for the `grok` learning-HTML skill (用 grok 讲解/学习 a paper or folder) or for Claude Code's built-in Agent tool subagents.
---

# Cross-agent call

Four agent harnesses are installed here, and every one of them has a headless single-shot mode. So any harness can use any other as a sub-agent: pick a model from a different vendor, shell out to its CLI, read the answer off stdout.

This skill records the entrypoints that were run and confirmed working, plus the flags that keep a headless sub-agent from stalling on a permission prompt.

Requests usually name only models ("派 luna 去实现, grok 和 sol 并行测试"): decode each name via [Model names and discovery](#model-names-and-discovery), then chain the calls — sequential stages one after another, independent ones as background jobs (`cmd1 & cmd2 & wait`).

## Quick reference

| Harness | Minimal verified command | Model slugs tested |
| --- | --- | --- |
| cursor-agent | `cursor-agent -p '<prompt>' --model cursor-grok-4.6-high --output-format text` | `cursor-grok-4.6-{low,medium,high}` |
| grok | `grok -p '<prompt>' -m grok-4.6 --reasoning-effort high --output-format plain` | `grok-4.6`, `grok-4.5` |
| codex | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh '<prompt>'` | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |
| claude | `claude -p '<prompt>' --effort high` | harness default; `--model <m>` to override |

Binaries, for shells whose PATH is thinner than an interactive one: `~/.local/bin/cursor-agent`, `~/.grok/bin/grok`, `codex` (on PATH), `~/.local/bin/claude`.

### Default effort

When the request names no effort, use these (all verified); go lower only when the user asks for speed or cheapness:

| Callee | Default |
| --- | --- |
| claude (any model) | `--effort high` |
| codex `gpt-5.6-sol` / `gpt-5.6-terra` | `-c model_reasoning_effort=xhigh` |
| codex `gpt-5.6-luna` | `-c model_reasoning_effort=max` |
| grok `grok-4.6` | `--reasoning-effort high` |
| cursor-agent Grok 4.6 | `cursor-grok-4.6-high` slug |

## cursor-agent

```bash
cursor-agent -p 'Summarize the tradeoffs in src/router.ts' \
  --model cursor-grok-4.6-medium --output-format text
```

- `-p` / `--print` is the headless mode. `--output-format text | json | stream-json`.
- Reasoning effort rides in the slug: `cursor-grok-4.6-{low,medium,high,xhigh}`, each with a `-fast` variant.
- Tool use: the default mode already carries every tool including shell and write, but headless runs stall on approval prompts, so add `-f` / `--force` to auto-approve. With `--force` it successfully ran a nested `claude -p`. Use `--mode ask` for read-only Q&A or `--mode plan` when the sub-agent should not touch the tree.
- Working dir defaults to cwd; `--workspace <path>` moves it, `-w` / `--worktree` runs in an isolated git worktree.

## grok

```bash
grok -p 'Review this diff for logic errors' -m grok-4.6 --output-format plain
```

- `-p` / `--single` is single-turn headless. `--output-format plain | json | streaming-json | streaming-messages-json`.
- `--reasoning-effort <effort>` for reasoning models.
- Tool use: `--permission-mode bypassPermissions` — verified by having it run a nested `codex exec`. For something tighter, `--allow <RULE>` / `--deny <RULE>`, `--tools`, and `--max-turns` narrow the surface.
- `--cwd <dir>` sets the working directory; `--prompt-file <path>` feeds a long prompt from disk.

## codex

```bash
codex exec -m gpt-5.6-sol -c model_reasoning_effort=low 'Explain what this script does'
```

- `codex exec` is the headless mode. Pass `-` as the prompt argument to read it from stdin.
- Effort comes in as a config override: `-c model_reasoning_effort=low|medium|high|xhigh|max`. An unquoted value is fine — anything that fails TOML parsing is taken as a literal string.
- Sandbox: `-s read-only | workspace-write | danger-full-access`, or `--dangerously-bypass-approvals-and-sandbox` to drop both approvals and the sandbox. See the gotcha below before letting a sandboxed codex call another harness.
- `--skip-git-repo-check` is required outside a git repo. `-C <dir>` sets the working root. `--ephemeral` skips writing session files.
- Clean output: plain stdout wraps the answer in a banner and token-usage lines, so use `-o` / `--output-last-message <file>` to get just the final message, or `--json` for JSONL events.

## claude

```bash
claude -p 'Give a second opinion on this design'
```

- `-p` / `--print` is headless and was confirmed callable both from inside another Claude Code session and from inside cursor-agent.
- `--effort <level>` sets reasoning effort.
- `--model <m>`, `--allowedTools`, `--output-format`, `--append-system-prompt`, `--agents <json>`, and `--max-turns` are all available; `claude --help` is the full list.
- Long prompts go in on stdin.

## Caller-side gotchas

**A sandboxed codex cannot spawn another harness.** Under `-s read-only`, calling the grok CLI fails with `Couldn't create session: Permission denied. FS_PERMISSION_DENIED` — the nested harness needs to write session state under its own dotfile directory and open the network, and the sandbox denies both. When codex is the caller, use `--dangerously-bypass-approvals-and-sandbox` (or `-s danger-full-access`) for the nested call. Put the flag on that one invocation; a sub-agent spawned this way runs unsandboxed, so widening the whole session hands the same freedom to everything else it does.

**Shell aliases do not exist in the shells scripts run in.** The user's interactive zsh defines `codex='command codex --dangerously-bypass-approvals-and-sandbox'`; a non-interactive shell gets the bare binary with default sandboxing. Spell every flag out in scripts and in commands you hand to another agent.

**Network needs the proxy.** This machine is on a mainland-China network and all four CLIs go through clash. Shells inherit `http_proxy` / `https_proxy` = `127.0.0.1:7899` once clash is on; `clashon` (a zsh function) turns it on. A hang or a TLS/connection error on any of these commands is the first thing to check.

**Quoting nests badly.** Single-quote the outer prompt so the callee's own quotes and `$` survive. Once the prompt contains quotes of both kinds, or runs past a line or two, stop fighting the shell: `codex exec -` and `claude -p` read stdin, `grok` takes `--prompt-file`, and `cursor-agent -p "$(cat prompt.txt)"` works for the rest.

## Model names and discovery

The user's shorthand maps to slugs like this:

| Said | Slug |
| --- | --- |
| sol | `gpt-5.6-sol` (codex) |
| terra, terral | `gpt-5.6-terra` (codex) |
| luna, tuna | `gpt-5.6-luna` (codex) |
| grok 4.6 | `grok-4.6` (grok CLI) or `cursor-grok-4.6-high` (cursor) |
| opus, sonnet, fable | `claude -p --model opus\|sonnet\|fable` (aliases; opus and fable verified) |

Snapshot of what each harness exposed at verification time:

- **codex** (`~/.codex/models_cache.json`): `gpt-5.6-sol` (the user's default, effort `xhigh` in `config.toml`), `gpt-5.6-sol-wm`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex-spark`, `codex-auto-review`.
- **grok**: `grok-4.6` (default), `grok-4.5`.
- **cursor-agent**: `cursor-grok-4.6-*`, `gpt-5.6-sol-{high,xhigh}[-fast]`, `gpt-5.6-luna-high`, `claude-opus-5-*`, `claude-sonnet-5-*`, `claude-fable-5-*`, `gpt-5.3-codex-*`, `composer-2.5`, `gemini-3.7-flash-high`, `auto`.

Model lists rot faster than this file does, so treat the discovery commands as the authority whenever a slug is rejected: `cursor-agent --list-models`, `grok models`, `codex exec --help` together with `~/.codex/models_cache.json`, and `claude --help`.

Versions the table above was verified against: cursor-agent 2026.08.11-e8db854, grok 1.0.4, codex-cli 0.144.1, claude 2.1.232.

## Verified cross-calls

| Caller | Callee | Result |
| --- | --- | --- |
| claude (Bash tool) | cursor-agent, grok, codex | works |
| cursor-agent `-p --force` | `claude -p` | works |
| grok `--permission-mode bypassPermissions` | `codex exec` | works |
| codex `--dangerously-bypass-approvals-and-sandbox` | grok CLI | works |
| codex `-s read-only` | grok CLI | fails, `FS_PERMISSION_DENIED` |

## Re-verifying on another machine

`scripts/smoke.sh [harness...]` runs one cheap echo-back call per harness and prints PASS or FAIL per row, exiting non-zero if any row fails. With no arguments it checks all four; name a subset to check only those. Run it after a CLI upgrade, on a new machine, or when a call that used to work starts failing — it separates "the flag changed" from "the network or login is down".

## See also

- `skill-mgmt/SKILL.md` — installing and syncing skills across these machines.
- Claude Code's own `Agent` tool and `.claude/agents/` — for subagents that stay inside this harness and share its context.
