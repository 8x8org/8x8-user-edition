#!/usr/bin/env python3
"""Bounded, non-executing static probe for MSG197 external repositories.

The probe fetches only the immutable commit and Git tree metadata. It reads a
bounded set of license and dependency-manifest blobs. It never checks out a
worktree, enables submodules, runs hooks, installs dependencies, imports
candidate modules, starts services, or executes candidate tests/scripts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "external-capabilities"
CENSUS_PATH = BASE / "REPOSITORY_CENSUS.json"
POLICY_PATH = BASE / "UPSTREAM_STATIC_SCAN_POLICY.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPO_NAME = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TREE_LINE = re.compile(
    rb"^(?P<mode>[0-9]{6}) (?P<kind>[^ ]+) (?P<sha>[0-9a-f]{40}) "
    rb"(?P<size>-|[0-9]+)\t(?P<path>.*)$"
)
SECRET_PATH = re.compile(
    r"(^|/)(\.env($|\.)|id_(rsa|dsa|ecdsa|ed25519)($|\.)|"
    r"credentials?($|\.)|secrets?($|\.)|.*\.(pem|p12|pfx|key|keystore)$)",
    re.IGNORECASE,
)
SENSITIVE_SCRIPT = re.compile(
    r"\b(curl|wget|ssh|scp|rsync|sudo|powershell|pwsh|docker|kubectl|"
    r"terraform|ansible|wallet|private[_ -]?key|secret|token)\b",
    re.IGNORECASE,
)
NATIVE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",
    ".m",
    ".mm",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".swift",
    ".cu",
    ".s",
    ".asm",
}


class ProbeError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug_for(repository: str) -> str:
    return repository.lower().replace("/", "__").replace(".", "_")


def run_git(repo_dir: Path, args: list[str], timeout: int, text: bool = False) -> subprocess.CompletedProcess[Any]:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "LC_ALL": "C.UTF-8",
    }
    cmd = [
        "git",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "fetch.recurseSubmodules=false",
        "-C",
        str(repo_dir),
        *args,
    ]
    try:
        return subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=text,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProbeError(f"git timeout: {' '.join(args[:3])}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", "replace")
        raise ProbeError(f"git failed: {' '.join(args[:3])}: {stderr[-1000:]}") from exc


def bounded_git_show(repo_dir: Path, commit: str, path: str, max_bytes: int, timeout: int) -> tuple[bytes | None, str | None]:
    try:
        result = run_git(repo_dir, ["show", f"{commit}:{path}"], timeout=timeout, text=False)
    except ProbeError as exc:
        return None, str(exc)
    data: bytes = result.stdout
    if len(data) > max_bytes:
        return None, f"blob exceeds bounded read limit: {len(data)} > {max_bytes}"
    return data, None


def matches_manifest(path: str, patterns: list[str]) -> bool:
    base = path.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(base, pattern) for pattern in patterns)


def parse_package_json(data: bytes) -> dict[str, Any]:
    try:
        package = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"parse_status": "ERROR", "error": str(exc)}
    dependency_groups: dict[str, list[str]] = {}
    for key in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "bundledDependencies"):
        value = package.get(key, {})
        if isinstance(value, dict):
            dependency_groups[key] = sorted(str(name) for name in value)
        elif isinstance(value, list):
            dependency_groups[key] = sorted(str(name) for name in value)
    scripts = package.get("scripts", {})
    script_names: list[str] = []
    sensitive: list[dict[str, str]] = []
    if isinstance(scripts, dict):
        for name, command in sorted(scripts.items()):
            script_names.append(str(name))
            command_text = str(command)
            if name in {"preinstall", "install", "postinstall", "prepare", "prepublish", "prepublishOnly"} or SENSITIVE_SCRIPT.search(command_text):
                sensitive.append({"name": str(name), "command_sha256": sha256_bytes(command_text.encode("utf-8"))})
    engines = package.get("engines", {})
    return {
        "parse_status": "PASS",
        "package_name": package.get("name"),
        "package_version": package.get("version"),
        "dependency_groups": dependency_groups,
        "dependency_count": sum(len(names) for names in dependency_groups.values()),
        "script_names": script_names,
        "sensitive_script_findings": sensitive,
        "engines": engines if isinstance(engines, dict) else {},
    }


def parse_pyproject(data: bytes) -> dict[str, Any]:
    try:
        payload = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return {"parse_status": "ERROR", "error": str(exc)}
    project = payload.get("project", {}) if isinstance(payload.get("project", {}), dict) else {}
    dependencies = project.get("dependencies", []) if isinstance(project.get("dependencies", []), list) else []
    optional = project.get("optional-dependencies", {}) if isinstance(project.get("optional-dependencies", {}), dict) else {}
    poetry = payload.get("tool", {}).get("poetry", {}) if isinstance(payload.get("tool", {}), dict) else {}
    poetry_deps = poetry.get("dependencies", {}) if isinstance(poetry, dict) and isinstance(poetry.get("dependencies", {}), dict) else {}
    build = payload.get("build-system", {}) if isinstance(payload.get("build-system", {}), dict) else {}
    return {
        "parse_status": "PASS",
        "project_name": project.get("name") or (poetry.get("name") if isinstance(poetry, dict) else None),
        "direct_dependencies": [str(item) for item in dependencies],
        "optional_dependency_groups": {str(key): [str(item) for item in value] for key, value in optional.items() if isinstance(value, list)},
        "poetry_dependency_names": sorted(str(name) for name in poetry_deps),
        "build_requires": [str(item) for item in build.get("requires", [])] if isinstance(build.get("requires", []), list) else [],
    }


def parse_cargo_toml(data: bytes) -> dict[str, Any]:
    try:
        payload = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return {"parse_status": "ERROR", "error": str(exc)}
    groups: dict[str, list[str]] = {}
    for key in ("dependencies", "dev-dependencies", "build-dependencies"):
        value = payload.get(key, {})
        if isinstance(value, dict):
            groups[key] = sorted(str(name) for name in value)
    workspace = payload.get("workspace", {})
    if isinstance(workspace, dict) and isinstance(workspace.get("dependencies", {}), dict):
        groups["workspace.dependencies"] = sorted(str(name) for name in workspace["dependencies"])
    return {"parse_status": "PASS", "dependency_groups": groups, "dependency_count": sum(len(value) for value in groups.values())}


def parse_requirements(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8", "replace")
    entries = []
    directives = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-"):
            directives.append(line[:200])
        else:
            entries.append(line[:500])
    return {"parse_status": "PASS", "direct_entries": entries, "directives": directives}


def parse_go_mod(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8", "replace")
    module = None
    dependencies: list[str] = []
    in_require = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("module "):
            module = line.split(None, 1)[1]
        elif line == "require (":
            in_require = True
        elif in_require and line == ")":
            in_require = False
        elif line.startswith("require "):
            dependencies.append(line.split(None, 1)[1][:500])
        elif in_require and line and not line.startswith("//"):
            dependencies.append(line[:500])
    return {"parse_status": "PASS", "module": module, "direct_requirements": dependencies}


def parse_workflow(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8", "replace")
    action_refs = sorted(set(re.findall(r"^\s*-?\s*uses:\s*['\"]?([^\s'\"]+)", text, flags=re.MULTILINE)))
    permissions = sorted(set(re.findall(r"^\s{0,4}([a-z-]+):\s*(read|write|none)\s*$", text, flags=re.MULTILINE)))
    sensitive_lines = []
    for number, line in enumerate(text.splitlines(), start=1):
        if SENSITIVE_SCRIPT.search(line):
            sensitive_lines.append({"line": number, "sha256": sha256_bytes(line.encode("utf-8"))})
    return {
        "parse_status": "PASS",
        "action_refs": action_refs,
        "declared_permissions": [{"scope": scope, "access": access} for scope, access in permissions],
        "sensitive_line_findings": sensitive_lines[:100],
        "sensitive_line_findings_truncated": len(sensitive_lines) > 100,
    }


def parse_manifest(path: str, data: bytes) -> dict[str, Any]:
    base = path.rsplit("/", 1)[-1]
    if base == "package.json":
        return parse_package_json(data)
    if base == "pyproject.toml":
        return parse_pyproject(data)
    if base == "Cargo.toml":
        return parse_cargo_toml(data)
    if fnmatch.fnmatch(base, "requirements*.txt"):
        return parse_requirements(data)
    if base == "go.mod":
        return parse_go_mod(data)
    if path.startswith(".github/workflows/") and base.endswith((".yml", ".yaml")):
        return parse_workflow(data)
    return {"parse_status": "RECORDED_HASH_ONLY"}


def probe_candidate(record: dict[str, Any], policy: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    repository = str(record["canonical"])
    commit = str(record["pinned_commit"])
    started_at = utc_now()
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "mission_id": "MSG197B_COUNCIL_SANDBOX_READINESS_V1",
        "candidate": repository,
        "pinned_commit": commit,
        "started_at": started_at,
        "status": "FAILED",
        "execution_boundary": "STATIC_METADATA_AND_BOUNDED_MANIFEST_READS_ONLY",
        "candidate_code_executed": false,
        "dependencies_installed": false,
        "tests_executed": false,
        "worktree_checked_out": false,
        "submodules_enabled": false,
    }
    if not REPO_NAME.fullmatch(repository):
        result["error"] = "invalid canonical repository identity"
        return result
    if not SHA40.fullmatch(commit):
        result["error"] = "invalid immutable commit pin"
        return result

    limits = policy["resource_limits"]
    timeout = int(limits["per_candidate_wall_seconds"])
    max_blob = int(limits["maximum_manifest_blob_bytes"])
    max_manifests = int(limits["maximum_manifests_per_candidate"])
    max_tree_entries = int(limits["maximum_tree_entries_recorded"])
    patterns = [str(pattern) for pattern in policy["manifest_patterns"]]

    temporary_root = Path(tempfile.mkdtemp(prefix=f"msg197-{slug_for(repository)}-"))
    bare_repo = temporary_root / "source.git"
    try:
        subprocess.run(["git", "init", "--bare", str(bare_repo)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        run_git(bare_repo, ["remote", "add", "origin", f"https://github.com/{repository}.git"], timeout=30)
        run_git(
            bare_repo,
            ["fetch", "--depth=1", "--filter=blob:none", "--no-tags", "origin", commit],
            timeout=timeout,
        )
        fetched = run_git(bare_repo, ["rev-parse", "FETCH_HEAD"], timeout=30, text=True).stdout.strip()
        if fetched != commit:
            raise ProbeError(f"exact commit mismatch: expected {commit}, got {fetched}")

        commit_fields = run_git(
            bare_repo,
            ["show", "-s", "--format=%H%x00%ct%x00%an%x00%ae%x00%s", commit],
            timeout=30,
            text=False,
        ).stdout.split(b"\x00", 4)
        if len(commit_fields) != 5:
            raise ProbeError("unexpected commit metadata format")
        commit_metadata = {
            "sha": commit_fields[0].decode("ascii", "replace"),
            "committed_unix": int(commit_fields[1]),
            "author_name": commit_fields[2].decode("utf-8", "replace")[:500],
            "author_email_sha256": sha256_bytes(commit_fields[3]),
            "subject": commit_fields[4].decode("utf-8", "replace").strip()[:1000],
        }

        raw_tree = run_git(bare_repo, ["ls-tree", "-r", "-l", "-z", "--full-tree", commit], timeout=timeout, text=False).stdout
        entries: list[dict[str, Any]] = []
        normalized_lines: list[bytes] = []
        manifest_paths: list[str] = []
        secret_paths: list[str] = []
        top_levels: set[str] = set()
        extension_counts: dict[str, int] = {}
        executable_count = 0
        symlink_count = 0
        large_blob_count = 0
        total_declared_bytes = 0
        tree_truncated = False

        for index, raw in enumerate(raw_tree.split(b"\x00")):
            if not raw:
                continue
            if index >= max_tree_entries:
                tree_truncated = True
                break
            match = TREE_LINE.match(raw)
            if not match:
                raise ProbeError("unable to parse git tree entry")
            mode = match.group("mode").decode("ascii")
            kind = match.group("kind").decode("ascii")
            object_sha = match.group("sha").decode("ascii")
            size_raw = match.group("size").decode("ascii")
            path = match.group("path").decode("utf-8", "surrogateescape")
            size = None if size_raw == "-" else int(size_raw)
            if size is not None:
                total_declared_bytes += size
                if size >= 5 * 1024 * 1024:
                    large_blob_count += 1
            if mode == "100755":
                executable_count += 1
            if mode == "120000":
                symlink_count += 1
            top_levels.add(path.split("/", 1)[0])
            suffix = Path(path).suffix.lower() or "<none>"
            extension_counts[suffix] = extension_counts.get(suffix, 0) + 1
            if matches_manifest(path, patterns):
                manifest_paths.append(path)
            if SECRET_PATH.search(path):
                secret_paths.append(path)
            normalized_lines.append(f"{mode} {kind} {object_sha} {size_raw}\t{path}\n".encode("utf-8", "surrogateescape"))
            entries.append({"mode": mode, "kind": kind, "sha": object_sha, "size": size, "path": path})

        entry_by_path = {entry["path"]: entry for entry in entries}
        manifest_paths = sorted(set(manifest_paths))
        manifests_truncated = len(manifest_paths) > max_manifests
        selected_manifests = manifest_paths[:max_manifests]
        manifest_records: list[dict[str, Any]] = []
        for path in selected_manifests:
            data, error = bounded_git_show(bare_repo, commit, path, max_bytes=max_blob, timeout=60)
            tree_entry = entry_by_path[path]
            record_out: dict[str, Any] = {
                "path": path,
                "git_blob_sha": tree_entry["sha"],
                "declared_size": tree_entry["size"],
            }
            if error is not None or data is None:
                record_out.update({"read_status": "SKIPPED", "reason": error})
            else:
                record_out.update(
                    {
                        "read_status": "PASS",
                        "sha256": sha256_bytes(data),
                        "bytes_read": len(data),
                        "analysis": parse_manifest(path, data),
                    }
                )
            manifest_records.append(record_out)

        license_record = record.get("license", {})
        license_path = str(license_record.get("path", ""))
        license_tree = entry_by_path.get(license_path)
        license_verification: dict[str, Any] = {
            "path": license_path,
            "expected_spdx": license_record.get("spdx"),
            "expected_blob_sha": license_record.get("blob_sha"),
            "tree_entry_present": license_tree is not None,
            "blob_sha_matches": bool(license_tree and license_tree["sha"] == license_record.get("blob_sha")),
        }
        if license_tree:
            license_data, license_error = bounded_git_show(bare_repo, commit, license_path, max_bytes=max_blob, timeout=60)
            license_verification["read_status"] = "PASS" if license_data is not None else "SKIPPED"
            license_verification["read_error"] = license_error
            if license_data is not None:
                license_verification["sha256"] = sha256_bytes(license_data)
                license_verification["bytes_read"] = len(license_data)

        result.update(
            {
                "status": "PASS_STATIC_METADATA_ONLY",
                "completed_at": utc_now(),
                "exact_commit_verified": true,
                "commit": commit_metadata,
                "tree": {
                    "sha256": sha256_bytes(b"".join(sorted(normalized_lines))),
                    "entry_count_recorded": len(entries),
                    "truncated": tree_truncated,
                    "total_declared_blob_bytes": total_declared_bytes,
                    "executable_count": executable_count,
                    "symlink_count": symlink_count,
                    "large_blob_count_at_or_above_5_mib": large_blob_count,
                    "top_level_entries": sorted(top_levels),
                    "extension_counts": dict(sorted(extension_counts.items(), key=lambda item: (-item[1], item[0]))[:100]),
                    "native_source_file_count": sum(count for suffix, count in extension_counts.items() if suffix in NATIVE_EXTENSIONS),
                },
                "dependency_and_execution_surfaces": {
                    "manifest_count_discovered": len(manifest_paths),
                    "manifest_count_read": sum(1 for item in manifest_records if item["read_status"] == "PASS"),
                    "manifests_truncated": manifests_truncated,
                    "manifests": manifest_records,
                    "workflow_count": sum(1 for path in manifest_paths if path.startswith(".github/workflows/")),
                    "container_definition_count": sum(1 for path in manifest_paths if "docker" in path.lower()),
                    "secret_shaped_path_count": len(secret_paths),
                    "secret_shaped_paths": sorted(secret_paths)[:200],
                    "secret_shaped_paths_truncated": len(secret_paths) > 200,
                },
                "license_verification": license_verification,
                "limitations": policy["limitations"],
            }
        )
    except Exception as exc:  # fail-visible receipt, never silent omission
        result.update({"status": "FAILED", "completed_at": utc_now(), "error": f"{type(exc).__name__}: {exc}"})
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)
        result["cleanup"] = {"temporary_source_removed": not temporary_root.exists(), "retained_candidate_source": false}

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{slug_for(repository)}.json"
    destination.write_bytes(canonical_json_bytes(result))
    result["receipt_path"] = destination.relative_to(ROOT).as_posix() if destination.is_relative_to(ROOT) else destination.as_posix()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", help="Canonical owner/name to probe")
    parser.add_argument("--all", action="store_true", help="Probe every candidate in the census")
    parser.add_argument("--output-dir", default="research/external-capabilities/scans/current")
    parser.add_argument("--workers", type=int)
    args = parser.parse_args()
    if bool(args.candidate) == bool(args.all):
        raise SystemExit("choose exactly one of --candidate or --all")

    census = load_json(CENSUS_PATH)
    policy = load_json(POLICY_PATH)
    records = list(census.get("repositories", []))
    by_name = {str(record["canonical"]): record for record in records}
    if len(records) != 13 or len(by_name) != 13:
        raise SystemExit("census must contain exactly 13 unique candidates")

    if args.candidate:
        if args.candidate not in by_name:
            raise SystemExit(f"candidate not in census: {args.candidate}")
        selected = [by_name[args.candidate]]
    else:
        selected = records

    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    maximum_workers = int(policy["resource_limits"]["maximum_parallel_candidates"])
    workers = max(1, min(args.workers or maximum_workers, maximum_workers, len(selected)))
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(probe_candidate, record, policy, output_dir): record["canonical"] for record in selected}
        for future in concurrent.futures.as_completed(futures):
            candidate = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    {
                        "schema_version": "1.0.0",
                        "mission_id": "MSG197B_COUNCIL_SANDBOX_READINESS_V1",
                        "candidate": candidate,
                        "status": "FAILED",
                        "error": f"worker failure: {type(exc).__name__}: {exc}",
                        "candidate_code_executed": false,
                        "dependencies_installed": false,
                        "cleanup": {"temporary_source_removed": "UNKNOWN", "retained_candidate_source": false},
                    }
                )

    results.sort(key=lambda item: str(item["candidate"]).lower())
    summary_core = {
        "schema_version": "1.0.0",
        "mission_id": "MSG197B_COUNCIL_SANDBOX_READINESS_V1",
        "truth_state": "STATIC_METADATA_PROBES_ONLY",
        "candidate_count": len(results),
        "pass_count": sum(1 for item in results if item.get("status") == "PASS_STATIC_METADATA_ONLY"),
        "failure_count": sum(1 for item in results if item.get("status") != "PASS_STATIC_METADATA_ONLY"),
        "candidate_code_executed": false,
        "dependencies_installed": false,
        "tests_executed": false,
        "results": [
            {
                "candidate": item["candidate"],
                "pinned_commit": item.get("pinned_commit"),
                "status": item.get("status"),
                "tree_sha256": item.get("tree", {}).get("sha256"),
                "manifest_count": item.get("dependency_and_execution_surfaces", {}).get("manifest_count_discovered"),
                "license_blob_matches": item.get("license_verification", {}).get("blob_sha_matches"),
                "error": item.get("error"),
            }
            for item in results
        ],
    }
    summary = {
        **summary_core,
        "generated_at": utc_now(),
        "summary_payload_sha256": sha256_bytes(canonical_json_bytes(summary_core)),
    }
    (output_dir / "STATIC_PROBE_SUMMARY.json").write_bytes(canonical_json_bytes(summary))

    hash_lines = []
    for path in sorted(output_dir.glob("*.json")):
        hash_lines.append(f"{sha256_bytes(path.read_bytes())}  {path.relative_to(ROOT).as_posix()}")
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    print(
        "MSG197_STATIC_PROBE_COMPLETE "
        f"candidates={len(results)} pass={summary['pass_count']} failed={summary['failure_count']} "
        "candidate_code_executed=false dependencies_installed=false"
    )
    if summary["failure_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
