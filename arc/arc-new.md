---
name: arc-new
description: Create a new arc (task) and immediately run /arc-objective. Use when the user says "/arc-new <brief>", "新建任务 ...", or similar.
---

# /arc-new — 新建任务并锁定目标

链式两步：(1) `arc new` 建骨架，(2) 自动进入 `/arc-objective` 跑 grill-me。

## Steps for the agent

1. 解析 brief：把用户给的描述凝练成 ≤5 个英文词的 snake-friendly 短语作为 brief。如果用户给的很模糊（"做点对齐的事"），先反问一句让用户澄清；不要自己脑补。

2. 调 CLI：
   ```bash
   arc new <brief words...>
   ```
   stdout 第一行是 7-char id（如 `260430c`），stderr 是 human message。从 stdout 抓 id。

3. 立刻提示用户 cd（不要 cd，避免污染 agent 的 cwd 状态；让用户决定）：
   ```
   ✓ Created arc 260430c.
   To start: cd $(arc cd 260430c)
   ```

4. 链式触发 `/arc-objective` skill：把 grill-me 流程跑起来，最终落地到 `1_objective.md`（用 `~/.claude/skills/arc/templates/1_objective.md` 作为骨架）。

## Important
- 不要在 `arc new` 之后立刻自己写 `1_objective.md`。链式进入 `/arc-objective`（grill-me 风格；**提问多少随任务复杂度自适应**，见 `arc-objective.md`）。
- 不要在 `arc new` 之后调 `arc touch` —— `arc new` 已经设了 last_active_at。
- 用户拒绝继续 grill-me（"先这样，我等会写 objective"）时，停在第 3 步，提醒"`arc list` 会显示 `needs 1_objective.md` 的 hint"。
