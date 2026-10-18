#!/usr/bin/env python3
"""Design choice server: serves ~/project/build_with_opus/design over HTTP and
records the options a reviewer picks in a design page.

GET  /  (and /index.html unless ROOT has one)  design index page (scripts/index.html)
GET  /api/designs                    every project's designs, grouped by version (JSON)
GET  /api/events?limit=300           newest version, choice and delivery events (JSON)
GET  /d/<project>/<key>              design index page (SPA; HEAD also supported)
GET  /<project>/<file>.html          static file (raw page; show users /d/... instead)
Optional <project>/_topics.json groups a project's designs into second-level topics.
POST /direction {"project", "name", "state": active|done|paused} sets a direction's state there.
POST /note   {"project", "target": <group key or version file>, "text"} keeps a note in
     <project>/_notes.json (empty text removes it); groups and versions carry it as "note".
POST /delete {"project", "key"} or {"project", "file"} moves a whole design (every version) or one
     version, with its thumb / choices / delivery / _parts, into <project>/.trash/<batch>/.
POST /restore {"project", "batch"} moves a deleted batch back.
GET  /ping                           health check; idle_left_min is measured before this ping
GET  /choices?page=<project>/<file>  latest submission for that page (or {})
POST /submit  {"page": "<project>/<file>.html", "choices": {...}, "note": "..."}
     -> writes <file>.choices.json next to the page (latest + history)

Idle exit: the server exits with code 0 after DESIGN_CHOICE_IDLE_MIN minutes
(default 120) without an active request; poll=1 does not reset the timer, 0 disables it.
"""
import fnmatch, json, os, re, signal, sys, threading, time
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
_thumb_stop = threading.Event()


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
        elif tag == "meta" and (attrs.get("name") or "").lower() in ("dc-change", "dc-why"):
            self.meta[attrs["name"].lower()] = attrs.get("content") or ""

    def handle_endtag(self, tag):
        if tag == "head":
            self.done = True
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and not self.done:
            self.title.append(data)


class FramesDone(Exception):
    pass


class FrameParser(HTMLParser):
    VOID = set("area base br col embed hr img input link meta param source track wbr".split())
    BLOCK = set("div section article aside header footer main nav figure p h1 h2 h3 ul ol table".split())

    def __init__(self):
        super().__init__()
        self.stack, self.frames, self.pending = [], [], []
        self.caption = None

    def finish_caption(self):
        if self.caption is not None:
            self.caption["item"]["cap"] = " ".join("".join(self.caption["parts"]).split())
            self.caption = None

    def check_done(self):
        if len(self.frames) == 60 and self.caption is None and not self.pending:
            raise FramesDone()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        is_cap = tag == "p" and "cap" in (attrs.get("class") or "").split()
        if self.caption is not None and tag in self.BLOCK:
            pnode = self.caption["node"]
            self.finish_caption()
            for i, n in enumerate(self.stack):
                if n is pnode:
                    del self.stack[i:]
                    break
        anchor = attrs.get("id") or None
        if anchor:
            for pending in self.pending[:]:
                if self.caption is not pending and any(n is pending["scope"] for n in self.stack):
                    pending["item"]["id"] = anchor
                    self.pending.remove(pending)
            self.check_done()
        parent = self.stack[-1] if self.stack else None
        enclosing = next((n["id"] for n in reversed(self.stack) if n["id"]), None)
        node = {"tag": tag, "id": anchor}
        if tag not in self.VOID:
            self.stack.append(node)
        if is_cap and len(self.frames) < 60:
            # a new caption in the same scope starts the next frame: earlier captions there stay unanchored
            self.pending = [p for p in self.pending if p["scope"] is not parent]
            item = {"cap": "", "id": enclosing}
            self.frames.append(item)
            self.caption = {"parts": [], "item": item, "scope": parent, "node": node}
            if not enclosing and parent is not None:
                self.pending.append(self.caption)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.caption is not None:
            self.caption["parts"].append(data)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                closing = self.stack[i:]
                if self.caption is not None and any(n is self.caption["node"] for n in closing):
                    self.finish_caption()
                self.pending = [p for p in self.pending if not any(n is p["scope"] for n in closing)]
                del self.stack[i:]
                break
        self.check_done()

    def close(self):
        super().close()
        self.finish_caption()


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
            if not parser.done:
                parser.close()
    except Exception:
        parser = HeadParser()  # malformed pages still get a cached default
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
    except FramesDone:
        pass
    except Exception:
        parser = FrameParser()
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
    return {"at": latest.get("submitted_at") or "", "items": items, "note": str(latest.get("note") or ""),
            "source": latest.get("source", ""), "n_history": len(choices_history(doc))}


def choices_history(doc):
    if "history" in doc:
        return doc["history"] if isinstance(doc["history"], list) else []
    latest = doc.get("latest")
    return [latest] if isinstance(latest, dict) and latest else []


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


