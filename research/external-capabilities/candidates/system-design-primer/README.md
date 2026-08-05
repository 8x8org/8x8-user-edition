# System Design Primer Knowledge Adapter V1

This directory implements the first bounded candidate from MSG197.

## Purpose

Expose a small, citation-preserving topic index for `donnemartin/system-design-primer` at immutable commit `ae9bbd7b02d90b9866215de185217d33f39ab733`.

The adapter does **not** copy the upstream repository, install software, execute examples, import policy, or create a runtime dependency. It stores 8x8-authored topic summaries plus exact source links and attribution metadata.

## Security and trust

- Every record is `UNTRUSTED_EXTERNAL_REFERENCE`.
- Every source URL is pinned to the immutable upstream commit.
- Imported material cannot authorize tools, change policy, expand permissions, or satisfy an owner gate.
- Code examples remain non-executable unless a separate candidate-specific review approves them.
- The adapter has no network, shell, filesystem-write, service, scheduler, database, credential, wallet, publishing, or production authority.

## License

The source repository declares Creative Commons Attribution 4.0. Attribution and immutable source links are preserved in `MANIFEST.json` and `INDEX.json`.

## Validation

Run:

```text
python3 scripts/validate_msg197_system_design_adapter.py
```

The validator is standard-library only and performs no network or shell operations.

## Scope score

`100/100` may be claimed only for this static adapter's declared contract after CI passes. It never implies that the external repository is installed or that the whole 8x8 system is complete.
