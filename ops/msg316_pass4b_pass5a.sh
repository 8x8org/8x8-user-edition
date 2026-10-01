#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=/root/8x8-github-local
META="$ROOT/github-metadata"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
ART_ROOT="$ROOT/actions-artifacts"
OUT="$ROOT/receipts/${TS}-artifact-download-native-census"
TERMUX_HOME=/data/data/com.termux/files/home
UBUNTU_HOME=/root
ANDROID=/storage/emulated/0

mkdir -p "$ART_ROOT" "$OUT"

fail() { echo "ERROR: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"; }
for c in gh jq git sha256sum stat find sort du awk df column sed tr wc; do need "$c"; done
[ -d "$META" ] || fail "missing metadata root: $META"
[ -d "$ROOT/repos" ] || fail "missing repo root: $ROOT/repos"

echo "============================================================"
echo " MSG316 PASS 4B + PASS 5A"
echo " ACTIONS ARTIFACT PRESERVATION + NATIVE ESTATE CENSUS"
echo "============================================================"
echo
echo "=== STORAGE BEFORE ==="
df -h /root

###############################################################################
# PASS 4B — DOWNLOAD ALL CURRENTLY AVAILABLE ACTIONS ARTIFACTS
###############################################################################

echo
echo "============================================================"
echo " PASS 4B — AVAILABLE ACTIONS ARTIFACTS"
echo "============================================================"

: > "$OUT/artifact-download-results.ndjson"

while IFS= read -r FILE; do
    REPO="${FILE#$META/}"
    REPO="${REPO%/artifacts.json}"
    OWNER="${REPO%%/*}"
    NAME="${REPO#*/}"
    DEST="$ART_ROOT/$OWNER/$NAME"
    mkdir -p "$DEST"

    while IFS= read -r OBJ; do
        ID="$(jq -r '.id' <<<"$OBJ")"
        ANAME="$(jq -r '.name // "artifact"' <<<"$OBJ")"
        SIZE="$(jq -r '.size_in_bytes // 0' <<<"$OBJ")"
        SAFE_NAME="$(printf '%s' "$ANAME" | tr '/[:space:]' '__' | tr -cd 'A-Za-z0-9._-')"
        [ -n "$SAFE_NAME" ] || SAFE_NAME="artifact"
        ZIP="$DEST/${ID}__${SAFE_NAME}.zip"
        TMP="${ZIP}.partial"
        ERR="$OUT/artifact-${ID}.err"

        echo "[$REPO] artifact=$ID name=$ANAME expected=$SIZE"
        STATUS="FAILED"
        if [ -s "$ZIP" ]; then
            STATUS="ALREADY_PRESENT"
        else
            rm -f "$TMP" "$ERR"
            if gh api -H "Accept: application/vnd.github+json" \
                "repos/$REPO/actions/artifacts/$ID/zip" \
                > "$TMP" 2>"$ERR"; then
                if [ -s "$TMP" ]; then
                    mv "$TMP" "$ZIP"
                    STATUS="DOWNLOADED"
                else
                    rm -f "$TMP"
                    STATUS="EMPTY_RESPONSE"
                fi
            else
                rm -f "$TMP"
                STATUS="DOWNLOAD_FAILED"
            fi
        fi

        ACTUAL=0
        SHA=""
        if [ -f "$ZIP" ]; then
            ACTUAL="$(stat -c '%s' "$ZIP")"
            SHA="$(sha256sum "$ZIP" | awk '{print $1}')"
        fi

        jq -cn \
          --arg repo "$REPO" \
          --argjson id "$ID" \
          --arg name "$ANAME" \
          --arg status "$STATUS" \
          --arg path "$ZIP" \
          --arg sha256 "$SHA" \
          --argjson expected "$SIZE" \
          --argjson actual "$ACTUAL" \
          '{repo:$repo,artifact_id:$id,name:$name,status:$status,expected_bytes:$expected,downloaded_bytes:$actual,path:$path,sha256:$sha256}' \
          >> "$OUT/artifact-download-results.ndjson"
    done < <(jq -c '.[] | select(.expired != true)' "$FILE")
done < <(find "$META" -mindepth 3 -maxdepth 3 -type f -name artifacts.json | LC_ALL=C sort)

if [ -s "$OUT/artifact-download-results.ndjson" ]; then
    jq -s '.' "$OUT/artifact-download-results.ndjson" > "$OUT/ARTIFACT_DOWNLOAD_RESULTS.json"
else
    printf '[]\n' > "$OUT/ARTIFACT_DOWNLOAD_RESULTS.json"
fi

