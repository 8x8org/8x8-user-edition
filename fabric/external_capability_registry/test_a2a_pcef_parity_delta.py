from __future__ import annotations

import json
import unittest
from pathlib import Path

from fabric.external_capability_registry.benchmark import materialize_benchmark

ROOT = Path(__file__).resolve().parent
BEFORE = ROOT / "benchmark_2026-08-11.json"
DELTA = ROOT / "a2a_pcef_parity_delta_2026-08-11.json"
EXPECTED_DELTA = {"D1": 0, "D2": 1, "D3": 0, "D4": 0, "D5": 0, "D6": 1, "D7": 0, "D8": 0}


def baseline(data: dict) -> dict:
    matches = [project for project in data["projects"] if project.get("kind") == "baseline"]
    if len(matches) != 1:
        raise AssertionError("benchmark must contain exactly one baseline")
    return matches[0]


class A2APCEFParityDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.before = json.loads(BEFORE.read_text(encoding="utf-8"))
        cls.after = materialize_benchmark()
        cls.delta = json.loads(DELTA.read_text(encoding="utf-8"))

    def test_exact_score_and_component_delta(self) -> None:
        before = baseline(self.before)
        after = baseline(self.after)
        observed = {key: after["components"][key] - before["components"][key] for key in EXPECTED_DELTA}
        recorded = {key: item["delta"] for key, item in self.delta["component_delta"].items()}
        self.assertEqual((before["score"], after["score"]), (78, 80))
        self.assertEqual((self.delta["base_score"], self.delta["next_score"], self.delta["score_change"]), (78, 80, 2))
        self.assertEqual(observed, EXPECTED_DELTA)
        self.assertEqual(recorded, EXPECTED_DELTA)
        self.assertEqual(sum(after["components"].values()), 80)

    def test_evidence_and_measurement_are_bounded(self) -> None:
        evidence = self.delta["private_core_evidence"]
        self.assertEqual(
            (evidence["pull_request"], evidence["validated_head"], evidence["merge"], evidence["workflow_run_id"]),
            (131, "de2d6e65d0e3e9869668f84d350503c5dc6b32d1", "c7213cd2ef360087b0eb5f816200281ae12153a4", 31458732764),
        )
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        self.assertEqual({gate["dimension"] for gate in self.delta["closed_bounded_gates"]}, {"D2", "D6"})
        measured = self.delta["measured_canary"]
        self.assertEqual((measured["processes"], measured["router_receipts"], measured["specialist_receipts"]), (2, 8, 8))
        self.assertGreater(measured["hosted_runner_total_ms"], 0)
        self.assertEqual(measured["timing_scope"], "SINGLE_CI_CANARY_NOT_PRODUCTION_THROUGHPUT")

    def test_nonclaims_and_order_survive_materialization(self) -> None:
        self.assertTrue(all(value is False for value in self.delta["truth_boundary"].values()))
        self.assertFalse(self.after["score_is_universal_rank"])
        self.assertFalse(self.after["global_100_claim_allowed"])
        status = self.after["frontier"]["current_status"]
        for marker in (
            "A2A_HTTP_JSON_TWO_PROCESS_SELF_INTEROP_VALIDATED",
            "INDEPENDENT_THIRD_PARTY_A2A_INTEROP_NOT_YET_PROVEN",
            "AUTHENTICATED_PRODUCTION_A2A_EDGE_NOT_YET_IMPLEMENTED",
            "NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN",
            "PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED",
        ):
            self.assertIn(marker, status)
        projects = self.after["projects"]
        self.assertEqual([project["score"] for project in projects], sorted((project["score"] for project in projects), reverse=True))
        names = [project["project"] for project in projects]
        self.assertGreater(names.index("8x8 One Fabric"), names.index("Microsoft Agent Framework"))
        self.assertLess(names.index("8x8 One Fabric"), names.index("CrewAI"))


if __name__ == "__main__":
    unittest.main()
