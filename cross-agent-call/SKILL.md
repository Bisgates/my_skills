---
name: cross-agent-call
description: Dispatch a model from a *different* harness as a headless sub-agent by shelling out to its CLI. Use when the user requests a model the current harness does not serve — e.g., from Claude Code invoke astra/sol/luna (codex) or grok (grok CLI); from codex invoke opus/fable (claude) or grok (grok CLI). Do NOT use for native models: claude→opus/sonnet/fable use the Agent tool; codex→astra/sol/luna use codex's Agent tool; grok→its native models use grok's Agent tool. Supports pipelines and parallel jobs like "用 opus 调研后派 luna 实现, 然后 grok 和 sol 并行测试".
---

# Cross-agent call

This skill covers three agent harnesses, and every one of them has a headless single-shot mode. So any harness can use any other as a sub-agent: pick a model from a different vendor, shell out to its CLI, read the answer off stdout.

This skill records the entrypoints that were run and confirmed working, plus the flags that keep a headless sub-agent from stalling on a permission prompt.

## Scope: when to use this skill

Route each model by ownership, not by its name:
- **Own harness:** a model the current harness serves natively goes through that harness's own subagent mechanism (Agent tool in Claude Code, Agent tool in codex, grok's native agent in grok). This keeps shared context and permissions.
  - Claude Code: use the `Agent` tool for opus, sonnet, fable
  - codex: use the `Agent` tool for astra, sol, luna
  - grok: use grok's native agent for its available models
- **Other harness:** shell out through *this skill only for models that live in another harness* — codex models from Claude Code, claude models from codex, etc.

A mixed pipeline splits accordingly: from Claude Code, "用 opus 调研后派 luna 实现" runs opus via the `Agent` tool and luna via `codex exec`.

## How to invoke

