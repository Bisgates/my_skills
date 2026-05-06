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
- **语言自然流畅，不要论文腔**：像在跟一个聪明的同事讲清楚，不是在写 abstract。
  - 禁用模板：避免"本文提出 / 综上所述 / 基于以上分析 / 不失一般性 / 值得注意的是"这类论文/机翻味连接词。
  - 节奏感：长短句交替，允许短句、反问、比喻、口语化转折（"换句话说""问题来了""听起来很玄, 其实……"）。一段不要超过 5–6 行；密集推理段落之间要给读者一口气。
  - 直觉先于形式：每个新术语第一次出现，先给一句"它大致是 X"的直觉锚点，再上定义/公式。
  - 第一/第二人称可用："我们""你会发现""试着想一下"比通篇被动语态更有人味。
  - 不要凑词：宁可一句话讲清，不要为了显得严谨堆三个从句。
- **网页感 ≠ 文字堆叠**：成品要像一篇精心设计的长读文章 / 产品页，不是把 Markdown 渲染出来。
  - 必须有清晰视觉层级：hero/封面、目录（侧栏 sticky 或顶部锚点）、章节标题带编号或图标、章节之间有色块/分隔/留白变化。
  - 必须有组件化区块：核心 insight 卡片、naive vs key-insight 并排对比、引文块（pull quote）、图示（SVG / CSS 画 / emoji 拼装均可）、术语小词条、脚注/侧注。
  - 严禁全页只是 760px 居中段落 + 偶尔 fenced code block 的 markdown 既视感。允许 full-bleed 段、双栏布局、卡片网格等版式变化。
  - 留白与排版细节：行高 ≥1.7、段间距、列表 marker 美化、代码块圆角 + 标题条、图注/caption 样式、深色 hero、浅色 body 的对比都要考虑到。
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

## 页面结构建议（最低组件清单）

每篇 HTML 至少包含下列组件，缺一项都算"文字堆叠"：

1. **Hero / 封面区** — 深色或带渐变背景，paper 标题 + 一句话 thesis + 元信息（作者、年份、会议、原 PDF 链接）+ 阅读时长估计。
2. **TOC** — 桌面端 sticky 侧栏（左 200–240px），移动端折叠为顶部 details；当前章节高亮。
3. **核心 insight 卡片** — `.insight` 横幅块，1–3 个，是全篇的"主菜"。
4. **Naive vs Insight 对比块** — 两栏并排（grid），左"显然但错的做法"右"paper 真正怎么做"。
5. **图示** — 至少 1–2 个 SVG 或 CSS/emoji 拼装的概念图；不要"图缺失"。
6. **代码块** — 带文件名/语言条的 Prism 代码块；伪代码也用代码块，不要塞进段落。
7. **交互模块** — `.interactive`，每个开头标"此模块要揭示：…"。
8. **外部引用区** — `aside.external` 或专用 callout，把 agent 联网补的内容显式区分。
9. **页脚** — 引用条目、参考资料链接、生成时间戳、`uncertain` 汇总。

## HTML 骨架

