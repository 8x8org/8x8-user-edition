# MSG197-VISION-001 Measured Supervision Canary Report

## Verdict

`PASS_MEASURED_EXTERNAL_CANARY_NOT_RUNTIME_INTEGRATION`

The exact pinned `roboflow/supervision` source at `bc20dd19fbc7b6cceaec447f1182346ca9158523` passed a disposable, no-model, no-private-media canary on Python 3.11 and 3.12. The resolved environments reported zero known vulnerabilities after the packaging toolchain was pinned to pip 26.1.2, setuptools 83.0.0, and wheel 0.46.2.

This result authorizes only the next design and owner-review stage for a narrow 8x8 adapter. It does not install Supervision into the active phone, Ubuntu PRoot, Hermes, control fabric, public deployment, or production runtime.

## Execution boundaries

- GitHub-hosted Ubuntu runner only
- exact sparse upstream commit
- synthetic NumPy arrays and blank in-memory image
- no model downloads
- no camera, microphone, API key, private image, or production telemetry
- network denied during execution
- read-only container root filesystem
- unprivileged user `65534:65534`
- one CPU, 768 MiB RAM, 128 process limit
- 30-second command timeout
- cleanup proven in both lanes

## Measured results

| Metric | Python 3.11 | Python 3.12 |
|---|---:|---:|
| Runtime | 3.11.15 | 3.12.13 |
| Import latency | 858.338 ms | 946.913 ms |
| Synthetic operation latency | 1.570 ms | 1.719 ms |
| Peak RSS | 115,532 KiB | 114,868 KiB |
| Installed distributions | 26 | 26 |
| Known vulnerable distributions | 0 | 0 |
| Cleanup | PASS | PASS |

Both lanes produced identical hashes:

- annotated image: `32043bb0b52fb6a6c707747a120474cff70a1983a27f658e83b6724addb4c7cc`
- IoU matrix: `daea5645b1d2b5d1fbe703c6cc246a9bd564a219c0f973eec83ecc14cc1afb46`
- NMS result: `85f90dfea1d8027e1463e5ca971a250110a20df0119d204a74220bc63516d15b`
- XYWH conversion: `3c9692b9791183499511b557c5025a7af17411821a0b820977d830d6e7b2d5ac`

## Workflow evidence

- workflow run: `31046645930`
- exact tested head: `255fd32813f7d3ca70c8851b373f03a2c7838c7c`
- Python 3.11 artifact: `8946729080`
- Python 3.11 artifact ZIP SHA-256: `e016464eefc37576ccbb78c35e3eb54d68c55f28a000a5542ed6c464940d16a1`
- Python 3.12 artifact: `8946731865`
- Python 3.12 artifact ZIP SHA-256: `ddb2bfa9131b437474b1c72a0bc96d0495be8eb19feafb31cde7acbd75e723b4`

## Earlier fail-closed discoveries

The canary initially detected current advisories in the virtual environment's bundled pip, setuptools, and wheel tools. The workflow was not weakened. It was rebuilt with fixed versions and rerun from the exact source pin. The final matrix passed the zero-vulnerability gate.

## Next permitted stage

A separate feature branch may design a narrow, disabled-by-default 8x8 adapter around model-agnostic data types and deterministic utilities. That stage still requires:

- an explicit capability manifest;
- no implicit model or remote-service dependency;
- bounded input sizes;
- provenance and untrusted-media treatment;
- an uninstall proof;
- owner approval before any long-lived installation.

## Non-actions

Installed third-party candidates in active 8x8 remain `0`. No phone, service, credential, wallet, private-data, database, public-deployment, or production-runtime change occurred.
