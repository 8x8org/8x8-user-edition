# MSG197-MEMORY-001 Compatibility Report

## Verdict

`ADOPT_SCHEMA_AND_ACL_PATTERNS_ONLY`

TencentDB Agent Memory contains useful ideas for portable memory assets, reviewed sharing, ownership, versioning, role-based visibility, skills, wiki structures and code graphs. It must not replace the 8x8 Memory Truth Graph, owner authority, identity registry, retention policy or receipt system.

## Evidence observed

The pinned README describes three cooperating services, `memory-core`, `memory-hub` and `proxy`, a human-facing panel, automatic extraction of chat memory and skills, Wiki and CodeGraph assets, team and agent loadouts, and `private`, `team` and restricted ACL visibility. It also requires modern Node, LLM parameters and a multi-service deployment.

## 8x8-native boundary

The adapter is a proposal layer only. It may list or transform synthetic memory assets, but every import, export, deletion, expiry or sharing change must pass the 8x8 policy engine and produce a receipt. The adapter cannot write identity, policy or canonical memory truth directly.

## Required synthetic canary

The future canary must prove cross-tenant denial, expiry filtering, hard-delete cleanup, export round-trip integrity, provenance preservation and denial of authority escalation. It must use synthetic records only.

## Decision

Static adapter design is complete. Runtime installation, database migration, private-data ingestion and production deployment remain prohibited until a separate owner-approved canary produces dependency, vulnerability, latency, storage, deletion and uninstall receipts.
