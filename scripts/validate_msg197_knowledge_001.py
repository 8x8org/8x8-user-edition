#!/usr/bin/env python3
"""Validate MSG197-KNOWLEDGE-001 static knowledge artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities" / "candidates" / "system-design-primer"
PIN = "ae9bbd7b02d90b9866215de185217d33f39ab733"
EXPECTED_TOPICS = 18
FORBIDDEN = re.compile(
    r"(?:\b(?:pip|npm|pnpm|yarn)\s+install\b|"
    r"\b(?:curl|wget|ssh|scp|rsync)\b|"
    r"\bdocker\s+run\b|\bkubectl\b|\bterraform\s+apply\b|"
    r"\bos\.system\b|\bsubprocess\.|\bshell\s*=\s*True\b)",
    re.IGNORECASE,
)

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()

def main() -> None:
    manifest = load_json(BASE / "SOURCE_MANIFEST.json")
    index = load_json(BASE / "TOPIC_INDEX.json")
    receipt = load_json(BASE / "receipts" / "MSG197_KNOWLEDGE_001_RECEIPT.json")

    assert manifest["mission_id"] == "MSG197-KNOWLEDGE-001"
    assert manifest["source"]["commit"] == PIN
    assert manifest["source"]["license_spdx"] == "CC-BY-4.0"
    assert manifest["installation_performed"] is False
    assert manifest["execution_performed"] is False
    assert manifest["trust"]["class"] == "UNTRUSTED_EXTERNAL_REFERENCE"
    assert manifest["trust"]["executable_policy"] is False
    assert manifest["trust"]["code_samples_enabled"] is False

    assert index["source_commit"] == PIN
    assert index["topic_count"] == EXPECTED_TOPICS
    assert len(index["topics"]) == EXPECTED_TOPICS
    ids = [item["id"] for item in index["topics"]]
    assert len(ids) == len(set(ids))

    for item in index["topics"]:
        assert item["execution_allowed"] is False
        assert f"/blob/{PIN}/README.md#" in item["source_url"]
        assert item["source_anchor"] == f"#{item['id']}"

    governed = receipt["governed_artifacts"]
    assert len(governed) >= 6
    for record in governed:
        path = ROOT / record["path"]
        assert path.is_file(), record["path"]
        assert sha256(path) == record["sha256"], record["path"]

    for relative in [
        "README.md",
        "ATTRIBUTION_AND_EXCERPT_POLICY.md",
        "THREAT_AND_TRUST_BOUNDARY.md",
        "SOURCE_MANIFEST.json",
        "TOPIC_INDEX.json",
    ]:
        text = (BASE / relative).read_text(encoding="utf-8")
        assert FORBIDDEN.search(text) is None, relative

    assert receipt["truth_state"] == "PASS_STATIC_KNOWLEDGE_INDEX_ONLY"
    assert receipt["installed_candidate_count"] == 0
    assert receipt["runtime_changes"] is False
    print("MSG197-KNOWLEDGE-001 validation: PASS_STATIC_KNOWLEDGE_INDEX_ONLY")

if __name__ == "__main__":
    main()
