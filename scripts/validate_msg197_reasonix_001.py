from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/deepseek-reasonix")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_REASONIX_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-REASONIX-001"
assert manifest["source"]["commit"] == "77cf9aa7080fb48fec4b6f5ee5d3509748e68c50"
assert manifest["decision"] == "ADOPT_SELECTED_EXTENSION_PROTOCOL_IDEAS_DEFER_RUNTIME"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert "remote shell workflows" in manifest["rejected_surfaces"]
assert receipt["provider_credentials_used"] is False
assert receipt["remote_shell_enabled"] is False

for line in (BASE / "receipts/MSG197_REASONIX_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv"):
    assert not (BASE / forbidden).exists()
print("MSG197-REASONIX-001 static protocol comparison validated")
