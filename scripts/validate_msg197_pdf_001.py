from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/external-capabilities/candidates/pdf-inspector"
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_PDF_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-PDF-001"
assert manifest["source"]["commit"] == "12e9a655e36924564057464bf25494b8c027eb57"
assert manifest["decision"] == "APPROVE_EPHEMERAL_SYNTHETIC_CI_CANARY_ONLY"
assert manifest["installation_performed_on_8x8"] is False
assert manifest["resource_limits"]["container_memory_mib"] <= 512
assert manifest["resource_limits"]["container_cpus"] == 1
assert manifest["resource_limits"]["input_max_bytes"] == 1048576
assert receipt["installed_candidate_count_on_8x8"] == 0
assert receipt["private_documents_used"] is False
assert receipt["production_deployment"] is False

paths = {
    "CANDIDATE_MANIFEST.json": BASE / "CANDIDATE_MANIFEST.json",
    "SANDBOX_CONTRACT.md": BASE / "SANDBOX_CONTRACT.md",
    "generate_msg197_pdf_001_fixtures.py": ROOT / "scripts/canary/generate_msg197_pdf_001_fixtures.py",
}
for line in (BASE / "receipts/MSG197_PDF_001_SHA256SUMS.txt").read_text().splitlines():
    digest, relative = line.split("  ", 1)
    name = Path(relative).name
    actual = hashlib.sha256(paths[name].read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv", "target"):
    assert not (BASE / forbidden).exists()
print("MSG197-PDF-001 sandbox contract validated")
