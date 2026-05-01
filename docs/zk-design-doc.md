# zk — Design Doc (v1)

> **zk** — agent-first Zettelkasten
> agent-curated knowledge base for code projects

本文档汇总 zk v1 的设计决定。每一节都来自一轮明确的讨论，可作为后续实现 `zk` skill 与命令的契约。

---

## 0. 设计公理

1. **doc 装"项目特定的活知识"**，不装代码地图、API 参考、操作手册——后者归 `docs/` 或 script。
2. **4 类内容**：`concept` / `decision` / `gotcha` / `finding`。可扩，但只在用过一段时间确实需要时才扩。
3. **agent 是主要写手**，人偶尔写；破坏性结构改动需要人确认。
4. **加法自主，减法谨慎**——为道日损但不轻易损。
5. **每次 doc 改动 = 一次独立 git commit**，让 `git log -- zk/` 成为认知演化史。
6. **质量重于覆盖率**——信息不足时宁可不建 note。

---

## 1. 命名

- 短名（命令、目录）：**`zk`**
- 短描述：**`zk — agent-first Zettelkasten`**
- 长描述：**`zk — agent-curated knowledge base for code projects`**

---

## 2. 物理布局

```
zk/
  .zk-config.yaml              # 系统元数据（slug 规则、行数上限、索引设置）
  README.md                    # 一句话指向 AGENTS.md > zk 节
  index.md                     # 自动生成，硬上限 200 行
  notes/
    concepts/
    decisions/
    gotchas/
    findings/
  MOC/                         # 人写的导览图（按需）
  sources/                     # 待蒸馏的大块原始素材；仅可被 cite，不可被 [[]] 链接
```

**目录命名 `zk/` 而非 `docs/`** 的理由：
- 避免与工程惯例上的"代码文档" namespace 冲突
- 视觉边界清晰：`docs/` = 静态人写文档，`zk/` = agent + 人共维护的活知识
- skill 命令与路径同名（`zk:new` 写 `zk/notes/...`），记忆负担最低
- 老项目兼容：现有 `docs/` 大杂烩可保留不动，zk 起新摊子

---

## 3. 内容范围（types）

只装这 4 类：

| 类型 | 例子 | 为什么进 zk |
|---|---|---|
| `concept` | "项目里 'session' 的语义"、"alpha batch window 的定义" | 概念定义需要单点真值 |
| `decision` | "为什么用 symlink 而不是 copy" | ADR 风格，决策理由可追溯 |
| `gotcha` | "macOS 上 symlink 在 zsh tab-complete 的怪行为" | 反直觉/踩坑值得显式记 |
| `finding` | "在 batch 里加 X 因子提升 Sharpe" | 经验性发现 + 出处 |

**不进 zk**：
- 代码地图/模块说明 → 真值在代码本身，docs 会越来越骗 agent
- 操作手册/runbook → 应该是 script 或 skill，不是文字
- API 参考 → 自动生成

未来可扩，但只在跑过一段时间确实需要时才加新 type。

---

## 4. 单 note 规约

### 4.1 命名（slug）

- **kebab-case，纯英文**
- **全局唯一**（在 `notes/**` 范围内）
- 撞名时强制语义更精确（不允许 `-2` 之类敷衍后缀）
- 文件名 = slug = `[[]]` 的链接目标

### 4.2 frontmatter

```yaml
---
slug: batch-x-factor-lifts-sharpe-v2
title: Batch X 因子提升 Sharpe（修正版）
type: finding                    # concept | decision | gotcha | finding
summary: OOS 上 batch 加 X 因子仅 +0.5% Sharpe，远低于 IS 上的 +3%，但仍小幅正向。
aliases: [X 因子, x-factor batch, batch x因子]
supersedes: [batch-x-factor-lifts-sharpe]
contradicts: []
---
```

| 字段 | 必填 | 约束 |
|---|---|---|
| `slug` | ✓ | = 文件名 stem |
| `title` | ✓ | 中/英自由，给人读 |
| `type` | ✓ | 4 类之一，必须与所在 folder 一致；以 frontmatter 为权威 |
| `summary` | ✓ | ≤ 80 字符（中文约 50 字），按 type 模板写 |
| `aliases` | ✓（可空） | 搜索同指词；**禁止**横切分类语义 |
| `supersedes` | ✓（可空） | skill 自动维护反向 `superseded_by` |
| `contradicts` | ✓（可空） | skill 自动镜像（对称） |

### 4.3 正文

- 目标 50–300 行
- **硬上限 600 行**（含 frontmatter）
- 超长 → 必须拆，除非 `type: source`（source 不允许被 `[[]]` 链接，只能被 cite）
- 链接全部用 `[[slug]]`，resolver 在 `notes/**` 全局
- `[[]]` 之外不需要任何"关联类型"标记

### 4.4 summary 写作模板

