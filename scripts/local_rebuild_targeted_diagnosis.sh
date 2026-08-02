#!/usr/bin/env bash
set -Eeuo pipefail

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
OS_ROOT="${EIGHTX8_OS_ROOT:-/root/8x8-os}"
RELAY_ROOT="${EIGHTX8_RELAY_ROOT:-/root/8x8-flashpoint-relay}"
OUTROOT="${EIGHTX8_DIAG_OUTPUT:-/root/.8x8-competition/diagnostics}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTDIR="$OUTROOT/$STAMP"
RECEIPT="$OUTDIR/TARGETED_LOCAL_DIAGNOSIS.txt"
SERVICES=(hermes-gateway jarvis-continuity-supervisor-v1 studio)
PORTS=(3000 8085 8086 8099 8360 9120)
PATHS=(/healthz /health /api/health /status /api/status /)

umask 077
mkdir -p "$OUTDIR"

redact() {
  sed -E \
    -e 's#([Bb]earer[[:space:]]+)[A-Za-z0-9._~+/=-]+#\1<redacted>#g' \
    -e 's#[0-9]{6,12}:[A-Za-z0-9_-]{20,}#<redacted-telegram-token>#g' \
    -e 's#^([[:space:]]*(export[[:space:]]+)?[A-Za-z_][A-Za-z0-9_]*(TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|CREDENTIAL|AUTHORIZATION|COOKIE|PRIVATE_?KEY)[A-Za-z0-9_]*[[:space:]]*=).*#\1<redacted>#I' \
    -e 's#(https?://[^?[:space:]]+)\?[^[:space:]]+#\1?<redacted-query>#g'
}

section() {
  printf '\n============================================================\n'
  printf '%s\n' "$1"
  printf '============================================================\n'
}

