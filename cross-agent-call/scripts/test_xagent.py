#!/usr/bin/env python3
"""Tests for scripts/xagent. Run: python3 scripts/test_xagent.py

Fake claude / codex / grok executables on a temp PATH record their argv and
env, emit fake codex JSONL, exit with chosen codes and sleep for signal tests.
Every registry line is validated with Vantage's own ``parse_line`` when the
integration worktree is present (skipped otherwise).
"""
import importlib.util
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import types
import unittest
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
XAGENT = os.path.join(HERE, "xagent")
VANTAGE_TREE = "/Users/han/project/build_with_opus/vantage-app"
THREAD_ID = "01a0ce89-88c0-7f90-a9c0-6258dcdefd51"
KEYS = {
    "start": {"v", "type", "run_id", "harness", "session_id", "model", "effort",
              "cwd", "pid", "parent_run_id", "at"},
    "child": {"v", "type", "run_id", "pid", "at"},
    "bind": {"v", "type", "run_id", "session_id", "at"},
    "end": {"v", "type", "run_id", "exit_code", "signal", "at"},
}


def load_parse_line():
    """Vantage's reader-side ``parse_line``, or None if the worktree is absent.

    The module is loaded from its file under a stub package so its
    ``from . import backends`` resolves without importing the whole app
    (which needs Python 3.11 and touches ~/.vantage).
    """
    path = os.path.join(VANTAGE_TREE, "vantage", "xagent.py")
    if not os.path.isfile(path):
        return None
    try:
        pkg = types.ModuleType("_xagent_contract")
        pkg.__path__ = []
        pkg.backends = types.ModuleType("_xagent_contract.backends")
        sys.modules["_xagent_contract"] = pkg
        sys.modules["_xagent_contract.backends"] = pkg.backends
        spec = importlib.util.spec_from_file_location("_xagent_contract.xagent", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.parse_line
    except Exception as exc:  # pragma: no cover - depends on the other tree
        sys.stderr.write("note: could not load parse_line (%s); contract check skipped\n" % exc)
        return None


PARSE_LINE = load_parse_line()

FAKE_CLI = r'''#!%(python)s
import json, os, signal, subprocess, sys, time
name = os.path.basename(sys.argv[0])
args = sys.argv[1:]
env = os.environ
rec = {"name": name, "argv": args, "parent_env": env.get("XAGENT_PARENT_RUN_ID"),
       "ppid": os.getppid(), "pid": os.getpid(),
       "hup_ignored": signal.getsignal(signal.SIGHUP) == signal.SIG_IGN}

def dump(entry):
    with open(env["FAKE_RECORD"], "a") as fh:
        fh.write(json.dumps(entry) + "\n")

if env.get("FAKE_TRAP"):
    def trap(signum, frame):
        dump({"name": name, "trapped": signum})
        sys.exit(int(env["FAKE_TRAP"]))
    signal.signal(signal.SIGTERM, trap)
    signal.signal(signal.SIGINT, trap)
    signal.signal(signal.SIGHUP, trap)
if env.get("FAKE_READ_STDIN") or (name == "codex" and "-" in args):
    rec["stdin"] = sys.stdin.read()
dump(rec)

if env.get("FAKE_NEST"):
    child_env = dict(env)
    child_env.pop("FAKE_NEST")
    sys.exit(subprocess.call([sys.executable, env["XAGENT_PATH"]] + json.loads(env["FAKE_NEST"]),
                             env=child_env))

last = env.get("FAKE_LAST", "FINAL ANSWER")
if name == "codex":
    out = None
    for i, a in enumerate(args):
        if a in ("-o", "--output-last-message") and i + 1 < len(args):
            out = args[i + 1]
        elif a.startswith("--output-last-message="):
            out = a.split("=", 1)[1]
        elif a.startswith("-o") and len(a) > 2:
            out = a[2:]
    failed = bool(env.get("FAKE_CODEX_ERROR"))
    if "--json" in args:
        def emit(ev):
            sys.stdout.write(json.dumps(ev) + "\n")
            sys.stdout.flush()
        emit({"type": "thread.started", "thread_id": env.get("FAKE_THREAD", "%(thread)s")})
        if env.get("FAKE_REPLAY"):   # an earlier turn's answer showing up in the stream
            emit({"type": "turn.started"})
            emit({"type": "item.completed", "item": {"id": "old", "type": "agent_message",
                                                     "text": env["FAKE_REPLAY"]}})
            emit({"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}})
        emit({"type": "turn.started"})
        if failed:
            emit({"type": "error", "message": "boom"})
            emit({"type": "turn.failed", "error": {"message": "boom"}})
        else:
            emit({"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": last}})
            emit({"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}})
    else:
        sys.stderr.write("OpenAI Codex (fake banner)\n")
        if not failed:
            sys.stdout.write(last + "\n")
    if out and not failed:
        with open(out, "w") as fh:
            fh.write(last)
elif env.get("FAKE_STDOUT"):
    sys.stdout.write(env["FAKE_STDOUT"])
sys.stdout.flush()

if env.get("FAKE_SLEEP"):
    with open(env["FAKE_READY"], "w") as fh:
        fh.write("ready")
    time.sleep(float(env["FAKE_SLEEP"]))
sys.exit(int(env.get("FAKE_EXIT", "0")))
'''


class XagentTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xagent-test-")
        self.bin = os.path.join(self.tmp, "bin")
        self.home = os.path.join(self.tmp, "home")
        self.tmpdir = os.path.join(self.tmp, "tmpdir")
        self.work = os.path.join(self.tmp, "work")
        for d in (self.bin, self.home, self.tmpdir, self.work):
            os.makedirs(d)
        self.work = os.path.realpath(self.work)
        script = FAKE_CLI % {"python": sys.executable, "thread": THREAD_ID}
        for name in ("claude", "codex", "grok"):
            self.install_fake(os.path.join(self.bin, name), script)
        self.log = os.path.join(self.tmp, "registry.jsonl")
        self.record = os.path.join(self.tmp, "record.jsonl")

    def tearDown(self):
        for root, dirs, _files in os.walk(self.tmp):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def install_fake(path, script):
        with open(path, "w") as fh:
            fh.write(script)
        os.chmod(path, 0o755)

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if k not in ("VANTAGE_XAGENT_LOG", "XAGENT_PARENT_RUN_ID", "TMUX", "TMUX_PANE")
               and not k.startswith("FAKE_")}
        env.update({"PATH": self.bin + os.pathsep + "/usr/bin:/bin", "HOME": self.home,
                    "TMPDIR": self.tmpdir, "VANTAGE_XAGENT_LOG": self.log,
                    "FAKE_RECORD": self.record, "XAGENT_PATH": XAGENT})
        for key, value in extra.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return env

    def run_xagent(self, harness, *args, **kw):
        input_data = kw.pop("input", None)
        return subprocess.run([sys.executable, XAGENT, harness] + list(args),
                              env=self.env(**kw), cwd=self.work, input=input_data,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

    def records(self):
        if not os.path.exists(self.record):
            return []
        with open(self.record) as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def events(self, path=None):
        path = path or self.log
        if not os.path.exists(path):
            return []
        out = []
        with open(path, "rb") as fh:
            data = fh.read()
        self.assertTrue(data == b"" or data.endswith(b"\n"), "registry must end with a newline")
        for raw in data.split(b"\n"):
            if not raw.strip():
                continue
            self.assertLess(len(raw), 4096)
            event = json.loads(raw)
            self.assertEqual(set(event), KEYS[event["type"]], event)
            self.assertEqual(event["v"], 1)
            if PARSE_LINE is not None:
                self.assertIsNotNone(PARSE_LINE(raw), "parse_line rejected %r" % raw)
            out.append(event)
        return out

    def one_run(self, expect_bind=False):
        """The single run's (start, bind-or-None, end), checking order and run_id.

        Every run that started its CLI has a child line right after start,
        carrying the pid of the CLI process (checked against the fake's record).
        """
        events = self.events()
        kinds = [e["type"] for e in events]
        self.assertEqual(kinds, ["start", "child", "bind", "end"] if expect_bind
                         else ["start", "child", "end"])
        self.assertEqual(len({e["run_id"] for e in events}), 1)
        recs = [r for r in self.records() if "pid" in r]
        if recs:
            self.assertEqual(events[1]["pid"], recs[0]["pid"])
            self.assertLessEqual(events[0]["at"], events[1]["at"])
        return events[0], (events[2] if expect_bind else None), events[-1]

    def start_line(self, stderr):
        lines = [l for l in stderr.decode().splitlines() if l.startswith("[xagent] run=")]
        self.assertEqual(len(lines), 1, stderr)
        return lines[0]

    def notes(self, stderr, needle):
        """[xagent] stderr lines mentioning ``needle``."""
        return [l for l in stderr.decode().splitlines() if l.startswith("[xagent] ") and needle in l]

    def reset(self):
        for path in (self.log, self.record):
            if os.path.exists(path):
                os.remove(path)


class ContractReaderTests(unittest.TestCase):
    @unittest.skipIf(not os.path.isdir(VANTAGE_TREE), "Vantage integration worktree absent")
    def test_parse_line_loaded_and_strict(self):
        self.assertIsNotNone(PARSE_LINE)
        self.assertIsNone(PARSE_LINE(b'{"v":1,"type":"end","run_id":"bad","exit_code":0,"at":1}'))
        rid = str(uuid.uuid4())
        child = PARSE_LINE(('{"v":1,"type":"child","run_id":"%s","pid":42,"at":1.5}' % rid).encode())
        self.assertEqual(child, {"type": "child", "run_id": rid, "pid": 42, "at": 1.5})
        self.assertIsNone(PARSE_LINE(('{"v":1,"type":"child","run_id":"%s","pid":0,"at":1}' % rid).encode()))


class ClaudeTests(XagentTestCase):
    def test_new_session_injects_session_id(self):
        r = self.run_xagent("claude", "-p", "--effort", "high", "--model", "opus", "hi",
                            FAKE_STDOUT="answer\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, b"answer\n")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[0], "--session-id")
        sid = argv[1]
        self.assertEqual(str(uuid.UUID(sid)), sid)
        self.assertEqual(argv[2:], ["-p", "--effort", "high", "--model", "opus", "hi"])
        start, _, end = self.one_run()
        self.assertEqual((start["harness"], start["session_id"], start["model"], start["effort"]),
                         ("claude", sid, "opus", "high"))
        self.assertEqual(start["cwd"], self.work)
        self.assertEqual(start["pid"], self.records()[0]["ppid"])
        self.assertIsNone(start["parent_run_id"])
        self.assertEqual((end["exit_code"], end["signal"]), (0, None))
        self.assertIn("harness=claude session=%s" % sid, self.start_line(r.stderr))
        self.assertIn("run=%s" % start["run_id"], self.start_line(r.stderr))

    def test_caller_session_id_is_kept(self):
        sid = str(uuid.uuid4())
        self.run_xagent("claude", "-p", "--session-id=%s" % sid, "hi")
        self.assertEqual(self.records()[0]["argv"], ["-p", "--session-id=%s" % sid, "hi"])
        self.assertEqual(self.one_run()[0]["session_id"], sid)

    def test_resume_keeps_resumed_id(self):
        rid = str(uuid.uuid4())
        for flag in ("--resume", "-r"):
            os.remove(self.log) if os.path.exists(self.log) else None
            os.remove(self.record) if os.path.exists(self.record) else None
            self.run_xagent("claude", "-p", flag, rid, "again")
            self.assertEqual(self.records()[0]["argv"], ["-p", flag, rid, "again"])
            self.assertEqual(self.one_run()[0]["session_id"], rid)

    def test_resume_with_fork_injects_new_id(self):
        rid = str(uuid.uuid4())
        self.run_xagent("claude", "-p", "--resume", rid, "--fork-session", "branch")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[0], "--session-id")
        self.assertNotEqual(argv[1], rid)
        self.assertEqual(self.one_run()[0]["session_id"], argv[1])

    def test_continue_leaves_id_unknown(self):
        r = self.run_xagent("claude", "-p", "--continue", "more")
        self.assertEqual(self.records()[0]["argv"], ["-p", "--continue", "more"])
        self.assertIsNone(self.one_run()[0]["session_id"])
        self.assertTrue(self.start_line(r.stderr).endswith("session=unknown"))

    def test_continue_with_fork_injects(self):
        self.run_xagent("claude", "-p", "-c", "--fork-session", "more")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[0], "--session-id")
        self.assertEqual(self.one_run()[0]["session_id"], argv[1])

    def test_non_uuid_resume_and_from_pr_unknown(self):
        self.run_xagent("claude", "-p", "--resume", "my title", "x")
        self.assertEqual(self.records()[0]["argv"], ["-p", "--resume", "my title", "x"])
        self.assertIsNone(self.one_run()[0]["session_id"])
        os.remove(self.log)
        os.remove(self.record)
        self.run_xagent("claude", "-p", "--from-pr", "12", "x")
        self.assertNotIn("--session-id", self.records()[0]["argv"])

    def test_interactive_and_subcommands_not_injected(self):
        self.run_xagent("claude", "mcp", "list")
        self.assertEqual(self.records()[0]["argv"], ["mcp", "list"])
        self.assertIsNone(self.one_run()[0]["session_id"])

    def test_no_session_persistence_respected(self):
        """Privacy flag passes through; run is registered with no session id."""
        rid = str(uuid.uuid4())
        cases = [["-p", "--no-session-persistence", "hi"],
                 ["-p", "--no-session-persistence", "--session-id", rid, "hi"],
                 ["-p", "--resume", rid, "--no-session-persistence", "hi"]]
        for args in cases:
            self.reset()
            r = self.run_xagent("claude", *args, FAKE_STDOUT="private\n", FAKE_EXIT="2")
            self.assertEqual((r.returncode, r.stdout), (2, b"private\n"), args)
            self.assertEqual(self.records()[0]["argv"], args)
            start, _, end = self.one_run()
            self.assertIsNone(start["session_id"], args)
            self.assertEqual(end["exit_code"], 2)
            self.assertEqual(len(self.notes(r.stderr, "--no-session-persistence")), 1, r.stderr)
            self.assertTrue(self.start_line(r.stderr).endswith("session=none"))

    def test_background_launch_not_registered(self):
        """--bg returns at once while the session runs on: pass through, register nothing."""
        for flag in ("--bg", "--background"):
            self.reset()
            args = ["-p", flag, "long task"]
            r = self.run_xagent("claude", *args, FAKE_STDOUT="bg-id\n", FAKE_EXIT="0")
            self.assertEqual((r.returncode, r.stdout), (0, b"bg-id\n"))
            rec = self.records()[0]
            self.assertEqual(rec["argv"], args)
            self.assertIsNone(rec["parent_env"])
            self.assertEqual(rec["ppid"], os.getpid(), "wrapper should exec the CLI in place")
            self.assertFalse(os.path.exists(self.log))
            self.assertEqual(len(self.notes(r.stderr, flag)), 1, r.stderr)
            self.assertNotIn(b"[xagent] run=", r.stderr)
        self.reset()
        r = self.run_xagent("claude", "-p", "--bg", "x", FAKE_EXIT="6")
        self.assertEqual(r.returncode, 6)

    def test_stdin_passthrough(self):
        r = self.run_xagent("claude", "-p", input=b"prompt from stdin\n", FAKE_READ_STDIN="1",
                            FAKE_STDOUT="ok\n")
        self.assertEqual(self.records()[0]["stdin"], "prompt from stdin\n")
        self.assertEqual(r.stdout, b"ok\n")

    def test_parent_run_id_env(self):
        parent = str(uuid.uuid4())
        self.run_xagent("claude", "-p", "hi", XAGENT_PARENT_RUN_ID=parent)
        start, _, _ = self.one_run()
        self.assertEqual(start["parent_run_id"], parent)
        self.assertEqual(self.records()[0]["parent_env"], start["run_id"])

    def test_bad_parent_run_id_ignored(self):
        self.run_xagent("claude", "-p", "hi", XAGENT_PARENT_RUN_ID="not-a-uuid")
        self.assertIsNone(self.one_run()[0]["parent_run_id"])


