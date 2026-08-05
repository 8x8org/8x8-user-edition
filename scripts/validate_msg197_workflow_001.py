from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/superpowers")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_WORKFLOW_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-WORKFLOW-001"
assert manifest["source"]["commit"] == "44c9b2d6e889982ac18c27d05a19fefe335194e1"
assert manifest["decision"] == "ADOPT_BOUNDED_PATTERNS_REJECT_ORCHESTRATOR"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert "competing scheduler" in manifest["rejected_patterns"]
assert receipt["scheduler_changes"] == 0
assert receipt["authority_changes"] == 0

expected = {}
for line in (BASE / "receipts/MSG197_WORKFLOW_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    expected[name] = digest
for name, digest in expected.items():
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv"):
    assert not (BASE / forbidden).exists()
print("MSG197-WORKFLOW-001 static pattern review validated")
