from copy import deepcopy
import subprocess

import pytest

from receipts.verifier import (
    issue_receipt,
    receipt_digest,
    validate_source_commit,
    verify_receipt,
)


def current_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def test_issue_and_verify_round_trip():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    verify_receipt(receipt)


def test_tampered_receipt_is_rejected():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    tampered = deepcopy(receipt)
    tampered["truth_class"] = "FAKE"
    with pytest.raises(ValueError, match="tamper seal"):
        verify_receipt(tampered)


def test_version_drift_is_rejected():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    receipt["product_version"] = "1.0.0"
    receipt["receipt_sha256"] = receipt_digest(receipt)
    with pytest.raises(ValueError, match="version must be 0.1.0-stable"):
        verify_receipt(receipt)


def test_whole_system_truth_is_bound_into_receipt():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    assert receipt["assertions"]["whole_system_complete"] is False
    assert receipt["assertions"]["whole_system_score"] == "NOT_INFERRED"
    assert receipt["assertions"]["stable_scope"] == "PUBLIC_WEB_CLIENT"


def test_bad_commit_is_rejected():
    with pytest.raises(ValueError, match="40-character hexadecimal"):
        issue_receipt("not-a-commit", "test-receipt-0.1.0")


def test_verify_rejects_branch_or_tag_revspec_even_with_resealed_receipt():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    receipt["source_commit"] = "main"
    receipt["receipt_sha256"] = receipt_digest(receipt)
    with pytest.raises(ValueError, match="40-character hexadecimal"):
        verify_receipt(receipt)


def test_verify_rejects_abbreviated_commit_even_with_resealed_receipt():
    receipt = issue_receipt(current_commit(), "test-receipt-0.1.0")
    receipt["source_commit"] = current_commit()[:12]
    receipt["receipt_sha256"] = receipt_digest(receipt)
    with pytest.raises(ValueError, match="40-character hexadecimal"):
        verify_receipt(receipt)


def test_source_commit_is_rebuilt_as_canonical_hex():
    observed = current_commit().upper()
    assert validate_source_commit(observed) == bytes.fromhex(observed).hex()
