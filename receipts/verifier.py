#!/usr/bin/env python3
"""Issue and verify tamper-evident public-state receipts for 8x8 OS 0.0.1 Beta."""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "state/public-state.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def receipt_digest(receipt: dict) -> str:
    body = deepcopy(receipt)
    body.pop("receipt_sha256", None)
    return sha256_bytes(canonical_bytes(body))


def critical_assertions(state: dict) -> dict:
    keys = [
        "public_beta",
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


def issue_receipt(source_commit: str, receipt_id: str) -> dict:
    if len(source_commit) != 40 or any(c not in "0123456789abcdef" for c in source_commit.lower()):
        raise ValueError("source_commit must be a 40-character hexadecimal Git commit")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state.get("product_version") != "0.0.1":
        raise ValueError("public state product_version drifted from 0.0.1")
    receipt = {
        "schema_version": "0.0.1",
        "product_version": "0.0.1",
        "receipt_id": receipt_id,
        "source_commit": source_commit.lower(),
        "state_path": "state/public-state.json",
        "state_sha256": file_sha256(STATE_PATH),
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
    if receipt["schema_version"] != "0.0.1" or receipt["product_version"] != "0.0.1":
        raise ValueError("receipt version must be 0.0.1")
    if receipt["reality"] != "PUBLIC_PRESENT":
        raise ValueError("public receipt reality must be PUBLIC_PRESENT")
    if receipt["state_path"] != "state/public-state.json":
        raise ValueError("unexpected state path")
    if receipt_digest(receipt) != receipt["receipt_sha256"]:
        raise ValueError("receipt tamper seal mismatch")
    if file_sha256(STATE_PATH) != receipt["state_sha256"]:
        raise ValueError("public-state SHA-256 mismatch")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if critical_assertions(state) != receipt["assertions"]:
        raise ValueError("receipt assertions do not match current public state")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    issue = sub.add_parser("issue")
    issue.add_argument("--commit", required=True)
    issue.add_argument("--id", required=True)
    issue.add_argument("--out", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("receipt")
    args = parser.parse_args()

    if args.command == "issue":
        receipt = issue_receipt(args.commit, args.id)
        out = ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"RECEIPT_ISSUED=PASS path={out} state_sha256={receipt['state_sha256']}")
    else:
        path = ROOT / args.receipt
        receipt = json.loads(path.read_text(encoding="utf-8"))
        verify_receipt(receipt)
        print(f"RECEIPT_VERIFIED=PASS receipt_id={receipt['receipt_id']} commit={receipt['source_commit']}")


if __name__ == "__main__":
    main()
