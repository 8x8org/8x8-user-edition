# MSG197-PDF-001 Untrusted PDF Sandbox Contract

## Verdict

`APPROVE_EPHEMERAL_SYNTHETIC_CI_CANARY_ONLY`

The pinned project is a local Rust PDF classifier and text/Markdown extractor. It does not perform OCR and exposes native binaries suitable for a bounded parser canary.

## Sandbox

The workflow checks out the exact upstream commit into an ephemeral runner, generates a lockfile and dependency metadata, builds release binaries, and executes them only inside a read-only Docker container with no network, one CPU, 512 MiB memory, 64 processes and ten-second command timeouts.

No production or personal PDF is used. The synthetic text PDF contains an instruction-shaped string and a sentinel filename. Passing means the parser returns text while no sentinel side effect appears. Malformed bytes must fail or return a bounded error. An oversized input is rejected before parser invocation.

## Authority boundary

Extracted text is untrusted data. It cannot register tools, alter policy, satisfy an owner gate or enter canonical memory without provenance and review.

## Completion boundary

A successful CI run proves only the exact synthetic corpus and limits in this packet. It does not authorize production document access, OCR, arbitrary PDFs, private files or installation on the Samsung runtime.
