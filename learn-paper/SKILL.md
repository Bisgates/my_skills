---
name: learn-paper
description: 把指定主题文件夹里的 paper PDF 转为同目录、单文件、自含 CDN 的交互式学习 HTML，按第一性原理讲解，80% 篇幅给核心 insight，以费曼 / karpathy 风格写给资深读者。Use when the user runs `/learn-paper <folder>` or asks to "学习 / 讲解 / 拆解 X 文件夹里的 paper" inside the `learn_with_agent` project.
---

# learn-paper

## Quick start

```
/learn-paper "260506_Coding Agents_alphazero"
/learn-paper "260506_Coding Agents_alphazero" --align
```

输出：`<folder>/<paper-name>.html`（与 PDF 同名同级，单文件，所有依赖走 CDN）。

## Trigger discipline

只在用户**显式**触发时进入：`/learn-paper <folder>`，或自然语言"学习 / 讲解 / 拆解 X 文件夹里的 paper"。看到 PDF **不要主动**开写。

## Workflow

1. **定位输入**
   - 解析 `<folder>`（相对项目根或绝对路径都接受）。
   - 在 folder 内找 `*.pdf`；多个 PDF 时**问用户**选哪个，不要默认第一个。
   - 若 `<folder>/_drafts/paper.md` 存在，**优先读它**；否则直接 Read PDF。
   - **不读其他主题文件夹**。

2. **生成模式分支**
   - 默认（无 `--align`）：跳到第 4 步。
   - 加 `--align`：执行第 3 步核心对齐 checkpoint。

3. **核心对齐（仅 `--align`）**
   - 在对话里输出，并写入 `<folder>/_drafts/outline.md`：
     1. **One-paragraph thesis**：paper 解决什么问题、关键 insight、与已有方案的根本差异。
     2. **章节大纲**：每章标题 + 一句话目的 + 篇幅占比。
     3. **80% 预算分配**：明确点出 1-3 个核心概念吃掉 80%；其他章节为何属于 20%（对照用户背景说明"读者已熟悉"）。
     4. **交互模块清单**：每个模块要揭示的具体洞见。
   - 等用户口头确认或修订后再进第 4 步。

4. **生成 HTML**
   - 输出文件名 = PDF 文件名替换 `.pdf` → `.html`，与 PDF 同级。
   - 用下方"HTML 骨架"起步。
   - 写作时遵循下面的**写作原则**与**硬约束**。
   - 中间笔记、外部引用资料如需保留，写进 `<folder>/_drafts/`。

## 写作原则

- **第一性原理**：从问题出发——先讲 naive solution → 它为什么失败 → key insight 救场 → 具体设计。**不要**从 "paper 提出 X 方法" 倒着讲。
- **80% 给核心**：篇幅是预算。1-3 个核心 insight 吃掉 80%；其余压缩为一句话或脚注。
- **因材施教**：读者是 CS PhD、视觉 DL 8 年（详见 `AGENTS.md`）。标准 backprop / Adam / ResNet / 普通 attention 这类**一笔带过或省略**；篇幅给真正新的部分。
- **费曼 / karpathy 风格**：举例驱动、预期-验证、揭示而非陈述。每个核心论断后跟"如果 X 真的成立，应该看到 Y"。
- **交互必须揭示洞见**：每个交互模块开头一行写"此模块要揭示：…"，并附预期观察 + 印证的 paper 章节。废交互（输入框 → 显示数字）禁止。

## 硬约束

- **单 HTML 文件**：所有 CSS/JS 内联或 CDN，**禁止**引用项目根、`_lib/`、本地资源。双击即用。
- **同名同级**：HTML 与 PDF 在同一文件夹，只替换扩展名。
- **数学**：KaTeX（CDN，auto-render）。
- **代码**：Prism 或 highlight.js（CDN）。
- **样式**：Tailwind CDN 或手写 CSS 都行；**禁 Bootstrap**。
- **禁构建步骤**：不要 npm / vite / webpack。
- **不读其他主题文件夹**：严格隔离。
- **联网自由**：可任意查外部资料；HTML 中 paper 原文 vs 外部解释**显式区分**（脚注、侧栏、`<aside>` 等稳定标记）。
- **不懂的处理**：先联网查；查不到也要写下去，但该位置**显式标注**"⚠ 此处未充分消化：[原因]"。**不要打断用户问问题**。
- **同名 HTML 已存在**：**直接覆盖**（同一篇 paper 重学即是想替换）；`_drafts/` 不动。

## HTML 骨架

每次从此骨架起步，按需扩展。CSS class 语义已统一：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><!-- paper 主标题 --></title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'\\[',right:'\\]',display:true},
    {left:'$',right:'$',display:false},
    {left:'\\(',right:'\\)',display:false}]})"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.css">
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  :root { --max-w: 760px; }
  body { font-family: ui-sans-serif, system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
  main { max-width: var(--max-w); margin: 0 auto; padding: 3rem 1.25rem; line-height: 1.75; }
  code, pre { font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; }
  .insight     { border-left: 3px solid #6366f1; padding: .5rem .9rem; background: #eef2ff; }
  .interactive { border: 1px dashed #94a3b8; padding: 1rem; border-radius: .5rem; margin: 1.25rem 0; }
  .uncertain   { border-left: 3px solid #d97706; padding: .5rem .9rem; background: #fef3c7; }
  aside.external { font-size: .9em; color: #475569; border-left: 2px solid #94a3b8; padding-left: .75rem; }
</style>
</head>
<body class="bg-slate-50 text-slate-900">
<main><!-- 内容 --></main>
</body>
</html>
```

CSS class 用法：
- `.insight` — 核心 insight 横幅。
- `.interactive` — 交互模块容器；首行必须是"此模块要揭示：…"。
- `.uncertain` — 未充分消化的位置。
- `aside.external` — 外部引用 / 联网补充内容。

## Gotchas

- 多 PDF 时**问用户**选哪个；不要静默选第一个。
- 不要默默留 TODO 占位章节；要么写完整，要么用 `.uncertain` 显式标注。
- 外部内容**必须**用 `aside.external` 或等价方式包起来——用户要一眼分清"paper 原文 vs agent 引入"。
- 引入的所有 CDN URL 都用稳定版本号，不要用 `@latest`。

## See also

- 项目根 `AGENTS.md` — 用户背景、项目级硬约束、触发协议。
