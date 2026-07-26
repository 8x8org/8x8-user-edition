"""Unit tests for scripts/validate_public_state.py"""

import json
import sys
from pathlib import Path

import pytest

# Make the scripts package importable without installation.
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_public_state import (  # noqa: E402
    FORBIDDEN_HTML_TERMS,
    MUST_BE_FALSE_KEYS,
    REQUIRED_FILES,
    check_html_content,
    check_public_state,
    check_required_files,
    run_checks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_repo(tmp_path: Path) -> Path:
    """Create a minimal valid repository layout under *tmp_path*."""
    # Required files
    (tmp_path / "state").mkdir(parents=True)
    for rel in REQUIRED_FILES:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("placeholder")

    # Minimal public-state.json with all boundary keys set to False
    state = {key: False for key in MUST_BE_FALSE_KEYS}
    (tmp_path / "state" / "public-state.json").write_text(json.dumps(state))

    # Benign index.html
    (tmp_path / "index.html").write_text("<html><body>Hello world</body></html>")

    return tmp_path


# ---------------------------------------------------------------------------
# check_required_files
# ---------------------------------------------------------------------------

class TestCheckRequiredFiles:
    def test_all_present_returns_empty(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        assert check_required_files(root) == []

    def test_single_missing_file_reported(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        (root / "index.html").unlink()
        missing = check_required_files(root)
        assert "index.html" in missing

    def test_multiple_missing_files_all_reported(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        (root / "styles.css").unlink()
        (root / "app.js").unlink()
        missing = check_required_files(root)
        assert "styles.css" in missing
        assert "app.js" in missing


# ---------------------------------------------------------------------------
# check_public_state
# ---------------------------------------------------------------------------

class TestCheckPublicState:
    def test_all_false_returns_empty(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        assert check_public_state(root) == []

    def test_true_value_detected(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        state["remote_shell_enabled"] = True
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        violations = check_public_state(root)
        assert "remote_shell_enabled" in violations

    def test_missing_key_detected(self, tmp_path):
        """A key absent from the JSON should also be flagged (not False)."""
        root = _make_valid_repo(tmp_path)
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        del state["credentials_included"]
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        violations = check_public_state(root)
        assert "credentials_included" in violations

    def test_null_value_detected(self, tmp_path):
        """null (None) is not the same as False and must be flagged."""
        root = _make_valid_repo(tmp_path)
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        state["live_trading_enabled"] = None
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        violations = check_public_state(root)
        assert "live_trading_enabled" in violations

    def test_multiple_violations_all_reported(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        state["wallet_material_included"] = True
        state["hidden_telemetry_enabled"] = True
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        violations = check_public_state(root)
        assert "wallet_material_included" in violations
        assert "hidden_telemetry_enabled" in violations


# ---------------------------------------------------------------------------
# check_html_content
# ---------------------------------------------------------------------------

class TestCheckHtmlContent:
    def test_clean_html_returns_empty(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        assert check_html_content(root) == []

    @pytest.mark.parametrize("term", FORBIDDEN_HTML_TERMS)
    def test_each_forbidden_term_detected(self, tmp_path, term):
        root = _make_valid_repo(tmp_path)
        (root / "index.html").write_text(f"<html>{term}</html>")
        matches = check_html_content(root)
        assert term in matches

    def test_case_insensitive_match(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        (root / "index.html").write_text("<html>SEED PHRASE</html>")
        matches = check_html_content(root)
        assert "seed phrase" in matches


# ---------------------------------------------------------------------------
# run_checks (integration)
# ---------------------------------------------------------------------------

class TestRunChecks:
    def test_valid_repo_exits_zero(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        assert run_checks(root) == 0

    def test_missing_file_exits_nonzero(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        (root / "sw.js").unlink()
        assert run_checks(root) != 0

    def test_boundary_violation_exits_nonzero(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        state["private_control_plane_connected"] = True
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        assert run_checks(root) != 0

    def test_forbidden_content_exits_nonzero(self, tmp_path):
        root = _make_valid_repo(tmp_path)
        (root / "index.html").write_text("<html>execute trade</html>")
        assert run_checks(root) != 0

    def test_all_errors_accumulate(self, tmp_path):
        """run_checks should not short-circuit; all failures are reported."""
        root = _make_valid_repo(tmp_path)
        (root / "SECURITY.md").unlink()
        state = {key: False for key in MUST_BE_FALSE_KEYS}
        state["wallet_material_included"] = True
        (root / "state" / "public-state.json").write_text(json.dumps(state))
        (root / "index.html").write_text("<html>private key</html>")
        assert run_checks(root) != 0
