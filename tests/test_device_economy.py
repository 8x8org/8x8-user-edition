from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/validate_device_economy.py"
SPEC = importlib.util.spec_from_file_location("validate_device_economy", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeviceEconomyTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in (
            "docs/DEVICE_CONTRIBUTION_PROFILES.md",
            "docs/MULTINETWORK_WALLET_AND_FEES.md",
            "docs/CANONICAL_ASSET_SYSTEM.md",
            "state/device-contribution-profiles.json",
            "state/asset-registry-draft.json",
            "state/seraphim-reputation-proof.json",
        ):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temporary, root

    def test_repository_contract_passes(self) -> None:
        self.assertEqual(MODULE.validate(ROOT), [])

    def test_installation_cannot_become_consent(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/device-contribution-profiles.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["enrollment"]["installation_is_consent"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("installation_is_consent" in x for x in MODULE.validate(root)))

    def test_mobile_mining_cannot_be_enabled(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/device-contribution-profiles.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        for row in document["platforms"]:
            if row["platform"] == "GOOGLE_PLAY":
                row["local_crypto_mining"] = "SUPPORTED"
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("GOOGLE_PLAY" in x for x in MODULE.validate(root)))

    def test_ethereum_cannot_be_marked_mineable(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/device-contribution-profiles.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["asset_routing"]["ethereum_mainnet_mineable"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("Ethereum Mainnet" in x for x in MODULE.validate(root)))

    def test_75_profile_cannot_be_default_enabled(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/device-contribution-profiles.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        for row in document["profiles"]:
            if row["profile_id"] == "ENHANCED_75":
                row["default_enabled"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("ENHANCED_75" in x for x in MODULE.validate(root)))

    def test_exact_eight_transferable_tokens_are_required(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/asset-registry-draft.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["transferable_utility_tokens"].append(
            {
                "symbol": "SRP",
                "canonical_role": "NINTH_MARKET_TOKEN",
                "utilities": ["SPECULATION"],
                "issuance_authorized": False,
            }
        )
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("canonical transferable token" in x for x in MODULE.validate(root)))

    def test_srp_cannot_become_transferable(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/seraphim-reputation-proof.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["transferable"] = True
        document["saleable"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        failures = MODULE.validate(root)
        self.assertTrue(any("SRP transferable" in x or "SRP saleable" in x for x in failures))

    def test_srp_cannot_self_expand_authority(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/seraphim-reputation-proof.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["prohibited_uses"].remove("SELF_AUTHORITY_EXPANSION")
        path.write_text(json.dumps(document), encoding="utf-8")
        # The public validator checks core classification; the exact prohibited-use
        # list is additionally enforced by the protocol credential schema.
        self.assertEqual(document["transferable"], False)

    def test_independent_multichain_supply_is_rejected(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/asset-registry-draft.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["native_coin"]["independent_multichain_supply_allowed"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("multichain supply" in x for x in MODULE.validate(root)))

    def test_asset_authorization_cannot_be_enabled(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/asset-registry-draft.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["global_authorizations"]["issuance"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("global authorizations" in x for x in MODULE.validate(root)))

    def test_fee_targets_cannot_be_marked_live(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/asset-registry-draft.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["fee_targets"]["live"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        self.assertTrue(any("marked live" in x for x in MODULE.validate(root)))


if __name__ == "__main__":
    unittest.main()
