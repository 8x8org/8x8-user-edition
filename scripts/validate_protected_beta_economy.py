#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKET = ["8x8", "Tx8", "Ux8", "Fx8", "XM8", "0x8", "TM8", "Mx8", "Sx8"]
ROLES = {
    "OWNER_TREASURY", "OPERATING_TREASURY", "LIQUIDITY", "FEE_COLLECTION",
    "TOKEN_ADMIN", "ASSET_RESERVE", "AGENT_OPERATIONAL_TESTNET_ONLY", "USER_SELF_CUSTODY",
}
CAP = 8_888_888


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate() -> list[str]:
    failures: list[str] = []
    state = load("protected-beta/account-economy-state.json")
    policy = load("protected-beta/economy-policy.json")

    if state.get("inherits_fabric") != "8x8 OS 0.1.0 Stable / Living Omniversal Gate R4":
        failures.append("protected-beta release lineage drift")
    if state.get("market_asset_family") != MARKET:
        failures.append("market asset family must be exact nine-asset order")
    if state.get("non_market_credential", {}).get("symbol") != "SRP":
        failures.append("SRP credential must remain separate")
    if state.get("non_market_credential", {}).get("classification") != "NON_TRANSFERABLE_VERIFIABLE_CREDENTIAL":
        failures.append("SRP credential classification drift")

    requested = state.get("requested_market_asset_policy", {})
    for key in ("max_live_total_supply_each", "requested_initial_mint_each"):
        if requested.get(key) != CAP:
            failures.append(f"{key} must equal {CAP}")
    if requested.get("initial_destination_role") != "OWNER_TREASURY":
        failures.append("initial destination must remain OWNER_TREASURY")
    if requested.get("mintable_within_hard_cap") is not True or requested.get("burnable") is not True:
        failures.append("requested mint/burn policy drift")
    if requested.get("independent_supply_per_network") is not False:
        failures.append("independent network supply must remain prohibited")

    truth = state.get("truth", {})
    false_truth = [
        "production_admin_login", "production_account_database", "owner_wallet_verified",
        "mainnet_assets_deployed", "testnet_assets_deployed", "tokens_minted", "primary_sale_live",
    ]
    for key in false_truth:
        if truth.get(key) is not False:
            failures.append(f"unsupported live claim: {key}")
    if truth.get("verified_user_count") is not None:
        failures.append("user count must remain unverified until load/account evidence exists")
    if truth.get("whole_system_score") != "NOT_INFERRED":
        failures.append("whole system score cannot be inferred")

    wallet = state.get("wallet_model", {})
    if wallet.get("store_private_keys_in_app") is not False or wallet.get("store_seed_phrases_in_app") is not False:
        failures.append("wallet secret isolation drift")
    if set(wallet.get("roles", [])) != ROLES:
        failures.append("wallet-role surface drift")

    if state.get("first_chain_target") != "ETHEREUM_SEPOLIA" or state.get("first_chain_id") != 11155111:
        failures.append("first chain must remain Sepolia chain 11155111 for this protected-beta contract")

    p_supply = policy.get("canonical_supply_rule", {})
    if p_supply.get("max_live_total_supply_per_market_asset") != CAP:
        failures.append("economy policy cap drift")
    if p_supply.get("cap_is_immutable_after_deployment") is not True:
        failures.append("hard cap must be immutable after deployment")
    if p_supply.get("independent_multichain_supply") is not False:
        failures.append("multichain independent supply prohibited")
    if p_supply.get("multichain_model") != "ONE_CANONICAL_ORIGIN_SUPPLY_PLUS_BRIDGED_OR_WRAPPED_REPRESENTATIONS":
        failures.append("multichain supply conservation model drift")

    assets = policy.get("market_assets", [])
    if [a.get("symbol") for a in assets] != MARKET:
        failures.append("economy policy market asset order drift")
    for asset in assets:
        if asset.get("requested_cap") != CAP or asset.get("requested_initial_mint") != CAP:
            failures.append(f"{asset.get('symbol')} cap/initial-mint drift")
        if asset.get("initial_destination_role") != "OWNER_TREASURY":
            failures.append(f"{asset.get('symbol')} destination drift")

    pricing = policy.get("pricing_truth", {})
    if pricing.get("primary_sale_price_can_be_set_by_authorized_8x8_policy") is not True:
        failures.append("primary sale configuration contract drift")
    if pricing.get("secondary_market_price_can_be_directly_set_by_admin") is not False:
        failures.append("secondary market price cannot be represented as direct admin control")

    p_truth = policy.get("truth", {})
    for key in ("wallet_addresses_created_or_verified", "contracts_deployed", "tokens_minted", "sale_live", "users_onboarded"):
        if p_truth.get(key) is not False:
            failures.append(f"economy policy fabricated state: {key}")

    if not (ROOT / "protected-beta/admin/index.html").is_file():
        failures.append("protected admin shell missing")
    if not (ROOT / "protected-beta/account/index.html").is_file():
        failures.append("protected account shell missing")
    if not (ROOT / "supabase/migrations/0002_wallet_bindings_and_platform_roles.sql").is_file():
        failures.append("wallet-binding migration missing")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PROTECTED_BETA_ECONOMY_VALIDATION=PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
