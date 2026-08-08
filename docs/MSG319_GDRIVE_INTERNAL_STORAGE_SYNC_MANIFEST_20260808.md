# MSG319 — Google Drive → Owner Device Storage Sync Manifest

Date: 2026-08-08

## Verified Pass 4B baseline

The owner-controlled mobile runtime preserved all 200 currently downloadable GitHub Actions artifacts with 0 failures and 521,652,000 bytes preserved.

- Receipt location: retained in the private local evidence store and intentionally omitted from public source.
- SHA256 `ARTIFACT_DOWNLOAD_RESULTS.json`: `774b59cd7b3200b3dbe5b25e48937e36fa3365a2b702ce7916bb98ae2f9ee562`
- SHA256 `TOTALS.json`: `bad83d3ec13df9f7da6e2b52f3fbca531a55185cfa0f9afa5a5e93e607351762`

## Confirmed Drive anchors

- `8x8 OS` folder ID: `1TirGz6ld99cBsO6I2Yp8PNQVr6wjeabs`
- `8x8 OS - External AI Research Archive` folder ID: `1B7OwCvQMBc10d1G7otS4denRSdigbKR3`
- `Agent Fleet Missions` folder ID: `1J8SJH3qEQ1tSdnfPAGwV69WIorJctOWW`
- `MSG291B Agent Fleet Teach + Help` folder ID: `1tuiEfq1QkkUOHvU-uxw33cMNDm5zrXTz`

Recent canonical Drive documents observed on 2026-08-08 include MSG319, the canonical program ledger, owner-absence continuity packet, MSG291B agent teaching packet, MSG289 full-convergence packet, master continuation index, coordinator start-here packet, and the 2026-08-08 Kimi research/build/evidence archive.

## Local synchronization policy

`ops/msg319_gdrive_internal_storage_snapshot.sh` performs an additive timestamped snapshot into the existing writable owner-device `8x8 OS` directory.

It intentionally does **not** use destructive mirroring:

- no Drive deletion;
- no local deletion;
- no force overwrite of the existing canonical owner-device estate;
- full provider file/folder inventory is written to a receipt;
- Google-native Docs/Sheets/Slides are exported to stable local formats;
- root-level 8x8 continuity material is included even if not filed under the Drive `8x8 OS` folder;
- every local file is SHA-256 manifested;
- Drive content remains source evidence until local/GitHub reconciliation promotes it to `VERIFIED`.

## Execution gate

Run the exact script from `feature/msg319-convergence-control-v1` on the authorized owner-controlled runtime, then require terminal marker:

`MSG319_GDRIVE_INTERNAL_STORAGE_SYNC_COMPLETE`

The resulting receipt remains in the private local evidence store and must be referenced by digest rather than by private filesystem topology in public source.

After that, Pass 5A runs against the combined estate and the comparison gate classifies each repository/artifact as `REMOTE_IDENTICAL`, `LOCAL_AHEAD_OR_LOCAL_ONLY`, `REMOTE_AHEAD`, or `DIVERGED_OR_UNRELATED`.
