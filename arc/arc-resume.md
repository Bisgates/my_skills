---
name: arc-resume
description: Resume an arc with full context load and a "where are we" report. Use when the user says "/arc-resume 260430c" or "继续 260430c".
---

# /arc-resume — 恢复任务上下文

## Steps for the agent

1. 调 CLI 翻状态（机械层）：
   ```bash
   arc resume <id>
   ```
   stdout 是 canonical 路径（`arcs/all/<id>_<slug>`）。stderr 是状态变化提示。

2. 提示用户 cd（不替用户 cd）：
   ```
   To work on it: cd $(arc cd <id>)
   ```

3. 加载 context（按存在性逐个读）：
   - `0_meta.md`：拿 brief / status 历史 / parent
   - `1_objective.md`：拿 goal / acceptance（如不存在，hint = `needs 1_objective.md`）
   - `2_plan.md`（如存在）
   - `3_process_log.md` **末尾 40 行**（用 `tail` 或 grep；不要读全）
   - `8_handoff_plan.md`（如存在，意味着 finalize 进行中）

4. 输出"重启报告"，结构：
   ```
   ## Arc 260430c — <brief>
   - status: <prev_status> -> active
   - parent: <parent_id or none>
   - last_active: <ISO>

   ## Goal (from 1_objective.md)
   <一句话>

   ## Plan summary (from 2_plan.md)
   <bullet 化的 steps，1 行 1 个>

   ## Recent activity (last 40 lines of 3_process_log.md)
   <精简到 ~10 行关键事件>

   ## Where we are
   <一句话：上次卡在哪 / 已完成到哪>

   ## Next-step candidates
   - A: ...
   - B: ...
   - C: ...
   ```

5. 等用户选下一步；不擅自进 /arc-execute。

## Don't
- 不要读 process_log 全文（可能很长）。需要更深 context 时用 `grep` / `Read --offset` 按需取。
- 不要自动 pause 别的 active arc。多 active 是被允许的。
- 如果 status 是 `done`，提醒用户 "this arc is done; resuming will set it back to active"，让用户确认意图。
