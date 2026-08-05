# MSG197 Council Vote Aggregation Contract V1

## Purpose

This contract turns independently produced council vote receipts into one deterministic quorum result without inventing identities, leases, signatures, votes or consensus.

## Inputs

- canonical session: `COUNCIL_SESSION.json`;
- canonical candidate ledger: `CANDIDATE_STATUS_LEDGER_V3.json`;
- zero or more vote JSON files conforming to `COUNCIL_VOTE.schema.json`;
- an explicit timezone-aware evaluation timestamp.

## Valid-vote gates

A vote counts only when all of the following are true:

1. the vote has exactly the governed top-level fields;
2. schema version and session ID match;
3. the input digest equals the session pin-set digest;
4. the agent ID is registered in the session;
5. identity status is `VERIFIED`;
6. the lease is `ACTIVE`, has an ID and expires after the evaluation time;
7. receipt status is `VALID_VOTE`;
8. output digest matches the canonical vote payload with `output_digest` set to `null`;
9. all thirteen candidates appear exactly once;
10. every decision is non-empty and confidence is between 0 and 1;
11. security veto entries are non-empty strings;
12. the agent has not already submitted another counted vote.

Rejected votes are retained in the aggregate with their source filename and exact rejection reason. They do not count toward quorum.

## Canonical output digest

A vote producer computes `output_digest` as SHA-256 over UTF-8 canonical JSON using:

- sorted object keys;
- compact separators `,` and `:`;
- Unicode preserved;
- `output_digest` temporarily set to `null`.

The aggregate itself receives an `aggregation_sha256` calculated before that field is inserted.

## Quorum and veto

- quorum is read from `COUNCIL_SESSION.json` and is currently four valid votes;
- one valid security veto blocks advancement even when quorum exists;
- absence of quorum always blocks advancement;
- a dashboard, advisory, comment, model response or unsigned file is not a vote.

## Disagreement preservation

For every candidate the aggregate records:

- every distinct decision;
- vote count for each decision;
- mean confidence for each decision;
- a majority decision only when one decision has more than half of valid votes.

Ties and pluralities remain `DISAGREEMENT_OR_INSUFFICIENT_VOTES` rather than being averaged into fictional consensus.

## Authority boundary

The aggregator:

- reads JSON files;
- writes one requested aggregate JSON file;
- performs no network calls;
- performs no signature creation;
- issues no leases;
- verifies no external identity provider;
- installs no candidate;
- changes no service, scheduler, database, credential, wallet or deployment.

Real identity and lease issuance remain owner/Hermes-controlled external prerequisites.

## Example

```bash
python3 scripts/aggregate_msg197_council_votes_v1.py \
  --votes-dir /path/to/verified-votes \
  --output /path/to/MSG197_COUNCIL_AGGREGATE.json \
  --now 2026-08-05T23:00:00Z
```

An empty directory produces a valid aggregate with zero votes, quorum false and advancement false.
