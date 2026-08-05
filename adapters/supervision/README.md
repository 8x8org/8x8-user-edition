# 8x8 Supervision Adapter V1

## Status

`CONTRACT_IMPLEMENTED_RUNTIME_NOT_INSTALLED`

This directory defines a disabled-by-default 8x8 contract for selected, bounded computer-vision utility operations derived from the measured MSG197-VISION-001 Supervision canary.

It does **not** install `roboflow/supervision`, activate a model, access a camera, read private media, expose a network service, or authorize production use.

## Exact upstream evidence

- repository: `roboflow/supervision`
- commit: `bc20dd19fbc7b6cceaec447f1182346ca9158523`
- version: `0.31.0.dev0`
- license: MIT
- measured canary merge: `16b51f18603156b1d485c75b7c5ab9dd77067ff8`

## Allowed contract operations

- confidence-based detection filtering;
- intersection-over-union matrix calculation;
- non-maximum suppression;
- bounded coordinate conversion;
- deterministic annotation metadata hashing.

These operations are contract names. No runtime implementation is included in this slice.

## Denied authority

The adapter denies network access, model downloads, camera and microphone use, private filesystem access, database writes, service or scheduler control, public deployment, wallets and financial actions.

## Data boundary

Only synthetic or explicitly public-licensed media may enter a future canary. The contract exchanges normalized detection coordinates and hashes rather than embedding private images or video.

## Activation sequence

A future runtime implementation requires a separate owner-approved branch and must complete:

1. exact dependency lock and SBOM;
2. vulnerability and secret scanning;
3. isolated external-node build;
4. synthetic malformed-input and resource-limit tests;
5. deterministic outputs across supported Python versions;
6. no-network, unprivileged execution;
7. uninstall and cleanup proof;
8. independent security and license review;
9. explicit owner activation receipt.

Until those gates pass, `enabled=false`, `install_state=NOT_INSTALLED`, `runtime_authority=NONE`, and `production_ready=false` are immutable release boundaries.

## Rollback

Because this slice contains schemas, fixtures, documentation and tests only, rollback is deletion of `adapters/supervision/`, its test, and its workflow. No process, package, port, scheduler, database object, model, cache or credential should exist.
