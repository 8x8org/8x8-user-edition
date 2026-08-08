#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="${EIGHTX8_SYNC_ROOT:-/root/8x8-github-local}"
WORK="$ROOT/repos"
META="$ROOT/github-metadata"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/receipts/${TS}-github-metadata-v2"
mkdir -p "$META" "$OUT"

log(){ printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }
command -v gh >/dev/null || { echo 'gh missing' >&2; exit 1; }
command -v jq >/dev/null || { echo 'jq missing' >&2; exit 1; }
gh auth status -h github.com >/dev/null 2>&1 || { echo 'GitHub auth missing' >&2; exit 1; }

# gh 2.46 has --paginate but not the newer --slurp flag. Stream pages to jq -s instead.
api_array(){
  local endpoint="$1" output="$2" err="$3"
  if gh api --paginate -H 'Accept: application/vnd.github+json' "$endpoint" 2>"$err" | jq -s 'add // []' >"$output"; then
    return 0
  fi
  printf '[]\n' >"$output"
  return 1
}

api_wrapped(){
  local endpoint="$1" key="$2" output="$3" err="$4"
  if gh api --paginate -H 'Accept: application/vnd.github+json' "$endpoint" 2>"$err" | jq -s --arg k "$key" '[.[] | .[$k][]?]' >"$output"; then
    return 0
  fi
  printf '[]\n' >"$output"
  return 1
}

mapfile -t REPOS < <(
  find "$WORK" -mindepth 2 -maxdepth 2 -type d | while read -r d; do
    git -C "$d" rev-parse --git-dir >/dev/null 2>&1 || continue
    printf '%s\n' "${d#$WORK/}"
  done | LC_ALL=C sort
)
printf '%s\n' "${REPOS[@]}" >"$OUT/REPOSITORIES.txt"
: >"$OUT/results.ndjson"
gh api rate_limit >"$OUT/RATE_LIMIT_BEFORE.json"

