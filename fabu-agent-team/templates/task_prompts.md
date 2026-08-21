# Worker prompt skeletons (copy, fill, keep the 时间盒 line)

## Research (read-only; sol/terra/qwen)
# 任务 R<n>：<一句话目标>
只读任务，不用 GPU。产出 $ARC/doc/r<n>_<slug>.md。
上下文：<项目/臂/口径 3-5 行>。
请给出：1) <机制清单 + 证据等级 A/B/C + 对本案例可能性>；2) <每条改法的 file:line、改动量、判据>；3) <按收益/成本排序的 ≤N 个候选，含具体数值>。
可以 grep 本地 <代码路径> 确认模块名；可用 web（若可用）。不改任何文件。

## Code-knob audit (qwen)
# 任务 R<n>：列出所有与 <目标属性> 相关的训练/采样旋钮（file:line、当前值、改法）
输出一张表：旋钮 | 文件:行 | 当前值 | 如何改（可粘贴的 yaml/dotlist/CLI）| 预期方向 | 风险。再单列：config 覆盖机制、采样脚本 CLI 缺口、导出链对新 run 的硬编码依赖。行号必须实测，给复核命令。

## Infra / launcher (qwen)
# 任务 D<n>：把 <上游 arc> 的发射链搬到本 arc 并发射 <臂>
1) copy <launch script> → $ARC/scripts/launch_arm.sh，改路径/GPU 白名单/端口/run root 为环境变量；保留所有 gate；支持 dotlist 覆盖（EXTRA_YAML_OVERRIDES）。
2) copy config → $ARC/configs/arm_base.yaml，只改 root；`grep precision|save_top_k|max_steps|devices` 核对。
3) 导出脚本参数化（RUN_NAME/RUN_ROOT/EXPECTED_STEP），provenance 含 init sha / config sha / steps / gpus。
4) smoke（30 step）→ 过关标准 <无 NaN/OOM、ckpt 落盘、采样 PNG 统计非全黑、config grep 全中>；smoke 后删 ckpt。
5) 发射 <臂>，等 5 分钟确认 step 推进，记录步速/ETA/PID。
6) 写 $ARC/doc/d<n>_infra.md：用法 + "下一臂怎么改参数"的一行命令。
注意磁盘 <余量>；不要开第二个 run。

## Eval toolkit (qwen)
# 任务 E0：一条命令给任意采样目录出 <指标> 逐窗表 + 与基线的配对检验
输入 `--samples --arm --baseline-samples --out`；输出 json + markdown；**selftest 必须复现基线的已发布数字（±0.01）**，selftest 命令和结果写进 doc。兼容 <旧布局> 与 <新布局>。

## Post-train chain (qwen)
# 任务 E1：训练退出 → 导 EMA → 删 ckpt → 双 GPU 采样 → eval → 表格，全自动、按 PID 等待、可续跑
每步写 `_tmp/chain_<RUN>.status` 一行（WAIT_TRAIN/EXPORT_EMA/SAMPLE/EVAL/DONE，失败写 FAILED 并建 .FAIL）；每阶段先检查产物存在再做（可续跑）；setsid 发射；先用已完成臂做 1 窗 smoke 验证 eval 三项都能出。

## Control arm (qwen)
# 任务 E<n>：补控制臂 —— <起点 ckpt> 本身在冻结口径下的指标
先查上游 arc 是否已有同口径样本（sha/seed/config 逐项核对，可复用则写 REUSE_PROVENANCE.md）；出 vs <历史锚> 与 vs <新臂> 两张表；回答"<新臂> 的增益中起点贡献 vs 训练贡献各多少"。

## Adversarial review (terra)
# 任务 R<n>：对抗式复核 —— 挑 <对象> 的漏洞
你的立场是反方。1) 找互相矛盾的结论并**自己复算**；2) 评估每个臂能否回答它声称的问题（混杂变量、起点、步数、功效）；3) 哪个指标最易被伪锐化/伪改善欺骗；4) ≤5 条具体修改建议（文件/臂/命令）。写结论要有复算数字。终审版加：从原始 json 重算全部头条 + 3 个样本从 PNG 重算 + 每个"null"的最小可检出效应 + handoff 措辞必须修正清单。

## Report (sol)
# 任务 H<n>：<compare HTML / 9_summary.html>
形式照抄 <上游 arc 的页面/生成器>（先读其结构/CSS）；内容来源 = $ARC/9_handoff.md（manager 写的权威叙事）+ <doc 列表>；双基线列、三档标色、机制列按 review 的措辞纪律；全量 + lite（<30MiB：视频 640x360 crf33 -an，PNG 480:270）；校验可解析/大小/视频数；写 doc/h<n>_*.md 复跑命令。
