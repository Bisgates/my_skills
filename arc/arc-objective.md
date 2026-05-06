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

3. **先估复杂度，再定提问深度**（grill-me 在 arc 里是**自适应**的，不是固定题量）：
   - **简单任务**（单目标、范围小、验收可从 brief 直接读出、无模糊分叉）：**少问**。只澄清真正还缺的 0–2 个点；一旦能写出 crisp 的 goal + 可检验 acceptance，**立即落盘**，不要为了「走完流程」而凑问题。
   - **复杂任务**（多目标/多干系人、成功标准模糊、跨系统或大 scope、强依赖或高风险）：**多问**。耐心走分支，把核心 goal、验收、边界、约束、依赖、风险逐个对齐；仍遵守「一次一问、给推荐答案」，但**该问的不要省**。
   - **切忌**：简单任务也硬套完整问卷、把分支清单当打卡表凑满；或复杂任务为了省事只问一两句就写 objective。
   - 若吃不准算简单还是复杂，**先问一句**让工作量大小的 self-assessment 露出来，再决定要不要展开长对话。

4. **进入 grill-me 循环**（用户偏好的"一次一问、给推荐答案"风格）：
   - 每问一题给一个推荐答案。
   - 每个分支锁定后才进下一个分支。
   - 不要一口气问 5 个问题；不要不给推荐答案。
   - **提问优先级：先核心，再边界。** 任务核心（要做什么、为什么做、成功长什么样）是第一位的；边界 / 约束 / 风险固然重要，但属于在核心锁定之后再收紧的护栏。切勿主次颠倒，一上来就纠缠 scope / 非目标 / 风险这类外围问题，让用户感觉跑偏。
   - 下列分支是**菜单**，按优先级选用；**简单任务只碰前两段里仍 unclear 的项**，其余可从略或用一句「沿用项目默认 / 无附加约束」在 `1_objective.md` 里收束，勿逐项盘问。
     1. **核心 Goal**：要解决什么问题、为什么现在做（动机 / 触发点）、成功长什么样。动词必须具体，禁止"研究 / 探索 / 看看"。
     2. **验收标准**：L1 量化指标 + L2 可视化（沿用 workspace AGENTS.md 准则），让"做完了"可被检验。
     3. In-scope vs Non-goals（边界）。
     4. 已知约束 / 假设。
     5. 上游依赖（数据 / 上游 arc / 主项目代码）。
     6. 主要风险（如果没有风险，不要硬凑，只输出真正的风险）。

5. 全部锁定后，把对话**压缩**成 `1_objective.md`，用 `~/.claude/skills/arc/templates/1_objective.md` 作为骨架。**只写决议，不抄对话。** 锁定后避免反复修改；目标变化用 4_pivot.md 或新 arc 表达。

6. 写完后调 `arc touch <id>`（脚本会更新 last_active_at + rebuild index）。

7. 最后告诉用户两条候选下一步：
   - `/arc-plan` 进入计划阶段
   - 或者先停下来 sanity check `1_objective.md`

## Don't
- **禁止零对齐编造**：brief 含糊或缺验收时，不能直接写一篇自说自话的 `1_objective.md`；若 brief 已足够清楚，允许极短确认（如复述 goal + acceptance 一句「这样写进 objective 可以吗？」）后直接落盘，**不**为凑题量多绕几圈。
- 不要把 acceptance 写得含糊（"效果好"、"基本对齐"）；指标必须是数字 + 阈值。
- 不要在 `1_objective.md` 里夹任何执行细节（那是 plan 的事）。
