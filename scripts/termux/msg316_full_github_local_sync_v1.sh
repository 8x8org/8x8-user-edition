#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# MSG316 — Full GitHub -> Termux/Ubuntu local mirror sync V1
# Safe by design:
# - never reset --hard
# - never force checkout
# - never overwrite a dirty worktree
# - never push
# - fetches all branch refs + tags
# - fast-forwards only a clean default-branch checkout
# - records divergence and dirty state for later reconciliation
# - treats horbolsi/8x8 as historical/quarantined, never as deployment authority

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="${EIGHTX8_SYNC_ROOT:-$HOME/8x8-github-local}"
REPOS_ROOT="$ROOT/repos"
RECEIPT_ROOT="$ROOT/receipts/$TS"
MIN_FREE_GIB="${EIGHTX8_MIN_FREE_GIB:-8}"
SYNC_LFS="${EIGHTX8_SYNC_LFS:-0}"
SYNC_SUBMODULES="${EIGHTX8_SYNC_SUBMODULES:-1}"
OWNERS=(horbolsi 8x8org)

mkdir -p "$REPOS_ROOT" "$RECEIPT_ROOT"
exec 9>"$ROOT/.msg316-sync.lock"
if command -v flock >/dev/null 2>&1; then
  flock -n 9 || { echo "Another MSG316 sync is already running." >&2; exit 75; }
fi

