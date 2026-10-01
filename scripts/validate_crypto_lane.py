#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOKEN_ROLES = {
    "Tx8": "TRANSACTION_AND_MARKETPLACE",
    "Ux8": "USER_UTILITY_AND_ACCESS",
    "Fx8": "FABRIC_OPERATIONS",
    "XM8": "EXECUTION_AND_COMPUTE",
    "0x8": "PROTOCOL_AND_INNOVATION",
    "TM8": "COMMUNITY_AND_IDENTITY",
    "Mx8": "MINING_AND_RESOURCE_CONTRIBUTION",
    "Sx8": "STORAGE_AND_SERVICES",
}
TOKENS = list(TOKEN_ROLES)
REQUIRED_NETWORKS = {
    "Ethereum Sepolia",
    "BNB Smart Chain Testnet",
    "Solana Devnet",
    "TON Testnet",
    "Bitcoin Testnet4/Signet research",
    "Pi Testnet",
}
REQUIRED_NETWORK_FIELDS = {
    "network", "chain_family", "chain_id", "source", "compiler_lock", "dependency_lock",
    "bytecode_sha256", "supply_model", "decimals", "authorities", "upgradeability",
    "bridge_assumptions", "gas_model", "signer_requirements", "verification_state",
    "testnet_receipts", "rollback", "unresolved_decisions",
}
ALLOWED_SIGNER_REQUIREMENTS = {
    "OWNER_REQUIRED_FOR_ANY_BROADCAST",
    "OWNER_REQUIRED_FOR_ANY_TRANSACTION",
    "OWNER_REQUIRED_FOR_ANY_BROADCAST_OR_ACCOUNT_ACCESS",
}
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
SUPPLY_INVARIANTS = {
    "single_canonical_supply_policy_required",
    "independent_chain_supply_prohibited",
    "bridge_supply_conservation_required",
    "wrapped_supply_must_be_backed_or_burn_mint_accounted",
    "chain_representation_registry_required",
}
OWNER_REQUIRED = {
    "final supply and decimals",
    "allocation and vesting",
    "origin-chain selection",
    "deployment signer provisioning",
    "mainnet deployment",
    "funded testnet broadcast",
    "bridge activation",
    "liquidity creation",
    "token sale or listing",
    "public financial promotion",
}
REQUIRED_GLOBAL_INVARIANTS = {
    "REJECT_MAINNET_CHAIN_IDS_AND_PRODUCTION_NETWORKS",
    "NO_SECRET_OR_WALLET_ACCESS",
    "NO_BROADCAST_WITHOUT_OWNER_SIGNER_AND_FUNDS",
    "SUPPLY_CONSERVATION_ACROSS_REPRESENTATIONS",
    "AUTHORITY_REVOCATION_MUST_BE_IRREVERSIBLE_OR_EXPLICITLY_GOVERNED",
    "DIGEST_BOUND_RECEIPTS_REQUIRED_FOR_ANY_VERIFIED_TESTNET_MILESTONE",
    "ROLLBACK_OR_NO_DEPLOYMENT_STATE_REQUIRED_PER_NETWORK",
}


