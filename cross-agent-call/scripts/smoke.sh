#!/usr/bin/env bash
# Smoke-test headless calls to each agent harness CLI with a cheap echo-back prompt.
# Usage: smoke.sh [harness...]   harness in {grok, codex, claude}; no args = all three.
set -u

TIMEOUT=60
ALL_HARNESSES=(grok codex claude)
requested=("$@")
[ ${#requested[@]} -eq 0 ] && requested=("${ALL_HARNESSES[@]}")

# Run "$@" in background, capturing to $outfile; kill it if it runs past TIMEOUT
# seconds. macOS has no `timeout` binary, so this is the simple substitute.
run_with_timeout() {
  local outfile="$1"; shift
  "$@" >"$outfile" 2>&1 &
  local pid=$! waited=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 1
    waited=$((waited + 1))
    if [ "$waited" -ge "$TIMEOUT" ]; then
      kill "$pid" 2>/dev/null
      break
    fi
  done
  wait "$pid" 2>/dev/null
}

overall=0
for h in "${requested[@]}"; do
  case "$h" in
    grok)
      token="CROSSCALL-GROK-OK"
      cmd=(grok -p "Reply with exactly this token and nothing else: $token" -m "${GROK_MODEL:?Resolve and export GROK_MODEL from grok models first}" --output-format plain)
      ;;
    codex)
      token="CROSSCALL-CODEX-OK"
      # `command codex` so the user's interactive alias (--dangerously-bypass...) can't interfere.
      cmd=(command codex exec -s read-only -m "${CODEX_MODEL:?Resolve and export CODEX_MODEL from the model catalog first}" -c model_reasoning_effort=low "Reply with exactly this token and nothing else: $token")
      ;;
    claude)
      token="CROSSCALL-CLAUDE-OK"
      cmd=(claude -p "Reply with exactly this token and nothing else: $token")
      ;;
    *)
      echo "FAIL $h (unknown harness)"
      overall=1
      continue
      ;;
  esac

  outfile=$(mktemp)
  start=$(date +%s)
  run_with_timeout "$outfile" "${cmd[@]}"
  end=$(date +%s)
  secs=$((end - start))

  # codex wraps the answer in banner / "tokens used" lines and may echo the prompt
  # (which contains the token mid-sentence), so require the token as a whole line.
  if grep -qxF "$token" "$outfile"; then
    echo "PASS $h (${secs}s)"
  else
    echo "FAIL $h"
    tail -5 "$outfile" | sed 's/^/    /'
    overall=1
  fi
  rm -f "$outfile"
done

exit $overall
