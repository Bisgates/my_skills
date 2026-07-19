---
name: web-reach
description: >-
  Fetch and search platform content that needs the user's logged-in browser
  session or a specialized backend — keyword-search on X/Twitter, 小红书
  (Xiaohongshu) and Bilibili feeds, RSS, GitHub, and clean web-page reads via
  Jina Reader. Each platform routes to its working backend (twitter-cli, rdt,
  yt-dlp, gh, Jina, …) through the local clash proxy, reading login cookies from
  the local Chrome profile for auth-gated sites (cookies stay on the machine).
  Use when the user shares a xiaohongshu.com / bilibili.com / github.com link or
  an RSS feed, wants to keyword-search X, or needs logged-in / gated content a
  logged-out reader can't reach. For a plain logged-out read of a Reddit thread,
  an X account or tweet, or a YouTube video, prefer `agy-reach` (zero-setup, via
  the Gemini subscription) and fall back here only when agy is unavailable or a
  login is required. Do NOT use for plain web search (built-in WebSearch) or
  multi-source fact-checked reports (use deep-research).
---

# web-reach

Give the agent real reach onto the platforms whose content the built-in tools choke on: Reddit (403 to anyone anonymous), X/Twitter, 小红书, YouTube transcripts, Bilibili — plus plain web, RSS, and GitHub. This is the local, field-tested version of the [agent-reach](https://github.com/Panniantong/agent-reach) idea: pick the working backend per platform, route through the proxy, reuse the browser login. The agent does the reading by calling the backend directly — this skill is the routing knowledge, not a wrapper.

## The one mental model

Access to any platform is three gates in series. All three must be open, so when a fetch fails, name the closed gate *before* retrying:

```
   reach = [ network ] × [ tool present ] × [ login session ]
```

- **network** — external traffic must go through clash at `http://127.0.0.1:7890`. The shell's `HTTP_PROXY`/`HTTPS_PROXY` env vars point at a company proxy that does **not** route to these sites — every request silently times out (`000`). This is the #1 cause of "it doesn't work". Pass the clash proxy explicitly, or re-export the env vars to it for tools that read them.
- **tool** — the per-platform backend. Zero-login platforms need only this.
- **login** — Reddit/X/小红书 have no anonymous path. They ride your existing browser session; the cookie is extracted from the local Chrome profile.

Failures are almost always gate 1 (wrong proxy) or gate 3 (not signed in), rarely the tool itself.

## Quick start

```bash
P=http://127.0.0.1:7890                                    # clash; everything goes through it
export HTTPS_PROXY=$P HTTP_PROXY=$P                        # for tools that read env (yt-dlp, gh, pip…)
bash scripts/check.sh                                      # doctor: proxy reachability + tool presence
```

| platform | login? | backend | shape of the call |
|---|---|---|---|
| web page | no | Jina Reader | `curl -s https://r.jina.ai/<URL>` |
| YouTube | no | yt-dlp | `yt-dlp --proxy $P --js-runtimes node …` |
| RSS/Atom | no | feedparser | `python -c "import feedparser; …"` |
| GitHub | no | gh CLI | `gh repo view o/r`, `gh search code …` |
| Bilibili | no | search API / bili-cli | direct search API, no login |
| Reddit | **yes** | rdt-cli / raw cookie | `rdt search "q"` once authenticated |
| X/Twitter | **yes** | twitter-cli | `twitter feed`, `twitter following <u>` |
| 小红书 | **yes** | cookie SSR / xiaohongshu-mcp | SSR `explore` feed via cookie; search needs a headless tool |

## Zero-login platforms

No auth, just the tool + the proxy.

- **YouTube** — yt-dlp needs a JS runtime to clear YouTube's anti-bot, or you get `Video unavailable`: pass `--js-runtimes node` (node is present) or install deno (deno works with no config). Captions without downloading the video:
  `yt-dlp --proxy $P --js-runtimes node --write-sub --sub-lang en --skip-download -o '%(id)s.%(ext)s' <URL>`. Metadata: `--print "%(title)s | %(duration)ss | %(view_count)s views"`.
- **Web page** — `curl -s https://r.jina.ai/<URL>` returns clean Markdown instead of tag soup. No key.
- **GitHub** — `gh` is already authed; `gh repo view`, `gh issue list`, `gh search code/repos/issues`.
- **RSS** — feedparser handles any feed: `feedparser.parse(url)` → `.entries`.
- **Bilibili** — the search API is reachable without login; for video detail/subtitles prefer bili-cli (yt-dlp is firewalled by Bilibili's risk control).

## Login-gated platforms (reuse the browser session)

Reddit/X/小红书 return 403 or a login redirect to anonymous requests, so they need your existing login. The durable path on this Mac: pull the cookie from the logged-in **Chrome** profile, hand it to the backend.

Cookies are live credentials. Keep them local, **mask** them in anything you print back to the user (show `len`/first chars, never the full value), write any credential file `chmod 600`, and delete temp credential files when done. Nothing is ever uploaded — the cookie only authenticates to the site it came from.

Extract with the bundled helper (WAL-aware copy so fresh logins aren't missed + macOS-keychain decrypt; a one-time keychain prompt pops that the user must approve):

```bash
python scripts/extract_cookies.py x.com --names auth_token,ct0      # specific cookies, for env export
python scripts/extract_cookies.py xiaohongshu.com --cookie-string   # full 'k=v; k=v' header
python scripts/extract_cookies.py reddit.com --mask                 # inspect, values masked
```

### Reddit
Anonymous is 403 everywhere — even the homepage and `.json`. Login is mandatory.
- cookie: `reddit_session`. Two ways to use it:
  - **rdt-cli** (project-native): write `~/.config/rdt-cli/credential.json` →
    `{"cookies": {"reddit_session": "<value>"}, "source": "manual", "username": "<you>", "modhash": null, "saved_at": 0, "last_verified_at": null}` (chmod 600), verify `rdt status --json` → `authenticated: true`, then `rdt search/sub/read`.
  - **raw cookie**: send `Cookie: reddit_session=<value>` with a desktop browser User-Agent. Browsing (`/r/<sub>/hot.json`) and reading (`/<permalink>.json`) work; `/api/v1/me.json` only returns identity with the OAuth `token_v2`, so don't rely on it for "who am I".

### X / Twitter
- cookies: `auth_token` + `ct0`. `export TWITTER_AUTH_TOKEN=<auth_token> TWITTER_CT0=<ct0>`, then twitter-cli.
- works: `status`, `feed` (home timeline), `following`/`followers`, reading tweets / threads / `article`.
- known breakage: `twitter search` 404s when twitter-cli fails to build the `x-client-transaction-id` header (X rotates its obfuscated JS; you'll see `Failed to init ClientTransaction`). The read endpoints are unaffected. For search, fall back to a real-browser backend (OpenCLI / bird) — that's exactly the "swap the backend" case this routing exists for.

### 小红书 (Xiaohongshu)
- cookies: the whole set (`a1`, `web_session`, `webId`, `gid`, …) — pass the full cookie string, not one name.
- cookie-only reach = the logged-in **`explore` feed**: that page is server-rendered, so the recommended notes sit inside `window.__INITIAL_STATE__` in the HTML. Fetch `https://www.xiaohongshu.com/explore` with the cookie + browser UA and parse note cards out of the JSON (`displayTitle`, `user.nickname`, `interactInfo.likedCount`).
- keyword search and arbitrary note detail need the `X-s`/`X-t` request signature, which only a real browser running 小红书's JS can compute. Cookie-only curl to those API endpoints bounces. Use [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (headless browser, scan to log in) or desktop OpenCLI for search/detail.

## Gotchas

- **Env proxy is dead for these sites.** `HTTP_PROXY` → company proxy → `000` on youtube/x/reddit/小红书. Only clash `127.0.0.1:7890` reaches them. Verify with `scripts/check.sh`.
- **macOS has no `timeout`.** Wrap a tool that might hang (twitter-cli has stalled for minutes): `perl -e 'alarm shift; exec @ARGV' 45 <cmd>`.
- **This shell is zsh.** Unquoted `$var` does **not** word-split. To pass a command stored in a variable, use explicit args or `${=var}`.
- **Chrome cookie store.** Fresh logins land in `Cookies-wal` before checkpointing — copy `Cookies` + `Cookies-wal` + `Cookies-shm` together, or you'll miss a just-completed login. Decryption needs the `Chrome Safe Storage` keychain key (the one-time prompt). `extract_cookies.py` does both; closing Chrome is not required.
- **Anti-bot / ban risk.** Scripted cookie use can trip a platform's automation detection. Prefer a throwaway/小号 over a main account where it matters; this is read-only, but the platform doesn't know that.
- **Cross-machine.** This cookie path assumes macOS + Chrome + clash. On a headless server the repo syncs to, there's no Chrome/keychain — use server-side logins instead (`rdt login`, xiaohongshu-mcp QR) and a server-side proxy.

## See also

- `agy-reach` skill — the zero-setup default for a logged-out read of a Reddit thread, an X account/tweet, or a YouTube video: it delegates the fetch to `agy`'s Gemini-subscription server-side reader (no cookies). Use web-reach when that isn't enough — keyword-search on X, 小红书/Bilibili, or anything needing your login.
- [agent-reach](https://github.com/Panniantong/agent-reach) — upstream inspiration; multi-backend routing + a `doctor` that reports the live backend per platform.
- `deep-research` skill — for multi-source, fact-checked research reports. web-reach only *fetches*; it doesn't synthesize or cite.
- Built-in **WebSearch** — generic web search. Use that, not this, for a plain "search the web for X" with no specific platform.
