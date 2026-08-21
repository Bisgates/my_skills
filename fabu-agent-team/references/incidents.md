# Incidents from the 260820a campaign and what settled each

## 1. Smoke run "died" with a 0-byte log (18:30)
Symptom: launcher returned STARTED, `train.pid` dead seconds later, log empty, GPUs idle.
Cause: the infra worker launched with plain `nohup … &`; when the codex exec session ended, its process group was killed.
Fix: `setsid nohup … < /dev/null &` in `launch_arm.sh`; verified with a sleep probe across a session boundary. Rule now in common_rules.

## 2. Hung NCCL trainings on GPU0+GPU6 (19:10–20:48, three attempts)
Symptom: both ranks alive, ~50 GB allocated, GPU util 0 %, memory churning, no `global_step` after 25 min; `NCCL_P2P_DISABLE=1` did not help. Same recipe on GPU2-3 / GPU4-5 reached step 9 in 8–17 min.
Decision: stop retrying that pair; queue the arm behind a good pair. Not root-caused (cross-NUMA pair; ptrace restricted so no py-spy).
Side effect: while the hung job sat there, every training on the host dropped from 12 to 30–40 s/step (see 4). Kill hung NCCL jobs within minutes.

## 3. Queue fired while the previous chain was still sampling (22:59)
Symptom: new arm OOM'd at startup ("Process X has 30 GB in use"), previous chain's sampler trapped, chain FAILED after EMA export.
Cause: `queue_after.sh` waited on the training PID; the chain keeps the same GPUs busy for ~40 min of export + sampling after the PID exits.
Fix (E1b): queue waits for `_tmp/chain_<prev>.status` to contain `DONE`; chain made resumable (skip stages whose artifacts verify) so the broken arm finished without re-exporting.

## 4. Host-wide training slowdown 12 → 33 s/step (from 20:40, recurring whenever two trainings ran)
Evidence (D2, read-only): `pt_autograd_0` thread of rank0 in `D` state at `rwsem_down_write_slowpath`; rank1's same thread spinning 100 % CPU; training GPUs at 60–90 W with "100 % util" (NCCL wait kernels); no throttling (`clocks_event_reasons` all inactive), no Xid, disks idle, pausing samplers for 4 min changed nothing; six long-lived `gpustat -i 1` pollers on the same lock; NUMA1 near full, 8 GB swap full.
Decision: serialize trainings (aggregate throughput of two concurrent jobs was below one job alone); samplers may run alongside one training.

## 5. Manager killed its own shell (three times)
`pgrep -f "post_arm_chain.sh t5"` matched the manager's own `bash -c …` command line, and process-group kills hit the harness shell (exit 143 "timed out after 0s"). Use `pgrep -f "[p]attern"` or explicit PID lists; collect the PID tree first, kill in a separate command.

## 6. Follower silently dead
A `lane_after_chain.sh` follower died (cause unknown) and its status file kept saying WAIT_CHAIN; the chain it waited on had been DONE for 40 min. Patrol must check follower PIDs (`pgrep -af "[l]ane_after"`) in addition to status files.

## 7. Headline gain that was the start checkpoint
T1 (+1.4 dB vs B1) was sampled from a better starting EMA; the control arm (start EMA alone) matched T1 on every metric. Always evaluate each start checkpoint under the frozen protocol before attributing gains to training; report "vs historical anchor" and "vs start" side by side.