jq '{artifacts:length,downloaded:([.[]|select(.status=="DOWNLOADED")]|length),already_present:([.[]|select(.status=="ALREADY_PRESENT")]|length),failed:([.[]|select(.status!="DOWNLOADED" and .status!="ALREADY_PRESENT")]|length),downloaded_bytes:([.[].downloaded_bytes]|add // 0)}' \
  "$OUT/ARTIFACT_DOWNLOAD_RESULTS.json" > "$OUT/ARTIFACT_DOWNLOAD_TOTALS.json"

echo
echo "=== ARTIFACT DOWNLOAD TOTALS ==="
cat "$OUT/ARTIFACT_DOWNLOAD_TOTALS.json"

###############################################################################
# CORRECT GIT DATABASE MEASUREMENT
###############################################################################

echo
echo "============================================================"
echo " CORRECTED GIT DATABASE SIZES"
echo "============================================================"

: > "$OUT/GIT_DATABASE_SIZES_CORRECTED.tsv"
find "$ROOT/repos" -mindepth 2 -maxdepth 2 -type d | while read -r REPO; do
    git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || continue
    REL="${REPO#$ROOT/repos/}"
    GITDIR="$(git -C "$REPO" rev-parse --absolute-git-dir)"
    BYTES="$(du -sb "$GITDIR" | awk '{print $1}')"
    printf '%s\t%s\t%s\n' "$BYTES" "$REL" "$GITDIR"
done | sort -nr > "$OUT/GIT_DATABASE_SIZES_CORRECTED.tsv"
column -t -s "$(printf '\t')" "$OUT/GIT_DATABASE_SIZES_CORRECTED.tsv" || true

###############################################################################
# PASS 5A — NATIVE ESTATE READ-ONLY CENSUS
###############################################################################

echo
echo "============================================================"
echo " PASS 5A — NATIVE ESTATE CENSUS"
echo "============================================================"

