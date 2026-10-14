#!/usr/bin/env python3
"""Design choice server: serves ~/project/build_with_opus/design over HTTP and
records the options a reviewer picks in a design page.

GET  /  (and /index.html unless ROOT has one)  design index page (scripts/index.html)
GET  /api/designs                    every project's designs, grouped by version (JSON)
GET  /<project>/<file>.html          static file (open designs through this URL)
GET  /ping                           health check; idle_left_min is measured before this ping
GET  /choices?page=<project>/<file>  latest submission for that page (or {})
POST /submit  {"page": "<project>/<file>.html", "choices": {...}, "note": "..."}
     -> writes <file>.choices.json next to the page (latest + history)

Idle exit: the server exits with code 0 after DESIGN_CHOICE_IDLE_MIN minutes
(default 120) without any request; every request resets the timer, 0 disables it.
"""
import html as htmllib, json, os, re, sys, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

ROOT_LINK = os.path.expanduser("~/project/build_with_opus/design")  # symlink to the SSD home
ROOT = os.path.realpath(ROOT_LINK)
PORT = int(os.environ.get("DESIGN_CHOICE_PORT", "47321"))
IDLE_MIN = float(os.environ.get("DESIGN_CHOICE_IDLE_MIN", "120"))
INDEX = os.path.join(os.path.dirname(os.path.realpath(__file__)), "index.html")

_last_request = [time.monotonic()]


def idle_left_min():
    if IDLE_MIN <= 0:
        return None
    return max(0.0, IDLE_MIN - (time.monotonic() - _last_request[0]) / 60)


def resolve_page(page):
    """Map a page reference (relative path, URL path or file:// path) to an html file under ROOT."""
    page = unquote(page or "").split("?")[0].split("#")[0]
    if page.startswith("file://"):
        page = page[len("file://"):]
    for prefix in (ROOT, ROOT_LINK):
        if page.startswith(prefix + os.sep):
            page = page[len(prefix):]
            break
    path = os.path.realpath(os.path.join(ROOT, page.lstrip("/")))
    if not path.startswith(ROOT + os.sep) or not path.endswith(".html") or not os.path.isfile(path):
        return None
    return path


def choices_path(html_path):
    return html_path[: -len(".html")] + ".choices.json"


# ---- design index -----------------------------------------------------------

DATE_RE = re.compile(r"^(\d{6})_(.+)$")
REV_RE = re.compile(r"^(.+?)[-_]([rv])(\d+)$", re.I)
MODEL_RE = re.compile(r"^(.+?)-(astra|opus|fable|sonnet|haiku|sol|luna|grok|codex|gemini)$", re.I)


def parse_name(stem):
    """Split '<YYMMDD>_<name>[-rN|_rN|-vN][-<model>]' into (group key, date, rev, model).

    Only a 6-digit date prefix, a trailing r/v + number and a known model name are
    stripped; anything else stays in the key, so unsure names form their own group.
    """
    date, rest = None, stem
    m = DATE_RE.match(stem)
    if m:
        date, rest = m.groups()
    rev = model = None
    for _ in range(2):  # suffixes may come in either order: -r2-astra / -astra-r2
        m = REV_RE.match(rest)
        if m and rev is None:
            rest, rev = m.group(1), m.group(2).lower() + m.group(3)
            continue
        m = MODEL_RE.match(rest)
        if m and model is None:
            rest, model = m.group(1), m.group(2).lower()
            continue
        break
    return rest, date, rev, model


_title_cache = {}


def page_title(path, mtime):
    hit = _title_cache.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    title = ""
    try:
        with open(path, "rb") as f:
            head = f.read(65536).decode("utf-8", "ignore")
        m = re.search(r"<title[^>]*>(.*?)</title>", head, re.I | re.S)
        if m:
            title = " ".join(htmllib.unescape(m.group(1)).split())
    except OSError:
        pass
    _title_cache[path] = (mtime, title)
    return title


def choices_summary(html_path):
    """Latest submission as {at, items: [{title, picked}], note}, or None."""
    try:
        with open(choices_path(html_path), encoding="utf-8") as f:
            latest = json.load(f).get("latest") or {}
    except (OSError, ValueError, AttributeError):
        return None
    if not isinstance(latest, dict) or not latest:
        return None
    choices = latest.get("choices")
    if not isinstance(choices, dict):  # older hand-written files keep choices at the top level
        choices = {k: v for k, v in latest.items() if k not in ("submitted_at", "note", "choices")}
    items = []
    for key, val in choices.items():
        title, picked = key, val
        if isinstance(val, dict):
            title, picked = val.get("title") or key, val.get("picked")
        if isinstance(picked, list):
            picked = "、".join(str(p) for p in picked)
        items.append({"title": str(title), "picked": "" if picked is None else str(picked)})
    return {"at": latest.get("submitted_at") or "", "items": items, "note": str(latest.get("note") or "")}


