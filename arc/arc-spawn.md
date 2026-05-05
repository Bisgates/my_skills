---
name: arc-spawn
description: Spawn a child arc when a separable task is discovered during another arc's execution. Use when the user says "/arc-spawn <brief>" or "把这块拆成新 arc".
---

# /arc-spawn — 派生子任务

## Steps for the agent

1. 解析 parent：
   - 用户当前 cwd 在某个 arc 内？parent = 该 arc。
   - 不在？必须给 `--parent <id>`。
2. 调 CLI：
   ```bash
   arc spawn <brief words...>          # parent 自动从 cwd 推
   # 或
   arc spawn <brief words...> --parent 260430a
   ```
   stdout 抓新 id。

3. **不**链式调 `/arc-objective`、**不**切焦点：用户的描述场景是"开新 terminal 再做"。

4. 报告（短）：
   ```
   ✓ Spawned arc 260430b (child of 260430a).
   To start working on it: open a new terminal and run /arc-resume 260430b
   (or /arc-objective 260430b if you want to define its goal first).
   ```

5. 在 parent arc 留一行 log（保留 trace，让 parent 之后看 log 知道 spawn 过）：
   ```bash
   arc log -i <parent_id> "[spawn] new child arc 260430b: <brief>"
   ```

## When to suggest /arc-spawn vs add-step

- 同一 objective 的细化 → 在当前 arc 加 step（不 spawn）
- 不同 objective、独立验收标准 → 建议 spawn
- 边界拿不准 → 问用户"要拆吗？" 让用户决定，不擅自 spawn

## Don't
- 不要 spawn 后自动写 `1_objective.md`（违反 Q8 决议）。
- 不要把 `parent` 字段写进 child 之外的任何地方；index 会自动反向显示 children 关系。
- 不要在 spawn 时暂停 parent；spawn 不切焦点。
