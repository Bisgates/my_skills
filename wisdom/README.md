# wisdom/

Knowledge skills compiled from books and documents — each subdirectory is one book or document collection turned into an agent skill (`SKILL.md` + `chapters/` + glossary / patterns / cheatsheet).

- Not listed in `manifest.txt`. `skill-mgmt/bin/install` auto-discovers every `wisdom/*/` dir containing a `SKILL.md` and symlinks it by basename into `~/.claude/skills`, `~/.codex/skills`, and `~/.gemini/antigravity/skills`.
- Generated from documents the user owns. Skills derived from copyrighted works stay in this private repo — do not redistribute them.
