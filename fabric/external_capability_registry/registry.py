from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from enum import IntEnum
from typing import Iterable

ROOT = "fabric://8x8/core"

FAMILIES = (
    "CHRONOS", "HELIOS", "GEOS", "MOLOS",
    "COSMOS", "TOPOS", "LOGOS", "VERITAS",
)

class Coverage(IntEnum):
    UNKNOWN = 0
    ABSENT = 1
    DISCOVERED = 2
    MAPPED = 3
    PARTIAL = 4
    IMPLEMENTED = 5
    TESTED = 6
    DEPLOYED = 7
    OBSERVED = 8
    PARITY = 9
    SUPERIOR = 10

@dataclass(frozen=True)
class CapabilityRecord:
    source: str
    project: str
    revision: str
    capability: str
    capability_family: str
    canonical_cell: str
    license: str
    dependency: str
    existing_evidence: str
    coverage_state: str
    benchmark: str
    gap: str
    reuse_strategy: str
    security_boundary: str
    implementation_candidate: str
    test: str
    receipt: str
    freshness: str
    provenance_hash: str

    def validate(self) -> None:
        if self.capability_family not in FAMILIES:
            raise ValueError(f"unknown family: {self.capability_family}")
        row, col = self.canonical_cell.split(".")
        if not (1 <= int(row) <= 8 and 1 <= int(col) <= 8):
            raise ValueError(f"invalid canonical cell: {self.canonical_cell}")
        if self.coverage_state not in Coverage.__members__:
            raise ValueError(f"unknown coverage state: {self.coverage_state}")
        expected_row = FAMILIES.index(self.capability_family) + 1
        if int(row) != expected_row:
            raise ValueError("cell row does not match family")

    @property
    def score(self) -> int:
        return int(Coverage[self.coverage_state])


def normalize(records: Iterable[CapabilityRecord]) -> list[CapabilityRecord]:
    by_key: dict[tuple[str, str, str], CapabilityRecord] = {}
    for record in records:
        record.validate()
        key = (record.project.strip().lower(), record.capability.strip().lower(), record.canonical_cell)
        current = by_key.get(key)
        if current is None or record.score > current.score:
            by_key[key] = record
    return sorted(by_key.values(), key=lambda r: (r.canonical_cell, r.project.lower(), r.capability.lower()))


def metrics(records: Iterable[CapabilityRecord]) -> dict:
    normalized = normalize(records)
    denominator = len(normalized)
    parity = sum(1 for r in normalized if r.score >= Coverage.PARITY)
    superior = sum(1 for r in normalized if r.score >= Coverage.SUPERIOR)
    observed = sum(1 for r in normalized if r.score >= Coverage.OBSERVED)
    return {
        "root": ROOT,
        "denominator": denominator,
        "observed": observed,
        "parity": parity,
        "superior": superior,
        "coverage_C": 0.0 if denominator == 0 else parity / denominator,
        "frontier_F": 0.0 if denominator == 0 else superior / denominator,
        "w_state": denominator > 0 and parity == denominator and superior > 0,
        "global_100_claim_allowed": False,
    }


def canonical_payload(records: Iterable[CapabilityRecord]) -> dict:
    normalized = normalize(records)
    return {
        "schema": "8x8.one-fabric.external-capability-registry.v1",
        "root": ROOT,
        "truth_rule": "No open-world 100% claim without a closed denominator and receipts.",
        "records": [asdict(r) for r in normalized],
        "metrics": metrics(normalized),
    }


def receipt_sha256(records: Iterable[CapabilityRecord]) -> str:
    payload = json.dumps(canonical_payload(records), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def load(path: str) -> list[CapabilityRecord]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [CapabilityRecord(**item) for item in raw["records"]]


if __name__ == "__main__":
    import pathlib
    path = pathlib.Path(__file__).with_name("seed_registry.json")
    records = load(str(path))
    print(json.dumps(canonical_payload(records), indent=2, sort_keys=True))
    print("RECEIPT_SHA256=" + receipt_sha256(records))
