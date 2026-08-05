from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/tencentdb-agent-memory")
manifest_path = BASE / "CANDIDATE_MANIFEST.json"
report_path = BASE / "COMPATIBILITY_REPORT.md"
receipt_path = BASE / "receipts/MSG197_MEMORY_001_RECEIPT.json"
sums_path = BASE / "receipts/MSG197_MEMORY_001_SHA256SUMS.txt"

manifest = json.loads(manifest_path.read_text())
receipt = json.loads(receipt_path.read_text())

assert manifest["mission_id"] == "MSG197-MEMORY-001"
assert manifest["source"]["commit"] == "b44c6db5f5b1a011eed645efb1949840f99f961a"
assert manifest["classification"] == "ADAPTER_REFERENCE"
assert manifest["decision"] == "ADOPT_SCHEMA_AND_ACL_PATTERNS_ONLY"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert manifest["production_data_used"] is False
assert manifest["adapter_contract"]["authority"] == "8x8 Memory Truth Graph remains canonical"
assert "cross_tenant_denial" in manifest["tests_required"]
assert receipt["installed_candidate_count"] == 0

expected: dict[str, str] = {}
for line in sums_path.read_text().splitlines():
    digest, name = line.split("  ", 1)
    expected[name] = digest

for name, digest in expected.items():
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv"):
    assert not (BASE / forbidden).exists()

assert report_path.read_text().startswith("# MSG197-MEMORY-001")
print("MSG197-MEMORY-001 static adapter design validated")
