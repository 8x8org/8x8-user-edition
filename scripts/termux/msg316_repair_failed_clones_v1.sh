#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="${EIGHTX8_SYNC_ROOT:-/root/8x8-github-local}"
REPOS_ROOT="$ROOT/repos"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/receipts/${TS}-repair"
mkdir -p "$OUT"

log(){ printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$OUT/run.log"; }
fail(){ log "FATAL: $*"; exit 1; }

for bin in git gh jq sha256sum; do
  command -v "$bin" >/dev/null 2>&1 || fail "Missing dependency: $bin"
done

gh auth status -h github.com >/dev/null 2>&1 || fail "GitHub CLI not authenticated"
gh auth setup-git >/dev/null 2>&1 || true

TARGETS=(
  "horbolsi/8x8-OS-Ecosystem"
  "horbolsi/8x8-OS-unified"
)

: > "$OUT/results.ndjson"

for full in "${TARGETS[@]}"; do
  owner="${full%%/*}"
  name="${full#*/}"
  dest="$REPOS_ROOT/$owner/$name"
  mkdir -p "$REPOS_ROOT/$owner"

  log "[$full] inspecting"
  meta="$(gh repo view "$full" --json url,defaultBranchRef,isPrivate,isArchived)" || fail "Cannot read $full metadata"
  url="$(jq -r '.url' <<<"$meta")"
  default_branch="$(jq -r '.defaultBranchRef.name // empty' <<<"$meta")"

  if [ -e "$dest" ] && [ ! -e "$dest/.git" ]; then
    quarantine="${dest}.FAILED_CLONE_${TS}"
    log "[$full] preserving incomplete non-git destination at $quarantine"
    mv "$dest" "$quarantine"
  fi

  if [ ! -e "$dest/.git" ]; then
    tmp="${dest}.CLONE_TMP_${TS}"
    rm -rf "$tmp"
    log "[$full] cloning into temporary path"
    if ! gh repo clone "$full" "$tmp" >>"$OUT/run.log" 2>&1; then
      rm -rf "$tmp"
      jq -cn --arg repo "$full" --arg status "CLONE_FAILED" '{repo:$repo,status:$status}' >> "$OUT/results.ndjson"
      log "[$full] clone FAILED"
      continue
    fi
    mv "$tmp" "$dest"
  fi

  origin="$(git -C "$dest" remote get-url origin 2>/dev/null || true)"
  case "$origin" in
    "$url"|"$url.git"|"https://github.com/${full}.git"|"git@github.com:${full}.git") ;;
    *)
      jq -cn --arg repo "$full" --arg status "REMOTE_MISMATCH" --arg origin "$origin" '{repo:$repo,status:$status,origin:$origin}' >> "$OUT/results.ndjson"
      log "[$full] REMOTE_MISMATCH origin=$origin"
      continue
      ;;
  esac

  log "[$full] fetching all branches + tags"
  if ! git -C "$dest" fetch --prune --tags origin '+refs/heads/*:refs/remotes/origin/*' >>"$OUT/run.log" 2>&1; then
    jq -cn --arg repo "$full" --arg status "FETCH_FAILED" '{repo:$repo,status:$status}' >> "$OUT/results.ndjson"
    log "[$full] fetch FAILED"
    continue
  fi

  dirty=false
  [ -n "$(git -C "$dest" status --porcelain=v1 --untracked-files=all)" ] && dirty=true
  branch="$(git -C "$dest" branch --show-current || true)"
  head="$(git -C "$dest" rev-parse HEAD)"
  remote_head="$(git -C "$dest" rev-parse "origin/$default_branch" 2>/dev/null || true)"
  status="FETCHED"

  if [ "$dirty" = false ] && [ "$branch" = "$default_branch" ]; then
    if git -C "$dest" merge --ff-only "origin/$default_branch" >>"$OUT/run.log" 2>&1; then
      status="FAST_FORWARD_OK"
      head="$(git -C "$dest" rev-parse HEAD)"
    else
      status="DIVERGED_NEEDS_RECONCILIATION"
    fi
  elif [ "$dirty" = true ]; then
    status="FETCHED_DIRTY_PRESERVED"
  else
    status="FETCHED_NONDEFAULT_BRANCH_PRESERVED"
  fi

  jq -cn \
    --arg repo "$full" --arg status "$status" --arg branch "$branch" \
    --arg head "$head" --arg remote_head "$remote_head" --argjson dirty "$dirty" \
    '{repo:$repo,status:$status,branch:$branch,head:$head,remote_default_head:$remote_head,dirty:$dirty}' \
    >> "$OUT/results.ndjson"
  log "[$full] $status local=$head remote_default=$remote_head dirty=$dirty"
done

jq -s '.' "$OUT/results.ndjson" > "$OUT/REPAIR_RESULTS.json"

# Top-level repo count: repos/<owner>/<name>/.git lives at depth 3 from repos/.
TOP_LEVEL_COUNT="$(find "$REPOS_ROOT" -mindepth 3 -maxdepth 3 -type d -name .git -print | wc -l | tr -d ' ')"

# Count logical top-level repo directories with either .git dir or file.
LOGICAL_COUNT=0
while IFS= read -r d; do
  [ -e "$d/.git" ] && LOGICAL_COUNT=$((LOGICAL_COUNT+1))
done < <(find "$REPOS_ROOT" -mindepth 2 -maxdepth 2 -type d -print)

jq -n \
  --arg mission "MSG316_REPAIR" \
  --arg generated_at "$(date -u +%FT%TZ)" \
  --arg root "$ROOT" \
  --argjson top_level_git_dirs "$TOP_LEVEL_COUNT" \
  --argjson logical_repo_count "$LOGICAL_COUNT" \
  '{mission:$mission,generated_at:$generated_at,root:$root,top_level_git_dirs:$top_level_git_dirs,logical_repo_count:$logical_repo_count}' \
  > "$OUT/RECEIPT.json"

sha256sum "$OUT/REPAIR_RESULTS.json" "$OUT/RECEIPT.json" > "$OUT/SHA256SUMS"
ln -sfn "$OUT" "$ROOT/LATEST_REPAIR_RECEIPT"

log "MSG316 REPAIR COMPLETE"
log "Logical top-level repositories now present: $LOGICAL_COUNT"
log "Receipt: $OUT"
