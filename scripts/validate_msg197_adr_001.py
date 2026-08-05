from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path("research/external-capabilities/candidates/uber-adr")
manifest = json.loads((BASE / "CANDIDATE_MANIFEST.json").read_text())
receipt = json.loads((BASE / "receipts/MSG197_ADR_001_RECEIPT.json").read_text())

assert manifest["mission_id"] == "MSG197-ADR-001"
assert manifest["source"]["commit"] == "73873e18948be7a8637955eeef2f813a541692b8"
assert manifest["decision"] == "ADOPT_TELEMETRY_SCHEMA_AND_ATTACK_TAXONOMY_ONLY"
assert manifest["installation_performed"] is False
assert manifest["execution_performed"] is False
assert manifest["privacy_boundary"]["allowed_data"] == "SYNTHETIC_FIXTURES_ONLY"
assert manifest["privacy_boundary"]["credentials"] == "DENY"
assert "ADR Prevention" in manifest["open_source_scope"]["not_included"]
assert receipt["prevention_component_claimed"] is False
assert receipt["production_telemetry_used"] is False
assert receipt["provider_credentials_used"] is False

for line in (BASE / "receipts/MSG197_ADR_001_SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)
    assert receipt["artifacts"][name] == digest

for forbidden in ("vendor", "node_modules", ".venv", "Detection", "Sensor"):
    assert not (BASE / forbidden).exists()
print("MSG197-ADR-001 static security compatibility review validated")
