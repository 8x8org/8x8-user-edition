from __future__ import annotations

import json
from pathlib import Path

ledger = json.loads(Path("research/external-capabilities/CANDIDATE_STATUS_LEDGER_V3.json").read_text())
assert ledger["schema_version"] == "3.0.0"
assert ledger["mission_id"] == "MSG197_EXTERNAL_CAPABILITY_INTAKE_V1"
assert ledger["supersedes"] == "CANDIDATE_STATUS_LEDGER_V2.json"
summary = ledger["summary"]
assert summary["candidate_count"] == 13
assert summary["candidate_packets_merged"] == 13
assert summary["candidate_packet_open"] == 0
assert summary["candidate_packets_blocked_from_promotion"] == 1
assert summary["external_measured_benchmarks_complete"] == 1
assert summary["external_measured_benchmarks_required"] == 2
assert summary["third_party_candidates_installed_into_8x8"] == 0
assert summary["production_runtime_changes"] == 0
assert summary["phone_changes"] == 0
assert summary["real_council_votes"] == 0
assert summary["council_quorum"] is False

candidates = ledger["candidates"]
assert len(candidates) == 13
assert len({item["id"] for item in candidates}) == 13
assert len({item["repository"] for item in candidates}) == 13
for item in candidates:
    assert len(item["pin"]) == 40
    assert item["packet"].startswith("MERGED")
    assert item["runtime"].startswith("NOT_INSTALLED")

by_id = {item["id"]: item for item in candidates}
vision = by_id["MSG197-VISION-001"]
assert vision["packet"] == "MERGED_MEASURED_EXTERNAL_CANARY_PASS"
assert vision["runtime"] == "NOT_INSTALLED_ADAPTER_DESIGN_OWNER_GATED"
assert vision["evidence"]["merge_commit"] == "16b51f18603156b1d485c75b7c5ab9dd77067ff8"
assert vision["evidence"]["workflow_run_id"] == 31046645930
assert vision["evidence"]["known_vulnerabilities"] == 0
assert vision["evidence"]["cleanup"] == "PASS"
assert vision["evidence"]["deterministic_outputs"] == "PASS"

pdf = by_id["MSG197-PDF-001"]
assert pdf["runtime"] == "NOT_INSTALLED_SUPPLY_CHAIN_BLOCKED"
air = by_id["MSG197-AIRLLM-001"]
assert air["runtime"] == "NOT_INSTALLED_GPU_AND_MODEL_APPROVAL_REQUIRED"

remaining = {item["id"]: item for item in ledger["remaining_dependencies"]}
assert set(remaining) == {"AIRLLM_CUDA_BENCHMARK", "REAL_RESEARCH_COUNCIL"}
assert remaining["AIRLLM_CUDA_BENCHMARK"]["issue"] == 53
assert remaining["REAL_RESEARCH_COUNCIL"]["issue"] == 58
assert remaining["REAL_RESEARCH_COUNCIL"]["valid_votes"] == 0

assert ledger["council"]["preferred_coordinator"] == "Hermes"
assert ledger["council"]["valid_votes"] == 0
assert ledger["council"]["quorum_reached"] is False
assert all(value is False for value in ledger["absolute_boundaries"].values())
print("MSG197 ledger V3 validated; packets=13 benchmark=1/2 installed=0 votes=0")
