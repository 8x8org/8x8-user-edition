from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BEFORE = ROOT / "benchmark_2026-08-10.json"
AFTER = ROOT / "benchmark_2026-08-11.json"
DELTA = ROOT / "spca_parity_delta_2026-08-11.json"


class SPCAParityDeltaTests(unittest.TestCase):
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

    def test_score_moves_exactly_75_to_78(self) -> None:
        before = self.baseline(self.before)
        after = self.baseline(self.after)
        self.assertEqual(before["score"], 75)
        self.assertEqual(after["score"], 78)
        self.assertEqual(self.delta["base_score"], 75)
        self.assertEqual(self.delta["next_score"], 78)
        self.assertEqual(self.delta["score_change"], 3)
        self.assertEqual(sum(after["components"].values()), 78)

    def test_only_d1_d4_d8_gain_one_point(self) -> None:
        before = self.baseline(self.before)["components"]
        after = self.baseline(self.after)["components"]
        expected_delta = {"D1": 1, "D2": 0, "D3": 0, "D4": 1, "D5": 0, "D6": 0, "D7": 0, "D8": 1}
        observed_delta = {key: after[key] - before[key] for key in sorted(before)}
        self.assertEqual(observed_delta, expected_delta)
        recorded = {key: item["delta"] for key, item in self.delta["component_delta"].items()}
        self.assertEqual(recorded, expected_delta)
        for key, item in self.delta["component_delta"].items():
            self.assertEqual(item["before"], before[key])
            self.assertEqual(item["after"], after[key])

    def test_private_acceptance_evidence_is_exact_and_bounded(self) -> None:
        evidence = self.delta["private_core_evidence"]
        self.assertEqual(evidence["repository"], "horbolsi/8x8")
        self.assertEqual(evidence["pull_request"], 130)
        self.assertEqual(evidence["validated_head"], "7745c9efede0727c1518bdb9cd99a8c063c4b5df")
        self.assertEqual(evidence["merge"], "54daf9c635bdd4a6a8cba64f1042decb4b9261cf")
        self.assertEqual(evidence["workflow_run_id"], 31456965566)
        self.assertEqual(evidence["exact_head_status"], "PASS")
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        gates = {gate["dimension"] for gate in self.delta["closed_bounded_gates"]}
        self.assertEqual(gates, {"D1", "D4", "D8"})

    def test_global_and_native_nonclaims_remain_false(self) -> None:
        self.assertFalse(self.after["score_is_universal_rank"])
        self.assertFalse(self.after["global_100_claim_allowed"])
        self.assertFalse(self.delta["score_is_universal_rank"])
        self.assertFalse(self.delta["global_100_claim_allowed"])
        truth = self.delta["truth_boundary"]
        for key, value in truth.items():
            self.assertIs(value, False, f"{key} must remain false")
        frontier = self.after["frontier"]["current_status"]
        self.assertIn("NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN", frontier)
        self.assertIn("PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED", frontier)

    def test_benchmark_order_tracks_new_score(self) -> None:
        projects = self.after["projects"]
        scores = [project["score"] for project in projects]
        self.assertEqual(scores, sorted(scores, reverse=True))
        names = [project["project"] for project in projects]
        self.assertLess(names.index("8x8 One Fabric"), names.index("Dify"))
        self.assertGreater(names.index("8x8 One Fabric"), names.index("n8n"))


if __name__ == "__main__":
    unittest.main()
