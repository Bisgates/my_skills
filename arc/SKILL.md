---
name: arc
description: Task management protocol with file-based traces. Use when the user explicitly invokes any /arc-* skill or `arc <subcmd>` CLI. Captures objective, plan, execution log, and finalization for tasks that may run in parallel, pause/resume, or be abandoned with traces preserved.
---

# Arc — Task Management Protocol

## When to use this skill
- 用户显式说 `/arc-new <brief>`、`/arc-resume 260430c`、或任何 `arc <subcmd>` CLI。
- 用户描述了一个值得"立项"的任务（多步骤、需要留痕、可能跨 session），且可能要在不同 agent / terminal 中协同。

**不主动触发**：本 skill 不在 session 启动时被触发；只有用户显式用 arc 协议时才进入。

## Core invariants（必须遵守，违反即 bug）
- **唯一物理路径**：`arcs/all/<id>_<slug>/`。任何 cwd / 日志 / 跨任务引用永远写这条路径。
- **状态权威**：`0_meta.md` 的 `status` 字段（`active | paused | done | abandoned`）。`arcs/{active,paused,done,abandoned}/` 是软链派生视图，不是数据。
- **状态翻转**：必须通过 CLI（`arc pause/resume/status/abandon`）。**agent 永远不手改 `0_meta.md`，永远不手 `ln -s`**。
- **ID 引用**：用户用 7 字符 `YYMMDDx`；CLI 也接受全名 `<id>_<slug>` 用于 tab-completion。
- **Done 硬门槛**：`arc status <id> done` 要求 `9_*.md` 存在且非空。
- **Abandoned 硬门槛**：必须给 `--reason "..."`。
- **Delete 是硬删（不保留 trace）**：仅当 arc 只有 `0_meta.md`（没动过的空骨架）时直接允许；任何额外文件 / 子目录都需 `--force` 强制。"想保留痕迹"用 `arc abandon`，"想彻底清掉"用 `arc delete`。
- **多 active 允许**：每个 terminal 独立 cwd 表达"焦点"；resume 不自动 pause 别的。

## File layout

### Project root
```
<project_root>/arcs/
  all/<id>_<slug>/                 # canonical 物理位置
  paused/   done/   abandoned/     # 软链视图（仅这三个状态）
  <id>_<slug>                      # active 状态的软链直接放 arcs/ 根
  index.md                         # 自动生成
```

`active` 状态没有专属子目录；active 软链直接位于 `arcs/<id>_<slug>`。

### 单个 arc 内部
```
arcs/all/<id>_<slug>/
  0_meta.md                 # 必选；脚本生成与维护
  1_objective.md            # 必选；/arc-objective 生成
  2_plan.md                 # 必选；/arc-plan 生成
  3_process_log.md          # 可选但强烈建议；arc log 追加
  4_*.md ~ 7_*.md           # 留白，自由命名（pivot/eval/blocker/decision_*）
  8_handoff_plan.md         # 仅 finalize 触发时生成
  9_summary.md              # done 状态硬门槛
  doc/                      # 自由 freeform 笔记（按需创建）
  utils/                    # 候选 promote 到主项目的代码（按需创建）
  scripts/                  # 一次性脚本，不 promote（按需创建）
  output/<YYMMDD_HHMM>_<name>/   # 实验产出（arc output 创建）
```

**子目录全部按需创建**：`arc new` / `arc spawn` 只生成 `0_meta.md`，子目录由 agent 写文件时自己 `mkdir -p`，或由 `arc output` 创建。

**根目录禁放散落 `.py / .html / .json / .ply`**。所有代码进 `utils/` 或 `scripts/`，所有产物进 `output/`。

## Phase commands（入口与子 skill）

| 阶段 | 触发 | 见子 skill |
|---|---|---|
| 立项 | `/arc-new <brief>` | `arc-new.md` |
| 锁定目标 | `/arc-objective [<id>]` | `arc-objective.md` |
| 写计划 | `/arc-plan [<id>]` | `arc-plan.md` |
| 执行 | `/arc-execute [<id>]` | `arc-execute.md` |
| 恢复上下文 | `/arc-resume <id>` | `arc-resume.md` |
| 派生子任务 | `/arc-spawn <brief>` | `arc-spawn.md` |
| 收尾 + promote | `/arc-finalize [<id>]` | `arc-finalize.md` |
| 硬删除（不保 trace） | `/arc-delete <id>` | `arc-delete.md` |

## CLI cheatsheet（agent 直接调）
```bash
arc init                              # 一次性冷启动；自动写 AGENTS.md hook
arc new <brief...>                    # 创建骨架
arc spawn <brief...> [--parent <id>]  # 子任务
arc pause <id?> --note "..."
arc resume <id>                       # echoes canonical path
arc status <id> {active|paused|done|abandoned} [--note ...] [--reason ...]
arc abandon <id> --reason "..."
arc delete <id> [--force]             # 硬删；只有 0_meta.md 时直接允许，否则需 --force
arc touch <id?>
arc log [-i <id>] <text...>
arc output [-i <id>] <name>           # echoes canonical output dir
arc list                              # prints index.md
arc cd <id>                           # echoes canonical path; use: cd $(arc cd 260430c)
arc rebuild                           # 修复软链 + index
```

## Agent behavior guidance
- **每完成一个有结论的步骤**（跑了脚本、得了数字、做了决定），调一次 `arc log "..."`。
- **写代码时区分**：可能复用 → `utils/`；一次性 → `scripts/`。拿不准先丢 `scripts/`。
- **写实验产出**：先 `out=$(arc output <name>)` 拿目录，所有产物写进 `$out`，避免散落。
- **遇到 plan 没预料的情况**：停下问用户，不要擅自改 objective / plan。
- **检测到边界感时建议 spawn**：如果发现一段工作有自己独立的 objective、独立验收，建议用户 `/arc-spawn <brief>`，但不擅自 spawn。
- **session 中途**：当用户说 `pause/abandon/...` 时直接调 CLI；不要试图代替 `0_meta.md` 写状态。
