from __future__ import annotations

import json
from pathlib import Path

path = Path("research/external-capabilities/CANDIDATE_STATUS_LEDGER_V2.json")
ledger = json.loads(path.read_text())

assert ledger["schema_version"] == "2.1.0"
assert ledger["mission_id"] == "MSG197_EXTERNAL_CAPABILITY_INTAKE_V1"
summary = ledger["summary"]
assert summary["candidate_count"] == 13
assert summary["candidate_packets_merged"] == 13
assert summary["candidate_packet_open"] == 0
assert summary["candidate_packets_blocked_from_promotion"] == 1
assert summary["third_party_candidates_installed_into_8x8"] == 0
assert summary["production_runtime_changes"] == 0
assert summary["phone_changes"] == 0
assert summary["real_council_votes"] == 0
assert summary["council_quorum"] is False

candidates = ledger["candidates"]
assert len(candidates) == 13
ids = {item["id"] for item in candidates}
repos = {item["repository"] for item in candidates}
assert len(ids) == 13
assert len(repos) == 13

by_id = {item["id"]: item for item in candidates}
assert by_id["MSG197-ADR-001"]["identity_correction"].startswith("ADR means Agentic AI Detection")
assert by_id["MSG197-ADR-001"]["decision"] == "ADOPT_TELEMETRY_SCHEMA_AND_ATTACK_TAXONOMY_ONLY"
assert by_id["MSG197-COMPUTER-001"]["identity_correction"].startswith("Preview Durable Object")
assert by_id["MSG197-COMPUTER-001"]["decision"] == "ADOPT_WORKSPACE_BOUNDARY_IDEAS_DEFER_ALL_EXECUTION"

pdf = by_id["MSG197-PDF-001"]
assert pdf["packet_state"] == "MERGED_PARSER_PASS_SUPPLY_CHAIN_BLOCKED"
assert pdf["merge_commit"] == "a10d0fc3065a755fc1b8de4c0b2fe59f3664b2d8"
assert pdf["runtime_state"] == "NOT_INSTALLED_SUPPLY_CHAIN_BLOCKED"
assert pdf["evidence"]["parser_canary"] == "PASS"
assert pdf["evidence"]["promotion_authorized"] is False
assert set(pdf["evidence"]["vulnerability_advisories"]) == {
    "RUSTSEC-2026-0176", "RUSTSEC-2026-0177"
}
assert pdf["evidence"]["unmaintained_warning"] == "RUSTSEC-2026-0192"

assert by_id["MSG197-AIRLLM-001"]["runtime_state"] == "NOT_INSTALLED_NO_MODEL_DOWNLOAD"
assert by_id["MSG197-VISION-001"]["runtime_state"] == "NOT_INSTALLED_NO_MODEL_NO_PRIVATE_MEDIA"
assert by_id["MSG197-LOOPX-001"]["runtime_state"] == "NOT_INSTALLED_NO_SECOND_CONTROL_PLANE"
assert by_id["MSG197-NEXT-001"]["runtime_state"] == "NOT_INSTALLED_NO_SERVER_RUNTIME"

for item in candidates:
    assert item["runtime_state"].startswith("NOT_INSTALLED")
    assert len(item["pin"]) == 40
    assert item["packet_state"].startswith("MERGED")

council = ledger["council"]
assert council["preferred_coordinator"] == "Hermes"
assert council["valid_votes"] == 0
assert council["quorum_required"] == 4
assert council["quorum_reached"] is False
assert council["chatgpt_submission"] == "ADVISORY_ONLY_NOT_COUNTED"

boundaries = ledger["absolute_boundaries"]
assert all(value is False for value in boundaries.values())
print("MSG197 candidate ledger V2 validated; merged=13 open=0 installed=0 blocked=1 votes=0")
