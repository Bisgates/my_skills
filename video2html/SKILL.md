---
name: video2html
description: Embed a video file into a single self-contained HTML page — re-encode to all-intra H.264 for instant seeking, inline the result as a base64 data URL, and ship native HTML5 controls plus a QuickTime-like two-finger trackpad scrub gesture. Use when the user asks to inline/embed a video into HTML, produce a single-file HTML containing a video, make HTML5 video scrub as smoothly as QuickTime, or invokes `/video2html`. Different from `frontend-design` (general UI) and `grok` (paper-learning HTML) — when those skills need a video inlined, call this one.
---

# video2html

Produces one HTML file containing one video, where the video lives inside the HTML as a `data:video/mp4;base64,...` URL. Output is `<video_stem>.html` next to the source by default.

The skill exists because doing this well requires three non-obvious decisions that the agent shouldn't re-derive every time:

1. **All-intra re-encode** (`-g 1 -bf 0`). With B-frames, the browser has to decode backward to land on an arbitrary timestamp — that's why HTML5 video scrubs jerk while QuickTime stays buttery. Forcing every frame to be a keyframe trades file size for instant seek.
2. **Base64 data URL**. The only way to keep a video and its viewer in a single file you can email, attach to a paper-learning HTML, or hand over a USB stick. Inflates the payload ~33%.
3. **Wheel scrub with momentum**. macOS trackpad two-finger swipes deliver `wheel` events with pixel-precision `deltaX`/`deltaY` *and* native inertial momentum after release. A small JS handler turns that into QT-style scrub.

The bundled script encapsulates all three.

## Quick start

```bash
~/.claude/skills/video2html/scripts/embed.py /path/to/video.mp4
# → /path/to/video.html  (single self-contained file, ~1.5× original size)
```

Open with `open video.html`. Hover over the video, two-finger swipe to scrub.

## Workflow

The standard path is one command. Take user-friendly defaults; only reach for flags when the user calls for them.

```bash
scripts/embed.py <video> [--out FILE] [--crf N] [--title TEXT] [--scrub-px-per-sec N] [--invert-scroll]
```

| Flag | Default | When to override |
|---|---|---|
| `--crf` | 23 | Bump to 28 if the HTML must stay under ~10MB; drop to 18 only for visually critical material. All-intra burns bits — CRF moves size by ~2× per 5 steps. |
| `--scrub-px-per-sec` | 60 | Larger = scrub feels slower / more controlled. Try 100–150 for long videos where small swipes shouldn't fly across minutes. |
| `--invert-scroll` | off | If the user says "left/right is reversed" or runs macOS without natural scrolling. |
| `--skip-reencode` | off | Use when the source is already known to be all-intra (e.g., second pass, screen recording with sparse motion). Saves time but seek smoothness depends on the input. |
| `--out` | `<video>.html` next to source | When the caller is splicing the result into a larger pipeline. |

After running, eyeball the resulting HTML in the browser **before** declaring done: confirm playback, confirm two-finger scrub works in both directions. If the user mentioned a specific size budget, also check `ls -lh` against it.

## When the user wants the video inside something bigger

If the user is not asking for a standalone HTML — they want the video inlined into an existing page (e.g., a `grok`-generated paper-learning HTML) — the right move is:

1. Run the script with `--out /tmp/discard.html --keep-intermediate` just to get the all-intra mp4 produced as a side effect. The kept file is `<out_stem>_allintra.mp4` next to `--out`.
2. Base64-encode that mp4, splice the resulting `data:video/mp4;base64,...` string into a `<video src="...">` inside the host HTML.
3. Copy the wheel-scrub `<script>` block from `templates/page.html` into the host HTML — the handler is ~15 lines, scoped via a single `<video>` element id.

Do not just shell out and dump the standalone HTML inside the host — the standalone wraps the video in its own `<html>/<body>` chrome.

## Tuning the scrub feel

The smoothness recipe lives in `templates/page.html`. The two knobs:

- `SCRUB_PX_PER_SEC` — wheel pixels mapped to one second of video. Lower = more reactive, easier to overshoot. The default 60 was tuned on a 14-second clip; for a 5-minute screencast bump it to 200+.
- `SCRUB_DIR` — `+1` follows natural-scroll semantics (swipe right → forward); `-1` inverts.

The resume-after-gesture timer is 220ms. Don't shorten it below ~180ms or trailing inertial wheel events will trigger spurious resumes mid-scrub.

## Gotchas

- **File size**: base64 inflates by 33% on top of the all-intra mp4, which is already 1.5–3× the original h.264 file. A 10MB source easily becomes a 25MB HTML. For multi-video pages, this compounds — at that point reconsider whether single-file distribution is still worth it vs. shipping a zip.
- **Browser startup cost**: the browser parses the entire base64 string before the video element can begin playback. ~30MB takes 1–2 s of frozen tab on first open. Subsequent plays are instant.
- **Memory**: the base64 string stays resident in the DOM. Embedding 5 videos at 20MB each = ~100MB of extra browser memory beyond the decoded frames.
- **`file://` sandbox**: opening the output via `file://` works for everything in this skill (data URLs aren't subject to CORS). But if the host HTML separately tries to load *external* video by relative path, that's a different question — file:// is strict about cross-directory reads.
- **Audio**: the script encodes audio to AAC if the source has it, and is a no-op when it doesn't. To strip an existing audio track, edit the ffmpeg command to add `-an`. Most scrub-demo material is mute screencasts, so this rarely matters.
- **Codec assumption**: the script always emits H.264. Modern Safari/Chrome/Firefox all play H.264 from a data URL. AV1/VP9 would be smaller but worse-supported; not worth it for this skill's distribution use case.
- **ffmpeg required**: `brew install ffmpeg`. Script fails fast with a clear message if missing.

## See also

- `templates/page.html` — the HTML scaffold. Modify here to change the player chrome project-wide; every invocation reads it fresh.
- `scripts/embed.py` — the pipeline. Source of truth for ffmpeg flags and base64 wiring.
- `grok` — paper-learning HTML generator. When a `grok` artifact needs an inlined video, follow the "When the user wants the video inside something bigger" workflow above.
