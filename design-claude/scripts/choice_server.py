#!/usr/bin/env python3
"""Design choice server: serves ~/project/build_with_opus/design over HTTP and
records the options a reviewer picks in a design page.

GET  /  (and /index.html unless ROOT has one)  design index page (scripts/index.html)
GET  /api/designs                    every project's designs, grouped by version (JSON)
GET  /api/events?limit=300           newest version, choice and delivery events (JSON)
GET  /d/<project>/<key>              design index page (SPA; HEAD also supported)
GET  /<project>/<file>.html          static file (open designs through this URL)
GET  /ping                           health check; idle_left_min is measured before this ping
GET  /choices?page=<project>/<file>  latest submission for that page (or {})
POST /submit  {"page": "<project>/<file>.html", "choices": {...}, "note": "..."}
     -> writes <file>.choices.json next to the page (latest + history)

Idle exit: the server exits with code 0 after DESIGN_CHOICE_IDLE_MIN minutes
(default 120) without any request; every request resets the timer, 0 disables it.
"""
import json, os, re, sys, threading, time
from datetime import datetime
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

ROOT_LINK = os.path.expanduser("~/project/build_with_opus/design")  # symlink to the SSD home
ROOT = os.path.realpath(os.environ.get("DESIGN_CHOICE_ROOT") or ROOT_LINK)
PORT = int(os.environ.get("DESIGN_CHOICE_PORT", "47321"))
IDLE_MIN = float(os.environ.get("DESIGN_CHOICE_IDLE_MIN", "120"))
PENDING_DAYS = float(os.environ.get("DESIGN_HUB_PENDING_DAYS", "3"))
INDEX = os.path.join(os.path.dirname(os.path.realpath(__file__)), "index.html")

_last_request = [time.monotonic()]
_thumb_signal = threading.Event()


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
_frames_cache = {}


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.done, self.in_title = False, False
        self.title, self.meta = [], {}

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs = dict(attrs)
        if tag == "body":
            self.done = True
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs.get("name", "").lower() in ("dc-change", "dc-why"):
            self.meta[attrs["name"].lower()] = attrs.get("content") or ""

    def handle_endtag(self, tag):
        if tag == "head":
            self.done = True
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and not self.done:
            self.title.append(data)


class FrameParser(HTMLParser):
    VOID = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self):
        super().__init__()
        self.stack, self.frames = [], []
        self.caption = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        anchor = attrs.get("id") or None
        if anchor:
            for node in self.stack:
                node["last_id"] = anchor
        node = {"tag": tag, "id": anchor, "last_id": None,
                "frame": "frame" in (attrs.get("class") or "").split()}
        if tag not in self.VOID:
            self.stack.append(node)
        if tag == "p" and "cap" in (attrs.get("class") or "").split() and len(self.frames) < 60:
            enclosing = next((n["id"] for n in reversed(self.stack) if n["id"]), None)
            parents = self.stack[:-1]
            scope = next((n for n in reversed(parents) if n["frame"]),
                         parents[-1] if parents else None)
            preceding = scope["last_id"] if scope and scope["tag"] not in ("html", "body") else None
            self.caption = {"parts": [], "id": enclosing or preceding}

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.caption is not None:
            self.caption["parts"].append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.caption is not None:
            self.frames.append({"cap": " ".join("".join(self.caption["parts"]).split()),
                                "id": self.caption["id"]})
            self.caption = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break


def page_metadata(path, mtime):
    hit = _title_cache.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    parser = HeadParser()
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            while not parser.done:
                chunk = f.read(16384)
                if not chunk:
                    break
                parser.feed(chunk)
    except OSError:
        pass
    change = None
    if parser.meta:
        change = {"what": parser.meta.get("dc-change", ""),
                  "why": parser.meta.get("dc-why", ""), "src": "meta"}
    result = {"title": " ".join("".join(parser.title).split()), "change": change}
    _title_cache[path] = (mtime, result)
    return result


def page_title(path, mtime):
    return page_metadata(path, mtime)["title"]


def page_frames(path, mtime):
    hit = _frames_cache.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    parser = FrameParser()
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for chunk in iter(lambda: f.read(65536), ""):
                parser.feed(chunk)
        parser.close()
    except OSError:
        pass
    _frames_cache[path] = (mtime, parser.frames)
    return parser.frames


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        return doc if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def parse_time(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value if float("-inf") < value < float("inf") else None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).timestamp()
        except (ValueError, OverflowError, OSError):
            pass
    return None


def delivery_path(html_path):
    return html_path[:-len(".html")] + ".delivery.json"


def delivery_summary(html_path):
    doc = read_json(delivery_path(html_path))
    if not doc:
        return None
    return {**{k: doc.get(k) for k in ("bot", "task", "at", "state")},
            "at_ts": parse_time(doc.get("at")), "file": os.path.basename(html_path)}


def choices_summary(html_path):
    """Latest submission as {at, items: [{title, picked}], note}, or None."""
    doc = read_json(choices_path(html_path))
    latest = doc.get("latest") or {}
    if not isinstance(latest, dict) or not latest:
        return None
    choices = latest.get("choices")
    if not isinstance(choices, dict):  # older hand-written files keep choices at the top level
        choices = {k: v for k, v in latest.items() if k not in ("submitted_at", "note", "choices", "source")}
    items = []
    for key, val in choices.items():
        title, picked = key, val
        if isinstance(val, dict):
            title, picked = val.get("title") or key, val.get("picked")
        if isinstance(picked, list):
            picked = "、".join(str(p) for p in picked)
        items.append({"title": str(title), "picked": "" if picked is None else str(picked)})
    history = doc.get("history")
    return {"at": latest.get("submitted_at") or "", "items": items, "note": str(latest.get("note") or ""),
            "source": latest.get("source", ""), "n_history": len(history) if isinstance(history, list) else 0}


