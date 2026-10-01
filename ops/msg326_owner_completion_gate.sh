#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# 8x8 OS MSG326 — Owner Completion Gate V1
# Public-safe runner: gathers local evidence, verifies canonical code, creates
# owner-input templates, and reports exact blockers. It never prints or stores
# private keys, seed phrases, API tokens, or wallet secrets.

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="${EIGHTX8_GITHUB_ROOT:-/root/8x8-github-local}"
REPO="${EIGHTX8_CANONICAL_REPO:-$ROOT/repos/8x8org/8x8-user-edition}"
RECEIPTS="${EIGHTX8_RECEIPTS:-$ROOT/receipts}"
OUT="$RECEIPTS/${TS}-msg326-owner-completion-gate"
INPUT_DIR="${EIGHTX8_OWNER_INPUT_DIR:-/root/.8x8-owner-inputs}"
INPUT_JSON="$INPUT_DIR/owner-public-inputs.json"
mkdir -p "$OUT" "$INPUT_DIR"

log(){ printf '%s\n' "$*" | tee -a "$OUT/run.log"; }
need(){ command -v "$1" >/dev/null 2>&1; }

log "============================================================"
log " MSG326 — 8x8 OWNER COMPLETION GATE"
log "============================================================"
log "timestamp_utc=$TS"

# ---------- canonical repository ----------
log ""
log "=== CANONICAL REPOSITORY ==="
if [ ! -d "$REPO/.git" ]; then
  log "CANONICAL_REPO_MISSING=$REPO"
  log "Create or restore the canonical local clone before continuing."
  exit 20
fi

git -C "$REPO" remote -v > "$OUT/remotes.txt"
git -C "$REPO" status --short --branch > "$OUT/status-before.txt"

git -C "$REPO" fetch --prune origin main
REMOTE_MAIN="$(git -C "$REPO" rev-parse origin/main)"
LOCAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
BRANCH="$(git -C "$REPO" branch --show-current)"

log "branch=$BRANCH"
log "local_head=$LOCAL_HEAD"
log "origin_main=$REMOTE_MAIN"

# Never destroy local work. Fast-forward only if clean and currently on main.
if [ "$BRANCH" = "main" ] && [ -z "$(git -C "$REPO" status --porcelain)" ]; then
  git -C "$REPO" merge --ff-only origin/main
  LOCAL_HEAD="$(git -C "$REPO" rev-parse HEAD)"
  log "fast_forwarded_main=$LOCAL_HEAD"
else
  log "LOCAL_WORK_PRESERVED=true"
fi

# ---------- exact known release surfaces ----------
log ""
log "=== RELEASE / PROTECTED-BETA FILES ==="
CHECK_PATHS=(
  "stable/index.html"
  "protected-beta/admin/index.html"
  "protected-beta/account/index.html"
  "protected-beta/account-economy-state.json"
  "protected-beta/economy-policy.json"
  "contracts/evm/EightX8CappedAsset.sol"
  "contracts/evm/MSG325_SEPOLIA_DEPLOYMENT_SPEC.json"
)
: > "$OUT/file-presence.tsv"
for p in "${CHECK_PATHS[@]}"; do
  if [ -f "$REPO/$p" ]; then
    printf 'PRESENT\t%s\t%s\n' "$p" "$(sha256sum "$REPO/$p" | awk '{print $1}')" >> "$OUT/file-presence.tsv"
  else
    printf 'MISSING\t%s\t-\n' "$p" >> "$OUT/file-presence.tsv"
  fi
done
cat "$OUT/file-presence.tsv" | tee -a "$OUT/run.log"

# ---------- protected-beta tests ----------
log ""
log "=== PROTECTED-BETA VALIDATION ==="
if need python3 && [ -f "$REPO/scripts/validate_protected_beta_economy.py" ]; then
  if (cd "$REPO" && python3 scripts/validate_protected_beta_economy.py) > "$OUT/protected-beta-validator.log" 2>&1; then
    log "PROTECTED_BETA_VALIDATOR=PASS"
  else
    log "PROTECTED_BETA_VALIDATOR=FAIL"
  fi
else
  log "PROTECTED_BETA_VALIDATOR=NOT_RUN"
fi

if need python3 && [ -f "$REPO/tests/test_protected_beta_economy.py" ]; then
  if (cd "$REPO" && python3 -m unittest tests/test_protected_beta_economy.py) > "$OUT/protected-beta-tests.log" 2>&1; then
    log "PROTECTED_BETA_TESTS=PASS"
  else
    log "PROTECTED_BETA_TESTS=FAIL_OR_DEPENDENCY_MISSING"
  fi
