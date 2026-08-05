from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/external-capabilities/candidates/supervision"
manifest = json.loads((BASE / "CANARY_EXECUTION_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_VISION_001_CANARY_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-VISION-001"
assert manifest["source_pin"] == "bc20dd19fbc7b6cceaec447f1182346ca9158523"
assert manifest["execution_scope"] == "DISPOSABLE_GITHUB_RUNNER_SYNTHETIC_ONLY"
assert manifest["model_downloads_authorized"] is False
assert manifest["private_media_authorized"] is False
assert manifest["phone_installation_authorized"] is False
assert manifest["production_deployment_authorized"] is False
assert manifest["network_execution_policy"] == "NONE"
assert manifest["python_matrix"] == ["3.11", "3.12"]
assert receipt["installed_candidate_count_on_8x8"] == 0
assert receipt["phone_changes"] == 0
assert receipt["production_changes"] == 0
assert receipt["truth_state"] == "CANARY_CONFIGURED_EXACT_HEAD_EVIDENCE_PENDING"

paths = {
    "CANARY_EXECUTION_MANIFEST.json": BASE / "CANARY_EXECUTION_MANIFEST.json",
    "CANARY_EXECUTION_CONTRACT.md": BASE / "CANARY_EXECUTION_CONTRACT.md",
    "run_msg197_vision_001.py": ROOT / "scripts/canary/run_msg197_vision_001.py",
}
for line in (BASE / "receipts/MSG197_VISION_001_CANARY_SHA256SUMS.txt").read_text().splitlines():
    digest, relative = line.split("  ", 1)
    name = Path(relative).name
    actual = hashlib.sha256(paths[name].read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "models", ".venv", "venv", "node_modules", "wheelhouse", "canary-results"):
    assert not (BASE / forbidden).exists()
print("MSG197-VISION-001 execution contract validated")
