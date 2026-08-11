#!/usr/bin/env python3
"""Issue and verify tamper-evident public-state receipts for 8x8 OS 0.1.0 Stable."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_REPO_PATH = "state/public-state.json"
EXPECTED_VERSION = "0.1.0"
EXPECTED_RELEASE = "0.1.0-stable"
FULL_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def receipt_digest(receipt: dict) -> str:
    body = deepcopy(receipt)
    body.pop("receipt_sha256", None)
    return sha256_bytes(canonical_bytes(body))


def validate_source_commit(value: object) -> str:
    """Return a newly canonicalized immutable full commit ID.

    The bytes round-trip is deliberate: downstream Git arguments are built from
    a fresh hex-only value rather than forwarding an arbitrary caller string.
    Branches, tags, option-like values, rev expressions and abbreviated SHAs
    cannot survive this boundary.
    """
    if not isinstance(value, str) or FULL_COMMIT_RE.fullmatch(value) is None:
        raise ValueError("source_commit must be a 40-character hexadecimal Git commit")
    return bytes.fromhex(value).hex()


def critical_assertions(state: dict) -> dict:
    keys = [
        "promotion_state",
        "stable_scope",
        "whole_system_complete",
        "whole_system_score",
        "private_control_plane_connected",
        "credentials_included",
        "wallet_material_included",
        "remote_shell_enabled",
        "live_trading_enabled",
        "public_billing_enabled",
        "hidden_telemetry_enabled",
        "targets_are_live_entitlements",
    ]
    return {key: state.get(key) for key in keys}


def state_bytes_at_commit(source_commit: str) -> bytes:
    """Read the exact public-state snapshot from one immutable full commit ID."""
    source_commit = validate_source_commit(source_commit)
    commit_object = source_commit + "^{commit}"
    state_object = source_commit + ":" + STATE_REPO_PATH
    try:
        subprocess.run(
            ["git", "cat-file", "-e", commit_object],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            shell=False,
        )
        completed = subprocess.run(
            ["git", "show", "--no-ext-diff", "--no-textconv", state_object],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(
            f"unable to resolve immutable public state at source_commit={source_commit}; "
            "ensure the full commit object and referenced state path are available in local git history"
            + (f": {detail}" if detail else "")
        ) from exc
    return completed.stdout


def state_at_commit(source_commit: str) -> tuple[bytes, dict]:
    source_commit = validate_source_commit(source_commit)
    raw = state_bytes_at_commit(source_commit)
    try:
        state = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid public state at source_commit={source_commit}") from exc
    return raw, state


def validate_release_identity(state: dict, *, context: str) -> None:
    if state.get("product_version") != EXPECTED_VERSION or state.get("release") != EXPECTED_RELEASE:
        raise ValueError(f"{context} version drifted from {EXPECTED_RELEASE}")
    if state.get("stable_scope") != "PUBLIC_WEB_CLIENT":
        raise ValueError(f"{context} stable scope drifted from PUBLIC_WEB_CLIENT")


def issue_receipt(source_commit: str, receipt_id: str) -> dict:
    source_commit = validate_source_commit(source_commit)
    state_raw, state = state_at_commit(source_commit)
    validate_release_identity(state, context="source public state")
    receipt = {
        "schema_version": EXPECTED_VERSION,
        "product_version": EXPECTED_VERSION,
        "release": EXPECTED_RELEASE,
        "receipt_id": receipt_id,
        "source_commit": source_commit,
        "state_path": STATE_REPO_PATH,
        "state_sha256": sha256_bytes(state_raw),
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reality": "PUBLIC_PRESENT",
        "truth_class": state.get("truth_class", "UNKNOWN"),
        "assertions": critical_assertions(state),
    }
    receipt["receipt_sha256"] = receipt_digest(receipt)
    return receipt


def verify_receipt(receipt: dict) -> None:
    required = {
        "schema_version",
        "product_version",
        "release",
        "receipt_id",
        "source_commit",
        "state_path",
        "state_sha256",
        "issued_at",
        "reality",
        "truth_class",
        "assertions",
        "receipt_sha256",
    }
    missing = required - set(receipt)
    if missing:
        raise ValueError(f"missing receipt fields: {sorted(missing)}")
    if receipt["schema_version"] != EXPECTED_VERSION or receipt["product_version"] != EXPECTED_VERSION or receipt["release"] != EXPECTED_RELEASE:
        raise ValueError(f"receipt version must be {EXPECTED_RELEASE}")
    if receipt["reality"] != "PUBLIC_PRESENT":
        raise ValueError("public receipt reality must be PUBLIC_PRESENT")
    if receipt["state_path"] != STATE_REPO_PATH:
        raise ValueError("unexpected state path")
    if receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("receipt tamper seal mismatch")

    # Validate immutable commit identity after the receipt's own tamper seal, but
    # before any Git resolution. The canonicalized value is fresh hex-only data.
    source_commit = validate_source_commit(receipt["source_commit"])
    state_raw, state = state_at_commit(source_commit)
    if sha256_bytes(state_raw) != receipt["state_sha256"]:
        raise ValueError("source-commit public-state SHA-256 mismatch")
    validate_release_identity(state, context="source-commit public state")
    if critical_assertions(state) != receipt["assertions"]:
        raise ValueError("receipt assertions do not match source-commit public state")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    issue = sub.add_parser("issue", help="emit one receipt JSON object to stdout")
    issue.add_argument("--commit", required=True)
    issue.add_argument("--id", required=True)
    sub.add_parser("verify", help="read one receipt JSON object from stdin and verify it")
    args = parser.parse_args()

    if args.command == "issue":
        receipt = issue_receipt(args.commit, args.id)
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        receipt = json.load(sys.stdin)
        if not isinstance(receipt, dict):
            raise ValueError("receipt input must be a JSON object")
        verify_receipt(receipt)
        print(
            f"RECEIPT_VERIFIED=PASS receipt_id={receipt['receipt_id']} "
            f"commit={receipt['source_commit']}"
        )


if __name__ == "__main__":
    main()
