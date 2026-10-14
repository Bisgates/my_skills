#!/usr/bin/env python3
"""Make first-screen thumbnails for project-level HTML designs (standard library only)."""
import argparse, os, shutil, signal, subprocess, tempfile, threading, time
from pathlib import Path

ROOT_LINK = os.path.expanduser("~/project/build_with_opus/design")
failed = {}
_active = set()
_active_lock = threading.Lock()
_cleanup_lock = threading.Lock()
_stopping = threading.Event()


def find_chrome():
    if os.environ.get("DESIGN_HUB_CHROME"):
        return os.path.expanduser(os.environ["DESIGN_HUB_CHROME"])
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.isfile(mac) and os.access(mac, os.X_OK):
        return mac
    return shutil.which("chromium") or shutil.which("google-chrome")


def thumb_path(path):
    return os.fspath(path)[:-len(".html")] + ".thumb.png"


def needs_thumb(html_mtime, thumb_mtime, force=False):
    return force or thumb_mtime is None or thumb_mtime < html_mtime


def find_candidates(root, project=None, force=False):
    candidates = []
    for name in sorted(os.listdir(root)):
        pdir = os.path.join(root, name)
        if name.startswith(".") or name.endswith("_parts") or not os.path.isdir(pdir):
            continue
        if project is not None and name != project:
            continue
        for fn in sorted(os.listdir(pdir)):
            path = os.path.join(pdir, fn)
            if fn.startswith(".") or not fn.lower().endswith(".html") or not os.path.isfile(path):
                continue
            thumb = thumb_path(path)
            try:
                html_mtime = os.path.getmtime(path)
                thumb_mtime = os.path.getmtime(thumb) if os.path.isfile(thumb) else None
            except OSError:
                continue
            if needs_thumb(html_mtime, thumb_mtime, force):
                if failed.get(path) != html_mtime:
                    candidates.append((path, thumb, html_mtime))
    candidates.sort(key=lambda c: (-c[2], c[0]))
    return [(path, thumb) for path, thumb, _ in candidates]


def clean_temps(root, project=None):
    cutoff = time.time() - 600
    for name in os.listdir(root):
        pdir = os.path.join(root, name)
        if name.startswith(".") or name.endswith("_parts") or not os.path.isdir(pdir):
            continue
        if project is not None and name != project:
            continue
        for fn in os.listdir(pdir):
            if fn.startswith(".thumb-") and fn.endswith(".png"):
                path = os.path.join(pdir, fn)
                try:
                    if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                        os.unlink(path)
                except OSError:
                    pass


def complete_png(path):
    try:
        with open(path, "rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                return False
            f.seek(-12, os.SEEK_END)
            return f.read() == b"\x00\x00\x00\x00IEND\xaeB`\x82"
    except OSError:
        return False


def stop_process(proc):
    with _cleanup_lock:
        if getattr(proc, "_thumb_stopped", False):
            return
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            proc.poll()  # reap the group leader before checking whether the group is gone
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                break
            time.sleep(.05)
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.wait()
        proc._thumb_stopped = True


def stop_all():
    with _active_lock:
        _stopping.set()  # registration and shutdown share the same lock
        processes = list(_active)
    for proc in processes:
        stop_process(proc)


def log_tail(log):
    log.seek(0, os.SEEK_END)
    log.seek(max(0, log.tell() - 4096))
    return " | ".join(log.read().decode("utf-8", "replace").splitlines()[-5:])


def capture(path, thumb, chrome):
    fd, tmp = tempfile.mkstemp(prefix=".thumb-", suffix=".png", dir=os.path.dirname(thumb))
    os.close(fd)
    proc = None
    try:
        with tempfile.TemporaryDirectory(prefix="design-thumb-") as profile, tempfile.TemporaryFile() as log:
            cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   "--window-size=1280,820", "--screenshot=" + tmp, "--user-data-dir=" + profile,
                   "--virtual-time-budget=3000", Path(path).resolve().as_uri()]
            try:
                with _active_lock:
                    if _stopping.is_set():
                        return False, "stopping"
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=log, start_new_session=True)
                    _active.add(proc)
                deadline, last_size = time.monotonic() + 40, None
                message, ready = "timeout (40s)", False
                while not _stopping.is_set() and time.monotonic() < deadline:
                    size = os.path.getsize(tmp)
                    if size == last_size and complete_png(tmp):
                        ready = True
                        break
                    last_size = size
                    if proc.poll() is not None:
                        ready = complete_png(tmp)  # PNG wins over a nonzero Chrome exit
                        message = "Chrome exit %s without a complete PNG" % proc.returncode
                        break
                    time.sleep(.25)
            finally:
                if proc is not None:
                    stop_process(proc)
                    with _active_lock:
                        _active.discard(proc)
            if ready:
                os.replace(tmp, thumb)
                return True, "saved"
            tail = log_tail(log)
            return False, message + (": " + tail if tail else "")
    except OSError as e:
        return False, str(e)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def make_thumbs(root, project=None, limit=None, force=False, chrome=None):
    chrome = chrome or find_chrome()
    if not chrome:
        return []
    clean_temps(root, project)
    candidates = find_candidates(root, project, force)
    if limit is not None:
        candidates = candidates[:max(0, limit)]
    results = []
    for path, thumb in candidates:
        if _stopping.is_set():
            break
        stamp = os.path.getmtime(path)
        ok, message = capture(path, thumb, chrome)
        if not ok:
            failed[path] = stamp
        else:
            failed.pop(path, None)
        print("%s %s: %s" % ("OK" if ok else "FAIL", thumb, message), flush=True)
        results.append((thumb, ok))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--root", default=os.environ.get("DESIGN_CHOICE_ROOT") or ROOT_LINK)
    args = parser.parse_args()
    chrome = find_chrome()
    if not chrome:
        print("Chrome not found: install Google Chrome, chromium or google-chrome.")
        return 2
    results = make_thumbs(os.path.realpath(args.root), args.project, args.limit, args.force, chrome)
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
