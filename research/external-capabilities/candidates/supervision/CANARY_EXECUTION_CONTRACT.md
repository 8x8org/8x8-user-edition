# MSG197-VISION-001 Supervision External-Node Canary Contract

## Authorized scope

The exact pinned `roboflow/supervision` source may be built and measured only on disposable GitHub-hosted Linux runners using Python 3.11 and 3.12.

The preparation phase may use the network solely to fetch the immutable upstream commit, Python wheels, vulnerability data, and pinned CI tooling. The execution phase runs in a read-only, unprivileged Docker container with no network.

## Synthetic workload

The canary uses generated NumPy arrays and a blank in-memory image. It tests only:

- package import;
- the pure NumPy compatibility backend;
- `Detections`;
- box IoU;
- non-maximum suppression;
- coordinate conversion;
- box annotation;
- deterministic output hashes.

It downloads no model and uses no private image, camera, microphone, API key, account, or production telemetry.

## Measurements

Each Python lane records:

- exact source commit;
- Python, pip, wheel, setuptools, and audit-tool versions;
- resolved distributions and `pip inspect` data;
- wheel names, sizes, and SHA-256 hashes;
- install duration and disk footprint;
- import and synthetic-operation latency;
- peak process RSS;
- Docker base-image identity;
- deterministic output hashes;
- vulnerability findings;
- cleanup and residual state.

## Promotion rule

A functional canary is not an installation approval. Any unresolved vulnerability, unmaintained critical dependency, model download, credential request, private-data access, network activity during execution, resource-limit breach, or unclassified cleanup residue blocks promotion.

The first exact-head run is allowed to discover and fail on supply-chain findings. A later evidence commit may classify an exact reproducible finding set as `CANARY_PASS_PROMOTION_BLOCKED`, but it may not hide, waive, or reinterpret the findings as safe.

## Prohibited targets

No files or packages from this canary may be installed into Samsung Termux, active Ubuntu PRoot, Hermes, control fabric, Vercel production, Neon, Replit, or any long-lived 8x8 environment.

## Cleanup

The workflow must remove the upstream checkout, wheelhouse, virtual environments, Docker build context, Docker container, Docker image, pip cache, synthetic results, and temporary files. Cleanup failure makes the canary fail.
