from __future__ import annotations

import json
import unittest

from fabric.external_capability_registry.benchmark import HERE, BASE_BENCHMARK, materialize_benchmark

A2A = HERE / "benchmark_2026-08-11_a2a_overlay.json"
SANDBOX = HERE / "benchmark_2026-08-11_sandbox_overlay.json"
GUARDED = HERE / "benchmark_2026-08-11_guarded_session_overlay.json"
CHECKPOINT = HERE / "benchmark_2026-08-11_checkpoint_replay_overlay.json"
AUTH_A2A = HERE / "benchmark_2026-08-11_authenticated_a2a_overlay.json"
SUPERSTEP = HERE / "benchmark_2026-08-11_typed_superstep_overlay.json"
DELTA = HERE / "typed_superstep_parity_delta_2026-08-11.json"


class TypedSuperstepParityDeltaTests(unittest.TestCase):
    def test_delta_moves_only_d2_and_score_by_one(self) -> None:
        before = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED, CHECKPOINT, AUTH_A2A))
        after = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED, CHECKPOINT, AUTH_A2A, SUPERSTEP))
        before_baseline = next(project for project in before["projects"] if project["kind"] == "baseline")
        after_baseline = next(project for project in after["projects"] if project["kind"] == "baseline")
        self.assertEqual(before_baseline["score"], 84)
        self.assertEqual(after_baseline["score"], 85)
        for dimension in (f"D{i}" for i in range(1, 9)):
            expected_delta = 1 if dimension == "D2" else 0
            self.assertEqual(
                after_baseline["components"][dimension] - before_baseline["components"][dimension],
                expected_delta,
                dimension,
            )

    def test_private_evidence_and_review_truth_are_exact(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        self.assertEqual((delta["base_score"], delta["next_score"], delta["score_change"]), (84, 85, 1))
        evidence = delta["private_core_evidence"]
        self.assertEqual(evidence["pull_request"], 137)
        self.assertEqual(evidence["validated_head"], "58503e79b009b336119a139fe838abab574a6b6e")
        self.assertEqual(evidence["workflow_run_id"], 31475986246)
        self.assertEqual(evidence["merge"], "fb927a97d5687c11a4b039878ceedf7611947dd3")
        self.assertEqual(evidence["current_master_sync_pull_request"], 140)
        self.assertEqual(evidence["current_master_synced_commit"], "4e6fbe0ae4822744e2210fda6a94b754f329e560")
        self.assertEqual(evidence["inherited_regression_tests"], 82)
        self.assertEqual(evidence["verification_audit_integrity_tests"], 1)
        self.assertEqual(evidence["typed_superstep_tests"], 15)
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        for marker in (
            "TIMING_SIDE_TELEMETRY",
            "PARENT_RECEIPT_DRIFT",
            "PARTIAL_FANOUT",
            "VERIFICATION_RESERVED_FIELD_SPOOF",
        ):
            self.assertIn(marker, evidence["manual_adversarial_review"])

    def test_truth_boundary_keeps_parallelism_bounded(self) -> None:
        truth = json.loads(DELTA.read_text(encoding="utf-8"))["truth_boundary"]
        for key in (
            "typed_eight_way_superstep",
            "eight_distinct_pcef_worker_pids",
            "child_verification_independent_from_lease_holder",
            "timing_evidence_pcef_digest_bound",
            "synchronization_barrier",
            "deterministic_slot_order_fanin",
            "coordinator_death_before_join_recovered",
            "verification_reserved_fields_spoof_protected",
        ):
            self.assertIs(truth[key], True, key)
        for key in (
            "production_council_control_plane_adoption",
            "distributed_orchestration_backend",
            "production_model_provider_execution",
            "native_device_runtime_binding",
            "distributed_session_backend",
            "distributed_checkpoint_backend",
            "public_https_tls_a2a",
            "oauth_oidc_authorization_server",
            "independent_third_party_a2a_interop",
            "external_provider_exactly_once",
            "privacy_preserving_attestation_implemented",
            "global_100_100",
        ):
            self.assertIs(truth[key], False, key)

    def test_canary_metrics_are_scoped_not_marketing_throughput(self) -> None:
        measured = json.loads(DELTA.read_text(encoding="utf-8"))["measured_canary"]
        self.assertEqual(measured["slot_count"], 8)
        self.assertEqual(len(measured["child_worker_pids"]), 8)
        self.assertEqual(len(set(measured["child_worker_pids"])), 8)
        self.assertNotEqual(measured["completion_order"], measured["canonical_fanin_order"])
        self.assertEqual(measured["canonical_fanin_order"], list(range(8)))
        self.assertEqual(measured["child_receipts_each"], 8)
        self.assertEqual(measured["parent_receipts"], 8)
        self.assertGreater(measured["total_ms"], 0)
        self.assertEqual(
            measured["timing_scope"],
            "SINGLE_HOSTED_CI_CANARY_NOT_PRODUCTION_DISTRIBUTED_THROUGHPUT",
        )


if __name__ == "__main__":
    unittest.main()
