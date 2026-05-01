---
name: arc-objective
description: Run grill-me to define the arc objective with crisp boundary and acceptance criteria. Use when the user says "/arc-objective", "/arc-objective 260430c", or right after /arc-new chains in.
---

# /arc-objective — 用 grill-me 锁目标

## Steps for the agent

1. 解析 arc：
   - 用户给了 id？跑 `arc cd <id>` 拿路径。
   - 没给？用 cwd（应在 `arcs/all/<id>_*/`）；不在则报错并要 id。

2. 读 `0_meta.md`（看 brief / parent）获得上下文。如果 `parent` 非 null，读 parent 的 `1_objective.md` 和 `9_summary.md`（如有），用作约束语境。

3. **进入 grill-me 循环**（用户偏好的"一次一问、给推荐答案"风格）：
   - 每问一题给一个推荐答案。
   - 每个分支锁定后才进下一个分支。
   - 不要一口气问 5 个问题；不要不给推荐答案。
   - 主要分支建议覆盖：
     - Goal 是什么（动词必须具体，禁止"研究 / 探索 / 看看"）
     - In-scope vs Non-goals（边界）
     - 验收 L1 量化指标 + L2 可视化（沿用 workspace AGENTS.md 准则）
     - 已知约束 / 假设
     - 上游依赖（数据 / 上游 arc / 主项目代码）
     - 主要风险

4. 全部锁定后，把对话**压缩**成 `1_objective.md`，用 `~/.claude/skills/arc/templates/1_objective.md` 作为骨架。**只写决议，不抄对话。** 锁定后避免反复修改；目标变化用 4_pivot.md 或新 arc 表达。

5. 写完后调 `arc touch <id>`（脚本会更新 last_active_at + rebuild index）。

6. 最后告诉用户两条候选下一步：
   - `/arc-plan` 进入计划阶段
   - 或者先停下来 sanity check `1_objective.md`

## Don't
- 不要省 grill-me 直接生成 `1_objective.md`。
- 不要把 acceptance 写得含糊（"效果好"、"基本对齐"）；指标必须是数字 + 阈值。
- 不要在 `1_objective.md` 里夹任何执行细节（那是 plan 的事）。