class GrokTests(XagentTestCase):
    def test_new_session_injects(self):
        r = self.run_xagent("grok", "-p", "hi", "-m", "grok-4.7", "--effort", "low",
                            "--output-format", "plain", FAKE_STDOUT="OK\n")
        self.assertEqual(r.stdout, b"OK\n")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[0], "--session-id")
        self.assertEqual(argv[2:], ["-p", "hi", "-m", "grok-4.7", "--effort", "low",
                                    "--output-format", "plain"])
        start, _, _ = self.one_run()
        self.assertEqual((start["session_id"], start["model"], start["effort"]),
                         (argv[1], "grok-4.7", "low"))

    def test_prompt_file_and_reasoning_effort(self):
        self.run_xagent("grok", "--prompt-file", "p.txt", "--reasoning-effort", "high")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[0], "--session-id")
        self.assertEqual(self.one_run()[0]["effort"], "high")

    def test_caller_short_session_id(self):
        sid = str(uuid.uuid4())
        self.run_xagent("grok", "-p", "hi", "-s", sid)
        self.assertEqual(self.records()[0]["argv"], ["-p", "hi", "-s", sid])
        self.assertEqual(self.one_run()[0]["session_id"], sid)

    def test_resume_cases(self):
        rid = str(uuid.uuid4())
        cases = [
            (["-p", "x", "-r", rid], rid, False),
            (["-p", "x", "--continue"], None, False),
            (["-p", "x", "-c", "--fork-session"], "new", True),
            (["-p", "x", "--resume", rid, "--fork-session"], "new", True),
            (["-p", "x", "-r"], None, False),
        ]
        for args, expect, injected in cases:
            for path in (self.log, self.record):
                if os.path.exists(path):
                    os.remove(path)
            self.run_xagent("grok", *args)
            argv = self.records()[0]["argv"]
            sid = self.one_run()[0]["session_id"]
            if injected:
                self.assertEqual(argv[:1], ["--session-id"], args)
                self.assertEqual(sid, argv[1])
                self.assertNotEqual(sid, rid)
            else:
                self.assertEqual(argv, args)
                self.assertEqual(sid, expect, args)

    def test_cwd_flag_sets_start_cwd(self):
        self.run_xagent("grok", "-p", "x", "--cwd", "sub")
        self.assertEqual(self.one_run()[0]["cwd"], os.path.join(self.work, "sub"))

    def test_subcommand_not_injected(self):
        self.run_xagent("grok", "models")
        self.assertEqual(self.records()[0]["argv"], ["models"])