else
  log "PROTECTED_BETA_TESTS=NOT_RUN"
fi

# ---------- owner public inputs ----------
log ""
log "=== OWNER PUBLIC INPUT PACKET ==="
if [ ! -f "$INPUT_JSON" ]; then
cat > "$INPUT_JSON" <<'JSON'
{
  "schema_version": "1.0.0",
  "owner_8x8_id": "",
  "owner_profile_handle": "FlashTM8",
  "wallets": {
    "OWNER_TREASURY": "",
    "OPERATING_TREASURY": "",
    "LIQUIDITY": "",
    "FEE_COLLECTION": "",
    "TOKEN_ADMIN": "",
    "ASSET_RESERVE": "",
    "AGENT_OPERATIONAL_TESTNET_ONLY": ""
  },
  "first_testnet": {
    "network": "Ethereum Sepolia",
    "chain_id": 11155111,
    "deployer_public_address": "",
    "policy_admin_public_address": "",
    "expected_max_spend_native": ""
  },
  "identity": {
    "preferred_login": "passkey",
    "recovery_contact_reference": ""
  },
  "notes": "PUBLIC ADDRESSES / NON-SECRET REFERENCES ONLY. NEVER PUT PRIVATE KEYS, SEED PHRASES, API TOKENS OR PASSWORDS HERE."
}
JSON
  chmod 600 "$INPUT_JSON"
  log "OWNER_INPUT_TEMPLATE_CREATED=$INPUT_JSON"
else
  log "OWNER_INPUT_TEMPLATE_PRESENT=$INPUT_JSON"
fi

# Validate only public-address shape; do not inspect secret stores.
if need jq; then
  jq empty "$INPUT_JSON" >/dev/null 2>&1 || { log "OWNER_INPUT_JSON=INVALID_JSON"; exit 30; }
  jq '{owner_8x8_id, wallet_roles:(.wallets|keys), first_testnet:{network,chain_id}}' "$INPUT_JSON" > "$OUT/owner-public-summary.json"

  MISSING_PUBLIC="$(jq -r '[
    .wallets.OWNER_TREASURY,
    .wallets.TOKEN_ADMIN,
    .first_testnet.deployer_public_address,
    .first_testnet.policy_admin_public_address
  ] | map(select(. == "" or . == null)) | length' "$INPUT_JSON")"
  log "required_public_fields_missing=$MISSING_PUBLIC"
else
  log "jq_missing=true"
fi

# ---------- local estate / one-Fabric discovery ----------
log ""
log "=== ONE-FABRIC LOCAL DISCOVERY ==="
SEARCH_ROOTS=(
  "/root"
  "/data/data/com.termux/files/home"
  "/storage/emulated/0/8x8 OS"
  "/storage/emulated/0/8x8"
)
: > "$OUT/fabric-candidates.txt"
for r in "${SEARCH_ROOTS[@]}"; do
  [ -e "$r" ] || continue
  find "$r" -maxdepth 5 \( \
      -iname '*1fabric*' -o \
      -iname '*control*fabric*' -o \
      -iname '*reality*graph*' -o \
      -iname '*context*capsule*' -o \
      -iname '*universal*suit*' -o \
      -iname '*mission*dag*' -o \
      -iname '*hermes*' \
    \) -print 2>/dev/null >> "$OUT/fabric-candidates.txt" || true
done
LC_ALL=C sort -u "$OUT/fabric-candidates.txt" -o "$OUT/fabric-candidates.txt"
log "fabric_candidate_paths=$(wc -l < "$OUT/fabric-candidates.txt" | tr -d ' ')"

