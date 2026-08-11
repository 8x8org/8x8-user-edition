from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_BENCHMARK = HERE / "benchmark_2026-08-11.json"
OVERLAY = HERE / "benchmark_2026-08-11_a2a_overlay.json"
EXPECTED_DIMENSIONS = tuple(f"D{i}" for i in range(1, 9))


class BenchmarkValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BenchmarkValidationError(message)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    require(isinstance(value, dict), f"{path.name}: root must be an object")
    return value


def _competition_ranks(projects: list[dict]) -> None:
    projects.sort(key=lambda project: (-int(project["score"]), str(project["project"])))
    prior_score: int | None = None
    prior_rank = 0
    for position, project in enumerate(projects, start=1):
        score = int(project["score"])
        rank = prior_rank if score == prior_score else position
        project["rank"] = rank
        prior_score = score
        prior_rank = rank


def materialize_benchmark(
    base_path: Path = BASE_BENCHMARK,
    overlay_path: Path = OVERLAY,
) -> dict:
    base = read_json(base_path)
    overlay = read_json(overlay_path)
    require(overlay.get("schema") == "8x8.one-fabric.external-benchmark-overlay.v1", "overlay schema mismatch")
    require(overlay.get("base_snapshot") == base_path.name, "overlay base snapshot mismatch")
    require(overlay.get("truth_boundary", {}).get("score_is_universal_rank") is False, "overlay universal-rank claim forbidden")
    require(overlay.get("truth_boundary", {}).get("global_100_claim_allowed") is False, "overlay global-100 claim forbidden")

    data = json.loads(json.dumps(base, ensure_ascii=False, allow_nan=False))
    baselines = [project for project in data.get("projects", []) if project.get("kind") == "baseline"]
    require(len(baselines) == 1, "base must contain exactly one baseline")
    baseline = baselines[0]
    require(baseline.get("project") == overlay.get("baseline_project"), "overlay baseline project mismatch")
    require(int(baseline.get("score", -1)) == int(overlay.get("expected_base_score", -2)), "overlay base score mismatch")

    component_patch = overlay.get("component_patch", {})
    require(isinstance(component_patch, dict) and component_patch, "component patch required")
    for dimension, value in component_patch.items():
        require(dimension in EXPECTED_DIMENSIONS, f"unknown component patch: {dimension}")
        baseline["components"][dimension] = int(value)
    baseline["score"] = sum(int(value) for value in baseline["components"].values())
    require(baseline["score"] == int(overlay.get("expected_materialized_score", -1)), "materialized score mismatch")

    baseline_fields = overlay.get("baseline_fields", {})
    require(isinstance(baseline_fields, dict), "baseline_fields must be an object")
    for key in ("primary_source", "evidence_summary", "single_extra_feature", "8x8_parity_gate"):
        require(isinstance(baseline_fields.get(key), str) and baseline_fields[key].strip(), f"overlay baseline field missing: {key}")
        baseline[key] = baseline_fields[key]

    external_source_patch = overlay.get("external_source_patch", {})
    require(isinstance(external_source_patch, dict), "external_source_patch must be an object")
    projects_by_name = {project["project"]: project for project in data["projects"]}
    for name, source in external_source_patch.items():
        require(name in projects_by_name, f"source patch project missing: {name}")
        require(isinstance(source, str) and source.startswith("https://"), f"source patch invalid: {name}")
        projects_by_name[name]["primary_source"] = source

    frontier_patch = overlay.get("frontier_patch", {})
    require(isinstance(frontier_patch, dict), "frontier_patch must be an object")
    for key in ("definition", "current_status", "why_it_is_one_feature"):
        require(isinstance(frontier_patch.get(key), str) and frontier_patch[key].strip(), f"frontier patch missing: {key}")
        data["frontier"][key] = frontier_patch[key]

    data["observed_at"] = overlay["observed_at"]
    _competition_ranks(data["projects"])
    return data


def load_benchmark() -> dict:
    return materialize_benchmark()


def validate(data: dict) -> dict:
    require(data.get("schema") == "8x8.one-fabric.external-benchmark.v1", "schema mismatch")
    require(data.get("root") == "fabric://8x8/core", "root mismatch")
    require(data.get("global_100_claim_allowed") is False, "global 100 claim must remain forbidden")
    require(data.get("score_is_universal_rank") is False, "benchmark must not claim universal ranking")

    dimensions = data.get("dimensions", [])
    require(len(dimensions) == 8, "benchmark requires exactly eight dimensions")
    require(tuple(item.get("id") for item in dimensions) == EXPECTED_DIMENSIONS, "dimension IDs must be D1..D8")
    weights = {item["id"]: int(item["weight"]) for item in dimensions}
    require(sum(weights.values()) == 100, "dimension weights must sum to 100")

    projects = data.get("projects", [])
    external = [project for project in projects if project.get("kind") == "external"]
    baseline = [project for project in projects if project.get("kind") == "baseline"]
    require(len(external) >= 10, "external denominator must contain at least 10 projects")
    require(len(baseline) == 1, "benchmark requires exactly one baseline")
    require(baseline[0].get("project") == "8x8 One Fabric", "baseline must be 8x8 One Fabric")

    prior_score = 101
    seen: set[str] = set()
    for project in projects:
        name = str(project.get("project", ""))
        require(bool(name), "project name is required")
        require(name not in seen, f"duplicate project: {name}")
        seen.add(name)
        components = project.get("components", {})
        require(tuple(sorted(components)) == EXPECTED_DIMENSIONS, f"{name}: components must be D1..D8")
        for key, value in components.items():
            value = int(value)
            require(0 <= value <= weights[key], f"{name}: {key}={value} exceeds weight {weights[key]}")
        computed = sum(int(value) for value in components.values())
        require(computed == int(project.get("score", -1)), f"{name}: score does not equal component sum")
        require(0 <= computed <= 100, f"{name}: score outside 0..100")
        require(str(project.get("primary_source", "")).startswith(("https://", "github://")), f"{name}: primary source missing")
        require(bool(str(project.get("single_extra_feature", "")).strip()), f"{name}: single extra feature missing")
        require(bool(str(project.get("8x8_parity_gate", "")).strip()), f"{name}: 8x8 parity gate missing")
        require(computed <= prior_score, f"{name}: project list must remain score-descending")
        prior_score = computed

    frontier = data.get("frontier", {})
    require(frontier.get("single_plus_one_feature") == "Sovereign Proof-Carrying Autonomy", "frontier feature drift")
    frontier_status = str(frontier.get("current_status", ""))
    for marker in (
        "A2A_HTTP_JSON_TWO_PROCESS_SELF_INTEROP_VALIDATED",
        "INDEPENDENT_THIRD_PARTY_A2A_INTEROP_NOT_YET_PROVEN",
        "AUTHENTICATED_PRODUCTION_A2A_EDGE_NOT_YET_IMPLEMENTED",
        "NATIVE_END_TO_END_BINDING_NOT_YET_PROVEN",
        "PRIVACY_PRESERVING_ATTESTATION_NOT_YET_IMPLEMENTED",
    ):
        require(marker in frontier_status, f"frontier status marker missing: {marker}")

    return {
        "external_denominator": len(external),
        "project_denominator": len(projects),
        "baseline_score": int(baseline[0]["score"]),
        "top_score": max(int(project["score"]) for project in projects),
        "global_100_claim_allowed": False,
        "status": "VALIDATED_BOUNDED_SNAPSHOT",
    }


if __name__ == "__main__":
    print(json.dumps(validate(load_benchmark()), sort_keys=True))
