#!/usr/bin/env python3
"""Fail closed when private operational or proprietary One-Fabric internals appear in public source.

The public User Edition is a product surface. It may publish user-facing UI,
product/API documentation, deliberately public schemas/verifiers, examples and
public evidence. It must not become a mirror of the OWNER_ROOT control plane,
private capability lattice, dormant-estate machinery, agent execution packets,
internal parity algorithms, private runtime topology or secret material.

Every tracked regular file is classified from its bytes. Strict UTF-8 text gets
semantic scanning; opaque/binary payloads get raw-byte scanning so credential
material cannot hide behind a misleading extension.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
EXCLUDED = {
    SELF,
    ROOT / "PUBLIC_INFORMATION_BOUNDARY.md",
    ROOT / ".github" / "workflows" / "validate-public-information-boundary.yml",
}

PATTERNS = {
    "private_android_path": re.compile(r"/data/data/", re.IGNORECASE),
    "private_root_path": re.compile(r"/root/", re.IGNORECASE),
    "private_runtime_directory": re.compile(r"(?:^|[\\/])\.hermes(?:[\\/]|$)", re.IGNORECASE),
    "private_state_database": re.compile(r"\bstate\.db\b", re.IGNORECASE),
    "private_repository_name": re.compile(r"\bhorbolsi/8x8-os-june2026\b", re.IGNORECASE),
    "private_mobile_runtime": re.compile(r"\b(?:Termux|Ubuntu\s+PRoot|Samsung\s+Galaxy)\b", re.IGNORECASE),
    "internal_coordinator_identity": re.compile(r"\bHermes(?:-led)?\b", re.IGNORECASE),
    "protected_deployment_identifier": re.compile(r"\bdpl_[A-Za-z0-9]{16,}\b"),
    "private_key_material": re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY"),
    "credential_like_token": re.compile(r"\b(?:gh[opsu]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b"),
    "private_drive_artifact_field": re.compile(r'"(?:vnext|rights_matrix)_drive_id"\s*:', re.IGNORECASE),
}

BYTE_PATTERNS = {
    "private_android_path": re.compile(rb"/data/data/", re.IGNORECASE),
    "private_root_path": re.compile(rb"/root/", re.IGNORECASE),
    "private_runtime_directory": re.compile(rb"(?:^|[\\/])\.hermes(?:[\\/]|$)", re.IGNORECASE),
    "private_state_database": re.compile(rb"\bstate\.db\b", re.IGNORECASE),
    "private_repository_name": re.compile(rb"\bhorbolsi/8x8-os-june2026\b", re.IGNORECASE),
    "protected_deployment_identifier": re.compile(rb"\bdpl_[A-Za-z0-9]{16,}\b"),
    "private_key_material": re.compile(rb"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY"),
    "credential_like_token": re.compile(rb"\b(?:gh[opsu]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b"),
    "private_drive_artifact_field": re.compile(rb'"(?:vnext|rights_matrix)_drive_id"\s*:', re.IGNORECASE),
}

# These implementation families belong to the private estate. Public consumers
# may use product/API projections of them, but not the private implementation,
# internal parity research or control-plane execution packets themselves.
FORBIDDEN_PATH_PREFIXES = (
    "research/external-capabilities/",
    "adapters/supervision/",
    "fabric/external_capability_registry/",
    "fabric/khronapeiron8/",
    "docs/agent_bridge/",
    "docs/control_plane/",
    "docs/round2/",
)
FORBIDDEN_EXACT_PATHS = {
    "tools/round2_v2_generate_validate.py",
    ".github/workflows/one-fabric-capability-registry.yml",
    ".github/workflows/one-fabric-external-benchmark.yml",
    ".github/workflows/khronapeiron8-veritas.yml",
    ".github/workflows/round2-v2-validate.yml",
    "docs/FIRST_BLINK_CONTEXT_BOOTSTRAP_V008.md",
    "docs/LEGACY_POWER_RECOVERY_MATRIX_0.0.1.md",
    "docs/MSG296E_FABRIC_MIRROR_V010.md",
    "docs/OMNIVERSAL_COMMAND_ATLAS_R2_RELEASE_0.0.1.md",
}
FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"^state/.*(?:run|operational)[-_]receipt.*\.json$", re.IGNORECASE),
    re.compile(r"^state/.*receipt.*(?:mission|runtime).*\.json$", re.IGNORECASE),
)


def tracked_paths() -> list[Path]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return [ROOT / name for name in names]


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def is_public_text_file(path: Path) -> bool:
    payload = path.read_bytes()
    if b"\x00" in payload:
        return False
    try:
        payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    return True


def iter_public_text_files(tracked: Sequence[Path]) -> list[Path]:
    return sorted(path for path in tracked if path.is_file() and path not in EXCLUDED and is_public_text_file(path))


def iter_public_binary_files(tracked: Sequence[Path]) -> list[Path]:
    return sorted(path for path in tracked if path.is_file() and path not in EXCLUDED and not is_public_text_file(path))


def path_policy_violations(tracked: Sequence[Path]) -> list[str]:
    rel_paths = [path.relative_to(ROOT).as_posix() for path in tracked]
    violations = [
        f"forbidden public path exists: {prefix}"
        for prefix in FORBIDDEN_PATH_PREFIXES
        if any(rel.startswith(prefix) for rel in rel_paths)
    ]
    violations.extend(f"forbidden private implementation path exists: {rel}" for rel in rel_paths if rel in FORBIDDEN_EXACT_PATHS)
    violations.extend(
        f"operational receipt path forbidden in public state: {rel}"
        for rel in rel_paths
        if any(pattern.fullmatch(rel) for pattern in FORBIDDEN_PATH_PATTERNS)
    )
    return violations


def content_policy_violations(files: Sequence[Path]) -> list[str]:
    violations: list[str] = []
    for path in files:
        rel = display_path(path)
        payload = path.read_bytes()
        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            violations.append(f"classification_drift_non_utf8_text: {rel}")
            continue
        violations.extend(f"{label}: {rel}" for label, pattern in PATTERNS.items() if pattern.search(text))
    return violations


def binary_content_policy_violations(files: Sequence[Path]) -> list[str]:
    violations: list[str] = []
    for path in files:
        rel = display_path(path)
        payload = path.read_bytes()
        violations.extend(f"binary_{label}: {rel}" for label, pattern in BYTE_PATTERNS.items() if pattern.search(payload))
    return violations


def main() -> int:
    tracked = tracked_paths()
    text_files = iter_public_text_files(tracked)
    binary_files = iter_public_binary_files(tracked)
    scanned_files = set(text_files) | set(binary_files)
    expected_files = {path for path in tracked if path.is_file() and path not in EXCLUDED}
    violations = path_policy_violations(tracked) + content_policy_violations(text_files) + binary_content_policy_violations(binary_files)
    if scanned_files != expected_files:
        missing = sorted(display_path(path) for path in expected_files - scanned_files)
        duplicate = sorted(display_path(path) for path in set(text_files) & set(binary_files))
        violations.extend(f"unclassified_tracked_artifact: {path}" for path in missing)
        violations.extend(f"multiply_classified_tracked_artifact: {path}" for path in duplicate)

    if violations:
        print("PUBLIC_INFORMATION_BOUNDARY=FAIL")
        for item in violations:
            print(f"- {item}")
        return 1

    print(
        "PUBLIC_INFORMATION_BOUNDARY=PASS "
        f"tracked={len(tracked)} text={len(text_files)} binary={len(binary_files)} "
        f"scanned={len(scanned_files)} expected={len(expected_files)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
