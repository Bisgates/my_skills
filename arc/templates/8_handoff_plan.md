# 8_handoff_plan — {{ARC_NAME}}

> 由 /arc-finalize 第一阶段生成。**仅起草，agent 不动主项目**。
> 用户回复 `approved` 或 `approved with changes: ...` 后才进入第二阶段。

## 1. Code promote 计划
| from (arc 内) | to (主项目) | 修改类型 | 行数 | 理由 |
|---|---|---|---|---|
| utils/<file>.py | <project>/<path>/<file>.py | new | <N> | <理由> |

> 修改类型 ∈ {new, merge, replace, delete}。

## 2. Docs 提议（沿用 AGENTS.md 协议）
- [NEW] docs/<sub>/<name>.md — <理由 1 行>
- [UPDATE] docs/<...>.md — <改了啥 1 行>
- [STALE?] docs/<...>.md — <为何疑似过期 1 行>

## 3. 跳过项（明确不 promote 的）
- scripts/* （默认全跳）
- utils/<file>.py — <理由>

## 4. 风险 / 待办
- <已知未做的、需要后续 arc 跟进的、或本次 promote 后可能引发的回归点>

---

请确认或修改后回复 `approved`。
