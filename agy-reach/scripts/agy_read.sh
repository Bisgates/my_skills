#!/usr/bin/env bash
# agy_read.sh — delegate a read/research task to `agy` (Antigravity CLI), whose
# server-side read_url_content reader (Gemini subscription) reads Reddit / X that
# ordinary WebFetch/curl can't. Prints agy's answer to stdout.
#
# Usage:   agy_read.sh "<prompt telling agy what to read and return>"
# Env:     AGY_READ_TIMEOUT  seconds before SIGALRM (default 240)
#
# Two sharp edges this wraps:
#  1. agy double-forks a `--bg-updater` child that keeps stdout open, so piping
#     `agy -p ... | cmd` never gets EOF and hangs. Writing to a file lets the
#     shell return as soon as the main agy process exits.
#  2. macOS ships no `timeout(1)`, so bound the run with a perl alarm.
set -uo pipefail

prompt="${1:-}"
if [ -z "$prompt" ]; then
  echo "usage: agy_read.sh \"<prompt>\"" >&2
  exit 2
fi

AGY="$(command -v agy || true)"
[ -n "$AGY" ] || AGY="$HOME/.local/bin/agy"
if [ ! -x "$AGY" ]; then
  echo "agy_read: 'agy' (Antigravity CLI) not found at PATH or ~/.local/bin/agy." >&2
  echo "agy_read: install/login agy, or fall back to the web-reach skill." >&2
  exit 127
fi

timeout_s="${AGY_READ_TIMEOUT:-240}"
tmp="$(mktemp -t agy_read.XXXXXX)"
trap 'rm -f "$tmp"' EXIT

# stdout -> file (never a pipe); stdin closed so it can't block on input.
perl -e 'alarm shift; exec @ARGV' "$timeout_s" \
  "$AGY" -p "$prompt" --dangerously-skip-permissions >"$tmp" 2>&1 </dev/null
rc=$?

cat "$tmp"
if [ "$rc" -eq 142 ]; then
  echo "[agy_read] timed out after ${timeout_s}s (SIGALRM); output above may be partial." >&2
fi
exit 0
