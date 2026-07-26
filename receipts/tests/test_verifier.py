"""
Unit tests for receipts/verifier.py

Tests cover:
  - Valid receipt passes all checks
  - Structural validation catches missing/extra/invalid fields
  - receipt_hash mismatch is detected (tamper detection)
  - state_hash mismatch is detected (state file alteration)
  - state_assertions mismatch is detected
  - Edge cases: wrong types, wrong patterns
"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Allow running as `python3 -m pytest receipts/tests/` from repo root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from verifier import (
    REQUIRED_ASSERTIONS,
    REQUIRED_FIELDS,
    VerificationError,
    compute_receipt_hash,
    issue_receipt,
    verify,
    verify_receipt_hash,
    verify_state_assertions,
    verify_state_hash,
)

GOOD_COMMIT = "6aec283cb3ee539b7bddad354ac885e87c7cc0f0"
GOOD_STATE_HASH = "1ef0c8813c2ccc7efdd4e4ab606b05a08e47064db37b268e91920fa84a72e777"


def _make_state_bytes(overrides: dict | None = None) -> bytes:
    """Return a minimal valid public-state.json as bytes."""
    data = {
        "schema_version": "1.0.0",
        "product": "8x8 User Edition",
        "private_control_plane_connected": False,
        "credentials_included": False,
        "wallet_material_included": False,
        "remote_shell_enabled": False,
        "live_trading_enabled": False,
        "targets_are_live_entitlements": False,
        "private_repositories_connected": False,
        "private_memory_connected": False,
        "private_messages_connected": False,
        "public_billing_enabled": False,
        "user_node_contribution_enabled": False,
        "hidden_telemetry_enabled": False,
        "camera_or_microphone_auto_access": False,
    }
    if overrides:
        data.update(overrides)
    return json.dumps(data, indent=2).encode()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _make_receipt(state_bytes: bytes | None = None, overrides: dict | None = None) -> dict:
    """Return a complete, valid receipt dict for the given state bytes."""
    if state_bytes is None:
        state_bytes = _make_state_bytes()
    sh = _sha256(state_bytes)
    body = {
        "schema_version": "1.0.0",
        "receipt_id": "test-receipt-20260101",
        "issued_at": "2026-01-01T00:00:00Z",
        "repository": "8x8org/8x8-user-edition",
        "commit_sha": GOOD_COMMIT,
        "state_file": "state/public-state.json",
        "state_hash": sh,
        "hash_algorithm": "sha256",
        "state_assertions": {
            "private_control_plane_connected": False,
            "credentials_included": False,
            "wallet_material_included": False,
            "remote_shell_enabled": False,
            "live_trading_enabled": False,
            "targets_are_live_entitlements": False,
        },
    }
    if overrides:
        # Allow removing a field by setting value to None
        for k, v in overrides.items():
            if v is None:
                body.pop(k, None)
            else:
                body[k] = v
    receipt_hash = compute_receipt_hash(body)
    return {**body, "receipt_hash": receipt_hash}


class TestStructuralValidation(unittest.TestCase):
    def _run(self, receipt_path, **kwargs):
        """Run verify() with state checks disabled."""
        verify(receipt_path, check_state=False, **kwargs)

    def _write(self, receipt: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, dir="/tmp"
        )
        json.dump(receipt, tmp)
        tmp.flush()
        return Path(tmp.name)

    def test_valid_receipt_passes(self):
        r = _make_receipt()
        p = self._write(r)
        self._run(p)  # should not raise

    def test_missing_required_field(self):
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                r = _make_receipt()
                del r[field]
                p = self._write(r)
                with self.assertRaises(VerificationError, msg=f"field={field}"):
                    self._run(p)

    def test_extra_field_rejected(self):
        r = _make_receipt()
        r["unexpected_key"] = "value"
        # recompute receipt_hash to pass hash check, but structural check should fail
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_invalid_schema_version(self):
        r = _make_receipt(overrides={"schema_version": "not-semver"})
        # recompute hash so tamper check passes, structural check fails
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_invalid_commit_sha_too_short(self):
        r = _make_receipt(overrides={"commit_sha": "abc123"})
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_invalid_commit_sha_uppercase(self):
        r = _make_receipt(overrides={"commit_sha": "A" * 40})
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_wrong_state_file_path(self):
        r = _make_receipt(overrides={"state_file": "state/other.json"})
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_wrong_hash_algorithm(self):
        r = _make_receipt(overrides={"hash_algorithm": "md5"})
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_invalid_issued_at_no_z(self):
        r = _make_receipt(overrides={"issued_at": "2026-01-01T00:00:00"})
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_missing_assertion_key(self):
        r = _make_receipt()
        del r["state_assertions"]["credentials_included"]
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_assertion_non_boolean(self):
        r = _make_receipt()
        r["state_assertions"]["credentials_included"] = "no"
        r["receipt_hash"] = compute_receipt_hash(
            {k: v for k, v in r.items() if k != "receipt_hash"}
        )
        p = self._write(r)
        with self.assertRaises(VerificationError):
            self._run(p)

    def test_not_a_json_object(self):
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, dir="/tmp"
        )
        json.dump(["not", "an", "object"], tmp)
        tmp.flush()
        with self.assertRaises(VerificationError):
            self._run(Path(tmp.name))

    def test_invalid_json(self):
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, dir="/tmp"
        )
        tmp.write("{not valid json}")
        tmp.flush()
        with self.assertRaises(VerificationError):
            self._run(Path(tmp.name))


class TestReceiptHashTamperDetection(unittest.TestCase):
    def _write(self, receipt: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, dir="/tmp"
        )
        json.dump(receipt, tmp)
        tmp.flush()
        return Path(tmp.name)

    def test_unmodified_receipt_passes_hash_check(self):
        r = _make_receipt()
        verify_receipt_hash(r)  # should not raise

    def test_altered_receipt_id_detected(self):
        r = _make_receipt()
        r["receipt_id"] = "tampered-receipt-id"
        with self.assertRaises(VerificationError):
            verify_receipt_hash(r)

    def test_altered_commit_sha_detected(self):
        r = _make_receipt()
        r["commit_sha"] = "a" * 40
        with self.assertRaises(VerificationError):
            verify_receipt_hash(r)

    def test_altered_state_hash_detected(self):
        r = _make_receipt()
        r["state_hash"] = "b" * 64
        with self.assertRaises(VerificationError):
            verify_receipt_hash(r)

    def test_altered_assertion_detected(self):
        r = _make_receipt()
        r["state_assertions"]["credentials_included"] = True
        with self.assertRaises(VerificationError):
            verify_receipt_hash(r)

    def test_wrong_receipt_hash_string(self):
        r = _make_receipt()
        r["receipt_hash"] = "0" * 64
        with self.assertRaises(VerificationError):
            verify_receipt_hash(r)


class TestStateHashVerification(unittest.TestCase):
    def _write_state(self, data: bytes) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="wb", delete=False, dir="/tmp"
        )
        tmp.write(data)
        tmp.flush()
        return Path(tmp.name)

    def test_matching_state_hash_passes(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        state_path = self._write_state(state_bytes)
        verify_state_hash(r, state_path)  # should not raise

    def test_altered_state_file_detected(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        # Write a different file
        state_path = self._write_state(state_bytes + b" ")
        with self.assertRaises(VerificationError):
            verify_state_hash(r, state_path)

    def test_missing_state_file_raises(self):
        r = _make_receipt()
        with self.assertRaises(VerificationError):
            verify_state_hash(r, Path("/tmp/nonexistent_state_99999.json"))


class TestStateAssertionsVerification(unittest.TestCase):
    def _write_state(self, data: bytes) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="wb", delete=False, dir="/tmp"
        )
        tmp.write(data)
        tmp.flush()
        return Path(tmp.name)

    def test_matching_assertions_pass(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        state_path = self._write_state(state_bytes)
        verify_state_assertions(r, state_path)  # should not raise

    def test_tampered_assertion_in_state_detected(self):
        state_bytes = _make_state_bytes({"credentials_included": True})
        r = _make_receipt(state_bytes=_make_state_bytes())  # receipt claims False
        state_path = self._write_state(state_bytes)
        with self.assertRaises(VerificationError):
            verify_state_assertions(r, state_path)

    def test_tampered_assertion_in_receipt_detected(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        r["state_assertions"]["live_trading_enabled"] = True
        state_path = self._write_state(state_bytes)
        with self.assertRaises(VerificationError):
            verify_state_assertions(r, state_path)


class TestEndToEndVerify(unittest.TestCase):
    def _write(self, obj, binary=False) -> Path:
        mode = "wb" if binary else "w"
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode=mode, delete=False, dir="/tmp"
        )
        if binary:
            tmp.write(obj)
        else:
            json.dump(obj, tmp)
        tmp.flush()
        return Path(tmp.name)

    def test_full_verify_valid_receipt_passes(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        receipt_path = self._write(r)
        state_path = self._write(state_bytes, binary=True)
        verify(receipt_path, state_path=state_path)  # should not raise

    def test_full_verify_no_state_check_passes(self):
        r = _make_receipt()
        receipt_path = self._write(r)
        verify(receipt_path, check_state=False)  # should not raise

    def test_full_verify_tampered_receipt_fails(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        r["receipt_id"] = "tampered"
        receipt_path = self._write(r)
        state_path = self._write(state_bytes, binary=True)
        with self.assertRaises(VerificationError):
            verify(receipt_path, state_path=state_path)

    def test_full_verify_altered_state_fails(self):
        state_bytes = _make_state_bytes()
        r = _make_receipt(state_bytes=state_bytes)
        receipt_path = self._write(r)
        altered_state = self._write(_make_state_bytes({"credentials_included": True}), binary=True)
        with self.assertRaises(VerificationError):
            verify(receipt_path, state_path=altered_state)


class TestExampleReceipt(unittest.TestCase):
    """Validate the committed example receipt against the repo's state file."""

    REPO_ROOT = Path(__file__).parent.parent.parent
    EXAMPLE = REPO_ROOT / "receipts" / "examples" / "receipt-0.1.0-beta.json"
    STATE = REPO_ROOT / "state" / "public-state.json"

    def test_example_receipt_exists(self):
        self.assertTrue(self.EXAMPLE.is_file(), f"Example receipt not found: {self.EXAMPLE}")

    def test_example_receipt_hash_intact(self):
        r = json.loads(self.EXAMPLE.read_text())
        verify_receipt_hash(r)  # raises on tamper

    def test_example_receipt_matches_current_state(self):
        """The example receipt must match the current state/public-state.json."""
        if not self.STATE.is_file():
            self.skipTest("state/public-state.json not found")
        verify(self.EXAMPLE, state_path=self.STATE)

    def test_example_receipt_schema_version(self):
        r = json.loads(self.EXAMPLE.read_text())
        self.assertEqual(r.get("schema_version"), "1.0.0")

    def test_example_receipt_has_all_required_assertions(self):
        r = json.loads(self.EXAMPLE.read_text())
        assertions = set(r.get("state_assertions", {}).keys())
        self.assertTrue(
            REQUIRED_ASSERTIONS.issubset(assertions),
            f"Missing assertion keys: {REQUIRED_ASSERTIONS - assertions}",
        )