def version_sort_key(v):
    rev = int(v["rev"][1:]) if v["rev"] else 0
    return (v["date"] or "", rev, v["mtime"])


def list_designs():
    projects = []
    for name in sorted(os.listdir(ROOT)):
        pdir = os.path.join(ROOT, name)
        if name.startswith(".") or not os.path.isdir(pdir):
            continue
        groups, pngs = {}, []
        for fn in os.listdir(pdir):
            path = os.path.join(pdir, fn)
            if fn.startswith(".") or not os.path.isfile(path):
                continue
            stem, ext = os.path.splitext(fn)
            ext = ext.lower()
            if ext not in (".html", ".png"):
                continue
            mtime = os.path.getmtime(path)
            key, date, rev, model = parse_name(stem)
            item = {"file": fn, "path": name + "/" + fn, "mtime": mtime, "date": date,
                    "rev": rev, "model": model, "key": key}
            if ext == ".png":
                pngs.append(item)
                continue
            item["title"] = page_title(path, mtime)
            item["choices"] = choices_summary(path)
            groups.setdefault(key, []).append(item)
        out_groups = []
        for key, versions in groups.items():
            versions.sort(key=version_sort_key, reverse=True)
            out_groups.append({"key": key, "versions": versions, "attachments": [],
                               "updated": max(v["mtime"] for v in versions)})
        by_key = {g["key"]: g for g in out_groups}
        refs = []
        for p in sorted(pngs, key=lambda p: p["mtime"], reverse=True):
            # a png joins a group only when its stem normalizes to the same key
            (by_key[p["key"]]["attachments"] if p["key"] in by_key else refs).append(p)
        out_groups.sort(key=lambda g: g["updated"], reverse=True)
        if not out_groups and not refs:
            continue
        stamps = [g["updated"] for g in out_groups] + [p["mtime"] for p in refs]
        projects.append({"name": name, "updated": max(stamps), "groups": out_groups, "refs": refs})
    projects.sort(key=lambda p: p["updated"], reverse=True)
    return {"root": ROOT, "generated_at": time.time(), "projects": projects}


# ---- http -------------------------------------------------------------------

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def parse_request(self):
        self.idle_left_before = idle_left_min()
        _last_request[0] = time.monotonic()
        return super().parse_request()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _index(self):
        try:
            with open(INDEX, "rb") as f:
                body = f.read()
        except OSError:
            return self._json(500, {"ok": False, "error": "index.html missing next to choice_server.py"})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_HEAD(self):
        path = urlparse(self.path).path
        if path == "/" or (path == "/index.html" and not os.path.isfile(os.path.join(ROOT, "index.html"))):
            return self._index()
        return super().do_HEAD()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or (url.path == "/index.html" and not os.path.isfile(os.path.join(ROOT, "index.html"))):
            return self._index()
        if url.path == "/api/designs":
            return self._json(200, list_designs())
        if url.path == "/ping":
            left = self.idle_left_before
            return self._json(200, {"ok": True, "root": ROOT, "idle_min": IDLE_MIN,
                                    "idle_left_min": None if left is None else round(left, 1)})
        if url.path == "/choices":
            html = resolve_page(parse_qs(url.query).get("page", [""])[0])
            if not html:
                return self._json(404, {"ok": False, "error": "page not found"})
            try:
                with open(choices_path(html), encoding="utf-8") as f:
                    return self._json(200, json.load(f).get("latest") or {})
            except FileNotFoundError:
                return self._json(200, {})
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/submit":
            return self._json(404, {"ok": False, "error": "not found"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._json(400, {"ok": False, "error": "bad json"})
        html = resolve_page(data.get("page", ""))
        if not html:
            return self._json(400, {"ok": False, "error": "page must be an existing .html under " + ROOT})
        entry = {
            "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "choices": data.get("choices") or {},
            "note": (data.get("note") or "").strip(),
        }
        out = choices_path(html)
        try:
            with open(out, encoding="utf-8") as f:
                doc = json.load(f)
        except (FileNotFoundError, ValueError):
            doc = {"page": os.path.relpath(html, ROOT), "history": []}
        doc["latest"] = entry
        doc["history"].append(entry)
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        os.replace(tmp, out)
        return self._json(200, {"ok": True, "file": out})

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % args))


def watch_idle(server):
    while idle_left_min() > 0:
        time.sleep(min(10.0, IDLE_MIN * 60 / 6))
    sys.stderr.write("%s idle for %g min, exiting\n" % (time.strftime("%H:%M:%S"), IDLE_MIN))
    server.shutdown()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    if IDLE_MIN > 0:
        threading.Thread(target=watch_idle, args=(server,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    sys.exit(0)
