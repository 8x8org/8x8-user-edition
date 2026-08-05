# MSG197 Errata and Supersession Record V2

## Purpose

This file preserves the original intake artifacts as historical evidence while preventing their early assumptions from being used as current candidate truth.

## Current authority order

1. `CANDIDATE_STATUS_LEDGER_V2.json`
2. `MSG197_COMPLETION_MATRIX_V2.md`
3. candidate-specific manifests, receipts, and merged pull requests
4. council session and vote receipts
5. original census, evaluation matrix, and backlog as historical first-pass evidence

## Corrected identities

### `uber/ADR`

The original intake treated ADR as an Architecture Decision Record tool. The exact pinned repository is **Agentic AI Detection and Response**. It contains a sensor, benchmark, detector, and synthetic security fixtures. The open-source scope does not include the separately described prevention product.

Current decision: adopt only telemetry schema and attack taxonomy patterns. No production telemetry, private sessions, provider credentials, or prevention capability are authorized.

### `cloudflare/computer`

The original intake framed this candidate as browser computer-use tooling. The exact pinned repository is a preview Durable Object virtual filesystem and execution substrate. It can expose filesystem-only, shell, JavaScript, and container backends, with the container backend capable of full Linux and real network access.

Current decision: retain workspace-boundary ideas and defer every execution backend. No Cloudflare account, Worker, Durable Object, FUSE mount, container, shell, JavaScript, network execution, or credential is authorized.

## PDF status supersession

The earlier ledger described PDF Inspector as a pending canary. PR #71 merged at `a10d0fc3065a755fc1b8de4c0b2fe59f3664b2d8`.

Current truth:

- parser canary: `PASS`;
- promotion gate: `BLOCKED`;
- installation: `NOT_INSTALLED`;
- vulnerabilities: `RUSTSEC-2026-0176` and `RUSTSEC-2026-0177` in `pyo3 0.25.1`;
- maintenance warning: `RUSTSEC-2026-0192` for `ttf-parser 0.25.1`.

A green evidence workflow means the blocked state was reproduced exactly. It does not mean the candidate passed the promotion gate.

## Deferred platform assumptions

- AirLLM requires an approved external CUDA node for the selected path and is rejected for Samsung Termux and active Ubuntu PRoot.
- Supervision is limited to a model-agnostic external-node benchmark. No model, camera, microphone, API key, or private media is authorized.
- Next.js and Tailwind remain deferred because the static public client is still canonical and no approved requirement justifies the added server or build toolchain.

## Council truth

The council framework is merged, but zero valid identity- and lease-bound votes exist. ChatGPT's submission is advisory only and cannot establish quorum.

## Installation truth

All thirteen candidate packets are merged. No third-party candidate has been installed into the active 8x8 runtime. Research completion, a canary pass, a blocked promotion, and production integration are distinct states.
