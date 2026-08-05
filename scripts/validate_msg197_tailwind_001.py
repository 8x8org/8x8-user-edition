from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/tailwindcss")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_TAILWIND_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-TAILWIND-001"
assert manifest["source"]["commit"] == "3524b4531097fff15962735cdacf56d2af425ead"
assert manifest["decision"] == "DEFER_NO_APPROVED_REQUIREMENT"
assert manifest["installation_performed"] is False
assert manifest["migration_performed"] is False
assert manifest["evaluation"]["current_trigger_met"] is False
assert receipt["packages_installed"] == 0
assert receipt["frontend_files_migrated"] == 0

for line in (BASE / "receipts/MSG197_TAILWIND_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

assert not (BASE / "node_modules").exists()
print("MSG197-TAILWIND-001 decision validated")
