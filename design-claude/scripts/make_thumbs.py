#!/usr/bin/env python3
"""Make first-screen thumbnails for project-level HTML designs (standard library only)."""
import argparse, os, shutil, subprocess, tempfile
from pathlib import Path

ROOT_LINK = os.path.expanduser("~/project/build_with_opus/design")


def find_chrome():
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
                candidates.append((path, thumb))
    return candidates


def capture(path, thumb, chrome):
    fd, tmp = tempfile.mkstemp(prefix=".thumb-", suffix=".png", dir=os.path.dirname(thumb))
    os.close(fd)
    try:
        with tempfile.TemporaryDirectory(prefix="design-thumb-") as profile, tempfile.TemporaryFile() as log:
            cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   "--window-size=1280,820", "--screenshot=" + tmp, "--user-data-dir=" + profile,
                   "--virtual-time-budget=3000", Path(path).resolve().as_uri()]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=log)
            timed_out = False
            try:
                code = proc.wait(timeout=40)
            except subprocess.TimeoutExpired:
                proc.kill()  # only this Popen's pid
                proc.wait()
                timed_out, code = True, proc.returncode
            if code != 0 and not timed_out:
                return False, "Chrome exit %s" % code
            with open(tmp, "rb") as f:
                if f.read(8) != b"\x89PNG\r\n\x1a\n":
                    return False, "timeout (40s)" if timed_out else "Chrome produced no PNG"
                f.seek(-12, os.SEEK_END)
                if f.read() != b"\x00\x00\x00\x00IEND\xaeB`\x82":
                    return False, "Chrome produced an incomplete PNG"
            os.replace(tmp, thumb)
            return True, "saved (Chrome stopped after 40s)" if timed_out else "saved"
    except OSError as e:
        return False, str(e)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def make_thumbs(root, project=None, limit=None, force=False, chrome=None):
    chrome = chrome or find_chrome()
    if not chrome:
        return []
    candidates = find_candidates(root, project, force)
    if limit is not None:
        candidates = candidates[:max(0, limit)]
    results = []
    for path, thumb in candidates:
        ok, message = capture(path, thumb, chrome)
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
