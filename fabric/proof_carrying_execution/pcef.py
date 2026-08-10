#!/usr/bin/env python3
"""Proof-Carrying Execution Fabric (PCEF) V1 — public-safe reference.

This module is the public, least-authority reference model for the 8x8
execution law: a consequential action is not "done" because a process
returned 0. It is done only when a canonical lifecycle reaches ``VERIFIED``
and then ``TERMINAL`` while carrying its own tamper-evident evidence.

    process returned 0  !=  EFFECT_COMMITTED  !=  VERIFIED  !=  TERMINAL

What is verifiable here (software, deterministic, dependency-free):

* the canonical lifecycle and its legal transitions;
* compare-and-swap (CAS) revision guarding against stale workers;
* unique idempotency keys;
* explicit leases with deterministic expiry enforcement;
* SHA-256 canonical input / dependency / output evidence;
* an append-only, hash-chained receipt ledger with tamper detection;
* optional secret-backed HMAC integrity tags on each receipt;
* deterministic serialize -> reopen -> replay with chain re-verification.

What is deliberately OUT of this public reference (owner runtime only):
real process identifiers, device topology, filesystem paths, durable
on-device stores, credentials or lease material. Those live behind the
public information boundary and are never published here. Actors, holders
and runtime fingerprints are opaque caller-supplied strings in this model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
from typing import Callable, Optional

SCHEMA = "8x8.pcef.v1"
GENESIS_HASH = "0" * 64

# Canonical lifecycle. FAILED_SAFE is the explicit fail-closed terminal path.
STATES = (
    "CREATED",
    "PICKED_UP",
    "LEASED",
    "STARTED",
    "PROGRESS",
    "EFFECT_COMMITTED",
    "VERIFIED",
    "TERMINAL",
    "FAILED_SAFE",
)

TERMINAL_STATES = frozenset({"TERMINAL", "FAILED_SAFE"})

# Legal forward edges. Any non-terminal state may also fail closed.
_ALLOWED = {
    "CREATED": {"PICKED_UP"},
    "PICKED_UP": {"LEASED"},
    "LEASED": {"STARTED"},
    "STARTED": {"PROGRESS"},
    "PROGRESS": {"PROGRESS", "EFFECT_COMMITTED"},
    "EFFECT_COMMITTED": {"VERIFIED"},
    "VERIFIED": {"TERMINAL"},
    "TERMINAL": set(),
    "FAILED_SAFE": set(),
}

# Transitions that require a live lease held by the acting party.
_LEASE_GUARDED = frozenset({"STARTED", "PROGRESS", "EFFECT_COMMITTED", "VERIFIED"})


class PcefError(Exception):
    """Base class for fail-closed execution-law violations."""


class IllegalTransition(PcefError):
    pass


class StaleTransition(PcefError):
    """CAS revision mismatch — a stale or racing worker was rejected."""


class DuplicateMission(PcefError):
    """An idempotency key was reused."""


class ExpiredLease(PcefError):
    pass


class LeaseViolation(PcefError):
    pass


class VerificationMismatch(PcefError):
    """Committed output evidence did not equal the independently expected hash."""


class TamperDetected(PcefError):
    pass


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_hash(payload: object) -> str:
    """Stable SHA-256 over any canonically-JSON-serializable payload."""
    return sha256_hex(canonical_bytes(payload))


@dataclass(frozen=True)
class Receipt:
    seq: int
    mission_id: str
    from_state: Optional[str]
    to_state: str
    actor: str
    at: float
    input_sha256: Optional[str]
    output_sha256: Optional[str]
    note: str
    prev_hash: str
    this_hash: str
    integrity_tag: Optional[str]

    def body(self) -> dict:
        """The signed portion — everything except the derived hash fields."""
        return {
            "seq": self.seq,
            "mission_id": self.mission_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "actor": self.actor,
            "at": self.at,
            "input_sha256": self.input_sha256,
            "output_sha256": self.output_sha256,
            "note": self.note,
            "prev_hash": self.prev_hash,
        }

    def to_dict(self) -> dict:
        data = self.body()
        data["this_hash"] = self.this_hash
        data["integrity_tag"] = self.integrity_tag
        return data


@dataclass
class Mission:
    mission_id: str
    idempotency_key: str
    state: str
    revision: int
    input_sha256: str
    dependency_sha256: str
    lease_holder: Optional[str] = None
    lease_expires_at: Optional[float] = None
    committed_output_sha256: Optional[str] = None
    receipts: list = field(default_factory=list)

    def head_hash(self) -> str:
        return self.receipts[-1].this_hash if self.receipts else GENESIS_HASH


def _now_zero() -> float:
    return 0.0


class ProofCarryingLedger:
    """In-memory, public-safe reference engine for proof-carrying execution.

    A durable owner runtime binds this same protocol to real leases and a
    persistent store; that binding is not part of this public reference.
    """

    def __init__(self, clock: Callable[[], float] = _now_zero, secret: Optional[bytes] = None):
        self._clock = clock
        self._secret = secret
        self._missions: dict[str, Mission] = {}
        self._idempotency: dict[str, str] = {}
        self._counter = 0

    # -- construction -------------------------------------------------------
    def _next_id(self) -> str:
        self._counter += 1
        return f"m{self._counter:08d}"

    def create(
        self,
        idempotency_key: str,
        inputs: object,
        dependencies: object = None,
    ) -> Mission:
        if idempotency_key in self._idempotency:
            raise DuplicateMission(f"idempotency key already used: {idempotency_key}")
        mission_id = self._next_id()
        mission = Mission(
            mission_id=mission_id,
            idempotency_key=idempotency_key,
            state="CREATED",
            revision=0,
            input_sha256=evidence_hash(inputs),
            dependency_sha256=evidence_hash(dependencies),
        )
        self._idempotency[idempotency_key] = mission_id
        self._missions[mission_id] = mission
        self._append_receipt(
            mission,
            from_state=None,
            to_state="CREATED",
            actor="fabric",
            input_sha256=mission.input_sha256,
            output_sha256=None,
            note="mission created",
        )
        return mission

    def get(self, mission_id: str) -> Mission:
        return self._missions[mission_id]

    # -- receipts -----------------------------------------------------------
    def _append_receipt(
        self,
        mission: Mission,
        *,
        from_state: Optional[str],
        to_state: str,
        actor: str,
        input_sha256: Optional[str],
        output_sha256: Optional[str],
        note: str,
    ) -> Receipt:
        prev_hash = mission.head_hash()
        body = {
            "seq": len(mission.receipts),
            "mission_id": mission.mission_id,
            "from_state": from_state,
            "to_state": to_state,
            "actor": actor,
            "at": self._clock(),
            "input_sha256": input_sha256,
            "output_sha256": output_sha256,
            "note": note,
            "prev_hash": prev_hash,
        }
        this_hash = sha256_hex(canonical_bytes(body))
        integrity_tag = None
        if self._secret is not None:
            integrity_tag = hmac.new(self._secret, this_hash.encode("utf-8"), hashlib.sha256).hexdigest()
        receipt = Receipt(this_hash=this_hash, integrity_tag=integrity_tag, **body)
        mission.receipts.append(receipt)
        return receipt

    # -- lease --------------------------------------------------------------
    def lease(self, mission_id: str, holder: str, ttl: float, expected_revision: int) -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._transition(mission, "LEASED", actor=holder, note="lease acquired")
        mission.lease_holder = holder
        mission.lease_expires_at = self._clock() + ttl
        return mission

    def _require_live_lease(self, mission: Mission, holder: str) -> None:
        if mission.lease_holder != holder:
            raise LeaseViolation(
                f"actor {holder!r} does not hold the lease on {mission.mission_id}"
            )
        if mission.lease_expires_at is None or self._clock() > mission.lease_expires_at:
            raise ExpiredLease(f"lease expired on {mission.mission_id}")

    # -- generic guarded transition ----------------------------------------
    def _check_cas(self, mission: Mission, expected_revision: int) -> None:
        if mission.revision != expected_revision:
            raise StaleTransition(
                f"stale revision for {mission.mission_id}: "
                f"expected {expected_revision}, actual {mission.revision}"
            )

    def _transition(
        self,
        mission: Mission,
        to_state: str,
        *,
        actor: str,
        note: str,
        input_sha256: Optional[str] = None,
        output_sha256: Optional[str] = None,
    ) -> Receipt:
        from_state = mission.state
        if from_state in TERMINAL_STATES:
            raise IllegalTransition(f"{mission.mission_id} is terminal ({from_state})")
        if to_state != "FAILED_SAFE" and to_state not in _ALLOWED[from_state]:
            raise IllegalTransition(f"{from_state} -> {to_state} is not a legal edge")
        mission.state = to_state
        mission.revision += 1
        return self._append_receipt(
            mission,
            from_state=from_state,
            to_state=to_state,
            actor=actor,
            input_sha256=input_sha256,
            output_sha256=output_sha256,
            note=note,
        )

    def pick_up(self, mission_id: str, actor: str, expected_revision: int) -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._transition(mission, "PICKED_UP", actor=actor, note="autonomous ingress")
        return mission

    def start(self, mission_id: str, holder: str, expected_revision: int) -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._require_live_lease(mission, holder)
        self._transition(mission, "STARTED", actor=holder, note="execution started")
        return mission

    def progress(self, mission_id: str, holder: str, expected_revision: int, note: str = "progress") -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._require_live_lease(mission, holder)
        self._transition(mission, "PROGRESS", actor=holder, note=note)
        return mission

    def commit_effect(self, mission_id: str, holder: str, expected_revision: int, output: object) -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._require_live_lease(mission, holder)
        output_sha = evidence_hash(output)
        mission.committed_output_sha256 = output_sha
        self._transition(
            mission,
            "EFFECT_COMMITTED",
            actor=holder,
            note="external effect committed",
            output_sha256=output_sha,
        )
        return mission

    def verify(self, mission_id: str, holder: str, expected_revision: int, expected_output_sha256: str) -> Mission:
        """Promote to VERIFIED only if committed evidence equals an independently expected hash."""
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._require_live_lease(mission, holder)
        if mission.committed_output_sha256 != expected_output_sha256:
            # Verification is the point of the fabric: a mismatch fails closed.
            self._transition(
                mission,
                "FAILED_SAFE",
                actor=holder,
                note="verification mismatch — failed closed",
            )
            raise VerificationMismatch(
                f"{mission_id}: committed {mission.committed_output_sha256} "
                f"!= expected {expected_output_sha256}"
            )
        self._transition(
            mission,
            "VERIFIED",
            actor=holder,
            note="output evidence verified",
            output_sha256=expected_output_sha256,
        )
        return mission

    def terminalize(self, mission_id: str, holder: str, expected_revision: int) -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._require_live_lease(mission, holder)
        self._transition(mission, "TERMINAL", actor=holder, note="mission terminal")
        return mission

    def fail_safe(self, mission_id: str, actor: str, expected_revision: int, note: str = "failed closed") -> Mission:
        mission = self._missions[mission_id]
        self._check_cas(mission, expected_revision)
        self._transition(mission, "FAILED_SAFE", actor=actor, note=note)
        return mission

    # -- integrity, serialization, replay ----------------------------------
    def verify_chain(self, mission_id: str) -> bool:
        mission = self._missions[mission_id]
        return verify_receipt_chain(mission.receipts, secret=self._secret)

    def export_mission(self, mission_id: str) -> dict:
        mission = self._missions[mission_id]
        return {
            "schema": SCHEMA,
            "mission_id": mission.mission_id,
            "idempotency_key": mission.idempotency_key,
            "state": mission.state,
            "revision": mission.revision,
            "input_sha256": mission.input_sha256,
            "dependency_sha256": mission.dependency_sha256,
            "committed_output_sha256": mission.committed_output_sha256,
            "head_hash": mission.head_hash(),
            "receipts": [r.to_dict() for r in mission.receipts],
        }


def verify_receipt_chain(receipts: list, secret: Optional[bytes] = None) -> bool:
    """Recompute the hash chain (and optional HMAC tags); True only if intact."""
    prev = GENESIS_HASH
    for index, receipt in enumerate(receipts):
        if receipt.seq != index:
            return False
        if receipt.prev_hash != prev:
            return False
        recomputed = sha256_hex(canonical_bytes(receipt.body()))
        if not hmac.compare_digest(recomputed, receipt.this_hash):
            return False
        if secret is not None:
            expected_tag = hmac.new(secret, receipt.this_hash.encode("utf-8"), hashlib.sha256).hexdigest()
            if receipt.integrity_tag is None or not hmac.compare_digest(expected_tag, receipt.integrity_tag):
                return False
        prev = receipt.this_hash
    return True


def reopen_receipts(exported: dict) -> list:
    """Deterministically rebuild receipt objects from an exported mission."""
    rebuilt = []
    for row in exported["receipts"]:
        rebuilt.append(
            Receipt(
                seq=row["seq"],
                mission_id=row["mission_id"],
                from_state=row["from_state"],
                to_state=row["to_state"],
                actor=row["actor"],
                at=row["at"],
                input_sha256=row["input_sha256"],
                output_sha256=row["output_sha256"],
                note=row["note"],
                prev_hash=row["prev_hash"],
                this_hash=row["this_hash"],
                integrity_tag=row["integrity_tag"],
            )
        )
    return rebuilt


def _demo() -> dict:
    """A deterministic, self-verifying happy-path run for CI evidence."""
    ticks = iter(range(1, 10_000))
    clock = lambda: float(next(ticks))  # noqa: E731 - deterministic reference clock
    ledger = ProofCarryingLedger(clock=clock, secret=b"public-reference-secret")

    m = ledger.create("demo-1", inputs={"task": "publish public evidence"}, dependencies=["dep-a"])
    ledger.pick_up(m.mission_id, actor="worker-1", expected_revision=m.revision)
    ledger.lease(m.mission_id, holder="worker-1", ttl=1000.0, expected_revision=m.revision)
    ledger.start(m.mission_id, holder="worker-1", expected_revision=m.revision)
    ledger.progress(m.mission_id, holder="worker-1", expected_revision=m.revision)
    output = {"result": "ok", "artifact": "public-safe"}
    ledger.commit_effect(m.mission_id, holder="worker-1", expected_revision=m.revision, output=output)
    ledger.verify(
        m.mission_id,
        holder="worker-1",
        expected_revision=m.revision,
        expected_output_sha256=evidence_hash(output),
    )
    ledger.terminalize(m.mission_id, holder="worker-1", expected_revision=m.revision)

    exported = ledger.export_mission(m.mission_id)
    return {
        "schema": SCHEMA,
        "final_state": m.state,
        "revision": m.revision,
        "receipt_count": len(m.receipts),
        "chain_intact": ledger.verify_chain(m.mission_id),
        "reopened_chain_intact": verify_receipt_chain(
            reopen_receipts(exported), secret=b"public-reference-secret"
        ),
        "head_hash": m.head_hash(),
        "process_exit_equals_verified": False,
    }


def main() -> int:
    result = _demo()
    print(json.dumps(result, indent=2, sort_keys=True))
    ok = (
        result["final_state"] == "TERMINAL"
        and result["chain_intact"]
        and result["reopened_chain_intact"]
        and result["process_exit_equals_verified"] is False
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
