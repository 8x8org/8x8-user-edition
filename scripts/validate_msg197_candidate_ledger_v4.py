from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "research" / "external-capabilities" / "CANDIDATE_STATUS_LEDGER_V4.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
require(ledger["schema_version"] == "4.0.0", "Unexpected ledger schema")
require(ledger["mission_id"] == "MSG197_EXTERNAL_CAPABILITY_INTAKE_V1", "Unexpected mission")
require(ledger["supersedes"] == "CANDIDATE_STATUS_LEDGER_V3.json", "V4 must supersede V3")

summary = ledger["summary"]
require(summary["candidate_count"] == 13, "Expected 13 candidates")
require(summary["candidate_packets_merged"] == 13, "Expected 13 merged packets")
require(summary["candidate_packet_open"] == 0, "Candidate packets remain open")
require(summary["candidate_packets_blocked_from_promotion"] == 1, "Expected one promotion-blocked candidate")
require(summary["external_measured_benchmarks_complete"] == 1, "Unexpected measured benchmark count")
require(summary["external_measured_benchmarks_required"] == 2, "Unexpected required benchmark count")
require(summary["disabled_adapter_contracts_merged"] == 1, "Expected one disabled adapter contract")
require(summary["third_party_candidates_installed_into_8x8"] == 0, "Third-party runtime installation is not authorized")
require(summary["production_runtime_changes"] == 0, "Production runtime changed unexpectedly")
require(summary["phone_changes"] == 0, "Phone changed unexpectedly")
require(summary["real_council_votes"] == 0, "Fabricated or unexpected council votes")
require(summary["council_quorum"] is False, "Council quorum must remain false")

candidates = ledger["candidates"]
require(len(candidates) == 13, "Expected exactly 13 candidate records")
require(len({item["id"] for item in candidates}) == 13, "Duplicate candidate IDs")
require(len({item["repository"] for item in candidates}) == 13, "Duplicate repositories")
require(len({item["pin"] for item in candidates}) == 13, "Duplicate upstream pins")
for item in candidates:
    require(len(item["pin"]) == 40 and all(char in "0123456789abcdef" for char in item["pin"]), f"Invalid pin: {item['id']}")
    require(item["packet"].startswith("MERGED"), f"Unmerged packet: {item['id']}")
    require(item["runtime"].startswith("NOT_INSTALLED"), f"Installed runtime claim: {item['id']}")

by_id = {item["id"]: item for item in candidates}
vision = by_id["MSG197-VISION-001"]
require(vision["packet"] == "MERGED_MEASURED_EXTERNAL_CANARY_AND_DISABLED_ADAPTER_CONTRACT", "Supervision packet drift")
require(vision["runtime"] == "NOT_INSTALLED_DISABLED_ADAPTER_CONTRACT_MERGED", "Supervision runtime boundary drift")
require(vision["evidence"]["measured_canary_merge_commit"] == "16b51f18603156b1d485c75b7c5ab9dd77067ff8", "Measured canary receipt drift")
require(vision["evidence"]["known_vulnerabilities"] == 0, "Supervision known vulnerability count changed")
require(vision["evidence"]["cleanup"] == "PASS", "Supervision cleanup failed")
require(vision["evidence"]["deterministic_outputs"] == "PASS", "Supervision determinism failed")

contract = vision["evidence"]["adapter_contract"]
require(contract["merge_commit"] == "a7d3be2dabce36b6cc994bbaab0d27ed5de5ae99", "Adapter merge receipt drift")
require(contract["source_head"] == "d219fc83bac02a39ff7c75757106a26968015c22", "Adapter source head drift")
require(contract["issue"] == 82, "Adapter issue drift")
require(contract["enabled"] is False, "Adapter must remain disabled")
require(contract["install_state"] == "NOT_INSTALLED", "Adapter installation claim detected")
require(contract["runtime_authority"] == "NONE", "Adapter runtime authority detected")
require(contract["production_ready"] is False, "Adapter must not claim production readiness")

pdf = by_id["MSG197-PDF-001"]
require(pdf["runtime"] == "NOT_INSTALLED_SUPPLY_CHAIN_BLOCKED", "PDF supply-chain block changed")
air = by_id["MSG197-AIRLLM-001"]
require(air["runtime"] == "NOT_INSTALLED_GPU_AND_MODEL_APPROVAL_REQUIRED", "AirLLM boundary changed")

remaining = {item["id"]: item for item in ledger["remaining_dependencies"]}
require(set(remaining) == {"AIRLLM_CUDA_BENCHMARK", "REAL_RESEARCH_COUNCIL"}, "Unexpected remaining dependency set")
require(remaining["AIRLLM_CUDA_BENCHMARK"]["issue"] == 53, "AirLLM issue drift")
require(remaining["REAL_RESEARCH_COUNCIL"]["issue"] == 58, "Council issue drift")
require(remaining["REAL_RESEARCH_COUNCIL"]["valid_votes"] == 0, "Unexpected real council vote")

require(ledger["council"]["preferred_coordinator"] == "Hermes", "Coordinator drift")
require(ledger["council"]["valid_votes"] == 0, "Council vote drift")
require(ledger["council"]["quorum_reached"] is False, "Council quorum drift")
require(all(value is False for value in ledger["absolute_boundaries"].values()), "Absolute boundary changed")

print("MSG197 ledger V4 validated; packets=13 benchmark=1/2 adapter_contracts=1 installed=0 votes=0")