# ---------- service census ----------
log ""
log "=== SERVICE CENSUS ==="
if need sv; then
  (sv status /data/data/com.termux/files/usr/var/service/* 2>/dev/null || true) > "$OUT/termux-services.txt"
fi
ps -eo pid,etime,cmd 2>/dev/null | grep -Ei '8x8|hermes|fabric|guardian|studio|agent' | grep -v grep > "$OUT/process-census.txt" || true

# ---------- internal storage media/product census ----------
log ""
log "=== INTERNAL STORAGE 8x8 OS CENSUS ==="
ANDROID_ROOT=""
for c in "/storage/emulated/0/8x8 OS" "/sdcard/8x8 OS"; do
  if [ -d "$c" ]; then ANDROID_ROOT="$c"; break; fi
done
if [ -n "$ANDROID_ROOT" ]; then
  log "android_8x8_root=$ANDROID_ROOT"
  find "$ANDROID_ROOT" -type f 2>/dev/null | LC_ALL=C sort > "$OUT/android-files.txt"
  awk 'BEGIN{IGNORECASE=1}
    /\.(png|jpg|jpeg|webp|gif|svg)$/ {img++}
    /\.(mp4|mov|mkv|webm)$/ {vid++}
    /\.(mp3|wav|flac|m4a|ogg)$/ {aud++}
    /\.(pdf|epub|docx|pptx|xlsx|md|txt)$/ {doc++}
    END{printf("images=%d\nvideos=%d\naudio=%d\ndocs=%d\n",img,vid,aud,doc)}' "$OUT/android-files.txt" > "$OUT/android-media-counts.txt"
  cat "$OUT/android-media-counts.txt" | tee -a "$OUT/run.log"
else
  log "android_8x8_root=NOT_FOUND_FROM_THIS_NAMESPACE"
fi

# ---------- Drive snapshot readiness ----------
log ""
log "=== DRIVE SYNC READINESS ==="
if need rclone; then
  rclone listremotes > "$OUT/rclone-remotes.txt" 2>/dev/null || true
  if [ -s "$OUT/rclone-remotes.txt" ]; then
    log "RCLONE_REMOTE_PRESENT=true"
  else
    log "RCLONE_REMOTE_PRESENT=false"
  fi
else
  log "RCLONE_NOT_INSTALLED=true"
fi

# ---------- contract toolchain readiness ----------
log ""
log "=== TESTNET TOOLCHAIN READINESS ==="
for tool in node npm python3 jq gh git forge cast solc; do
  if need "$tool"; then
    printf '%s\tPRESENT\t%s\n' "$tool" "$(command -v "$tool")" >> "$OUT/toolchain.tsv"
  else
    printf '%s\tMISSING\t-\n' "$tool" >> "$OUT/toolchain.tsv"
  fi
done
cat "$OUT/toolchain.tsv" | tee -a "$OUT/run.log"

# ---------- secret presence checks by NAME ONLY ----------
# We do not print values. This simply tells the owner what local integration
# classes appear configured.
log ""
log "=== LOCAL SECRET-CLASS PRESENCE (NAMES ONLY) ==="
SECRET_NAMES=(OPENROUTER_API_KEY BITGET_API_KEY TG_BOT_TOKEN DISCORD_TOKEN DATABASE_URL)
: > "$OUT/secret-class-presence.tsv"
for n in "${SECRET_NAMES[@]}"; do
  if [ -n "${!n:-}" ]; then
    printf '%s\tPRESENT_IN_ENV\n' "$n" >> "$OUT/secret-class-presence.tsv"
  else
    printf '%s\tNOT_IN_CURRENT_ENV\n' "$n" >> "$OUT/secret-class-presence.tsv"
  fi
done
cat "$OUT/secret-class-presence.tsv" | tee -a "$OUT/run.log"

# ---------- deterministic blocker report ----------
log ""
log "=== NEXT EXACT GATES ==="
BLOCKERS=()
[ -f "$REPO/protected-beta/admin/index.html" ] || BLOCKERS+=("protected-beta-admin-surface")
[ -f "$REPO/contracts/evm/EightX8CappedAsset.sol" ] || BLOCKERS+=("evm-token-source")
if need jq; then
  [ "${MISSING_PUBLIC:-4}" -eq 0 ] || BLOCKERS+=("owner-public-address-inputs")
fi
need forge || BLOCKERS+=("foundry-forge")
need cast || BLOCKERS+=("foundry-cast")

if [ "${#BLOCKERS[@]}" -eq 0 ]; then
  log "PRE_TESTNET_OWNER_INPUT_GATE=PASS"
  log "NEXT=compile_and_run_contract_tests_then_prepare_sepolia_unsigned_transaction_packet"
else
  log "PRE_TESTNET_OWNER_INPUT_GATE=BLOCKED"
  for b in "${BLOCKERS[@]}"; do log "blocker=$b"; done
fi

# ---------- receipt hashes ----------
log ""
log "=== RECEIPT DIGEST ==="
find "$OUT" -maxdepth 1 -type f ! -name SHA256SUMS -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum > "$OUT/SHA256SUMS"
sha256sum "$INPUT_JSON" > "$OUT/OWNER_PUBLIC_INPUT_SHA256"
cat "$OUT/SHA256SUMS"

ln -sfn "$OUT" "$ROOT/LATEST_MSG326_OWNER_COMPLETION_GATE"
log ""
log "receipt=$OUT"
log "MSG326_OWNER_COMPLETION_GATE_COMPLETE"
