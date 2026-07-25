# Contributing to 8x8 User Edition

Thank you for your interest. This repository is the **public demo cockpit** of 8x8 OS. It is intentionally small, static and public-safe, and contributions must keep it that way.

## Before you start — license status

This repository currently has **no license**. Until the owner publishes one:

- default copyright applies to the existing code;
- we cannot yet define the license your contribution would be released under;
- substantial code contributions may therefore be held (not merged) until the license decision lands.

Small fixes (typos, accessibility, documentation accuracy) are still welcome; by submitting a pull request you agree the project may license your contribution under the license the owner later selects.

## What contributions are welcome

- accuracy corrections to documentation (claims must match evidence);
- accessibility and mobile-layout improvements;
- performance and correctness fixes to the static cockpit;
- improvements to the validation workflow;
- translations of public documentation.

## Hard boundaries — will be rejected

A pull request must **never** add:

- credentials, tokens, API keys, cookies or authorization headers (real or realistic);
- wallet material, seed phrases or signing authority;
- private hostnames, internal paths, device topology or raw logs;
- code that calls external APIs, collects telemetry or executes remote commands;
- claims that a capability exists without evidence (see the ladder in [ARCHITECTURE.md](ARCHITECTURE.md));
- a `LICENSE` file (owner decision pending — see above);
- links to unverified social-media accounts.

## Workflow

1. Fork and create a topic branch; do not target `main` directly from a shared branch.
2. Keep the app dependency-free: no build step, no package manager, no external CDN assets.
3. Run the checks locally before opening a PR:

   ```bash
   python3 -m json.tool state/public-state.json
   python3 -m json.tool manifest.webmanifest
   python3 -m json.tool vercel.json
   python3 -m http.server 8080   # then load the cockpit in a browser
   ```

4. Open the pull request as a **draft** first. The `Validate Public Beta` workflow must pass.
5. A maintainer reviews for the boundaries above before anything is merged.

## Reporting security issues

Do **not** open a public issue for vulnerabilities. Follow [SECURITY.md](SECURITY.md) and never include a real secret value in a report.
