# User-Owned Nodes, Resource Contribution, and BYOK

## Ownership boundary

An 8x8 user workspace is user-owned. Installation does not transfer ownership of the device, storage, credentials, data, network connection, compute capacity, mining hardware, or generated artifacts to 8x8.

The following permissions are separate and must never be bundled into one vague approval:

`installation ≠ account creation ≠ API credential use ≠ node enrollment ≠ CPU consent ≠ GPU consent ≠ storage consent ≠ bandwidth consent ≠ telemetry consent ≠ location consent ≠ remote-miner management ≠ rewards consent ≠ remote support`

Every optional permission is disabled by default, purpose-limited, time-bounded where practical, revocable, and receipted.

## BYOK credentials

Future user-provided API keys and credentials must follow these rules:

- secret values never enter public repositories, public logs, public analytics, reward calculations, or shared-node storage;
- the product stores secrets only in a user-controlled local vault or a vault explicitly selected by the user;
- interfaces use opaque secret references, not secret values;
- credentials are scoped to the minimum provider permissions;
- users can inspect, test, revoke, rotate, export, and delete credentials;
- provider requests identify which credential and permission scope will be used before execution;
- no credential is reused for another user, device, provider, mission, or reward process;
- diagnostic exports redact secret values and sensitive request contents;
- uninstall and account deletion clearly state what local and remote secret material remains.

## Resource classes

### CPU and GPU

Consent must define workload category, maximum utilization, schedule, pause conditions, thermal limits, battery rules, network rules, data classification, and maximum duration. Interactive user activity takes priority.

### Storage

Consent must define a hard byte quota, data class, encryption, replication, retention, deletion behavior, integrity checks, and whether data may leave the device. Private keys, credentials, health records, legal records, financial records, private messages, and unrelated personal files are never eligible contribution data.

### Bandwidth

Consent must define upload and download limits, metered-network behavior, roaming behavior, allowed destinations, protocol classes, and scheduling. The system must not operate as an undisclosed proxy, relay, exit node, scraper, or traffic origin.

### Remote mining hardware

A mobile or desktop client may eventually manage separately owned remote ASIC, GPU, or mining-rig infrastructure after explicit authorization. Management and monitoring are distinct from performing mining on the client device.

The mobile application must not mine cryptocurrency on the phone or tablet. Remote-miner management must include device allowlists, pool and wallet destination review, power and thermal safeguards, action budgets, kill switch, audit receipts, and separate approval for payout-address changes.

### GPS and precise location

Location is not a default contribution resource. Precise location may be used only for a service directly requested by the user, with separate affirmative consent, visible active-state indication where appropriate, retention limits, deletion controls, and no hidden sale or sharing.

Location consent must not be inferred from node enrollment, rewards enrollment, subscription, or another permission. Rewarding precise location requires an additional legal, privacy, safety, abuse, and discrimination review and is disabled in the current design.

## Workload admission

A future node accepts work only when all checks pass:

1. authenticated coordinator and signed workload manifest;
2. user consent covers the exact resource and workload class;
3. workload stays inside the declared data boundary;
4. capacity, thermal, battery, network, and schedule limits pass;
5. package integrity and provenance pass;
6. action is not denied by local policy;
7. kill switch is clear;
8. receipt sink is writable;
9. reward stage, if any, is explicitly disclosed;
10. local user can pause or revoke execution.

Unknown or ambiguous work fails closed.

## Receipts and metering

Each contribution interval should produce a hash-bound receipt containing:

- node pseudonymous identifier;
- consent identifier and version;
- workload identifier and code digest;
- coordinator identity;
- start and end timestamps;
- measured resource units;
- declared resource ceilings;
- completion, interruption, or rejection status;
- policy and integrity decisions;
- reward accounting stage;
- dispute window;
- receipt digest and previous-receipt link.

Receipts must not expose secret values, precise location, personal file paths, private message bodies, or unrelated device inventory.

## Safety controls

Required controls include:

- local pause and emergency stop;
- automatic stop on thermal, battery, storage, network, or policy thresholds;
- bounded retry and no duplicate external actions;
- per-workload sandboxing;
- resource quotas and scheduling;
- package signatures and provenance;
- anti-Sybil and abuse controls;
- dispute and correction process;
- user-readable contribution history;
- complete uninstall and revocation behavior.

## Current status

This document is a public design contract. It does not prove that node enrollment, distributed storage, compute contribution, remote mining management, GPS use, rewards, tokens, or coin settlement are deployed.
