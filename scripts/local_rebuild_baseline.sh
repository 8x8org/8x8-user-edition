#!/usr/bin/env bash
set -Eeuo pipefail

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
STATE_ROOT="${EIGHTX8_STATE_ROOT:-/root/.8x8-control-fabric}"
RELAY_ROOT="${EIGHTX8_RELAY_ROOT:-/root/8x8-flashpoint-relay}"
OS_ROOT="${EIGHTX8_OS_ROOT:-/root/8x8-os}"
OUTPUT_ROOT="${EIGHTX8_BASELINE_OUTPUT:-/root/.8x8-competition/baselines}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="$OUTPUT_ROOT/$STAMP"
RECEIPT="$OUTPUT_DIR/LOCAL_REBUILD_BASELINE.json"

umask 077
mkdir -p "$OUTPUT_DIR"

python3 - "$PREFIX" "$STATE_ROOT" "$RELAY_ROOT" "$OS_ROOT" "$RECEIPT" <<'PY'
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

prefix = pathlib.Path(sys.argv[1])
state_root = pathlib.Path(sys.argv[2])
relay_root = pathlib.Path(sys.argv[3])
os_root = pathlib.Path(sys.argv[4])
receipt_path = pathlib.Path(sys.argv[5])

surfaces = [
    {"id": "8x8-studio", "url": "http://127.0.0.1:8085/"},
    {"id": "8x8-main", "url": "http://127.0.0.1:8086/"},
    {"id": "readonly-dashboard", "url": "http://127.0.0.1:8099/"},
    {"id": "flash-360", "url": "http://127.0.0.1:8360/"},
    {"id": "control-plane", "url": "http://127.0.0.1:9120/"},
    {"id": "frontend", "url": "http://127.0.0.1:3000/"},
]


