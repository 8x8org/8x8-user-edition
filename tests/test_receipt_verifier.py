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


if __name__ == "__main__":
    unittest.main()
