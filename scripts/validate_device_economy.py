#!/usr/bin/env python3
"""Validate device contribution, canonical assets, and wallet-economy boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

CANONICAL_TOKENS = {
    "Tx8": "TRANSACTION_AND_MARKETPLACE",
    "Ux8": "USER_UTILITY_AND_ACCESS",
    "Fx8": "FABRIC_OPERATIONS",
    "XM8": "EXECUTION_AND_COMPUTE",
    "0x8": "PROTOCOL_AND_INNOVATION",
    "TM8": "COMMUNITY_AND_IDENTITY",
    "Mx8": "MINING_AND_RESOURCE_CONTRIBUTION",
    "Sx8": "STORAGE_AND_SERVICES",
}


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
        "docs/CANONICAL_ASSET_SYSTEM.md",
        "state/device-contribution-profiles.json",
        "state/asset-registry-draft.json",
        "state/seraphim-reputation-proof.json",
    )
    for relative in required:
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    if failures:
        return failures

    try:
        profiles = load(root, "state/device-contribution-profiles.json")
        assets = load(root, "state/asset-registry-draft.json")
        srp = load(root, "state/seraphim-reputation-proof.json")
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
    for profile_id, ceiling in {"STANDARD_25": 25, "ENHANCED_75": 75}.items():
        row = rows.get(profile_id)
        if not row:
            failures.append(f"missing profile: {profile_id}")
            continue
        if row.get("default_enabled") is not False:
            failures.append(f"{profile_id} cannot be enabled by default")
        if row.get("separate_approval_required") is not True:
            failures.append(f"{profile_id} requires separate approval")
        maximums = row.get("maximums", {})
        for resource in ("cpu_percent", "gpu_percent", "available_memory_percent"):
            if maximums.get(resource) != ceiling:
                failures.append(f"{profile_id} {resource} must equal {ceiling}")
        if row.get("automatic_after_enrollment") is not True:
            failures.append(f"{profile_id} should automate only after enrollment")

    platforms = {row.get("platform"): row for row in profiles.get("platforms", [])}
    for platform in ("APPLE_APP_STORE", "GOOGLE_PLAY"):
        if platforms.get(platform, {}).get("local_crypto_mining") != "PROHIBITED":
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

    if assets.get("schema") != "8x8.asset-registry-draft.v2":
        failures.append("asset registry must use v2 schema")
    if assets.get("status") != "CANONICAL_DESIGN_RESOLVED_NOT_ISSUED":
        failures.append("canonical asset design must remain resolved but not issued")
    model = assets.get("model", {})
    if model.get("transferable_utility_token_count") != 8:
        failures.append("transferable utility-token count must be eight")
    if model.get("native_coin_count") != 1 or model.get("coin_symbol") != "8x8":
        failures.append("registry must contain one future 8x8 native coin")
    if model.get("non_transferable_credential_count") != 1 or model.get("credential_symbol") != "SRP":
        failures.append("registry must contain one non-transferable SRP credential")

    tokens = assets.get("transferable_utility_tokens", [])
    token_roles = {row.get("symbol"): row.get("canonical_role") for row in tokens}
    if token_roles != CANONICAL_TOKENS:
        failures.append("canonical transferable token symbols or roles changed")
    for row in tokens:
        if row.get("issuance_authorized") is not False:
            failures.append(f"{row.get('symbol')} issuance must remain unauthorized")
        if not row.get("utilities"):
            failures.append(f"{row.get('symbol')} requires explicit utilities")

    coin = assets.get("native_coin", {})
    if coin.get("symbol") != "8x8" or coin.get("native_chain") != "FUTURE_8X8_CHAIN":
        failures.append("8x8 coin must remain a future native-chain design")
    if coin.get("bitcoin_checkpoint_anchoring_target") is not True:
        failures.append("8x8 design must preserve Bitcoin checkpoint anchoring target")
    if coin.get("independent_multichain_supply_allowed") is not False:
        failures.append("independent uncoordinated multichain supply is prohibited")
    if coin.get("issuance_authorized") is not False:
        failures.append("8x8 coin issuance must remain unauthorized")

    credentials = assets.get("non_transferable_credentials", [])
    if len(credentials) != 1 or credentials[0].get("symbol") != "SRP":
        failures.append("SRP must be the single non-transferable credential identity")
    elif credentials[0].get("credential_type") != "NON_TRANSFERABLE_VERIFIABLE_CREDENTIAL":
        failures.append("SRP must remain a non-transferable verifiable credential")

    if srp.get("symbol") != "SRP" or srp.get("name") != "Seraphim Reputation Proof":
        failures.append("Seraphim credential identity changed")
    if srp.get("classification") != "NON_TRANSFERABLE_VERIFIABLE_CREDENTIAL":
        failures.append("SRP classification must remain non-transferable credential")
    for key in ("fungible", "transferable", "saleable", "swappable", "market_listing_allowed", "guaranteed_value"):
        if srp.get(key) is not False:
            failures.append(f"SRP {key} must remain false")
    for key in ("revocable", "expiry_required", "periodic_reverification_required"):
        if srp.get(key) is not True:
            failures.append(f"SRP {key} must remain true")
    if srp.get("issuance_authorized") is not False:
        failures.append("SRP issuance must remain unauthorized")

    authorizations = assets.get("global_authorizations", {})
    if not authorizations or any(value is not False for value in authorizations.values()):
        failures.append("all asset global authorizations must remain false")

    fees = assets.get("fee_targets", {})
    for key in ("coin_buy_bps", "coin_sell_bps", "nft_secondary_buy_sell_bps"):
        if fees.get(key) != 488:
            failures.append(f"{key} must remain 488 basis points")
    if fees.get("ordinary_protocol_transfer_bps") != 0:
        failures.append("ordinary protocol transfer fee target must remain zero")
    if fees.get("token_specific_fees_undecided") is not True:
        failures.append("token-specific fees must remain undecided")
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

    asset_doc = (root / "docs/CANONICAL_ASSET_SYSTEM.md").read_text(encoding="utf-8")
    for text in (
        "eight transferable utility-token identities",
        "Seraphim Reputation Proof",
        "non-transferable",
        "No independent uncoordinated supply",
    ):
        if text not in asset_doc:
            failures.append(f"canonical asset documentation missing: {text}")

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
