from __future__ import annotations

import json
import unittest
from pathlib import Path

from fabric.external_capability_registry.benchmark import BASE_BENCHMARK, HERE, materialize_benchmark

A2A_OVERLAY = HERE / "benchmark_2026-08-11_a2a_overlay.json"
SANDBOX_OVERLAY = HERE / "benchmark_2026-08-11_sandbox_overlay.json"
GUARDED_OVERLAY = HERE / "benchmark_2026-08-11_guarded_session_overlay.json"
DELTA = HERE / "guarded_session_trace_parity_delta_2026-08-11.json"


class GuardedSessionTraceParityDeltaTests(unittest.TestCase):
    def test_delta_moves_only_d2_and_score_by_one(self) -> None:
        before = materialize_benchmark(BASE_BENCHMARK, (A2A_OVERLAY, SANDBOX_OVERLAY))
        after = materialize_benchmark(BASE_BENCHMARK, (A2A_OVERLAY, SANDBOX_OVERLAY, GUARDED_OVERLAY))
        before_baseline = next(project for project in before["projects"] if project["kind"] == "baseline")
        after_baseline = next(project for project in after["projects"] if project["kind"] == "baseline")
        self.assertEqual(before_baseline["score"], 81)
        self.assertEqual(after_baseline["score"], 82)
        for dimension in (f"D{i}" for i in range(1, 9)):
            expected_delta = 1 if dimension == "D2" else 0
            self.assertEqual(
                after_baseline["components"][dimension] - before_baseline["components"][dimension],
                expected_delta,
                dimension,
            )

    def test_private_evidence_and_review_truth_are_exact(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        self.assertEqual((delta["base_score"], delta["next_score"], delta["score_change"]), (81, 82, 1))
        evidence = delta["private_core_evidence"]
        self.assertEqual(evidence["validated_head"], "1122b18920464aa5941a704e72371e828de041d8")
        self.assertEqual(evidence["workflow_run_id"], 31466513039)
        self.assertEqual(evidence["merge"], "43ae08431b37b58f43a5461e7d6828aa1e246ed6")
        self.assertEqual(evidence["combined_master_validated_head"], "ff285fcd97fbf386070452263b446c2020cec424")
        self.assertEqual(evidence["combined_master_workflow_run_id"], 31466652794)
        self.assertEqual(evidence["combined_master_evidence_merge"], "30029d4b66754ab95a702cbb51705cf97bb8e300")
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        self.assertIn("REQUIRED_STAGE_OMISSION", evidence["manual_adversarial_review"])

    def test_truth_boundary_stays_bounded(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        truth = delta["truth_boundary"]
        for key in (
            "cross_process_sqlite_session_persistence",
            "required_guardrail_stage_completeness",
            "privacy_first_digest_trace",
            "combined_master_compatibility",
        ):
            self.assertIs(truth[key], True, key)
        for key in (
            "production_model_provider_called",
            "distributed_session_backend",
            "all_production_agent_runs_guarded",
            "native_device_runtime_binding_proven",
            "external_provider_effect_proven",
            "privacy_preserving_attestation_implemented",
            "global_100_100",
        ):
            self.assertIs(truth[key], False, key)

    def test_canary_measurement_is_scoped_not_performance_marketing(self) -> None:
        measured = json.loads(DELTA.read_text(encoding="utf-8"))["measured_canary"]
        self.assertEqual(measured["successful_processes"], 2)
        self.assertEqual(measured["trace_count"], 3)
        self.assertEqual(measured["session_turns"], 5)
        self.assertEqual(measured["pcef_receipts_per_successful_mission"], 8)
        self.assertGreater(measured["total_ms"], 0)
        self.assertEqual(
            measured["timing_scope"],
            "SINGLE_HOSTED_CI_CANARY_NOT_MODEL_LATENCY_OR_PRODUCTION_THROUGHPUT",
        )


if __name__ == "__main__":
    unittest.main()
