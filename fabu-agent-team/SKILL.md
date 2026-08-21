---
name: fabu-agent-team
description: Run a long autonomous experiment campaign as an agent team — a Claude manager (Fable 5 / Opus 5) that only plans, dispatches, patrols and synthesizes, plus fabu-codex workers (`codex exec --model k3 | qwen3.8-max | gpt-5.6-sol | gpt-5.6-terra`) that do research, infra, GPU jobs, evaluation, adversarial review and report building. Use when the user says "用 agent team / 多开 subagent 推进 / 派 worker / 你当 manager / 18h 自主执行 / 晚上自己推进 / subagent 用 fabu-codex", or hands over an arc with a multi-hour budget and wants parallel workers. Do NOT trigger for a single short codex question (use use_codex), for arc bookkeeping alone (use arc), or for GPU booking rules alone (read agent_gpu_coord/PROTOCOL.md).
---

# fabu-agent-team — manager + fabu-codex workers

Distilled from a real 18-hour autonomous run (street-crafter arc 260820a, 22 workers, 6 training arms, 3 incidents). The manager is the scarce resource: its context window and its judgment. Everything below exists to keep the manager out of the weeds and to stop the four failure modes that actually cost hours that night — a worker that dies silently, a queue that fires on the wrong condition, a manager that kills its own shell, and a "big win" that turns out to be the start checkpoint.

## Quick start

```bash
ARC=$(arc cd <id>)                                   # all work lives in the arc
cp ~/.claude/skills/fabu-agent-team/scripts/run_codex.sh  $ARC/scripts/
cp ~/.claude/skills/fabu-agent-team/templates/common_rules.md $ARC/_tmp/   # edit arc id / write roots
# one worker = one prompt file + one model + one timeout
cat > $ARC/_tmp/r1.prompt.md <<'P'
# 任务 R1：...（目标 / 输入路径 / 产出文件 / 规则 / 时间盒）
P
nohup bash $ARC/scripts/run_codex.sh r1 gpt-5.6-sol 5400 $ARC/_tmp/r1.prompt.md >/dev/null 2>&1 &
# results: $ARC/_tmp/agents/r1.{final.md,rc,log,out}
```

Then set the hourly patrol (`CronCreate` with `templates/patrol_prompt.md`) and go back to being the manager.

## Roles

**Manager (Fable 5 / Opus 5)** — writes the objective/plan, designs arms and controls, dispatches workers, patrols hourly, reads `final.md` summaries (not worker logs), writes `arc log` / `3_state.md` / `9_handoff.md` itself. It does not read large files, run long GPU commands in the foreground, or re-derive numbers a worker already verified. Memory `feedback_autonomous_context_protection` is the reason: every MB of worker output the manager reads is context it cannot spend on decisions.

