from __future__ import annotations

import unittest

from fabric.external_capability_registry.benchmark import load_benchmark, validate


class ExternalBenchmarkTests(unittest.TestCase):
    def test_bounded_snapshot_validates(self) -> None:
        result = validate(load_benchmark())
        self.assertGreaterEqual(result["external_denominator"], 10)
        self.assertEqual(result["project_denominator"], 12)
        self.assertEqual(result["baseline_score"], 78)
        self.assertFalse(result["global_100_claim_allowed"])
        self.assertEqual(result["status"], "VALIDATED_BOUNDED_SNAPSHOT")

    def test_frontier_is_not_promoted_by_declaration(self) -> None:
        data = load_benchmark()
        status = data["frontier"]["current_status"]
        self.assertIn("REPOSITORY_PROCESS_DEATH_RECOVERY_VALIDATED", status)
        self.assertIn("AGENT_STATE_CAPSULE_VALIDATED", status)
        self.assertIn("VERSIONED_SPCA_EVAL_CORPUS_VALIDATED", status)
        self.assertIn("NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN", status)
        self.assertIn("PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED", status)


if __name__ == "__main__":
    unittest.main()
