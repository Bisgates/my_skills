## Arc Protocol
- 任务管理协议：~/.claude/skills/arc/SKILL.md。
- agent **不主动**读 arcs/index.md；仅在用户显式触发 /arc-* skill 或 `arc <subcmd>` CLI 时进入任务流程。
- 触发 skill：/arc-new, /arc-objective, /arc-plan, /arc-execute, /arc-resume, /arc-spawn, /arc-finalize。
- 触发 CLI：arc {new,spawn,pause,resume,status,abandon,touch,log,output,list,cd,rebuild,init}。
- ID 永远 7 字符 YYMMDDx；canonical 路径 `arcs/all/<id>_*`；状态权威在 `0_meta.md`。
- `done` 必须存在 `9_*.md`；`abandoned` 必须有 `--reason`。
