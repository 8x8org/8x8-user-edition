#!/usr/bin/env python3
"""
Public verifier for 8x8 User Edition state receipts.

Verifies that a receipt:
  1. Matches the receipt schema (structural validation).
  2. Has an intact receipt_hash (tamper detection over all other fields).
  3. Has a state_hash that matches the SHA-256 of the current local
     state/public-state.json file (state integrity check).
  4. Has state_assertions that match the values in the current state file.

All verification is performed against public repository data only.
No credentials, private endpoints, or network access is required for
the core local verification mode.

Usage:
    python3 receipts/verifier.py receipts/examples/receipt-0.1.0-beta.json
    python3 receipts/verifier.py <receipt.json> [--state-file <path>]
    python3 receipts/verifier.py <receipt.json> --no-state-check
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SCHEMA_VERSION = "1.0.0"
REQUIRED_FIELDS = {
    "schema_version",
    "receipt_id",
    "issued_at",
    "repository",
    "commit_sha",
    "state_file",
    "state_hash",
    "hash_algorithm",
    "state_assertions",
    "receipt_hash",
}
REQUIRED_ASSERTIONS = {
    "private_control_plane_connected",
    "credentials_included",
    "wallet_material_included",
    "remote_shell_enabled",
    "live_trading_enabled",
    "targets_are_live_entitlements",
}
HASH_ALGORITHM = "sha256"
STATE_FILE_PATH = "state/public-state.json"

# Compile patterns once
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_ISO8601_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


class VerificationError(Exception):
    """Raised when receipt verification fails."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: dict) -> bytes:
    """Return canonical (sorted-keys, no spaces) JSON bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def compute_receipt_hash(receipt: dict) -> str:
    """Compute the expected receipt_hash for the given receipt document.

    The hash is computed over the canonical JSON of the receipt with the
    ``receipt_hash`` field removed.
    """
    body = {k: v for k, v in receipt.items() if k != "receipt_hash"}
    return sha256_hex(canonical_json(body))


def validate_structure(receipt: dict) -> None:
    """Raise VerificationError if the receipt is structurally invalid."""
    missing = REQUIRED_FIELDS - receipt.keys()
    if missing:
        raise VerificationError(f"Receipt is missing required fields: {sorted(missing)}")

    extra = receipt.keys() - REQUIRED_FIELDS
    if extra:
        raise VerificationError(f"Receipt contains unexpected fields: {sorted(extra)}")

    sv = receipt["schema_version"]
    if not isinstance(sv, str) or not _SEMVER_RE.match(sv):
        raise VerificationError(f"schema_version must be a semver string, got: {sv!r}")

    rid = receipt["receipt_id"]
    if not isinstance(rid, str) or not rid:
        raise VerificationError("receipt_id must be a non-empty string")

    ia = receipt["issued_at"]
    if not isinstance(ia, str) or not _ISO8601_RE.match(ia):
        raise VerificationError(
            f"issued_at must be an ISO 8601 UTC timestamp ending in Z, got: {ia!r}"
        )

    repo = receipt["repository"]
    if not isinstance(repo, str) or not _REPO_RE.match(repo):
        raise VerificationError(
            f"repository must be in 'owner/repo' format, got: {repo!r}"
        )

    sha = receipt["commit_sha"]
    if not isinstance(sha, str) or not _COMMIT_RE.match(sha):
        raise VerificationError(
            f"commit_sha must be a 40-character hex string, got: {sha!r}"
        )

    sf = receipt["state_file"]
    if sf != STATE_FILE_PATH:
        raise VerificationError(
            f"state_file must be '{STATE_FILE_PATH}', got: {sf!r}"
        )

    sh = receipt["state_hash"]
    if not isinstance(sh, str) or not _SHA256_RE.match(sh):
        raise VerificationError(
            f"state_hash must be a 64-character hex sha256 digest, got: {sh!r}"
        )

    ha = receipt["hash_algorithm"]
    if ha != HASH_ALGORITHM:
        raise VerificationError(
            f"hash_algorithm must be '{HASH_ALGORITHM}', got: {ha!r}"
        )

    assertions = receipt["state_assertions"]
    if not isinstance(assertions, dict):
        raise VerificationError("state_assertions must be an object")
    missing_a = REQUIRED_ASSERTIONS - assertions.keys()
    if missing_a:
        raise VerificationError(
            f"state_assertions is missing required keys: {sorted(missing_a)}"
        )
    for key, val in assertions.items():
        if not isinstance(val, bool):
            raise VerificationError(
                f"state_assertions[{key!r}] must be a boolean, got: {val!r}"
            )

    rh = receipt["receipt_hash"]
    if not isinstance(rh, str) or not _SHA256_RE.match(rh):
        raise VerificationError(
            f"receipt_hash must be a 64-character hex sha256 digest, got: {rh!r}"
        )


def verify_receipt_hash(receipt: dict) -> None:
    """Raise VerificationError if the receipt_hash does not match."""
    expected = compute_receipt_hash(receipt)
    actual = receipt["receipt_hash"]
    if actual != expected:
        raise VerificationError(
            f"receipt_hash mismatch — the receipt has been altered.\n"
            f"  stored : {actual}\n"
            f"  computed: {expected}"
        )


def verify_state_hash(receipt: dict, state_path: Path) -> None:
    """Raise VerificationError if the state_hash does not match the file on disk."""
    if not state_path.is_file():
        raise VerificationError(f"State file not found: {state_path}")
    data = state_path.read_bytes()
    actual = sha256_hex(data)
    expected = receipt["state_hash"]
    if actual != expected:
        raise VerificationError(
            f"state_hash mismatch — the state file does not match this receipt.\n"
            f"  receipt : {expected}\n"
            f"  on-disk : {actual}"
        )


def verify_state_assertions(receipt: dict, state_path: Path) -> None:
    """Raise VerificationError if state_assertions diverge from the state file."""
    if not state_path.is_file():
        raise VerificationError(f"State file not found: {state_path}")
    state = json.loads(state_path.read_text())
    mismatches = []
    for key, receipt_val in receipt["state_assertions"].items():
        state_val = state.get(key)
        if state_val != receipt_val:
            mismatches.append(
                f"  {key}: receipt={receipt_val!r}, state={state_val!r}"
            )
    if mismatches:
        raise VerificationError(
            "state_assertions do not match the state file:\n" + "\n".join(mismatches)
        )


def verify(
    receipt_path: Path,
    *,
    state_path: Path | None = None,
    check_state: bool = True,
) -> None:
    """Run the full verification pipeline.

    Parameters
    ----------
    receipt_path:
        Path to the receipt JSON file to verify.
    state_path:
        Path to the state file. Defaults to ``state/public-state.json``
        relative to the current working directory.
    check_state:
        When False, skip the on-disk state hash and assertion checks.
        Useful for CI environments where only the receipt itself is available.
    """
    try:
        receipt = json.loads(receipt_path.read_text())
    except json.JSONDecodeError as exc:
        raise VerificationError(f"Receipt is not valid JSON: {exc}") from exc

    if not isinstance(receipt, dict):
        raise VerificationError("Receipt must be a JSON object")

    validate_structure(receipt)
    verify_receipt_hash(receipt)

    if check_state:
        if state_path is None:
            state_path = Path(STATE_FILE_PATH)
        verify_state_hash(receipt, state_path)
        verify_state_assertions(receipt, state_path)


def issue_receipt(state_path: Path, commit_sha: str, receipt_id: str) -> dict:
    """Generate a new receipt for the given state file and commit SHA.

    This helper is used to bootstrap the first receipt from a known-good
    state. It should not be called automatically in CI — receipts are
    created once per release and committed alongside the state file.
    """
    import datetime

    if not state_path.is_file():
        raise ValueError(f"State file not found: {state_path}")
    if not _COMMIT_RE.match(commit_sha):
        raise ValueError(f"commit_sha must be 40 hex chars, got: {commit_sha!r}")

    data = state_path.read_bytes()
    state = json.loads(data)
    state_hash = sha256_hex(data)

    assertions = {k: state[k] for k in REQUIRED_ASSERTIONS if k in state}

    body = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": receipt_id,
        "issued_at": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "repository": "8x8org/8x8-user-edition",
        "commit_sha": commit_sha,
        "state_file": STATE_FILE_PATH,
        "state_hash": state_hash,
        "hash_algorithm": HASH_ALGORITHM,
        "state_assertions": assertions,
    }
    receipt_hash = sha256_hex(canonical_json(body))
    return {**body, "receipt_hash": receipt_hash}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify an 8x8 User Edition public state receipt.",
        epilog=(
            "Exit code 0 means all checks passed. "
            "Non-zero means at least one check failed."
        ),
    )
    parser.add_argument(
        "receipt",
        metavar="RECEIPT",
        type=Path,
        help="Path to the receipt JSON file.",
    )
    parser.add_argument(
        "--state-file",
        metavar="PATH",
        type=Path,
        default=None,
        help=(
            f"Path to the state file (default: {STATE_FILE_PATH} "
            "relative to the current directory)."
        ),
    )
    parser.add_argument(
        "--no-state-check",
        action="store_true",
        default=False,
        help="Skip the on-disk state hash and assertion checks.",
    )
    args = parser.parse_args(argv)

    try:
        verify(
            args.receipt,
            state_path=args.state_file,
            check_state=not args.no_state_check,
        )
    except VerificationError as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1

    receipt_path = args.receipt
    receipt = json.loads(receipt_path.read_text())
    print(
        f"RECEIPT_VERIFIED receipt_id={receipt['receipt_id']!r} "
        f"commit={receipt['commit_sha'][:12]} "
        f"state_hash={receipt['state_hash'][:16]}…"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
