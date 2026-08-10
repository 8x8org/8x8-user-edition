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

meta=''
if meta="$(curl -sS -L --fail-with-body \
  --retry 3 --retry-all-errors \
  --connect-timeout 10 --max-time 60 \
  -D "$headers" -o "$body" \
  -w $'%{http_code}\t%{content_type}\t%{url_effective}' \
  "$PUBLIC_ALIAS/")"; then
  :
else
  curl_exit=$?
  echo "PROVENANCE=FAIL reason=fetch_failed curl_exit=$curl_exit alias=$PUBLIC_ALIAS" >&2
  exit 1
fi

IFS=$'\t' read -r status final_content_type effective_url <<<"$meta"

if [[ "$status" != '200' ]]; then
  echo "PROVENANCE=FAIL reason=http_status status=$status effective_url=$effective_url" >&2
  exit 1
fi

if [[ ! "$final_content_type" =~ ^text/html([\;].*)?$ ]]; then
  echo "PROVENANCE=FAIL reason=content_type_not_html content_type=$final_content_type effective_url=$effective_url" >&2
  exit 1
fi

final_disposition="$(awk '
  BEGIN { IGNORECASE=1; disposition="" }
  /^HTTP\// { disposition="" }
  /^content-disposition:/ { disposition=$0 }
  END { gsub(/\r/, "", disposition); print disposition }
' "$headers")"
if [[ "$final_disposition" =~ [Aa][Tt][Tt][Aa][Cc][Hh][Mm][Ee][Nn][Tt] ]]; then
  echo "PROVENANCE=FAIL reason=attachment_disposition disposition=$final_disposition" >&2
  exit 1
fi

source_sha256="$(sha256sum "$SOURCE_PATH" | awk '{print $1}')"
live_sha256="$(sha256sum "$body" | awk '{print $1}')"
source_bytes="$(wc -c < "$SOURCE_PATH" | tr -d ' ')"
live_bytes="$(wc -c < "$body" | tr -d ' ')"

if [[ "$source_sha256" != "$live_sha256" ]]; then
  echo "PROVENANCE=FAIL reason=digest_mismatch source_sha256=$source_sha256 live_sha256=$live_sha256 source_bytes=$source_bytes live_bytes=$live_bytes effective_url=$effective_url" >&2
  exit 1
fi

for marker in 'Living Omniversal Gate R4' '0.1.0 Stable' 'WHOLE_SYSTEM_COMPLETE=false'; do
  grep -Fq "$marker" "$body" || {
    echo "PROVENANCE=FAIL reason=truth_marker_missing marker=$marker" >&2
    exit 1
  }
done

printf 'PROVENANCE=PASS source_path=%s source_sha256=%s live_sha256=%s bytes=%s alias=%s effective_url=%s\n' \
  "$SOURCE_PATH" "$source_sha256" "$live_sha256" "$live_bytes" "$PUBLIC_ALIAS" "$effective_url"
printf 'PUBLIC_SCOPE=PUBLIC_WEB_CLIENT WHOLE_SYSTEM_SCORE=NOT_INFERRED\n'