| type | 模板 |
|---|---|
| concept | "X 是 Y 的 Z。" |
| decision | "选 X 不选 Y，因为 Z。" |
| gotcha | "在 X 条件下 Y 会失败，需 Z 规避。" |
| finding | "在 X 上观察到 Y，但仅限 Z 条件。" |

### 4.5 aliases 的语义

- ✅ "如果有人想搜这个 note，可能会输入什么词？" → 写进 aliases
- ❌ "这个 note 还属于什么大类别？" → **不写 aliases**，写成 `[[]]` 链向 MOC

**禁止把 `aliases` 当 `tags` 用**。横切分类机制 v1 不引入；将来真有需要再加 `tags` 字段。

---

## 5. 链接语义

| 关系 | 表现位置 | 反向维护 |
|---|---|---|
| 普通关联 | 正文 `[[xx]]` | 由 backlink 工具自动得到 |
| 推翻 / 取代 | frontmatter `supersedes:` | skill 自动写 `superseded_by:` |
| 矛盾 | frontmatter `contradicts:` | skill 自动镜像（对称） |

**只此两类 typed relation**——`refines`、`related`、`see-also` 全部用纯 `[[]]` 在正文里写，避免 over-engineering。

### agent 行为约束

- 读到带 `superseded_by` 的 note → 默认跳到新版本（除非任务明确要历史）
- 读到带 `contradicts` 的 note → 必须读双方，输出里 surface 矛盾，不能只引用一边
- 链可能形成 A←B←C；skill 提供 `--resolve-latest` 折叠到末端

---

## 6. 读端流程

```
任务开始
  └─ 读 zk/index.md（≤200 行；按 type 列出 slug + summary）

任务中遇到项目术语 / 模糊处
  ├─ rg <term> zk/notes/        # 命中 slug / title / aliases / summary
  ├─ 没命中 → 读相关 MOC 顺 [[]] follow
  └─ 仍无 → 不建 note，改问用户或在正文备注"未确认"
```

**不引入 embedding 检索**（YAGNI）。Claude/Cursor 的 grep + 读 [[]] 已足够，且永远与真值同步。

---

## 7. 写端流程

### 7.1 自主度

| 操作 | 自主 / 需确认 |
|---|---|
| 改正文 / 改 frontmatter（非破坏性） | 自主 |
| 新建 note | 自主 |
| `supersedes` / `contradicts` | 自主（git 兜底） |
| rename slug / 改 type / 拆 / 合 | 自主，但 skill 必须**单 commit 原子完成** |
| MOC 重排 | 自主 |
| **delete** | **需确认** |
| **批量操作（audit 一次给多条建议）** | **需确认（一次性 review）** |

**两条总规则**：
1. 单步可 revert 的操作 → 自主
2. delete + 批量 → 需确认

### 7.2 操作面

- **正文**：直接 edit（agent 自然写作）
- **结构性改动**（新建、改 slug、改 type、supersedes、拆/合、delete）：**走 skill 命令**，否则破坏不变量

### 7.3 commit 纪律

- 每次 doc 变更 = 单独 commit，**不与代码 commit 混合**
- msg 模板：`zk(<type>): <op> <slug> — <summary>`
- 例：`zk(finding): new batch-x-factor-lifts-sharpe-v2 — OOS 上 batch X 因子仅 +0.5%...`

### 7.4 clarify 循环（朴素版）

```
任务中遇到一个概念：
  ├─ 已有且对：不动
  ├─ 已有但有偏差：直接 edit 修正
  ├─ 已有但完全过期：写新 note + supersedes 旧
  └─ 没有但值得记：新建 note（哪怕只有 summary + 几段）
信息不足时不建 note。
```

**不引入** `stub` 工作流、不引入 `status` 字段、不结构化 body 段——保持最小机制。

---

## 8. /arc 集成（弱耦合，via AGENTS.md）

不写 hook，不挂代码注册表。机制：

1. `zk init` 在 `AGENTS.md` 末尾插入 marker 包裹的一节，描述 zk 存在 + 用法
2. /arc finalize 流程让 agent 读 AGENTS.md，自然知道 "任务结束时考虑沉淀到 zk"
3. agent 调 `zk:from-context` 把当前任务/对话蒸馏成 doc 候选清单，逐条 review/编辑/丢弃

`AGENTS.md` 注入的标准块：

```markdown
<!-- zk:start -->
## zk: 项目知识系统

本项目使用 zk（agent-first Zettelkasten）维护项目特定的概念、决策、踩坑、实验结论。

- 入口：`zk/index.md`
- 4 类内容：concept / decision / gotcha / finding，分别在 `zk/notes/<type>/`
- 链接全部用 `[[slug]]`，slug 全局唯一
- 写入用 skill `zk:*` 命令；正文可直接 edit
- 任务结束时（含 /arc finalize），review 是否有可沉淀内容，
  用 `zk:from-context` 把当前对话蒸馏成候选

完整规则见 [zk skill](../zk/SKILL.md)。
<!-- zk:end -->
```

