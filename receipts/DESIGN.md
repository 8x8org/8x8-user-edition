# Receipt Design Note: Public State Verifiable Receipts

## Purpose

This document explains the threat model, design decisions, and limitations of
the verifiable receipt scheme introduced for `state/public-state.json`.

---

## Problem

The evidence ladder in 8x8 User Edition relies on `state/public-state.json` to
make public boundary assertions (e.g. "no credentials included", "no remote
shell enabled"). Without a tamper-evident binding, there is no way for an
independent observer to verify that a published state file corresponds to a
specific, immutable revision of the repository.

---

## Threat Model

### What the receipt proves

1. **Content integrity at issuance.** The `state_hash` field is the SHA-256
   digest of the raw bytes of `state/public-state.json` as it existed when the
   receipt was issued. Any post-issuance modification of the state file will
   produce a different hash.

2. **Receipt self-integrity.** The `receipt_hash` field is the SHA-256 digest
   of the canonical JSON of the receipt body (all fields except `receipt_hash`
   itself, serialised with sorted keys and no extra whitespace). Altering any
   field in the receipt — including the `state_hash` or `commit_sha` — will
   produce a different `receipt_hash`, allowing the verifier to detect tampering.

3. **Revision linkage.** The `commit_sha` field binds the receipt to a specific
   40-character git commit SHA in the public GitHub repository. Because git
   commits are content-addressed and publicly auditable, the commit SHA can be
   independently looked up on GitHub to confirm the state of the repository at
   the time the receipt was issued.

4. **Critical boundary flags.** The `state_assertions` object embeds the six
   most security-sensitive boolean flags from the state file. An independent
   verifier can confirm that those flags are `false` without fetching the full
   state file from a remote source.

### What the receipt does NOT prove

- **No cryptographic signature.** Receipts are not signed with a private key.
  They are hash-linked documents. Anyone with write access to the repository
  could replace both the state file and the receipt. The receipt is useful for
  detecting accidental or opportunistic tampering; it is not a substitute for
  code-signing or a transparency log.

- **No server-side attestation.** The receipt does not prove that a live server
  is running the stated version. It only proves that, at the named commit, the
  state file had the given content.

- **No guarantee of continuous validity.** A receipt is a point-in-time
  snapshot. If the state file changes after the receipt is issued, the receipt
  becomes stale. New receipts should be issued whenever the state file is
  updated.

- **No append-only log.** The current scheme does not maintain a signed,
  append-only log of past receipts. Each release has exactly one receipt. A
  transparency log (e.g. a Merkle tree) is a natural extension but is out of
  scope for this initial implementation.

### Trust assumptions

- **GitHub commit integrity.** The scheme relies on GitHub's integrity for the
  commit-SHA → content mapping. GitHub is a trusted public record.
- **SHA-256 collision resistance.** Tampering is detected via SHA-256 hashes,
  which are currently considered collision-resistant.
- **Honest issuance.** The receipt is honest at the time it is created. A
  malicious issuer could create a false receipt. Reviewers should verify the
  `commit_sha` directly on GitHub.

---

## Schema Overview

Receipts are JSON objects that conform to
[`receipts/schema/receipt-schema.json`](schema/receipt-schema.json).

| Field | Type | Description |
|---|---|---|
| `schema_version` | semver string | Version of the receipt schema |
| `receipt_id` | string | Human-readable unique ID (e.g. `8x8-user-edition-0.1.0-beta-20260726`) |
| `issued_at` | ISO 8601 UTC | Timestamp at which the receipt was created |
| `repository` | string | `owner/repo` of the public GitHub repository |
| `commit_sha` | string (40 hex) | Git commit SHA the receipt covers |
| `state_file` | string (const) | Always `state/public-state.json` |
| `state_hash` | string (64 hex) | SHA-256 of the raw bytes of the state file |
| `hash_algorithm` | string (const) | Always `sha256` |
| `state_assertions` | object | Subset of boolean boundary flags from the state file |
| `receipt_hash` | string (64 hex) | SHA-256 of canonical receipt body (tamper seal) |

---

## Verification Algorithm

The [`receipts/verifier.py`](verifier.py) script performs four checks in order:

1. **Structural validation** — all required fields are present, no unexpected
   fields exist, and all values have the correct types and patterns.

2. **Receipt hash check** — `receipt_hash` is recomputed from the receipt body
   and compared with the stored value. Any modification to any field fails this
   check.

3. **State file hash check** — the SHA-256 of the on-disk `state/public-state.json`
   is compared with `state_hash`. Fails if the file was altered since issuance.

4. **Assertions cross-check** — the values in `state_assertions` are compared
   with the corresponding keys in the current state file. Fails if any flag has
   been changed.

```
$ python3 receipts/verifier.py receipts/examples/receipt-0.1.0-beta.json
RECEIPT_VERIFIED receipt_id='8x8-user-edition-0.1.0-beta-20260726' commit=6aec283cb3ee state_hash=1ef0c8813c2ccc7e…
```

Exit code 0 means all checks passed. Any non-zero exit code means at least one
check failed; the reason is printed to stderr.

---

## Issuance Process

Receipts are created once per meaningful state-file change and committed to the
repository. They are not generated automatically in CI; instead CI *verifies*
the committed receipt.

To issue a new receipt (maintainer only):

```bash
python3 - <<'PY'
import json, sys
sys.path.insert(0, 'receipts')
from verifier import issue_receipt
from pathlib import Path

receipt = issue_receipt(
    Path('state/public-state.json'),
    commit_sha='<40-char-sha-of-the-relevant-commit>',
    receipt_id='8x8-user-edition-<release>-<YYYYMMDD>',
)
print(json.dumps(receipt, indent=2, sort_keys=True))
PY
```

Copy the output to `receipts/examples/receipt-<release>.json` and commit both
files together.

---

## Future Extensions

- **Signed receipts.** Add an optional `signature` field containing a detached
  signature from a well-known public key (e.g. GPG or Sigstore).
- **Transparency log.** Record each receipt in a Merkle-based append-only log
  to prevent deletion of past evidence.
- **Release automation.** A GitHub Actions workflow could issue and commit a new
  receipt automatically when `state/public-state.json` is updated on `main`.
