---
name: learn-paper
description: 把指定主题文件夹里的 paper PDF 转为同目录、单文件、自含 CDN 的**editorial-grade** 交互式学习 HTML：暖纸面 + 衬线正文 + mono 小标签 + 章节级色码的杂志感长读，按"begin with why"开篇，第一性原理拆解，80% 篇幅给核心 insight，配色码变量、多语义 callout、lab block、timeline。Use when the user runs `/learn-paper <folder>` or asks to "学习 / 讲解 / 拆解 X 文件夹里的 paper" inside the `learn_with_agent` project.
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
     1. **Begin-with-why 段**：这篇 paper 出现之前领域被什么问题卡住？最显然的做法是什么？为什么不行？这一段是 chapter 0，不是 chapter 1。
     2. **One-paragraph thesis**：这篇 paper 的关键 insight，与已有方案的根本差异。
     3. **章节大纲**：每章标题（含一个 `<strong>` 重点词）+ 一句话 italic hook + 篇幅占比。
     4. **80% 预算分配**：明确点出 1–3 个核心概念吃掉 80%；其他章节为何属于 20%（"读者已熟悉"——见 AGENTS.md 的背景声明）。
     5. **Color-code 计划**：列出 paper 反复出现的关键变量 / 关键概念（如 score function、加噪点 vs 原点、column vectors、target b…），给每个分配一个固定颜色（红/蓝/绿/紫/橙），后面公式、SVG、段落 inline 都复用同色。
     6. **Per-topic accent**（可选）：如果 paper 有 2–3 个并列的核心概念（PSNR/SSIM/LPIPS 类的），给每个 section 一个 accent 色条。
     7. **交互模块清单**：每个 lab block 要揭示的具体洞见 + 用的可视化形式 + 对应 paper 章节。
   - 等用户口头确认或修订后再进第 4 步。

4. **生成 HTML**
   - 输出文件名 = PDF 文件名替换 `.pdf` → `.html`，与 PDF 同级。
   - 用下方"HTML 骨架"起步。
   - 写作时遵循下面的**写作原则**与**硬约束**。
   - 中间笔记、外部引用资料如需保留，写进 `<folder>/_drafts/`。

## 写作原则

> 不是写论文综述，是**写一篇编辑级长读**——读者翻开页面就该觉得"有人替我把这件事讲明白了"。

### 1 · Begin with why（chapter 0 的硬要求）

读者打开页面看到的**第一章**绝对不是"本文方法概览"。它必须是**领域级困境**：

- 这篇 paper 出现之前，所有人都被什么问题卡住？
- 最显然的做法是什么？为什么不行？（用 `.danger` 卡片明确标出"致命问题"）
- 给一个具体场景／物理直觉（"假设你有一万张猫的图片"）把问题翻译成数学。
- 列一张"前辈如何各自绕开"的对比表（VAE / GAN / Flow / 这篇）。
- 收尾一句 Feynman 级元洞察："如果不能直接解决，先问我真正需要的是什么——也许我需要的比我以为的少得多。"

第二章再进入 paper 真正的 key insight。Diffusion 范式：`ch0 根本困境 → ch1 天才洞察 (Score Function) → ch2 怎么用 (Langevin) → ch3 怎么学 (Score Matching) → …`。

**反例**："Section 1 介绍 / Section 2 相关工作 / Section 3 方法"——直接 ban。

### 2 · 第一性原理：naive → 致命问题 → 救场 insight → 设计

每个核心概念按这个序列展开：先讲"任何聪明人都能想到的做法"，让读者自己感到"这思路应该可以"，**然后**揭穿它的隐藏漏洞，再让 paper 的 insight 自然涌现。**禁止**从 "paper 提出 X" 倒着讲。

### 3 · 80% 给核心，是预算不是建议

1–3 个核心 insight 吃掉 80% 篇幅；其他全部压成一句话或脚注。如果一篇 paper 有 5 个 contribution，挑最深的 1–3 个深讲，剩下两句带过。**不要写完整 ablation table**。

### 4 · 因材施教（读者档案见 AGENTS.md）

读者是 CS PhD、视觉 DL 8 年。**一笔带过或省略**的内容：

- 标准 backprop / Adam / SGD / Layer Norm
- 普通 self-attention / multi-head attention
- ResNet / U-Net / ViT 的基本结构
- 一般的 cross-entropy / KL divergence

**篇幅给真正新的部分**：paper 的 key insight、新机制、为什么只有这种设计能 work。

### 5 · 费曼 / Karpathy 风格

- 举例驱动：先给具体例子，再抽象。
- 预期-验证："如果 X 真的成立，应该看到 Y——然后 paper 的实验确实显示 Y。"
- 揭示而非陈述：不是"X 等于 Y"，而是"为什么 X 必须等于 Y——因为 Z"。
- 物理直觉锚点：score function = "上山方向"，加噪 = "把山岭抹平"，归一化常数 Z = "全空间的体积积分"。

### 6 · 语言自然流畅，**反论文腔**

