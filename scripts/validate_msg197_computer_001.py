from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/cloudflare-computer")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_COMPUTER_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-COMPUTER-001"
assert manifest["source"]["commit"] == "76d9e75c5688713b656bce85540d9e0071cece8b"
assert manifest["decision"] == "ADOPT_WORKSPACE_BOUNDARY_IDEAS_DEFER_ALL_EXECUTION"
assert manifest["preview_status"] == "UPSTREAM_PREVIEW_ONLY_NOT_PRODUCTION"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert manifest["adapter_contract"]["default_backend"] == "NONE"
assert manifest["adapter_contract"]["runtime_exec"] == "DENY"
assert all(item["allowed"] is False for item in manifest["runtime_backends"])
assert receipt["cloudflare_resources_created"] == 0
assert receipt["runtime_backends_enabled"] == 0
assert receipt["network_execution_performed"] is False

for line in (BASE / "receipts/MSG197_COMPUTER_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv", "wrangler.toml"):
    assert not (BASE / forbidden).exists()
print("MSG197-COMPUTER-001 static workspace safety review validated")
