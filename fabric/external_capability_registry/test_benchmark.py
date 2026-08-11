from __future__ import annotations

import unittest

from fabric.external_capability_registry.benchmark import load_benchmark, validate


class ExternalBenchmarkTests(unittest.TestCase):
    def test_bounded_snapshot_validates(self) -> None:
        result = validate(load_benchmark())
        self.assertGreaterEqual(result["external_denominator"], 10)
        self.assertEqual(result["project_denominator"], 12)
        self.assertEqual(result["baseline_score"], 82)
        self.assertFalse(result["global_100_claim_allowed"])
        self.assertEqual(result["status"], "VALIDATED_BOUNDED_SNAPSHOT")

    def test_frontier_is_not_promoted_by_declaration(self) -> None:
        data = load_benchmark()
        status = data["frontier"]["current_status"]
        for marker in (
            "REPOSITORY_PROCESS_DEATH_RECOVERY_VALIDATED",
            "AGENT_STATE_CAPSULE_VALIDATED",
            "VERSIONED_SPCA_EVAL_CORPUS_VALIDATED",
            "A2A_HTTP_JSON_TWO_PROCESS_SELF_INTEROP_VALIDATED",
            "REPOSITORY_CI_PCEF_SANDBOX_ISOLATION_VALIDATED",
            "PCEF_GUARDED_PERSISTENT_SESSION_TRACE_VALIDATED",
            "GUARDED_SESSION_COMBINED_MASTER_COMPATIBILITY_VALIDATED",
            "ALL_PRODUCTION_AGENT_RUNS_GUARDED_NOT_YET_PROVEN",
            "DISTRIBUTED_SESSION_BACKEND_NOT_IMPLEMENTED",
            "PRODUCTION_MODEL_PROVIDER_GUARDED_RUN_NOT_YET_PROVEN",
            "ALL_RISKY_PRODUCTION_LANES_SANDBOXED_NOT_YET_PROVEN",
            "VM_MICROVM_ISOLATION_NOT_IMPLEMENTED",
            "INDEPENDENT_THIRD_PARTY_A2A_INTEROP_NOT_YET_PROVEN",
            "AUTHENTICATED_PRODUCTION_A2A_EDGE_NOT_YET_IMPLEMENTED",
            "NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN",
            "PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED",
        ):
            self.assertIn(marker, status)


if __name__ == "__main__":
    unittest.main()
