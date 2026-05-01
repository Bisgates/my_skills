---
name: arc-plan
description: Generate 2_plan.md based on locked 1_objective.md. Use when the user says "/arc-plan" or "/arc-plan 260430c".
---

# /arc-plan — 写执行计划

## Steps for the agent

1. 解析 arc：与 /arc-objective 同（id 或 cwd）。
2. 读 `1_objective.md`；如果不存在或为骨架，停下提示先跑 `/arc-objective`。
3. 读 `0_meta.md` 的 parent（如有），读 parent 的 `2_plan.md` / `9_summary.md` 作为参考。
4. 问用户 1–3 个澄清问题（如有），每个给推荐答案；如果 1_objective 已经够清楚，可以直接写。
5. 用 `~/.claude/skills/arc/templates/2_plan.md` 作为骨架，写 `2_plan.md`。重点：
   - **Smoke Test First** 区块必填：先用小数据跑一遍验证 plan，再做正式实验。这是 workspace AGENTS.md 强调的"先做数据契约/预处理 + smoke train"。
   - **Out-of-Scope** 必填，可写"无"，但要思考过。
   - Steps 自由格式，不强制 checkbox；可以写编号 + 子项。
6. 调 `arc touch <id>` 后告诉用户："plan ready, run /arc-execute when you're ready"。

## Don't
- 不要在 plan 里复述 objective（plan 假设 objective 已锁）。
- 不要写"先调研一下" 这种没产出的 step；每个 step 必须有 expected output。
- 不要绕过 smoke test 直接安排长跑（除非用户明确要求）。