class CodexTests(XagentTestCase):
    def test_exec_binds_and_keeps_stdout_clean(self):
        r = self.run_xagent("codex", "exec", "-m", "gpt-6-astra", "-c", "model_reasoning_effort=low",
                            "--skip-git-repo-check", "reply with OK", FAKE_LAST="OK")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, b"OK\n")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv, ["exec", "--json", "-m", "gpt-6-astra", "-c", "model_reasoning_effort=low",
                                "--skip-git-repo-check", "reply with OK"])
        self.assertEqual(os.listdir(self.tmpdir), [], "no temp files")
        start, bind, end = self.one_run(expect_bind=True)
        self.assertIsNone(start["session_id"])
        self.assertEqual((start["model"], start["effort"]), ("gpt-6-astra", "low"))
        self.assertEqual(bind["session_id"], THREAD_ID)
        self.assertEqual(end["exit_code"], 0)
        self.assertTrue(self.start_line(r.stderr).endswith("session=pending"))
        self.assertIn(("[xagent] session=%s" % THREAD_ID).encode(), r.stderr)
        self.assertNotIn(b"thread.started", r.stdout + r.stderr)

    def test_late_answer_after_exit_is_still_read(self):
        # codex exits while a grandchild holding the pipe writes the answer later:
        # the wrapper keeps draining while lines arrive instead of cutting off at a fixed timeout.
        msg = '{"type":"item.completed","item":{"type":"agent_message","text":"%s"}}'
        # total 6s > the 5s grace, but never 5s of silence: a fixed timeout would stop at EARLY
        script = "#!/bin/sh\n(sleep 3; echo '%s'; sleep 3; echo '%s') &\nexit 0\n" % (
            msg % "EARLY", msg % "LATE")
        self.install_fake(os.path.join(self.bin, "codex"), script)
        r = self.run_xagent("codex", "exec", "q")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, b"LATE\n")
        self.assertNotIn(b"still open", r.stderr)

    def test_caller_output_file_is_used_and_printed(self):
        out = os.path.join(self.work, "last.txt")
        r = self.run_xagent("codex", "exec", "-o", out, "q", FAKE_LAST="ANSWER")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv, ["exec", "--json", "-o", out, "q"])
        with open(out) as fh:
            self.assertEqual(fh.read(), "ANSWER")
        self.assertEqual(r.stdout, b"ANSWER\n")
        self.one_run(expect_bind=True)

    def test_caller_output_file_tilde_is_expanded(self):
        r = self.run_xagent("codex", "exec", "-C", self.work, "-o", "~/out.txt", "q", FAKE_LAST="T")
        path = os.path.join(self.home, "out.txt")
        self.assertEqual(self.records()[0]["argv"][-2:], [path, "q"])
        self.assertEqual(r.stdout, b"T\n")

    def test_late_signal_stops_draining_a_chatty_grandchild(self):
        # grandchild keeps writing every second forever: the idle grace never trips,
        # but a signal after codex exited ends the wait instead of hanging the caller
        line = '{"type":"item.completed","item":{"type":"agent_message","text":"ANS"}}'
        script = "#!/bin/sh\necho '%s'\n(while :; do sleep 1; echo '{}'; done) &\necho $! > %s/gc.pid\nexit 0\n" % (
            line, self.tmp)
        self.install_fake(os.path.join(self.bin, "codex"), script)
        proc = subprocess.Popen([sys.executable, XAGENT, "codex", "exec", "q"], env=self.env(),
                                cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            time.sleep(3)
            self.assertIsNone(proc.poll(), "still draining while the grandchild writes")
            proc.send_signal(signal.SIGTERM)
            out, _err = proc.communicate(timeout=10)
        finally:
            with open(os.path.join(self.tmp, "gc.pid")) as fh:
                try:
                    os.kill(int(fh.read().strip()), signal.SIGKILL)
                except OSError:
                    pass
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(out, b"ANS\n")
        self.assertEqual(self.events()[-1]["exit_code"], 0)

    def test_caller_output_file_long_form(self):
        out = os.path.join(self.work, "last.txt")
        r = self.run_xagent("codex", "exec", "--output-last-message=%s" % out, "q", FAKE_LAST="A2")
        self.assertEqual(self.records()[0]["argv"], ["exec", "--json", "--output-last-message=%s" % out, "q"])
        self.assertEqual(r.stdout, b"A2\n")

    def test_relative_output_file_resolved_against_codex_cwd(self):
        sub = os.path.join(self.work, "sub")
        os.makedirs(sub)
        cases = [
            (["exec", "-C", "sub", "-o", "last.txt", "q"],
             ["exec", "--json", "-C", "sub", "-o", os.path.join(sub, "last.txt"), "q"], sub),
            (["exec", "--cd=sub", "--output-last-message", "last.txt", "q"],
             ["exec", "--json", "--cd=sub", "--output-last-message", os.path.join(sub, "last.txt"), "q"], sub),
            (["-C", "sub", "exec", "-olast.txt", "q"],
             ["-C", "sub", "exec", "--json", "-o" + os.path.join(sub, "last.txt"), "q"], sub),
            (["exec", "--output-last-message=last.txt", "q"],
             ["exec", "--json", "--output-last-message=%s" % os.path.join(self.work, "last.txt"), "q"],
             self.work),
            (["exec", "-o=last.txt", "q"],
             ["exec", "--json", "-o" + os.path.join(self.work, "last.txt"), "q"], self.work),
        ]
        for args, expect_argv, where in cases:
            self.reset()
            for d in (sub, self.work):
                if os.path.exists(os.path.join(d, "last.txt")):
                    os.remove(os.path.join(d, "last.txt"))
            r = self.run_xagent("codex", *args, FAKE_LAST="REL")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.records()[0]["argv"], expect_argv)
            with open(os.path.join(where, "last.txt")) as fh:
                self.assertEqual(fh.read(), "REL")
            self.assertEqual(r.stdout, b"REL\n")
            self.assertEqual(self.one_run(expect_bind=True)[0]["cwd"], where)

    def test_stale_output_file_never_printed(self):
        """A failed run prints nothing on stdout, even when the caller's -o file holds an old answer."""
        out = os.path.join(self.work, "last.txt")
        with open(out, "w") as fh:
            fh.write("STALE ANSWER")
        r = self.run_xagent("codex", "exec", "-o", "last.txt", "q", FAKE_CODEX_ERROR="1", FAKE_EXIT="1")
        self.assertEqual((r.returncode, r.stdout), (1, b""))
        self.assertIn(b"ERROR: boom", r.stderr)
        with open(out) as fh:
            self.assertEqual(fh.read(), "STALE ANSWER")
        self.reset()
        r = self.run_xagent("codex", "exec", "-o", "last.txt", "q", FAKE_LAST="FRESH")
        self.assertEqual((r.returncode, r.stdout), (0, b"FRESH\n"))

    def test_final_message_is_this_turns(self):
        """An agent_message from an earlier turn in the stream is never this run's answer."""
        r = self.run_xagent("codex", "exec", "resume", THREAD_ID, "again", FAKE_REPLAY="OLD", FAKE_LAST="NEW")
        self.assertEqual((r.returncode, r.stdout), (0, b"NEW\n"))
        self.reset()
        r = self.run_xagent("codex", "exec", "resume", THREAD_ID, "again", FAKE_REPLAY="OLD",
                            FAKE_CODEX_ERROR="1", FAKE_EXIT="1")
        self.assertEqual((r.returncode, r.stdout), (1, b""))

    def test_multiline_final_message(self):
        r = self.run_xagent("codex", "exec", "q", FAKE_LAST="line 1\nline 2\n")
        self.assertEqual(r.stdout, b"line 1\nline 2\n")

    def test_json_passthrough(self):
        r = self.run_xagent("codex", "exec", "--json", "q", FAKE_LAST="X")
        self.assertEqual(self.records()[0]["argv"], ["exec", "--json", "q"])
        lines = [json.loads(l) for l in r.stdout.decode().splitlines()]
        self.assertEqual([e["type"] for e in lines],
                         ["thread.started", "turn.started", "item.completed", "turn.completed"])
        self.assertEqual(self.one_run(expect_bind=True)[1]["session_id"], THREAD_ID)

    def test_ephemeral_respected(self):
        """--ephemeral passes through; run is registered without a session id and never bound."""
        for args in (["exec", "--ephemeral", "q"], ["exec", "resume", THREAD_ID, "--ephemeral", "q"]):
            self.reset()
            r = self.run_xagent("codex", *args, FAKE_LAST="EPH")
            self.assertEqual((r.returncode, r.stdout), (0, b"EPH\n"), r.stderr)
            self.assertEqual(self.records()[0]["argv"], ["exec", "--json"] + args[1:])
            start, _, end = self.one_run(expect_bind=False)
            self.assertIsNone(start["session_id"])
            self.assertEqual(end["exit_code"], 0)
            warn = [l for l in r.stderr.decode().splitlines() if "--ephemeral" in l]
            self.assertEqual(len(warn), 1)
            self.assertTrue(warn[0].startswith("[xagent] "))
            self.assertTrue(self.start_line(r.stderr).endswith("session=none"))
            self.assertNotIn(b"[xagent] session=", r.stderr)

    def test_cloud_exec_not_registered(self):
        args = ["cloud", "exec", "--env", "e1", "task"]
        r = self.run_xagent("codex", *args, FAKE_LAST="task-123")
        self.assertEqual((r.returncode, r.stdout), (0, b"task-123\n"))
        rec = self.records()[0]
        self.assertEqual(rec["argv"], args)
        self.assertEqual(rec["ppid"], os.getpid())
        self.assertFalse(os.path.exists(self.log))
        self.assertEqual(len(self.notes(r.stderr, "cloud exec")), 1, r.stderr)
        self.reset()
        self.run_xagent("codex", "-c", "k=v", "cloud", "list")   # not a launch: registered as usual
        self.assertEqual(self.records()[0]["argv"], ["-c", "k=v", "cloud", "list"])
        self.one_run()

    def test_resume_injects_after_exec(self):
        rid = "01a0ce8a-175d-71a2-bfc8-0c700212f371"
        r = self.run_xagent("codex", "exec", "resume", rid, "again", FAKE_THREAD=rid, FAKE_LAST="R")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv, ["exec", "--json", "resume", rid, "again"])
        self.assertEqual(self.one_run(expect_bind=True)[1]["session_id"], rid)
        self.assertEqual(r.stdout, b"R\n")

    def test_top_level_options_before_exec(self):
        self.run_xagent("codex", "-m", "gpt-6-sol", "-c", 'model_reasoning_effort="xhigh"', "exec", "q")
        argv = self.records()[0]["argv"]
        self.assertEqual(argv[:6], ["-m", "gpt-6-sol", "-c", 'model_reasoning_effort="xhigh"', "exec", "--json"])
        start = self.one_run(expect_bind=True)[0]
        self.assertEqual((start["model"], start["effort"]), ("gpt-6-sol", "xhigh"))

    def test_exec_alias_e(self):
        self.run_xagent("codex", "e", "q")
        self.assertEqual(self.records()[0]["argv"][:2], ["e", "--json"])

    def test_non_exec_codex_passthrough(self):
        r = self.run_xagent("codex", "review", "--uncommitted", FAKE_STDOUT="")
        self.assertEqual(self.records()[0]["argv"], ["review", "--uncommitted"])
        self.assertIsNone(self.one_run()[0]["session_id"])
        self.assertTrue(self.start_line(r.stderr).endswith("session=unknown"))

    def test_stdin_prompt(self):
        r = self.run_xagent("codex", "exec", "-", input=b"long prompt\n", FAKE_LAST="S")
        self.assertEqual(self.records()[0]["stdin"], "long prompt\n")
        self.assertEqual(r.stdout, b"S\n")

    def test_argv_prompt_with_idle_stdin_pipe_does_not_hang(self):
        # A background shell hands down a pipe nobody writes or closes.
        r_fd, w_fd = os.pipe()
        try:
            r = subprocess.run([sys.executable, XAGENT, "codex", "exec", "q"], env=self.env(FAKE_LAST="S", FAKE_READ_STDIN="1"),
                               cwd=self.work, stdin=r_fd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=30)
        finally:
            os.close(r_fd)
            os.close(w_fd)
        self.assertEqual(r.stdout, b"S\n")
        self.assertEqual(self.records()[0]["stdin"], "")
        self.assertIn(b"stdin=/dev/null", r.stderr)

    def test_argv_prompt_keeps_piped_stdin_context(self):
        self.run_xagent("codex", "exec", "q", input=b"ctx\n", FAKE_LAST="S", FAKE_READ_STDIN="1")
        self.assertEqual(self.records()[0]["stdin"], "ctx\n")

    def test_error_surfaces_on_stderr_and_exit_code(self):
        r = self.run_xagent("codex", "exec", "q", FAKE_CODEX_ERROR="1", FAKE_EXIT="1")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")
        self.assertEqual(r.stderr.decode().count("ERROR: boom"), 1)
        self.assertEqual(self.one_run(expect_bind=True)[2]["exit_code"], 1)


