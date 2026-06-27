#!/usr/bin/env python3
"""Extract decrypted cookies from the local Chrome (or Edge) profile on macOS.

WAL-aware (a just-completed login lives in Cookies-wal before it is checkpointed)
and decrypts cookie values with the browser's "Safe Storage" key from the macOS
keychain. Output goes to stdout only — nothing is written to disk and nothing
leaves the machine; the cookie only authenticates to the site it came from.
A one-time keychain prompt may appear ("security wants to use Chrome Safe
Storage"); the user must approve it.

Usage:
  extract_cookies.py <domain-suffix> [--browser chrome|edge]
                                     [--names a,b,c | --cookie-string] [--mask]

  --names a,b,c     print only those cookies as NAME=VALUE lines (for env export)
  --cookie-string   print a single 'k=v; k=v; …' header (all cookies for domain)
  --mask            mask values (first5…last3 + length) for safe display
  default           print a name<TAB>value table of every cookie for the domain

Requires pycryptodome(x) (ships with browser_cookie3): pip install browser_cookie3
"""
import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
except ImportError:  # pycryptodome (not the -x fork) installs under Crypto
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2

# subdir under ~/Library/Application Support, keychain account, keychain service
BROWSERS = {
    "chrome": ("Google/Chrome", "Chrome", "Chrome Safe Storage"),
    "edge": ("Microsoft Edge", "Microsoft Edge", "Microsoft Edge Safe Storage"),
}


def open_jar(browser):
    sub, account, service = BROWSERS[browser]
    base = os.path.expanduser(f"~/Library/Application Support/{sub}/Default")
    tmp = tempfile.mkdtemp()
    # copy the db AND its WAL/SHM so uncheckpointed (fresh) cookies are visible
    for ext in ("", "-wal", "-shm"):
        src = os.path.join(base, "Cookies" + ext)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(tmp, "c.db" + ext))
    con = sqlite3.connect(os.path.join(tmp, "c.db"))
    con.text_factory = bytes  # encrypted_value is a BLOB; skip auto UTF-8 decode
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # fold WAL into our copy
    except sqlite3.OperationalError:
        pass
    pw = subprocess.run(
        ["security", "find-generic-password", "-wa", account, "-s", service],
        capture_output=True, text=True, timeout=90,
    ).stdout.strip()
    if not pw:
        sys.exit(f"could not read '{service}' from keychain (prompt denied?)")
    key = PBKDF2(pw.encode(), b"saltysalt", dkLen=16, count=1003)
    return con, key, tmp


def decrypt(enc, plain, key):
    if not enc:
        return plain.decode("utf-8", "replace") if isinstance(plain, bytes) else (plain or "")
    if enc[:3] in (b"v10", b"v11"):
        dec = AES.new(key, AES.MODE_CBC, b" " * 16).decrypt(enc[3:])
        dec = dec[:-dec[-1]]  # strip PKCS7 padding
        try:
            return dec.decode("utf-8")
        except UnicodeDecodeError:
            return dec[32:].decode("utf-8", "replace")  # recent Chrome: 32-byte domain hash prefix
    return plain.decode("utf-8", "replace") if isinstance(plain, bytes) else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domain", help="host suffix, e.g. x.com or xiaohongshu.com")
    ap.add_argument("--browser", default="chrome", choices=list(BROWSERS))
    ap.add_argument("--names", help="comma-separated cookie names -> NAME=VALUE lines")
    ap.add_argument("--cookie-string", action="store_true", help="single 'k=v; …' header")
    ap.add_argument("--mask", action="store_true", help="mask values for display")
    a = ap.parse_args()

    con, key, tmp = open_jar(a.browser)
    cur = con.cursor()
    cur.execute(
        "SELECT name, encrypted_value, value FROM cookies WHERE host_key LIKE ?",
        ("%" + a.domain,),
    )
    jar = {}
    for name, enc, plain in cur.fetchall():
        name = name.decode() if isinstance(name, bytes) else name
        jar[name] = decrypt(enc, plain, key)
    shutil.rmtree(tmp, ignore_errors=True)

    if not jar:
        sys.exit(f"no cookies for *{a.domain} in {a.browser} — are you logged in there?")

    def show(v):
        return f"{v[:5]}…{v[-3:]}(len={len(v)})" if (a.mask and v) else v

    if a.names:
        for n in (x.strip() for x in a.names.split(",")):
            print(f"{n}={show(jar.get(n, ''))}")
    elif a.cookie_string:
        print("; ".join(f"{k}={show(v)}" for k, v in jar.items() if v))
    else:
        for k, v in sorted(jar.items()):
            print(f"{k}\t{show(v)}")


if __name__ == "__main__":
    main()
