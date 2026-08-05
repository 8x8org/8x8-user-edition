# Verified council vote intake

Place only machine-verifiable MSG197 council vote JSON files in this directory on a candidate-specific evidence branch.

A file is not a valid vote merely because it exists here. The aggregator independently enforces:

- registered participant identity;
- `VERIFIED` identity state;
- active non-expired lease;
- exact shared input digest;
- valid output digest;
- all thirteen candidate recommendations;
- unique agent vote;
- valid receipt status.

No real vote files are committed on `main` yet. Current valid-vote count remains zero.

Do not commit:

- credentials or signing keys;
- private identity documents;
- API tokens;
- retrospective or fabricated leases;
- unsigned model prose presented as a vote;
- private runtime data;
- candidate binaries or model files.