class CodexModelAliasTests(XagentTestCase):
    def catalogs(self, vantage=None, models=()):
        """Vantage latest cache (family -> slug) and codex models_cache (slug, visibility)."""
        if vantage is not None:
            os.makedirs(os.path.join(self.home, ".vantage", "cache"))
            with open(os.path.join(self.home, ".vantage", "cache", "latest_models.json"), "w") as fh:
                json.dump({"codex": vantage}, fh)
        if models:
            os.makedirs(os.path.join(self.home, ".codex"))
            with open(os.path.join(self.home, ".codex", "models_cache.json"), "w") as fh:
                json.dump({"client_version": "0.154.0",
                           "models": [{"slug": s, "visibility": v} for s, v in models]}, fh)

    def test_family_takes_vantage_latest_over_an_older_codex_cache(self):
        # an old codex client rewrote models_cache.json without the newest sol
        self.catalogs({"sol": "gpt-6.1-sol"}, [("gpt-6-sol", "list"), ("gpt-5.6-sol", "list")])
        r = self.run_xagent("codex", "exec", "-m", "sol", "-c", "model_reasoning_effort=high", "q",
                            FAKE_LAST="OK", CODEX_HOME=None)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.records()[0]["argv"],
                         ["exec", "--json", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=high", "q"])
        self.assertEqual(self.one_run(expect_bind=True)[0]["model"], "gpt-6.1-sol")
        self.assertEqual(len(self.notes(r.stderr, "model sol -> gpt-6.1-sol (vantage)")), 1)

    def test_newer_visible_codex_model_wins_and_versions_compare_numerically(self):
        self.catalogs({"luna": "gpt-6.9-luna"},
                      [("gpt-6.10-luna", "list"), ("gpt-7-luna", "hide"), ("gpt-6-sol", "list")])
        for form, expected in ((["--model=tuna"], "--model=gpt-6.10-luna"), (["-mluna"], "-mgpt-6.10-luna")):
            self.reset()
            r = self.run_xagent("codex", "exec", *(form + ["q"]), CODEX_HOME=None)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.records()[0]["argv"], ["exec", "--json", expected, "q"])

    def test_full_slug_passes_through(self):
        self.catalogs({"astra": "gpt-7-astra"})
        self.run_xagent("codex", "exec", "-m", "gpt-6-astra", "q", CODEX_HOME=None)
        self.assertEqual(self.records()[0]["argv"], ["exec", "--json", "-m", "gpt-6-astra", "q"])

    def test_unresolvable_family_fails_before_codex_starts(self):
        self.catalogs({"sol": "gpt-6.1-sol"})
        r = self.run_xagent("codex", "exec", "-m", "astra", "q", CODEX_HOME=None)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.records(), [])
        self.assertEqual(self.events(), [])
        self.assertEqual(len(self.notes(r.stderr, "pass a full model slug")), 1)


