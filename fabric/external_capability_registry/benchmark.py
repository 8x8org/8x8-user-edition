from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK = HERE / "benchmark_2026-08-11.json"
EXPECTED_DIMENSIONS = tuple(f"D{i}" for i in range(1, 9))


class BenchmarkValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BenchmarkValidationError(message)


def load_benchmark(path: Path = BENCHMARK) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


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
    external = [p for p in projects if p.get("kind") == "external"]
    baseline = [p for p in projects if p.get("kind") == "baseline"]
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
    require("NOT_YET_PROVEN" in frontier_status, "native end-to-end nonclaim must remain explicit")
    require("NOT_YET_IMPLEMENTED" in frontier_status, "privacy attestation nonclaim must remain explicit")

    return {
        "external_denominator": len(external),
        "project_denominator": len(projects),
        "baseline_score": int(baseline[0]["score"]),
        "top_score": max(int(p["score"]) for p in projects),
        "global_100_claim_allowed": False,
        "status": "VALIDATED_BOUNDED_SNAPSHOT",
    }


if __name__ == "__main__":
    print(json.dumps(validate(load_benchmark()), sort_keys=True))
