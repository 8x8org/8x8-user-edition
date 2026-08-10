#!/usr/bin/env python3
"""KHRONAPEIRON-8 VERITAS V1.

Evidence-first implementation of the computationally testable portion of the
8x8 handoff dossier. Physical/speculative claims are deliberately outside this
module and must never be promoted to VERIFIED without independent evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Iterable

W_ANCHOR = 0x57  # Uppercase ASCII W = 01010111. Protocol constant, not a derived proof.
SEED = 8_888_888
MULTIPLIERS = (888_888, 88_888, 8_888, 888, 88, 8)
PHASES = (
    "CHRONOS",
    "HELIOS",
    "GEOS",
    "MOLOS",
    "COSMOS",
    "TOPOS",
    "LOGOS",
    "VERITAS",
)


@dataclass(frozen=True)
class Calculation:
    index: int
    phase: str
    value: int
    binary: str
    hex: str
    digital_root: int
    mod256: int


def digital_root(value: int) -> int:
    if value < 0:
        raise ValueError("digital_root expects a non-negative integer")
    if value == 0:
        return 0
    return 1 + ((value - 1) % 9)


def chained_values(seed: int = SEED, multipliers: Iterable[int] = MULTIPLIERS) -> list[int]:
    values = [seed]
    for multiplier in multipliers:
        if multiplier <= 0:
            raise ValueError("multipliers must be positive integers")
        values.append(values[-1] * multiplier)
    return values


def grand_aggregate(values: Iterable[int]) -> int:
    values = list(values)
    if len(values) != 7:
        raise ValueError("VERITAS V1 requires exactly seven precursor calculations")
    return sum(values)


def calculations() -> list[Calculation]:
    values = chained_values()
    aggregate = grand_aggregate(values)
    all_values = values + [aggregate]
    return [
        Calculation(
            index=i,
            phase=PHASES[i - 1],
            value=value,
            binary=format(value, "b"),
            hex=format(value, "x"),
            digital_root=digital_root(value),
            mod256=value % 256,
        )
        for i, value in enumerate(all_values, start=1)
    ]


def canonical_payload() -> dict:
    rows = [asdict(row) for row in calculations()]
    aggregate = rows[-1]["value"]
    return {
        "schema": "8x8.khronapeiron8.veritas.v1",
        "seed": SEED,
        "multipliers": list(MULTIPLIERS),
        "w_anchor": {
            "role": "protocol_symbol",
            "decimal": W_ANCHOR,
            "binary": format(W_ANCHOR, "08b"),
            "ascii": chr(W_ANCHOR),
            "derived_from_arithmetic": False,
        },
        "calculations": rows,
        "invariants": {
            "precursor_count": 7,
            "matrix_rows": 8,
            "matrix_columns": 8,
            "matrix_cells": 64,
            "aggregate_is_sum_of_1_through_7": True,
            "aggregate_digital_root": digital_root(aggregate),
            "aggregate_mod256": aggregate % 256,
        },
        "truth_boundary": {
            "software_arithmetic": "VERIFIABLE",
            "w_anchor": "DEFINED_PROTOCOL_CONSTANT",
            "phononium_8": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
            "retrocausality": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
            "multiverse_branch_control": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
            "cosmological_constant_control": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
            "biosphere_neural_control": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
            "infinite_energy_or_storage": "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
        },
    }


def canonical_json_bytes() -> bytes:
    return (json.dumps(canonical_payload(), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def receipt_sha256() -> str:
    return hashlib.sha256(canonical_json_bytes()).hexdigest()


def verify() -> dict:
    rows = calculations()
    values = [row.value for row in rows]
    precursor = values[:7]
    aggregate = values[7]

    checks = {
        "calc1_seed": values[0] == SEED,
        "calc2_chain": values[1] == values[0] * 888_888,
        "calc3_chain": values[2] == values[1] * 88_888,
        "calc4_chain": values[3] == values[2] * 8_888,
        "calc5_chain": values[4] == values[3] * 888,
        "calc6_chain": values[5] == values[4] * 88,
        "calc7_chain": values[6] == values[5] * 8,
        "calc8_sum": aggregate == sum(precursor),
        "matrix_8x8": len(rows) == 8 and 8 * 8 == 64,
        "aggregate_digital_root_is_8": digital_root(aggregate) == 8,
        "w_anchor_binary": format(W_ANCHOR, "08b") == "01010111",
        "w_anchor_ascii": chr(W_ANCHOR) == "W",
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "aggregate": aggregate,
        "aggregate_hex": format(aggregate, "x"),
        "aggregate_binary": format(aggregate, "b"),
        "aggregate_mod256": aggregate % 256,
        "receipt_sha256": receipt_sha256(),
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