def load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    assets = load(root, "state/crypto-asset-registry-0.0.1.json")
    chains = load(root, "state/crypto-chain-readiness-0.0.1.json")

    if assets.get("schema") != "8x8.crypto-asset-registry.v1":
        failures.append("asset registry schema drift")
    if assets.get("product_version") != "0.0.1 Beta":
        failures.append("asset registry product version drift")
    if assets.get("status") != "DESIGN_RESOLVED_NOT_ISSUED":
        failures.append("asset registry must remain not issued")
    if assets.get("market_asset_count") != 9:
        failures.append("market asset count must be exactly nine")
    if assets.get("transferable_utility_token_count") != 8 or assets.get("native_coin_count") != 1:
        failures.append("asset composition must remain eight utility tokens plus one native coin")
    if assets.get("credential_count_excluded_from_market_assets") != 1:
        failures.append("exactly one non-market credential must remain excluded")

    rows = assets.get("transferable_utility_tokens", [])
    if [row.get("symbol") for row in rows] != TOKENS:
        failures.append("canonical token order or identity drift")
    for row in rows:
        symbol = row.get("symbol")
        if TOKEN_ROLES.get(symbol) != row.get("role"):
            failures.append(f"{symbol} role drift")
        if row.get("issuance_authorized") is not False:
            failures.append(f"{symbol} issuance must remain unauthorized")
        if row.get("final_supply") is not None or row.get("decimals") is not None:
            failures.append(f"{symbol} final supply/decimals must remain unresolved")

    coin = assets.get("native_coin", {})
    if coin.get("symbol") != "8x8" or coin.get("role") != "SETTLEMENT_AND_NETWORK_SECURITY":
        failures.append("native 8x8 coin identity/role drift")
    if coin.get("native_chain") != "FUTURE_8X8_CHAIN":
        failures.append("native 8x8 chain identity drift")
    if coin.get("issuance_authorized") is not False:
        failures.append("native 8x8 issuance must remain unauthorized")
    if coin.get("final_supply") is not None or coin.get("decimals") is not None:
        failures.append("native 8x8 coin final supply/decimals must remain unresolved")
    if coin.get("independent_multichain_supply_allowed") is not False:
        failures.append("independent multichain supply must remain prohibited")

    credential = assets.get("credential", {})
    if credential.get("symbol") != "SRP" or credential.get("name") != "Seraphim Reputation Proof":
        failures.append("SRP credential identity drift")
    if credential.get("classification") != "NON_TRANSFERABLE_VERIFIABLE_CREDENTIAL":
        failures.append("SRP classification drift")
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
    if set(supply) != SUPPLY_INVARIANTS:
        failures.append("supply invariant surface changed")
    for key in SUPPLY_INVARIANTS:
        if supply.get(key) is not True:
            failures.append(f"missing supply invariant: {key}")

    owner_required = assets.get("owner_required", [])
    if not isinstance(owner_required, list) or set(owner_required) != OWNER_REQUIRED or len(owner_required) != len(OWNER_REQUIRED):
        failures.append("OWNER_REQUIRED decision surface drift")

    if chains.get("schema") != "8x8.crypto-chain-readiness.v1":
        failures.append("chain readiness schema drift")
    if chains.get("product_version") != "0.0.1 Beta" or chains.get("mode") != "OWNER_AWAY_TESTNET_ONLY":
        failures.append("chain readiness mode/version drift")
    networks = chains.get("networks", [])
    names = [row.get("network") for row in networks]
    if len(networks) != len(REQUIRED_NETWORKS) or len(names) != len(set(names)) or set(names) != REQUIRED_NETWORKS:
        failures.append("chain readiness networks must be exactly six unique canonical networks")
    for row in networks:
        network = row.get("network")
        if set(row) != REQUIRED_NETWORK_FIELDS:
            failures.append(f"{network} readiness field surface drift")
        if row.get("verification_state") not in {"DESIGN_ONLY", "RESEARCH_ONLY"}:
            failures.append(f"{network} cannot claim deployed verification")
        if row.get("testnet_receipts") != []:
            failures.append(f"{network} cannot contain unverified testnet receipts")
        signer = row.get("signer_requirements")
        if not isinstance(signer, str) or signer not in ALLOWED_SIGNER_REQUIREMENTS:
            failures.append(f"{network} signer gate must use an exact OWNER_REQUIRED policy string")
        if row.get("rollback") not in {"NO_DEPLOYMENT_EXISTS", "NO_TRANSACTION_OR_ASSET_EXISTS"}:
            failures.append(f"{network} rollback state must prove no deployment")
        if row.get("bytecode_sha256") is not None:
            failures.append(f"{network} cannot claim bytecode digest before a selected implementation")
        if row.get("compiler_lock") is not None or row.get("dependency_lock") is not None:
            failures.append(f"{network} cannot claim compiler/dependency locks before a selected implementation")
        if not isinstance(row.get("source"), str) or not row.get("source", "").startswith("NO_"):
            failures.append(f"{network} source must remain explicitly unselected")
        if not isinstance(row.get("unresolved_decisions"), list) or not row.get("unresolved_decisions"):
            failures.append(f"{network} unresolved decisions must remain explicit")

    for row in networks:
        if row.get("chain_family") != "EVM":
            continue
        if row.get("network") == "Ethereum Sepolia" and row.get("chain_id") != 11155111:
            failures.append("Sepolia chain-id drift")
        elif row.get("network") == "BNB Smart Chain Testnet" and row.get("chain_id") != 97:
            failures.append("BSC Testnet chain-id drift")
        elif row.get("network") not in {"Ethereum Sepolia", "BNB Smart Chain Testnet"}:
            failures.append("unexpected EVM network")

    invariants = chains.get("global_invariants", [])
    if not isinstance(invariants, list) or set(invariants) != REQUIRED_GLOBAL_INVARIANTS or len(invariants) != len(REQUIRED_GLOBAL_INVARIANTS):
        failures.append("global crypto invariant surface drift")
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
