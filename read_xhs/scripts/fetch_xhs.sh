#!/usr/bin/env bash
# fetch_xhs.sh <xhs-post-url>
#
# Downloads a Xiaohongshu (小红书) note's HTML and all post images into
#   /tmp/xhs/<post-id>/
# and prints that directory path on stdout. The agent then reads each
# img*.jpg with the Read tool — those images carry the substantive content.
#
# meta.txt fields are best-effort grep extraction (title / author / desc /
# stats). The caption is usually short or just hashtags; trust images first.
# Comments are intentionally not extracted.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <xiaohongshu-post-url>" >&2
  exit 2
fi

url=$1

# XHS blocks the user's default HTTPS proxy; force a direct connection.
unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy ALL_PROXY all_proxy

# Post id is the path segment after /explore/ or /discovery/item/.
post_id=$(printf '%s' "$url" | sed -nE 's#.*/(explore|discovery/item)/([a-f0-9]+).*#\2#p')
if [[ -z "$post_id" ]]; then
  echo "could not extract post id from URL: $url" >&2
  exit 3
fi

out=/tmp/xhs/$post_id
mkdir -p "$out"
html=$out/page.html

ua='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
curl -sL --max-time 30 -A "$ua" "$url" -o "$html"

if [[ ! -s "$html" ]]; then
  echo "empty response — XHS may have returned a login wall or rate-limited" >&2
  exit 4
fi

# Best-effort metadata. Take the first match — sidebar recommendations and
# footer ICP links share the same field names but appear later in the doc.
title=$(grep -oE '<title>[^<]*</title>' "$html" | head -1 | sed 's#<title>##;s# - 小红书</title>##;s#</title>##')
author=$(grep -oE '"nickname":"[^"]*"' "$html" | head -1 | sed 's/"nickname":"//;s/"$//')
desc=$(grep -oE '"desc":"[^"]*"' "$html" | head -1 | sed 's/"desc":"//;s/"$//')
liked=$(grep -oE '"likedCount":"[^"]*"' "$html" | head -1 | sed 's/.*:"//;s/"//')
collected=$(grep -oE '"collectedCount":"[^"]*"' "$html" | head -1 | sed 's/.*:"//;s/"//')
shared=$(grep -oE '"shareCount":"[^"]*"' "$html" | head -1 | sed 's/.*:"//;s/"//')

{
  printf 'url: %s\n' "$url"
  printf 'post_id: %s\n' "$post_id"
  printf 'title: %s\n' "$title"
  printf 'author: %s\n' "$author"
  printf 'liked: %s  collected: %s  shared: %s\n' "$liked" "$collected" "$shared"
  printf 'desc: %s\n' "$desc"
} > "$out/meta.txt"

# Image URLs: each main-image object carries a `urlDefault` field. The nested
# infoList objects use the field name `url`, so a global grep for urlDefault
# only hits one entry per image and avoids the thumbnail variants.
# bash 3.2 (macOS default) has no `mapfile`; use a portable while-read loop.
url_list=$(grep -oE '"urlDefault":"[^"]*"' "$html" \
  | sed 's/"urlDefault":"//;s/"$//;s/\\u002F/\//g')

if [[ -z "$url_list" ]]; then
  # No images → likely a video-only note. Surface that explicitly; the skill
  # body tells the agent how to react.
  echo "no_images_found" > "$out/kind"
  echo "$out"
  exit 0
fi

i=1
while IFS= read -r u; do
  [[ -z "$u" ]] && continue
  curl -sL --max-time 30 -A "$ua" -o "$out/img${i}.jpg" "$u"
  i=$((i+1))
done <<< "$url_list"

printf 'images: %d\n' "$((i-1))" >> "$out/meta.txt"
echo "$out"
