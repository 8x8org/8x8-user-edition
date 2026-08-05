import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aggregate_msg197_council_votes_v1.py"
SPEC = importlib.util.spec_from_file_location("msg197_council_aggregate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

SESSION = json.loads((ROOT / "research/external-capabilities/council/COUNCIL_SESSION.json").read_text(encoding="utf-8"))
LEDGER = json.loads((ROOT / "research/external-capabilities/CANDIDATE_STATUS_LEDGER_V3.json").read_text(encoding="utf-8"))
NOW = datetime(2026, 8, 5, 23, 0, tzinfo=timezone.utc)
CANDIDATES = sorted(item["repository"] for item in LEDGER["candidates"])


def make_vote(agent_id, *, decision="ADOPT_PATTERNS_ONLY", vetoes=None, expires=None, input_digest=None):
    vote = {
        "schema_version": "1.0.0",
        "session_id": SESSION["session_id"],
        "participant": {
            "agent_id": agent_id,
            "display_name": agent_id.replace("-", " ").title(),
            "identity_status": "VERIFIED",
        },
        "lease": {
            "lease_id": f"lease-{agent_id}",
            "status": "ACTIVE",
            "expires_at": (expires or (NOW + timedelta(hours=1))).isoformat().replace("+00:00", "Z"),
        },
        "input_digest": input_digest or SESSION["input_pin_set_sha256"],
        "recommendations": [
            {"candidate": candidate, "decision": decision, "confidence": 0.9}
            for candidate in CANDIDATES
        ],
        "security_veto": list(vetoes or []),
        "output_digest": None,
        "receipt_status": "VALID_VOTE",
    }
    vote["output_digest"] = MODULE.vote_output_digest(vote)
    return vote


def write_vote(directory, name, vote):
    path = directory / name
    path.write_text(json.dumps(vote, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


class CouncilAggregationContract(unittest.TestCase):
    def aggregate(self, votes):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            files = [write_vote(directory, name, vote) for name, vote in votes]
            return MODULE.aggregate(files, session=SESSION, ledger=LEDGER, now=NOW)

    def test_zero_votes_remains_pending(self):
        result = MODULE.aggregate([], session=SESSION, ledger=LEDGER, now=NOW)
        self.assertEqual(0, result["valid_vote_count"])
        self.assertFalse(result["quorum_reached"])
        self.assertFalse(result["advancement_allowed"])
        self.assertEqual("QUORUM_PENDING", result["truth_state"])
        self.assertRegex(result["aggregation_sha256"], r"^[0-9a-f]{64}$")

    def test_four_valid_votes_reach_quorum(self):
        agents = ["hermes", "flashtm8-agent", "seraphim", "claude"]
        result = self.aggregate([(f"{index}.json", make_vote(agent)) for index, agent in enumerate(agents)])
        self.assertEqual(4, result["valid_vote_count"])
        self.assertTrue(result["quorum_reached"])
        self.assertFalse(result["security_veto_active"])
        self.assertTrue(result["advancement_allowed"])
        self.assertEqual("QUORUM_REACHED_NO_SECURITY_VETO", result["truth_state"])
        self.assertTrue(all(item["majority_decision"] == "ADOPT_PATTERNS_ONLY" for item in result["candidate_results"]))

    def test_security_veto_blocks_advancement_even_with_quorum(self):
        agents = ["hermes", "flashtm8-agent", "seraphim", "claude"]
        votes = [(f"{index}.json", make_vote(agent, vetoes=["SUPPLY_CHAIN_BLOCK"]) if agent == "hermes" else make_vote(agent)) for index, agent in enumerate(agents)]
        result = self.aggregate(votes)
        self.assertTrue(result["quorum_reached"])
        self.assertTrue(result["security_veto_active"])
        self.assertFalse(result["advancement_allowed"])
        self.assertEqual(["SUPPLY_CHAIN_BLOCK"], result["security_vetoes"])
        self.assertEqual("QUORUM_REACHED_SECURITY_VETO_ACTIVE", result["truth_state"])

    def test_expired_lease_is_rejected(self):
        vote = make_vote("hermes", expires=NOW - timedelta(seconds=1))
        result = self.aggregate([("expired.json", vote)])
        self.assertEqual(0, result["valid_vote_count"])
        self.assertEqual("LEASE_EXPIRED", result["rejected_votes"][0]["reason"])

    def test_wrong_input_digest_is_rejected(self):
        vote = make_vote("hermes", input_digest="0" * 64)
        result = self.aggregate([("wrong-input.json", vote)])
        self.assertEqual("INPUT_DIGEST_MISMATCH", result["rejected_votes"][0]["reason"])

    def test_unverified_identity_is_rejected(self):
        vote = make_vote("hermes")
        vote["participant"]["identity_status"] = "UNVERIFIED"
        vote["output_digest"] = MODULE.vote_output_digest(vote)
        result = self.aggregate([("unverified.json", vote)])
        self.assertEqual("IDENTITY_NOT_VERIFIED", result["rejected_votes"][0]["reason"])

    def test_digest_tampering_is_rejected(self):
        vote = make_vote("hermes")
        vote["recommendations"][0]["decision"] = "TAMPERED_AFTER_SIGNING"
        result = self.aggregate([("tampered.json", vote)])
        self.assertEqual("OUTPUT_DIGEST_MISMATCH", result["rejected_votes"][0]["reason"])

    def test_duplicate_agent_vote_counts_once(self):
        first = make_vote("hermes")
        second = make_vote("hermes", decision="DEFER")
        result = self.aggregate([("a.json", first), ("b.json", second)])
        self.assertEqual(1, result["valid_vote_count"])
        self.assertEqual(1, result["rejected_vote_count"])
        self.assertEqual("DUPLICATE_AGENT_VOTE", result["rejected_votes"][0]["reason"])

    def test_disagreement_is_preserved_without_false_consensus(self):
        votes = [
            ("a.json", make_vote("hermes", decision="ADOPT")),
            ("b.json", make_vote("flashtm8-agent", decision="DEFER")),
        ]
        result = self.aggregate(votes)
        self.assertFalse(result["quorum_reached"])
        self.assertTrue(all(item["majority_decision"] is None for item in result["candidate_results"]))
        self.assertTrue(all(item["state"] == "DISAGREEMENT_OR_INSUFFICIENT_VOTES" for item in result["candidate_results"]))

    def test_output_is_deterministic_across_file_order(self):
        votes = [("z.json", make_vote("hermes")), ("a.json", make_vote("seraphim"))]
        first = self.aggregate(votes)
        second = self.aggregate(list(reversed(votes)))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