class RobustnessTests(XagentTestCase):
    def test_no_env_still_runs(self):
        r = self.run_xagent("claude", "-p", "hi", VANTAGE_XAGENT_LOG=None, FAKE_STDOUT="fine\n", FAKE_EXIT="4")
        self.assertEqual((r.returncode, r.stdout), (4, b"fine\n"))
        self.assertFalse(os.path.exists(self.log))
        self.assertNotIn(b"registration", r.stderr)
        self.assertEqual(self.records()[0]["argv"][0], "--session-id")

    def assert_unregistered_but_same(self, log_path, expect_stderr_note=True):
        r = self.run_xagent("codex", "exec", "q", VANTAGE_XAGENT_LOG=log_path, FAKE_LAST="SAME", FAKE_EXIT="5")
        self.assertEqual(r.returncode, 5)
        self.assertEqual(r.stdout, b"SAME\n")
        notes = [l for l in r.stderr.decode().splitlines() if "registration skipped" in l]
        self.assertEqual(len(notes), 1 if expect_stderr_note else 0, r.stderr)
        self.assertIn(("[xagent] session=%s" % THREAD_ID).encode(), r.stderr)

    def test_missing_parent_dir_is_not_created(self):
        missing = os.path.join(self.tmp, "nope", "registry.jsonl")
        self.assert_unregistered_but_same(missing)
        self.assertFalse(os.path.exists(os.path.dirname(missing)))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores file modes")
    def test_unwritable_log(self):
        with open(self.log, "w"):
            pass
        os.chmod(self.log, 0o400)
        self.assert_unregistered_but_same(self.log)
        self.assertEqual(os.path.getsize(self.log), 0)

    def test_new_file_mode_0600(self):
        self.run_xagent("claude", "-p", "hi")
        self.assertEqual(stat.S_IMODE(os.stat(self.log).st_mode), 0o600)

    def test_appends_to_existing_file(self):
        with open(self.log, "w") as fh:
            fh.write('{"v":99,"type":"future"}\n')
        self.run_xagent("claude", "-p", "a")
        self.run_xagent("grok", "-p", "b")
        with open(self.log) as fh:
            lines = fh.read().splitlines()
        self.assertEqual(lines[0], '{"v":99,"type":"future"}')
        kinds = [json.loads(l)["type"] for l in lines[1:]]
        self.assertEqual(kinds, ["start", "child", "end", "start", "child", "end"])

    def test_exit_codes_propagate(self):
        for harness, args in (("claude", ["-p", "x"]), ("grok", ["-p", "x"]), ("codex", ["exec", "x"])):
            for path in (self.log, self.record):
                if os.path.exists(path):
                    os.remove(path)
            r = self.run_xagent(harness, *args, FAKE_EXIT="3")
            self.assertEqual(r.returncode, 3, harness)
            self.assertEqual(self.events()[-1]["exit_code"], 3)

    def test_nested_parent_run_id(self):
        r = self.run_xagent("grok", "-p", "outer", FAKE_NEST=json.dumps(["claude", "-p", "inner"]))
        self.assertEqual(r.returncode, 0, r.stderr)
        events = self.events()
        starts = [e for e in events if e["type"] == "start"]
        self.assertEqual([s["harness"] for s in starts], ["grok", "claude"])
        outer, inner = starts
        self.assertIsNone(outer["parent_run_id"])
        self.assertEqual(inner["parent_run_id"], outer["run_id"])
        claude_rec = [x for x in self.records() if x["name"] == "claude"][0]
        grok_rec = [x for x in self.records() if x["name"] == "grok"][0]
        self.assertEqual(claude_rec["parent_env"], inner["run_id"])
        for run, rec in ((outer, grok_rec), (inner, claude_rec)):
            mine = [e for e in events if e["run_id"] == run["run_id"]]
            self.assertEqual([e["type"] for e in mine], ["start", "child", "end"])
            self.assertEqual(mine[1]["pid"], rec["pid"])
        # the inner run lives entirely inside the outer one
        order = [(e["type"], e["run_id"]) for e in events]
        self.assertLess(order.index(("start", outer["run_id"])), order.index(("start", inner["run_id"])))
        self.assertLess(order.index(("end", inner["run_id"])), order.index(("end", outer["run_id"])))

    def test_binary_fallback_and_missing(self):
        os.remove(os.path.join(self.bin, "claude"))
        r = self.run_xagent("claude", "-p", "x")
        self.assertEqual(r.returncode, 127)
        self.assertIn(b"command not found", r.stderr)
        self.assertFalse(os.path.exists(self.log))
        fallback = os.path.join(self.home, ".local", "bin", "claude")
        os.makedirs(os.path.dirname(fallback))
        self.install_fake(fallback, FAKE_CLI % {"python": sys.executable, "thread": THREAD_ID})
        r = self.run_xagent("claude", "-p", "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.records()[0]["name"], "claude")

    def test_unlaunchable_binary_registers_start_and_end_only(self):
        with open(os.path.join(self.bin, "grok"), "w") as fh:
            fh.write("#!/nonexistent/interpreter\n")
        r = self.run_xagent("grok", "-p", "x")
        self.assertEqual(r.returncode, 127)
        self.assertIn(b"cannot run", r.stderr)
        events = self.events()
        self.assertEqual([e["type"] for e in events], ["start", "end"])
        self.assertEqual(events[1]["exit_code"], 127)

    def test_usage_errors(self):
        r = subprocess.run([sys.executable, XAGENT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 2)
        r = subprocess.run([sys.executable, XAGENT, "gemini", "-p", "x"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 2)
        r = subprocess.run([sys.executable, XAGENT, "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 0)
        self.assertIn(b"xagent", r.stdout)


def default_signals():
    """preexec_fn: start the wrapper with default dispositions, whatever the test runner has."""
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, signal.SIG_DFL)


class PaneFallbackTests(XagentTestCase):
    SID = "01a0ce7b-499d-7000-b226-dcad6d0fb85b"

    def fake_tmux(self, output, key=""):
        # window-local options only (show-options -w without -A): "" = not set on the window
        self.install_fake(os.path.join(self.bin, "tmux"),
                          "#!/bin/sh\necho \"$*\" >> %s/tmux.args\n"
                          "case \"$*\" in *@vantage_xagent_key*) v='%s';; *) v='%s';; esac\n"
                          "[ -n \"$v\" ] && printf '%%s\\n' \"$v\"\nexit 0\n"
                          % (self.tmp, key, output))

    def test_pane_label_locates_log_when_env_missing(self):
        os.makedirs(os.path.join(self.home, ".vantage"))
        self.fake_tmux(self.SID)
        r = self.run_xagent("grok", "-p", "x", VANTAGE_XAGENT_LOG=None,
                            TMUX="/tmp/tmux-1/default,1,0", TMUX_PANE="%7")
        self.assertEqual(r.returncode, 0, r.stderr)
        log = os.path.join(self.home, ".vantage", "agent_xagent", self.SID + ".jsonl")
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(log)).st_mode), 0o700)
        self.assertEqual([e["type"] for e in self.events(log)], ["start", "child", "end"])
        with open(os.path.join(self.tmp, "tmux.args")) as fh:
            self.assertIn("show-options -wqv -t %7 @vantage_sid", fh.read())

    def test_xagent_key_option_wins_over_rotated_sid(self):
        key = "01a0ce7b-0000-7000-8000-000000000001"
        os.makedirs(os.path.join(self.home, ".vantage"))
        self.fake_tmux(self.SID, key=key)                   # after a resume the two differ
        r = self.run_xagent("grok", "-p", "x", VANTAGE_XAGENT_LOG=None,
                            TMUX="/tmp/t,1,0", TMUX_PANE="%7")
        self.assertEqual(r.returncode, 0, r.stderr)
        log = os.path.join(self.home, ".vantage", "agent_xagent", key + ".jsonl")
        self.assertEqual([e["type"] for e in self.events(log)], ["start", "child", "end"])

    def test_env_wins_over_pane_label(self):
        os.makedirs(os.path.join(self.home, ".vantage"))
        self.fake_tmux(self.SID)
        self.run_xagent("grok", "-p", "x", TMUX="/tmp/t,1,0", TMUX_PANE="%7")
        self.assertTrue(self.events())
        self.assertFalse(os.path.exists(os.path.join(self.home, ".vantage", "agent_xagent")))

    def test_non_vantage_pane_is_not_registered(self):
        os.makedirs(os.path.join(self.home, ".vantage"))
        self.fake_tmux("")                                   # window has no @vantage_sid
        r = self.run_xagent("grok", "-p", "x", VANTAGE_XAGENT_LOG=None,
                            TMUX="/tmp/t,1,0", TMUX_PANE="%7")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.home, ".vantage", "agent_xagent")))

    def test_no_state_dir_no_registration(self):
        self.fake_tmux(self.SID)
        r = self.run_xagent("grok", "-p", "x", VANTAGE_XAGENT_LOG=None,
                            TMUX="/tmp/t,1,0", TMUX_PANE="%7")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.home, ".vantage")))


