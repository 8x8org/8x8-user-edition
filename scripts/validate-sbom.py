#!/usr/bin/env python3
"""Validate the CycloneDX SBOM produced by generate-sbom.py.

Run from the repository root or from the scripts/ sub-directory:

    python3 scripts/validate-sbom.py

Exits 0 on success, 1 on any structural or integrity failure.
"""

import hashlib
import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = {"bomFormat", "specVersion", "version", "serialNumber", "metadata", "components"}
REQUIRED_METADATA = {"timestamp", "component"}


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    root = here.parent if here.name == "scripts" else here

    sbom_path = root / "sbom.cdx.json"
    if not sbom_path.is_file():
        print("ERROR: sbom.cdx.json not found — run generate-sbom.py first", file=sys.stderr)
        sys.exit(1)

    sbom = json.loads(sbom_path.read_text(encoding="utf-8"))

    # Structural checks
    errors: list[str] = []

    missing_fields = REQUIRED_TOP_LEVEL - sbom.keys()
    if missing_fields:
        errors.append(f"SBOM missing required top-level fields: {sorted(missing_fields)}")

    if sbom.get("bomFormat") != "CycloneDX":
        errors.append(f"unexpected bomFormat: {sbom.get('bomFormat')!r}")

    if sbom.get("specVersion") not in {"1.4", "1.5", "1.6"}:
        errors.append(f"unsupported specVersion: {sbom.get('specVersion')!r}")

    metadata = sbom.get("metadata", {})
    missing_meta = REQUIRED_METADATA - metadata.keys()
    if missing_meta:
        errors.append(f"metadata missing fields: {sorted(missing_meta)}")

    serial = sbom.get("serialNumber", "")
    if not serial.startswith("urn:uuid:"):
        errors.append(f"serialNumber must start with 'urn:uuid:' — got: {serial!r}")

    components = sbom.get("components", [])
    if not components:
        errors.append("SBOM contains no components")

    # Per-component hash integrity checks
    for component in components:
        name = component.get("name", "<unknown>")
        p = root / name
        if not p.is_file():
            errors.append(f"{name}: referenced file not found on disk")
            continue

        hashes = {h["alg"]: h["content"] for h in component.get("hashes", [])}
        recorded = hashes.get("SHA-256", "")
        if not recorded:
            errors.append(f"{name}: no SHA-256 hash recorded in SBOM")
            continue

        actual = sha256_hex(p)
        if actual != recorded:
            errors.append(
                f"{name}: SHA-256 mismatch\n"
                f"  recorded={recorded}\n"
                f"  actual  ={actual}"
            )

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"SBOM_VALIDATION=PASS  components={len(components)}")


if __name__ == "__main__":
    main()
