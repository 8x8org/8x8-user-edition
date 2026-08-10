#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_PATH="${1:-stable/index.html}"
PUBLIC_ALIAS="${2:-https://8x8-os-ecosystem.vercel.app}"

if [[ ! -f "$SOURCE_PATH" ]]; then
  echo "PROVENANCE=FAIL reason=source_missing path=$SOURCE_PATH" >&2
  exit 1
fi

body="$(mktemp)"
headers="$(mktemp)"
trap 'rm -f "$body" "$headers"' EXIT

curl -fsS --retry 3 --retry-all-errors -D "$headers" -o "$body" "$PUBLIC_ALIAS/"

grep -Eiq '^content-type:[[:space:]]*text/html' "$headers" || {
  echo "PROVENANCE=FAIL reason=content_type_not_html" >&2
  exit 1
}

if grep -Eiq '^content-disposition:.*attachment' "$headers"; then
  echo "PROVENANCE=FAIL reason=attachment_disposition" >&2
  exit 1
fi

source_sha256="$(sha256sum "$SOURCE_PATH" | awk '{print $1}')"
live_sha256="$(sha256sum "$body" | awk '{print $1}')"
source_bytes="$(wc -c < "$SOURCE_PATH" | tr -d ' ')"
live_bytes="$(wc -c < "$body" | tr -d ' ')"

if [[ "$source_sha256" != "$live_sha256" ]]; then
  echo "PROVENANCE=FAIL reason=digest_mismatch source_sha256=$source_sha256 live_sha256=$live_sha256 source_bytes=$source_bytes live_bytes=$live_bytes" >&2
  exit 1
fi

for marker in 'Living Omniversal Gate R4' '0.1.0 Stable' 'whole_system_complete=false'; do
  grep -Fq "$marker" "$body" || {
    echo "PROVENANCE=FAIL reason=truth_marker_missing marker=$marker" >&2
    exit 1
  }
done

printf 'PROVENANCE=PASS source_path=%s source_sha256=%s live_sha256=%s bytes=%s alias=%s\n' \
  "$SOURCE_PATH" "$source_sha256" "$live_sha256" "$live_bytes" "$PUBLIC_ALIAS"
printf 'PUBLIC_SCOPE=PUBLIC_WEB_CLIENT WHOLE_SYSTEM_SCORE=NOT_INFERRED\n'
