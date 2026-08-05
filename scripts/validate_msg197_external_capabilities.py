#!/usr/bin/env python3
"""Validate MSG197 external-capability intake without network or side effects."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities"
ALLOWED_CLASSES = {
    "KNOWLEDGE_SOURCE",
    "OPTIONAL_PLUGIN",
    "ADAPTER_REFERENCE",
    "SANDBOX_EXPERIMENT",
    "UI_DEPENDENCY",
    "REJECT_OR_DEFER",
}
REQUIRED = [
    BASE / "README.md",
    BASE / "REPOSITORY_CENSUS.json",
    BASE / "EVALUATION_MATRIX.csv",
    BASE / "COUNCIL_REPORT.md",
    BASE / "THREAT_MODEL.md",
    BASE / "LICENSE_AND_SBOM_REPORT.md",
    BASE / "INTEGRATION_BACKLOG.json",
    BASE / "ROLLBACK_AND_UNINSTALL_PLAN.md",
    BASE / "ARCHITECTURE_DECISIONS" / "ADR-001-external-code-remains-subordinate.md",
    BASE / "ARCHITECTURE_DECISIONS" / "ADR-002-knowledge-is-not-executable-policy.md",
    BASE / "ARCHITECTURE_DECISIONS" / "ADR-003-computer-use-sandbox.md",
    BASE / "receipts" / "MSG197_ARTIFACT_SHA256SUMS.txt",
    BASE / "receipts" / "MSG197_INTAKE_RECEIPT.json",
]
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash_manifest(path: Path) -> int:
    count = 0
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        digest, relative = raw.split("  ", 1)
        if not SHA64.fullmatch(digest):
            raise SystemExit(f"invalid SHA-256 digest for {relative}")
        if relative in seen:
            raise SystemExit(f"duplicate hash path: {relative}")
        seen.add(relative)
        target = ROOT / relative
        if not target.is_file():
            raise SystemExit(f"hash target missing: {relative}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            raise SystemExit(f"hash mismatch: {relative}")
        count += 1
    if count < 11:
        raise SystemExit("artifact hash manifest is incomplete")
    return count


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
    if missing:
        raise SystemExit(f"required MSG197 files missing: {missing}")

    census = load_json(BASE / "REPOSITORY_CENSUS.json")
    records = census.get("repositories", [])
    if len(records) != 13:
        raise SystemExit(f"expected 13 repositories, found {len(records)}")
    if census.get("installation_performed") is not False:
        raise SystemExit("intake must not claim installation")
    if census.get("truth_state") != "UPSTREAM_CENSUS_COMPLETE_STATIC_RESEARCH_ONLY":
        raise SystemExit("unexpected census truth state")

    canonical = [record.get("canonical") for record in records]
    if len(set(canonical)) != 13:
        raise SystemExit("canonical repository identities are not unique")
    if "huangruiteng/loopx" not in canonical or "uber/ADR" not in canonical:
        raise SystemExit("known repository casing corrections are missing")

    for record in records:
        if record.get("primary_classification") not in ALLOWED_CLASSES:
            raise SystemExit(f"invalid classification: {record.get('canonical')}")
        if not SHA40.fullmatch(str(record.get("pinned_commit", ""))):
            raise SystemExit(f"invalid commit pin: {record.get('canonical')}")
        license_record = record.get("license", {})
        if not license_record.get("spdx") or not license_record.get("path"):
            raise SystemExit(f"missing license evidence: {record.get('canonical')}")
        if not SHA40.fullmatch(str(license_record.get("blob_sha", ""))):
            raise SystemExit(f"invalid license blob: {record.get('canonical')}")
        if record.get("archived") is not False:
            raise SystemExit(f"unexpected archived candidate: {record.get('canonical')}")

    boundaries = census.get("absolute_boundaries", {})
    if not boundaries or any(value is not False for value in boundaries.values()):
        raise SystemExit("all intake mutation boundaries must remain false")

    backlog = load_json(BASE / "INTEGRATION_BACKLOG.json")
    items = backlog.get("items", [])
    if len(items) != 13:
        raise SystemExit(f"expected 13 backlog items, found {len(items)}")
    backlog_candidates = {item.get("candidate") for item in items}
    if backlog_candidates != set(canonical):
        raise SystemExit("backlog candidates do not match census")
    if backlog.get("truth_state") != "PLANNED_CANDIDATE_WORK_NO_INSTALLATION":
        raise SystemExit("backlog must remain plan-only")

    with (BASE / "EVALUATION_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 13:
        raise SystemExit(f"expected 13 evaluation rows, found {len(rows)}")
    if {row["repository"] for row in rows} != set(canonical):
        raise SystemExit("evaluation matrix candidates do not match census")
    if any(row["classification"] not in ALLOWED_CLASSES for row in rows):
        raise SystemExit("evaluation matrix contains an invalid classification")

    hash_count = verify_hash_manifest(BASE / "receipts" / "MSG197_ARTIFACT_SHA256SUMS.txt")
    receipt = load_json(BASE / "receipts" / "MSG197_INTAKE_RECEIPT.json")
    if receipt.get("status") != "PASS_STATIC_INTAKE_ONLY":
        raise SystemExit("unexpected intake receipt status")
    if receipt.get("installed_candidate_count") != 0:
        raise SystemExit("receipt falsely claims candidate installation")
    if receipt.get("candidate_count") != 13:
        raise SystemExit("receipt candidate count drift")
    if receipt.get("artifact_hash_count") != hash_count:
        raise SystemExit("receipt artifact hash count drift")
    if not SHA64.fullmatch(str(receipt.get("upstream_pin_set_sha256", ""))):
        raise SystemExit("receipt upstream pin-set digest is invalid")

    print(
        "MSG197_VALIDATION_PASS "
        f"candidates={len(records)} matrix_rows={len(rows)} "
        f"backlog_items={len(items)} artifact_hashes={hash_count} installed=0"
    )


if __name__ == "__main__":
    main()
