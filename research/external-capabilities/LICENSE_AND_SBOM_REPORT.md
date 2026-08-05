# MSG197 License and SBOM Intake Report

## Scope

This is an intake-level license and provenance report. It verifies the top-level license file at each immutable upstream commit. It is **not** a dependency SBOM and does not authorize installation. Candidate-specific dependency resolution, package-lock capture and vulnerability scanning occur only in disposable canaries.

## Verified top-level licenses

| Repository | Commit | License | License file blob |
|---|---|---|---|
| `donnemartin/system-design-primer` | `ae9bbd7b02d90b9866215de185217d33f39ab733` | CC BY 4.0 | `5a04d642d61db37868f7485fa0fbcc96d8916919` |
| `huangruiteng/loopx` | `22b57a76e18736c31fe749867292f3feeb62f27b` | MIT | `f5746a7eee9f275edd9b23f3ac1af27d02e9cd2d` |
| `TencentCloud/TencentDB-Agent-Memory` | `b44c6db5f5b1a011eed645efb1949840f99f961a` | MIT | `86fd8a122221fc402da9fd64724172d08c6bbbd3` |
| `cloudflare/computer` | `76d9e75c5688713b656bce85540d9e0071cece8b` | MIT | `631c4d3e0ae173bb364ceafd3d8f8e9fef869e8b` |
| `lyogavin/airllm` | `64a4e4fc3749aa7dc9bba4788f560ed0d7e74bd2` | Apache-2.0 | `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` |
| `obra/superpowers` | `44c9b2d6e889982ac18c27d05a19fefe335194e1` | MIT | `abf0390320aa14406af7a520b9b0739fdda9bf08` |
| `addyosmani/agent-skills` | `bdf76c7c6b7b3b3e01bb15c9fdc42ac5351855c1` | MIT | `d67778ada6b9cda6227e9130da182c13e73c8b2e` |
| `uber/ADR` | `73873e18948be7a8637955eeef2f813a541692b8` | Apache-2.0 | `6d772a80340d3ed09a2e272d02727302076d8c2e` |
| `roboflow/supervision` | `bc20dd19fbc7b6cceaec447f1182346ca9158523` | MIT | `ab7110e8f2f73a80097d40f3b6ba6da6ce3d942f` |
| `firecrawl/pdf-inspector` | `12e9a655e36924564057464bf25494b8c027eb57` | MIT | `d5fb797d08725991f833cb9ab303a34542a28f7f` |
| `esengine/DeepSeek-Reasonix` | `77cf9aa7080fb48fec4b6f5ee5d3509748e68c50` | MIT | `bc45a281d8050c59c9b833ea2d0b1fb6e02602c0` |
| `tailwindlabs/tailwindcss` | `3524b4531097fff15962735cdacf56d2af425ead` | MIT | `d6a82290738a9f78946cbcb4594535d6984086dd` |
| `vercel/next.js` | `ab7fc5fb581c396f0116f1a406da17ede2e15440` | MIT | `5948ee9bd0de5064423688a2967ab3111c2658ed` |

## Compatibility observations

- MIT and Apache-2.0 are generally compatible with the public repository's Apache-2.0 license when notices and attribution are preserved.
- CC BY 4.0 applies to the system-design-primer content. Curated excerpts require attribution and change indication. It must not be treated as an executable package or silently relicensed.
- Top-level license compatibility does not prove every bundled model, dataset, font, example, generated asset or transitive package is compatible.

## Candidate-specific SBOM gate

Before a candidate executes, its sandbox branch must produce:

1. CycloneDX or SPDX SBOM for resolved dependencies.
2. Package-manager lockfile or immutable dependency manifest.
3. Source repository and commit.
4. Build tool and runtime versions.
5. Native libraries and external binaries.
6. Model and dataset licenses, when applicable.
7. Container or environment digest.
8. Vulnerability scan with timestamps and severity policy.
9. Secret scan and provenance attestation.
10. Reproducible uninstall inventory.

## Additional rights review

The following need extra review even where the repository license is permissive:

- model weights and model-specific terms used with AirLLM;
- sample videos, images and datasets used with Supervision;
- PDFs and extracted content processed by pdf-inspector;
- third-party skill text or examples embedded by agent-skills or superpowers;
- icons, fonts, examples and plugins in frontend frameworks;
- browser content and account data encountered by computer-use tooling.

## Current verdict

`TOP_LEVEL_LICENSES_VERIFIED_DEPENDENCY_SBOMS_NOT_GENERATED`

No dependency package, binary, model, dataset or framework has been installed by this intake branch.
