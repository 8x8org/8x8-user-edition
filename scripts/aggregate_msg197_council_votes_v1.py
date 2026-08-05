#!/usr/bin/env python3
"""Aggregate MSG197 council votes without network, secrets, or runtime mutation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SESSION = ROOT / "research/external-capabilities/council/COUNCIL_SESSION.json"
DEFAULT_LEDGER = ROOT / "research/external-capabilities/CANDIDATE_STATUS_LEDGER_V3.json"
SHA64 = set("0123456789abcdef")
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "session_id",
    "participant",
    "lease",
    "input_digest",
    "recommendations",
    "security_veto",
    "output_digest",
    "receipt_status",
}


class VoteRejected(ValueError):
    """A vote failed a deterministic council gate."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def vote_output_digest(vote: dict[str, Any]) -> str:
    payload = copy.deepcopy(vote)
    payload["output_digest"] = None
    return sha256_json(payload)


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise VoteRejected("LEASE_EXPIRY_MISSING")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise VoteRejected("LEASE_EXPIRY_INVALID") from exc
    if parsed.tzinfo is None:
        raise VoteRejected("LEASE_EXPIRY_MUST_BE_TIMEZONE_AWARE")
    return parsed.astimezone(timezone.utc)


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= SHA64


def validate_vote(
    vote: dict[str, Any],
    *,
    session: dict[str, Any],
    candidates: set[str],
    now: datetime,
) -> dict[str, Any]:
    if not isinstance(vote, dict):
        raise VoteRejected("VOTE_MUST_BE_OBJECT")
    if set(vote) != REQUIRED_TOP_LEVEL:
        raise VoteRejected("TOP_LEVEL_SCHEMA_MISMATCH")
    if vote.get("schema_version") != "1.0.0":
        raise VoteRejected("SCHEMA_VERSION_MISMATCH")
    if vote.get("session_id") != session.get("session_id"):
        raise VoteRejected("SESSION_ID_MISMATCH")
    if vote.get("input_digest") != session.get("input_pin_set_sha256"):
        raise VoteRejected("INPUT_DIGEST_MISMATCH")

    participant = vote.get("participant")
    if not isinstance(participant, dict) or set(participant) != {"agent_id", "display_name", "identity_status"}:
        raise VoteRejected("PARTICIPANT_SCHEMA_MISMATCH")
    agent_id = participant.get("agent_id")
    eligible = {item.get("agent_id") for item in session.get("participants", [])}
    if agent_id not in eligible:
        raise VoteRejected("PARTICIPANT_NOT_REGISTERED")
    if participant.get("identity_status") != "VERIFIED":
        raise VoteRejected("IDENTITY_NOT_VERIFIED")
    if not isinstance(participant.get("display_name"), str) or not participant["display_name"].strip():
        raise VoteRejected("DISPLAY_NAME_MISSING")

    lease = vote.get("lease")
    if not isinstance(lease, dict) or set(lease) != {"lease_id", "status", "expires_at"}:
        raise VoteRejected("LEASE_SCHEMA_MISMATCH")
    if lease.get("status") != "ACTIVE":
        raise VoteRejected("LEASE_NOT_ACTIVE")
    if not isinstance(lease.get("lease_id"), str) or not lease["lease_id"].strip():
        raise VoteRejected("LEASE_ID_MISSING")
    expires_at = parse_time(lease.get("expires_at"))
    if expires_at <= now:
        raise VoteRejected("LEASE_EXPIRED")

    if vote.get("receipt_status") != "VALID_VOTE":
        raise VoteRejected("RECEIPT_NOT_VALID_VOTE")
    if not valid_sha256(vote.get("output_digest")):
        raise VoteRejected("OUTPUT_DIGEST_INVALID")
    expected_output = vote_output_digest(vote)
    if vote["output_digest"] != expected_output:
        raise VoteRejected("OUTPUT_DIGEST_MISMATCH")

    recommendations = vote.get("recommendations")
    if not isinstance(recommendations, list) or len(recommendations) != len(candidates):
        raise VoteRejected("RECOMMENDATION_COUNT_MISMATCH")
    seen_candidates: set[str] = set()
    normalized_recommendations: list[dict[str, Any]] = []
    for item in recommendations:
        if not isinstance(item, dict) or set(item) != {"candidate", "decision", "confidence"}:
            raise VoteRejected("RECOMMENDATION_SCHEMA_MISMATCH")
        candidate = item.get("candidate")
        decision = item.get("decision")
        confidence = item.get("confidence")
        if candidate not in candidates:
            raise VoteRejected("UNKNOWN_CANDIDATE")
        if candidate in seen_candidates:
            raise VoteRejected("DUPLICATE_CANDIDATE")
        if not isinstance(decision, str) or not decision.strip():
            raise VoteRejected("DECISION_MISSING")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise VoteRejected("CONFIDENCE_OUT_OF_RANGE")
        seen_candidates.add(candidate)
        normalized_recommendations.append({
            "candidate": candidate,
            "decision": decision,
            "confidence": float(confidence),
        })
    if seen_candidates != candidates:
        raise VoteRejected("CANDIDATE_SET_MISMATCH")

    vetoes = vote.get("security_veto")
    if not isinstance(vetoes, list) or any(not isinstance(item, str) or not item.strip() for item in vetoes):
        raise VoteRejected("SECURITY_VETO_SCHEMA_MISMATCH")

    return {
        "agent_id": agent_id,
        "display_name": participant["display_name"],
        "lease_id": lease["lease_id"],
        "lease_expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "output_digest": vote["output_digest"],
        "recommendations": sorted(normalized_recommendations, key=lambda item: item["candidate"]),
        "recommendations_sha256": sha256_json(sorted(normalized_recommendations, key=lambda item: item["candidate"])),
        "security_veto": sorted(set(vetoes)),
    }


