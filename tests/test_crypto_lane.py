from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_crypto_lane import validate

ROOT = Path(__file__).resolve().parents[1]


class CryptoLaneTests(unittest.TestCase):
    def test_current_contracts_pass(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def _tampered_root(self, asset_mutator=None, chain_mutator=None) -> Path:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "state").mkdir()
        assets = json.loads((ROOT / "state/crypto-asset-registry-0.0.1.json").read_text())
        chains = json.loads((ROOT / "state/crypto-chain-readiness-0.0.1.json").read_text())
        if asset_mutator:
            asset_mutator(assets)
        if chain_mutator:
            chain_mutator(chains)
        (tmp / "state/crypto-asset-registry-0.0.1.json").write_text(json.dumps(assets), encoding="utf-8")
        (tmp / "state/crypto-chain-readiness-0.0.1.json").write_text(json.dumps(chains), encoding="utf-8")
        return tmp

    def test_rejects_token_issuance_authority(self) -> None:
        root = self._tampered_root(lambda a: a["transferable_utility_tokens"][0].update({"issuance_authorized": True}))
        self.assertTrue(validate(root))

    def test_rejects_mainnet_authorization(self) -> None:
        root = self._tampered_root(lambda a: a["global_authorizations"].update({"mainnet_deployment": True}))
        self.assertTrue(validate(root))

    def test_rejects_independent_multichain_supply(self) -> None:
        root = self._tampered_root(lambda a: a["native_coin"].update({"independent_multichain_supply_allowed": True}))
        self.assertTrue(validate(root))

    def test_rejects_fake_testnet_receipt(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"testnet_receipts": [{"sha256": "0" * 64, "status": "PASS"}]}))
        self.assertTrue(validate(root))

    def test_rejects_mainnet_like_verification_claim(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"verification_state": "DEPLOYED_VERIFIED"}))
        self.assertTrue(validate(root))

    def test_rejects_chain_id_drift(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"chain_id": 1}))
        self.assertTrue(validate(root))

    def test_rejects_resolved_supply_without_owner_gate(self) -> None:
        root = self._tampered_root(lambda a: a["transferable_utility_tokens"][0].update({"final_supply": 1000000, "decimals": 18}))
        self.assertTrue(validate(root))

    def test_rejects_native_coin_supply_or_decimals_resolution(self) -> None:
        root = self._tampered_root(lambda a: a["native_coin"].update({"final_supply": 888000000, "decimals": 8}))
        self.assertTrue(validate(root))

    def test_rejects_duplicate_network_masking_chain_id_drift(self) -> None:
        def mutate(c):
            duplicate = dict(c["networks"][0])
            duplicate["chain_id"] = 1
            c["networks"].append(duplicate)
        self.assertTrue(validate(self._tampered_root(chain_mutator=mutate)))

    def test_rejects_signer_gate_substring_bypass(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"signer_requirements": "NOT_OWNER_REQUIRED"}))
        self.assertTrue(validate(root))

    def test_rejects_unknown_signer_policy_even_with_owner_required_substring(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"signer_requirements": "OWNER_REQUIRED_BUT_AUTOMATION_MAY_BROADCAST"}))
        self.assertTrue(validate(root))

    def test_rejects_non_string_signer_policy_without_exception(self) -> None:
        for malformed in (["OWNER_REQUIRED_FOR_ANY_BROADCAST"], {"policy": "OWNER_REQUIRED_FOR_ANY_BROADCAST"}):
            with self.subTest(malformed=malformed):
                root = self._tampered_root(chain_mutator=lambda c, value=malformed: c["networks"][0].update({"signer_requirements": value}))
                failures = validate(root)
                self.assertTrue(any("signer gate" in failure for failure in failures))

    def test_rejects_token_role_drift(self) -> None:
        root = self._tampered_root(lambda a: a["transferable_utility_tokens"][0].update({"role": "TREASURY_CONTROL"}))
        self.assertTrue(any("role drift" in f for f in validate(root)))

    def test_rejects_srp_classification_drift(self) -> None:
        root = self._tampered_root(lambda a: a["credential"].update({"classification": "TRANSFERABLE_TOKEN"}))
        self.assertTrue(any("SRP classification" in f for f in validate(root)))

    def test_rejects_native_chain_identity_drift(self) -> None:
        root = self._tampered_root(lambda a: a["native_coin"].update({"native_chain": "ETHEREUM_MAINNET"}))
        self.assertTrue(any("chain identity" in f for f in validate(root)))

    def test_rejects_owner_required_gate_removal(self) -> None:
        root = self._tampered_root(lambda a: a["owner_required"].remove("mainnet deployment"))
        self.assertTrue(any("OWNER_REQUIRED" in f for f in validate(root)))

    def test_rejects_unselected_source_claiming_bytecode(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"bytecode_sha256": "1" * 64}))
        self.assertTrue(any("bytecode digest" in f for f in validate(root)))

    def test_rejects_unselected_source_claiming_toolchain_locks(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"compiler_lock": "solc-0.8.30", "dependency_lock": "fake-lock"}))
        self.assertTrue(any("compiler/dependency" in f for f in validate(root)))

    def test_rejects_selected_source_without_promotion_contract(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"source": "contracts/Token.sol"}))
        self.assertTrue(any("source must remain explicitly unselected" in f for f in validate(root)))

    def test_rejects_global_invariant_removal(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["global_invariants"].remove("NO_SECRET_OR_WALLET_ACCESS"))
        self.assertTrue(any("global crypto invariant" in f for f in validate(root)))

    def test_rejects_readiness_field_surface_expansion(self) -> None:
        root = self._tampered_root(chain_mutator=lambda c: c["networks"][0].update({"mainnet_rpc": "https://example.invalid"}))
        self.assertTrue(any("readiness field surface" in f for f in validate(root)))


if __name__ == "__main__":
    unittest.main()
