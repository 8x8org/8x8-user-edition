from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BEFORE = ROOT / "benchmark_2026-08-11.json"
AFTER = ROOT / "benchmark_2026-08-11_v2.json"
DELTA = ROOT / "a2a_pcef_parity_delta_2026-08-11.json"


class A2APCEFParityDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.before = json.loads(BEFORE.read_text(encoding="utf-8"))
        cls.after = json.loads(AFTER.read_text(encoding="utf-8"))
        cls.delta = json.loads(DELTA.read_text(encoding="utf-8"))

    @staticmethod
    def baseline(data: dict) -> dict:
        matches = [project for project in data["projects"] if project.get("kind") == "baseline"]
        if len(matches) != 1:
            raise AssertionError("benchmark must contain exactly one baseline")
        return matches[0]

    def test_score_moves_exactly_78_to_80(self) -> None:
        before = self.baseline(self.before)
        after = self.baseline(self.after)
        self.assertEqual(before["score"], 78)
        self.assertEqual(after["score"], 80)
        self.assertEqual(self.delta["base_score"], 78)
        self.assertEqual(self.delta["next_score"], 80)
        self.assertEqual(self.delta["score_change"], 2)
        self.assertEqual(sum(after["components"].values()), 80)

    def test_only_d2_and_d6_gain_one_point(self) -> None:
        before = self.baseline(self.before)["components"]
        after = self.baseline(self.after)["components"]
        expected = {"D1": 0, "D2": 1, "D3": 0, "D4": 0, "D5": 0, "D6": 1, "D7": 0, "D8": 0}
        observed = {key: after[key] - before[key] for key in sorted(before)}
        self.assertEqual(observed, expected)
        recorded = {key: item["delta"] for key, item in self.delta["component_delta"].items()}
        self.assertEqual(recorded, expected)
        for key, item in self.delta["component_delta"].items():
            self.assertEqual(item["before"], before[key])
            self.assertEqual(item["after"], after[key])

    def test_private_acceptance_evidence_is_exact_and_bounded(self) -> None:
        evidence = self.delta["private_core_evidence"]
        self.assertEqual(evidence["repository"], "horbolsi/8x8")
        self.assertEqual(evidence["pull_request"], 131)
        self.assertEqual(evidence["validated_head"], "de2d6e65d0e3e9869668f84d350503c5dc6b32d1")
        self.assertEqual(evidence["merge"], "c7213cd2ef360087b0eb5f816200281ae12153a4")
        self.assertEqual(evidence["workflow_run_id"], 31458732764)
        self.assertEqual(evidence["exact_head_status"], "PASS")
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        gates = {gate["dimension"] for gate in self.delta["closed_bounded_gates"]}
        self.assertEqual(gates, {"D2", "D6"})

    def test_canary_measurement_is_not_promoted_to_throughput(self) -> None:
        measured = self.delta["measured_canary"]
        self.assertEqual(measured["processes"], 2)
        self.assertEqual(measured["router_receipts"], 8)
        self.assertEqual(measured["specialist_receipts"], 8)
        self.assertGreater(measured["hosted_runner_total_ms"], 0)
        self.assertEqual(measured["timing_scope"], "SINGLE_CI_CANARY_NOT_PRODUCTION_THROUGHPUT")

    def test_interop_and_global_nonclaims_remain_false(self) -> None:
        self.assertFalse(self.after["score_is_universal_rank"])
        self.assertFalse(self.after["global_100_claim_allowed"])
        self.assertFalse(self.delta["score_is_universal_rank"])
        self.assertFalse(self.delta["global_100_claim_allowed"])
        truth = self.delta["truth_boundary"]
        for key, value in truth.items():
            self.assertIs(value, False, f"{key} must remain false")
        frontier = self.after["frontier"]["current_status"]
        self.assertIn("A2A_HTTP_JSON_TWO_PROCESS_SELF_INTEROP_VALIDATED", frontier)
        self.assertIn("INDEPENDENT_THIRD_PARTY_A2A_INTEROP_NOT_YET_PROVEN", frontier)
        self.assertIn("AUTHENTICATED_PRODUCTION_A2A_EDGE_NOT_YET_IMPLEMENTED", frontier)
        self.assertIn("NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN", frontier)
        self.assertIn("PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED", frontier)

    def test_benchmark_order_tracks_new_score(self) -> None:
        projects = self.after["projects"]
        scores = [project["score"] for project in projects]
        self.assertEqual(scores, sorted(scores, reverse=True))
        names = [project["project"] for project in projects]
        self.assertGreater(names.index("8x8 One Fabric"), names.index("Microsoft Agent Framework"))
        self.assertLess(names.index("8x8 One Fabric"), names.index("CrewAI"))
        self.assertLess(names.index("8x8 One Fabric"), names.index("n8n"))


if __name__ == "__main__":
    unittest.main()