DIRECTION_STATES = ("active", "done", "paused")


def load_topics(pdir):
    """<project>/_topics.json: {"topics": [{"name": "模型路由", "keys": ["model-routing*", ...]}]}.

    Second level inside a project: each design group (by key) joins the first topic
    whose glob matches; unmatched groups stay directly under the project.
    """
    doc = read_json(os.path.join(pdir, "_topics.json"))
    out = []
    for t in (doc or {}).get("topics") or []:
        if isinstance(t, dict) and t.get("name") and isinstance(t.get("keys"), list):
            out.append((str(t["name"]), [str(k) for k in t["keys"]]))
    return out


def load_notes(pdir):
    """<project>/_notes.json: {"notes": {"<group key>": "...", "<version file>.html": "..."}}."""
    notes = read_json(os.path.join(pdir, "_notes.json")).get("notes")
    return {k: v for k, v in notes.items() if isinstance(v, str)} if isinstance(notes, dict) else {}


def write_json(path, doc):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def version_files(pdir, html_name):
    """A version's html plus everything named after it: thumb, choices, delivery and the _parts dir."""
    stem = html_name[:-len(".html")]
    names = [html_name] + [stem + suf for suf in (".thumb.png", ".choices.json", ".delivery.json", "_parts")]
    return [n for n in names if os.path.exists(os.path.join(pdir, n))]


def topic_of(key, topics):
    for name, pats in topics:
        if any(fnmatch.fnmatchcase(key, pat) for pat in pats):
            return name
    return None