for REPO in "${REPOS[@]}"; do
  OWNER="${REPO%%/*}"; NAME="${REPO#*/}"; DEST="$META/$OWNER/$NAME"; mkdir -p "$DEST"
  ERRORS=0
  log "[$REPO] repository metadata"
  gh api -H 'Accept: application/vnd.github+json' "repos/$REPO" >"$DEST/repository.json" 2>"$DEST/repository.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/branches?per_page=100" "$DEST/branches.json" "$DEST/branches.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/tags?per_page=100" "$DEST/tags.json" "$DEST/tags.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/issues?state=all&per_page=100" "$DEST/issues-all.json" "$DEST/issues-all.err" || ERRORS=$((ERRORS+1))
  jq '[.[] | select(has("pull_request") | not)]' "$DEST/issues-all.json" >"$DEST/issues-only.json"
  api_array "repos/$REPO/issues/comments?per_page=100" "$DEST/issue-comments.json" "$DEST/issue-comments.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/pulls?state=all&per_page=100&sort=created&direction=asc" "$DEST/pulls.json" "$DEST/pulls.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/pulls/comments?per_page=100" "$DEST/pull-review-comments.json" "$DEST/pull-review-comments.err" || ERRORS=$((ERRORS+1))
  api_array "repos/$REPO/releases?per_page=100" "$DEST/releases.json" "$DEST/releases.err" || ERRORS=$((ERRORS+1))
  api_wrapped "repos/$REPO/actions/workflows?per_page=100" workflows "$DEST/workflows.json" "$DEST/workflows.err" || ERRORS=$((ERRORS+1))
  api_wrapped "repos/$REPO/actions/runs?per_page=100" workflow_runs "$DEST/workflow-runs.json" "$DEST/workflow-runs.err" || ERRORS=$((ERRORS+1))
  api_wrapped "repos/$REPO/actions/artifacts?per_page=100" artifacts "$DEST/artifacts.json" "$DEST/artifacts.err" || ERRORS=$((ERRORS+1))

  : >"$DEST/.reviews.ndjson"
  while read -r PR; do
    [ -n "$PR" ] || continue
    if ! gh api --paginate -H 'Accept: application/vnd.github+json' "repos/$REPO/pulls/$PR/reviews?per_page=100" 2>>"$DEST/pull-reviews.err" | jq -c --argjson pr "$PR" '.[] | . + {archived_pr_number:$pr}' >>"$DEST/.reviews.ndjson"; then
      ERRORS=$((ERRORS+1))
    fi
  done < <(jq -r '.[].number' "$DEST/pulls.json")
  if [ -s "$DEST/.reviews.ndjson" ]; then jq -s '.' "$DEST/.reviews.ndjson" >"$DEST/pull-reviews.json"; else printf '[]\n' >"$DEST/pull-reviews.json"; fi
  rm -f "$DEST/.reviews.ndjson"

  ISSUE_COUNT="$(jq 'length' "$DEST/issues-only.json")"
  COMMENT_COUNT="$(jq 'length' "$DEST/issue-comments.json")"
  PULL_COUNT="$(jq 'length' "$DEST/pulls.json")"
  REVIEW_COUNT="$(jq 'length' "$DEST/pull-reviews.json")"
  REVIEW_COMMENT_COUNT="$(jq 'length' "$DEST/pull-review-comments.json")"
  RELEASE_COUNT="$(jq 'length' "$DEST/releases.json")"
  WORKFLOW_COUNT="$(jq 'length' "$DEST/workflows.json")"
  RUN_COUNT="$(jq 'length' "$DEST/workflow-runs.json")"
  ARTIFACT_COUNT="$(jq 'length' "$DEST/artifacts.json")"
  ARTIFACT_BYTES="$(jq '[.[].size_in_bytes // 0] | add // 0' "$DEST/artifacts.json")"

  find "$DEST" -maxdepth 1 -type f -name '*.json' -print0 | sort -z | xargs -0 sha256sum >"$DEST/SHA256SUMS"
  jq -cn --arg repo "$REPO" --argjson issues "$ISSUE_COUNT" --argjson comments "$COMMENT_COUNT" --argjson pulls "$PULL_COUNT" --argjson reviews "$REVIEW_COUNT" --argjson review_comments "$REVIEW_COMMENT_COUNT" --argjson releases "$RELEASE_COUNT" --argjson workflows "$WORKFLOW_COUNT" --argjson workflow_runs "$RUN_COUNT" --argjson artifacts "$ARTIFACT_COUNT" --argjson artifact_bytes "$ARTIFACT_BYTES" --argjson errors "$ERRORS" '{repo:$repo,issues:$issues,issue_comments:$comments,pulls:$pulls,reviews:$reviews,review_comments:$review_comments,releases:$releases,workflows:$workflows,workflow_runs:$workflow_runs,artifacts:$artifacts,artifact_bytes:$artifact_bytes,errors:$errors}' >>"$OUT/results.ndjson"
  log "[$REPO] issues=$ISSUE_COUNT pulls=$PULL_COUNT reviews=$REVIEW_COUNT runs=$RUN_COUNT artifacts=$ARTIFACT_COUNT errors=$ERRORS"
done

jq -s '.' "$OUT/results.ndjson" >"$OUT/GITHUB_METADATA_RESULTS.json"
jq '{repositories:length,issues:([.[].issues]|add//0),issue_comments:([.[].issue_comments]|add//0),pulls:([.[].pulls]|add//0),reviews:([.[].reviews]|add//0),review_comments:([.[].review_comments]|add//0),releases:([.[].releases]|add//0),workflows:([.[].workflows]|add//0),workflow_runs:([.[].workflow_runs]|add//0),actions_artifacts:([.[].artifacts]|add//0),artifact_bytes:([.[].artifact_bytes]|add//0),repos_with_errors:([.[]|select(.errors>0)]|length)}' "$OUT/GITHUB_METADATA_RESULTS.json" >"$OUT/TOTALS.json"
gh api rate_limit >"$OUT/RATE_LIMIT_AFTER.json"
sha256sum "$OUT/REPOSITORIES.txt" "$OUT/GITHUB_METADATA_RESULTS.json" "$OUT/TOTALS.json" "$OUT/RATE_LIMIT_BEFORE.json" "$OUT/RATE_LIMIT_AFTER.json" >"$OUT/SHA256SUMS"
ln -sfn "$OUT" "$ROOT/LATEST_GITHUB_METADATA_RECEIPT"
cat "$OUT/TOTALS.json"
cat "$OUT/SHA256SUMS"
du -sh "$META"
df -h /root
echo MSG316_GITHUB_METADATA_ARCHIVE_V2_COMPLETE
