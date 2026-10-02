#!/usr/bin/env python3
"""Merge per-model HTML drafts into one comparison page.

Usage:
  merge_html.py --title T --out OUT.html [--sub S] [--note N] [--index rows.tsv] PART[=LABEL] ...

Each PART is one model's draft file. Its id is the file stem (astra.html -> astra);
LABEL is the band heading (default: the id). Parts that follow the scoped-section
contract (one <section class="set...-<id>"> with all CSS inside, every selector
prefixed) are inlined. Anything else is embedded as an <iframe srcdoc>, so a part
that ignored the contract still shows up without breaking the others.

--index takes a TSV of `model<TAB>version<TAB>concept` rows for the top table;
without it the table lists each part's <h2> headings.
"""
import argparse, collections, html, pathlib, re, sys

CSS = """
body{background:#faf8f4;margin:0}
.hub{font:15px/1.6 -apple-system,"PingFang SC",sans-serif;color:#1f1d1a;max-width:1280px;margin:0 auto;padding:40px 24px}
.hub h1{font-size:28px;margin:0 0 6px} .hub .sub{color:#6b665e;margin:0 0 24px}
.hub table{border-collapse:collapse;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.hub td,.hub th{padding:10px 14px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
.hub th{background:#f3efe8;font-weight:600} .hub a{color:#b4541f}
.hub .note{margin:16px 0 0;color:#6b665e}
.band{border-top:6px solid #1f1d1a;margin-top:56px;padding-top:8px}
.band>h2{font:700 22px/1.3 -apple-system,"PingFang SC",sans-serif;max-width:1280px;margin:0 auto 8px;padding:0 24px}
.band>iframe{display:block;width:100%;border:0;min-height:600px}
"""
# Resize each srcdoc iframe to its content so the page scrolls as one document.
FIT_JS = """<script>
document.querySelectorAll('.band>iframe').forEach(f=>{const fit=()=>{try{f.style.height=f.contentDocument.documentElement.scrollHeight+'px'}catch(e){}};f.addEventListener('load',()=>{fit();setTimeout(fit,800)})});
</script>"""
SELECTORS = re.compile(r'(?:^|[{};])\s*([^{};@]+?)\s*\{')
KEYFRAME_STEP = re.compile(r'^(from|to|[\d.]+%)$')


def unscoped(styles, pid):
    """Selectors in the part's CSS that do not start with its .set*-<id> class."""
    styles = re.sub(r'/\*.*?\*/', '', styles, flags=re.S)
    prefix = re.compile(r'^\.set\d*-%s\b' % re.escape(pid))
    bad = []
    for group in SELECTORS.findall(styles):
        for sel in group.split(','):
            sel = sel.strip()
            if sel and not KEYFRAME_STEP.match(sel) and not prefix.match(sel):
                bad.append(sel)
    return bad


def scoped_section(src, pid):
    """Return the part's scoped <section>, or None if the contract was not followed."""
    m = re.search(r'<section\b[^>]*class="[^"]*\bset\d*-%s\b' % re.escape(pid), src)
    if not m:
        return None
    i, j = m.start(), src.rfind('</section>') + len('</section>')
    sec = src[i:j]
    if sec.count('<section') != sec.count('</section>'):
        return None
    styles = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', sec, re.S))
    bad = unscoped(styles, pid)
    if bad:
        print(f'{pid}: unscoped selectors {bad[:3]} -> iframe', file=sys.stderr)
        return None
    return sec


def headings(src):
    return [re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h2[^>]*>(.*?)</h2>', src, re.S)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--sub', default='')
    ap.add_argument('--note', default='')
    ap.add_argument('--index')
    ap.add_argument('parts', nargs='+')
    a = ap.parse_args()

    bands, rows, all_ids = [], [], collections.Counter()
    for spec in a.parts:
        path, _, label = spec.partition('=')
        p = pathlib.Path(path)
        pid = p.stem
        label = label or pid
        src = p.read_text(encoding='utf-8')
        sec = scoped_section(src, pid)
        if sec:
            body, mode = sec, 'inline'
            all_ids.update(re.findall(r'\sid="([^"]+)"', sec))
        else:
            body = '<iframe srcdoc="%s" loading="lazy"></iframe>' % html.escape(src, quote=True)
            mode = 'iframe'
        bands.append('<div class="band" id="%s"><h2>%s</h2>%s</div>' % (pid, html.escape(label), body))
        for h in headings(sec or src):
            rows.append((label, pid, h, ''))
        print(f'{pid}: {mode}, {len(body)} chars', file=sys.stderr)

    if a.index:
        rows = []
        for line in pathlib.Path(a.index).read_text(encoding='utf-8').splitlines():
            if line.strip():
                model, version, concept = (line.split('\t') + ['', ''])[:3]
                rows.append((model, model.split('-')[0], version, concept))
    has_concept = any(r[3] for r in rows)
    head = '<tr><th>模型</th><th>版本</th>%s</tr>' % ('<th>概念</th>' if has_concept else '')
    trs = ''.join('<tr><td>%s</td><td><a href="#%s">%s</a></td>%s</tr>' % (
        html.escape(m), html.escape(pid), html.escape(v), '<td>%s</td>' % html.escape(c) if has_concept else '')
        for m, pid, v, c in rows)

    page = ('<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>'
            '<div class="hub"><h1>%s</h1>%s<table>%s%s</table>%s</div>\n%s\n%s</body></html>') % (
        html.escape(a.title), CSS, html.escape(a.title),
        '<p class="sub">%s</p>' % html.escape(a.sub) if a.sub else '', head, trs,
        '<p class="note">%s</p>' % html.escape(a.note) if a.note else '',
        '\n'.join(bands), FIT_JS)
    pathlib.Path(a.out).write_text(page, encoding='utf-8')

    dup = [k for k, v in all_ids.items() if v > 1]
    if dup:
        print('warning: duplicate ids across inlined parts: ' + ', '.join(dup[:10]), file=sys.stderr)
    print(a.out)


if __name__ == '__main__':
    main()