def list_designs():
    now = time.time()
    projects = []
    for name in sorted(os.listdir(ROOT)):
        pdir = os.path.join(ROOT, name)
        if name.startswith(".") or name.endswith("_parts") or not os.path.isdir(pdir):
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
        topics = load_topics(pdir)
        notes = load_notes(pdir)
        for key, versions in groups.items():
            for v in versions:
                v["note"] = notes.get(v["file"], "")
            versions.sort(key=version_sort_key, reverse=True)
            delivery, delivery_mtime = None, float("-inf")
            for i, v in enumerate(versions):
                if v["change"] is None and i + 1 < len(versions):
                    older = next((p for p in versions[i + 1:] if
                                  version_sort_key(p)[:2] < version_sort_key(v)[:2]), None)  # skip same-rev siblings
                    previous = older["choices"] if older else None
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
            out_groups.append({"key": key, "topic": topic_of(key, topics), "note": notes.get(key, ""),
                               "versions": versions, "attachments": [],
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
        states = read_json(os.path.join(pdir, "_topics.json")).get("states")
        projects.append({"name": name, "updated": max(stamps), "groups": out_groups, "refs": refs,
                         "states": states if isinstance(states, dict) else {}})
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
                cpath = choices_path(path)
                for entry in choices_history(read_json(cpath)):
                    if not isinstance(entry, dict):
                        continue
                    stamp = parse_time(entry.get("submitted_at"))
                    if stamp is None:
                        try:
                            stamp = os.path.getmtime(cpath)
                        except OSError:
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
        ok = super().parse_request()
        if ok and "1" not in parse_qs(urlparse(self.path).query).get("poll", []):
            _last_request[0] = time.monotonic()
        return ok

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
            return self._json(200, read_json(choices_path(html)).get("latest") or {})
        return super().do_GET()

    def set_direction_state(self):
        """POST /direction {"project", "name", "state"}: a direction (topic name, or the key of a
        design group outside any topic) is active / done / paused; kept in <project>/_topics.json."""
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._json(400, {"ok": False, "error": "bad json"})
        proj, name, state = (data.get(k) if isinstance(data, dict) else None for k in ("project", "name", "state"))
        if not (isinstance(proj, str) and isinstance(name, str) and name and state in DIRECTION_STATES):
            return self._json(400, {"ok": False, "error": "need project, name and state in " + "/".join(DIRECTION_STATES)})
        pdir = os.path.realpath(os.path.join(ROOT, proj))
        if os.path.dirname(pdir) != ROOT or not os.path.isdir(pdir):
            return self._json(400, {"ok": False, "error": "unknown project"})
        out = os.path.join(pdir, "_topics.json")
        doc = read_json(out)
        states = doc.get("states") if isinstance(doc.get("states"), dict) else {}
        if state == "active":
            states.pop(name, None)
        else:
            states[name] = state
        doc["states"] = states
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        os.replace(tmp, out)
        return self._json(200, {"ok": True, "states": states})

    def _body(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return None
        return data if isinstance(data, dict) else None

    def _same_origin(self):
        # writes that change files are only taken from the hub itself (no Origin = curl / same tab)
        origin = self.headers.get("Origin")
        return not origin or urlparse(origin).hostname in ("127.0.0.1", "localhost")

    def _project(self, data):
        proj = data.get("project")
        if not isinstance(proj, str) or not proj or proj.startswith("."):
            return None
        pdir = os.path.realpath(os.path.join(ROOT, proj))
        return pdir if os.path.dirname(pdir) == ROOT and os.path.isdir(pdir) else None

    def set_note(self):
        data = self._body()
        if data is None:
            return self._json(400, {"ok": False, "error": "bad json"})
        pdir, target, text = self._project(data), data.get("target"), data.get("text")
        if not pdir or not (isinstance(target, str) and target and "/" not in target and isinstance(text, str)):
            return self._json(400, {"ok": False, "error": "need project, target and text"})
        out = os.path.join(pdir, "_notes.json")
        doc = read_json(out)
        notes = doc.get("notes") if isinstance(doc.get("notes"), dict) else {}
        if text.strip():
            notes[target] = text.strip()
        else:
            notes.pop(target, None)
        doc["notes"] = notes
        write_json(out, doc)
        return self._json(200, {"ok": True})

    def delete_design(self):
        data = self._body()
        if data is None:
            return self._json(400, {"ok": False, "error": "bad json"})
        pdir, key, file = self._project(data), data.get("key"), data.get("file")
        if not pdir:
            return self._json(400, {"ok": False, "error": "unknown project"})
        htmls = sorted(fn for fn in os.listdir(pdir) if fn.lower().endswith(".html") and not fn.startswith(".")
                       and os.path.isfile(os.path.join(pdir, fn)))
        if isinstance(file, str) and file:
            picked = [file] if file in htmls else []
        elif isinstance(key, str) and key:
            picked = [fn for fn in htmls if parse_name(fn[:-len(".html")])[0] == key]
        else:
            picked = []
        if not picked:
            return self._json(400, {"ok": False, "error": "need key or file of an existing design"})
        batch = time.strftime("%y%m%d-%H%M%S") + "-" + (key or file[:-len(".html")])[:40].replace("/", "_")
        dest = os.path.join(pdir, ".trash", batch)
        os.makedirs(dest, exist_ok=True)
        moved = []
        for fn in picked:
            for n in version_files(pdir, fn):
                os.replace(os.path.join(pdir, n), os.path.join(dest, n))
                moved.append(n)
        return self._json(200, {"ok": True, "batch": batch, "moved": moved})

    def restore_design(self):
        data = self._body()
        if data is None:
            return self._json(400, {"ok": False, "error": "bad json"})
        pdir, batch = self._project(data), data.get("batch")
        src = os.path.join(pdir or "", ".trash", batch) if isinstance(batch, str) else ""
        if not pdir or not batch or "/" in batch or batch.startswith(".") or not os.path.isdir(src):
            return self._json(400, {"ok": False, "error": "unknown batch"})
        names = os.listdir(src)
        clash = [n for n in names if os.path.exists(os.path.join(pdir, n))]
        if clash:
            return self._json(409, {"ok": False, "error": "already exists: " + ", ".join(clash)})
        for n in names:
            os.replace(os.path.join(src, n), os.path.join(pdir, n))
        os.rmdir(src)
        return self._json(200, {"ok": True, "restored": names})

    def do_POST(self):
        route = urlparse(self.path).path
        if route in ("/direction", "/note", "/delete", "/restore") and not self._same_origin():
            return self._json(403, {"ok": False, "error": "cross-origin write refused"})
        if route == "/direction":
            return self.set_direction_state()
        if route == "/note":
            return self.set_note()
        if route == "/delete":
            return self.delete_design()
        if route == "/restore":
            return self.restore_design()
        if urlparse(self.path).path != "/submit":
            return self._json(404, {"ok": False, "error": "not found"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._json(400, {"ok": False, "error": "bad json"})
        if not isinstance(data, dict):
            return self._json(400, {"ok": False, "error": "body must be an object"})
        if not isinstance(data.get("page", ""), str) or not isinstance(data.get("note") or "", str):
            return self._json(400, {"ok": False, "error": "page and note must be strings"})
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
        doc = read_json(out)
        doc.setdefault("page", os.path.relpath(html, ROOT))
        doc.setdefault("history", choices_history(doc))
        if not isinstance(doc["history"], list):
            doc["history"] = []
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
    while not _thumb_stop.is_set():
        _thumb_signal.clear()
        try:
            make_thumbs(ROOT, limit=1, chrome=chrome)
        except OSError:
            pass
        _thumb_signal.wait(60)


if __name__ == "__main__":
    from make_thumbs import stop_all
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown, daemon=True).start())
    thumb_thread = None
    try:
        if os.environ.get("DESIGN_HUB_THUMBS", "1") != "0":
            thumb_thread = threading.Thread(target=watch_thumbs, daemon=True)
            thumb_thread.start()
        if IDLE_MIN > 0:
            threading.Thread(target=watch_idle, args=(server,), daemon=True).start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _thumb_stop.set()
        _thumb_signal.set()
        stop_all()
        if thumb_thread is not None:
            thumb_thread.join(timeout=5)
        server.server_close()
    sys.exit(0)
