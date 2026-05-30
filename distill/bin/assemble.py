#!/usr/bin/env python3
"""Assemble a deepdive report from a skeleton + ordered section fragments + ordered lab JS.

The skill's generation step fans out one agent per chapter group; each writes a
`<section>` fragment and a lab-JS fragment. This stitches them into the single-file
report: sections go before </main>, lab IIFEs go before the final </script>, and
{{TOKEN}} placeholders are filled.

Usage:
  assemble.py --skeleton skeleton.html --out report.html \
      --sections A_sections.html B_sections.html ... \
      --labs A_labs.js B_labs.js ... \
      --set TITLE=... --set KICKER=... --set DECK=... --set FOOTER=... --set STATS=@stats.html
A --set value of the form @path reads the replacement text from that file.
"""
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sections", nargs="+", required=True, help="section HTML fragments, in display order")
    ap.add_argument("--labs", nargs="*", default=[], help="lab JS fragments, in the same order")
    ap.add_argument("--set", action="append", default=[], dest="sets",
                    help="KEY=VALUE to replace {{KEY}}; VALUE may be @file")
    ap.add_argument("--three", action="store_true",
                    help="inject the pinned three.js r128 global build (for real-3D reports)")
    args = ap.parse_args()

    html = Path(args.skeleton).read_text()

    if args.three:
        html = html.replace(
            "<!--THREEJS-->",
            '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>')

    for kv in args.sets:
        k, _, v = kv.partition("=")
        if v.startswith("@"):
            v = Path(v[1:]).read_text()
        html = html.replace("{{" + k + "}}", v)

    sections = "\n\n".join(Path(p).read_text() for p in args.sections)
    if "</main>" not in html:
        raise SystemExit("skeleton has no </main> anchor")
    html = html.replace("</main>", sections + "\n\n</main>", 1)

    if args.labs:
        # each lab in its OWN <script> so a runtime error in one can't halt the others
        blocks = "\n".join(f"<script>\n{Path(p).read_text()}\n</script>" for p in args.labs)
        if "</body>" not in html:
            raise SystemExit("skeleton has no </body> anchor")
        html = html.replace("</body>", blocks + "\n</body>", 1)

    Path(args.out).write_text(html)
    leftover = html.count("{{")
    print(f"wrote {args.out}: {len(html)} bytes, "
          f"{html.count('<section')} sections, {html.count('<canvas')} canvases, "
          f"{leftover} unresolved {{{{tokens}}}}")
    if leftover:
        import re
        print("  unresolved:", sorted(set(re.findall(r'{{(\w+)}}', html))))


if __name__ == "__main__":
    main()
