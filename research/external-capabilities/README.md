# MSG197 External Capability Intake V1

This directory implements the research and governance layer for Issue #41.

## Current truth

- thirteen exact upstream repositories are resolved;
- default branches and immutable commits are recorded;
- top-level license files are verified at those commits;
- every candidate has exactly one primary classification;
- no candidate has been installed, merged into the runtime or declared production-ready;
- independent Hermes-led council execution remains receipt-pending;
- candidate dependency SBOMs and sandbox canaries remain candidate-level work.

## Files

- `REPOSITORY_CENSUS.json`: exact identities, corrections, branches, pins, sizes, licenses and classifications.
- `EVALUATION_MATRIX.csv`: value, overlap, risk, platform, resource, test and rollback assessment.
- `COUNCIL_REPORT.md`: Hermes-led council contract and initial synthesis.
- `THREAT_MODEL.md`: supply-chain, authority, data, parser, resource and boundary threats.
- `LICENSE_AND_SBOM_REPORT.md`: verified top-level licenses and candidate SBOM requirements.
- `INTEGRATION_BACKLOG.json`: one-candidate-per-branch work packets and advancement gates.
- `ROLLBACK_AND_UNINSTALL_PLAN.md`: universal and candidate-specific removal doctrine.
- `ARCHITECTURE_DECISIONS/`: accepted intake architecture decisions.
- `receipts/`: machine-readable intake receipt and SHA-256 artifact manifest.

## State model

`CENSUSED -> STATIC_REVIEWED -> COUNCIL_REVIEWED -> CANARY_DESIGNED -> CANARY_PASSED -> ADAPTER_DESIGNED -> IMPLEMENTED_NOT_DEPLOYED -> RELEASE_CANDIDATE -> OWNER_APPROVED`

All candidates are currently at `STATIC_REVIEWED` or a more conservative deferred state.

## Validation

Run:

```bash
python3 scripts/validate_msg197_external_capabilities.py
```

The validator checks exact record counts, classifications, pins, licenses, boundaries, backlog coverage, CSV coverage, required documents and artifact hashes.

## Non-actions

This package performs no cloning into production paths, package installation, model download, service restart, scheduler change, database mutation, credential access, external account action, public deployment, wallet action or financial operation.
