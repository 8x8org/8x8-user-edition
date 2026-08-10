# 8x8 One-Fabric External Capability Registry V1

Root: `fabric://8x8/core`

This module turns the W-parity model into a real, bounded software contract.

It provides the canonical mechanism to ingest one capability observation, normalize it, map it into the 8x8 capability lattice, calculate evidence-backed coverage, and expand the denominator without losing provenance.

## Core rule

`one observation -> normalized capability -> canonical cell -> evidence state -> parity/frontier measurement -> receipt`

A single observation may enrich many downstream views, but it never upgrades unrelated capabilities by declaration.

## Coverage states

`UNKNOWN`, `ABSENT`, `DISCOVERED`, `MAPPED`, `PARTIAL`, `IMPLEMENTED`, `TESTED`, `DEPLOYED`, `OBSERVED`, `PARITY`, `SUPERIOR`.

## 8 families

1. CHRONOS - mission runtime and orchestration
2. HELIOS - model and compute plane
3. GEOS - universal I/O and connector plane
4. MOLOS - sandboxed creation plane
5. COSMOS - knowledge and retrieval plane
6. TOPOS - trust, security and provenance plane
7. LOGOS - telemetry, evaluation and receipts
8. VERITAS - denominator, reconciliation and frontier measurement

## Truth boundary

`100/100` applies only to an explicitly closed denominator. Open-world coverage remains open until the external capability census is bounded and refreshed.