**Workers (fabu-codex)** — `codex exec` processes. Each gets the common rules + one task prompt, writes files into the arc (or the arc's scratch root on /ssd), and returns a ≤15-line summary. Workers never call the `arc` CLI, never write `3_state.md`/`0_meta.md`, never touch the main project. The roster of worker types that proved useful, with the model that suited each, is in `references/worker_roster.md`.

Model choice (user policy + observed behaviour): for infra / execution / eval / GPU work the order is **`k3` first, `qwen3.8-max` as fallback** — k3 is the user's preferred worker when the fabu backend serves it; it died once on a transient 503 after writing its script, so if a k3 worker exits with rc≠0 and no `final.md`, re-dispatch the same prompt on `qwen3.8-max` with "复用已有产物续跑" (qwen ran 11 such tasks with zero crashes and obeys file-scope rules). `gpt-5.6-sol` for research and report building (strong, but can run to timeout — set a time box and ask for progress files); `gpt-5.6-terra` for adversarial review (caught real errors both times). `gpt-5.6-luna` is the CLI default.

## The campaign loop

1. **Research fan-out first (hour 0).** 3–5 read-only workers in parallel: method survey, code-knob audit with `file:line`, archaeology of prior arcs, one GPU diagnosis that measures the ceiling (e.g. VAE round-trip) — then **an adversarial reviewer on the research itself** before any arm launches. In 260820a the reviewer (R7) caught a wrong "93 % loss mass" claim and a two-knob arm that would have been unattributable.
2. **Cheap control arms before expensive ones.** Sample/evaluate every *starting checkpoint* under the frozen protocol before training on top of it. The night's headline "+1.4 dB" arm was entirely its start checkpoint (E2 control); two 4-hour training arms would have been unnecessary had the control run first.
3. **Infra worker builds the chain, then the manager launches arms.** One worker produces `launch_arm.sh` (gates + `setsid`), `post_arm_chain.sh` (train-exit → export → sample → eval → doc, resumable), `lane_chain.sh`, `eval_arm.py` with a self-test that reproduces the baseline numbers bit-for-bit. Launching an arm is then one env-var command the manager runs itself.
4. **Chain, don't notify.** Every follow-up action lives in a background script that waits on a *status file* (`_tmp/chain_<arm>.status` reaching `DONE`), not on a PID and not on the manager remembering. Background waiters (`run_in_background` bash loops grepping the status file) wake the manager with the headline table already extracted.
5. **Hourly patrol (cron).** Agents: `*.rc` / `*.log` / `.out` mtime (>40 min stale with a live process = hung → kill by PID, re-dispatch on another model with "resume from existing artifacts"). GPUs: `nvidia-smi` power draw, not just util (100 % util at 60 W = waiting on a lock). Training: tensorboard `global_step` rate, loss non-NaN. Disk: `df` on every write root. Then read new `final.md`s, advance the plan, `arc log`, overwrite `3_state.md`, emit a ≤8-line digest.
6. **Adversarial review before handoff.** A terra worker re-computes every headline number from the raw JSON and from a few PNGs, states the statistical power of every "null", and dictates wording fixes. Adopt its wording verbatim ("not detected under X" ≠ "ineffective").
7. **Report workers at the end**, manager writes `9_handoff.md` itself (it is the synthesis), a worker turns it into `9_summary.html` in the house format and rebuilds the compare HTML with all arms.

## Prompt contract for every worker

The prompt file is `common_rules.md` + task. The task section always has: goal in one line; exact input paths; exact output paths (doc in `$ARC/doc/`, scripts in `$ARC/scripts/`, data under the arc's `/ssd` root); which GPUs by `CUDA_VISIBLE_DEVICES` (never "pick a free one"); a time box; "all numbers must be reproducible — give the command"; "write `未得到` rather than invent". For execution workers add: write a progress/status file after each unit so the patrol can see liveness.

Why `< /dev/null`, `timeout`, `-o final.md`: codex hangs on an open stdin (memory `feedback_autonomous_heartbeat`), runs to the backend's patience otherwise, and the chain-of-thought on stdout is not the deliverable.

Why `-s danger-full-access`: workers must write to `/ssd` and spawn GPU jobs; the file-scope discipline therefore lives in the prompt, and the manager verifies it (`git status` on the main project after each delivery — memory `feedback_subagent_shared_file_diff`).

## GPU discipline that the night proved

- Book all cards once at the start (`gpu_coord acquire --agent <arc-id>`), then assign fixed pairs per arm. Do not let short smoke runs `attach` their PID to the manager's claim — the claim is reclaimed the moment that PID exits.
- **Serialize trainings on this host.** Two concurrent 2-GPU DeepSpeed jobs each ran at 30–40 s/step vs 12 s alone; sampling alongside one training is fine. Queue arms behind each other (`queue_after.sh` waiting on chain `DONE`).
- A hung NCCL job (GPU util 0 %, memory churning, no step after 20 min) poisons the whole host (driver rwsem contention; every training on the machine slowed 2.7×). Kill it within minutes, by PID tree. On gpu7 the GPU0+GPU6 pairing hung 3/3 times; 2–3 and 4–5 never did. Record such pairs in the arc and stop retrying them.
- First logged step can take 8–17 min after launch (checkpoint hash + model load + step-0 image log). Distinguish "slow init" (power rising, memory growing) from "hung" (0 % util, no growth) before killing.
- Every ckpt is ~35–44 GB; `save_top_k=0`, export EMA, delete `last.ckpt` inside the chain; spread run roots over `/ssd` and `/home` and check `df` in the patrol.

## Manager self-inflicted wounds (do not repeat)

- `pgrep -f <pattern> | xargs kill` and `pkill -f` match the manager's own `bash -c` command line → the manager killed its own shell three times. Use `pgrep -f "[p]attern"` or kill explicit PID lists; never process-group kills from the manager shell.
- A queue that waits for the *training PID* to exit fires while the chain is still sampling on the same GPUs → OOM for both. Wait on the chain's `DONE` line.
- `setsid nohup … &` from a codex session is required; plain `nohup` children are killed when the codex session ends (first smoke "died" with a 0-byte log).
- Do not launch an attribution-confounded arm (two knobs) just because it is the "effect-size" option; the review will make you run the control anyway.
- Write status words the followers grep for exactly (`DONE `, `FAILED`); a dead follower looks like "waiting" forever — the patrol must check follower PIDs, not only status files.

## Measurement discipline

Frozen protocol (seed/steps/CFG/decoder) for every arm; a self-test that reproduces the baseline numbers before the toolkit touches a new arm; paired tests per window; a stated noise floor (here PSNR 0.3 dB / LPIPS 0.01 / r(hp) 0.02); two baselines when the start checkpoint changes ("vs historical anchor" and "vs current best"); perceptual sharpness and pixel fidelity can dissociate — the user's eye is the L2 gate, report both and say so. Workspace rules in `docs/evaluation/generated_video_realism_metrics.md` still apply (never FVD; FD-DINOv2 ÷ floor; exposure condition on every realism claim).

## Files in this skill

- `scripts/run_codex.sh` — worker launcher (prompt = common rules + task; writes `_tmp/agents/<name>.{prompt.md,out,final.md,rc,log}`).
- `templates/common_rules.md` — the rules block prepended to every worker prompt; edit the arc id and write roots.
- `templates/patrol_prompt.md` — the hourly `CronCreate` prompt.
- `templates/task_prompts.md` — skeletons for research / infra / eval-chain / control-arm / adversarial-review / report workers.
- `references/worker_roster.md` — the worker types used in 260820a, what each delivered, which model, and how it performed.
- `references/incidents.md` — the three incidents and the slowdown diagnosis, with the evidence that settled each.

## See also

- `arc` — task isolation, `3_state.md` / `9_handoff.md` contract the manager owns.
- `use_codex` — single-shot codex usage; this skill is the multi-worker campaign layer on top of it.
- `agent_gpu_coord/PROTOCOL.md` (workspace) — card booking; `drivestudio-train` / `sg-train` for the per-project training entrypoints the infra worker wraps.
