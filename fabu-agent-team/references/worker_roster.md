# Worker roster — what was dispatched in arc 260820a (18 h, 22 workers) and how each did

Default worker set for a fabu-agent-team campaign. "Perf" is the manager's after-action grade.

| # | Worker | Model | Job | Deliverable | Perf / notes |
|---|---|---|---|---|---|
| R1 | method survey | gpt-5.6-sol | why SVD/EDM fine-tunes go soft; fixes with code landing spots | doc/r1_methods.md (6 train arms, 3 sample arms, evidence-graded) | Excellent; its #1 suspicion (steps/start point) was what the data later showed |
| R2 | code-knob audit | qwen3.8-max | every sharpness-related knob, file:line, current value, paste-ready override | doc/r2_knobs.md (26 knobs) | Excellent; found decode-chunk=1 → per-frame temporal decoder, dotlist override mechanism, EMA warm-up hidden knob; most-cited doc |
| R3/R3b | blur diagnosis (GPU) | k3 → qwen3.8-max | GT→VAE→GT ceiling, band-energy ratios, crops | doc/r3_blur_diagnosis.md | k3 died on backend 503 after writing the script; qwen resumed. Most valuable qualitative result (VAE not the bottleneck; finest band missing) |
| R4 | archaeology | gpt-5.6-terra | prior arcs' sampling/blur conclusions, asset list | doc/r4_archaeology.md | Good; exposed that fourcam-8k vs B1 had never been compared → control arm E2 |
| R5 | objective-side survey | qwen3.8-max | losses/decoders/data for sharpness | doc/r5_sharpness_objectives.md | Mixed: useful candidates, but a loss-mass inference was wrong (caught by R7) |
| R6 | high-res feasibility | gpt-5.6-sol | memory/step estimates, code blockers | doc/r6_highres_feasibility.md | Good; clear no-go without wasting GPU |
| R7 | adversarial review of R1–R5 + arm design | gpt-5.6-terra | contradictions recomputed, arm confounds | doc/r7_adversarial_review.md | Excellent; changed T2 to single-knob, flagged warm-up mismatch |
| R8 | final adversarial review | gpt-5.6-terra | recompute all headlines from JSON + PNG; power analysis; wording fixes | doc/r8_final_review.md | Excellent; 12 arm×cam numbers to 3e-15; 5 wording rules adopted verbatim |
| D1 | infra + smoke + first arm | qwen3.8-max | launch_arm.sh, arm_base.yaml, export_arm_ema.sh | doc/d1_infra.md | Excellent; diagnosed the 0-byte-log smoke death (codex session kills nohup children) and fixed with setsid |
| D2 | slowdown diagnosis | gpt-5.6-sol | why two trainings dropped 12→33 s/step | doc/d2_slowdown_diagnosis.md | Good; driver rwsem contention via /proc wchan, no root; could not pin single trigger |
| E0 | eval toolkit | qwen3.8-max | eval_arm.py with baseline self-test | doc/e0_eval_toolkit.md | Excellent; self-test 31/31; recovered after S1 overwrote its file, added OWNERSHIP header |
| E1 | post-train chain | qwen3.8-max | post_arm_chain.sh | doc/e1_chain.md | Good; correct but not resumable (fixed by E1b) |
| E1b | incident recovery | qwen3.8-max | resumable chain, finish broken arm, relaunch, fix queue | doc/e1b_recovery.md | Excellent; cleaned up the manager's queue mistake end to end |
| E2 | control arm | qwen3.8-max | start checkpoint under frozen protocol, 3-way attribution | doc/e2_fourcam8k_control.md | Excellent; the night's key reversal (gain = start point); reused prior samples with provenance |
| S1 | sampling sweep | gpt-5.6-sol | steps/decode/CFG/rho/sigma_max on fixed weights | samples + partial doc | Mixed: rigorous (base bit-identical) but hit 4 h timeout; once overwrote E0's script |
| S1b | sweep wrap-up | qwen3.8-max | evaluate remaining tags, final doc with guard-rail recommendation | doc/s_sweep.md | Good |
| S2 | lane chain | qwen3.8-max | lane_chain.sh, baseline reproduction | doc/s2_lane_chain.md | Excellent; 288/288 sha bit-identical |
| S3 | mass sampling for user pick | qwen3.8-max | all val windows × 4 cams × shift0/3/5 with the user-chosen arm, browse page | output/…_more_samples | (dispatched after user L2 judgment) |
| H1/H2/H3 | report builders | gpt-5.6-sol | compare HTML (full + lite), 9_summary.html | output/…trackC_compare, 9_summary.html | Good; dual-baseline columns, three-tier colouring, lite <30 MiB first try |

## Patterns worth keeping

- Research fan-out → adversarial review → control arm → (only then) training arms. The control arm (E2) was worth more than the two 4-hour training arms it invalidated.
- One infra worker owns the launch/export/eval chain; the manager launches arms with one env-var command and never hand-edits the chain while it runs.
- Every execution worker writes a progress/status file; the patrol reads files, not worker stdout.
- Reviewer workers (terra) at two points: after research (design) and before handoff (numbers + wording).
- Resumption prompt for a dead worker: "前一个代理因 X 中断，已存在 <files>，先检查现有产物，复用而不是重写".

## Model notes (observed on the fabu provider)

- qwen3.8-max: 11 tasks, 0 crashes, best at following file-scope rules; prefer for anything that touches GPUs or the filesystem.
- gpt-5.6-sol: best writing/research depth; give it a time box and progress file, it will otherwise run to `timeout`.
- gpt-5.6-terra: use for review; it recomputes rather than paraphrases.
- k3: one backend 503 death; fine as spare.
- Backend 503 is transient; a re-dispatch with "resume from artifacts" lost ~15 min, not the work.
