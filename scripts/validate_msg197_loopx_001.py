from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/loopx")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_LOOPX_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-LOOPX-001"
assert manifest["source"]["commit"] == "22b57a76e18736c31fe749867292f3feeb62f27b"
assert manifest["decision"] == "DEFER_RUNTIME_ADOPTION_EXTRACT_SELECTED_PROTOCOL_PATTERNS"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert "second local control plane" in manifest["rejected_surfaces"]
assert receipt["control_planes_added"] == 0
assert receipt["schedulers_added"] == 0

for line in (BASE / "receipts/MSG197_LOOPX_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv", ".loopx"):
    assert not (BASE / forbidden).exists()
print("MSG197-LOOPX-001 overlap review validated")
