from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/council")
schema = json.loads((BASE / "COUNCIL_VOTE.schema.json").read_text())
advisory = json.loads((BASE / "CHATGPT_ADVISORY.json").read_text())
session = json.loads((BASE / "COUNCIL_SESSION.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_COUNCIL_001_RECEIPT.json").read_text())

EXPECTED_DIGEST = "ab40f0f1c010d862f38c34ec4efea5e18ff7c405d68231b82815342521a749e7"
assert schema["$id"].endswith("msg197-council-vote-v1.json")
assert advisory["input_digest"] == EXPECTED_DIGEST
assert advisory["participant"]["identity_status"] == "UNVERIFIED"
assert advisory["lease"]["status"] == "NOT_ISSUED"
assert advisory["receipt_status"] == "ADVISORY_ONLY"
assert advisory["output_digest"] is None
assert len(advisory["recommendations"]) == 13
assert len({item["candidate"] for item in advisory["recommendations"]}) == 13
assert session["input_pin_set_sha256"] == EXPECTED_DIGEST
assert session["coordinator"]["preferred"] == "Hermes"
assert len(session["participants"]) == 6
assert session["quorum"]["valid_votes"] == 0
assert session["quorum"]["reached"] is False
assert session["rules"]["missing_identity_cannot_vote"] is True
assert session["rules"]["missing_or_expired_lease_cannot_vote"] is True
assert receipt["valid_votes"] == 0
assert receipt["quorum_reached"] is False
assert receipt["council_complete"] is False

for line in (BASE / "receipts/MSG197_COUNCIL_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

print("MSG197-COUNCIL-001 framework validated; valid_votes=0 quorum=false")
