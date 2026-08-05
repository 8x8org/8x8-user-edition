# MSG197 External Capability Intake V2

This directory is the evidence and governance layer for Issue #41.

## Current authority

For current candidate status, use:

1. `CANDIDATE_STATUS_LEDGER_V2.json`
2. `MSG197_COMPLETION_MATRIX_V2.md`
3. candidate-specific manifests and receipts under `candidates/`
4. council state under `council/`

The original `REPOSITORY_CENSUS.json`, `EVALUATION_MATRIX.csv`, and `INTEGRATION_BACKLOG.json` remain historical intake evidence. Their early recommendations are superseded where the V2 ledger records a corrected identity or later decision.

## Current truth

- thirteen exact upstream repositories are resolved and commit-pinned;
- all thirteen candidate research, decision, plan, or blocked-evidence packets are merged;
- PDF Inspector passed its exact bounded synthetic parser canary but remains supply-chain blocked and uninstalled;
- Uber ADR and Cloudflare Computer have corrected identities and scopes;
- zero third-party candidates are installed into the active 8x8 runtime;
- zero Termux, Ubuntu PRoot, service, credential, wallet, private-data, or production changes were performed by MSG197;
- AirLLM and Supervision still require approved external-node measurements;
- the Hermes-led council framework is merged, with zero valid votes and no quorum.

## Files

- `CANDIDATE_STATUS_LEDGER_V2.json`: current machine-readable candidate authority.
- `MSG197_COMPLETION_MATRIX_V2.md`: current human-readable status and remaining gates.
- `MSG197_ERRATA_V2.md`: corrected identities and supersession record.
- `MSG197_EXECUTION_HANDOFF_V2.md`: exact remaining external-node and council work.
- `REPOSITORY_CENSUS.json`: historical upstream identity, branch, pin, size, and license census.
- `EVALUATION_MATRIX.csv`: historical first-pass value and risk assessment.
- `COUNCIL_REPORT.md`: original council design.
- `council/`: identity-, lease-, digest-, quorum-, veto-, and receipt-bound council framework.
- `candidates/`: candidate-specific manifests, analyses, tests, hashes, and receipts.
- `THREAT_MODEL.md`: common supply-chain, authority, parser, resource, and data threats.
- `LICENSE_AND_SBOM_REPORT.md`: verified top-level licenses and candidate SBOM requirements.
- `INTEGRATION_BACKLOG.json`: historical one-candidate-per-branch work packets.
- `ROLLBACK_AND_UNINSTALL_PLAN.md`: common and candidate-specific removal doctrine.
- `ARCHITECTURE_DECISIONS/`: accepted intake architecture decisions.
- `receipts/`: parent intake receipts and governed artifact hashes.

## State model

`CENSUSED -> STATIC_REVIEWED -> COUNCIL_REVIEWED -> CANARY_DESIGNED -> CANARY_PASSED_OR_BLOCKED -> ADAPTER_DESIGNED -> IMPLEMENTED_NOT_DEPLOYED -> RELEASE_CANDIDATE -> OWNER_APPROVED`

A candidate can be complete in research or decision scope while remaining deliberately uninstalled or rejected from promotion.

## Validation

Run:

```bash
python3 scripts/validate_msg197_external_capabilities.py
python3 scripts/validate_msg197_candidate_ledger_v2.py
```

Candidate packets include their own deterministic validators and GitHub Actions workflows.

## Non-actions

MSG197 does not authorize blind cloning into production paths, package installation on the active phone, model downloads, service restarts, scheduler changes, database mutation, credential access, external account changes, public deployment, wallet actions, or financial operations.
