from __future__ import annotations

import json
import unittest

from fabric.external_capability_registry.benchmark import HERE, BASE_BENCHMARK, materialize_benchmark

A2A = HERE / "benchmark_2026-08-11_a2a_overlay.json"
SANDBOX = HERE / "benchmark_2026-08-11_sandbox_overlay.json"
GUARDED = HERE / "benchmark_2026-08-11_guarded_session_overlay.json"
CHECKPOINT = HERE / "benchmark_2026-08-11_checkpoint_replay_overlay.json"
AUTH = HERE / "benchmark_2026-08-11_authenticated_a2a_overlay.json"
DELTA = HERE / "authenticated_a2a_pcef_parity_delta_2026-08-11.json"


class AuthenticatedA2APCEFParityDeltaTests(unittest.TestCase):
    def test_delta_moves_only_d5_and_score_by_one(self) -> None:
        before = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED, CHECKPOINT))
        after = materialize_benchmark(BASE_BENCHMARK, (A2A, SANDBOX, GUARDED, CHECKPOINT, AUTH))
        before_baseline = next(project for project in before["projects"] if project["kind"] == "baseline")
        after_baseline = next(project for project in after["projects"] if project["kind"] == "baseline")
        self.assertEqual(before_baseline["score"], 83)
        self.assertEqual(after_baseline["score"], 84)
        for dimension in (f"D{i}" for i in range(1, 9)):
            expected_delta = 1 if dimension == "D5" else 0
            self.assertEqual(
                after_baseline["components"][dimension] - before_baseline["components"][dimension],
                expected_delta,
                dimension,
            )

    def test_private_evidence_is_exact_and_review_truth_is_not_inflated(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        self.assertEqual((delta["base_score"], delta["next_score"], delta["score_change"]), (83, 84, 1))
        evidence = delta["private_core_evidence"]
        self.assertEqual(evidence["pull_request"], 138)
        self.assertEqual(evidence["validated_head"], "e6ae8d0db7c3266216b7e0e723f6677f3646db20")
        self.assertEqual(evidence["workflow_run_id"], 31474965207)
        self.assertEqual(evidence["merge"], "4e6fbe0ae4822744e2210fda6a94b754f329e560")
        self.assertEqual(evidence["exact_head_status"], "PASS")
        self.assertEqual(evidence["inherited_regression_tests"], 29)
        self.assertEqual(evidence["authenticated_edge_tests"], 15)
        self.assertEqual(evidence["router_pcef_receipts"], 8)
        self.assertEqual(evidence["specialist_pcef_receipts"], 8)
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        for marker in (
            "TOKEN_ROTATION_REQUEST_IDENTITY",
            "CROSS_PRINCIPAL_DUPLICATE_PROJECTION",
            "ACL_FIRST_LIST_AUTHORIZATION",
            "PRE_INGRESS_CRASH_SAFE_OWNERSHIP",
            "NARROW_FOLLOWUP_ACL_REWRITE",
        ):
            self.assertIn(marker, evidence["manual_adversarial_review"])

    def test_truth_boundary_preserves_production_nonclaims(self) -> None:
        truth = json.loads(DELTA.read_text(encoding="utf-8"))["truth_boundary"]
        for key in (
            "repository_two_process_authenticated_a2a",
            "caller_scoped_acl_first_authorization",
            "pre_ingress_ownership_reservation",
            "credential_rotation_idempotency",
            "durable_token_revocation",
        ):
            self.assertIs(truth[key], True, key)
        for key in (
            "public_https_tls_deployment",
            "oauth_oidc_authorization_server",
            "independent_third_party_a2a_interop",
            "authenticated_production_a2a_edge",
            "native_device_service_binding",
            "external_provider_effect",
            "privacy_preserving_attestation_implemented",
            "global_100_100",
        ):
            self.assertIs(truth[key], False, key)

    def test_hosted_timing_is_not_promoted_to_production_throughput(self) -> None:
        measured = json.loads(DELTA.read_text(encoding="utf-8"))["measured_canary"]
        self.assertEqual(measured["processes"], 2)
        self.assertEqual(measured["router_pcef_receipts"], 8)
        self.assertEqual(measured["specialist_pcef_receipts"], 8)
        self.assertEqual(measured["authentication_scheme"], "Bearer")
        self.assertGreater(measured["total_ms"], 0)
        self.assertEqual(
            measured["timing_scope"],
            "SINGLE_HOSTED_CI_CANARY_NOT_PRODUCTION_AUTH_OR_NETWORK_THROUGHPUT",
        )


if __name__ == "__main__":
    unittest.main()
