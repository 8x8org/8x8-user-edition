from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/nextjs")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_NEXT_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-NEXT-001"
assert manifest["source"]["commit"] == "ab7fc5fb581c396f0116f1a406da17ede2e15440"
assert manifest["source"]["pin_class"] == "MOVING_CANARY_NOT_PRODUCTION_SELECTION"
assert manifest["decision"] == "DEFER_STATIC_CLIENT_REMAINS_CANONICAL"
assert manifest["installation_performed"] is False
assert manifest["hosting_changed"] is False
assert manifest["server_runtime_added"] is False
assert receipt["packages_installed"] == 0
assert receipt["server_runtimes_added"] == 0
assert receipt["hosting_changes"] == 0

for line in (BASE / "receipts/MSG197_NEXT_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

assert not (BASE / "node_modules").exists()
print("MSG197-NEXT-001 client architecture decision validated")
