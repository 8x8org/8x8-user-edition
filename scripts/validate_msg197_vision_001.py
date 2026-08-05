from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/supervision")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
plan = json.loads((BASE / "NO_MODEL_CANARY_PLAN.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_VISION_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-VISION-001"
assert manifest["source"]["commit"] == "bc20dd19fbc7b6cceaec447f1182346ca9158523"
assert manifest["decision"] == "NARROW_SUBSET_EXTERNAL_NODE_ONLY"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert "model downloads" in manifest["excluded_first_pass"]
assert "camera or microphone access" in manifest["excluded_first_pass"]
assert plan["status"] == "NOT_EXECUTED_EXTERNAL_NODE_REQUIRED"
assert receipt["external_benchmark_executed"] is False
assert receipt["model_downloads"] == 0
assert receipt["phone_changes"] == 0

for line in (BASE / "receipts/MSG197_VISION_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "models", ".venv", "venv", "node_modules"):
    assert not (BASE / forbidden).exists()
print("MSG197-VISION-001 external-node plan validated")
