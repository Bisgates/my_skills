---
name: read_xhs
description: >
  Fetch a Xiaohongshu (xiaohongshu.com / 小红书) post by URL and summarize content primarily from in-image text; the caption/desc is supplementary and comments are ignored. Use when the user shares a xiaohongshu.com or xhs.in URL and asks to read, summarize, extract, translate, or analyze the post. Chinese phrasings include 看下/总结/读取/讲了啥/帮我看 + 小红书/xhs/这条/这个帖子. Do NOT trigger for other platforms (Weibo, Douyin, TikTok, X, Instagram), for video-only xhs posts where the user wants transcription, or for generic URL summarization without an xhs URL.
---

# read_xhs

A Xiaohongshu (小红书 / xhs) note is an image-first format. The web HTML's `desc` field is usually a one-liner plus hashtags — the substantive content (article body, tables, screenshots) lives **inside the images**. So this skill treats images as primary source and uses caption only for framing.

## Quick start

```bash
out=$(/Users/han/project/agent/skills/read_xhs/scripts/fetch_xhs.sh "<xhs-url>")
cat "$out/meta.txt"
ls "$out"/img*.jpg
```

Then Read each `img*.jpg` with the Read tool (Claude is multimodal — JPEGs read directly). Summarize from the images; fold in title/author/desc from `meta.txt` only where useful.

## Workflow

1. **Fetch.** Run `scripts/fetch_xhs.sh <url>`. It writes `/tmp/xhs/<post-id>/` containing `page.html`, `meta.txt`, and `img1.jpg, img2.jpg, …`. The script's stdout is that directory.
2. **Check kind.** If `kind` file exists with `no_images_found`, the note is video-only — surface that to the user; do not fabricate content from the caption alone. Optionally ask whether to try a different approach.
3. **Read images in order.** Image N is page N of the article. Process all of them — XHS authors often put the punch line on the last image.
4. **Summarize.** Image text is the source of truth. The `desc` is usually hashtag soup; quote from it only when it carries non-redundant framing (the author's disclaimer, the article's stated thesis). Don't pad output with stats (`liked`/`collected`) unless the user asked.
5. **Output shape.** Mirror the article's own structure (numbered list → numbered list; before/after → before/after). End with one short editorial line — what kind of post this is, who it targets, what's new vs. boilerplate — calibrated to the user's depth, not a generic "hope this helps" wrap.

## What this skill explicitly does not do

- **Comments.** The HTML carries comment data; ignore it. The user does not want comment-mined opinions polluting the summary of the author's post.
- **Sidebar / recommended notes.** The fetcher takes only the main note's images. Don't follow related-note links unprompted.
- **Login-walled content.** No cookie/session handling. If the curl response is empty or the meta fields are blank, surface that and ask the user to paste the content from their logged-in browser (the user typically has Arc / desktop XHS logged in).

## Gotchas

- **Proxy blocks XHS.** The user's default `HTTPS_PROXY` (a remote tunnel) is blocked by xhs CDN. The script unsets all proxy env vars before curl — don't reintroduce them.
- **Caption ≠ content.** `meta.txt` `desc:` is often just `本文不构成投资建议 #tag1 #tag2 …`. Trust the images.
- **Image URL escapes.** XHS embeds image URLs with `/` escapes inside the JSON blob — the script normalises them to `/`. If you reimplement extraction by hand, don't forget this step.
- **Image URLs are `http://`, not https.** Intentional on XHS's CDN side; curl handles it fine. Don't rewrite to https — some edges reject it.
- **First-match parsing.** `meta.txt` uses `head -1` for title / nickname / desc / stats because XHS ships sidebar-recommend cards and footer ICP entries with the same field names later in the document. If the *wrong* post's metadata starts coming through, the page structure changed — re-inspect `page.html`.
- **Post-id regex.** The script handles `/explore/<id>` and `/discovery/item/<id>`. Short-link `xhs.in/<code>` redirects — `curl -L` follows it, but the post id derivation runs against the *original* URL; pass the resolved URL if needed.
- **Video notes.** When `kind` says `no_images_found`, this skill bails out. Don't try to summarise a video post from caption alone.

## Should-trigger / should-not-trigger sanity

Should trigger:
- "总结这个小红书 https://www.xiaohongshu.com/explore/..."
- "帮我看下这条 xhs <url>"
- "这个帖子讲了啥 <xhs url>"
- "translate this xiaohongshu post <url>"
- "<xhs url> 提取下要点"

Should NOT trigger:
- "总结这个抖音 / 微博 / Twitter" — wrong platform
- "用小红书风格写一段文案" — about aesthetic, not reading a post
- "下载这个小红书视频" — video download, not summarisation
- "总结这个网页 <non-xhs url>" — generic web summary, use WebFetch directly
- "小红书最近有什么趋势" — research, not a single post

## See also

- `../write-a-skill/SKILL.md` — authoring conventions, in case this skill needs structural changes.