class SignalTests(XagentTestCase):
    def spawn_sleeping(self, prefix=(), **extra):
        ready = os.path.join(self.tmp, "ready")
        env = self.env(FAKE_SLEEP="30", FAKE_READY=ready, **extra)
        proc = subprocess.Popen(list(prefix) + [sys.executable, XAGENT, "claude", "-p", "x"], env=env,
                                cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                preexec_fn=default_signals)
        deadline = time.time() + 20
        while not os.path.exists(ready):
            if time.time() > deadline or proc.poll() is not None:
                proc.kill()
                self.fail("fake child never became ready")
            time.sleep(0.05)
        return proc

    def test_signal_death_records_signal(self):
        for sig, name in ((signal.SIGTERM, "SIGTERM"), (signal.SIGINT, "SIGINT"), (signal.SIGHUP, "SIGHUP")):
            for path in (self.log, self.record, os.path.join(self.tmp, "ready")):
                if os.path.exists(path):
                    os.remove(path)
            proc = self.spawn_sleeping()
            child_pid = self.records()[0]["pid"]
            self.assertFalse(self.records()[0]["hup_ignored"])
            proc.send_signal(sig)
            proc.communicate(timeout=20)
            self.assertEqual(proc.returncode, 128 + sig, name)
            start, _, end = self.one_run()
            self.assertEqual(start["pid"], proc.pid)
            self.assertEqual((end["exit_code"], end["signal"]), (None, name))
            self.assertRaises(OSError, os.kill, child_pid, 0)

    def test_nohup_sighup_ignore_reaches_child(self):
        """Under nohup the wrapper keeps SIGHUP ignored, so the child inherits the ignore."""
        proc = self.spawn_sleeping(prefix=["/usr/bin/nohup"])
        try:
            rec = self.records()[0]
            self.assertTrue(rec["hup_ignored"], "child must inherit SIGHUP=SIG_IGN")
            self.assertEqual(rec["ppid"], proc.pid)       # nohup exec'd the wrapper in place
            proc.send_signal(signal.SIGHUP)
            time.sleep(0.5)
            self.assertIsNone(proc.poll(), "wrapper must survive SIGHUP under nohup")
            os.kill(rec["pid"], 0)                        # child still alive
        finally:
            proc.send_signal(signal.SIGTERM)             # still forwarded
            proc.communicate(timeout=20)
        self.assertEqual(proc.returncode, 128 + signal.SIGTERM)
        start, _, end = self.one_run()
        self.assertEqual((end["exit_code"], end["signal"]), (None, "SIGTERM"))
        self.assertRaises(OSError, os.kill, rec["pid"], 0)

    def test_child_that_handles_signal_keeps_its_exit_code(self):
        proc = self.spawn_sleeping(FAKE_TRAP="7")
        proc.send_signal(signal.SIGTERM)
        proc.communicate(timeout=20)
        self.assertEqual(proc.returncode, 7)
        self.assertIn({"name": "claude", "trapped": int(signal.SIGTERM)}, self.records())
        end = self.one_run()[2]
        self.assertEqual((end["exit_code"], end["signal"]), (7, None))


if __name__ == "__main__":
    if PARSE_LINE is None:
        sys.stderr.write("note: %s absent; parse_line contract check skipped\n" % VANTAGE_TREE)
    unittest.main(verbosity=1)
