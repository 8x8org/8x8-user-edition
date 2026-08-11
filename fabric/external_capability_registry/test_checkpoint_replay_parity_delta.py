from __future__ import annotations

import json
import unittest

from fabric.external_capability_registry.benchmark import HERE, BASE_BENCHMARK, materialize_benchmark

A2A = HERE / "benchmark_2026-08-11_a2a_overlay.json"
SANDBOX = HERE / "benchmark_2026-08-11_sandbox_overlay.json"
GUARDED = HERE / "benchmark_2026-08-11_guarded_session_overlay.json"
CHECKPOINT = HERE / "benchmark_2026-08-11_checkpoint_replay_overlay.json"
DELTA = HERE / "checkpoint_replay_parity_delta_2026-08-11.json"


class CheckpointReplayParityDeltaTests(unittest.TestCase):
    def test_delta_moves_only_d1_and_score_by_one(self) -> None:
        before = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED))
        after = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED, CHECKPOINT))
        before_baseline = next(project for project in before["projects"] if project["kind"] == "baseline")
        after_baseline = next(project for project in after["projects"] if project["kind"] == "baseline")
        self.assertEqual(before_baseline["score"], 82)
        self.assertEqual(after_baseline["score"], 83)
        for dimension in (f"D{i}" for i in range(1, 9)):
            expected_delta = 1 if dimension == "D1" else 0
            self.assertEqual(
                after_baseline["components"][dimension] - before_baseline["components"][dimension],
                expected_delta,
                dimension,
            )

    def test_private_evidence_is_exact_and_review_truth_is_not_inflated(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        self.assertEqual((delta["base_score"], delta["next_score"], delta["score_change"]), (82, 83, 1))
        evidence = delta["private_core_evidence"]
        self.assertEqual(evidence["pull_request"], 136)
        self.assertEqual(evidence["validated_head"], "a0e5856506b0fb571bb176780243c731a14e5bcb")
        self.assertEqual(evidence["workflow_run_id"], 31471288957)
        self.assertEqual(evidence["merge"], "1337a080b89062616d53a9120c5984f55084f414")
        self.assertEqual(evidence["exact_head_status"], "PASS")
        self.assertEqual(evidence["inherited_regression_tests"], 61)
        self.assertEqual(evidence["checkpoint_replay_tests"], 21)
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        for marker in (
            "MISSION_LOCAL_EFFECT_ID",
            "NONTERMINAL_SOURCE_RACE",
            "HISTORICAL_RECEIPT_TRUST_ANCHOR",
        ):
            self.assertIn(marker, evidence["manual_adversarial_review"])

    def test_truth_boundary_preserves_bounded_scope(self) -> None:
        truth = json.loads(DELTA.read_text(encoding="utf-8"))["truth_boundary"]
        for key in (
            "cross_process_checkpoint_reopen",
            "immutable_original_history",
            "fork_without_history_rewrite",
            "sealed_source_required_for_effectful_replay",
            "historical_receipt_membership_verified",
            "thread_wide_replay_effect_identity",
            "sibling_fork_effect_reuse_blocked",
            "failed_reservations_remain_blocked",
        ):
            self.assertIs(truth[key], True, key)
        for key in (
            "external_provider_replay",
            "distributed_checkpoint_backend",
            "cross_database_replay_reservation",
            "native_device_checkpoint_binding",
            "production_workflow_replay_adoption",
            "external_provider_exactly_once",
            "privacy_preserving_attestation_implemented",
            "global_100_100",
        ):
            self.assertIs(truth[key], False, key)

    def test_hosted_timing_is_not_promoted_to_production_throughput(self) -> None:
        measured = json.loads(DELTA.read_text(encoding="utf-8"))["measured_canary"]
        self.assertEqual(measured["processes"], 2)
        self.assertEqual(measured["checkpoint_count"], 2)
        self.assertEqual(measured["branch_count"], 2)
        self.assertEqual(measured["lineage_registry_effect_count"], 2)
        self.assertEqual(measured["pcef_receipts_per_mission"], 8)
        self.assertGreater(measured["total_ms"], 0)
        self.assertEqual(
            measured["timing_scope"],
            "SINGLE_HOSTED_CI_CANARY_NOT_PRODUCTION_REPLAY_THROUGHPUT",
        )


if __name__ == "__main__":
    unittest.main()
