---
name: arc-delete
description: Hard-delete an arc (no trace preserved). Use when the user says "/arc-delete <id>", "删除 <id>", "/arc delete <id>", or otherwise explicitly asks to fully remove an arc from disk. For "preserve trace" semantics use /arc-abandon instead.
---

# /arc-delete — 硬删除一个 arc

与 `arc abandon` 的区别：`abandon` 保留目录到 `arcs/abandoned/<id>_*` 留作 trace；`delete` 直接 `rm -rf` canonical 目录 + 清掉 view 软链 + rebuild index，**不留痕**。

## When to delete vs abandon
- **delete**：`arc new` 之后什么都没动 / 只有 meta 的空骨架；误建；测试残留。
- **abandon**：已经写过 `1_objective.md` / `2_plan.md` / 跑过实验，但决定不继续 —— 留 trace 给未来回顾。

## Steps for the agent

1. 解析用户给的 id：7-char `YYMMDDx` 或全名 `<id>_<slug>`。

2. 先读一眼 `arc list`（或直接看 `arcs/all/<id>_*` 目录）确认这个 arc 有没有内容。

3. 调 CLI：
   ```bash
   arc delete <id>
   ```
   - 如果 arc 只有 `0_meta.md`，命令直接成功。
   - 如果 arc 有 `1_objective.md` / `2_plan.md` / `3_process_log.md` / `output/` / `doc/` 等额外内容，命令会 refuse 并打印有哪些文件。

4. 命令 refuse 时，**停下来问用户**：
   ```
   arc 260502g 含有: 1_objective.md, 2_plan.md, output/...
   是要 (a) 强制硬删（--force，不保留任何 trace）
        (b) 改用 arc abandon（保留目录到 arcs/abandoned/）
   ```
   只有用户明确说 "强制 / force / 都删了" 才加 `--force`：
   ```bash
   arc delete <id> --force
   ```

5. 删除成功后简短确认：
   ```
   ✓ Deleted 260502g_data_dir_inventory_cleanup.
   ```

## Important
- **永远先 list / 看目录再删**。不要凭 id 盲删。
- **不要自己 `rm -rf arcs/all/<id>*`**：跳过 CLI 会漏掉 view 软链（`arcs/<id>_*` / `arcs/abandoned/<id>_*` 等）和 `index.md` 的刷新；`arc rebuild` 虽然能修复，但流程不对。
- 不需要 `--reason`：trace 已经被删了，写 reason 没地方放。如果用户给了 reason / 想保留原因，劝他改用 `arc abandon`。
