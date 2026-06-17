#!/usr/bin/env python3
"""Strip base64 data URIs and script/style bodies from distill HTML so reader
agents can analyze structure+prose+CSS at low token cost. Keeps tags, classes,
text, and <style> CSS; replaces <script> bodies and data: URIs with markers."""
import re, sys, pathlib

def lean(html: str) -> str:
    # drop base64 / long data URIs
    html = re.sub(r'data:[^"\')\s]{80,}', '[DATA_URI]', html)
    # empty out <script> bodies but keep the tag + src
    html = re.sub(r'(<script\b[^>]*>)(.*?)(</script>)',
                  lambda m: m.group(1) + ('[JS:%d chars]' % len(m.group(2))) + m.group(3),
                  html, flags=re.S|re.I)
    # collapse runs of blank lines / trailing ws
    html = re.sub(r'[ \t]+\n', '\n', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html

for p in sys.argv[1:]:
    src = pathlib.Path(p)
    out = src.parent / 'lean' / (src.stem + '.txt')
    txt = lean(src.read_text(errors='replace'))
    out.write_text(txt)
    print(f"{out.name}: {len(src.read_text(errors='replace'))//1024}KB -> {len(txt)//1024}KB")