class TestIssueReceipt(unittest.TestCase):
    def _write_state(self, data: bytes) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", mode="wb", delete=False, dir="/tmp"
        )
        tmp.write(data)
        tmp.flush()
        return Path(tmp.name)

    def test_issued_receipt_is_self_consistent(self):
        state_bytes = _make_state_bytes()
        state_path = self._write_state(state_bytes)
        r = issue_receipt(state_path, GOOD_COMMIT, "test-20260101")
        verify_receipt_hash(r)  # should not raise

    def test_issued_receipt_state_hash_matches(self):
        state_bytes = _make_state_bytes()
        state_path = self._write_state(state_bytes)
        r = issue_receipt(state_path, GOOD_COMMIT, "test-20260101")
        self.assertEqual(r["state_hash"], _sha256(state_bytes))

    def test_issue_receipt_bad_commit_raises(self):
        state_bytes = _make_state_bytes()
        state_path = self._write_state(state_bytes)
        with self.assertRaises(ValueError):
            issue_receipt(state_path, "notasha", "test")

    def test_issue_receipt_missing_state_raises(self):
        with self.assertRaises(ValueError):
            issue_receipt(Path("/tmp/nonexistent_99999.json"), GOOD_COMMIT, "test")


if __name__ == "__main__":
    unittest.main()
