#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# MSG319 — Google Drive -> Samsung internal-storage 8x8 snapshot
# Non-destructive: additive timestamped copies only. Never deletes cloud or local files.
# Requires a working rclone Google Drive remote on the Samsung/Ubuntu estate.

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="/root/8x8-github-local"
RECEIPT="$ROOT/receipts/${TS}-gdrive-internal-storage-sync"
mkdir -p "$RECEIPT"

fail() { echo "ERROR: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"; }
for c in rclone sha256sum find sort awk sed grep df du stat; do need "$c"; done

# Locate the existing Android 8x8 OS folder without creating a competing root.
DEST_ROOT=""
for CANDIDATE in \
  "/storage/emulated/0/8x8 OS" \
  "/sdcard/8x8 OS" \
  "/storage/emulated/0/8x8_OS"; do
  if [ -d "$CANDIDATE" ] && [ -w "$CANDIDATE" ]; then
    DEST_ROOT="$CANDIDATE"
    break
  fi
done
[ -n "$DEST_ROOT" ] || fail "existing writable Android 8x8 OS folder not found"

SNAP="$DEST_ROOT/CloudSync/GoogleDrive/$TS"
mkdir -p "$SNAP"

# Detect the Drive remote safely without printing config or tokens.
REMOTE="${RCLONE_REMOTE:-}"
if [ -z "$REMOTE" ]; then
  mapfile -t REMOTES < <(rclone listremotes | sed 's/:$//' | sed '/^$/d')
  for R in "${REMOTES[@]}"; do
    if rclone lsf "$R:" --dirs-only --max-depth 1 2>/dev/null | grep -Fxq '8x8 OS/'; then
      REMOTE="$R"
      break
    fi
    if rclone lsf "$R:" --dirs-only --max-depth 1 2>/dev/null | grep -Fxq '8x8 OS - External AI Research Archive/'; then
      REMOTE="$R"
      break
    fi
  done
fi
[ -n "$REMOTE" ] || fail "no rclone remote containing the 8x8 Drive folders was found; set RCLONE_REMOTE=<remote-name>"

printf '%s\n' "$REMOTE" > "$RECEIPT/RCLONE_REMOTE_NAME.txt"
printf '%s\n' "$DEST_ROOT" > "$RECEIPT/ANDROID_8X8_ROOT.txt"
printf '%s\n' "$SNAP" > "$RECEIPT/SNAPSHOT_PATH.txt"

cat > "$RECEIPT/SYNC_POLICY.txt" <<'EOF'
MODE=ADDITIVE_TIMESTAMPED_SNAPSHOT
DELETE_REMOTE=false
DELETE_LOCAL=false
OVERWRITE_EXISTING_CANONICAL=false
GOOGLE_NATIVE_EXPORTS=docx,xlsx,pptx,pdf,txt
TRUTH_BOUNDARY=Drive files are preserved as cloud-source material; they become canonical only through later evidence reconciliation.
EOF

echo "============================================================"
echo " MSG319 — GOOGLE DRIVE -> INTERNAL STORAGE SNAPSHOT"
echo "============================================================"
echo "remote=$REMOTE"
echo "dest=$SNAP"
echo

echo "=== STORAGE BEFORE ==="
df -h "$DEST_ROOT" /root || true

# Provider-side inventories. Full inventory records what exists even when a file is
# not copied into the 8x8 project snapshot.
rclone lsjson "$REMOTE:" --recursive --files-only --metadata > "$RECEIPT/DRIVE_FULL_FILE_INVENTORY.json"
rclone lsf "$REMOTE:" --recursive --dirs-only > "$RECEIPT/DRIVE_FULL_FOLDER_INVENTORY.txt"

# Copy the canonical project folder and the external-AI archive as complete,
# additive snapshots. Google-native files are exported to stable local formats.
copy_tree() {
  local SRC="$1"
  local DST="$2"
  if rclone lsf "$REMOTE:$SRC" --max-depth 1 >/dev/null 2>&1; then
    mkdir -p "$DST"
    rclone copy "$REMOTE:$SRC" "$DST" \
      --drive-export-formats docx,xlsx,pptx,pdf,txt \
      --create-empty-src-dirs \
      --metadata \
      --transfers 4 \
      --checkers 8 \
      --stats 30s \
      --stats-one-line
  else
    printf 'MISSING_REMOTE_PATH\t%s\n' "$SRC" >> "$RECEIPT/MISSING_REMOTE_PATHS.tsv"
  fi
}

copy_tree "8x8 OS" "$SNAP/8x8 OS"
copy_tree "8x8 OS - External AI Research Archive" "$SNAP/8x8 OS - External AI Research Archive"

# Also preserve current root-level 8x8/Hermes/MSG continuity material that may
# not yet have been filed under the 8x8 OS Drive folder.
ROOT_RELEVANT="$SNAP/Root-Level-8x8-Relevant"
mkdir -p "$ROOT_RELEVANT"
rclone copy "$REMOTE:" "$ROOT_RELEVANT" \
  --max-depth 1 \
  --include '*8x8*' \
  --include '*8X8*' \
  --include 'HERMES*' \
  --include 'MSG*' \
  --include 'Terminal Text*' \
  --include 'After boot*' \
  --drive-export-formats docx,xlsx,pptx,pdf,txt \
  --metadata \
  --transfers 4 \
  --checkers 8 \
  --stats 30s \
  --stats-one-line

# Local file manifest. Paths are relative to the timestamped snapshot.
(
  cd "$SNAP"
  find . -type f -print0 | LC_ALL=C sort -z | while IFS= read -r -d '' F; do
    SIZE="$(stat -c '%s' "$F")"
    SHA="$(sha256sum "$F" | awk '{print $1}')"
    printf '%s\t%s\t%s\n' "$SHA" "$SIZE" "${F#./}"
  done
) > "$RECEIPT/LOCAL_SNAPSHOT_SHA256.tsv"

FILES="$(wc -l < "$RECEIPT/LOCAL_SNAPSHOT_SHA256.tsv" | tr -d ' ')"
BYTES="$(awk -F '\t' '{s+=$2} END{printf "%.0f",s+0}' "$RECEIPT/LOCAL_SNAPSHOT_SHA256.tsv")"

cat > "$RECEIPT/TOTALS.txt" <<EOF
snapshot_files=$FILES
snapshot_bytes=$BYTES
snapshot_path=$SNAP
remote=$REMOTE
EOF

sha256sum \
  "$RECEIPT/DRIVE_FULL_FILE_INVENTORY.json" \
  "$RECEIPT/DRIVE_FULL_FOLDER_INVENTORY.txt" \
  "$RECEIPT/LOCAL_SNAPSHOT_SHA256.tsv" \
  "$RECEIPT/TOTALS.txt" \
  > "$RECEIPT/SHA256SUMS"

# Stable pointers, without replacing prior snapshots.
mkdir -p "$DEST_ROOT/CloudSync/GoogleDrive"
ln -sfn "$SNAP" "$DEST_ROOT/CloudSync/GoogleDrive/LATEST" 2>/dev/null || true
ln -sfn "$RECEIPT" "$ROOT/LATEST_GDRIVE_INTERNAL_STORAGE_SYNC" 2>/dev/null || true

echo
echo "=== RESULTS ==="
cat "$RECEIPT/TOTALS.txt"
cat "$RECEIPT/SHA256SUMS"
echo
echo "=== STORAGE AFTER ==="
df -h "$DEST_ROOT" /root || true
echo
echo "Receipt: $RECEIPT"
echo "MSG319_GDRIVE_INTERNAL_STORAGE_SYNC_COMPLETE"
