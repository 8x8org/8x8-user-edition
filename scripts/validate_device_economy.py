#!/usr/bin/env python3
"""Validate device contribution and wallet-economy truth boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads((root / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative} must contain an object")
    return value


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required = (
        "docs/DEVICE_CONTRIBUTION_PROFILES.md",
        "docs/MULTINETWORK_WALLET_AND_FEES.md",
        "state/device-contribution-profiles.json",
        "state/asset-registry-draft.json",
    )
    for relative in required:
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    if failures:
        return failures

    try:
        profiles = load(root, "state/device-contribution-profiles.json")
        assets = load(root, "state/asset-registry-draft.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid JSON contract: {exc}"]

    enrollment = profiles.get("enrollment", {})
    for key in (
        "installation_is_consent",
        "subscription_is_consent",
        "wallet_creation_is_consent",
        "telegram_use_is_consent",
        "browser_use_is_consent",
    ):
        if enrollment.get(key) is not False:
            failures.append(f"{key} must remain false")
    for key in (
        "affirmative_node_enrollment_required",
        "separate_resource_consent_required",
        "revocable",
        "local_pause_required",
        "emergency_stop_required",
    ):
        if enrollment.get(key) is not True:
            failures.append(f"{key} must remain true")

    rows = {row.get("profile_id"): row for row in profiles.get("profiles", [])}
    expected = {
        "STANDARD_25": (25, True),
        "ENHANCED_75": (75, True),
    }
    for profile_id, (ceiling, separate) in expected.items():
        row = rows.get(profile_id)
        if not row:
            failures.append(f"missing profile: {profile_id}")
            continue
        if row.get("default_enabled") is not False:
            failures.append(f"{profile_id} cannot be enabled by default")
        if row.get("separate_approval_required") is not separate:
            failures.append(f"{profile_id} requires separate approval")
        maximums = row.get("maximums", {})
        for resource in ("cpu_percent", "gpu_percent", "available_memory_percent"):
            if maximums.get(resource) != ceiling:
                failures.append(f"{profile_id} {resource} must equal {ceiling}")
        if row.get("automatic_after_enrollment") is not True:
            failures.append(f"{profile_id} should automate only after enrollment")

    platforms = {row.get("platform"): row for row in profiles.get("platforms", [])}
    for platform in ("APPLE_APP_STORE", "GOOGLE_PLAY"):
        row = platforms.get(platform, {})
        if row.get("local_crypto_mining") != "PROHIBITED":
            failures.append(f"{platform} local mining must remain prohibited")
    if platforms.get("TELEGRAM_MINI_APP", {}).get("background_compute") != "WEBVIEW_LIFECYCLE_LIMITED":
        failures.append("Telegram compute must remain webview-lifecycle limited")
    if platforms.get("BROWSER", {}).get("background_compute") != "THROTTLED_OR_FROZEN":
        failures.append("browser background compute must remain throttled or frozen")

    routing = profiles.get("asset_routing", {})
    if routing.get("ethereum_mainnet_mineable") is not False:
        failures.append("Ethereum Mainnet cannot be marked mineable")
    if routing.get("bitcoin_requires_mining_capable_hardware") is not True:
        failures.append("Bitcoin routing must require mining-capable hardware")
    if routing.get("profitability_guaranteed") is not False:
        failures.append("profitability cannot be guaranteed")
    if routing.get("treasury_destination_requires_consent") is not True:
        failures.append("treasury destination requires consent")

    if assets.get("status") != "BLOCKED_IDENTITY_COUNT_CONFLICT":
        failures.append("asset registry must remain blocked until count conflict is resolved")
    intended = assets.get("intended_model", {})
    observed = assets.get("observed_utility_symbols", [])
    if intended.get("utility_token_count") != 8:
        failures.append("intended utility-token count must remain eight")
    if len(observed) != 9 or assets.get("observed_utility_symbol_count") != 9:
        failures.append("observed utility-token conflict must preserve all nine symbols")
    for key in (
        "issuance_authorized",
        "deployment_authorized",
        "trading_authorized",
        "treasury_movement_authorized",
        "wallet_custody_authorized",
    ):
        if assets.get(key) is not False:
            failures.append(f"{key} must remain false")

    fees = assets.get("fee_targets", {})
    for key in ("coin_buy_bps", "coin_sell_bps", "nft_secondary_buy_sell_bps"):
        if fees.get(key) != 488:
            failures.append(f"{key} must remain 488 basis points")
    if fees.get("ordinary_protocol_transfer_bps") != 0:
        failures.append("ordinary protocol transfer fee target must remain zero")
    if fees.get("live") is not False:
        failures.append("fee targets cannot be marked live")

    subscription = assets.get("subscription", {})
    if subscription.get("monthly_usd_target") != 8.88:
        failures.append("monthly subscription target must remain USD 8.88")
    if subscription.get("live") is not False:
        failures.append("subscription cannot be marked live")
    if subscription.get("token_purchase_required") is not False:
        failures.append("subscription cannot require token purchase")
    if subscription.get("node_contribution_required") is not False:
        failures.append("subscription cannot require node contribution")

    device_doc = (root / "docs/DEVICE_CONTRIBUTION_PROFILES.md").read_text(encoding="utf-8")
    for text in (
        "off until the user affirmatively enrolls",
        "must not mine cryptocurrency on the phone or tablet",
        "Ethereum Mainnet is proof-of-stake",
        "A profile ceiling is not a target",
    ):
        if text not in device_doc:
            failures.append(f"device profile documentation missing: {text}")

    wallet_doc = (root / "docs/MULTINETWORK_WALLET_AND_FEES.md").read_text(encoding="utf-8")
    for text in (
        "nine utility-token symbols",
        "4.88%",
        "ordinary wallet transfer protocol fee target: 0%",
        "No 8x8 coin",
    ):
        if text not in wallet_doc:
            failures.append(f"wallet documentation missing: {text}")

    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = validate(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("DEVICE_ECONOMY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
