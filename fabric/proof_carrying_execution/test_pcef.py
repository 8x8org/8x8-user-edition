from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
import unittest

from fabric.proof_carrying_execution.pcef import (
    DuplicateMission,
    ExpiredLease,
    IllegalTransition,
    ProofCarryingLedger,
    StaleTransition,
    VerificationMismatch,
    evidence_hash,
    reopen_receipts,
    verify_receipt_chain,
)

CONTRACT = Path(__file__).with_name("contract.v1.json")


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def _driven_to_verified(secret: bytes | None = b"s"):
    clock = _Clock()
    ledger = ProofCarryingLedger(clock=clock, secret=secret)
    m = ledger.create("k1", inputs={"task": "x"}, dependencies=["d"])
    ledger.pick_up(m.mission_id, "w1", m.revision)
    ledger.lease(m.mission_id, "w1", ttl=1000.0, expected_revision=m.revision)
    ledger.start(m.mission_id, "w1", m.revision)
    ledger.progress(m.mission_id, "w1", m.revision)
    out = {"r": "ok"}
    ledger.commit_effect(m.mission_id, "w1", m.revision, output=out)
    ledger.verify(m.mission_id, "w1", m.revision, expected_output_sha256=evidence_hash(out))
    return ledger, m, out


class PcefLifecycleTests(unittest.TestCase):
    def test_full_verified_lifecycle_reaches_terminal(self) -> None:
        ledger, m, _ = _driven_to_verified()
        ledger.terminalize(m.mission_id, "w1", m.revision)
        self.assertEqual(m.state, "TERMINAL")
        # process-exit semantics are explicitly not verification
        states = [r.to_state for r in m.receipts]
        self.assertEqual(
            states,
            ["CREATED", "PICKED_UP", "LEASED", "STARTED", "PROGRESS",
             "EFFECT_COMMITTED", "VERIFIED", "TERMINAL"],
        )

    def test_hash_chain_is_intact(self) -> None:
        ledger, m, _ = _driven_to_verified()
        self.assertTrue(ledger.verify_chain(m.mission_id))
        self.assertTrue(verify_receipt_chain(m.receipts, secret=b"s"))

    def test_illegal_transition_rejected(self) -> None:
        # verify before any effect is committed is not a legal edge
        clock = _Clock()
        ledger = ProofCarryingLedger(clock=clock)
        m = ledger.create("k", inputs={}, dependencies=None)
        ledger.pick_up(m.mission_id, "w1", m.revision)
        ledger.lease(m.mission_id, "w1", ttl=100.0, expected_revision=m.revision)
        ledger.start(m.mission_id, "w1", m.revision)
        with self.assertRaises(IllegalTransition):
            ledger.terminalize(m.mission_id, "w1", m.revision)  # STARTED -> TERMINAL illegal

    def test_stale_worker_cas_rejected(self) -> None:
        clock = _Clock()
        ledger = ProofCarryingLedger(clock=clock)
        m = ledger.create("k", inputs={}, dependencies=None)
        ledger.pick_up(m.mission_id, "w1", m.revision)  # revision now advanced
        with self.assertRaises(StaleTransition):
            ledger.lease(m.mission_id, "w1", ttl=100.0, expected_revision=0)  # stale revision 0

    def test_duplicate_idempotency_rejected(self) -> None:
        ledger = ProofCarryingLedger(clock=_Clock())
        ledger.create("same", inputs={"a": 1}, dependencies=None)
        with self.assertRaises(DuplicateMission):
            ledger.create("same", inputs={"a": 2}, dependencies=None)

    def test_failed_safe_is_terminal(self) -> None:
        ledger = ProofCarryingLedger(clock=_Clock())
        m = ledger.create("k", inputs={}, dependencies=None)
        ledger.pick_up(m.mission_id, "w1", m.revision)
        ledger.fail_safe(m.mission_id, "w1", m.revision, note="operator abort")
        self.assertEqual(m.state, "FAILED_SAFE")
        with self.assertRaises(IllegalTransition):
            ledger.fail_safe(m.mission_id, "w1", m.revision)

    def test_crash_reopen_replay_persistence(self) -> None:
        ledger, m, _ = _driven_to_verified()
        ledger.terminalize(m.mission_id, "w1", m.revision)
        exported = ledger.export_mission(m.mission_id)
        # deterministic round-trip through JSON, as a durable store would persist
        blob = json.dumps(exported, sort_keys=True)
        restored = json.loads(blob)
        reopened = reopen_receipts(restored)
        self.assertTrue(verify_receipt_chain(reopened, secret=b"s"))
        self.assertEqual(restored["state"], "TERMINAL")
        self.assertEqual(restored["head_hash"], m.head_hash())

    def test_expired_lease_rejected(self) -> None:
        clock = _Clock()
        ledger = ProofCarryingLedger(clock=clock)
        m = ledger.create("k", inputs={}, dependencies=None)
        ledger.pick_up(m.mission_id, "w1", m.revision)
        ledger.lease(m.mission_id, "w1", ttl=1.0, expected_revision=m.revision)
        # advance the clock beyond the lease TTL before starting
        for _ in range(5):
            clock()
        with self.assertRaises(ExpiredLease):
            ledger.start(m.mission_id, "w1", m.revision)

    def test_receipt_tamper_detected(self) -> None:
        ledger, m, _ = _driven_to_verified()
        # forge a receipt body without recomputing the chain hash
        tampered = list(m.receipts)
        tampered[3] = replace(tampered[3], note="silently altered")
        self.assertFalse(verify_receipt_chain(tampered, secret=b"s"))

    def test_verification_mismatch_fails_closed(self) -> None:
        clock = _Clock()
        ledger = ProofCarryingLedger(clock=clock)
        m = ledger.create("k", inputs={}, dependencies=None)
        ledger.pick_up(m.mission_id, "w1", m.revision)
        ledger.lease(m.mission_id, "w1", ttl=1000.0, expected_revision=m.revision)
        ledger.start(m.mission_id, "w1", m.revision)
        ledger.progress(m.mission_id, "w1", m.revision)
        ledger.commit_effect(m.mission_id, "w1", m.revision, output={"r": "actual"})
        with self.assertRaises(VerificationMismatch):
            ledger.verify(m.mission_id, "w1", m.revision, expected_output_sha256=evidence_hash({"r": "expected"}))
        self.assertEqual(m.state, "FAILED_SAFE")


class PcefContractTests(unittest.TestCase):
    def test_contract_lifecycle_matches_module(self) -> None:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "8x8.pcef.contract.v1")
        self.assertEqual(
            payload["lifecycle"],
            ["CREATED", "PICKED_UP", "LEASED", "STARTED", "PROGRESS",
             "EFFECT_COMMITTED", "VERIFIED", "TERMINAL"],
        )
        self.assertIn("FAILED_SAFE", payload["fail_closed_terminal"])

    def test_contract_rejects_process_exit_as_success(self) -> None:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["truth_boundary"]["process_exit_zero_means_verified"], False)
        self.assertEqual(payload["truth_boundary"]["private_runtime_binding"], "OWNER_RUNTIME_NOT_PUBLISHED")


if __name__ == "__main__":
    unittest.main()
