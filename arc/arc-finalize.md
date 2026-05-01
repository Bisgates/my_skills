---
name: arc-finalize
description: Two-stage finalization — first draft 8_handoff_plan.md (no project changes), then after user "approved", actually promote code/docs and write 9_summary.md. Use when the user says "/arc-finalize" or "/arc-finalize 260430c".
---

# /arc-finalize — 收尾两阶段

**阶段一只起草，绝不动主项目**。等用户回 `approved`（或 `approved with changes: ...`）才进阶段二。

## Stage 1 — Draft 8_handoff_plan.md

1. 解析 arc：id 或 cwd。
2. 全面巡检：
   - `utils/*.py`：每个文件评估 promote 价值（值得复用？纯函数？跟主项目代码是否有冲突？）
   - `scripts/*.py`：默认全跳，但要列出来声明跳过
   - `doc/*.md`：判断是否值得提级到主项目 `docs/`
   - `3_process_log.md` 全文扫读：找到"踩坑 >15 min"、"定下命名约定"、"读了 paper"、"做了重大决策" → 触发 [NEW] 提议（沿用 workspace AGENTS.md 的 New-knowledge triggers）
   - `1_objective.md` 的 acceptance 是否达成 → Verification 草稿
3. 用 `~/.claude/skills/arc/templates/8_handoff_plan.md` 生成 `8_handoff_plan.md`，**四个区块全部填**：
   - Code promote 计划（每个 utils/*.py 必须出现在 promote 表 OR 跳过项里恰好一次）
   - Docs 提议 [NEW]/[UPDATE]/[STALE?]
   - 跳过项（明确不 promote 的）
   - 风险 / 待办
4. 调 `arc touch <id>`。
5. 报告："草稿在 8_handoff_plan.md，请 review 后回 `approved` 或 `approved with changes: ...`。"
6. **停下**，进入等待状态。**不要**进入阶段二。

## Stage 2 — Execute (after user "approved")

仅在用户明确说 `approved` 或类似时启动。如果是 `approved with changes: ...`，先按 changes 改 8_handoff_plan.md，再继续。

1. **Code promote**：按 8_* 的表格执行。
   - 每个文件改完调 `arc log "[promote] utils/<x>.py -> <project>/<path>/<x>.py (<modtype>, <N> lines)"`。
   - 主项目的代码风格遵守该 subproject 的本地规约（参考 workspace AGENTS.md 的 Code Style）。

2. **Docs 落地**：
   - `[NEW]`：创建文件，必须带 yaml front-matter（`id / type / domain / summary / status / last_verified / related_code / related_docs`）。
   - `[UPDATE]`：精确改动；保留原 yaml front-matter；更新 `last_verified` 为今天。
   - `[STALE?]`：**仅打标，不动文件**；放进 9_summary.md 的"待用户处理"区。

3. **不进 git commit**（项目目前没接 git；上 git 后此 skill 需要扩展）。

4. 写 `9_summary.md`，用 `~/.claude/skills/arc/templates/9_summary.md` 骨架。**六个字段全部填**：
   - TL;DR（≤3 行）
   - Promoted Code（写"无"也可）
   - Docs Changes（含 STALE? 未处理项）
   - Verification（L1 + L2，对照 1_objective.md 的 acceptance）
   - Follow-ups
   - Doc Suggestions

5. 翻状态：
   ```bash
   arc status <id> done
   ```
   若 `9_summary.md` 不存在或为空，CLI 会拒绝；说明上一步漏写了。

6. 报告：完成 + 总结改了什么 + 是否有 STALE? 留给用户决定。

## On failure mid-stage-2
- 如果 promote 中途出错：
  - **不要**调 `arc status done`（任务保持 active）。
  - 在 process_log 写 `[finalize-failed] <什么坏了> <已做到哪>`。
  - 报告用户，等指令（修 / 回滚 / 略过）。

## Don't
- 不要在 Stage 1 动主项目任何文件。
- 不要在 Stage 2 跳过 9_summary.md 直接 `arc status done`（CLI 会拒绝）。
- 不要把 `output/` 的产物 promote 到主项目（默认 .gitignore，本就是临时产物）。
- 不要把 8_/9_ 区块漏填——每个字段至少写"无"。