for BASE in "$TERMUX_HOME" "$UBUNTU_HOME"; do
    LABEL="$(printf '%s' "$BASE" | sed 's#^/##; s#/#__#g')"
    echo "Scanning: $BASE"
    if [ ! -d "$BASE" ]; then
        : > "$OUT/${LABEL}__GIT_DIRS.txt"
        : > "$OUT/${LABEL}__ASSET_CANDIDATES.tsv"
        continue
    fi

    find "$BASE" -xdev -type d -name .git -print 2>/dev/null | LC_ALL=C sort > "$OUT/${LABEL}__GIT_DIRS.txt"
    find "$BASE" -xdev -type f \
      \( -iname '*.db' -o -iname '*.sqlite' -o -iname '*.sqlite3' -o -iname '*.json' -o -iname '*.jsonl' -o -iname '*.ndjson' \
      -o -iname '*.bundle' -o -iname '*.tar' -o -iname '*.tgz' -o -iname '*.zip' -o -iname '*.7z' \
      -o -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' -o -iname '*.webm' \
      -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.gif' \
      -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.m4a' -o -iname '*.flac' -o -iname '*.ogg' \
      -o -iname '*.glb' -o -iname '*.gltf' -o -iname '*.blend' -o -iname '*.onnx' -o -iname '*.safetensors' -o -iname '*.pt' -o -iname '*.pth' \) \
      -printf '%s\t%T@\t%p\n' 2>/dev/null | sort -nr > "$OUT/${LABEL}__ASSET_CANDIDATES.tsv"
done

echo
echo "=== ANDROID SHARED STORAGE TOP-LEVEL ==="
if [ -d "$ANDROID" ]; then
    find "$ANDROID" -mindepth 1 -maxdepth 2 -printf '%y\t%s\t%T@\t%p\n' 2>/dev/null | LC_ALL=C sort > "$OUT/ANDROID_TOP_LEVEL.tsv"
else
    : > "$OUT/ANDROID_TOP_LEVEL.tsv"
fi

: > "$OUT/NAMED_PROJECT_SIGNALS.tsv"
for BASE in "$TERMUX_HOME" "$UBUNTU_HOME" "$ANDROID"; do
    [ -d "$BASE" ] || continue
    find "$BASE" -maxdepth 6 \
      \( -iname '*8x8*' -o -iname '*studio*' -o -iname '*quran*' -o -iname '*earth*' -o -iname '*planet*' \
      -o -iname '*btc*' -o -iname '*bitcoin*' -o -iname '*trading*' -o -iname '*dashboard*' -o -iname '*world*' \
      -o -iname '*360*' -o -iname '*omniverse*' -o -iname '*agent*' -o -iname '*voice*' -o -iname '*memory*' \
      -o -iname '*message*' -o -iname '*receipt*' -o -iname '*backup*' -o -iname '*fabric*' \) \
      -printf '%y\t%s\t%T@\t%p\n' 2>/dev/null >> "$OUT/NAMED_PROJECT_SIGNALS.tsv"
done
LC_ALL=C sort -o "$OUT/NAMED_PROJECT_SIGNALS.tsv" "$OUT/NAMED_PROJECT_SIGNALS.tsv"

cat "$OUT/data__data__com.termux__files__home__GIT_DIRS.txt" "$OUT/root__GIT_DIRS.txt" 2>/dev/null | sort -u > "$OUT/ALL_LOCAL_GIT_DIRS.txt"
: > "$OUT/local-git-results.ndjson"

while IFS= read -r GITDIR; do
    [ -n "$GITDIR" ] || continue
    REPO="${GITDIR%/.git}"
    HEAD="$(git -C "$REPO" rev-parse HEAD 2>/dev/null || true)"
    BRANCH="$(git -C "$REPO" branch --show-current 2>/dev/null || true)"
    ORIGIN="$(git -C "$REPO" remote get-url origin 2>/dev/null || true)"
    DIRTY=false
    [ -z "$(git -C "$REPO" status --porcelain=v1 --untracked-files=all 2>/dev/null || true)" ] || DIRTY=true
    REF_COUNT="$(git -C "$REPO" for-each-ref 2>/dev/null | wc -l | tr -d ' ')"
    COMMIT_COUNT="$(git -C "$REPO" rev-list --all --count 2>/dev/null || echo 0)"
    jq -cn --arg path "$REPO" --arg origin "$ORIGIN" --arg head "$HEAD" --arg branch "$BRANCH" \
      --argjson dirty "$DIRTY" --argjson refs "$REF_COUNT" --argjson commits "$COMMIT_COUNT" \
      '{path:$path,origin:$origin,head:$head,branch:$branch,dirty:$dirty,ref_count:$refs,commit_count:$commits}' \
      >> "$OUT/local-git-results.ndjson"
done < "$OUT/ALL_LOCAL_GIT_DIRS.txt"

if [ -s "$OUT/local-git-results.ndjson" ]; then
    jq -s '.' "$OUT/local-git-results.ndjson" > "$OUT/LOCAL_GIT_REPOSITORIES.json"
else
    printf '[]\n' > "$OUT/LOCAL_GIT_REPOSITORIES.json"
fi

jq '{repositories:length,dirty:([.[]|select(.dirty==true)]|length),clean:([.[]|select(.dirty==false)]|length),without_origin:([.[]|select(.origin=="")]|length),total_reachable_commits:([.[].commit_count]|add // 0)}' \
  "$OUT/LOCAL_GIT_REPOSITORIES.json" > "$OUT/LOCAL_GIT_TOTALS.json"
cat "$OUT/LOCAL_GIT_TOTALS.json"

jq -r 'sort_by(.commit_count)|reverse|.[0:40][]|[.commit_count,.ref_count,.dirty,.branch,.origin,.path]|@tsv' \
  "$OUT/LOCAL_GIT_REPOSITORIES.json" | column -t -s "$(printf '\t')" > "$OUT/LARGEST_LOCAL_GIT_HISTORIES.txt" || true
cat "$OUT/LARGEST_LOCAL_GIT_HISTORIES.txt" || true

: > "$OUT/NATIVE_ROOT_SIZES.txt"
for BASE in "$TERMUX_HOME" "$UBUNTU_HOME" "$ANDROID"; do
    [ -e "$BASE" ] && du -sh "$BASE" 2>/dev/null >> "$OUT/NATIVE_ROOT_SIZES.txt" || true
done
cat "$OUT/NATIVE_ROOT_SIZES.txt"

echo
echo "=== SHA256 RECEIPT ==="
sha256sum \
  "$OUT/ARTIFACT_DOWNLOAD_RESULTS.json" \
  "$OUT/ARTIFACT_DOWNLOAD_TOTALS.json" \
  "$OUT/GIT_DATABASE_SIZES_CORRECTED.tsv" \
  "$OUT/ALL_LOCAL_GIT_DIRS.txt" \
  "$OUT/LOCAL_GIT_REPOSITORIES.json" \
  "$OUT/LOCAL_GIT_TOTALS.json" \
  "$OUT/NAMED_PROJECT_SIGNALS.tsv" \
  "$OUT/NATIVE_ROOT_SIZES.txt" \
  > "$OUT/SHA256SUMS"
cat "$OUT/SHA256SUMS"

ln -sfn "$OUT" "$ROOT/LATEST_NATIVE_CENSUS_RECEIPT"

echo
echo "=== STORAGE AFTER ==="
df -h /root

echo
echo "Receipt: $OUT"
echo "MSG316_PASS4B_PASS5A_COMPLETE"
