from __future__ import annotations

import unittest

from fabric.external_capability_registry.benchmark import (
    FRONTIER_STATUS_REQUIRED_MARKERS,
    load_benchmark,
    validate,
)


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
        for marker in FRONTIER_STATUS_REQUIRED_MARKERS:
            self.assertIn(marker, status)

    def test_frontier_marker_contract_is_single_sourced(self) -> None:
        self.assertGreater(len(FRONTIER_STATUS_REQUIRED_MARKERS), 30)
        self.assertEqual(
            len(FRONTIER_STATUS_REQUIRED_MARKERS),
            len(set(FRONTIER_STATUS_REQUIRED_MARKERS)),
        )


if __name__ == "__main__":
    unittest.main()
