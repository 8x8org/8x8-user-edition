# MSG197 Rollback and Uninstall Plan V1.1

## Rule

A candidate is not integrated until it can be removed without damaging the canonical 8x8 core. “We can probably delete the folder” is not an uninstall strategy. It is the opening sentence of a future incident report.

## Required install inventory

Every canary and implementation branch must record:

- exact upstream repository and commit;
- package and binary versions;
- created files and directories;
- modified files with before/after SHA-256;
- environment variables and secret references, never secret values;
- services, timers, cron jobs and scheduled tasks;
- processes and ports;
- databases, schemas, tables and migrations;
- model, dataset and cache paths;
- network domains and external accounts;
- capability and plugin registrations;
- UI routes and public assets;
- telemetry schemas, retention rules and deletion paths;
- generated evidence and logs.

## Universal rollback sequence

1. Revoke the candidate lease and disable its capability manifest.
2. Stop only the named candidate process or disposable environment.
3. Verify no candidate process, port or child remains.
4. Export evidence needed for audit, excluding secrets and private payloads.
5. Revert the candidate branch or release unit to its recorded parent SHA.
6. Restore modified configuration from hash-verified backups.
7. Remove candidate-created files, packages, caches and disposable data stores from the inventory only.
8. Re-run public/private boundary tests, service health checks and storage checks.
9. Produce an uninstall receipt with residual findings.
10. Keep the candidate blocked when cleanup is incomplete.

## Candidate-specific rollback

### Knowledge and workflow sources

Remove curated records and index entries, restore the previous knowledge manifest and retain required attribution history. No executable service or automatic session hook should exist.

### TencentDB Agent Memory

Use a disposable database branch. Export synthetic test data, test deletion, drop only the disposable branch or candidate schema and verify production data is unchanged. Remove adapter registration and connection secret references.

### Cloudflare Computer

Revoke test bindings, destroy the Durable Object and ephemeral execution backends, remove synthetic workspaces and verify no container, FUSE mount, worker, process, artifact or network route remains. Retain only redacted receipts.

### AirLLM

Delete the isolated environment, model layers and caches listed in the manifest. Verify GPU processes and download jobs are absent. Never remove shared models without a separate ownership check.

### Uber ADR agent-security research

Remove the sensor or schema adapter, detector environment and all synthetic benchmark outputs. Revoke any disposable provider keys, prove that no production agent was instrumented, delete collected traces according to the canary retention policy and retain only redacted aggregate receipts. There are no Markdown architecture-decision records to preserve because this repository is Agentic AI Detection and Response.

### PDF and vision plugins

Stop the isolated worker, delete temporary inputs and outputs, remove native dependencies only from the disposable environment and verify no uploaded document or media remains.

### LoopX and Reasonix

Destroy the comparison environment. Do not merge Git histories, registries, schedulers, credential stores or runtime databases into 8x8. Preserve only reviewed pattern notes and citations.

### Tailwind and Next.js

Revert the dedicated migration branch, dependency lockfile and generated assets. Restore the prior static deployment and verify routes, CSP, service worker, offline behavior, accessibility and rollback target.

## Uninstall acceptance

An uninstall passes only when:

- all named candidate processes and ports are absent;
- modified canonical files match their pre-install hashes;
- no candidate service, hook or scheduler remains;
- secret references are removed or revoked;
- disposable databases, telemetry and caches are accounted for;
- public and private boundary tests pass;
- storage usage is measured before and after;
- residual files are zero or explicitly accepted;
- the receipt records operator, time, target SHA and result.

## Production boundary

No production deployment may use a candidate whose uninstall has not already passed in the same class of environment.
