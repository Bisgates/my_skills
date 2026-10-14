#!/usr/bin/env python3
"""Isolated HTTP contract tests; no real Chrome or running design service is used."""
import builtins, contextlib, io, json, os, socket, subprocess, sys, tempfile, time, unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
import make_thumbs
import choice_server

SCRIPTS = Path(__file__).resolve().parent


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
                  "<div class='frame'><a id='preceding'></a><div><p class='cap'>Before</p></div></div>"
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
                         [{"cap": "One & two", "id": "inner"}, {"cap": "Before", "id": "preceding"},
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


class ParserTests(unittest.TestCase):
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

    def test_capture_timeout_pid_cleanup_and_atomic_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "design.html"
            html.write_text("design")
            thumb = Path(make_thumbs.thumb_path(html))
            thumb.write_bytes(b"old thumbnail")
            proc = Mock()
            proc.returncode = -9
            proc.wait.side_effect = [subprocess.TimeoutExpired("Chrome", 40), -9]
            captured = {}
            png = b"\x89PNG\r\n\x1a\n" + b"test payload" + b"\x00\x00\x00\x00IEND\xaeB`\x82"

            def popen(cmd, **kwargs):
                captured["tmp"] = next(arg.split("=", 1)[1] for arg in cmd if arg.startswith("--screenshot="))
                captured["profile"] = next(arg.split("=", 1)[1] for arg in cmd if arg.startswith("--user-data-dir="))
                self.assertTrue(Path(captured["profile"]).is_dir())
                self.assertEqual(thumb.read_bytes(), b"old thumbnail")
                Path(captured["tmp"]).write_bytes(png)
                return proc

            with patch.object(make_thumbs.subprocess, "Popen", side_effect=popen):
                ok, message = make_thumbs.capture(str(html), str(thumb), "fake-chrome")
            self.assertTrue(ok)
            self.assertIn("40s", message)
            proc.kill.assert_called_once_with()
            self.assertEqual(proc.wait.call_args_list[0].kwargs, {"timeout": 40})
            self.assertEqual(thumb.read_bytes(), png)
            self.assertFalse(Path(captured["tmp"]).exists())
            self.assertFalse(Path(captured["profile"]).exists())

            failed = Mock()
            failed.wait.side_effect = [subprocess.TimeoutExpired("Chrome", 40), -9]
            failed.returncode = -9
            with patch.object(make_thumbs.subprocess, "Popen", return_value=failed):
                self.assertFalse(make_thumbs.capture(str(html), str(thumb), "fake-chrome")[0])
            self.assertEqual(thumb.read_bytes(), png)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["design.html", "design.thumb.png"])


if __name__ == "__main__":
    unittest.main()
