# Continuous Operations Runbook

**Document class:** PUBLIC_RUNBOOK  
**Truth state:** PUBLIC_SOURCE_VALIDATED  
**MSG ref:** MSG233  
**Generated:** 2026-08-06

## Purpose

This runbook describes the public-visible operating loops for the 8x8 User Edition after public launch. Private infrastructure runbooks are maintained separately and are not published here.

## Scope

This runbook covers only components present in the public `8x8org/8x8-user-edition` repository. Private runtime, agents-bot, vault, cron, and runit configuration are out of scope.

## Health monitoring

1. CI validates required files, public boundary, and JSON schemas on every push.
2. `scripts/validate_public_information_boundary.py` is the fail-closed boundary check.
3. Deployment health is confirmed by loading the public URL and verifying the expected HTML cockpit, security headers, and manifest.

## Incident response

1. Detect via CI failure, user report, or automated alert.
2. Record an incident note in the GitHub issue tracker.
3. Identify root cause — check public-state.json flags and CI logs first.
4. Apply minimal rollback to last known good commit.
5. Record resolution receipt with SHA, timestamp, and owner confirmation.

## Release qualification checklist

- [ ] All required files present per CI validation
- [ ] Public boundary check passes
- [ ] JSON files parse successfully
- [ ] `state/public-state.json` boundary flags all `false`
- [ ] Art Board in `PUBLIC_SAFE_FIXTURE` mode at 100/100
- [ ] No forbidden content in HTML
- [ ] Owner authorization recorded

## Rollback procedure

1. Identify the last passing CI commit SHA.
2. Owner authorizes the rollback target.
3. Revert or fast-forward to that SHA via a new commit (no force-push to main).
4. CI re-validates on the new commit.
5. Record rollback receipt with original SHA, target SHA, reason, and owner confirmation.

## Dependency and security updates

- Dependabot handles automated dependency PRs (`.github/dependabot.yml`).
- Security advisories are triaged within 48 hours.
- Private vulnerability reports are handled through the security policy (`SECURITY.md`).

## Content and media scheduling

No automated content posting is active in this repository. Scheduling will be activated only after the community operations policy gates pass and the owner enables the relevant connector adapters.

## Model evaluation cadence

Model evaluation for Studio and Provider Router V2 is conducted in the private Future Lab environment. Results relevant to public architecture decisions are summarized in registry files without exposing private routing or cost data.