Requests usually name only models ("派 luna 去实现, grok 和 sol 并行测试"): decode each name via [Model names and discovery](#model-names-and-discovery), then chain the calls — sequential stages one after another, independent ones as background jobs (`cmd1 & cmd2 & wait`).

## Quick reference

Resolve the variables below using [Model names and discovery](#model-names-and-discovery) before running these commands.

| Harness | Command pattern | Model selection |
| --- | --- | --- |
| grok | `grok -p '<prompt>' -m "$GROK_MODEL" --reasoning-effort high --output-format plain` | Latest available Grok |
| codex | `codex exec -m "$CODEX_MODEL" -c "model_reasoning_effort=$CODEX_EFFORT" '<prompt>'` | Latest available model in the requested GPT family |
| claude | `claude -p '<prompt>' --effort high` | harness default; `--model <m>` to override |

Fabu-hosted models are reached with `fabux exec -m <slug>` using that provider's own available model catalog; from the Mac, plain `codex` uses the personal quota.

Binaries, for shells whose PATH is thinner than an interactive one: `~/.grok/bin/grok`, `codex` (on PATH), `~/.local/bin/claude`.

### Default effort

These are this skill's invocation defaults, not necessarily the harness or model-catalog defaults. When the request names no effort, use these; go lower only when the user asks for speed or cheapness:

| Callee | Default |
| --- | --- |
| claude (any model) | `--effort high` |
| codex Astra | `-c model_reasoning_effort=medium` |
| codex Sol | `-c model_reasoning_effort=high` |
| codex Luna | `-c model_reasoning_effort=max` |
| grok (latest available) | `--reasoning-effort high` |

## grok

```bash
grok -p 'Review this diff for logic errors' -m "$GROK_MODEL" --reasoning-effort high --output-format plain
```

- `-p` / `--single` is single-turn headless. `--output-format plain | json | streaming-json | streaming-messages-json`.
- `--reasoning-effort <effort>` for reasoning models.
- Tool use: `--permission-mode bypassPermissions` — verified by having it run a nested `codex exec`. For something tighter, `--allow <RULE>` / `--deny <RULE>`, `--tools`, and `--max-turns` narrow the surface.
- `--cwd <dir>` sets the working directory; `--prompt-file <path>` feeds a long prompt from disk.

## codex

```bash
codex exec -m "$CODEX_MODEL" -c "model_reasoning_effort=$CODEX_EFFORT" 'Explain what this script does'
```

- `codex exec` is the headless mode. Pass `-` as the prompt argument to read it from stdin.
- Effort comes in as a config override: `-c model_reasoning_effort=low|medium|high|xhigh|max|ultra`. Check the selected model's supported levels in the model catalog; not every model supports `max` or `ultra`. An unquoted value is fine — anything that fails TOML parsing is taken as a literal string.
- Sandbox: `-s read-only | workspace-write | danger-full-access`, or `--dangerously-bypass-approvals-and-sandbox` to drop both approvals and the sandbox. See the gotcha below before letting a sandboxed codex call another harness.
- `--skip-git-repo-check` is required outside a git repo. `-C <dir>` sets the working root. `--ephemeral` skips writing session files.
- Clean output: plain stdout wraps the answer in a banner and token-usage lines, so use `-o` / `--output-last-message <file>` to get just the final message, or `--json` for JSONL events.

## claude

```bash
claude -p 'Give a second opinion on this design'
```

- `-p` / `--print` is headless and was confirmed callable from inside another Claude Code session.
- `--effort <level>` sets reasoning effort.
- `--model <m>`, `--allowedTools`, `--output-format`, `--append-system-prompt`, `--agents <json>`, and `--max-turns` are all available; `claude --help` is the full list.
- Long prompts go in on stdin.

## Caller-side gotchas

**A sandboxed codex cannot spawn another harness.** Under `-s read-only`, calling the grok CLI fails with `Couldn't create session: Permission denied. FS_PERMISSION_DENIED` — the nested harness needs to write session state under its own dotfile directory and open the network, and the sandbox denies both. When codex is the caller, use `--dangerously-bypass-approvals-and-sandbox` (or `-s danger-full-access`) for the nested call. Put the flag on that one invocation; a sub-agent spawned this way runs unsandboxed, so widening the whole session hands the same freedom to everything else it does.

**Shell aliases do not exist in the shells scripts run in.** The user's interactive zsh defines `codex='command codex --dangerously-bypass-approvals-and-sandbox'`; a non-interactive shell gets the bare binary with default sandboxing. Spell every flag out in scripts and in commands you hand to another agent.

**Network needs the proxy.** This machine is on a mainland-China network and all three CLIs go through clash. Shells inherit `http_proxy` / `https_proxy` = `127.0.0.1:7899` once clash is on; `clashon` (a zsh function) turns it on. A hang or a TLS/connection error on any of these commands is the first thing to check.

**Quoting nests badly.** Single-quote the outer prompt so the callee's own quotes and `$` survive. Once the prompt contains quotes of both kinds, or runs past a line or two, stop fighting the shell: `codex exec -` and `claude -p` read stdin, and `grok` takes `--prompt-file`.

## Model names and discovery

Use the latest available model by default, resolving it once per dispatch batch from the target harness's model catalog. Versioned slugs in old transcripts are not defaults. Explicit user versions or full slugs take precedence: preserve them exactly.

| Said | Selection | Default effort |
| --- | --- | --- |
| astra | Latest available Astra family model | medium |
| sol | Latest available Sol family model | high |
| luna, tuna | Latest available Luna family model | max |
| gpt, codex (no family) | Latest available general-purpose GPT generation; prefer the flagship when several families share that generation | Selected family's default above, otherwise catalog default |
| grok (no version) | Latest available general-purpose Grok model | high |
| opus, sonnet, fable | Pass the Claude CLI's latest-model alias directly | high |

- **Codex:** use the current native tool model list when available; for CLI dispatch, inspect `~/.codex/models_cache.json` and its freshness. Use visible, available models and their supported reasoning levels. Refresh discovery through the target harness if the cache is stale or the requested family is absent. `codex exec --help` documents flags, not available models. Resolve the exact slug into `CODEX_MODEL` and the effort into `CODEX_EFFORT`; shorthand family names are skill inputs, not assumed CLI aliases.
- **Grok:** run `grok models`, choose the newest available general-purpose version, and set `GROK_MODEL` to that exact slug. A model marked default is not necessarily the newest.
- Compare numeric version components (for example, 4.10 is newer than 4.9), not lexicographic order. Do not silently switch a requested family, select hidden/review/special-purpose models, or invent a `latest` slug. If discovery cannot establish the latest available model, report that limitation instead of presenting an old snapshot as current.
- Pass the selected model and effort explicitly, including through native subagent tools. Explicit user effort overrides the skill default. If the selected model does not support that effort, report the mismatch instead of silently changing it.
- Keep discovery provider-specific: personal Codex availability does not establish Fabu availability.

## Verified cross-calls

| Caller | Callee | Result |
| --- | --- | --- |
| claude (Bash tool) | grok, codex | works |
| grok `--permission-mode bypassPermissions` | `codex exec` | works |
| codex `--dangerously-bypass-approvals-and-sandbox` | grok CLI | works |
| codex `-s read-only` | grok CLI | fails, `FS_PERMISSION_DENIED` |

## Re-verifying on another machine

`scripts/smoke.sh [harness...]` runs one cheap echo-back call per harness and prints PASS or FAIL per row, exiting non-zero if any row fails. Before running, resolve and export `CODEX_MODEL` and `GROK_MODEL` as above (only the variables for the selected harnesses are required). The script uses low effort for the Codex echo check to keep verification cheap. With no arguments it checks all three; name a subset to check only those. Run it after a CLI upgrade, on a new machine, or when a call that used to work starts failing — it separates "the flag changed" from "the network or login is down".

## See also

- `skill-mgmt/SKILL.md` — installing and syncing skills across these machines.
- Claude Code's own `Agent` tool and `.claude/agents/` — for subagents that stay inside this harness and share its context.
