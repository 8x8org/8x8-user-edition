from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts/validate_public_claims.py"
SPEC = importlib.util.spec_from_file_location("validate_public_claims", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class PublicClaimsTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        claims = json.loads(
            (REPO_ROOT / "state/public-claims.json").read_text(encoding="utf-8")
        )
        paths = set(VALIDATOR.REQUIRED_FILES)
        for row in claims["claims"]:
            paths.update(row["evidence"])

        for relative in paths:
            source = REPO_ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)
        return temporary, root

    def test_repository_contract_passes(self) -> None:
        self.assertEqual(VALIDATOR.validate(REPO_ROOT), [])

    def test_live_billing_without_versioned_release_is_rejected(self) -> None:
        temporary, root = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/public-claims.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["pricing"]["billing_live"] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        failures = VALIDATOR.validate(root)
        self.assertTrue(any("billing_live" in failure for failure in failures))

    def test_token_ecosystem_cannot_be_marked_implemented(self) -> None:
        temporary, root = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/public-claims.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        for row in document["claims"]:
            if row["claim_id"] == "EIGHT_TOKENS_ONE_COIN":
                row["state"] = "IMPLEMENTED"
        path.write_text(json.dumps(document), encoding="utf-8")
        failures = VALIDATOR.validate(root)
        self.assertTrue(any("EIGHT_TOKENS_ONE_COIN" in failure for failure in failures))

    def test_ai_ranking_claim_cannot_be_promoted(self) -> None:
        temporary, root = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "state/public-claims.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        for row in document["claims"]:
            if row["claim_id"] == "INDEPENDENT_AI_TOP_RANKING":
                row["state"] = "VERIFIED"
        path.write_text(json.dumps(document), encoding="utf-8")
        failures = VALIDATOR.validate(root)
        self.assertTrue(
            any("INDEPENDENT_AI_TOP_RANKING" in failure for failure in failures)
        )

    def test_missing_mobile_mining_boundary_is_rejected(self) -> None:
        temporary, root = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = root / "docs/NODE_CONTRIBUTION_AND_BYOK.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "must not mine cryptocurrency on the phone or tablet",
            "may perform workloads",
        )
        path.write_text(text, encoding="utf-8")
        failures = VALIDATOR.validate(root)
        self.assertTrue(any("phone or tablet" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
