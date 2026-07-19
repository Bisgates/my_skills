---
name: agy-reach
description: >-
  Read and research content on YouTube, Reddit, and X/Twitter by delegating the
  fetch to the Antigravity CLI (`agy`), whose server-side `read_url_content`
  reader uses the user's Gemini subscription to pierce the login / anti-bot walls
  that block ordinary WebFetch and curl — no cookies, no paid API, no local
  scraper. Use when the user shares a reddit.com / x.com / twitter.com /
  youtube.com link, or asks to read / summarize / "see what's being said on" a
  Reddit thread, an X account or tweet, or a YouTube video, and the built-in web
  fetch returns a login wall or an empty JS shell. This is the default,
  zero-setup path for those three sites. Do NOT trigger for keyword search on X,
  小红书 (Xiaohongshu), or Bilibili, or for logged-in-only content — those need
  the cookie / browser backends in `web-reach`. For plain web pages that the
  built-in WebSearch / WebFetch already handle, don't use this.
---

# agy-reach

Reddit returns 403 to anyone anonymous; X serves logged-out visitors an empty JS
shell; both walls stop a normal `WebFetch`/`curl` cold. `agy` (the Antigravity
CLI) carries a tool the caller doesn't have: `read_url_content`, a **server-side
"Fetched live" reader** tied to the user's Gemini subscription. It reads those
pages logged-out and un-walled — no cookie extraction, no X API bill, no local
scraping stack. So when your own fetch hits a wall on these sites, don't fight
it — shell out to `agy` and let its reader do the fetch.

This skill is the routing knowledge plus one wrapper script. It does **not**
replace `web-reach`: that skill logs into sites with your browser cookies and can
keyword-search X / read 小红书 / Bilibili. `agy-reach` is the simpler default for
the three walled sites `agy` reads well.

## The one call

Everything routes through `agy -p` (print mode) via the bundled wrapper, which
handles the sharp edges (see Gotchas):

```bash
scripts/agy_read.sh "<what agy should read and return>"
```

The wrapper prints `agy`'s answer to stdout. Treat that text as the fetched
data. When exact wording matters (quotes, titles, numbers), tell `agy` to
**quote the raw returned text, not paraphrase** — its reader sometimes summarizes
on its own, and a paraphrase you then re-summarize drifts from the source.

## Per-platform routing

`agy` already knows this routing if the user has the global rule in
`~/.gemini/GEMINI.md` (see See also), but state it in the prompt anyway so the
skill is self-contained.

### Reddit — read works; discovery is two-step
- **Read a known URL** (subreddit, permalink, user): give the URL, ask for what
  you need.
  `scripts/agy_read.sh "Use read_url_content to read https://www.reddit.com/r/LocalLLaMA/top/?t=week and list the post titles verbatim."`
- **Find threads by topic**: `agy` can `search_web` (Google indexes Reddit), so
  ask it to search first, then read the winners.
  `scripts/agy_read.sh "search_web for site:reddit.com <topic>, pick the 3 most relevant permalinks, then read_url_content each and summarize with URLs."`

### X / Twitter — read works; there is no keyword search
- **Read an account or a tweet**: give `x.com/<handle>` or the tweet URL.
  `scripts/agy_read.sh "Use read_url_content to read https://x.com/<handle> and quote the latest posts verbatim."`
- **No keyword search.** Google does not index x.com, so `search_web` returns
  nothing for X — `agy` cannot find tweets by topic. The user must supply the
  handle or tweet URL. If they want topic-search on X, that needs Grok / the X
  API / cookie search — out of scope here; point them at `web-reach` or say so.

### YouTube — transcript/metadata via yt-dlp, not the reader
`read_url_content` on a watch page hits YouTube's "Sign in to confirm you're not
a bot" wall, so `agy` (per its routing rule) uses local `yt-dlp` instead. You can
let `agy` do it, or just run `yt-dlp` yourself — it needs no subscription:

```bash
P="${https_proxy:-http://127.0.0.1:7899}"   # clash; env may already be set
yt-dlp --proxy "$P" --js-runtimes node --skip-download \
  --write-auto-sub --sub-lang en --convert-subs srt -o '%(id)s.%(ext)s' "<url>"
# metadata only:
yt-dlp --proxy "$P" --js-runtimes node --skip-download \
  --print "%(title)s | %(duration)ss | %(view_count)s views" "<url>"
```

## Gotchas

- **Never pipe `agy -p` into another command.** `agy` double-forks a
  `--bg-updater` child that keeps stdout open, so `agy -p … | head` never sees
  EOF and hangs forever. The wrapper writes to a temp file instead — use it, or
  redirect to a file yourself (`agy -p … >out 2>&1 </dev/null`).
- **macOS has no `timeout(1)`.** The wrapper bounds the run with a `perl alarm`
  (default 240s, override `AGY_READ_TIMEOUT`). A read that stalls past that
  returns what it has plus a timeout note on stderr.
- **`--model` wants the full label, not an alias.** `--model flash` errors; it's
  `--model "Gemini 3.5 Flash (Medium)"`. Omit `--model` and the wrapper uses the
  account default, which is fine for reading.
- **Trust but verify.** `agy` runs with `--dangerously-skip-permissions` so it
  won't block on approval, but that also means it can fall back to writing its
  own scraper via `run_command`. If fidelity matters, tell it to use
  `read_url_content` only and to quote raw — and sanity-check any URL it returns
  before citing it.
- **You must have `agy` installed and logged in.** It lives at `~/.local/bin/agy`
  (Antigravity CLI, authenticated to the Gemini subscription). If it's absent,
  this skill can't run — fall back to `web-reach`.

## See also

- `web-reach` — the cookie / multi-backend reader: X keyword-search, 小红书,
  Bilibili, and anything needing your logged-in session. Use it when `agy`'s
  logged-out reader isn't enough.
- `~/.gemini/GEMINI.md` — a global rule that makes `agy` route reddit/x→
  `read_url_content` and youtube→`yt-dlp` on its own. This skill restates that
  routing so it works even without the rule.
