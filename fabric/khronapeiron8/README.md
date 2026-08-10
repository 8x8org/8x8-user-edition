# KHRONAPEIRON-8 / VERITAS V1

This directory is the executable, evidence-bounded implementation of the computational portion of the Complete 8x8 Handoff Dossier.

## What is implemented

- Exact chained integer calculations 1 through 7.
- Correct Calculation 8 as the sum of Calculations 1 through 7.
- Binary, hexadecimal, digital-root and modulo-256 derivations.
- `W = 01010111 = 87` as an explicit protocol anchor.
- A machine-readable eight-phase, eight-cell-per-phase contract (64 unique cells).
- Evidence classifications that prevent conceptual physics from being promoted to verified runtime truth.
- Deterministic canonical JSON and SHA-256 receipt generation.
- Regression tests for arithmetic, contract shape, legacy Calc-8 rejection, truth boundaries and the W anchor.
- A dedicated GitHub Actions VERITAS gate.

## Correct calculation chain

| Calc | Phase | Exact value |
|---|---|---:|
| 1 | CHRONOS | 8,888,888 |
| 2 | HELIOS | 7,901,225,876,544 |
| 3 | GEOS | 702,324,165,714,243,072 |
| 4 | MOLOS | 6,242,257,184,868,192,423,936 |
| 5 | COSMOS | 5,543,124,380,162,954,872,455,168 |
| 6 | TOPOS | 487,794,945,454,340,028,776,054,784 |
| 7 | LOGOS | 3,902,359,563,634,720,230,208,438,272 |
| 8 | VERITAS | **4,395,703,876,428,740,148,998,380,664** |

The previously supplied value `499,581,037,244,762,775,498,942,392` is preserved in `contract.v1.json` as a legacy value and explicitly marked **not** equal to the sum of calculations 1 through 7.

The corrected aggregate has digital root **8** and `mod 256 = 120`. The W anchor is therefore intentionally a protocol symbol, not an asserted consequence of an undefined horizontal/vertical parity transformation.

## Scientific/evidence boundary

The contract distinguishes source-supported research from extrapolation. Majorana 2, NIST's 2026 additional-signature round, INBL research, and the CMTEM/COE-HM proposal are recorded with bounded claims. None of those sources establishes infinite energy/storage, arbitrary matter or DNA rewriting, cosmological-constant control, multiverse navigation, absolute physical unhackability, retrocausal verification, or hyper-Turing oracle hardware.

Those dossier concepts remain preserved as conceptual architecture and research targets where appropriate. They are not deleted, but VERITAS refuses to label them empirically verified.

## Run

```bash
python3 fabric/khronapeiron8/veritas.py
python3 -m unittest fabric.khronapeiron8.test_veritas -v
```

A successful run means the **bounded software contract** passes every implemented invariant. It does not mean the entire 8x8 ecosystem, external world, physics, or future work has reached global 100% completeness.