log(){ printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$RECEIPT_ROOT/run.log"; }
fail(){ log "FATAL: $*"; exit 1; }

for bin in git gh jq sha256sum df awk sed sort; do
  command -v "$bin" >/dev/null 2>&1 || fail "Missing dependency: $bin"
done

gh auth status -h github.com >/dev/null 2>&1 || fail "GitHub CLI is not authenticated. Run: gh auth login"
gh auth setup-git >/dev/null 2>&1 || true

FREE_KB="$(df -Pk "$ROOT" | awk 'NR==2{print $4}')"
FREE_GIB="$((FREE_KB / 1024 / 1024))"
log "Root: $ROOT"
log "Free storage: ${FREE_GIB} GiB"
if [ "$FREE_GIB" -lt "$MIN_FREE_GIB" ]; then
  fail "Free storage below safety floor (${MIN_FREE_GIB} GiB). Refusing a fleet-wide clone/fetch."
fi

log "Enumerating GitHub repositories for: ${OWNERS[*]}"
: > "$RECEIPT_ROOT/repo_sources.ndjson"
for owner in "${OWNERS[@]}"; do
  gh repo list "$owner" --limit 200 \
    --json nameWithOwner,url,isPrivate,isArchived,defaultBranchRef,updatedAt \
    | jq -c '.[]' >> "$RECEIPT_ROOT/repo_sources.ndjson"
done

jq -s 'unique_by(.nameWithOwner) | sort_by(.nameWithOwner)' \
  "$RECEIPT_ROOT/repo_sources.ndjson" > "$RECEIPT_ROOT/ALL_REPOSITORIES.json"
REPO_COUNT="$(jq 'length' "$RECEIPT_ROOT/ALL_REPOSITORIES.json")"
log "Discovered repositories: $REPO_COUNT"

# Known estate classification. Discovery remains dynamic; this only prevents
# historical/quarantined material from becoming a deployment source by accident.
cat > "$RECEIPT_ROOT/CLASSIFICATION.json" <<'JSON'
{
  "rules": {
    "8x8org/8x8-user-edition": "CANONICAL_PUBLIC_SOURCE",
    "horbolsi/8x8-OS-Ecosystem": "HISTORICAL_PUBLIC_PRODUCTION_CARRIER",
    "horbolsi/8x8": "QUARANTINED_HISTORICAL_DO_NOT_DEPLOY",
    "default": "MIRROR_AND_RECONCILE"
  }
}
JSON

: > "$RECEIPT_ROOT/results.ndjson"

repo_result(){
  jq -cn \
    --arg repo "$1" --arg path "$2" --arg action "$3" --arg status "$4" \
    --arg branch "$5" --arg head "$6" --arg remote_head "$7" \
    --arg dirty "$8" --arg note "$9" \
    '{repo:$repo,path:$path,action:$action,status:$status,branch:$branch,head:$head,remote_default_head:$remote_head,dirty:$dirty,note:$note}' \
    >> "$RECEIPT_ROOT/results.ndjson"
}

while IFS=$'\t' read -r full url default_branch is_private is_archived; do
  [ -n "$full" ] || continue
  owner="${full%%/*}"
  name="${full#*/}"
  dest="$REPOS_ROOT/$owner/$name"
  mkdir -p "$REPOS_ROOT/$owner"

  classification="MIRROR_AND_RECONCILE"
  case "$full" in
    8x8org/8x8-user-edition) classification="CANONICAL_PUBLIC_SOURCE" ;;
    horbolsi/8x8-OS-Ecosystem) classification="HISTORICAL_PUBLIC_PRODUCTION_CARRIER" ;;
    horbolsi/8x8) classification="QUARANTINED_HISTORICAL_DO_NOT_DEPLOY" ;;
  esac

  log "[$full] class=$classification default=${default_branch:-UNKNOWN} private=$is_private archived=$is_archived"

  action="FETCH_ONLY"
  status="UNKNOWN"
  note=""

  if [ ! -d "$dest/.git" ]; then
    if [ -e "$dest" ]; then
      repo_result "$full" "$dest" "SKIP" "BLOCKED_NON_GIT_PATH" "" "" "" "true" "Destination exists but is not a git repository"
      log "[$full] BLOCKED: $dest exists and is not a git repository"
      continue
    fi
    log "[$full] cloning full repository"
    if ! git clone "$url.git" "$dest" >>"$RECEIPT_ROOT/run.log" 2>&1; then
      # gh repo list returns https://github.com/owner/repo without .git on some versions.
      if ! git clone "$url" "$dest" >>"$RECEIPT_ROOT/run.log" 2>&1; then
        repo_result "$full" "$dest" "CLONE" "FAILED" "" "" "" "false" "Clone failed"
        log "[$full] clone FAILED"
        continue
      fi
    fi
    action="CLONED"
  fi

  origin="$(git -C "$dest" remote get-url origin 2>/dev/null || true)"
  case "$origin" in
    "$url"|"$url.git"|"git@github.com:${full}.git"|"https://github.com/${full}.git") ;;
    *)
      repo_result "$full" "$dest" "SKIP" "REMOTE_MISMATCH" "" "$(git -C "$dest" rev-parse HEAD 2>/dev/null || true)" "" "true" "origin=$origin expected=$url"
      log "[$full] BLOCKED: origin mismatch: $origin"
      continue
      ;;
  esac

  # Fetch all remote branches and tags without touching checked-out files.
  if ! git -C "$dest" fetch --prune --tags origin '+refs/heads/*:refs/remotes/origin/*' >>"$RECEIPT_ROOT/run.log" 2>&1; then
    repo_result "$full" "$dest" "$action" "FETCH_FAILED" "$(git -C "$dest" branch --show-current || true)" "$(git -C "$dest" rev-parse HEAD 2>/dev/null || true)" "" "true" "git fetch failed"
    log "[$full] fetch FAILED"
    continue
  fi

  if [ "$SYNC_LFS" = "1" ] && command -v git-lfs >/dev/null 2>&1 && [ -f "$dest/.gitattributes" ] && grep -q 'filter=lfs' "$dest/.gitattributes"; then
    log "[$full] fetching Git LFS objects"
    git -C "$dest" lfs fetch --all origin >>"$RECEIPT_ROOT/run.log" 2>&1 || note="${note}LFS_FETCH_FAILED;"
  fi

  dirty="false"
  [ -n "$(git -C "$dest" status --porcelain=v1 --untracked-files=all)" ] && dirty="true"
  current_branch="$(git -C "$dest" branch --show-current || true)"
  local_head="$(git -C "$dest" rev-parse HEAD 2>/dev/null || true)"
  remote_head=""
  [ -n "$default_branch" ] && remote_head="$(git -C "$dest" rev-parse "origin/$default_branch" 2>/dev/null || true)"

  if [ "$classification" = "QUARANTINED_HISTORICAL_DO_NOT_DEPLOY" ]; then
    status="FETCHED_QUARANTINED"
    note="${note}No checkout mutation by policy;"
  elif [ "$dirty" = "true" ]; then
    status="FETCHED_DIRTY_PRESERVED"
    note="${note}Dirty worktree preserved; remote refs updated only;"
  elif [ -z "$default_branch" ]; then
    status="FETCHED_NO_DEFAULT_BRANCH"
  else
    if [ "$current_branch" != "$default_branch" ]; then
      status="FETCHED_NONDEFAULT_BRANCH_PRESERVED"
      note="${note}Current branch $current_branch preserved; default remote ref updated;"
    else
      if git -C "$dest" merge --ff-only "origin/$default_branch" >>"$RECEIPT_ROOT/run.log" 2>&1; then
        status="FAST_FORWARD_OK"
        action="${action}+FF_ONLY"
      else
        status="DIVERGED_NEEDS_RECONCILIATION"
        note="${note}ff-only merge refused; no history rewritten;"
      fi
    fi
  fi

  if [ "$SYNC_SUBMODULES" = "1" ] && [ "$dirty" = "false" ] && [ -f "$dest/.gitmodules" ]; then
    git -C "$dest" submodule sync --recursive >>"$RECEIPT_ROOT/run.log" 2>&1 || note="${note}SUBMODULE_SYNC_FAILED;"
    git -C "$dest" submodule update --init --recursive >>"$RECEIPT_ROOT/run.log" 2>&1 || note="${note}SUBMODULE_UPDATE_FAILED;"
  fi

  current_branch="$(git -C "$dest" branch --show-current || true)"
  local_head="$(git -C "$dest" rev-parse HEAD 2>/dev/null || true)"
  remote_head=""
  [ -n "$default_branch" ] && remote_head="$(git -C "$dest" rev-parse "origin/$default_branch" 2>/dev/null || true)"
  dirty="false"
  [ -n "$(git -C "$dest" status --porcelain=v1 --untracked-files=all)" ] && dirty="true"

  repo_result "$full" "$dest" "$action" "$status" "$current_branch" "$local_head" "$remote_head" "$dirty" "$note"
  log "[$full] $status local=$local_head remote_default=$remote_head dirty=$dirty"
