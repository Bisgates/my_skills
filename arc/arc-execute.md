---
name: arc-execute
description: Execute the arc's plan from current state, logging progress, until the plan is complete or an unexpected situation arises. Use when the user says "/arc-execute" or "/arc-execute 260430c".
---

# /arc-execute — 执行计划并留痕

## Steps for the agent

1. 解析 arc：id 或 cwd。
2. 读 `0_meta.md`、`1_objective.md`、`2_plan.md`、`3_process_log.md` 末尾约 40 行（grep 末尾即可，不要读全）。
3. 判断当前进度：
   - process_log 中最后一个有结论的步骤是哪个？
   - 对照 plan，下一步应该做什么？
4. **默认一口气推到 plan 末尾**。每完成一个有结论的动作（跑了脚本、得了数字、做了决定）调一次：
   ```bash
   arc log "[<phase>] <一行结论>"
   ```
5. **代码 / 产物归位**（子目录按需创建——首次写入前先 `mkdir -p` 或用支持自动建父目录的 Write tool）：
   - 一次性脚本 → `scripts/`（带 argparse / 入口块）
   - 可能复用 → `utils/`（纯函数 + docstring，不写 `__main__`）
   - 实验产出 → `out=$(arc output <name>)` 自动创建目录并 echo 路径，所有文件写进 `$out`
   - 自由经验 → `doc/<name>.md`
6. **遇到 plan 没预料的情况**（错误、矛盾、需要决策、要改 objective）：**停下问用户**。例：
   - "step 3 跑出来 RMSE 比基线还高，plan 没规定阈值不达标怎么办，你想怎么处理？"
7. 推完最后一个 step 后：
   - 在 process_log 写一行 `[done] all plan steps complete; ready for /arc-finalize`。
   - 提示用户："plan 完成，建议 `/arc-finalize`。"

## Don't
- 不要每个 step 都暂停问 continue（除非遇到了 plan 没预料的情况）。
- 不要在根目录散落 `.py / .html / .json`（违反 layout 约束）。
- 不要擅自改 `1_objective.md`、`2_plan.md`（要改就停下问）。
- 不要跑长跑（>10 min）之前没跑 smoke。
- 不要塞 binary（图片、ply、ckpt）进 git；这些都进 `output/`，被 `.gitignore`。
