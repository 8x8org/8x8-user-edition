#!/usr/bin/env python3
"""Validate MSG197 council framework without network or side effects."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities" / "council"
BASE_RESOLVED = BASE.resolve()
EXPECTED_DIGEST = "ab40f0f1c010d862f38c34ec4efea5e18ff7c405d68231b82815342521a749e7"
EXPECTED_TRUTH_STATE = "FRAMEWORK_PASS_REAL_COUNCIL_PENDING"
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"unable to load JSON {path.relative_to(ROOT)}: {exc}")


def resolve_council_artifact(name: str) -> Path:
    if not name or name.startswith("-"):
        fail(f"unsafe council artifact path: {name!r}")
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 1:
        fail(f"unsafe council artifact path: {name}")
    target = (BASE / relative).resolve()
    try:
        target.relative_to(BASE_RESOLVED)
    except ValueError as exc:
        raise SystemExit(f"council artifact escapes base: {name}") from exc
    if not target.is_file():
        fail(f"missing council artifact: {name}")
    return target


def main() -> None:
    schema = load_json(BASE / "COUNCIL_VOTE.schema.json")
    advisory = load_json(BASE / "CHATGPT_ADVISORY.json")
    session = load_json(BASE / "COUNCIL_SESSION.json")
    receipt = load_json(BASE / "receipts" / "MSG197_COUNCIL_001_RECEIPT.json")

    require(str(schema.get("$id", "")).endswith("msg197-council-vote-v1.json"), "unexpected council vote schema ID")
    require(advisory.get("input_digest") == EXPECTED_DIGEST, "advisory input digest drift")
    require(advisory.get("participant", {}).get("identity_status") == "UNVERIFIED", "advisory identity must remain unverified")
    require(advisory.get("lease", {}).get("status") == "NOT_ISSUED", "advisory lease must remain unissued")
    require(advisory.get("receipt_status") == "ADVISORY_ONLY", "ChatGPT submission must remain advisory-only")
    require(advisory.get("output_digest") is None, "advisory must not claim a signed output digest")

    recommendations = advisory.get("recommendations", [])
    require(len(recommendations) == 13, "expected thirteen advisory recommendations")
    require(len({item.get("candidate") for item in recommendations}) == 13, "advisory candidate identities are not unique")

    require(session.get("input_pin_set_sha256") == EXPECTED_DIGEST, "session input digest drift")
    require(session.get("coordinator", {}).get("preferred") == "Hermes", "Hermes must remain preferred coordinator")
    require(len(session.get("participants", [])) == 6, "expected six council participants")
    require(session.get("quorum", {}).get("valid_votes") == 0, "real council votes must not be fabricated")
    require(session.get("quorum", {}).get("reached") is False, "quorum must remain false")
    require(session.get("rules", {}).get("missing_identity_cannot_vote") is True, "identity gate missing")
    require(session.get("rules", {}).get("missing_or_expired_lease_cannot_vote") is True, "lease gate missing")

    require(receipt.get("valid_votes") == 0, "receipt valid-vote count drift")
    require(receipt.get("quorum_reached") is False, "receipt quorum must remain false")
    require(receipt.get("council_complete") is False, "receipt must not claim council completion")
    require(session.get("truth_state") == EXPECTED_TRUTH_STATE, "session truth state drift")
    require(receipt.get("truth_state") == EXPECTED_TRUTH_STATE, "receipt truth state drift")
    require(session.get("truth_state") == receipt.get("truth_state"), "session and receipt truth states disagree")

    sums_path = BASE / "receipts" / "MSG197_COUNCIL_001_SHA256SUMS.txt"
    seen: set[str] = set()
    for raw in sums_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        fields = raw.split("  ", 1)
        require(len(fields) == 2, f"malformed council hash line: {raw!r}")
        digest, name = fields
        require(bool(SHA64.fullmatch(digest)), f"invalid SHA-256 digest for {name}")
        require(name not in seen, f"duplicate council hash path: {name}")
        seen.add(name)
        target = resolve_council_artifact(name)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        require(actual == digest, f"council hash mismatch: {name}")
        require(receipt.get("artifacts", {}).get(name) == digest, f"receipt hash mismatch: {name}")

    require(len(seen) == 4, "expected four governed council artifacts")
    print("MSG197-COUNCIL-001 framework validated; valid_votes=0 quorum=false")


if __name__ == "__main__":
    main()