done < <(jq -r '.[] | [.nameWithOwner,.url,(.defaultBranchRef.name // ""),(.isPrivate|tostring),(.isArchived|tostring)] | @tsv' "$RECEIPT_ROOT/ALL_REPOSITORIES.json")

jq -s '.' "$RECEIPT_ROOT/results.ndjson" > "$RECEIPT_ROOT/SYNC_RESULTS.json"

# Exact local git-state manifest. This hashes status text, not repository contents,
# so it remains practical across a multi-repository estate.
: > "$RECEIPT_ROOT/GIT_STATE_SHA256SUMS"
while IFS= read -r gitdir; do
  repo="${gitdir%/.git}"
  rel="${repo#$REPOS_ROOT/}"
  {
    git -C "$repo" rev-parse HEAD 2>/dev/null || true
    git -C "$repo" status --porcelain=v1 --untracked-files=all | LC_ALL=C sort
    git -C "$repo" remote -v | LC_ALL=C sort
  } | sha256sum | awk -v r="$rel" '{print $1"  "r}' >> "$RECEIPT_ROOT/GIT_STATE_SHA256SUMS"
done < <(find "$REPOS_ROOT" -type d -name .git -print | LC_ALL=C sort)

sha256sum "$RECEIPT_ROOT/ALL_REPOSITORIES.json" \
          "$RECEIPT_ROOT/SYNC_RESULTS.json" \
          "$RECEIPT_ROOT/GIT_STATE_SHA256SUMS" \
          > "$RECEIPT_ROOT/SHA256SUMS"

jq -n \
  --arg mission "MSG316" \
  --arg generated_at "$(date -u +%FT%TZ)" \
  --arg root "$ROOT" \
  --argjson repo_count "$REPO_COUNT" \
  --argjson lfs "$( [ "$SYNC_LFS" = 1 ] && echo true || echo false )" \
  --argjson submodules "$( [ "$SYNC_SUBMODULES" = 1 ] && echo true || echo false )" \
  '{mission:$mission,generated_at:$generated_at,root:$root,repo_count:$repo_count,lfs_synced:$lfs,submodules_synced:$submodules,destructive_reset:false,push_performed:false,whole_system_complete:false}' \
  > "$RECEIPT_ROOT/RECEIPT.json"

ln -sfn "$RECEIPT_ROOT" "$ROOT/LATEST_RECEIPT"

log "============================================================"
log "MSG316 GITHUB LOCAL SYNC COMPLETE"
log "Repositories discovered: $REPO_COUNT"
log "Receipt: $RECEIPT_ROOT"
log "Results: $RECEIPT_ROOT/SYNC_RESULTS.json"
log "SHA256: $RECEIPT_ROOT/SHA256SUMS"
log "No pushes, hard resets, or forced history rewrites were performed."
log "Next gate: reconcile any DIRTY/DIVERGED/REMOTE_MISMATCH rows, then run the full test matrix."
log "============================================================"
