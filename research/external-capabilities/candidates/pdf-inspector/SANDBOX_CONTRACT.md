# MSG197-PDF-001 Untrusted PDF Sandbox Contract

## Verdict

`PASS_PARSER_CANARY_SUPPLY_CHAIN_BLOCKED`

The pinned project is a local Rust PDF classifier and text/Markdown extractor. It does not perform OCR. Its exact native binaries were exercised successfully only as a bounded synthetic parser canary.

## Executed sandbox

GitHub Actions run `31042742548` fetched immutable upstream commit `12e9a655e36924564057464bf25494b8c027eb57`, generated a Cargo lockfile, built the exact release binaries, and executed them inside a read-only Docker container with:

- no network;
- one CPU;
- 512 MiB memory;
- 64-process limit;
- all Linux capabilities dropped;
- no-new-privileges;
- an unprivileged user;
- ten-second command timeouts.

No production or personal PDF was used. The instruction-shaped text remained inert, malformed bytes returned a bounded failure, and the oversized fixture was rejected before parser invocation. Cleanup completed.

## Supply-chain block

The generated dependency graph is not eligible for adoption or installation.

`cargo audit` returned exit code `1` with:

- `RUSTSEC-2026-0176` affecting `pyo3 0.25.1`;
- `RUSTSEC-2026-0177` affecting `pyo3 0.25.1`;
- no patched versions reported for either advisory in the observed audit;
- `RUSTSEC-2026-0192`, warning that `ttf-parser 0.25.1` is unmaintained.

The zero-vulnerability promotion gate remains enforced. The workflow accepts this exact finding set only as a reproducible blocked-evidence state and fails on advisory drift. It does not convert the candidate into an approved plugin.

## Authority boundary

Extracted text is untrusted data. It cannot register tools, alter policy, satisfy an owner gate, enter canonical memory, or expand filesystem, network, credential, browser, wallet, publishing, or execution authority without separate provenance and review.

## Completion boundary

This packet completes the exact synthetic parser-canary investigation. It does not authorize:

- installation on Termux, Ubuntu PRoot, Replit, Vercel, Neon, or production;
- access to private or arbitrary documents;
- OCR;
- a public upload endpoint;
- background document ingestion;
- dependency overrides;
- ignoring or suppressing the recorded advisories.

Reconsideration requires a new immutable upstream pin, a reproducible lockfile, zero unresolved vulnerabilities, maintained dependencies, the same sandbox limits, an uninstall proof, and candidate-level owner approval.
