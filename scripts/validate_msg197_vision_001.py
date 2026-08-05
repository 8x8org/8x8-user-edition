from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/supervision")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
execution = json.loads((BASE / "CANARY_EXECUTION_MANIFEST.json").read_text())
summary = json.loads((BASE / "MEASURED_CANARY_SUMMARY.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_VISION_001_RECEIPT.json").read_text())

PIN = "bc20dd19fbc7b6cceaec447f1182346ca9158523"

assert manifest["mission_id"] == "MSG197-VISION-001"
assert manifest["source"]["commit"] == PIN
assert manifest["decision"] == "NARROW_SUBSET_ELIGIBLE_FOR_ADAPTER_DESIGN_NOT_RUNTIME_INSTALLATION"
assert manifest["installation_performed"] is False
assert manifest["runtime_installation_authorized"] is False
assert manifest["execution_performed"] is True
assert manifest["external_benchmark"]["functional"] == "PASS"
assert manifest["external_benchmark"]["supply_chain"] == "PASS"
assert manifest["external_benchmark"]["known_vulnerabilities"] == 0

assert execution["source_pin"] == PIN
assert execution["truth_state"] == "PASS_FUNCTIONAL_AND_SUPPLY_CHAIN_CANARY_NOT_INSTALLED"
assert execution["toolchain"] == {
    "pip": "26.1.2",
    "pip_audit": "2.7.3",
    "setuptools": "83.0.0",
    "wheel": "0.46.2",
}
assert execution["workflow"]["run_id"] == 31046645930

assert summary["source_pin"] == PIN
assert summary["truth_state"] == "PASS_MEASURED_EXTERNAL_CANARY_NOT_RUNTIME_INTEGRATION"
cross = summary["cross_lane"]
assert cross["functional_canary"] == "PASS"
assert cross["supply_chain_gate"] == "PASS_ZERO_KNOWN_VULNERABILITIES"
assert cross["cleanup"] == "PASS_BOTH_LANES"
assert cross["deterministic_output_hashes_match"] is True
assert cross["runtime_installation_authorized"] is False
assert cross["installed_candidate_count_on_8x8"] == 0

for lane in summary["lanes"].values():
    assert lane["audit_exit_code"] == 0
    assert lane["vulnerable_distribution_count"] == 0
    assert lane["backend"] == "fallback"
    assert lane["model_packages_present"] == []
    assert lane["cleanup_status"] == "PASS"

assert receipt["external_benchmark_executed"] is True
assert receipt["external_benchmark_result"] == "PASS_FUNCTIONAL_AND_SUPPLY_CHAIN_CANARY"
assert receipt["installed_candidate_count"] == 0
assert receipt["runtime_installation_authorized"] is False
assert receipt["model_downloads"] == 0
assert receipt["phone_changes"] == 0
assert receipt["production_changes"] == 0
assert receipt["private_media_used"] is False

paths = {
    "CANDIDATE_MANIFEST.json": BASE / "CANDIDATE_MANIFEST.json",
    "CANARY_EXECUTION_MANIFEST.json": BASE / "CANARY_EXECUTION_MANIFEST.json",
    "MEASURED_CANARY_SUMMARY.json": BASE / "MEASURED_CANARY_SUMMARY.json",
    "MEASURED_CANARY_REPORT.md": BASE / "MEASURED_CANARY_REPORT.md",
}
for line in (BASE / "receipts/MSG197_VISION_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256(paths[name].read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "models", ".venv", "venv", "node_modules", "wheelhouse", "canary-results"):
    assert not (BASE / forbidden).exists()

print("MSG197-VISION-001 measured external canary validated; installed=0")
