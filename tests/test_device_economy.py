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
            "state/device-contribution-profiles.json",
            "state/asset-registry-draft.json",
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

    def test_asset_conflict_cannot_be_hidden(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/asset-registry-draft.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["observed_utility_symbols"].pop()
        document["observed_utility_symbol_count"] = 8
        document["status"] = "READY"
        path.write_text(json.dumps(document), encoding="utf-8")
        failures = MODULE.validate(root)
        self.assertTrue(any("count conflict" in x or "nine symbols" in x for x in failures))

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
