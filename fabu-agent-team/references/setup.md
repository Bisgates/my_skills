# fabux setup

`fabux` is a thin profile wrapper. Both machines use the same call path:

```text
fabux -m <slug> -> codex --profile fabu -c model_provider=<crs|cpa> -> crs.fabu.ai / cpa.fabu.ai
```

The fabu profile holds two gateways that serve disjoint models, with one key:

| provider | base_url | models |
|---|---|---|
| `crs` (default) | `http://crs.fabu.ai/openai` | `qwen3.8-max`, `deepseek-v4.1-flash`, `qwen3.8-flash`, `glm-5.2` |
| `cpa` | `http://cpa.fabu.ai/v1` | `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna` |

A codex profile has one `model_provider`, so fabux reads the model's `provider`
field from `fabu.models.json` and adds `-c model_provider=<name>` (after the
subcommand for `exec` / `review`, where a top-level override loses to the
profile). A catalog entry without `provider` uses the profile default. Plain
`codex --profile fabu -m gpt-6-sol` goes to crs and returns 404.

The gateways are reachable only on the fabu network (VPN/office). Off-site, use
plain `codex` with the personal ChatGPT quota.

## Profile file

Create `~/.codex/fabu.config.toml`. Use absolute paths for
`model_catalog_json`; TOML does not expand `$HOME`. If the file already exists,
back it up first:

```bash
[ -f ~/.codex/fabu.config.toml ] && cp ~/.codex/fabu.config.toml ~/.codex/fabu.config.toml.bak.$(date +%Y%m%d-%H%M%S)
```

Mac / environment-key auth:

```toml
model_provider = "crs"
model = "qwen3.8-max"
model_reasoning_effort = "xhigh"
model_catalog_json = "/ABSOLUTE/PATH/.codex/fabu.models.json"
disable_response_storage = true
approvals_reviewer = "user"

[model_providers.crs]
name = "crs"
base_url = "http://crs.fabu.ai/openai"
wire_api = "responses"
env_key = "FABU_CRS_KEY"

[model_providers.cpa]
name = "cpa"
base_url = "http://cpa.fabu.ai/v1"
wire_api = "responses"
env_key = "FABU_CRS_KEY"
```

Each entry of `fabu.models.json` carries `"provider": "crs"` or `"provider": "cpa"`;
`fabux models` prints that column.

Export `FABU_CRS_KEY` from the shell startup file. Do not put the key in the
profile file.

Linux / Codex auth.json:

```toml
model_provider = "fabu"
model = "gpt-5.6-luna"
model_reasoning_effort = "xhigh"
model_catalog_json = "/ABSOLUTE/PATH/.codex/fabu.models.json"
disable_response_storage = true
approval_policy = "never"
sandbox_mode = "danger-full-access"
service_tier = "fast"
web_search = "live"

[model_providers.fabu]
name = "fabu"
base_url = "http://crs.fabu.ai/openai"
wire_api = "responses"
requires_openai_auth = true
```

The Linux profile reuses `~/.codex/auth.json`; do not copy the Mac environment
key into it. A catalog entry whose `provider` names a table this profile lacks
makes codex fail; add a matching `[model_providers.cpa]` table or drop the field. Keep `fabu.models.json` at the path named by the profile.

## Install the command

Create the command symlink (the skill installer links skill directories only):

```bash
# Mac
mkdir -p ~/.local/bin
ln -sf /Users/han/project/agent/skills/fabu-agent-team/scripts/fabux ~/.local/bin/fabux

# gpu7
mkdir -p ~/.local/bin
ln -sf /home/hanjialu/my_skills/fabu-agent-team/scripts/fabux ~/.local/bin/fabux
```

`~/.local/bin` must be on PATH in both login and non-interactive shells (the
manager reaches gpu7 over `ssh gpu7 '...'`, which is non-interactive):

```bash
ssh gpu7 'echo $PATH' | tr : '\n' | grep -x "$HOME/.local/bin\|/home/hanjialu/.local/bin"
ssh gpu7 'bash -lc "echo \$PATH"' | tr : '\n' | grep .local/bin
# if either is empty, add to ~/.bashrc on gpu7 (above any early `return` for non-interactive shells):
#   export PATH="$HOME/.local/bin:$PATH"
```

`run_codex.sh` needs `timeout`; on macOS install it with `brew install coreutils` (`gtimeout` is picked up automatically).

Then check the installation:

```bash
fabux doctor
fabux models
```

`fabux` and `fabux -m k3` open the interactive TUI; `fabux exec -m k3 '...'`
is the headless form. The TUI `/model` picker reads the fabu catalog from
`model_catalog_json`.

To test the wrapper without a network preflight, use
`FABUX_SKIP_PREFLIGHT=1`. To test the off-network branch without changing
configuration, set `FABUX_PREFLIGHT_HOST` to an unreachable host; rc=3 means
switch workers to plain `codex exec -m gpt-5.6-sol`.