- **禁用模板词**：本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得注意的是 / 显然地 / 与此同时 / 据此可知 / 由上可见。
- **节奏感**：长短句交替，允许短句、反问、比喻、口语化转折（"换句话说""问题来了""听起来很玄, 其实……""注意一个微妙的点"）。一段不要超过 5–6 行。密集推理段之间要给读者一口气。
- **直觉先于形式**：每个新术语第一次出现，先一句"它大致是 X"的直觉，再上定义 / 公式。
- **第一/第二人称**："我们""你会发现""试着想一下"比通篇被动语态更有人味。
- **不要凑词**：宁可一句话讲清，不要为了显得严谨堆三个从句。

### 7 · Color-coded variables（一处定义，全文复用）

凡是数学 / SVG / 段落里反复出现的关键变量／对象，**给每个一个固定颜色**：

```html
<span class="v-x">x</span>      <!-- 红 -->
<span class="v-y">y</span>      <!-- 蓝 -->
<span class="v-z">z</span>      <!-- 绿 -->
<span class="v-b">b</span>      <!-- 紫 (target) -->
```

公式里 `\(\textcolor{#dc2626}{x}\)`，SVG 里同色画箭头，段落 inline 同色 `<span>`——读者只需对一次色谱，之后所有公式 / 图都不再需要脑内翻译变量。

参考 MIT 18.06 的 vec-col1/2/3/b：column vectors 三色 + target 紫色，从 row picture 的折线 → column picture 的箭头 → matrix 形式 → n-dim 抽象，颜色一以贯之。

### 8 · 揭示式交互（不是控件 demo）

每个 lab block 第一行明写**「此 lab 揭示：…（对应 paper §X）」**。废交互（输入框 → 显示数字、纯滑条改色）一律禁止。常见有用形式：

- 向量场 / 流形可视化（点击放粒子，观察被 score 引导）
- 参数滑动 → 几何对象变化（两条直线相交点、planes 交线、奇异 vs 非奇异）
- 退火序列：从大噪声到小噪声逐帧播
- 多步算法的 step-dot 序列：上一步 / 下一步按钮 + 高亮当前步骤
- 多 method 切 tab：column method vs row method（同一计算两种视角）

### 9 · 网页感 = editorial-grade

成品要让人觉得这是一篇**杂志长读**或**专业期刊新版教材**——不是 Markdown 渲染：

- **暖色纸面**（不是 `#ffffff`），如 `#fafaf9` / `#f5f0e8` / `#fdfcf9`；深色 hero 与浅色 body 形成对比。
- **衬线正文**（Iowan Old Style / Source Serif 4 / Georgia）+ **mono 小标签**（JetBrains Mono / Courier New 用于 eyebrow / label / 代码）。
- **章节级版式**：eyebrow `CH 03` → 大标题（含 `<strong>` 重点词）→ italic hook 一句话 → `.lead` 1.15rem 引导段 → 正文。
- **Callout 矩阵**至少 3 种以上语义色：`.insight`（蓝）/`.danger`（红）/`.success`（绿）/`.warning`（橙）/`.definition`（蓝浅）/`.feynman`（深底白字 + 大引号）。
- **Math box 三件套**：mono label（"能量模型 Energy-Based Model"）+ LaTeX + 普通话 math-note。
- **Per-topic accent**（paper 有 2–3 并列概念时）：每个 section / formula-card 用 `:before` 色条标识归属，颜色全文一致。
- **章末**用 `· · ·` editorial-divider，不要 `<hr>`。
- **不允许**：通篇 760px 居中段落 + 偶尔 `<pre>` 的 markdown 既视感。

## 硬约束

- **单 HTML 文件**：所有 CSS/JS 内联或 CDN，**禁止**引用项目根、`_lib/`、本地资源。双击即用。
- **同名同级**：HTML 与 PDF 在同一文件夹，只替换扩展名。
- **数学**：KaTeX（CDN，auto-render）。
- **代码**：Prism 或 highlight.js（CDN）。
- **样式**：Tailwind CDN 或手写 CSS 都行；**禁 Bootstrap**。
- **字体**：Google Fonts 加载衬线 body + mono；禁 system-ui-only 默认字体。
- **禁构建步骤**：不要 npm / vite / webpack。
- **不读其他主题文件夹**：严格隔离。
- **联网自由**：可任意查外部资料；HTML 中 paper 原文 vs 外部解释**显式区分**（`aside.external`）。
- **不懂的处理**：先联网查；查不到也要写下去，但该位置**显式标注** `<div class="uncertain">⚠ 此处未充分消化：[原因]</div>`。**不要打断用户问问题**。
- **同名 HTML 已存在**：**直接覆盖**（同一篇 paper 重学即是想替换）；`_drafts/` 不动。
- **CDN 版本**：所有 CDN URL 用稳定版本号，**不要 `@latest`**。

## 必备组件清单

每篇 HTML 至少包含下列组件，缺一项都算"文字堆叠"：