**关键点**：
- `zk init` 幂等：再跑一次只更新 marker 之间的内容，不重写其他段
- AGENTS.md 是公共 surface，zk 通过它通信而不修改任何外部 skill
- 默认插入位置：文件末尾（marker 包裹后下次按 marker 找位置，不会乱跑）
- hook 注册表方案保留作未来选项（YAGNI，等 AGENTS.md 软约束合规率不够再补）

---

## 9. skill 命令骨架（v1 推荐范围）

| 命令 | 作用 | 自主度 |
|---|---|---|
| `zk init` | 初始化项目（建目录 + AGENTS.md 注入），幂等 | — |
| `zk new <type> <slug>` | 新建 note（模板 + frontmatter 校验） | 自主 |
| `zk rename <old> <new>` | 改 slug + 全局改反链，单 commit | 自主 |
| `zk move <slug> <new-type>` | 改 type + 移 folder + 改 frontmatter | 自主 |
| `zk supersede <old> <new>` | 自动维护反向 | 自主 |
| `zk contradict <a> <b>` | 双向写入 | 自主 |
| `zk split <slug>` | 拆 note，原子单 commit | 自主 |
| `zk merge <a> <b>` | 合并 note，原子单 commit | 自主 |
| `zk delete <slug>` | 删 note，需确认 | 需确认 |
| `zk index` | 重生成 `zk/index.md` | 自主 |
| `zk lint` | 检查不变量（slug 唯一、行数、断链、frontmatter schema） | 只读 |
| `zk audit` | 扫全库报告候选改动（重复、孤岛、超长），不写 | 输出待人 review |
| `zk recent [N]` | 列最近 N 次 doc commit | 只读 |
| `zk from-context` | 把当前对话/任务上下文蒸馏成 doc 候选清单 | 输出待人 review |

---

## 10. 仍未决的 gap（v1 留白，按需迭代）

### Gap A. MOC 的具体玩法
- 谁写、何时建、是否限制体积——v1 不约束
- 跑一段看实际使用频率再补规则

### Gap B. `.zk-config.yaml` 的字段集
- 初期可能只有 `version: 1` 一行
- 写第一版 skill 时再敲

### Gap C. agent 判断"doc-worthy"的启发式
- `zk:from-context` 的判断逻辑写成 3–5 条软启发式放在 zk SKILL.md 里
- 不写代码硬规则；用一段时间发现命中率不行再迭代
- 候选启发式：
  - 出现"项目特定概念被解释" → concept 候选
  - "决定 X 不选 Y 因为 Z" 模式 → decision 候选
  - "踩坑 / 反直觉" → gotcha 候选
  - "实验结果 / 数据观察" → finding 候选
  - 高 clarification cost（agent 花了不少时间才搞明白）→ 强信号

### Gap D. 项目首次 bootstrap
- v1 选 (i) 完全空，等任务自然沉淀
- 不做 `--from-existing-docs` 自动扫描，避免老 `docs/` 大杂烩污染进来

### Gap E. Obsidian 兼容
- v1 不强制
- 设计选择不主动破坏（slug-only `[[]]` 依赖 Obsidian 的 unique note name 配置）
- 想用时再确认

### Gap F. 多人协作 / 同步
- v1 不解决，单人单机用，git 自然兜底
- 多 agent 并发再设计 lock 机制

---

## 11. 实现路线建议

最小可行起步（按顺序）：

1. **写 `zk/SKILL.md`** —— 把本文档第 0–8 节浓缩成 agent 可读的 skill 指令
2. **实现 `zk init`** —— 建目录骨架 + 写 AGENTS.md 注入块
3. **实现 `zk new`** —— 模板 + frontmatter 校验
4. **实现 `zk lint`** —— 不变量检查
5. **实现 `zk index`** —— 自动生成 index.md

之后按需添加 `rename`、`supersede`、`split`、`from-context` 等。

---

## 12. 决策溯源

本设计来自 2026-05-01 的一轮 grill-me 讨论，关键决策点：

- §3 4 类 type 的范围限定（拒绝 runbook / code map）
- §4.3 600 行硬上限（agent 读 budget 角度）
- §2 子目录 + slug-only 链接（修正了最初的"平铺 + 文件名前缀"提议）
- §4.5 用 `aliases` 不用 `tags`（避免横切分类污染）
- §4.2 强制 `summary ≤ 80`（让 index.md 成为知识摘要而非目录）
- §5 只 `supersedes` + `contradicts` 两类 typed（拒绝 `refines` 等 over-engineering）
- §7 git commit 强纪律使破坏性操作可自主（除 delete + 批量）
- §7.4 拒绝 stub 工作流（最小必要动作原则）
- §8 用 AGENTS.md 注入替代 hook 注册表（与 agent 真实工作方式对齐）
- §2 目录命名 `zk/` 不是 `docs/`（与 docs 工程惯例解耦）
