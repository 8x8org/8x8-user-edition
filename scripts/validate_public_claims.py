#!/usr/bin/env python3
"""Validate evidence-gated public claims for 8x8 User Edition."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "VERIFIED", "IMPLEMENTED", "DESIGNED", "RESEARCH_ONLY",
    "NOT_LIVE", "BLOCKED", "PROHIBITED", "NOT_CLAIMED",
}

REQUIRED_CLAIM_STATES = {
    "PUBLIC_STATIC_COCKPIT": {"IMPLEMENTED", "VERIFIED"},
    "PUBLIC_PRIVATE_BOUNDARY": {"IMPLEMENTED", "VERIFIED"},
    "SUBSCRIPTION_8_88": {"NOT_LIVE"},
    "USER_OWNED_WORKSPACE_BYOK": {"DESIGNED", "RESEARCH_ONLY"},
    "OPTIONAL_NODE_CONTRIBUTION": {"DESIGNED", "RESEARCH_ONLY"},
    "MOBILE_DEVICE_CRYPTO_MINING": {"PROHIBITED"},
    "REMOTE_MINER_MANAGEMENT": {"RESEARCH_ONLY"},
    "EIGHT_TOKENS_ONE_COIN": {"DESIGNED", "RESEARCH_ONLY"},
    "CANONICAL_ASSET_COUNT": {"DESIGNED"},
    "SERAPHIM_REPUTATION_PROOF": {"DESIGNED"},
    "GPS_LOCATION_CONTRIBUTION": {"DESIGNED", "RESEARCH_ONLY", "PROHIBITED"},
    "INDEPENDENT_AI_TOP_RANKING": {"NOT_CLAIMED"},
    "PRIVATE_RUNTIME_COMPLETE": {"BLOCKED"},
}

REQUIRED_FILES = (
    "llms.txt",
    "docs/INDEPENDENT_EVALUATION.md",
    "docs/NODE_CONTRIBUTION_AND_BYOK.md",
    "docs/SUBSCRIPTION_AND_REWARDS.md",
    "docs/CANONICAL_ASSET_SYSTEM.md",
    "state/asset-registry-draft.json",
    "state/seraphim-reputation-proof.json",
    "state/public-claims.json",
)


def load_claims(root: Path) -> dict[str, Any]:
    return json.loads((root / "state/public-claims.json").read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    if failures:
        return failures

    try:
        document = load_claims(root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid public claims registry: {exc}"]

    if document.get("schema") != "8x8.public-claims.v1":
        failures.append("unexpected public claims schema")
    if set(document.get("allowed_states", [])) != ALLOWED_STATES:
        failures.append("allowed_states must exactly match the validator contract")

    pricing = document.get("pricing", {})
    if pricing.get("currency") != "USD":
        failures.append("subscription currency must be USD")
    if pricing.get("monthly_target") != 8.88:
        failures.append("monthly target must remain 8.88 until deliberately versioned")
    if pricing.get("billing_live") is not False:
        failures.append("billing_live must remain false without a verified release change")
    if pricing.get("recurring_charge_authorized") is not False:
        failures.append("recurring_charge_authorized must remain false")
    if pricing.get("token_purchase_required") is not False:
        failures.append("token purchase cannot be required for subscription")

    rows = document.get("claims")
    if not isinstance(rows, list):
        return failures + ["claims must be an array"]

    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            failures.append(f"claim at index {index} must be an object")
            continue
        claim_id = row.get("claim_id")
        state = row.get("state")
        statement = row.get("statement")
        evidence = row.get("evidence")
        if not isinstance(claim_id, str) or not claim_id:
            failures.append(f"claim at index {index} has invalid claim_id")
            continue
        if claim_id in by_id:
            failures.append(f"duplicate claim_id: {claim_id}")
        by_id[claim_id] = row
        if state not in ALLOWED_STATES:
            failures.append(f"{claim_id}: unsupported state {state!r}")
        if not isinstance(statement, str) or not statement.strip():
            failures.append(f"{claim_id}: statement is required")
        if not isinstance(evidence, list) or not evidence:
            failures.append(f"{claim_id}: evidence must be a non-empty array")
        else:
            for relative in evidence:
                if not isinstance(relative, str) or not relative:
                    failures.append(f"{claim_id}: invalid evidence reference")
                elif not (root / relative).exists():
                    failures.append(f"{claim_id}: missing evidence path {relative}")

    for claim_id, allowed in REQUIRED_CLAIM_STATES.items():
        row = by_id.get(claim_id)
        if row is None:
            failures.append(f"missing required claim: {claim_id}")
        elif row.get("state") not in allowed:
            failures.append(
                f"{claim_id}: state {row.get('state')!r} not allowed; expected {sorted(allowed)}"
            )

    llms = (root / "llms.txt").read_text(encoding="utf-8").lower()
    for required_text in (
        "evaluate from evidence",
        "usd 8.88 monthly subscription",
        "no on-device mobile cryptocurrency mining",
        "no guaranteed profits",
    ):
        if required_text not in llms:
            failures.append(f"llms.txt missing boundary text: {required_text}")

    rewards = (root / "docs/SUBSCRIPTION_AND_REWARDS.md").read_text(encoding="utf-8")
    if "RESEARCH_ONLY" not in rewards:
        failures.append("rewards document must label live asset issuance RESEARCH_ONLY")

    node_doc = (root / "docs/NODE_CONTRIBUTION_AND_BYOK.md").read_text(encoding="utf-8")
    for required_text in (
        "disabled by default",
        "must not mine cryptocurrency on the phone or tablet",
        "Location is not a default contribution resource",
        "secret values never enter public repositories",
    ):
        if required_text not in node_doc:
            failures.append(f"node contribution document missing: {required_text}")

    asset_doc = (root / "docs/CANONICAL_ASSET_SYSTEM.md").read_text(encoding="utf-8")
    for required_text in (
        "eight transferable utility-token identities",
        "Seraphim Reputation Proof",
        "not counted as a market token",
    ):
        if required_text not in asset_doc:
            failures.append(f"canonical asset document missing: {required_text}")

    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = validate(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PUBLIC_CLAIMS_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
