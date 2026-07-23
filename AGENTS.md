## Project goal

`my_skills` 是用户个人 agent skill 的**单一真相源**（single source of truth）。

- 仓库位置：Mac `~/project/agent/skills/`，服务器 `~/my_skills/`，远端 `github.com/Bisgates/my_skills`。
- 每个顶层子目录是一个 skill；`<repo>/<name>/SKILL.md` 是该 skill 的**唯一物理源文件**。
- `~/.claude/skills/<name>`、`~/.codex/skills/<name>`、`~/.gemini/antigravity/skills/<name>` 全部是指向仓库的 **symlink**，编辑仓库内 SKILL.md 即对所有 runtime 生效，无需 copy。
- 跨机器同步 = 标准 `git push` / `git pull --rebase`。
- `manifest.txt` 列出所有应该被链接的 skill；**第一行必须是 `skill-mgmt`**。

## skill-mgmt = 元 skill（管理其它 skill 的 skill）

`skill-mgmt/` 是这个仓库的"主"skill：它是唯一一个**管理其它 skill 生命周期**的 skill，所有 install/sync/adopt/new 操作都通过它的 `bin/` 脚本完成。其它 skill 都是**被 skill-mgmt 管理**的对象。

- 权威说明：`<repo>/skill-mgmt/SKILL.md`（agent 在触发时应优先读它）。
- 四个核心脚本（idempotent）：
  - `skill-mgmt/bin/install [name...]` — 装/重建 symlink，自动解析 `dependencies:` 闭包
  - `skill-mgmt/bin/sync` — `git pull --rebase` 后再 `install`
  - `skill-mgmt/bin/adopt <name>` — 把散落在 `~/.claude/skills/` 等位置的真实目录收编进 repo
  - `skill-mgmt/bin/new <name> [desc]` — 用 `templates/SKILL.md.template` 脚手架新 skill
- 严格触发条件（仅在用户明说时进入此流程）：
  - "新建/创建 skill X" / "create/scaffold a skill X"
  - "同步 skills" / "sync my skills"
  - "adopt / 收编 skill X"
  - "在这台机器装 my skills" / "bootstrap skills here"
  - "安装 skill X" / "rebuild links for X"
- **不要触发**的情形：
  - 询问某个具体 skill 的功能（直接读那个 skill 的 SKILL.md 即可）
  - 仅编辑现有 skill 的内容（直接改 `<repo>/<name>/SKILL.md`，改完默认 commit + push）
  - 普通 git 操作
- Git 自动化：`new` / `adopt` 在脚本启动时仓库为 clean 的情况下自动 `git add/commit/pull --rebase/push`；`SKILL_MGMT_AUTOCOMMIT=0` / `SKILL_MGMT_AUTOPUSH=0` 可关闭。
- 依赖声明在 SKILL.md frontmatter 的 `dependencies:`（也接受 `depends_on:` / `requires:`），install 会递归解析。

读取顺序（agent 视角）：用户触发任一上面列出的操作 → 读 `skill-mgmt/SKILL.md` → 调对应 `bin/` 脚本。其余情况都不应主动调度 skill-mgmt。

## Arc Protocol
- 任务管理协议：~/.claude/skills/arc/SKILL.md。
- agent **不主动**读 arcs/index.md；仅在用户显式触发 /arc-* skill 或 `arc <subcmd>` CLI 时进入任务流程。
- 触发 skill：/arc-new, /arc-objective, /arc-plan, /arc-execute, /arc-resume, /arc-spawn, /arc-finalize。
- 触发 CLI：arc {new,spawn,pause,resume,status,abandon,touch,log,output,list,cd,rebuild,init}。
- ID 永远 7 字符 YYMMDDx；canonical 路径 `arcs/<id>_*`（单层，无 all/ 无 view 软链）；状态权威在 `0_meta.md`。
- `done` 必须存在 `9_*.md`；`abandoned` 必须有 `--reason`。
