"""validate_public_state.py – v1.0.0

Reproduces the public-boundary checks previously inlined in
.github/workflows/validate-public-beta.yml:

1. Required files must be present on disk.
2. Defined keys in state/public-state.json must be explicitly False.
3. index.html must not contain any forbidden content strings.

Exit codes
----------
0  all checks pass
1  one or more checks failed
"""

import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.webmanifest",
    "icon.svg",
    "sw.js",
    "vercel.json",
    "state/public-state.json",
    "README.md",
    "ARCHITECTURE.md",
    "IMPLEMENTATION_STATUS.md",
    "SECURITY.md",
]

MUST_BE_FALSE_KEYS = [
    "private_control_plane_connected",
    "private_repositories_connected",
    "private_memory_connected",
    "private_messages_connected",
    "credentials_included",
    "wallet_material_included",
    "remote_shell_enabled",
    "live_trading_enabled",
    "public_billing_enabled",
    "user_node_contribution_enabled",
    "hidden_telemetry_enabled",
    "camera_or_microphone_auto_access",
    "targets_are_live_entitlements",
]

FORBIDDEN_HTML_TERMS = [
    "seed phrase",
    "private key",
    "api_key=",
    "authorization: bearer",
    "/api/terminal",
    "execute trade",
    "wallet address",
]


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_required_files(root: Path) -> list[str]:
    """Return a list of paths that are missing relative to *root*."""
    return [p for p in REQUIRED_FILES if not (root / p).is_file()]


def check_public_state(root: Path) -> list[str]:
    """Return keys whose values are not exactly False in public-state.json."""
    state_path = root / "state" / "public-state.json"
    state = json.loads(state_path.read_text())
    return [key for key in MUST_BE_FALSE_KEYS if state.get(key) is not False]


def check_html_content(root: Path) -> list[str]:
    """Return forbidden terms found in index.html (case-insensitive)."""
    html = (root / "index.html").read_text().lower()
    return [term for term in FORBIDDEN_HTML_TERMS if term in html]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_checks(root: Path) -> int:
    """Execute all checks and print results.  Returns the exit code."""
    failed = False

    missing = check_required_files(root)
    if missing:
        print(f"ERROR – Missing required files: {missing}", file=sys.stderr)
        failed = True

    violations = check_public_state(root)
    if violations:
        print(f"ERROR – Public boundary violation: {violations}", file=sys.stderr)
        failed = True

    forbidden = check_html_content(root)
    if forbidden:
        print(f"ERROR – Forbidden public content: {forbidden}", file=sys.stderr)
        failed = True

    if not failed:
        print("PUBLIC_BETA_VALIDATION=PASS")
    return 1 if failed else 0


def main() -> None:
    root = Path(__file__).parent.parent
    sys.exit(run_checks(root))


if __name__ == "__main__":
    main()
