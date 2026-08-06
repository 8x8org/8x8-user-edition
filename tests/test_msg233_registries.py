"""Tests for MSG233 public registry artifacts."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class RegistryFilesExistTest(unittest.TestCase):
    REQUIRED = [
        "AGENT_BODY_AND_CAPABILITY_REGISTRY.json",
        "MODEL_PROVIDER_ROUTING_REGISTRY.json",
        "CONNECTOR_AND_SOCIAL_ADAPTER_REGISTRY.json",
        "TESTNET_ECONOMY_REGISTRY.json",
        "STUDIO_LANGUAGE_AND_MEDIA_REGISTRY.json",
        "PUBLIC_RELEASE_TRAIN.json",
        "100_PERCENT_CONVERGENCE_SCORECARD.json",
    ]

    def test_registry_files_exist_and_parse(self) -> None:
        for name in self.REQUIRED:
            path = REGISTRY / name
            self.assertTrue(path.is_file(), f"Missing registry file: {name}")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data.get("schema_version"), "1.0.0", f"{name}: schema_version must be 1.0.0")
            self.assertEqual(data.get("document_class", "").startswith("PUBLIC"), True,
                             f"{name}: document_class must start with PUBLIC")
            self.assertEqual(data.get("truth_state"), "PUBLIC_SOURCE_VALIDATED",
                             f"{name}: truth_state must be PUBLIC_SOURCE_VALIDATED")


class PolicyAndRunbookFilesTest(unittest.TestCase):
    def test_community_operations_policy_exists(self) -> None:
        path = ROOT / "COMMUNITY_OPERATIONS_POLICY.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("owner gate", text.lower())
        self.assertIn("receipt", text.lower())

    def test_continuous_operations_runbook_exists(self) -> None:
        path = ROOT / "CONTINUOUS_OPERATIONS_RUNBOOK.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("rollback", text.lower())

    def test_latest_msg233_receipt_exists(self) -> None:
        path = ROOT / "LATEST_MSG233_RECEIPT.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("MSG233", text)
        self.assertIn("NOT_INFERRED", text)


class AgentRegistryContentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((REGISTRY / "AGENT_BODY_AND_CAPABILITY_REGISTRY.json").read_text(encoding="utf-8"))

    def test_archetypes_present(self) -> None:
        archetypes = {a["id"] for a in self.data["agent_archetypes"]}
        for expected_id in ["archetype:FlashTM8", "archetype:Coordinator", "archetype:SOMA"]:
            self.assertIn(expected_id, archetypes)

    def test_no_private_runtime_connected(self) -> None:
        for agent in self.data["agent_archetypes"]:
            self.assertFalse(agent.get("private_runtime_connected"),
                             f"{agent['id']} must not claim private_runtime_connected")


class ConnectorRegistryContentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((REGISTRY / "CONNECTOR_AND_SOCIAL_ADAPTER_REGISTRY.json").read_text(encoding="utf-8"))

    def test_disabled_adapters_are_disabled(self) -> None:
        disabled_ids = {"x", "facebook", "tiktok"}
        for adapter in self.data["adapters"]:
            if adapter["id"] in disabled_ids:
                self.assertEqual(adapter["status"], "DISABLED",
                                 f"Adapter {adapter['id']} must remain DISABLED until owner creates developer app")

    def test_all_adapters_have_disable_switch(self) -> None:
        for adapter in self.data["adapters"]:
            self.assertTrue(adapter.get("disable_switch"),
                            f"Adapter {adapter['id']} must have a disable_switch")


class TestnetRegistryContentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((REGISTRY / "TESTNET_ECONOMY_REGISTRY.json").read_text(encoding="utf-8"))

    def test_mainnet_not_authorized(self) -> None:
        self.assertFalse(self.data.get("mainnet_authorized"))

    def test_no_financial_promises(self) -> None:
        self.assertFalse(self.data.get("financial_promises"))
        self.assertFalse(self.data.get("automated_trading"))
        self.assertFalse(self.data.get("staking_or_liquidity"))

    def test_testnet_label_present(self) -> None:
        self.assertIn("TESTNET", self.data.get("testnet_label", ""))


class ConvergenceScorecardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((REGISTRY / "100_PERCENT_CONVERGENCE_SCORECARD.json").read_text(encoding="utf-8"))

    def test_whole_system_score_not_inferred(self) -> None:
        self.assertEqual(self.data.get("whole_system_score"), "NOT_INFERRED")

    def test_all_lanes_present(self) -> None:
        lane_ids = {lane["lane"] for lane in self.data["public_user_edition_lanes"]}
        for expected in ["A_runtime_stability", "D_public_release_train", "I_testnet_economy"]:
            self.assertIn(expected, lane_ids)


if __name__ == "__main__":
    unittest.main()
