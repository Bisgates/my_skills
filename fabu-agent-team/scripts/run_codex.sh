#!/usr/bin/env bash
# Launch one fabu-codex worker (fabu-agent-team skill). Usage: run_codex.sh <name> <model> <timeout_sec> <prompt_file>
# Writes _tmp/agents/<name>.{out,log,final.md,rc}; stdin closed (codex hangs otherwise).
set -uo pipefail
ARC=${ARC:-$(pwd)}   # run from the arc dir or export ARC
NAME=$1; MODEL=$2; TMO=$3; PF=$4
D="$ARC/_tmp/agents"; mkdir -p "$D"
COMMON=$(cat "${COMMON_RULES:-$ARC/_tmp/common_rules.md}")
{ echo "$COMMON"; echo; cat "$PF"; } > "$D/$NAME.prompt.md"
FABUX_BIN="$(command -v fabux 2>/dev/null || true)"
if [ -z "$FABUX_BIN" ]; then
  SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  FABUX_BIN="$SCRIPT_DIR/fabux"
fi
TIMEOUT_BIN="$(command -v timeout || command -v gtimeout || true)"   # macOS: brew install coreutils
if [ -z "$TIMEOUT_BIN" ]; then echo "run_codex.sh: no timeout/gtimeout binary (macOS: brew install coreutils)" >&2; echo 127 > "$D/$NAME.rc"; exit 127; fi
echo "$(date +%F_%T) start $NAME model=$MODEL" >> "$D/$NAME.log"
"$TIMEOUT_BIN" "$TMO" "$FABUX_BIN" exec --model "$MODEL" -s danger-full-access -C "$ARC" -o "$D/$NAME.final.md" "$(cat "$D/$NAME.prompt.md")" < /dev/null > "$D/$NAME.out" 2>&1
rc=$?; echo "$rc" > "$D/$NAME.rc"
echo "$(date +%F_%T) end $NAME rc=$rc" >> "$D/$NAME.log"
