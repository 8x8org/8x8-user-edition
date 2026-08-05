from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/airllm")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
plan = json.loads((BASE / "EXTERNAL_CANARY_PLAN.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_AIRLLM_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-AIRLLM-001"
assert manifest["source"]["commit"] == "64a4e4fc3749aa7dc9bba4788f560ed0d7e74bd2"
assert manifest["decision"] == "EXTERNAL_CUDA_ONLY_PHONE_AND_ACTIVE_NODE_REJECTED"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert manifest["measured_external_benchmark"] is False
assert plan["status"] == "NOT_EXECUTED_EXTERNAL_NODE_REQUIRED"
assert plan["required_node"]["cuda"] == "12.x"
assert receipt["external_benchmark_executed"] is False
assert receipt["model_downloads"] == 0
assert receipt["phone_changes"] == 0

for line in (BASE / "receipts/MSG197_AIRLLM_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "models", ".venv", "huggingface", "node_modules"):
    assert not (BASE / forbidden).exists()
print("MSG197-AIRLLM-001 external-node feasibility plan validated")