def run(args: list[str], timeout: int = 8) -> dict:
    try:
        completed = subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
        return {
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr_class": "present" if completed.stderr.strip() else None,
        }
    except FileNotFoundError:
        return {"available": False, "returncode": None, "stdout": "", "stderr_class": "FileNotFoundError"}
    except subprocess.TimeoutExpired:
        return {"available": True, "returncode": None, "stdout": "", "stderr_class": "TimeoutExpired"}


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_surface(item: dict) -> dict:
    record = {**item, "reachable": False, "status_code": None, "error_class": None}
    request = urllib.request.Request(item["url"], headers={"User-Agent": "8x8-local-rebuild-baseline/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            response.read(1024)
            record["reachable"] = True
            record["status_code"] = int(getattr(response, "status", 200))
    except urllib.error.HTTPError as exc:
        record["reachable"] = True
        record["status_code"] = int(exc.code)
        record["error_class"] = "HTTPError"
    except Exception as exc:
        record["error_class"] = type(exc).__name__
    return record


def git_record(path: pathlib.Path) -> dict:
    if not (path / ".git").exists():
        return {"path": str(path), "present": False}
    head = run(["git", "-C", str(path), "rev-parse", "HEAD"])
    branch = run(["git", "-C", str(path), "branch", "--show-current"])
    status = run(["git", "-C", str(path), "status", "--porcelain=v1", "--untracked-files=all"])
    return {
        "path": str(path),
        "present": True,
        "head": head["stdout"] if head["returncode"] == 0 else None,
        "branch": branch["stdout"] if branch["returncode"] == 0 else None,
        "changed_path_count": len([line for line in status["stdout"].splitlines() if line.strip()]),
        "status_command_ok": status["returncode"] == 0,
    }


def service_records() -> list[dict]:
    service_root = prefix / "var" / "service"
    sv = prefix / "bin" / "sv"
    records = []
    if not service_root.is_dir() or not sv.is_file():
        return records
    for path in sorted(service_root.iterdir(), key=lambda p: p.name.lower()):
        name = path.name
        if not re.search(r"(?:8x8|hermes|studio|jarvis|control)", name, re.I):
            continue
        result = run([str(sv), "status", str(path)])
        first = result["stdout"].splitlines()[0][:500] if result["stdout"] else None
        records.append({
            "name": name,
            "status": first,
            "command_ok": result["returncode"] == 0,
        })
    return records


def process_records() -> list[dict]:
    records = []
    proc = pathlib.Path("/proc")
    if not proc.is_dir():
        return records
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            comm = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()[:120]
            cmdline = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="replace")
        except (OSError, PermissionError):
            continue
        if not re.search(r"(?:8x8|hermes|studio|jarvis|control[_-]?fabric)", f"{comm} {cmdline}", re.I):
            continue
        records.append({"pid": int(entry.name), "comm": comm})
    return sorted(records, key=lambda item: item["pid"])


def msg205_record() -> dict:
    roots = [state_root, pathlib.Path("/root/.hermes"), relay_root, os_root]
    matches = []
    for root in roots:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*"):
                if len(matches) >= 100:
                    break
                if "msg205" not in path.name.lower():
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    continue
                matches.append({
                    "root": str(root),
                    "name": path.name,
                    "kind": "file" if path.is_file() else "directory" if path.is_dir() else "other",
                    "size_bytes": stat.st_size if path.is_file() else None,
                    "sha256": sha256_file(path),
                })
        except OSError:
            continue
    final_markers = [item for item in matches if re.search(r"(?:final|complete|completion|receipt)", item["name"], re.I)]
    return {
        "match_count": len(matches),
        "final_marker_count": len(final_markers),
        "matches": matches,
        "truth": "FINAL_MARKER_PRESENT_REQUIRES_CONTENT_REVIEW" if final_markers else "FINAL_RECEIPT_NOT_FOUND",
    }


def disk_record(path: pathlib.Path) -> dict:
    target = path if path.exists() else pathlib.Path("/")
    usage = shutil.disk_usage(target)
    return {
        "target": str(target),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
        "used_percent": round((usage.used / usage.total) * 100, 2) if usage.total else None,
    }

surface_records = [probe_surface(item) for item in surfaces]
services = service_records()
processes = process_records()
msg205 = msg205_record()

receipt = {
    "schema_version": "1.0.0",
    "mission": "8x8-local-rebuild-baseline",
    "observed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "mode": "READ_ONLY",
    "mutations_performed": False,
    "services_restarted": False,
    "processes_signaled": False,
    "external_network_access": False,
    "credentials_accessed": False,
    "secret_values_collected": False,
    "surfaces": surface_records,
    "surface_summary": {
        "reachable_count": sum(1 for item in surface_records if item["reachable"]),
        "eightx8_main_http": next((item["status_code"] for item in surface_records if item["id"] == "8x8-main"), None),
        "studio_http": next((item["status_code"] for item in surface_records if item["id"] == "8x8-studio"), None),
    },
    "runit_services": services,
    "matching_processes": processes,
    "repositories": [git_record(relay_root), git_record(os_root)],
    "storage": disk_record(relay_root),
    "msg205": msg205,
    "hermes_truth": (
        "PROCESS_OR_SERVICE_EVIDENCE_PRESENT_HTTP_ENDPOINT_UNRESOLVED"
        if any(re.search(r"hermes", json.dumps(item), re.I) for item in [*services, *processes])
        else "NO_LOCAL_PROCESS_OR_SERVICE_EVIDENCE"
    ),
}

canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
receipt_path.parent.mkdir(parents=True, exist_ok=True)
receipt_path.write_text(canonical, encoding="utf-8")
receipt_path.chmod(0o600)
receipt_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

print(json.dumps(receipt, indent=2, sort_keys=True))
print(f"BASELINE_RECEIPT={receipt_path}")
print(f"BASELINE_RECEIPT_SHA256={receipt_sha}")
print("BASELINE_MODE=READ_ONLY")
print("MUTATIONS_PERFORMED=false")
PY