{
  echo 'MISSION=8x8-targeted-local-diagnosis'
  echo 'MODE=READ_ONLY'
  echo "OBSERVED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo 'SERVICE_MUTATIONS=false'
  echo 'PROCESSES_SIGNALED=false'
  echo 'ENVIRONMENT_VALUES_READ=false'
  echo 'SECRET_VALUES_COLLECTED=false'

  section 'TARGET SERVICE STATUS'
  for name in "${SERVICES[@]}"; do
    service="$PREFIX/var/service/$name"
    echo "SERVICE=$name"
    "$PREFIX/bin/sv" status "$service" 2>&1 || true
    echo "SERVICE_DIR=$service"
    if [ -e "$service" ]; then
      echo "SERVICE_DIR_RESOLVED=$(readlink -f "$service" 2>/dev/null || true)"
    else
      echo 'SERVICE_DIR_PRESENT=false'
    fi
    if [ -f "$service/run" ]; then
      echo "RUN_SCRIPT_SHA256=$(sha256sum "$service/run" | awk '{print $1}')"
      echo 'RUN_SCRIPT_SANITIZED_BEGIN'
      sed -n '1,220p' "$service/run" | redact
      echo 'RUN_SCRIPT_SANITIZED_END'
    else
      echo 'RUN_SCRIPT_PRESENT=false'
    fi
    echo
  done

  section 'RELATED PROCESS TREE'
  ps -eo pid=,ppid=,user=,comm=,args= --sort=pid 2>/dev/null \
    | grep -Ei 'hermes|jarvis|studio|8x8-main|control.fabric|PID' \
    | redact || true

  section 'LISTENING TCP SOCKETS'
  if command -v ss >/dev/null 2>&1; then
    ss -ltnp 2>&1 | redact || true
  else
    echo 'SS_COMMAND=missing'
    echo 'PROC_NET_TCP_LISTENERS_BEGIN'
    awk 'NR==1 || $4=="0A" {print}' /proc/net/tcp /proc/net/tcp6 2>/dev/null || true
    echo 'PROC_NET_TCP_LISTENERS_END'
  fi

  section 'SAFE LOOPBACK HTTP PROBES'
  for port in "${PORTS[@]}"; do
    found=0
    for path in "${PATHS[@]}"; do
      url="http://127.0.0.1:${port}${path}"
      code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 "$url" 2>/dev/null || true)"
      [ -n "$code" ] || code=000
      echo "HTTP_PROBE port=$port path=$path code=$code"
      case "$code" in
        2*|3*|4*) found=1; break ;;
      esac
    done
    [ "$found" -eq 1 ] || true
  done

  section 'SANITIZED TARGET LOG TAILS'
  for name in "${SERVICES[@]}"; do
    service="$PREFIX/var/service/$name"
    candidates=(
      "$PREFIX/var/log/sv/$name/current"
      "$service/log/main/current"
      "$service/log/current"
    )
    found=0
    for log in "${candidates[@]}"; do
      [ -f "$log" ] || continue
      found=1
      echo "LOG_SERVICE=$name"
      echo "LOG_PATH=$log"
      echo "LOG_SIZE_BYTES=$(stat -c '%s' "$log" 2>/dev/null || echo unknown)"
      echo "LOG_SHA256=$(sha256sum "$log" | awk '{print $1}')"
      echo 'LOG_TAIL_SANITIZED_BEGIN'
      tail -n 120 "$log" 2>/dev/null | redact || true
      echo 'LOG_TAIL_SANITIZED_END'
    done
    [ "$found" -eq 1 ] || echo "LOG_SERVICE=$name LOG_PRESENT=false"
  done

  section 'REPOSITORY COMMAND DIAGNOSIS'
  for repo in "$RELAY_ROOT" "$OS_ROOT"; do
    echo "REPOSITORY=$repo"
    if [ ! -e "$repo" ]; then
      echo 'PRESENT=false'
      continue
    fi
    git -C "$repo" rev-parse --is-inside-work-tree 2>&1 | redact || true
    git -C "$repo" rev-parse HEAD 2>&1 | redact || true
    git -C "$repo" branch --show-current 2>&1 | redact || true
    echo 'GIT_STATUS_BEGIN'
    set +e
    timeout 20 git -C "$repo" status --porcelain=v1 --untracked-files=all 2>&1 | redact
    rc=${PIPESTATUS[0]}
    set -e
    echo "GIT_STATUS_RETURN_CODE=$rc"
    echo 'GIT_STATUS_END'
    echo 'GIT_SUBMODULE_STATUS_BEGIN'
    set +e
    timeout 20 git -C "$repo" submodule status --recursive 2>&1 | redact
    rc=${PIPESTATUS[0]}
    set -e
    echo "GIT_SUBMODULE_RETURN_CODE=$rc"
    echo 'GIT_SUBMODULE_STATUS_END'
  done

  section 'MSG205 INVENTORY'
  for root in "$OS_ROOT" /root/.hermes; do
    [ -d "$root" ] || continue
    echo "MSG205_ROOT=$root"
    find "$root" -maxdepth 9 \
      \( -path '*/.git' -o -path '*/node_modules' -o -path '*/.venv' -o -path '*/venv' -o -path '*/__pycache__' \) -prune -o \
      \( -iname '*msg205*' -o -iname '*genesis*census*' -o -iname '*census*genesis*' \) -print 2>/dev/null \
      | sort \
      | while IFS= read -r item; do
          [ -n "$item" ] || continue
          if [ -f "$item" ]; then
            echo "MSG205_FILE=$item"
            echo "MSG205_FILE_SIZE=$(stat -c '%s' "$item" 2>/dev/null || echo unknown)"
            echo "MSG205_FILE_SHA256=$(sha256sum "$item" | awk '{print $1}')"
            if [ "$(stat -c '%s' "$item" 2>/dev/null || echo 9999999)" -le 2097152 ]; then
              echo 'MSG205_MARKERS_SANITIZED_BEGIN'
              grep -Ein 'MSG205|FINAL|RECEIPT|COMPLETE|COMPLETED|PASS|FAIL|BLOCKED|GENESIS|CENSUS' "$item" 2>/dev/null \
                | head -n 80 \
                | redact || true
              echo 'MSG205_MARKERS_SANITIZED_END'
            fi
          elif [ -d "$item" ]; then
            echo "MSG205_DIRECTORY=$item"
            find "$item" -maxdepth 2 -type f -printf '%TY-%Tm-%TdT%TH:%TM:%TSZ %s %p\n' 2>/dev/null \
              | sort \
              | tail -n 120 \
              | redact || true
          fi
        done
  done

  section 'STORAGE'
  df -h "$RELAY_ROOT" 2>&1 || true
  df -P "$RELAY_ROOT" 2>/dev/null | awk 'NR==2 {print "DISK_USED_PERCENT=" $5; print "DISK_FREE_KB=" $4}'

  section 'DIAGNOSIS SUMMARY FLAGS'
  "$PREFIX/bin/sv" status "$PREFIX/var/service/hermes-gateway" 2>&1 \
    | grep -q '^run:' && echo 'HERMES_GATEWAY_RUNIT=RUN' || echo 'HERMES_GATEWAY_RUNIT=NOT_RUN'
  "$PREFIX/bin/sv" status "$PREFIX/var/service/jarvis-continuity-supervisor-v1" 2>&1 \
    | grep -q '^run:' && echo 'JARVIS_CONTINUITY_SUPERVISOR=RUN' || echo 'JARVIS_CONTINUITY_SUPERVISOR=DOWN'
  "$PREFIX/bin/sv" status "$PREFIX/var/service/studio" 2>&1 \
    | grep -q '^run:' && echo 'STUDIO_RUNIT=RUN' || echo 'STUDIO_RUNIT=DOWN'
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8085/ 2>/dev/null || true)"
  [ "$code" = 200 ] && echo 'STUDIO_HTTP_8085=200' || echo "STUDIO_HTTP_8085=${code:-000}"
  echo 'NEXT_ACTION=REVIEW_DIAGNOSIS_THEN_BUILD_BOUNDED_REPAIR'
} | tee "$RECEIPT"

printf 'DIAGNOSIS_RECEIPT=%s\n' "$RECEIPT"
printf 'DIAGNOSIS_RECEIPT_SHA256=%s\n' "$(sha256sum "$RECEIPT" | awk '{print $1}')"
printf 'DIAGNOSIS_MODE=READ_ONLY\n'
printf 'SERVICE_MUTATIONS=false\n'
printf 'PROCESSES_SIGNALED=false\n'
