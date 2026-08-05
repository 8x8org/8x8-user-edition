#!/usr/bin/env python3
"""Fail closed when private operational topology appears in public source."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
EXCLUDED = {
    SELF,
    ROOT / "PUBLIC_INFORMATION_BOUNDARY.md",
    ROOT / ".github" / "workflows" / "validate-public-information-boundary.yml",
}
TEXT_SUFFIXES = {
    ".css", ".csv", ".html", ".js", ".json", ".md", ".mjs", ".py",
    ".svg", ".txt", ".webmanifest", ".yaml", ".yml",
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
    "credential_like_token": re.compile(r"\b(?:gh[opsu]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{20,})\b"),
}

FORBIDDEN_PATH_PREFIXES = (
    "research/external-capabilities/",
    "adapters/supervision/",
)


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return [ROOT / name for name in names]


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in tracked_paths():
        if not path.is_file() or path in EXCLUDED:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name == "LICENSE":
            files.append(path)
    return sorted(files)


def main() -> int:
    violations: list[str] = []
    files = iter_public_text_files()

    for prefix in FORBIDDEN_PATH_PREFIXES:
        if any(path.relative_to(ROOT).as_posix().startswith(prefix) for path in tracked_paths()):
            violations.append(f"forbidden public path exists: {prefix}")

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(f"non-UTF-8 public text file: {rel}")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                violations.append(f"{label}: {rel}")

    if violations:
        print("PUBLIC_INFORMATION_BOUNDARY=FAIL")
        for item in violations:
            print(f"- {item}")
        return 1

    print(f"PUBLIC_INFORMATION_BOUNDARY=PASS files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
