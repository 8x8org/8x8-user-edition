from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/agent-skills")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_SKILLS_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-SKILLS-001"
assert manifest["source"]["commit"] == "bdf76c7c6b7b3b3e01bb15c9fdc42ac5351855c1"
assert manifest["classification"] == "ADAPTER_REFERENCE"
assert manifest["decision"] == "ADOPT_SELECTED_WORKFLOW_SCHEMAS_NOT_SKILL_EXECUTION"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert manifest["automatic_tool_registration"] is False
assert manifest["permission_policy"]["default"] == "DENY"
assert manifest["permission_policy"]["wallet"] == "DENY"
assert receipt["permissions_expanded"] is False
assert receipt["tools_registered"] == 0

expected = {}
for line in (BASE / "receipts/MSG197_SKILLS_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    expected[name] = digest
for name, digest in expected.items():
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv"):
    assert not (BASE / forbidden).exists()
print("MSG197-SKILLS-001 static capability mapping validated")
