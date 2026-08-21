[arc <ARC_ID> hourly patrol] 你是 manager。巡检：
(1) `ls -la --time-style=+%T _tmp/agents/` + 各 *.rc/*.log：哪些 worker 结束/超时/挂死（.out mtime 超 40 min 未动且进程仍在 = 挂死 → 按 PID 杀，换模型重派并让它"复用已有产物续跑"）；
(2) `nvidia-smi --query-gpu=index,memory.used,power.draw,utilization.gpu`（100% util 但 <100 W = 在等锁/对端）+ gpu_coord status + `df -h` 每个写根；
(3) 在跑训练的 tensorboard global_step 速率 + loss 非 NaN；chain/queue/follower 的 status 文件最后一行 **以及它们的进程是否还活着**；
(4) 读已完成 worker 的 final.md，按 2_plan.md 推进（派新 worker / 启动下一臂 / 评测）；GPU 空闲且计划允许就补控制臂或调研；
(5) 有结论就 `arc log`，步骤完成就覆写 3_state.md；
(6) 给用户 ≤8 行中文 status digest（数字 + 下一决策点时间）。
arc 目录 <ARC_PATH>。
