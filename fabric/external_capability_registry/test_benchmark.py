from __future__ import annotations

import unittest

from fabric.external_capability_registry.benchmark import load_benchmark, validate


class ExternalBenchmarkTests(unittest.TestCase):
    def test_bounded_snapshot_validates(self) -> None:
        result = validate(load_benchmark())
        self.assertGreaterEqual(result["external_denominator"], 10)
        self.assertEqual(result["project_denominator"], 12)
        self.assertEqual(result["baseline_score"], 85)
        self.assertFalse(result["global_100_claim_allowed"])
        self.assertEqual(result["status"], "VALIDATED_BOUNDED_SNAPSHOT")

    def test_frontier_is_not_promoted_by_declaration(self) -> None:
        status = load_benchmark()["frontier"]["current_status"]
        for marker in (
            "REPOSITORY_PROCESS_DEATH_RECOVERY_VALIDATED",
            "AGENT_STATE_CAPSULE_VALIDATED",
            "VERSIONED_SPCA_EVAL_CORPUS_VALIDATED",
            "A2A_HTTP_JSON_TWO_PROCESS_SELF_INTEROP_VALIDATED",
            "REPOSITORY_TWO_PROCESS_AUTHENTICATED_A2A_EDGE_VALIDATED",
            "A2A_CALLER_SCOPED_ACL_FIRST_AUTHORIZATION_VALIDATED",
            "A2A_PRE_INGRESS_OWNERSHIP_RESERVATION_VALIDATED",
            "A2A_CREDENTIAL_ROTATION_IDEMPOTENCY_VALIDATED",
            "A2A_DURABLE_TOKEN_REVOCATION_VALIDATED",
            "REPOSITORY_CI_PCEF_SANDBOX_ISOLATION_VALIDATED",
            "PCEF_GUARDED_PERSISTENT_SESSION_TRACE_VALIDATED",
            "GUARDED_SESSION_COMBINED_MASTER_COMPATIBILITY_VALIDATED",
            "PCEF_CHECKPOINT_REPLAY_FORK_V1_VALIDATED",
            "REPLAY_SOURCE_TERMINAL_SEAL_VALIDATED",
            "REPLAY_HISTORICAL_RECEIPT_MEMBERSHIP_VALIDATED",
            "REPLAY_THREAD_WIDE_EFFECT_IDENTITY_VALIDATED",
            "PCEF_TYPED_EIGHT_WAY_SUPERSTEP_VALIDATED",
            "SUPERSTEP_EIGHT_DISTINCT_PCEF_WORKER_PIDS_VALIDATED",
            "SUPERSTEP_INDEPENDENT_CHILD_VERIFICATION_VALIDATED",
            "SUPERSTEP_TIMING_EVIDENCE_PCEF_BOUND_VALIDATED",
            "SUPERSTEP_COORDINATOR_DEATH_REOPEN_VALIDATED",
            "PCEF_VERIFICATION_RESERVED_AUDIT_FIELDS_VALIDATED",
            "PRODUCTION_COUNCIL_CONTROL_PLANE_ADOPTION_NOT_YET_PROVEN",
            "DISTRIBUTED_ORCHESTRATION_BACKEND_NOT_IMPLEMENTED",
            "PRODUCTION_WORKFLOW_REPLAY_ADOPTION_NOT_YET_PROVEN",
            "DISTRIBUTED_CHECKPOINT_BACKEND_NOT_IMPLEMENTED",
            "CROSS_DATABASE_REPLAY_RESERVATION_NOT_IMPLEMENTED",
            "DISTRIBUTED_SESSION_BACKEND_NOT_IMPLEMENTED",
            "ALL_PRODUCTION_AGENT_RUNS_GUARDED_NOT_YET_PROVEN",
            "PRODUCTION_MODEL_PROVIDER_GUARDED_RUN_NOT_YET_PROVEN",
            "ALL_RISKY_PRODUCTION_LANES_SANDBOXED_NOT_YET_PROVEN",
            "VM_MICROVM_ISOLATION_NOT_IMPLEMENTED",
            "INDEPENDENT_THIRD_PARTY_A2A_INTEROP_NOT_YET_PROVEN",
            "AUTHENTICATED_PRODUCTION_A2A_EDGE_NOT_YET_IMPLEMENTED",
            "PUBLIC_HTTPS_TLS_A2A_NOT_YET_PROVEN",
            "OAUTH_OIDC_AUTHORIZATION_SERVER_NOT_IMPLEMENTED",
            "NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN",
            "EXTERNAL_PROVIDER_EXACTLY_ONCE_NOT_YET_PROVEN",
            "PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED",
        ):
            self.assertIn(marker, status)


if __name__ == "__main__":
    unittest.main()