1. **Hero / 封面** — 深色或带渐变背景，paper 标题（含 `<em>` 副标题强化）+ 一句话 thesis + 元信息（作者、年份、会议、原 PDF 链接）+ 阅读时长估计 + eyebrow 标签如 "第一性原理 · Feynman 讲法"。
2. **顶部进度条** — `position:fixed; top:0; height:3px;`，随滚动条填充。
3. **导航**（二选一或同时）：
   - 左侧 sticky TOC 列表（学术风、章节多时用）
   - 右侧固定 nav-dot 列表（hover 出 chapter label，narrative 长读用）
4. **Chapter 模式** — 每章必须有 `.ch-num` + `.ch-title`（含 `<strong>` 重点词）+ `.ch-hook`（italic 一句话）+ 第一段用 `.lead`。
5. **Callout 矩阵** — 至少使用 3 种：`.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`。
6. **Math box 三件套** — `<div class="math-box"><div class="math-label">…</div>$$…$$<div class="math-note">…</div></div>`。
7. **Naive vs Insight 对比** — 两栏并排，左 naive，右 paper 解法；每篇至少 1 个。
8. **图示** — 至少 1–2 个 SVG / CSS / emoji 拼装的概念图。"图缺失"不允许。
9. **Lab block** — `.lab` 容器 + `.lab-title`（带 ⚗ 等小图标）+ 一行揭示句 + canvas + `.ctrl-row` + `.btn-row` + `.lab-note`。
10. **Timeline**（强烈推荐 paper 处于明确传承时） — 历史脉络（Hyvärinen 2005 → Vincent 2011 → Sohl-Dickstein 2015 → DDPM 2020 …）。
11. **Comparison table** — "model × 怎么绕开 × 代价" 这类对照。
12. **`aside.external`** — 联网补充的内容必须显式区分。
13. **Pull quote / `.feynman`** — 至少 1 段提炼的金句或 Feynman 风元洞察。
14. **Editorial divider** — `· · ·` 章末分隔。
15. **Footer** — 引用条目、参考资料链接、生成时间戳、`uncertain` 汇总。

## HTML 骨架

每次从此骨架起步，按需扩展。骨架已含 hero + 进度条 + 右侧 nav-dot + chapter 模式 + 全套 callout + math-box + lab block + timeline + footer。**不要再退化成 760px 单柱 markdown**。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><!-- paper 主标题 --></title>

<!-- Fonts: 衬线 body + mono 小标签；按需可加 display 衬线 -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},
    {left:'\\[',right:'\\]',display:true},
    {left:'$',right:'$',display:false},
    {left:'\\(',right:'\\)',display:false}]})"></script>

<!-- Prism (代码高亮) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.css">
<script defer src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>

