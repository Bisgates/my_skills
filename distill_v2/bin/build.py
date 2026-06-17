#!/usr/bin/env python3
"""distill_v2 single-file assembler.

Produces ONE self-contained .html that renders a real Distill article offline:
the official `template.v2.js` (patched for offline KaTeX) and KaTeX (js + css +
woff2 fonts base64-inlined) are all vendored inline. Modern browsers skip the
webcomponents / IntersectionObserver polyfills natively, so the only thing the
file ever needs from the network is nothing.

Token model (literal string replacement, NOT str.format — JS/CSS contain braces):
  skeleton.html carries the tokens below; everything large is injected verbatim.

  {{TITLE}}            <title> text
  {{FRONTMATTER}}      YAML body of <script type="text/front-matter">
  {{EXTRA_CSS}}        author CSS for labs/figures (distill-compatible)
  {{CONTENT}}          inner HTML of <d-article>
  {{APPENDIX}}         inner HTML of <d-appendix> (before the auto bibliography)
  {{BIBLIOGRAPHY}}     BibTeX text for <script type="text/bibliography">
  {{LABS_JS}}          author JS (lab IIFEs)
  {{KATEX_HEAD_CSS}}   injected: <style> full katex css, base64 woff2 </style>
  {{KATEX_SHADOW_CSS}} injected: katex layout css (font-face stripped) for shadow roots
  {{KATEX_JS}}         injected: katex.min.js
  {{TEMPLATE_JS}}      injected: patched template.v2.js
"""
import argparse, base64, pathlib, re, sys

VENDOR = pathlib.Path(__file__).resolve().parent.parent / "vendor"


def _b64_font(name: str) -> str:
    p = VENDOR / "fonts" / name
    return base64.b64encode(p.read_bytes()).decode("ascii")


def build_katex_css():
    """Return (head_css, shadow_css).

    head_css  : full katex css, every woff2 inlined as a data: URI, woff/ttf
                alternates stripped. Lives in document <head> (covers inline
                delimited math rendered into light DOM + registers @font-face).
    shadow_css: head_css with @font-face blocks removed — injected into each
                d-math shadow root (fonts already registered globally, so we
                avoid duplicating ~380KB of base64 per math element).
    """
    css = (VENDOR / "katex.min.css").read_text()
    # inline each woff2
    for m in sorted(set(re.findall(r"fonts/(KaTeX_[A-Za-z0-9_-]+\.woff2)", css))):
        data = _b64_font(m)
        css = css.replace(f"fonts/{m}", f"data:font/woff2;base64,{data}")
    # drop woff/ttf alternates (keep only the inlined woff2)
    css = re.sub(r",url\(fonts/KaTeX_[A-Za-z0-9_-]+\.(?:woff|ttf)\)\s*format\(\"(?:woff|truetype)\"\)", "", css)
    head_css = css
    shadow_css = re.sub(r"@font-face\{[^}]*\}", "", css)
    return head_css, shadow_css


def read(path):
    return pathlib.Path(path).read_text() if path else ""


def _lab_harness(skeleton_path):
    """The shared lab harness (so.fit/raf/drag/...) lives beside the skeleton in
    templates/; prepend it to author labs so every build has it. Optional."""
    h = pathlib.Path(skeleton_path).resolve().parent / "lab_harness.js"
    return (h.read_text() + "\n") if h.exists() else ""


def main():
    ap = argparse.ArgumentParser(description="Assemble a single-file Distill article.")
    ap.add_argument("--skeleton", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--frontmatter", help="YAML file (front-matter body)")
    ap.add_argument("--content", required=True, help="HTML fragment: inner <d-article>")
    ap.add_argument("--appendix", help="HTML fragment: inner <d-appendix>")
    ap.add_argument("--bib", help="BibTeX file")
    ap.add_argument("--css", help="author CSS file")
    ap.add_argument("--labs", nargs="*", default=[], help="author JS files")
    args = ap.parse_args()

    head_css, shadow_css = build_katex_css()
    katex_js = (VENDOR / "katex.min.js").read_text()
    template_js = (VENDOR / "template.v2.js").read_text()

    html = pathlib.Path(args.skeleton).read_text()
    repl = {
        "{{TITLE}}": args.title,
        "{{FRONTMATTER}}": read(args.frontmatter),
        "{{EXTRA_CSS}}": read(args.css),
        "{{CONTENT}}": read(args.content),
        "{{APPENDIX}}": read(args.appendix),
        "{{BIBLIOGRAPHY}}": read(args.bib),
        "{{LABS_JS}}": _lab_harness(args.skeleton) + "\n".join(read(p) for p in args.labs),
        "{{KATEX_HEAD_CSS}}": "<style>" + head_css + "</style>",
        "{{KATEX_SHADOW_CSS}}": shadow_css,
        "{{KATEX_JS}}": katex_js,
        "{{TEMPLATE_JS}}": template_js,
    }
    for k, v in repl.items():
        html = html.replace(k, v)

    leftover = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if leftover:
        print(f"WARN unfilled tokens: {sorted(set(leftover))}", file=sys.stderr)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    kb = len(html.encode()) / 1024
    print(f"wrote {out} ({kb:.0f}KB)")


if __name__ == "__main__":
    main()