每次从此骨架起步，按需扩展。骨架已经给出 hero + TOC + 主内容区的基本版式，**不要再退化成 760px 单柱**。

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
  :root {
    --reading-w: 68ch;        /* 正文阅读宽度 */
    --shell-w: 1180px;        /* 主壳最大宽度，含 TOC */
    --ink: #0f172a;
    --muted: #475569;
    --bg: #f8fafc;
    --accent: #6366f1;
    --accent-soft: #eef2ff;
  }
  html { scroll-behavior: smooth; }
  body {
    font-family: ui-sans-serif, system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    color: var(--ink); background: var(--bg); line-height: 1.75;
  }
  code, pre { font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; }

  /* hero */
  .hero {
    background: radial-gradient(1200px 500px at 20% -10%, #6366f155, transparent 60%),
                linear-gradient(180deg, #0b1220 0%, #111827 100%);
    color: #e2e8f0;
    padding: 4.5rem 1.25rem 3rem;
  }
  .hero-inner { max-width: var(--shell-w); margin: 0 auto; }
  .hero h1 { font-size: clamp(2rem, 4vw, 3rem); line-height: 1.15; font-weight: 700; }
  .hero .thesis { font-size: 1.15rem; color: #cbd5e1; max-width: 60ch; margin-top: 1rem; }
  .hero .meta { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1.5rem; font-size: .9rem; color: #94a3b8; }

  /* shell: TOC + main */
  .shell { max-width: var(--shell-w); margin: 0 auto; padding: 2.5rem 1.25rem 5rem;
           display: grid; grid-template-columns: 220px 1fr; gap: 3rem; }
  @media (max-width: 900px) { .shell { grid-template-columns: 1fr; } .toc { position: static; } }
  .toc { position: sticky; top: 1rem; align-self: start; font-size: .92rem; color: var(--muted); }
  .toc a { display: block; padding: .25rem 0; color: var(--muted); text-decoration: none; }
  .toc a.active, .toc a:hover { color: var(--accent); }

  article { max-width: var(--reading-w); }
  article h2 { font-size: 1.6rem; margin-top: 2.75rem; margin-bottom: 1rem; font-weight: 700;
               border-bottom: 1px solid #e2e8f0; padding-bottom: .5rem; }
  article h3 { font-size: 1.2rem; margin-top: 1.75rem; font-weight: 600; }
  article p  { margin: 1rem 0; }

  /* component blocks */
  .insight     { border-left: 4px solid var(--accent); background: var(--accent-soft);
                 padding: 1rem 1.25rem; border-radius: 0 .5rem .5rem 0; margin: 1.5rem 0; }
  .insight .label { font-size: .75rem; letter-spacing: .1em; text-transform: uppercase;
                    color: var(--accent); font-weight: 700; }
  .compare     { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0; }
  @media (max-width: 700px) { .compare { grid-template-columns: 1fr; } }
  .compare > div { border: 1px solid #e2e8f0; border-radius: .75rem; padding: 1rem; background: #fff; }
  .compare .naive  { border-top: 3px solid #94a3b8; }
  .compare .insight-card { border-top: 3px solid var(--accent); }
  .interactive { border: 1px dashed #94a3b8; padding: 1.25rem; border-radius: .75rem;
                 background: #fff; margin: 1.5rem 0; }
  .interactive .reveal { font-size: .8rem; letter-spacing: .05em; text-transform: uppercase;
                         color: #475569; margin-bottom: .75rem; font-weight: 600; }
  .uncertain   { border-left: 4px solid #d97706; background: #fef3c7;
                 padding: .75rem 1rem; border-radius: 0 .5rem .5rem 0; }
  .pull-quote  { font-size: 1.25rem; line-height: 1.5; color: var(--ink);
                 border-left: 3px solid var(--ink); padding-left: 1rem; margin: 2rem 0;
                 font-style: italic; }
  aside.external { display: block; font-size: .92em; color: var(--muted);
                   border-left: 2px solid #94a3b8; background: #f1f5f9;
                   padding: .75rem 1rem; border-radius: 0 .5rem .5rem 0; margin: 1rem 0; }
  aside.external::before { content: "外部补充 · agent"; display: block;
                           font-size: .7rem; letter-spacing: .1em; text-transform: uppercase;
                           color: #64748b; margin-bottom: .25rem; }
  figure.diagram { background: #fff; border: 1px solid #e2e8f0; border-radius: .75rem;
                   padding: 1rem; margin: 1.5rem 0; }
  figure.diagram figcaption { font-size: .85rem; color: var(--muted); margin-top: .5rem; }

  pre[class*="language-"] { border-radius: .75rem; padding: 1rem 1.1rem !important;
                            font-size: .9rem; }

  footer.page-foot { max-width: var(--shell-w); margin: 0 auto;
                     padding: 2rem 1.25rem 4rem; color: var(--muted); font-size: .9rem;
                     border-top: 1px solid #e2e8f0; }
</style>
</head>
<body>

<header class="hero">
  <div class="hero-inner">
    <div style="font-size:.8rem;letter-spacing:.15em;text-transform:uppercase;color:#94a3b8">paper · 第一性原理拆解</div>
    <h1><!-- paper 主标题 --></h1>
    <p class="thesis"><!-- 一句话讲清这篇 paper 解决什么、关键 insight 是什么 --></p>
    <div class="meta">
      <span>作者 · …</span><span>年份 · …</span><span>会议 · …</span>
      <span>预计阅读 · ~XX 分钟</span>
      <a style="color:#a5b4fc" href="./<!-- 同名 PDF -->">原 PDF</a>
    </div>
  </div>
</header>

<div class="shell">
  <nav class="toc" aria-label="目录">
    <div style="font-weight:700;color:var(--ink);margin-bottom:.5rem">目录</div>
    <!-- a href="#sec-1" 等 -->
  </nav>

  <article>
    <!-- 章节示例：

    <section id="sec-1">
      <h2>1 · 问题是什么</h2>
      <p>……</p>
      <div class="compare">
        <div class="naive"><strong>显然的做法</strong><p>……</p></div>
        <div class="insight-card"><strong>paper 的做法</strong><p>……</p></div>
      </div>
    </section>

    <section id="sec-2">
      <h2>2 · 核心 insight</h2>
      <div class="insight">
        <div class="label">key insight</div>
        <p>……</p>
      </div>
      <figure class="diagram">
        <svg viewBox="0 0 600 200">…</svg>
        <figcaption>图 1 · ……</figcaption>
      </figure>
      <div class="interactive">
        <div class="reveal">此模块要揭示：……（对应 paper §X）</div>
        <!-- 控件 + 可视化 -->
      </div>
    </section>

    -->
  </article>
</div>

<footer class="page-foot">
  <div>参考：…</div>
  <div>生成：<!-- ISO 时间 --> · 由 agent 基于原 PDF + 联网补充整理</div>
</footer>

</body>
</html>
```

CSS class 用法：
- `.hero` — 顶部封面，必须有；标题、thesis、元信息一站式。
- `.toc` — sticky 侧栏目录；移动端自动塌陷。
- `.insight` — 核心 insight 横幅，全篇 1–3 个。
- `.compare > .naive / .insight-card` — naive vs paper 解法的并排对比卡。
- `.interactive` — 交互模块容器；`.reveal` 子元素首行写"此模块要揭示：…"。
- `.uncertain` — 未充分消化的位置。
- `.pull-quote` — 引文/金句块。
- `figure.diagram` — 图示容器（SVG / CSS / emoji 拼装均可）。
- `aside.external` — 外部引用 / 联网补充内容；自带"外部补充 · agent"标注。

## Gotchas

- 多 PDF 时**问用户**选哪个；不要静默选第一个。
- 不要默默留 TODO 占位章节；要么写完整，要么用 `.uncertain` 显式标注。
- 外部内容**必须**用 `aside.external` 或等价方式包起来——用户要一眼分清"paper 原文 vs agent 引入"。
- 引入的所有 CDN URL 都用稳定版本号，不要用 `@latest`。
- **写完先自审"文字堆叠"问题**：如果整页只有 `<p>` + 少量 `<pre>`，没有 hero / TOC / `.compare` / `.insight` 卡片 / 任何 SVG 或 figure——立刻回去补，否则不算交付。
- **写完先自审"论文腔"问题**：通读一遍，把"本文 / 综上 / 基于此 / 不失一般性 / 值得注意的是 / 显然地"这类词全部替换或删掉；段落如果连续 6 行以上没有换段、没有短句、没有比喻，就拆。
- **TOC 要真的有效**：每个 `<section>` 必须有 id；TOC 里的 `<a href="#id">` 必须真能跳。可以加一段最小 IntersectionObserver JS 高亮当前章节。

## See also

- 项目根 `AGENTS.md` — 用户背景、项目级硬约束、触发协议。
