---
name: arc-execute
description: Execute the arc's plan from current state, logging progress, until the plan is complete or an unexpected situation arises. Use when the user says "/arc-execute" or "/arc-execute 260430c".
---

# /arc-execute — 执行计划并留痕

## Steps for the agent

1. 解析 arc：id 或 cwd。
2. 读 `0_meta.md`（frontmatter + history + `## log` 段；log 段只取末尾约 40 行，不要读全）、`1_objective.md`、`2_plan.md`。
3. 判断当前进度：
   - `## log` 里最后一个有结论的步骤是哪个？
   - 对照 plan，下一步应该做什么？
4. **识别可并行步骤并默认派发 sub-agent**：扫描 plan 中下一波待执行的 steps，判断哪些 step 之间**没有数据依赖**（独立 input、独立 output、不共享会被改写的中间状态）。
   - **默认行为**：把彼此独立的 step **并行**派发给多个 sub-agent，加速执行。**在同一条消息里发出多个 Agent 工具调用**（这是触发并发的硬性条件，分多条消息会变成串行）。
   - **subagent 选型**：用 `general-purpose`，**不要显式传 `model` 参数**——`general-purpose` 默认继承父 agent 的模型，从而保持"sub-agent 模型与主模型一致"。
   - **每个 sub-agent prompt 必须自包含**：arc id 与 canonical 路径、它负责的 step 原文、输入文件路径、输出目录（**主 agent 提前调 `arc output <step_name>` 创建好后传给它**）、要回报哪些数字 / 路径、字数上限（建议 ≤200 字）。sub-agent 没有本对话上下文，要把背景一次性给够。
   - **日志单一写入者**：sub-agent **不调 `arc log`**；主 agent 收齐所有并行结果后，**统一**为每个完成的 step 调一次 `arc log "[<step>] <一行结论>"`，避免并发写入撕裂 `## log`。
   - **必须串行的情形**（不要并行）：step A 的 output 是 step B 的 input；多个 step 会改写同一文件（如同一份 `utils/foo.py`、同一个 plan 注解）；step 需要用户交互决策；尚未跑通 smoke test 之前的所有步骤；长跑（>10 min）类 step 之间通常也单独跑，便于失败定位。
   - **拿不准就串行**：并行错误的代价（污染下游、覆盖产物）远大于串行慢一点。
5. **默认一口气推到 plan 末尾**。每完成一个有结论的动作（跑了脚本、得了数字、做了决定）调一次：
   ```bash
   arc log "[<phase>] <一行结论>"
   ```
   （`arc log` 会 append 到 `0_meta.md` 的 `## log` 段，不要手改文件。）
6. **代码 / 产物归位**（子目录按需创建——首次写入前先 `mkdir -p` 或用支持自动建父目录的 Write tool）：
   - 一次性脚本 → `scripts/`（带 argparse / 入口块）
   - 可能复用 → `utils/`（纯函数 + docstring，不写 `__main__`）
   - 实验产出 → `out=$(arc output <name>)` 自动创建目录并 echo 路径，所有文件写进 `$out`
   - 自由经验 → `doc/<name>.md`
7. **遇到 plan 没预料的情况**（错误、矛盾、需要决策、要改 objective）：**停下问用户**。例：
   - "step 3 跑出来 RMSE 比基线还高，plan 没规定阈值不达标怎么办，你想怎么处理？"
8. 推完最后一个 step 后：
   - 调 `arc log "[done] all plan steps complete; ready for /arc-finalize"`。
   - 提示用户："plan 完成，建议 `/arc-finalize`。"

## Don't
- 不要每个 step 都暂停问 continue（除非遇到了 plan 没预料的情况）。
- 不要在根目录散落 `.py / .html / .json`（违反 layout 约束）。
- 不要擅自改 `1_objective.md`、`2_plan.md`（要改就停下问）。
- 不要跑长跑（>10 min）之前没跑 smoke。
- 不要塞 binary（图片、ply、ckpt）进 git；这些都进 `output/`，被 `.gitignore`。
- 不要把有数据依赖的 step 并行（A 的 output 是 B 的 input → 必须串行；并发写同一文件 → 必须串行）。
- 不要给并行 sub-agent 显式传 `model` 参数（应让 `general-purpose` 继承父模型，保持模型一致）。
- 不要让多个 sub-agent 各自调 `arc log`（并发追加会撕裂 `## log`；统一由主 agent 写日志）。