def version_date(date, mtime):
    if date:
        try:
            return datetime.strptime("20" + date, "%Y%m%d").strftime("%Y-%m-%d"), "name"
        except ValueError:
            pass
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d"), "mtime"


def version_sort_key(v):
    rev = int(v["rev"][1:]) if v["rev"] else 0
    return (v["date"] or "", rev, v["mtime"])


def list_designs():
    now = time.time()
    projects = []
    for name in sorted(os.listdir(ROOT)):
        pdir = os.path.join(ROOT, name)
        if name.startswith(".") or not os.path.isdir(pdir):
            continue
        groups, pngs = {}, []
        for fn in os.listdir(pdir):
            path = os.path.join(pdir, fn)
            if fn.startswith(".") or fn.lower().endswith(".thumb.png") or not os.path.isfile(path):
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
            item["date"], item["date_src"] = version_date(date, mtime)
            item.update(page_metadata(path, mtime))
            item["frames"] = page_frames(path, mtime)
            item["choices"] = choices_summary(path)
            thumb = path[:-len(".html")] + ".thumb.png"
            item["thumb"] = name + "/" + os.path.basename(thumb) if os.path.isfile(thumb) else None
            item["thumb_mtime"] = os.path.getmtime(thumb) if item["thumb"] else None
            groups.setdefault(key, []).append(item)
        out_groups = []
        for key, versions in groups.items():
            versions.sort(key=version_sort_key, reverse=True)
            delivery, delivery_mtime = None, float("-inf")
            for i, v in enumerate(versions):
                if v["change"] is None and i + 1 < len(versions):
                    previous = versions[i + 1]["choices"]
                    if previous and previous["note"]:
                        v["change"] = {"what": "", "why": previous["note"], "src": "note"}
                path = os.path.join(ROOT, v["path"])
                d = delivery_summary(path)
                if d:
                    try:
                        stamp = os.path.getmtime(delivery_path(path))
                    except OSError:
                        continue
                    if stamp > delivery_mtime:
                        delivery, delivery_mtime = d, stamp
            latest = versions[0]
            if delivery and (delivery["file"] == latest["file"] or
                             (delivery["at_ts"] is not None and delivery["at_ts"] >= latest["mtime"])):
                status = "delivered"
            elif latest["choices"]:
                status = "submitted"
            elif now - latest["mtime"] < PENDING_DAYS * 86400:
                status = "pending"
            else:
                status = "idle"
            out_groups.append({"key": key, "versions": versions, "attachments": [],
                               "updated": max(v["mtime"] for v in versions),
                               "date": latest["date"], "status": status, "delivery": delivery})
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
    _thumb_signal.set()
    return {"root": ROOT, "generated_at": now, "pending_days": PENDING_DAYS, "projects": projects}


def list_events(limit=300):
    events = []
    for project in list_designs()["projects"]:
        for group in project["groups"]:
            for v in group["versions"]:
                base = {"project": project["name"], "key": group["key"], "file": v["file"],
                        "rev": v["rev"], "title": v["title"]}
                events.append({**base, "t": v["mtime"], "kind": "version"})
                path = os.path.join(ROOT, v["path"])
                history = read_json(choices_path(path)).get("history", [])
                for entry in history if isinstance(history, list) else []:
                    if not isinstance(entry, dict):
                        continue
                    stamp = parse_time(entry.get("submitted_at"))
                    if stamp is None:
                        continue
                    choices = entry.get("choices") or {}
                    events.append({**base, "t": stamp, "kind": "choices", "note": entry.get("note") or "",
                                   "n_items": len(choices) if isinstance(choices, dict) else 0,
                                   "source": entry.get("source", "")})
                d = delivery_summary(path)
                if d:
                    try:
                        stamp = d["at_ts"] if d["at_ts"] is not None else os.path.getmtime(delivery_path(path))
                    except OSError:
                        continue
                    events.append({**base, "t": stamp, "kind": "delivery",
                                   **{k: d[k] for k in ("bot", "task", "state")}})
    events.sort(key=lambda e: e["t"], reverse=True)
    return {"generated_at": time.time(), "events": events[:max(0, limit)]}


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
        if path == "/" or path.startswith("/d/") or (path == "/index.html" and not os.path.isfile(os.path.join(ROOT, "index.html"))):
            return self._index()
        return super().do_HEAD()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or url.path.startswith("/d/") or (url.path == "/index.html" and not os.path.isfile(os.path.join(ROOT, "index.html"))):
            return self._index()
        if url.path == "/api/designs":
            return self._json(200, list_designs())
        if url.path == "/api/events":
            try:
                limit = int(parse_qs(url.query).get("limit", ["300"])[0])
            except ValueError:
                return self._json(400, {"ok": False, "error": "limit must be an integer"})
            return self._json(200, list_events(limit))
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
        if "source" in data:
            entry["source"] = data["source"]
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


def watch_thumbs():
    from make_thumbs import find_chrome, make_thumbs
    chrome = find_chrome()
    if not chrome:
        return
    while True:
        _thumb_signal.clear()
        try:
            make_thumbs(ROOT, limit=1, chrome=chrome)
        except OSError:
            pass
        _thumb_signal.wait(60)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    if os.environ.get("DESIGN_HUB_THUMBS", "1") != "0":
        threading.Thread(target=watch_thumbs, daemon=True).start()
    if IDLE_MIN > 0:
        threading.Thread(target=watch_idle, args=(server,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    sys.exit(0)
