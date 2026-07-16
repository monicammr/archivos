#!/usr/bin/env bash
# Sync master_run.log from the running brannmark_full_p1.py stdout (handles unlinked log path)
# and append a timestamped "last 10 lines" block every 3 minutes.
set -uo pipefail
LOG="${BRANNMARK_LOG_MASTER:-/workspace/BRANNMARK_P1/master_run.log}"
DIGEST="${BRANNMARK_LOG_DIGEST:-/workspace/BRANNMARK_P1/master_run_last10_every3m.log}"
INTERVAL="${BRANNMARK_LOG_INTERVAL_SEC:-180}"
# Pick the real Python worker (bash wrappers can embed the same substring in argv).
PATTERN="${BRANNMARK_LOG_PGRPAT:-brannmark_full_p1\\.py}"

mkdir -p "$(dirname "$LOG")"
touch "$LOG" "$DIGEST"

while true; do
  pid=""
  while read -r p; do
    exe=$(readlink -f "/proc/$p/exe" 2>/dev/null || true)
    case "$exe" in *python*) ;; *) continue ;; esac
    if [[ -r "/proc/$p/fd/1" ]]; then
      pid=$p
      break
    fi
  done < <(pgrep -f "$PATTERN" || true) || true
  cp_err=""
  if [[ -n "$pid" ]]; then
    # Keep the monitor alive across transient copy failures, but surface the
    # reason in the digest instead of discarding it silently.
    if ! cp_err=$(cp "/proc/$pid/fd/1" "$LOG" 2>&1); then
      cp_err="cp failed: ${cp_err}"
    else
      cp_err=""
    fi
  fi
  {
    echo "======== $(date -Iseconds) last 10 lines of $LOG (pid=${pid:-none}) ========"
    [[ -n "$cp_err" ]] && printf 'WARNING: %s\n' "$cp_err"
    tail -n 10 "$LOG" 2>/dev/null || printf '%s\n' "(unavailable)"
    echo
  } >>"$DIGEST"
  sleep "$INTERVAL"
done
