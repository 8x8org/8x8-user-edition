#!/usr/bin/env python3
"""Validate the generated CycloneDX SBOM and every recorded release-asset hash."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = {"bomFormat", "specVersion", "version", "serialNumber", "metadata", "components"}


def sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sbom_path = root / "sbom.cdx.json"
    if not sbom_path.is_file():
        print("ERROR: sbom.cdx.json missing; run scripts/generate-sbom.py first", file=sys.stderr)
        raise SystemExit(1)

    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    missing = REQUIRED_TOP_LEVEL - set(sbom)
    if missing:
        errors.append(f"missing top-level fields: {sorted(missing)}")
    if sbom.get("bomFormat") != "CycloneDX":
        errors.append("bomFormat must be CycloneDX")
    if sbom.get("specVersion") != "1.5":
        errors.append("specVersion must be 1.5")
    if not str(sbom.get("serialNumber", "")).startswith("urn:uuid:"):
        errors.append("serialNumber must be a urn:uuid")

    metadata_component = sbom.get("metadata", {}).get("component", {})
    if metadata_component.get("version") != "0.0.1":
        errors.append("metadata component version must remain 0.0.1")

    components = sbom.get("components", [])
    if not components:
        errors.append("SBOM must contain release components")

    for component in components:
        name = component.get("name")
        if not isinstance(name, str):
            errors.append("component without string name")
            continue
        path = root / name
        if not path.is_file():
            errors.append(f"{name}: file missing")
            continue
        recorded = None
        for item in component.get("hashes", []):
            if item.get("alg") == "SHA-256":
                recorded = item.get("content")
                break
        if not recorded:
            errors.append(f"{name}: SHA-256 missing")
            continue
        actual = sha256_hex(path)
        if actual != recorded:
            errors.append(f"{name}: SHA-256 mismatch")
        if component.get("version") != "0.0.1":
            errors.append(f"{name}: component version drifted from 0.0.1")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(f"SBOM_VALIDATION=PASS components={len(components)} product_version=0.0.1")


if __name__ == "__main__":
    main()
