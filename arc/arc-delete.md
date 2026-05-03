---
name: arc-delete
description: Hard-delete an arc (no trace preserved). Use when the user says "/arc-delete <id>", "删除 <id>", "/arc delete <id>", or otherwise explicitly asks to fully remove an arc from disk. For "preserve trace" semantics use /arc-abandon instead.
---

# /arc-delete — 硬删除一个 arc

与 `arc abandon` 的区别：`abandon` 保留目录到 `arcs/abandoned/<id>_*` 留作 trace；`delete` 直接 `rm -rf` canonical 目录 + 清掉 view 软链 + rebuild index，**不留痕**。

## When to delete vs abandon
- **delete**：误建 / 测试残留 / 用户明确说"全删，不要痕迹"。
- **abandon**：已经写过 `1_objective.md` / `2_plan.md` / 跑过实验，但决定不继续 —— 留 trace 给未来回顾。

## Steps for the agent

1. 解析用户给的 id：7-char `YYMMDDx` 或全名 `<id>_<slug>`。

2. 调 CLI：
   ```bash
   arc delete <id>
   ```

3. 命令打印 `arc: deleted <name>.` 后简短确认：
   ```
   ✓ Deleted 260502g_data_dir_inventory_cleanup.
   ```

## Important
- **CLI 无门槛**：不会因为 arc 有 `1_objective.md` / `output/` 等内容就 refuse。意味着用户/agent 自己要确认意图。
- **如果不确定用户意图**：当看到 arc 已经写过 objective/plan/log，先停下问一句"删 → 不留 trace；abandon → 留 trace 到 `arcs/abandoned/`，要哪个？"，不要默认就删。
- **不要自己 `rm -rf arcs/all/<id>*`**：跳过 CLI 会漏掉 view 软链（`arcs/<id>_*` / `arcs/abandoned/<id>_*` 等）和 `index.md` 的刷新。
- 不需要 `--reason`：trace 已经被删了，没地方放。如果用户给了 reason / 想保留原因，劝他改用 `arc abandon`。
