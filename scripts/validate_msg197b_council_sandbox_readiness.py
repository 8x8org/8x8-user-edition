#!/usr/bin/env python3
"""Validate MSG197B contracts and optional generated static-probe receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities"
CENSUS = BASE / "REPOSITORY_CENSUS.json"
CONTRACTS = BASE / "CANDIDATE_CAPABILITY_CONTRACTS.json"
COUNCIL = BASE / "COUNCIL_DECISION_LEDGER.json"
POLICY = BASE / "UPSTREAM_STATIC_SCAN_POLICY.json"
PROBE = ROOT / "scripts" / "msg197_static_probe.py"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_CANDIDATES = 13


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_static_contracts() -> set[str]:
    required = [CENSUS, CONTRACTS, COUNCIL, POLICY, PROBE]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing MSG197B files: {missing}")

    census = load_json(CENSUS)
    records = census.get("repositories", [])
    if len(records) != EXPECTED_CANDIDATES:
        raise SystemExit(f"expected {EXPECTED_CANDIDATES} census records")
    candidates = {str(record.get("canonical")) for record in records}
    if len(candidates) != EXPECTED_CANDIDATES:
        raise SystemExit("census candidate identities are not unique")
    for record in records:
        if not SHA40.fullmatch(str(record.get("pinned_commit", ""))):
            raise SystemExit(f"invalid immutable pin: {record.get('canonical')}")

    contracts = load_json(CONTRACTS)
    if contracts.get("truth_state") != "DESIGN_CONTRACTS_IMPLEMENTED_NO_CANDIDATE_ACTIVATED":
        raise SystemExit("unexpected capability-contract truth state")
    contract_records = contracts.get("contracts", [])
    if len(contract_records) != EXPECTED_CANDIDATES:
        raise SystemExit("capability contracts must cover every candidate")
    if {item.get("candidate") for item in contract_records} != candidates:
        raise SystemExit("capability-contract candidates drift from census")
    if len({item.get("contract_id") for item in contract_records}) != EXPECTED_CANDIDATES:
        raise SystemExit("capability contract IDs are not unique")
    for item in contract_records:
        envelope = item.get("resource_envelope", {})
        if not envelope or any(not isinstance(value, int) or value <= 0 for value in envelope.values()):
            raise SystemExit(f"invalid resource envelope: {item.get('candidate')}")
        if not item.get("prohibited") or not item.get("promotion_gate") or not item.get("decision"):
            raise SystemExit(f"incomplete capability contract: {item.get('candidate')}")

    invariants = contracts.get("global_invariants", {})
    expected_true = {
        "one_candidate_per_implementation_branch",
        "immutable_upstream_commit_required",
        "external_code_never_becomes_policy",
        "undeclared_capability_is_denied",
        "submodules_enabled",
        "git_hooks_enabled",
        "automatic_production_merge",
    }
    for key in expected_true:
        if key not in invariants:
            raise SystemExit(f"missing global invariant: {key}")
    if invariants["one_candidate_per_implementation_branch"] is not True:
        raise SystemExit("one candidate per branch must remain true")
    if invariants["immutable_upstream_commit_required"] is not True:
        raise SystemExit("immutable source pin must remain required")
    if invariants["external_code_never_becomes_policy"] is not True:
        raise SystemExit("external code must remain subordinate")
    if invariants["undeclared_capability_is_denied"] is not True:
        raise SystemExit("undeclared capabilities must be denied")
    for false_key in (
        "private_data_in_research",
        "production_credentials_in_research",
        "wallet_or_financial_authority",
        "government_high_impact_authority",
        "unrestricted_shell",
        "unrestricted_network",
        "submodules_enabled",
        "git_hooks_enabled",
        "automatic_production_merge",
    ):
        if invariants.get(false_key) is not False:
            raise SystemExit(f"unsafe global invariant drift: {false_key}")

    council = load_json(COUNCIL)
    if council.get("truth_state") != "CHATGPT_ASSESSMENT_RECORDED_INDEPENDENT_COUNCIL_PENDING":
        raise SystemExit("council ledger must not claim unperformed independent review")
    if council.get("preferred_coordinator") != "HERMES":
        raise SystemExit("Hermes must remain preferred coordinator")
    roles = council.get("mandatory_council_roles", [])
    if "SECURITY_REVIEWER" not in roles or "OWNER_FLASH_TM8" not in roles:
        raise SystemExit("mandatory council roles are incomplete")
    council_candidates = council.get("candidates", [])
    if len(council_candidates) != EXPECTED_CANDIDATES:
        raise SystemExit("council ledger must cover every candidate")
    if {item.get("candidate") for item in council_candidates} != candidates:
        raise SystemExit("council candidates drift from census")
    decision_rule = council.get("decision_rule", {})
    if decision_rule.get("majority_vote_sufficient") is not False:
        raise SystemExit("majority vote cannot bypass mandatory gates")
    for key in ("security_veto_with_evidence_blocks", "license_block_blocks", "rollback_failure_blocks", "owner_gate_required_for_executable_canary", "owner_gate_required_for_merge_or_deploy"):
        if decision_rule.get(key) is not True:
            raise SystemExit(f"council gate drift: {key}")

    policy = load_json(POLICY)
    if policy.get("truth_state") != "STATIC_SCAN_POLICY_IMPLEMENTED":
        raise SystemExit("unexpected static scan policy state")
    source_rules = policy.get("source_rules", {})
    for key in ("exact_commit_only", "default_branch_is_not_authority", "partial_clone"):
        if source_rules.get(key) is not True:
            raise SystemExit(f"static source rule must be true: {key}")
    for key in ("submodules", "git_hooks", "lfs_smudge", "credential_prompt", "fetch_tags", "checkout_worktree", "source_retention_after_job"):
        if source_rules.get(key) is not False:
            raise SystemExit(f"static source rule must be false: {key}")
    prohibited = "\n".join(str(item).lower() for item in policy.get("prohibited_operations", []))
    for phrase in ("install candidate dependencies", "execute candidate scripts", "start candidate services", "enable submodules"):
        if phrase not in prohibited:
            raise SystemExit(f"static policy missing prohibition: {phrase}")

    probe_text = PROBE.read_text(encoding="utf-8")
    for forbidden in ("pip install", "npm install", "docker run", "shell=True", "checkout --recurse-submodules", "submodule update"):
        if forbidden in probe_text:
            raise SystemExit(f"probe contains forbidden operation: {forbidden}")
    required_markers = (
        '"--filter=blob:none"',
        '"--no-tags"',
        'worktree_checked_out": false',
        'candidate_code_executed": false',
        'dependencies_installed": false',
        'shutil.rmtree',
    )
    for marker in required_markers:
        if marker not in probe_text:
            raise SystemExit(f"probe missing safety marker: {marker}")

    print(
        "MSG197B_STATIC_VALIDATION_PASS "
        f"candidates={len(candidates)} contracts={len(contract_records)} "
        f"council_records={len(council_candidates)}"
    )
    return candidates


def validate_scan_outputs(scan_dir: Path, expected_candidates: set[str]) -> None:
    summary_path = scan_dir / "STATIC_PROBE_SUMMARY.json"
    sums_path = scan_dir / "SHA256SUMS.txt"
    if not summary_path.is_file() or not sums_path.is_file():
        raise SystemExit("scan output is missing summary or SHA256SUMS")
    summary = load_json(summary_path)
    if summary.get("truth_state") != "STATIC_METADATA_PROBES_ONLY":
        raise SystemExit("scan summary truth state drift")
    if summary.get("candidate_count") != EXPECTED_CANDIDATES:
        raise SystemExit("scan did not cover all candidates")
    if summary.get("pass_count") + summary.get("failure_count") != EXPECTED_CANDIDATES:
        raise SystemExit("scan pass/failure accounting drift")
    for key in ("candidate_code_executed", "dependencies_installed", "tests_executed"):
        if summary.get(key) is not False:
            raise SystemExit(f"scan falsely claims execution boundary: {key}")
    result_candidates = {item.get("candidate") for item in summary.get("results", [])}
    if result_candidates != expected_candidates:
        raise SystemExit("scan candidates drift from census")
    if not SHA64.fullmatch(str(summary.get("summary_payload_sha256", ""))):
        raise SystemExit("invalid scan summary payload digest")

    listed: dict[str, str] = {}
    for raw in sums_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        digest, relative = raw.split("  ", 1)
        if not SHA64.fullmatch(digest):
            raise SystemExit(f"invalid output digest: {relative}")
        if relative in listed:
            raise SystemExit(f"duplicate output hash path: {relative}")
        listed[relative] = digest
    json_files = sorted(scan_dir.glob("*.json"))
    expected_paths = {path.relative_to(ROOT).as_posix() for path in json_files}
    if set(listed) != expected_paths:
        raise SystemExit("output SHA256SUMS does not cover exactly the generated JSON files")
    for path in json_files:
        relative = path.relative_to(ROOT).as_posix()
        if sha256(path) != listed[relative]:
            raise SystemExit(f"generated output hash mismatch: {relative}")
    print(
        "MSG197B_SCAN_OUTPUT_VALIDATION_PASS "
        f"pass={summary['pass_count']} failed={summary['failure_count']} outputs={len(json_files)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-dir")
    args = parser.parse_args()
    candidates = validate_static_contracts()
    if args.scan_dir:
        validate_scan_outputs((ROOT / args.scan_dir).resolve(), candidates)


if __name__ == "__main__":
    main()
