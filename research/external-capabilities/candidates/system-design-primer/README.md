# MSG197-KNOWLEDGE-001: System Design Knowledge Index

## Truth state

`STATIC_ATTRIBUTED_INDEX_ONLY`

This directory implements the first bounded MSG197 work packet for Issue #45. It indexes selected architecture topics from `donnemartin/system-design-primer` at immutable commit `ae9bbd7b02d90b9866215de185217d33f39ab733`.

It does **not** install the upstream repository, vendor its code, execute examples, register tools, modify runtime policy, or grant any capability. The upstream material is external reference data and remains subordinate to 8x8 governance.

## Artifacts

- `SOURCE_MANIFEST.json`: exact source, license, trust, staleness and rollback metadata.
- `TOPIC_INDEX.json`: curated topic-to-8x8-domain mapping with exact commit URLs.
- `ATTRIBUTION_AND_EXCERPT_POLICY.md`: attribution, excerpt and transformation rules.
- `THREAT_AND_TRUST_BOUNDARY.md`: prompt-injection and executable-content boundary.
- `receipts/MSG197_KNOWLEDGE_001_SHA256SUMS.txt`: governed artifact hashes.
- `receipts/MSG197_KNOWLEDGE_001_RECEIPT.json`: machine-readable completion receipt.
- `scripts/validate_msg197_knowledge_001.py`: deterministic validator.

## Source and license

Source: `donnemartin/system-design-primer`  
Pinned commit: `ae9bbd7b02d90b9866215de185217d33f39ab733`  
License: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)  
Copyright notice: Copyright 2017 Donne Martin

The source links in the manifests resolve to the exact pinned commit rather than a moving branch.

## Advancement boundary

This packet may advance only to `STATIC_INDEX_VALIDATED`. It cannot become an executable knowledge agent, retrieval plugin, package, service or policy source without a separate reviewed design and owner gate.
