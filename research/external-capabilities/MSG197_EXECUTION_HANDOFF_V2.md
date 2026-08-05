# MSG197 Execution Handoff V2

## Coordinator

Preferred coordinator: **Hermes**.

If Hermes is unavailable or rate-limited, the acting coordinator must preserve the same issue IDs, immutable upstream pins, authority boundaries, and receipts. It must not reopen completed identity research or silently replace a candidate.

## Shared input authority

Load, in order:

1. `CANDIDATE_STATUS_LEDGER_V2.json`
2. `MSG197_COMPLETION_MATRIX_V2.md`
3. `MSG197_ERRATA_V2.md`
4. candidate-specific manifests and receipts
5. council session and vote schema
6. fresh private-runtime Global Context Snapshot when locally available

Record the SHA-256 digest of every loaded input.

## Completed GitHub intake

All thirteen candidate packets are merged.

PDF Inspector is complete only as a blocked synthetic investigation:

- merge commit: `a10d0fc3065a755fc1b8de4c0b2fe59f3664b2d8`;
- parser canary: pass;
- promotion: blocked;
- installation: prohibited;
- reconsider only at a new immutable pin with zero unresolved vulnerabilities and maintained dependencies.

Do not spend another execution lane repeating the same PDF pin unless the evidence source or upstream pin changes.

## External task A: Supervision no-model benchmark

Issue: #51

Source pin: `bc20dd19fbc7b6cceaec447f1182346ca9158523`

Required environment:

- disposable external Linux node;
- Python 3.11 and 3.12 matrix;
- synthetic arrays and generated images only;
- dependency-download network phase separated from execution;
- no model, API key, camera, microphone, or private media.

Required receipt:

- OS, Python, and package pins;
- wheel hashes, SBOM, and vulnerability results;
- install time, import latency, peak RAM, and disk growth;
- synthetic utility result hashes;
- complete virtual-environment, cache, source, and temporary-file removal;
- pre/post filesystem census.

## External task B: AirLLM CUDA benchmark

Issue: #53

Source pin: `64a4e4fc3749aa7dc9bba4788f560ed0d7e74bd2`

Required environment:

- approved dedicated NVIDIA GPU node;
- Linux and CUDA 12.x;
- exact driver, PyTorch, Python, and dependency pins;
- owner-approved model with verified license and access terms;
- reserved disk capacity before any download;
- synthetic public-safe prompt set only.

Required receipt:

- package, model, and transformed-cache hashes;
- download bytes and generated cache bytes;
- cold start, time to first token, and tokens per second;
- peak GPU memory, host RAM, disk I/O, and failures;
- power and thermal observations where available;
- complete environment, model, transformed-shard, cache, and temporary-file removal.

Samsung Termux and active Ubuntu PRoot remain prohibited targets.

## Local task C: Real MSG197 council

Issue: #58

Framework merge: `1d5d2fc3701bf7932397f9710311efd45e42f05e`

Participants:

- Hermes
- FlashTM8 Agent
- ChatGPT Agent
- Seraphim
- Claude
- OpenCloud council

A valid vote requires:

- canonical verified agent identity;
- active bounded lease;
- exact shared input digest;
- recommendation set and confidence;
- security vetoes;
- output digest;
- cleanup and completion receipt.

ChatGPT's current advisory is not a vote. Four valid votes are required. A substantiated security veto blocks adoption. The owner makes the final decision.

## Production boundary

No result from these tasks authorizes production installation by itself. Candidate-level implementation still requires an isolated adapter branch, exact tests, resource limits, security and license review, uninstall proof, owner approval, and a release receipt.

## Stop conditions

Stop and emit `BLOCKED` when:

- the exact pin cannot be reproduced;
- a license or model right is unresolved;
- credentials or private data would be required outside the approved scope;
- a resource ceiling is exceeded;
- cleanup cannot be proven;
- an agent lacks identity or lease;
- a security veto remains unresolved;
- the requested action would install onto the active phone or modify production without a separate exact authorization.