def aggregate(
    vote_files: list[Path],
    *,
    session: dict[str, Any],
    ledger: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    candidates = {item["repository"] for item in ledger.get("candidates", [])}
    if len(candidates) != 13:
        raise SystemExit("canonical ledger must contain exactly thirteen unique candidates")

    valid_votes: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    seen_agents: set[str] = set()

    for path in sorted(vote_files, key=lambda item: item.name):
        try:
            vote = json.loads(path.read_text(encoding="utf-8"))
            normalized = validate_vote(vote, session=session, candidates=candidates, now=now)
            if normalized["agent_id"] in seen_agents:
                raise VoteRejected("DUPLICATE_AGENT_VOTE")
            seen_agents.add(normalized["agent_id"])
            normalized["source_file"] = path.name
            valid_votes.append(normalized)
        except (OSError, json.JSONDecodeError, VoteRejected) as exc:
            reason = str(exc) if isinstance(exc, VoteRejected) else exc.__class__.__name__
            rejected.append({"source_file": path.name, "reason": reason})

    quorum_required = int(session.get("quorum", {}).get("minimum_valid_votes", 4))
    quorum_reached = len(valid_votes) >= quorum_required
    all_vetoes = sorted({veto for vote in valid_votes for veto in vote["security_veto"]})
    security_veto_active = bool(all_vetoes)
    advancement_allowed = quorum_reached and not security_veto_active

    decision_counts: dict[str, Counter[str]] = defaultdict(Counter)
    confidence_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for vote in valid_votes:
        for item in vote["recommendations"]:
            decision_counts[item["candidate"]][item["decision"]] += 1
            confidence_values[(item["candidate"], item["decision"])].append(item["confidence"])

    candidate_results: list[dict[str, Any]] = []
    for candidate in sorted(candidates):
        counts = decision_counts[candidate]
        decisions = []
        for decision, count in sorted(counts.items()):
            values = confidence_values[(candidate, decision)]
            decisions.append({
                "decision": decision,
                "votes": count,
                "mean_confidence": round(sum(values) / len(values), 6),
            })
        majority = None
        if counts:
            decision, count = counts.most_common(1)[0]
            if count > len(valid_votes) / 2:
                majority = decision
        candidate_results.append({
            "candidate": candidate,
            "decision_distribution": decisions,
            "majority_decision": majority,
            "state": "MAJORITY_RECORDED" if majority else "DISAGREEMENT_OR_INSUFFICIENT_VOTES",
        })

    if not quorum_reached:
        truth_state = "QUORUM_PENDING"
    elif security_veto_active:
        truth_state = "QUORUM_REACHED_SECURITY_VETO_ACTIVE"
    else:
        truth_state = "QUORUM_REACHED_NO_SECURITY_VETO"

    output = {
        "schema_version": "1.0.0",
        "session_id": session["session_id"],
        "generated_at": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input_digest": session["input_pin_set_sha256"],
        "candidate_count": len(candidates),
        "eligible_participant_count": len(session.get("participants", [])),
        "quorum_required": quorum_required,
        "valid_vote_count": len(valid_votes),
        "rejected_vote_count": len(rejected),
        "quorum_reached": quorum_reached,
        "security_veto_active": security_veto_active,
        "security_vetoes": all_vetoes,
        "advancement_allowed": advancement_allowed,
        "truth_state": truth_state,
        "valid_votes": sorted(valid_votes, key=lambda item: item["agent_id"]),
        "rejected_votes": sorted(rejected, key=lambda item: (item["source_file"], item["reason"])),
        "candidate_results": candidate_results,
    }
    output["aggregation_sha256"] = sha256_json(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--votes-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--session", type=Path, default=DEFAULT_SESSION)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--now", required=True, help="UTC timestamp, for example 2026-08-05T22:30:00Z")
    args = parser.parse_args()

    now = parse_time(args.now)
    session = json.loads(args.session.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    vote_files = sorted(args.votes_dir.glob("*.json")) if args.votes_dir.is_dir() else []
    result = aggregate(vote_files, session=session, ledger=ledger, now=now)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "MSG197_COUNCIL_AGGREGATION_PASS "
        f"valid={result['valid_vote_count']} rejected={result['rejected_vote_count']} "
        f"quorum={str(result['quorum_reached']).lower()} veto={str(result['security_veto_active']).lower()}"
    )


if __name__ == "__main__":
    main()
