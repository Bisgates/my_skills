#!/usr/bin/env bash
# web-reach doctor — read-only. Confirms the proxy reaches each platform and
# which backend tools are installed. The two gates this skill gets wrong most
# often are "wrong proxy" and "missing tool"; this surfaces both in one shot.
#
# Usage: bash check.sh            (uses clash at 127.0.0.1:7890)
#        WEB_REACH_PROXY=... bash check.sh
set -u
P="${WEB_REACH_PROXY:-http://127.0.0.1:7890}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

echo "proxy = $P"
echo
echo "reachability (200/302 = ok; reddit 403 = anon-blocked, login needed; 000 = proxy not routing):"
probe() {
  code=$(curl -s -m 12 -o /dev/null -w '%{http_code}' -x "$P" -A "$UA" "$2" 2>/dev/null)
  printf '  %-14s %s\n' "$1" "${code:-ERR}"
}
probe youtube      https://www.youtube.com
probe x.com        https://x.com
probe reddit       https://www.reddit.com
probe xiaohongshu  https://www.xiaohongshu.com
probe bilibili     https://www.bilibili.com
probe jina         https://r.jina.ai/https://example.com

echo
echo "backend tools (MISSING zero-login ones block that platform; gated ones only matter once you use them):"
for t in yt-dlp gh node deno ffmpeg rdt twitter opencli bili; do
  printf '  %-10s ' "$t"
  if command -v "$t" >/dev/null 2>&1; then echo "ok"; else echo "MISSING"; fi
done

echo
echo "cookie extraction prereq:"
printf '  %-10s ' "pycryptodome"
python3 -c "import Cryptodome" 2>/dev/null && echo "ok" \
  || { python3 -c "import Crypto" 2>/dev/null && echo "ok (Crypto)" || echo "MISSING (pip install browser_cookie3)"; }
