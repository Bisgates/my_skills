#!/bin/zsh
# Concatenate accepted per-version PDFs into one review PDF, in list order.
# Generalized from a hand-kept _merge_all.sh: the list now lives in a text file
# next to the drafts, so accepting a new version = append one line and rerun.
#
# Usage: merge_pdf.sh <list.txt> <out.pdf>
#   list.txt: one PDF path per line, relative to the list file's directory;
#             blank lines and '#' comments are ignored.
set -euo pipefail
[[ $# -eq 2 ]] || { print -u2 "usage: merge_pdf.sh <list.txt> <out.pdf>"; exit 2; }
command -v pdfunite >/dev/null || { print -u2 "pdfunite not found (brew install poppler)"; exit 1; }

list=${1:A}; out=${2:A}
cd "${list:h}"
files=()
missing=0
while IFS= read -r line || [[ -n $line ]]; do
  line=${line%%#*}
  line="${line#"${line%%[![:space:]]*}"}"; line="${line%"${line##*[![:space:]]}"}"
  [[ -z $line ]] && continue
  if [[ -f $line ]]; then files+=("$line"); else print -u2 "missing: $line"; missing=1; fi
done < "$list"
(( missing == 0 )) || exit 1
(( ${#files} > 0 )) || { print -u2 "list is empty"; exit 1; }
pdfunite "${files[@]}" "$out"
print "$out (${#files} files)"
