from copy import deepcopy

import pytest

from receipts.verifier import issue_receipt, receipt_digest, verify_receipt


COMMIT = "1" * 40


def test_issue_and_verify_round_trip():
    receipt = issue_receipt(COMMIT, "test-receipt-0.0.1")
    verify_receipt(receipt)


def test_tampered_receipt_is_rejected():
    receipt = issue_receipt(COMMIT, "test-receipt-0.0.1")
    tampered = deepcopy(receipt)
    tampered["truth_class"] = "FAKE"
    with pytest.raises(ValueError, match="tamper seal"):
        verify_receipt(tampered)


def test_version_drift_is_rejected():
    receipt = issue_receipt(COMMIT, "test-receipt-0.0.1")
    receipt["product_version"] = "1.0.0"
    receipt["receipt_sha256"] = receipt_digest(receipt)
    with pytest.raises(ValueError, match="version must be 0.0.1"):
        verify_receipt(receipt)


def test_bad_commit_is_rejected():
    with pytest.raises(ValueError, match="40-character hexadecimal"):
        issue_receipt("not-a-commit", "test-receipt-0.0.1")
