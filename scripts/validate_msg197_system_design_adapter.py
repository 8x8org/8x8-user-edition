#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities" / "candidates" / "system-design-primer"
EXPECTED_REPO = "donnemartin/system-design-primer"
EXPECTED_COMMIT = "ae9bbd7b02d90b9866215de185217d33f39ab733"
EXPECTED_LICENSE = "CC-BY-4.0"
EXPECTED_RECORDS = 14
EXPECTED_FILES = {"README.md", "MANIFEST.json", "INDEX.json", "RECEIPT.json"}


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    require(BASE.is_dir(), "candidate directory missing")
    actual_files = {p.name for p in BASE.iterdir() if p.is_file()}
    require(actual_files == EXPECTED_FILES, f"unexpected candidate files: {sorted(actual_files)}")
    require(not any(p.is_symlink() for p in BASE.rglob("*")), "symlinks are forbidden")

    manifest = load("MANIFEST.json")
    index = load("INDEX.json")
    receipt = load("RECEIPT.json")

    upstream = manifest.get("upstream", {})
    require(upstream.get("repository") == EXPECTED_REPO, "repository identity drift")
    require(upstream.get("commit") == EXPECTED_COMMIT, "upstream commit drift")
    require(upstream.get("default_branch") == "master", "default branch drift")
    require(upstream.get("license") == EXPECTED_LICENSE, "license drift")
    require(manifest.get("classification") == "KNOWLEDGE_SOURCE", "classification drift")
    require(manifest.get("trust_class") == "UNTRUSTED_EXTERNAL_REFERENCE", "trust-class drift")
    require(manifest.get("truth_state") == "IMPLEMENTED_STATIC_KNOWLEDGE_ADAPTER_NOT_RUNTIME_INSTALLED", "truth-state drift")

    execution = manifest.get("execution", {})
    require(execution and all(value is False for value in execution.values()), "adapter gained execution authority")

    records = index.get("records", [])
    require(len(records) == EXPECTED_RECORDS, "record count drift")
    require(index.get("generated_from_commit") == EXPECTED_COMMIT, "index commit drift")
    policy = index.get("content_policy", {})
    require(policy.get("full_upstream_content_copied") is False, "upstream content must not be vendored")
    require(policy.get("citations_required") is True, "citations must remain required")
    require(policy.get("execution_prohibited") is True, "execution must remain prohibited")

    ids = set()
    topics = set()
    expected_prefix = f"https://github.com/{EXPECTED_REPO}/blob/{EXPECTED_COMMIT}/"
    for record in records:
        record_id = record.get("record_id")
        topic = record.get("topic")
        require(record_id not in ids, "duplicate record ID")
        require(topic not in topics, "duplicate topic")
        ids.add(record_id)
        topics.add(topic)
        require(record.get("source_commit") == EXPECTED_COMMIT, "record commit drift")
        require(record.get("license") == EXPECTED_LICENSE, "record license drift")
        require(record.get("trust_class") == "UNTRUSTED_EXTERNAL_REFERENCE", "record trust drift")
        require(record.get("executable") is False, "record became executable")
        source_url = record.get("source_url", "")
        parsed = urlparse(source_url)
        require(parsed.scheme == "https" and parsed.netloc == "github.com", "source URL host drift")
        require(source_url.startswith(expected_prefix), "source URL is not immutable")
        require(len(record.get("summary", "")) <= 220, "summary is unexpectedly large")

    expected_hashes = receipt.get("artifact_sha256", {})
    require(expected_hashes.get("MANIFEST.json") == sha256(BASE / "MANIFEST.json"), "manifest hash mismatch")
    require(expected_hashes.get("INDEX.json") == sha256(BASE / "INDEX.json"), "index hash mismatch")
    expected_pin = hashlib.sha256(f"{EXPECTED_REPO}@{EXPECTED_COMMIT}".encode("utf-8")).hexdigest()
    require(receipt.get("source_pin_sha256") == expected_pin, "source pin digest mismatch")
    require(receipt.get("status") == "PASS_STATIC_ADAPTER_SCOPE", "receipt status drift")
    assertions = receipt.get("assertions", {})
    require(assertions and all(value is False for value in assertions.values()), "receipt contains a false completion or mutation claim")

    forbidden_dirs = ["vendor", "node_modules", ".venv", "dist", "build"]
    require(not any((BASE / name).exists() for name in forbidden_dirs), "vendored or built dependency directory found")
    print("MSG197 system-design-primer static knowledge adapter: PASS")


if __name__ == "__main__":
    main()
