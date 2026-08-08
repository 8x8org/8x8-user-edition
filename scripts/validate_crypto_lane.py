#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOKENS = ["Tx8", "Ux8", "Fx8", "XM8", "0x8", "TM8", "Mx8", "Sx8"]
FORBIDDEN_AUTH = {
    "mainnet_deployment",
    "testnet_broadcast_requiring_signer_or_funds",
    "token_issuance",
    "minting_for_value",
    "bridge_activation",
    "liquidity_creation",
    "token_sale",
    "listing",
    "treasury_movement",
    "wallet_custody",
    "production_rpc_control",
}


def load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    assets = load(root, "state/crypto-asset-registry-0.0.1.json")
    chains = load(root, "state/crypto-chain-readiness-0.0.1.json")

    if assets.get("product_version") != "0.0.1 Beta":
        failures.append("asset registry product version drift")
    if assets.get("status") != "DESIGN_RESOLVED_NOT_ISSUED":
        failures.append("asset registry must remain not issued")
    if assets.get("market_asset_count") != 9:
        failures.append("market asset count must be exactly nine")
    if assets.get("transferable_utility_token_count") != 8 or assets.get("native_coin_count") != 1:
        failures.append("asset composition must remain eight utility tokens plus one native coin")

    rows = assets.get("transferable_utility_tokens", [])
    if [row.get("symbol") for row in rows] != TOKENS:
        failures.append("canonical token order or identity drift")
    for row in rows:
        if row.get("issuance_authorized") is not False:
            failures.append(f"{row.get('symbol')} issuance must remain unauthorized")
        if row.get("final_supply") is not None or row.get("decimals") is not None:
            failures.append(f"{row.get('symbol')} final supply/decimals must remain unresolved")

    coin = assets.get("native_coin", {})
    if coin.get("symbol") != "8x8" or coin.get("issuance_authorized") is not False:
        failures.append("native 8x8 coin identity/authorization drift")
    if coin.get("independent_multichain_supply_allowed") is not False:
        failures.append("independent multichain supply must remain prohibited")

    credential = assets.get("credential", {})
    for key in ("fungible", "transferable", "saleable", "swappable", "issuance_authorized"):
        if credential.get(key) is not False:
            failures.append(f"SRP {key} must remain false")
    if credential.get("revocable") is not True:
        failures.append("SRP must remain revocable")

    auth = assets.get("global_authorizations", {})
    if set(auth) != FORBIDDEN_AUTH:
        failures.append("global authorization surface changed")
    for key in FORBIDDEN_AUTH:
        if auth.get(key) is not False:
            failures.append(f"{key} must remain false")

    supply = assets.get("supply_invariants", {})
    for key in (
        "single_canonical_supply_policy_required",
        "independent_chain_supply_prohibited",
        "bridge_supply_conservation_required",
        "wrapped_supply_must_be_backed_or_burn_mint_accounted",
        "chain_representation_registry_required",
    ):
        if supply.get(key) is not True:
            failures.append(f"missing supply invariant: {key}")

    if chains.get("product_version") != "0.0.1 Beta" or chains.get("mode") != "OWNER_AWAY_TESTNET_ONLY":
        failures.append("chain readiness mode/version drift")
    networks = chains.get("networks", [])
    names = {row.get("network") for row in networks}
    required = {"Ethereum Sepolia", "BNB Smart Chain Testnet", "Solana Devnet", "TON Testnet", "Bitcoin Testnet4/Signet research", "Pi Testnet"}
    if names != required:
        failures.append("chain readiness network set drift")
    for row in networks:
        if row.get("verification_state") not in {"DESIGN_ONLY", "RESEARCH_ONLY"}:
            failures.append(f"{row.get('network')} cannot claim deployed verification")
        if row.get("testnet_receipts") != []:
            failures.append(f"{row.get('network')} cannot contain unverified testnet receipts")
        if "OWNER_REQUIRED" not in str(row.get("signer_requirements")):
            failures.append(f"{row.get('network')} signer gate must remain OWNER_REQUIRED")
        if row.get("rollback") not in {"NO_DEPLOYMENT_EXISTS", "NO_TRANSACTION_OR_ASSET_EXISTS"}:
            failures.append(f"{row.get('network')} rollback state must prove no deployment")

    evm = {row["network"]: row for row in networks if row.get("chain_family") == "EVM"}
    if evm.get("Ethereum Sepolia", {}).get("chain_id") != 11155111:
        failures.append("Sepolia chain-id drift")
    if evm.get("BNB Smart Chain Testnet", {}).get("chain_id") != 97:
        failures.append("BSC Testnet chain-id drift")

    invariants = set(chains.get("global_invariants", []))
    for invariant in (
        "REJECT_MAINNET_CHAIN_IDS_AND_PRODUCTION_NETWORKS",
        "NO_SECRET_OR_WALLET_ACCESS",
        "SUPPLY_CONSERVATION_ACROSS_REPRESENTATIONS",
        "DIGEST_BOUND_RECEIPTS_REQUIRED_FOR_ANY_VERIFIED_TESTNET_MILESTONE",
    ):
        if invariant not in invariants:
            failures.append(f"missing global invariant: {invariant}")
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = validate(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("CRYPTO_LANE_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
