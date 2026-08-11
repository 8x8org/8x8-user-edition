import json
import unittest
from unittest.mock import patch

from receipts import verifier


class ReceiptVerifierSourceCommitTests(unittest.TestCase):
    def source_state(self, promotion_state="PUBLIC_STABLE"):
        return {
            "product_version": "0.1.0",
            "release": "0.1.0-stable",
            "stable_scope": "PUBLIC_WEB_CLIENT",
            "promotion_state": promotion_state,
            "whole_system_complete": False,
            "whole_system_score": "NOT_INFERRED",
            "private_control_plane_connected": False,
            "credentials_included": False,
            "wallet_material_included": False,
            "remote_shell_enabled": False,
            "live_trading_enabled": False,
            "public_billing_enabled": False,
            "hidden_telemetry_enabled": False,
            "targets_are_live_entitlements": False,
            "truth_class": "PUBLIC_SOURCE_VALIDATED",
        }

    def receipt_for(self, source_state):
        raw = (json.dumps(source_state, indent=2) + "\n").encode("utf-8")
        receipt = {
            "schema_version": "0.1.0",
            "product_version": "0.1.0",
            "release": "0.1.0-stable",
            "receipt_id": "historical-regression",
            "source_commit": "a" * 40,
            "state_path": "state/public-state.json",
            "state_sha256": verifier.sha256_bytes(raw),
            "issued_at": "2026-08-09T00:00:00Z",
            "reality": "PUBLIC_PRESENT",
            "truth_class": source_state["truth_class"],
            "assertions": verifier.critical_assertions(source_state),
        }
        receipt["receipt_sha256"] = verifier.receipt_digest(receipt)
        return raw, receipt

    def test_historical_public_stable_receipt_verifies_against_source_commit_snapshot(self):
        raw, receipt = self.receipt_for(self.source_state("PUBLIC_STABLE"))
        with patch.object(verifier, "state_bytes_at_commit", return_value=raw):
            verifier.verify_receipt(receipt)

    def test_protected_beta_receipt_verifies_against_its_own_source_commit_snapshot(self):
        raw, receipt = self.receipt_for(self.source_state("PROTECTED_BETA"))
        with patch.object(verifier, "state_bytes_at_commit", return_value=raw):
            verifier.verify_receipt(receipt)

    def test_source_snapshot_hash_mismatch_is_rejected(self):
        raw, receipt = self.receipt_for(self.source_state("PUBLIC_STABLE"))
        changed_raw = raw.replace(b"PUBLIC_STABLE", b"PROTECTED_BETA")
        with patch.object(verifier, "state_bytes_at_commit", return_value=changed_raw):
            with self.assertRaisesRegex(ValueError, "source-commit public-state SHA-256 mismatch"):
                verifier.verify_receipt(receipt)

    def test_mutable_branch_revspec_is_rejected_before_git_resolution(self):
        _, receipt = self.receipt_for(self.source_state())
        receipt["source_commit"] = "main"
        receipt["receipt_sha256"] = verifier.receipt_digest(receipt)
        with patch.object(verifier, "state_bytes_at_commit") as state_lookup:
            with self.assertRaisesRegex(ValueError, "40-character hexadecimal"):
                verifier.verify_receipt(receipt)
            state_lookup.assert_not_called()

    def test_abbreviated_commit_is_rejected_before_git_resolution(self):
        _, receipt = self.receipt_for(self.source_state())
        receipt["source_commit"] = "a" * 12
        receipt["receipt_sha256"] = verifier.receipt_digest(receipt)
        with patch.object(verifier, "state_bytes_at_commit") as state_lookup:
            with self.assertRaisesRegex(ValueError, "40-character hexadecimal"):
                verifier.verify_receipt(receipt)
            state_lookup.assert_not_called()

    def test_receipt_cli_path_cannot_escape_receipts_root(self):
        with self.assertRaisesRegex(ValueError, "under receipts"):
            verifier.resolve_receipt_path("../outside.json")
        with self.assertRaisesRegex(ValueError, "under receipts"):
            verifier.resolve_receipt_path("state/public-state.json")

    def test_receipt_cli_path_accepts_receipts_subtree(self):
        path = verifier.resolve_receipt_path("receipts/example.json")
        self.assertEqual(path.name, "example.json")
        self.assertEqual(path.parent.name, "receipts")


if __name__ == "__main__":
    unittest.main()
