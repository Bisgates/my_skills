#!/usr/bin/env python3
"""Isolated HTTP contract tests; no real Chrome or running design service is used."""
import builtins, contextlib, io, json, os, signal, socket, subprocess, sys, tempfile, time, unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch

sys.dont_write_bytecode = True
import make_thumbs
import choice_server

SCRIPTS = Path(__file__).resolve().parent
PNG = b"\x89PNG\r\n\x1a\n" + b"test payload" + b"\x00\x00\x00\x00IEND\xaeB`\x82"


def fake_chrome(root, body):
    path = Path(root) / "fake-chrome"
    path.write_text("#!" + sys.executable + "\nimport os, signal, subprocess, sys, time\nfrom pathlib import Path\n" +
                    "shot = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--screenshot='))\n" + body)
    path.chmod(0o755)
    return str(path)


def group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.project = self.root / "demo"
        self.project.mkdir()
        self.now = time.time()
        self.fixtures()
        self.start_server()

    def start_server(self, **overrides):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        self.assertNotEqual(port, 47321)
        self.base = "http://127.0.0.1:%s" % port
        env = dict(os.environ, DESIGN_CHOICE_ROOT=str(self.root), DESIGN_CHOICE_PORT=str(port),
                   DESIGN_HUB_THUMBS="0", DESIGN_CHOICE_IDLE_MIN="0", PYTHONDONTWRITEBYTECODE="1")
        env.pop("DESIGN_HUB_PENDING_DAYS", None)
        env.pop("DESIGN_HUB_CHROME", None)
        env.update(overrides)
        self.proc = subprocess.Popen([sys.executable, str(SCRIPTS / "choice_server.py")],
                                     env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self.stop)
        for _ in range(100):
            try:
                self.get("/ping")
                break
            except OSError:
                if self.proc.poll() is not None:
                    self.fail("test server exited with %s" % self.proc.returncode)
                time.sleep(.02)
        else:
            self.fail("test server did not start")

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        self.proc.wait(timeout=5)

    def html(self, name, body="", head="", mtime=None):
        path = self.project / name
        path.write_text("<!doctype html><html><head><title>Design &amp; test</title>" + head +
                        "</head><body>" + body + "</body></html>", encoding="utf-8")
        stamp = self.now if mtime is None else mtime
        os.utime(path, (stamp, stamp))
        return path

    def sidecar(self, name, suffix, doc, mtime=None):
        path = self.project / (name[:-5] + suffix)
        path.write_text(json.dumps(doc), encoding="utf-8")
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path

    def choices(self, name, note="feedback", source="reviewer"):
        entries = [{"submitted_at": datetime.fromtimestamp(self.now - age).strftime("%Y-%m-%d %H:%M:%S"),
                    "choices": {"layout": {"title": "Layout", "picked": ["A", "B"]}},
                    "note": note, "source": source} for age in (100, 50)]
        return self.sidecar(name, ".choices.json", {"latest": entries[-1], "history": entries})

    def fixtures(self):
        self.html("261014_named-r2-opus.html")
        self.html("plain.html", mtime=1650000000)
        self.html("991332_invalid.html")
        self.html("261014_pending-r3.html", mtime=self.now - 30)
        self.choices("261014_pending-r3.html", note="r3 feedback")
        self.html("261014_pending-r4.html", mtime=self.now - 20)
        self.html("261014_submitted.html")
        self.choices("261014_submitted.html")
        self.html("261014_idle.html", mtime=self.now - 4 * 86400)
        self.html("261014_delivered.html", mtime=self.now - 4 * 86400)
        self.choices("261014_delivered.html")
        self.sidecar("261014_delivered.html", ".delivery.json",
                     {"bot": "builder", "task": "Tsk1", "at": self.now - 5, "state": "merged"})
        self.html("261014_handoff-r1.html", mtime=self.now - 40)
        self.html("261014_handoff-r2.html", mtime=self.now - 20)
        self.sidecar("261014_handoff-r1.html", ".delivery.json",
                     {"bot": "builder", "task": "Tsk2", "at": datetime.fromtimestamp(self.now, timezone.utc).isoformat(),
                      "state": "developing"})
        self.html("261014_local.html")
        self.sidecar("261014_local.html", ".delivery.json",
                     {"bot": "builder", "task": "Tsk3", "at": datetime.fromtimestamp(self.now).strftime("%Y-%m-%d %H:%M:%S"),
                      "state": "merged"})
        self.html("261014_stale-r1.html", mtime=self.now - 40)
        self.html("261014_stale-r2.html", mtime=self.now - 20)
        self.sidecar("261014_stale-r1.html", ".delivery.json",
                     {"bot": "builder", "task": "old", "at": self.now - 60, "state": "merged"})
        self.html("261014_meta-r1.html", mtime=self.now - 10)
        self.choices("261014_meta-r1.html", note="older note")
        self.html("261014_meta-r2.html", head="<meta content='Changed &amp; polished' name='dc-change'>"
                  "<meta NAME='dc-why' content='Because feedback'>")
        self.html("261014_empty-meta.html", head="<meta name='dc-why' content=''>")
        self.html("261014_frames.html", body=" " * 2000000 +
                  "<div id='outer'><section id='inner'><p class='small cap'>One <b>&amp; two</b></p></section></div>"
                  "<div class='frame'><p class='cap'>Before</p><div class='frame-row'><div id='following' data-frame></div></div></div>"
                  "<div class='frame'><p class='cap'>No anchor</p></div>")
        self.html("261014_cap-limit.html", body="".join("<div id='f%s'><p class='cap'>%s</p></div>" % (i, i) for i in range(65)))
        (self.project / "261014_named-r2-opus.thumb.png").write_bytes(b"thumbnail")
        (self.project / "orphan.thumb.png").write_bytes(b"thumbnail")
        (self.project / "261014_named.png").write_bytes(b"reference")
        (self.project / "reference.png").write_bytes(b"reference")
        parts = self.project / "ignored_parts"
        parts.mkdir()
        (parts / "nested.html").write_text("ignored")

    def get(self, path):
        with urlopen(self.base + path, timeout=5) as response:
            return json.load(response)

    def groups(self):
        doc = self.get("/api/designs")
        self.assertEqual(doc["root"], str(self.root))
        self.assertEqual(doc["pending_days"], 3)
        return {g["key"]: g for g in doc["projects"][0]["groups"]}

    def test_dates_and_existing_fields(self):
        groups = self.groups()
        named = groups["named"]["versions"][0]
        self.assertEqual((named["date"], named["date_src"]), ("2026-10-14", "name"))
        self.assertEqual((named["rev"], named["model"], named["title"]), ("r2", "opus", "Design & test"))
        plain = groups["plain"]["versions"][0]
        self.assertEqual((plain["date"], plain["date_src"]),
                         (datetime.fromtimestamp(1650000000).strftime("%Y-%m-%d"), "mtime"))
        self.assertEqual(groups["invalid"]["versions"][0]["date_src"], "mtime")
        for g in groups.values():
            self.assertEqual(g["date"], g["versions"][0]["date"])
            for v in g["versions"]:
                self.assertRegex(v["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_four_statuses_and_new_revision(self):
        groups = self.groups()
        for key in ("pending", "submitted", "delivered", "idle"):
            self.assertEqual(groups[key]["status"], key)
        self.assertEqual(groups["pending"]["versions"][0]["rev"], "r4")
        self.assertIsNone(groups["pending"]["versions"][0]["choices"])
        self.assertIsNotNone(groups["pending"]["versions"][1]["choices"])
        self.assertEqual(groups["handoff"]["status"], "delivered")
        self.assertEqual(groups["stale"]["status"], "pending")

    def test_change_and_choices_summary(self):
        groups = self.groups()
        self.assertEqual(groups["meta"]["versions"][0]["change"],
                         {"what": "Changed & polished", "why": "Because feedback", "src": "meta"})
        self.assertEqual(groups["pending"]["versions"][0]["change"],
                         {"what": "", "why": "r3 feedback", "src": "note"})
        self.assertIsNone(groups["pending"]["versions"][1]["change"])
        self.assertEqual(groups["empty-meta"]["versions"][0]["change"], {"what": "", "why": "", "src": "meta"})
        choices = groups["submitted"]["versions"][0]["choices"]
        self.assertEqual((choices["source"], choices["n_history"]), ("reviewer", 2))
        self.assertEqual(choices["items"], [{"title": "Layout", "picked": "A、B"}])
        self.choices("261014_submitted.html", source="")
        path = self.project / "261014_submitted.choices.json"
        doc = json.loads(path.read_text())
        del doc["latest"]["source"]
        path.write_text(json.dumps(doc))
        self.assertEqual(self.groups()["submitted"]["versions"][0]["choices"]["source"], "")

    def test_frames_full_file_scope_and_limit(self):
        groups = self.groups()
        self.assertEqual(groups["frames"]["versions"][0]["frames"],
                         [{"cap": "One & two", "id": "inner"}, {"cap": "Before", "id": "following"},
                          {"cap": "No anchor", "id": None}])
        frames = groups["cap-limit"]["versions"][0]["frames"]
        self.assertEqual(len(frames), 60)
        self.assertEqual(frames[-1], {"cap": "59", "id": "f59"})

    def test_html_cache_invalidation(self):
        before = self.groups()["frames"]["versions"][0]
        self.assertEqual(len(before["frames"]), 3)
        self.html("261014_frames.html", head="<meta name='dc-change' content='New'>",
                  body="<div id='changed'><p class='cap'>Changed</p></div>", mtime=self.now + 2)
        after = self.groups()["frames"]["versions"][0]
        self.assertEqual(after["frames"], [{"cap": "Changed", "id": "changed"}])
        self.assertEqual(after["change"]["what"], "New")

    def test_delivery_times_and_newest_sidecar(self):
        groups = self.groups()
        self.assertEqual(groups["delivered"]["delivery"]["at_ts"], self.now - 5)
        for key in ("local", "handoff"):
            self.assertAlmostEqual(groups[key]["delivery"]["at_ts"], self.now, delta=1)
        self.assertEqual(groups["handoff"]["delivery"]["file"], "261014_handoff-r1.html")
        self.sidecar("261014_handoff-r2.html", ".delivery.json",
                     {"bot": "new", "task": "Tsk4", "at": "unparseable", "state": "merged"}, self.now + 20)
        delivery = self.groups()["handoff"]["delivery"]
        self.assertEqual((delivery["bot"], delivery["at"], delivery["at_ts"]), ("new", "unparseable", None))
        self.assertEqual(self.groups()["handoff"]["status"], "delivered")

    def test_thumbs_not_refs_or_attachments(self):
        doc = self.get("/api/designs")
        groups = {g["key"]: g for g in doc["projects"][0]["groups"]}
        named = groups["named"]["versions"][0]
        self.assertEqual(named["thumb"], "demo/261014_named-r2-opus.thumb.png")
        self.assertEqual(named["thumb_mtime"], (self.project / "261014_named-r2-opus.thumb.png").stat().st_mtime)
        self.assertIsNone(groups["plain"]["versions"][0]["thumb"])
        self.assertIsNone(groups["plain"]["versions"][0]["thumb_mtime"])
        self.assertEqual([p["file"] for p in groups["named"]["attachments"]], ["261014_named.png"])
        self.assertEqual([p["file"] for p in doc["projects"][0]["refs"]], ["reference.png"])
        with urlopen(self.base + "/" + named["thumb"]) as response:
            self.assertEqual(response.read(), b"thumbnail")

    def test_events_descending_kinds_and_limit(self):
        events = self.get("/api/events")["events"]
        self.assertEqual({e["kind"] for e in events}, {"version", "choices", "delivery"})
        self.assertEqual([e["t"] for e in events], sorted((e["t"] for e in events), reverse=True))
        choices = [e for e in events if e["kind"] == "choices" and e["key"] == "submitted"]
        self.assertEqual(len(choices), 2)
        self.assertEqual((choices[0]["note"], choices[0]["n_items"], choices[0]["source"]), ("feedback", 1, "reviewer"))
        self.assertEqual({e["task"] for e in events if e["kind"] == "delivery"}, {"Tsk1", "Tsk2", "Tsk3", "old"})
        self.assertEqual(self.get("/api/events?limit=2")["events"], events[:2])
        self.assertEqual(self.get("/api/events?limit=0")["events"], [])
        for e in events:
            self.assertTrue({"t", "kind", "project", "key", "file", "rev", "title"} <= e.keys())

    def test_spa_static_and_ping(self):
        index = (SCRIPTS / "index.html").read_bytes()
        with urlopen(self.base + "/d/x/y?v=r4") as response:
            self.assertEqual(response.read(), index)
        with urlopen(Request(self.base + "/d/x/y", method="HEAD")) as response:
            self.assertEqual(int(response.headers["Content-Length"]), len(index))
            self.assertEqual(response.read(), b"")
        with urlopen(self.base + "/demo/plain.html") as response:
            self.assertEqual(response.read(), (self.project / "plain.html").read_bytes())
        ping = self.get("/ping")
        self.assertTrue(ping["ok"])
        self.assertIsNone(ping["idle_left_min"])

    def test_submit_history_choices_and_root_link(self):
        name = "261014_named-r2-opus.html"
        self.assertEqual(self.get("/choices?page=demo/" + name), {})
        refs = ["demo/" + name, "file://" + str(self.project / name),
                str(Path.home() / "project/build_with_opus/design/demo" / name)]
        for i, ref in enumerate(refs):
            payload = {"page": ref, "choices": {"layout": "A"}, "note": " note %s " % i, "source": "hub"}
            request = Request(self.base + "/submit", data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json"})
            with urlopen(request) as response:
                self.assertTrue(json.load(response)["ok"])
        doc = json.loads((self.project / "261014_named-r2-opus.choices.json").read_text())
        self.assertEqual(len(doc["history"]), 3)
        self.assertEqual(doc["latest"], doc["history"][-1])
        self.assertEqual(doc["latest"]["note"], "note 2")
        self.assertEqual(self.get("/choices?page=" + quote(refs[1])), doc["latest"])
        self.assertEqual(self.groups()["named"]["status"], "submitted")

    def test_pending_days_env(self):
        self.stop()
        self.start_server(DESIGN_HUB_PENDING_DAYS="5")
        doc = self.get("/api/designs")
        self.assertEqual(doc["pending_days"], 5)
        idle = next(g for g in doc["projects"][0]["groups"] if g["key"] == "idle")
        self.assertEqual(idle["status"], "pending")

    def test_idle_exit(self):
        self.stop()
        self.start_server(DESIGN_CHOICE_IDLE_MIN="0.015")
        ping = self.get("/ping")
        self.assertEqual(ping["idle_min"], .015)
        self.assertIsNotNone(ping["idle_left_min"])
        self.assertEqual(self.proc.wait(timeout=4), 0)

    def test_poll_does_not_extend_idle(self):
        self.stop()
        self.start_server(DESIGN_CHOICE_IDLE_MIN="0.02")
        started, count = time.monotonic(), 0
        while self.proc.poll() is None and time.monotonic() - started < 3:
            try:
                self.get("/api/designs?poll=1" if count % 2 else "/api/events?poll=1")
                count += 1
            except OSError:
                break
            time.sleep(.1)
        self.assertGreater(count, 3)
        self.assertEqual(self.proc.wait(timeout=1), 0)
        self.assertLess(time.monotonic() - started, 2.5)

    def test_bad_html_and_missing_meta_name(self):
        self.html("261014_bad-head.html", head="<![bogus[")
        self.html("261014_bad-body.html", body="<![bogus[")
        self.html("261014_meta-name.html", head="<meta name content='ignored'><meta name='dc-change' content='safe'>")
        for _ in range(2):
            groups = self.groups()
            self.assertIsInstance(groups["bad-head"]["versions"][0]["title"], str)
            self.assertEqual(groups["bad-body"]["versions"][0]["frames"], [])
            self.assertEqual(groups["meta-name"]["versions"][0]["change"]["what"], "safe")
            self.assertTrue(self.get("/api/events")["events"])

    def test_latest_only_choices_and_timestamp_fallback(self):
        latest = {"choices": {"layout": "A"}, "note": "latest only", "source": "hub",
                  "submitted_at": "2026-10-14T11:40:52"}
        cpath = self.sidecar("261014_submitted.html", ".choices.json", {"latest": latest}, self.now - 123)
        for stamp in ("2026-10-14T11:40:52", "", "broken"):
            latest["submitted_at"] = stamp
            cpath.write_text(json.dumps({"latest": latest}))
            os.utime(cpath, (self.now - 123, self.now - 123))
            self.assertEqual(self.groups()["submitted"]["versions"][0]["choices"]["n_history"], 1)
            events = [e for e in self.get("/api/events")["events"] if e["kind"] == "choices" and e["key"] == "submitted"]
            self.assertEqual(len(events), 1)
            expected = datetime.fromisoformat(stamp).timestamp() if "T" in stamp else self.now - 123
            self.assertEqual(events[0]["t"], expected)
            self.assertEqual(events[0]["note"], "latest only")

    def test_note_skips_same_rev_siblings(self):
        self.html("261014_pending-r4-astra.html", mtime=self.now)
        self.choices("261014_pending-r4.html", note="same revision")
        newest = self.groups()["pending"]["versions"][0]
        self.assertEqual(newest["model"], "astra")
        self.assertEqual(newest["change"]["why"], "r3 feedback")

    def test_note_fallback_without_revs_uses_older_date(self):
        self.html("261007_plain.html", mtime=self.now - 5000)
        self.choices("261007_plain.html", note="make it blue")
        self.html("261009_plain.html", mtime=self.now - 4000)
        newest = self.groups()["plain"]["versions"][0]
        self.assertEqual(newest["file"], "261009_plain.html")
        self.assertEqual(newest["change"], {"what": "", "why": "make it blue", "src": "note"})

    def test_parts_are_not_projects(self):
        pdir = self.root / "extra_parts"
        pdir.mkdir()
        (pdir / "ignored.html").write_text("ignored")
        self.assertEqual([p["name"] for p in self.get("/api/designs")["projects"]], ["demo"])
        self.assertTrue(all(Path(p).parent.name == "demo" for p, _ in make_thumbs.find_candidates(self.root)))

    def test_post_invalid_body_missing_history_and_bad_choices(self):
        for body in ([], None, "text", 7, {"page": 5}, {"page": "demo/261014_pending-r4.html", "note": 5}):
            request = Request(self.base + "/submit", data=json.dumps(body).encode())
            with self.assertRaises(HTTPError) as caught:
                urlopen(request)
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()
        name = "261014_named-r2-opus.html"
        cpath = self.sidecar(name, ".choices.json", {"latest": {"choices": {"layout": "old"}}})
        request = Request(self.base + "/submit", data=json.dumps({"page": "demo/" + name, "choices": {"layout": "new"}}).encode())
        with urlopen(request) as response:
            self.assertTrue(json.load(response)["ok"])
        doc = json.loads(cpath.read_text())
        self.assertEqual([e["choices"]["layout"] for e in doc["history"]], ["old", "new"])
        cpath.write_text("bad JSON")
        self.assertEqual(self.get("/choices?page=demo/" + name), {})

    def test_service_exit_cleans_active_screenshot_group(self):
        for mode in ("idle", "term", "interrupt"):
            with self.subTest(mode=mode):
                self.stop()
                pidfile = self.root / (mode + "-pids.json")
                chrome = fake_chrome(self.root,
                    "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(999)'])\n"
                    "def stop(*args):\n    child.terminate()\n    child.wait()\n    sys.exit(0)\n"
                    "signal.signal(signal.SIGTERM, stop)\n"
                    "profile = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--user-data-dir='))\n"
                    "Path(%r).write_text(str(os.getpid()) + '\\n' + profile)\ntime.sleep(999)\n" % str(pidfile))
                self.start_server(DESIGN_HUB_THUMBS="1", DESIGN_HUB_CHROME=chrome,
                                  DESIGN_CHOICE_IDLE_MIN="0.02" if mode == "idle" else "0")
                deadline = time.monotonic() + 3
                while not pidfile.exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue(pidfile.exists())
                pid, profile = pidfile.read_text().splitlines()
                pid = int(pid)
                self.assertTrue(group_exists(pid))
                if mode != "idle":
                    self.proc.send_signal(signal.SIGTERM if mode == "term" else signal.SIGINT)
                self.assertEqual(self.proc.wait(timeout=6), 0)
                self.assertFalse(group_exists(pid))
                self.assertFalse(Path(profile).exists())
                self.assertEqual(list(self.project.glob(".thumb-*.png")), [])


class ParserTests(unittest.TestCase):
    def test_frame_future_anchor_priority_unclosed_caps_and_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frames.html"
            path.write_text("<div id='outer'><p class='cap'>Outer</p><div id='inner'></div></div>"
                            "<div class='frame'><a id='before'></a><p class='cap'>After</p><div id='first'></div><div id='second'></div></div>"
                            "<div class='frame'><p class='cap'>None</p></div><div id='outside'></div>"
                            "<div class='frame'><p class='cap'>Unclosed<p class='cap'>Next</p><div id='next'></div></div>")
            self.assertEqual(choice_server.page_frames(str(path), 1),
                             [{"cap": "Outer", "id": "outer"}, {"cap": "After", "id": "first"},
                              {"cap": "None", "id": None}, {"cap": "Unclosed", "id": None},
                              {"cap": "Next", "id": "next"}])
            path.write_text("<section><p class='cap'>A</p><div>no id</div><p class='cap'>B</p><div id='b'></div></section>")
            self.assertEqual(choice_server.page_frames(str(path), 3),
                             [{"cap": "A", "id": None}, {"cap": "B", "id": "b"}])
            path.write_text("".join("<div><p class='cap'>%s</p><div id='f%s'></div></div>" % (i, i) for i in range(60)) +
                            "<![bogus[" + " " * 2000000)
            frames = choice_server.page_frames(str(path), 2)
            self.assertEqual(len(frames), 60)
            self.assertEqual(frames[-1]["id"], "f59")

    def test_bad_html_defaults_are_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.html"
            path.write_text("<head><title>Partial</title><![bogus[")
            # Python 3.14 tolerates this declaration; older parsers raise AssertionError.
            with patch.object(choice_server.HeadParser, "feed", side_effect=AssertionError("bad declaration")), \
                 patch.object(choice_server.FrameParser, "feed", side_effect=AssertionError("bad declaration")):
                self.assertEqual(choice_server.page_metadata(str(path), 1), {"title": "", "change": None})
                self.assertEqual(choice_server.page_frames(str(path), 1), [])
            with patch("builtins.open", side_effect=AssertionError("cache should avoid open")):
                self.assertEqual(choice_server.page_metadata(str(path), 1), {"title": "", "change": None})
                self.assertEqual(choice_server.page_frames(str(path), 1), [])

    def test_head_bounded_read_and_mtime_caches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.html"
            path.write_text("<head><title>Large</title><meta name='dc-why' content='head'></head>" +
                            "<body><meta name='dc-change' content='ignored'>" + " " * 2000000 +
                            "<div id='last'><p class='cap'>Last</p></div></body>")
            reads = []
            real_open = builtins.open

            def track_open(*args, **kwargs):
                f = real_open(*args, **kwargs)
                original_read = f.read

                def read(size=-1):
                    result = original_read(size)
                    reads.append(len(result))
                    return result
                f.read = read
                return f

            with patch("builtins.open", side_effect=track_open):
                metadata = choice_server.page_metadata(str(path), 1)
                self.assertEqual(sum(reads), 16384)
                self.assertEqual(metadata["change"], {"what": "", "why": "head", "src": "meta"})
                reads.clear()
                self.assertEqual(choice_server.page_metadata(str(path), 1), metadata)
                self.assertEqual(reads, [])
                frames = choice_server.page_frames(str(path), 1)
                self.assertEqual(frames, [{"cap": "Last", "id": "last"}])
                self.assertEqual(sum(reads), len(path.read_text()))
                reads.clear()
                self.assertEqual(choice_server.page_frames(str(path), 1), frames)
                self.assertEqual(reads, [])
            with patch.object(choice_server, "ROOT", tmp):
                self.assertIsNone(choice_server.resolve_page("../outside.html"))

    def test_background_thumbs_do_not_touch_idle_timer(self):
        class StopLoop(Exception):
            pass

        stamp = choice_server._last_request[0]
        with patch.object(make_thumbs, "find_chrome", return_value="fake-chrome"), \
             patch.object(make_thumbs, "make_thumbs", return_value=[]) as make, \
             patch.object(choice_server._thumb_signal, "wait", side_effect=StopLoop):
            with self.assertRaises(StopLoop):
                choice_server.watch_thumbs()
            make.assert_called_once_with(choice_server.ROOT, limit=1, chrome="fake-chrome")
        self.assertEqual(choice_server._last_request[0], stamp)
        with patch.object(make_thumbs, "find_chrome", return_value=None), \
             patch.object(make_thumbs, "make_thumbs") as make:
            choice_server.watch_thumbs()
            make.assert_not_called()


class ThumbTests(unittest.TestCase):
    def test_needs_thumb(self):
        self.assertTrue(make_thumbs.needs_thumb(10, None))
        self.assertTrue(make_thumbs.needs_thumb(10, 9))
        self.assertFalse(make_thumbs.needs_thumb(10, 10))
        self.assertFalse(make_thumbs.needs_thumb(10, 11))
        self.assertTrue(make_thumbs.needs_thumb(10, 11, force=True))

    def test_candidate_scope_project_and_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for project in ("one", "two", "hidden_parts", ".hidden"):
                pdir = root / project
                pdir.mkdir()
                for name in ("missing.html", "stale.html", "fresh.html"):
                    html = pdir / name
                    html.write_text("design")
                    os.utime(html, (100, 100))
                for name, stamp in (("stale", 99), ("fresh", 101)):
                    thumb = pdir / (name + ".thumb.png")
                    thumb.write_bytes(b"png")
                    os.utime(thumb, (stamp, stamp))
                (pdir / "draft_parts").mkdir()
                (pdir / "draft_parts/nested.html").write_text("nested")
            (root / "root.html").write_text("root")
            found = make_thumbs.find_candidates(tmp)
            self.assertEqual(len(found), 4)
            self.assertEqual({Path(p).parent.name for p, _ in found}, {"one", "two"})
            self.assertEqual({Path(p).name for p, _ in found}, {"missing.html", "stale.html"})
            self.assertEqual(len(make_thumbs.find_candidates(tmp, project="one")), 2)
            self.assertEqual(len(make_thumbs.find_candidates(tmp, project="one", force=True)), 3)
            with patch.object(make_thumbs, "find_chrome", return_value=None):
                self.assertEqual(make_thumbs.make_thumbs(tmp), [])
                output = io.StringIO()
                with patch.object(sys, "argv", ["make_thumbs.py", "--root", tmp]), contextlib.redirect_stdout(output):
                    self.assertEqual(make_thumbs.main(), 2)
                self.assertIn("Chrome not found", output.getvalue())

    def test_fake_chrome_stable_png_and_group_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "design.html"
            html.write_text("design")
            thumb = Path(make_thumbs.thumb_path(html))
            thumb.write_bytes(b"old thumbnail")
            pidfile = Path(tmp) / "pid"
            chrome = fake_chrome(tmp,
                "Path(%r).write_text(str(os.getpid()))\n" % str(pidfile) +
                "Path(shot).write_bytes(%r)\ntime.sleep(999)\n" % PNG)
            started = time.monotonic()
            ok, message = make_thumbs.capture(str(html), str(thumb), chrome)
            self.assertTrue(ok, message)
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertEqual(thumb.read_bytes(), PNG)
            self.assertFalse(group_exists(int(pidfile.read_text())))
            self.assertEqual(list(Path(tmp).glob(".thumb-*.png")), [])
            self.assertEqual(make_thumbs._active, set())

    def test_nonzero_exit_png_success_and_failure_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "design.html"
            html.write_text("design")
            thumb = make_thumbs.thumb_path(html)
            chrome = fake_chrome(tmp, "Path(shot).write_bytes(%r)\nsys.exit(7)\n" % PNG)
            self.assertTrue(make_thumbs.capture(str(html), thumb, chrome)[0])
            chrome = fake_chrome(tmp, "print('render failed marker', file=sys.stderr)\nsys.exit(7)\n")
            ok, message = make_thumbs.capture(str(html), thumb, chrome)
            self.assertFalse(ok)
            self.assertIn("render failed marker", message)
            self.assertEqual(Path(thumb).read_bytes(), PNG)
            self.assertEqual(list(Path(tmp).glob(".thumb-*.png")), [])

    def test_failure_skip_newest_first_mtime_retry_and_temp_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "one"
            project.mkdir()
            old, new = project / "old.html", project / "new.html"
            for path, stamp in ((old, 100), (new, 200)):
                path.write_text("design")
                os.utime(path, (stamp, stamp))
            stale, recent = project / ".thumb-old.png", project / ".thumb-recent.png"
            stale.write_bytes(b"old")
            os.utime(stale, (time.time() - 601, time.time() - 601))
            recent.write_bytes(b"current")
            self.assertEqual(make_thumbs.find_candidates(tmp)[0][0], str(new))
            with patch.object(make_thumbs, "capture", side_effect=[(False, "bad"), (True, "saved")]) as capture, \
                 contextlib.redirect_stdout(io.StringIO()):
                make_thumbs.make_thumbs(tmp, limit=1, chrome="fake")
                make_thumbs.make_thumbs(tmp, limit=1, chrome="fake")
                self.assertEqual([call.args[0] for call in capture.call_args_list], [str(new), str(old)])
            self.assertEqual(make_thumbs.failed[str(new)], 200)
            self.assertFalse(stale.exists())
            self.assertTrue(recent.exists())
            os.utime(new, (300, 300))
            self.assertEqual(make_thumbs.find_candidates(tmp)[0][0], str(new))

    def test_timeout_and_sigkill_escalation(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "design.html"
            html.write_text("design")
            pidfile = Path(tmp) / "pid"
            chrome = fake_chrome(tmp,
                "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n" +
                "Path(%r).write_text(str(os.getpid()))\n" % str(pidfile) +
                "print('timeout marker', file=sys.stderr, flush=True)\ntime.sleep(999)\n")
            real_clock = time.monotonic
            started = real_clock()
            ready_at = []

            def fast_clock():
                now = real_clock()
                if pidfile.exists() and not ready_at:
                    ready_at.append(now)
                return now if not ready_at else ready_at[0] + (now - ready_at[0]) * 200

            with patch.object(make_thumbs.time, "monotonic", side_effect=fast_clock):
                ok, message = make_thumbs.capture(str(html), make_thumbs.thumb_path(html), chrome)
            self.assertFalse(ok)
            self.assertIn("timeout (40s)", message)
            self.assertIn("timeout marker", message)
            self.assertFalse(group_exists(int(pidfile.read_text())))

    def test_chrome_env_override(self):
        with patch.dict(os.environ, {"DESIGN_HUB_CHROME": "/fake/chrome"}):
            self.assertEqual(make_thumbs.find_chrome(), "/fake/chrome")


if __name__ == "__main__":
    unittest.main()