<style>
  :root {
    /* —— 暖纸面 + 衬线 body + mono 小标签 —— */
    --paper:    #f8f5ee;          /* 主背景，暖纸 */
    --paper-2:  #efeae0;          /* lab / aside 副背景 */
    --surface:  #ffffff;          /* 卡片白纸 */
    --ink:      #1a1a1a;          /* 正文墨色 */
    --ink-soft: #3f3a33;          /* 标题深褐 */
    --muted:    #8a8278;          /* 次级文字 */
    --border:   #d8d2c4;          /* 暖纸 border */
    --hairline: #e6e0d2;          /* 极淡分隔线 */

    /* —— 主 accent + per-topic 色 —— */
    --accent:    #1e5a8a;         /* 主蓝（核心 insight） */
    --c-insight: #1e5a8a;
    --c-danger:  #b03a2e;
    --c-success: #2d7a4f;
    --c-warning: #c47a18;
    --c-feynman: #2d2842;         /* feynman 深底 */

    /* —— color-coded variables（按需重命名为 paper 真实变量）—— */
    --v-x:  #c0392b;              /* 红 */
    --v-y:  #1e5a8a;              /* 蓝 */
    --v-z:  #2d7a4f;              /* 绿 */
    --v-b:  #6c3483;              /* 紫（target） */

    /* —— 字体 stack —— */
    --font-body:    'Source Serif 4', 'Iowan Old Style', Georgia, 'Times New Roman', serif;
    --font-display: 'Space Grotesk', 'Source Serif 4', Georgia, serif;
    --font-mono:    'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    --font-sans:    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

    --reading-w: 760px;           /* 章节正文最大宽 */
    --shell-w:   1180px;          /* 主壳最大宽（含右 rail） */
  }
  *,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--paper); color: var(--ink);
    font-family: var(--font-body); font-size: 17px; line-height: 1.78;
    -webkit-font-smoothing: antialiased;
  }
  code, pre, .mono { font-family: var(--font-mono); }

  /* —— 顶部进度条 —— */
  #progress { position: fixed; top: 0; left: 0; right: 0; height: 3px;
              background: rgba(0,0,0,0.06); z-index: 999; }
  #progress > div { height: 100%; width: 0; background: var(--accent); transition: width .1s; }

  /* —— Hero —— */
  .hero { background: linear-gradient(180deg,#1a1a2e 0%, #2d2842 100%);
          color: #e8e8f0; padding: 72px 24px 56px; text-align: center;
          border-bottom: 4px solid var(--accent); }
  .hero .eyebrow { font-family: var(--font-mono); font-size: .75rem;
                   letter-spacing: .15em; text-transform: uppercase;
                   color: #9999c0; margin-bottom: 12px; }
  .hero h1 { font-family: var(--font-display); font-size: clamp(2rem, 4vw, 3rem);
             font-weight: 600; line-height: 1.18; letter-spacing: -.01em; max-width: 800px; margin: 0 auto; }
  .hero h1 em { color: #aac4ff; font-style: normal; }
  .hero .thesis { color: #c8c2d8; font-size: 1.1rem; max-width: 60ch;
                  margin: 16px auto 0; font-style: italic; }
  .hero .meta { display: flex; gap: 18px; flex-wrap: wrap; justify-content: center;
                margin-top: 24px; font-family: var(--font-mono);
                font-size: .82rem; color: #8a8aaa; }
  .hero .meta a { color: #aac4ff; text-decoration: none; }
  .hero .meta a:hover { text-decoration: underline; }

  /* —— 右侧 nav-dot rail —— */
  #rail { position: fixed; right: 22px; top: 50%; transform: translateY(-50%);
          display: flex; flex-direction: column; gap: 10px; z-index: 100; }
  .dot { width: 11px; height: 11px; border-radius: 50%;
         background: var(--border); cursor: pointer; position: relative;
         transition: all .2s; border: 2px solid transparent; }
  .dot:hover, .dot.active { background: var(--accent); transform: scale(1.3); }
  .dot .lbl { position: absolute; right: 18px; top: 50%; transform: translateY(-50%);
              background: var(--ink-soft); color: #f8f5ee;
              padding: 4px 9px; border-radius: 3px; font-family: var(--font-mono);
              font-size: .72rem; white-space: nowrap; opacity: 0;
              pointer-events: none; transition: opacity .2s; }
  .dot:hover .lbl { opacity: 1; }
  @media (max-width: 900px) { #rail { display: none; } }

  /* —— Chapter —— */
  .chapter { max-width: var(--reading-w); margin: 0 auto;
             padding: 72px 28px 24px; scroll-margin-top: 24px;
             border-bottom: 1px solid var(--hairline); }
  .chapter:last-of-type { border-bottom: 0; }
  .ch-num { font-family: var(--font-mono); font-size: .76rem;
            letter-spacing: .14em; text-transform: uppercase;
            color: var(--muted); margin-bottom: 8px; }
  .ch-title { font-family: var(--font-display); font-size: 1.95rem;
              font-weight: 600; color: var(--ink-soft); line-height: 1.22;
              letter-spacing: -.005em; }
  .ch-title strong { color: var(--accent); font-weight: 700; }
  .ch-hook { font-style: italic; color: var(--muted);
             font-size: 1.08rem; margin: 8px 0 22px;
             padding-bottom: 18px; border-bottom: 2px solid var(--border); }
  .lead { font-size: 1.18rem; color: var(--ink-soft); margin-bottom: 20px; }
  .chapter p { margin-bottom: 18px; }

  /* —— Per-topic accent stripe（paper 有 2–3 并列概念时）—— */
  .topic-a:before, .topic-b:before, .topic-c:before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; border-radius: 2px;
  }
  .topic-a { position: relative; padding-left: 20px; }
  .topic-a:before { background: var(--c-insight); }
  .topic-b { position: relative; padding-left: 20px; }
  .topic-b:before { background: var(--c-success); }
  .topic-c { position: relative; padding-left: 20px; }
  .topic-c:before { background: var(--c-danger); }

  /* —— Callout 矩阵 —— */
  .insight, .danger, .success, .warning, .definition {
    border-left: 4px solid; background: #fff;
    padding: 16px 20px; margin: 22px 0; border-radius: 0 4px 4px 0;
  }
  .insight    { border-color: var(--c-insight); background: #eef3fb; }
  .danger     { border-color: var(--c-danger);  background: #fdf0ee; }
  .success    { border-color: var(--c-success); background: #eef8f0; }
  .warning    { border-color: var(--c-warning); background: #fdf5ee; }
  .definition { border-color: var(--c-insight); background: #eef3fb; }
  .insight .label, .danger .label, .success .label,
  .warning .label, .definition .label {
    font-family: var(--font-mono); font-size: .72rem;
    letter-spacing: .1em; text-transform: uppercase;
    font-weight: 700; margin-bottom: 6px; display: block;
  }
  .insight    .label { color: var(--c-insight); }
  .danger     .label { color: var(--c-danger); }
  .success    .label { color: var(--c-success); }
  .warning    .label { color: var(--c-warning); }
  .definition .label { color: var(--c-insight); }

  /* —— Feynman 块（深底 + 大引号）—— */
  .feynman { background: var(--c-feynman); color: #e8e8f0;
             padding: 22px 26px; margin: 28px 0; border-radius: 4px;
             position: relative; }
  .feynman::before { content: '"'; position: absolute; top: -10px; left: 18px;
                     font-size: 4rem; color: #4a4a7a; font-family: Georgia, serif;
                     line-height: 1; }
  .feynman p { font-style: italic; color: #d8d8f0; margin-bottom: 8px; }
  .feynman .attribution { color: #9090b0; font-size: .82rem; font-style: normal;
                          font-family: var(--font-mono); }

  /* —— Math box 三件套 —— */
  .math-box { background: #fef9e7; border: 1px solid var(--border);
              border-radius: 4px; padding: 18px 22px; margin: 20px 0;
              overflow-x: auto; }
  .math-box .math-label { font-family: var(--font-mono); font-size: .72rem;
                          letter-spacing: .1em; text-transform: uppercase;
                          color: var(--muted); margin-bottom: 10px; }
  .math-box .math-note  { font-size: .9rem; color: var(--muted);
                          margin-top: 10px; font-style: italic; }

  /* —— Naive vs Insight 对比 —— */
  .compare { display: grid; grid-template-columns: 1fr 1fr;
             gap: 16px; margin: 24px 0; }
  @media (max-width: 700px) { .compare { grid-template-columns: 1fr; } }
  .compare > div { border: 1px solid var(--border); background: var(--surface);
                   border-radius: 6px; padding: 16px 18px; }
  .compare .naive       { border-top: 3px solid var(--muted); }
  .compare .insight-card{ border-top: 3px solid var(--accent); }
  .compare .label       { font-family: var(--font-mono); font-size: .72rem;
                          letter-spacing: .1em; text-transform: uppercase;
                          color: var(--muted); margin-bottom: 6px; display: block; }

  /* —— Lab block —— */
  .lab { background: var(--paper-2); border: 1px solid var(--border);
         border-radius: 6px; padding: 22px; margin: 28px 0; }
  .lab-title { font-family: var(--font-mono); font-size: .8rem;
               letter-spacing: .1em; text-transform: uppercase;
               color: var(--ink-soft); margin-bottom: 8px;
               display: flex; align-items: center; gap: 8px; }
  .lab-reveal { font-size: .92rem; color: var(--muted);
                margin-bottom: 14px; font-style: italic; }
  .lab canvas, .lab svg { display: block; margin: 0 auto;
                          max-width: 100%; border-radius: 4px;
                          background: #fff; }
  .ctrl-row { display: flex; align-items: center; gap: 14px;
              margin-top: 14px; flex-wrap: wrap;
              font-family: var(--font-mono); font-size: .85rem; }
  .ctrl-row label { color: var(--muted); min-width: 70px; }
  .ctrl-row input[type=range] { flex: 1; min-width: 120px; accent-color: var(--accent); }
  .ctrl-val { color: var(--accent); min-width: 48px; text-align: right; }
  .btn-row { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
  .btn { padding: 6px 14px; background: var(--ink-soft); color: #f8f5ee;
         border: none; border-radius: 3px; cursor: pointer; font-size: .85rem;
         font-family: var(--font-mono); transition: opacity .15s; }
  .btn:hover { opacity: .8; }
  .btn.outline { background: transparent; border: 1px solid var(--ink-soft);
                 color: var(--ink-soft); }
  .lab-note { font-size: .82rem; color: var(--muted); margin-top: 12px;
              font-style: italic; }
  .step-dots { display: flex; gap: 6px; margin: 12px 0; align-items: center; }
  .step-dots .d { width: 9px; height: 9px; border-radius: 50%;
                  background: var(--border); transition: background .25s; }
  .step-dots .d.active { background: var(--accent); }
  .step-dots .d.done   { background: var(--c-success); }

  /* —— Timeline —— */
  .timeline { position: relative; padding-left: 28px; margin: 24px 0; }
  .timeline::before { content: ''; position: absolute; left: 7px; top: 8px;
                      bottom: 8px; width: 2px; background: var(--border); }
  .tl-item { position: relative; margin-bottom: 22px; }
  .tl-dot { position: absolute; left: -24px; top: 6px;
            width: 12px; height: 12px; border-radius: 50%;
            background: var(--accent); border: 2px solid var(--paper);
            box-shadow: 0 0 0 2px var(--accent); }
  .tl-year { font-family: var(--font-mono); font-size: .78rem;
             color: var(--accent); font-weight: 700; margin-bottom: 2px; }
  .tl-title { font-weight: 600; margin-bottom: 2px; color: var(--ink-soft); }
  .tl-desc  { color: var(--muted); font-size: .92rem; }

  /* —— Pull quote —— */
  .pull-quote { font-family: var(--font-display); font-size: 1.32rem;
                line-height: 1.48; color: var(--ink-soft);
                border-left: 3px solid var(--ink-soft);
                padding: 6px 0 6px 18px; margin: 32px 0;
                font-style: italic; }

  /* —— Comparison table —— */
  table { width: 100%; border-collapse: collapse;
          margin: 22px 0; font-size: .92rem; }
  th { background: var(--ink-soft); color: #f8f5ee;
       padding: 10px 14px; text-align: left;
       font-weight: 500; font-family: var(--font-mono);
       font-size: .78rem; letter-spacing: .05em; }
  td { padding: 10px 14px; border-bottom: 1px solid var(--border);
       vertical-align: top; }
  tr:hover td { background: var(--paper-2); }

  /* —— External (agent 联网补充) —— */
  aside.external { display: block; background: #f1ede1;
                   border-left: 3px solid var(--muted);
                   padding: 12px 16px; margin: 18px 0;
                   border-radius: 0 4px 4px 0;
                   font-size: .92em; color: var(--ink-soft); }
  aside.external::before { content: "外部补充 · agent"; display: block;
                           font-family: var(--font-mono); font-size: .68rem;
                           letter-spacing: .12em; color: var(--muted);
                           margin-bottom: 6px; }

  /* —— Uncertain（未充分消化）—— */
  .uncertain { border-left: 4px solid #d97706; background: #fef3c7;
               padding: 12px 16px; border-radius: 0 4px 4px 0;
               margin: 16px 0; }

  /* —— Color-coded variables（vec 等）—— */
  .v-x { color: var(--v-x); font-weight: 600; }
  .v-y { color: var(--v-y); font-weight: 600; }
  .v-z { color: var(--v-z); font-weight: 600; }
  .v-b { color: var(--v-b); font-weight: 600; }

  /* —— Editorial divider —— */
  .ch-end { text-align: center; margin: 48px 0 12px;
            color: var(--border); font-size: 1.2rem;
            letter-spacing: .5em; }

  /* —— Code block 圆角 + 暖光 —— */
  pre[class*="language-"] { border-radius: 6px; padding: 14px 18px !important;
                            font-size: .88rem; }

  /* —— Footer —— */
  footer.page-foot { background: var(--ink-soft); color: #c8c2b8;
                     padding: 32px 24px; text-align: center;
                     font-family: var(--font-mono); font-size: .82rem;
                     line-height: 1.6; }
  footer.page-foot a { color: #e8d8b8; text-decoration: none; }

  @media (max-width: 700px) {
    body { font-size: 16px; }
    .chapter { padding: 48px 18px 18px; }
    .hero h1 { font-size: 1.7rem; }
    .hero { padding: 48px 16px 36px; }
  }
</style>
</head>
<body>

<div id="progress"><div></div></div>

<!-- 右侧 nav-dot rail -->
<nav id="rail" aria-label="章节导航">
  <div class="dot active" data-target="ch0"><span class="lbl">困境</span></div>
  <div class="dot" data-target="ch1"><span class="lbl">关键 insight</span></div>
  <div class="dot" data-target="ch2"><span class="lbl">怎么训</span></div>
  <!-- 按需增加 -->
</nav>

<!-- Hero -->
<header class="hero">
  <div class="eyebrow">Paper · 第一性原理 · Karpathy 风格</div>
  <h1><!-- paper 主标题 --><br><em><!-- 一句话副 --></em></h1>
  <p class="thesis"><!-- 一句话讲清这篇 paper 解决什么、关键 insight 是什么 --></p>
  <div class="meta">
    <span><!-- 作者 · 年份 · 会议 --></span>
    <span>预计阅读 ~XX 分钟</span>
    <a href="./<!-- 同名 PDF -->">原 PDF</a>
  </div>
</header>

<!-- ═══ Chapter 0 — 根本困境（begin with why）═══ -->
<section class="chapter" id="ch0">
  <div class="ch-num">Chapter 0</div>
  <h2 class="ch-title">领域级<strong>根本困境</strong></h2>
  <p class="ch-hook">在理解这篇 paper 之前，我们必须先理解它在解决什么问题。</p>

  <p class="lead"><!-- 具体场景：假设你有 X，你想做 Y，这意味着数学上需要 Z --></p>
  <p><!-- 把 Y 翻译成数学；引入主要变量并第一次给颜色：<span class="v-x">x</span> 等 --></p>

  <div class="insight">
    <span class="label">核心问题</span>
    <p><!-- 用一句话说清楚整个领域被卡在哪 --></p>
  </div>

  <p>最自然的想法：<!-- naive idea --></p>

  <div class="math-box">
    <div class="math-label"><!-- e.g. 能量模型 Energy-Based Model --></div>
    \[ <!-- naive 公式 --> \]
    <div class="math-note"><!-- 普通话解释 --></div>
  </div>

  <div class="danger">
    <span class="label">致命问题</span>
    <p><!-- naive 为什么 dead-on-arrival --></p>
  </div>

  <table>
    <tr><th>模型</th><th>如何绕开</th><th>代价</th></tr>
    <tr><td>VAE</td><td>用 ELBO 近似下界</td><td>样本质量受限</td></tr>
    <tr><td>GAN</td><td>不建模 p(x)，用判别器</td><td>训练不稳定</td></tr>
    <tr><td><strong>这篇 paper</strong></td><td><strong>…</strong></td><td><strong>…</strong></td></tr>
  </table>

  <div class="feynman">
    <p>如果你不能直接解决一个问题，先问：我真正需要的是什么？也许我需要的比我以为的少得多。</p>
    <div class="attribution">— Feynman 式思维</div>
  </div>

  <div class="ch-end">· · ·</div>
</section>

<!-- ═══ Chapter 1 — Key Insight ═══ -->
<section class="chapter" id="ch1">
  <div class="ch-num">Chapter 1</div>
  <h2 class="ch-title">天才洞察：<strong><!-- key concept --></strong></h2>
  <p class="ch-hook"><!-- italic hook 一句话 --></p>

  <p class="lead"><!-- 物理直觉先行：站在山上想到山顶 --></p>
  <p><!-- 把直觉翻译成数学，引入新符号 --></p>

  <div class="math-box">
    <div class="math-label"><!-- e.g. Score Function --></div>
    \[ s(x) = \nabla_x \log p(x) \]
    <div class="math-note"><!-- 这是 log 概率密度对 x 的梯度，每点指向"概率上山"方向 --></div>
  </div>

  <div class="success">
    <span class="label">关键突破</span>
    <p><!-- 为什么这个 insight 一下就把困境化解了 --></p>
  </div>

  <div class="lab">
    <div class="lab-title">⚗ <!-- lab 名 --></div>
    <p class="lab-reveal">此 lab 揭示：<!-- 具体洞见 --> · 对应 paper §X</p>
    <canvas id="canvas-1" width="760" height="320"></canvas>
    <div class="ctrl-row">
      <label>参数 σ</label>
      <input type="range" id="r1" min="0" max="1" step=".01" value=".5">
      <span class="ctrl-val" id="r1v">0.50</span>
    </div>
    <div class="btn-row">
      <button class="btn">运行</button>
      <button class="btn outline">重置</button>
    </div>
    <div class="lab-note"><!-- 怎么操作 + 注意观察什么 --></div>
  </div>

  <div class="ch-end">· · ·</div>
</section>

<!-- ═══ Chapter N — Timeline（如果 paper 在传承中）═══ -->
<section class="chapter" id="chN">
  <div class="ch-num">Chapter N</div>
  <h2 class="ch-title">这条路是怎么走过来的：<strong>历史脉络</strong></h2>
  <p class="ch-hook">这篇 paper 不是凭空冒出来的。</p>

  <div class="timeline">
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2005 · Hyvärinen</div>
      <div class="tl-title">Score Matching</div>
      <div class="tl-desc">证明可以不用 Z 来学 score function，但计算代价高</div>
    </div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-year">2011 · Vincent</div>
      <div class="tl-title">Denoising Score Matching</div>
      <div class="tl-desc">去噪 = 学 score，计算高效</div>
    </div>
    <!-- … -->
  </div>

  <div class="ch-end">· · ·</div>
</section>

<footer class="page-foot">
  <div>引用：<!-- BibTeX 行内 --></div>
  <div>生成 <!-- ISO 时间 --> · 由 agent 基于原 PDF + 联网补充整理</div>
</footer>

<script>
  /* —— 进度条 —— */
  const prog = document.querySelector('#progress > div');
  window.addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = (h.scrollTop) / (h.scrollHeight - h.clientHeight);
    prog.style.width = (p * 100) + '%';
  }, { passive: true });

  /* —— 右 rail 当前章节高亮 —— */
  const dots = document.querySelectorAll('#rail .dot');
  const sections = [...document.querySelectorAll('section.chapter')];
  dots.forEach(d => d.addEventListener('click', () => {
    const t = document.getElementById(d.dataset.target);
    if (t) t.scrollIntoView({ behavior: 'smooth' });
  }));
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        dots.forEach(d => d.classList.toggle('active', d.dataset.target === e.target.id));
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach(s => io.observe(s));
</script>

</body>
</html>
```

### CSS class 用途速查

| Class | 用途 | 备注 |
|---|---|---|
| `.hero` | 顶部封面 | 深底 + display 字 + eyebrow + thesis + meta |
| `#progress` | 顶部 3px 进度条 | fixed，随滚动 |
| `#rail .dot` | 右侧 nav-dot rail | hover 出 chapter label |
| `.chapter` `.ch-num` `.ch-title` `.ch-hook` `.lead` | 标准章节模式 | 每章必备 4 件套 |
| `.insight` `.danger` `.success` `.warning` `.definition` | 5 种语义 callout | 内部 `<span class="label">` 写小标 |
| `.feynman` | 深底 Feynman 元洞察块 | 大引号字符 + attribution |
| `.math-box` `.math-label` `.math-note` | 数学三件套 | mono label + LaTeX + 普通话注 |
| `.compare > .naive` `.compare > .insight-card` | naive vs paper 解法对比 | 两栏并排 |
| `.lab` `.lab-title` `.lab-reveal` `.ctrl-row` `.btn-row` `.lab-note` | 完整交互 lab | 揭示句必写 |
| `.step-dots` `.d.active/.done` | 多步算法的状态指示 | 给序列动画用 |
| `.timeline` `.tl-item` `.tl-dot` `.tl-year` `.tl-title` `.tl-desc` | 历史脉络 | 传承谱系强烈推荐 |
| `.pull-quote` | 段中金句 | display 字 + 左竖线 |
| `aside.external` | 联网外部补充 | 自带 "外部补充 · agent" eyebrow |
| `.uncertain` | 未充分消化标记 | `⚠` 开头 |
| `.v-x` `.v-y` `.v-z` `.v-b` | color-coded variables | 公式/段落/SVG 共享 |
| `.ch-end` `· · ·` | 章末 editorial divider | 不要 `<hr>` |
| `.topic-a/b/c` | per-topic accent stripe | 多概念并列 paper 用 |

## 自审清单（写完后逐条对，缺一项就回去补）

写作 / 内容：
- [ ] **Chapter 0 是 "begin with why"**：领域困境 + naive + 致命问题 + 前辈对比表 + Feynman 元洞察。**不是**"本文方法概览"。
- [ ] 每章有 `ch-num` + `ch-title`（含 `<strong>` 重点词）+ `ch-hook`（italic 一句话）+ `.lead` 引导段。
- [ ] 论文腔词全清：通读一遍把"本文 / 综上 / 基于此 / 不失一般性 / 值得注意的是 / 显然地"全部替换或删掉。
- [ ] 段落不超过 5–6 行；密集推理段之间有口气（短句 / 反问 / 比喻）。
- [ ] 每个新术语第一次出现给一句直觉锚点，再上定义/公式。

视觉 / 组件：
- [ ] 至少使用 **3 种** `.insight` / `.danger` / `.success` / `.warning` / `.definition` / `.feynman`（不能全篇只有 `.insight`）。
- [ ] 至少 **1 个** Math box 三件套（label + LaTeX + math-note）。
- [ ] 至少 **1 个** Naive vs Insight `.compare` 对比卡。
- [ ] 至少 **1 个** Lab block，第一行写 `class="lab-reveal"` 揭示句。
- [ ] 至少 **1 个** SVG / canvas 图示（不允许"图缺失"）。
- [ ] 如果 paper 在明确传承中（有清晰前辈），加 `.timeline`。
- [ ] 关键变量有 color-code，公式 / SVG / 段落 inline 同色复用。
- [ ] 暖纸面背景（不是 `#ffffff`），衬线正文 + mono 小标签。
- [ ] 章末用 `· · ·`，不要 `<hr>`。
- [ ] 顶部进度条 + 右侧 nav-dot rail 至少有一个能用。

技术：
- [ ] 单 HTML 文件、所有 CDN URL 用稳定版本号、无本地资源引用。
- [ ] 每个 `<section class="chapter">` 有 id，rail dot `data-target` 对得上，IntersectionObserver 真高亮当前章节。
- [ ] 联网补充内容包在 `aside.external` 里。
- [ ] 未充分消化处用 `<div class="uncertain">⚠ …</div>` 显式标注，没有静默 TODO。

## Gotchas

- **多 PDF 时问用户**选哪个；不要静默选第一个。
- **Mac 字体降级**：`Source Serif 4` 偶尔加载失败时正文会回落到 Iowan Old Style → Georgia → Times New Roman；`JetBrains Mono` 失败时回落到 Fira Code → Courier New。CSS stack 已经写好，不要省略 fallback。
- **KaTeX 与 color-coded variable 同时使用**：在 LaTeX 内用 `\textcolor{#c0392b}{x}` 直接给颜色（KaTeX 支持）；在普通段落里用 `<span class="v-x">x</span>`。两边色谱必须一致。
- **`@latest` 禁用**：所有 CDN 都钉死版本号（`katex@0.16.11`、`prismjs@1.29.0`），跨月加载稳定。
- **不要默默留 TODO 占位章节**：要么写完整，要么用 `.uncertain` 显式标注。
- **写完先自审"文字堆叠"**：如果整页只有 `<p>` + 偶尔 `<pre>`，没有 hero / nav / 章节模式 / 多种 callout / 任何 SVG / lab block——立刻回去补，否则不算交付。
- **不要把 callout 用成段落 wrapper**：callout 是为了**强调一句话**或**一段命题**，不是普通正文的容器。`<div class="insight">` 里塞 5 段就是滥用。
- **TOC / rail 必须真有效**：每个 `<section>` 必须有 id；rail dot 的 `data-target` 必须真能跳；IntersectionObserver 必须真高亮。骨架里的 JS 已经给好，不要漏。
- **Per-topic accent 不要乱用**：只有 paper 真有 2–3 个并列核心概念（PSNR/SSIM/LPIPS、Score/Langevin/Denoising 这种）时才用。其他情况单一 `--accent` 就够。

## See also

- 项目根 `AGENTS.md` — 用户背景、项目级硬约束、触发协议。
- 参考样本（视觉与讲解风格的 ground truth）：
  - `~/Documents/manus_out/3dgs/3DGS_Metrics_Interactive.html` — editorial / per-topic accent / oklch 配色
  - `~/Documents/manus_out/3dgs/Depth Anything 3 交互网页 (1).html` — 衬线 + Space Grotesk 现代感
  - `~/Documents/manus_out/other_reading/Diffusion Concepts Interactive Webpage (1).html` — begin-with-why 范式 + 多语义 callout + timeline + 右 rail
  - `~/Documents/manus_out/other_reading/mit1806_lecture1.html` — 干净排版 + 演示动画 + color-coded variables + tab 切换方法
