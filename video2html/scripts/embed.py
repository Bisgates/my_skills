#!/usr/bin/env python3
"""
video2html — embed a video into a single self-contained HTML file with smooth
trackpad-scrub controls.

Pipeline:
  1. Re-encode the input to all-intra H.264 (every frame is a keyframe) so the
     browser can seek to any timestamp in one decode step — this is the single
     biggest contributor to QuickTime-like scrub feel.
  2. Base64-encode the re-encoded mp4 and inject it as a data: URL into the
     HTML template (templates/page.html).
  3. Write the HTML next to the source video by default.

CRF guide (quality vs. file size tradeoff, all-intra is bitrate-heavy):
   18  visually lossless                ~3x original size
   23  good (default)                   ~1.5x original size
   28  acceptable for screen content    ~0.6x original size
   32  small but soft                   ~0.3x original size

Base64 then adds ~33% on top.
"""
from __future__ import annotations
import argparse, base64, mimetypes, os, shutil, subprocess, sys, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE  = SKILL_DIR / "templates" / "page.html"


def die(msg: str, code: int = 1) -> None:
    print(f"video2html: {msg}", file=sys.stderr)
    sys.exit(code)


def reencode_all_intra(src: Path, dst: Path, crf: int) -> None:
    """Re-encode `src` to `dst` as all-intra H.264, faststart, no audio drop."""
    if not shutil.which("ffmpeg"):
        die("ffmpeg not found in PATH — install it (brew install ffmpeg)")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
        "-g", "1", "-keyint_min", "1", "-bf", "0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dst),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die(f"ffmpeg failed:\n{r.stderr.strip()}")


def build_html(mp4: Path, *, title: str, subtitle: str,
               scrub_px_per_sec: int, invert_scroll: bool) -> str:
    mime = mimetypes.guess_type(mp4.name)[0] or "video/mp4"
    b64 = base64.b64encode(mp4.read_bytes()).decode()
    html = TEMPLATE.read_text()
    return (html
        .replace("__TITLE__", title)
        .replace("__SUBTITLE__", subtitle)
        .replace("__MIME__", mime)
        .replace("__SCRUB_PX_PER_SEC__", str(scrub_px_per_sec))
        .replace("__SCRUB_DIR__", "-1" if invert_scroll else "+1")
        .replace("__B64__", b64))  # b64 last — huge string, do it once


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path, help="input video path")
    ap.add_argument("--out", "-o", type=Path, default=None,
                    help="output HTML path (default: <video>.html next to input)")
    ap.add_argument("--crf", type=int, default=23, help="x264 CRF, lower = better quality, bigger file (default 23)")
    ap.add_argument("--title", default=None, help="HTML <title> and <h1> (default: video filename stem)")
    ap.add_argument("--subtitle", default=None,
                    help="line below the title (default: video metadata summary)")
    ap.add_argument("--scrub-px-per-sec", type=int, default=60,
                    help="trackpad sensitivity: wheel pixels mapped to 1 second of video (default 60)")
    ap.add_argument("--invert-scroll", action="store_true",
                    help="reverse two-finger scrub direction")
    ap.add_argument("--skip-reencode", action="store_true",
                    help="trust the input already has dense keyframes; embed it as-is")
    ap.add_argument("--keep-intermediate", action="store_true",
                    help="keep the re-encoded mp4 next to the HTML for inspection")
    args = ap.parse_args()

    src: Path = args.video.expanduser().resolve()
    if not src.is_file():
        die(f"input not found: {src}")

    out = (args.out or src.with_suffix(".html")).expanduser().resolve()
    title = args.title or src.stem
    subtitle = args.subtitle or f"single-file HTML · embedded from {src.name}"

    with tempfile.TemporaryDirectory() as td:
        if args.skip_reencode:
            staged = src
        else:
            staged = Path(td) / (src.stem + "_allintra.mp4")
            print(f"[1/2] re-encoding all-intra (crf={args.crf}) → {staged.name}", file=sys.stderr)
            reencode_all_intra(src, staged, args.crf)

        print(f"[2/2] embedding {staged.stat().st_size/1e6:.1f}MB video as base64 → {out.name}", file=sys.stderr)
        html = build_html(staged, title=title, subtitle=subtitle,
                          scrub_px_per_sec=args.scrub_px_per_sec,
                          invert_scroll=args.invert_scroll)
        out.write_text(html)

        if args.keep_intermediate and not args.skip_reencode:
            kept = out.with_name(out.stem + "_allintra.mp4")
            shutil.copy(staged, kept)
            print(f"      kept intermediate: {kept}", file=sys.stderr)

    print(f"done · {out} ({out.stat().st_size/1e6:.1f}MB)")


if __name__ == "__main__":
    main()
