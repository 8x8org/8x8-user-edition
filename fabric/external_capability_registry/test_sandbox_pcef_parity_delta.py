from __future__ import annotations

import json
import unittest
from pathlib import Path

from fabric.external_capability_registry.benchmark import BASE_BENCHMARK, HERE, materialize_benchmark


DELTA = HERE / "sandbox_pcef_parity_delta_2026-08-11.json"
A2A_OVERLAY = HERE / "benchmark_2026-08-11_a2a_overlay.json"
SANDBOX_OVERLAY = HERE / "benchmark_2026-08-11_sandbox_overlay.json"


class SandboxPCEFParityDeltaTests(unittest.TestCase):
    def test_delta_moves_only_d5_and_score_by_one(self) -> None:
        before = materialize_benchmark(BASE_BENCHMARK, (A2A_OVERLAY,))
        after = materialize_benchmark(BASE_BENCHMARK, (A2A_OVERLAY, SANDBOX_OVERLAY))
        before_baseline = next(project for project in before["projects"] if project["kind"] == "baseline")
        after_baseline = next(project for project in after["projects"] if project["kind"] == "baseline")

        self.assertEqual(before_baseline["score"], 80)
        self.assertEqual(after_baseline["score"], 81)
        for dimension in (f"D{i}" for i in range(1, 9)):
            expected_delta = 1 if dimension == "D5" else 0
            self.assertEqual(
                after_baseline["components"][dimension] - before_baseline["components"][dimension],
                expected_delta,
                dimension,
            )

    def test_delta_receipt_preserves_bounded_truth(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        self.assertEqual(delta["base_score"], 80)
        self.assertEqual(delta["next_score"], 81)
        self.assertEqual(delta["score_change"], 1)
        self.assertFalse(delta["score_is_universal_rank"])
        self.assertFalse(delta["global_100_claim_allowed"])
        evidence = delta["private_core_evidence"]
        self.assertEqual(evidence["validated_head"], "4771fb8bf16bac736ae2db9c520cbd3f95be9fa6")
        self.assertEqual(evidence["merge"], "496750dba375abf601f9a947fcc93ac14dd5b96d")
        self.assertEqual(evidence["exact_head_status"], "PASS")
        self.assertEqual(evidence["detailed_coderabbit_line_review"], "NOT_PERFORMED_RATE_LIMITED")
        self.assertEqual(evidence["manual_adversarial_review"], "PERFORMED_AND_PROOF_SEMANTICS_HARDENED")

        truth = delta["truth_boundary"]
        self.assertTrue(truth["repository_ci_container_isolation"])
        for key in (
            "all_risky_production_lanes_sandboxed",
            "vm_or_microvm_isolation",
            "native_device_local_sandbox_binding",
            "third_party_image_provenance",
            "external_provider_effect_isolation",
            "native_end_to_end_binding_proven",
            "external_provider_exactly_once_proven",
            "privacy_preserving_attestation_implemented",
            "global_100_100",
        ):
            self.assertFalse(truth[key], key)

    def test_observed_controls_are_not_requested_flag_aliases(self) -> None:
        delta = json.loads(DELTA.read_text(encoding="utf-8"))
        controls = delta["observed_controls"]
        for key in (
            "root_mount_read_only",
            "input_mount_read_only",
            "input_write_blocked",
            "tmpfs_mounted_strict",
            "network_loopback_only",
            "outbound_tcp_blocked",
            "non_root_user",
            "cap_eff_zero",
            "no_new_privileges",
            "pids_limit",
            "memory_limit",
            "cpu_limit",
            "host_secret_unreachable",
            "host_environment_not_inherited",
            "pcef_chain_verified",
            "pcef_terminal",
        ):
            self.assertIs(controls[key], True, key)
        self.assertEqual(controls["network_interfaces"], ["lo"])


if __name__ == "__main__":
    unittest.main()
