# MSG197 External Capability Threat Model V1.1

## Protected assets

- owner credentials, signing keys, wallets and recovery material;
- private repositories, messages, memory and phone imports;
- Termux and Ubuntu PRoot services;
- Control Fabric operation registry and authority leases;
- user identity, tenant records and private documents;
- agent prompts, intent, tool calls, arguments and execution traces;
- public release integrity and rollback state;
- storage headroom, battery life and service stability.

## Trust boundaries

1. Untrusted upstream source and release artifacts.
2. Disposable research environment.
3. Candidate adapter process.
4. 8x8 capability broker and policy guardian.
5. Private runtime and data stores.
6. Public client and tenant data plane.
7. External accounts, browsers, models and APIs.

Upstream popularity, organization ownership and permissive licensing do not cross these boundaries automatically.

## Principal threats

### Supply-chain substitution

A repository name, tag or default branch may change. Every experiment must use the canonical repository identity and a full immutable commit SHA. Package registries must also be pinned by version and integrity digest. Floating `main`, `master`, `canary`, `develop` or `feat/server_team` references are forbidden in a release manifest.

### Prompt and skill injection

Knowledge repositories and skill files may contain instructions that attempt to expand authority. Imported text is data, not policy. It cannot override the system prompt, Control Fabric registry, owner gates or capability manifest. Automatic session hooks from skill frameworks remain disabled during static review.

### Competing control planes

LoopX, Reasonix, computer-use tooling and memory frameworks may bring schedulers, state stores, agent registries or remote execution paths. No candidate may become a second source of mission truth, agent identity or authority.

### Agent telemetry capture

Uber ADR is Agentic AI Detection and Response, not architecture-decision-record tooling. Its observability model can capture agent intent, tool use and execution traces. The first 8x8 study must use synthetic traces only. Private prompts, tool arguments, credentials, file contents and production sessions cannot enter a canary. Collection purpose, minimization, retention, redaction, access control, deletion and false-positive handling must be proven before any real telemetry is considered.

### Credential and account capture

Execution and browser tooling can encounter logins, cookies, OAuth tokens and payment pages. Initial canaries use synthetic identities and isolated workspaces only. Credential entry, CAPTCHA handling, purchases, messages, publishing and account changes are prohibited.

### Host and filesystem escape

Candidate code may follow symlinks, mount host roots, traverse paths, invoke shells or read environment variables. Sandboxes require explicit read-only mounts, empty secret environments, bounded working directories and deny-by-default network policy. Cloudflare Computer's full-Linux and real-network backend is treated as critical-risk preview software.

### Malicious or pathological documents

PDF and vision inputs may exploit parsers, trigger decompression bombs or consume excessive CPU, RAM and disk. Input size, page/frame count, wall time, output size and temporary storage must be bounded.

### Resource exhaustion

AirLLM, Supervision, Next.js and large dependency graphs can exhaust phone storage, RAM, GPU memory, battery or CI minutes. Resource feasibility is measured before model or dataset downloads. Phone installation is not the default.

### Remote model code and model rights

AirLLM examples can load model repositories and gated weights. Remote model code, provider tokens, model-specific dependencies and model licenses require independent review. No model download begins until disk, CUDA, cache, removal and rights gates pass.

### Data-retention drift

Memory systems can retain sensitive content after deletion or mix tenants. Synthetic canaries must test create, retrieve, export, delete, expiry, backup and tenant isolation before any private data is considered.

### License and provenance loss

Curated knowledge and copied patterns must preserve source URL, commit, license, attribution and transformation history. No content is republished without the rights required by its license.

### Public/private boundary leakage

Third-party dashboards or adapters must not expose private endpoints, topology, owner identifiers, raw receipts, secrets, private memory or agent telemetry through public routes.

## Mandatory controls

- immutable upstream commit pins;
- license-file blob hashes;
- candidate-specific SBOM before execution;
- vulnerability and secret scanning;
- no production credentials in sandboxes;
- network and domain allowlists;
- CPU, RAM, disk, wall-time and process limits;
- explicit capability manifest;
- deterministic input and output schemas;
- structured logs with secret-shaped redaction;
- telemetry minimization, retention and deletion tests;
- kill switch and lease expiry;
- uninstall and rollback rehearsal;
- post-run process, port, file and network cleanup census.

## Candidate risk tiers

| Tier | Candidates | Required environment |
|---|---|---|
| Low | system-design-primer | Read-only curation without execution |
| Medium | Tailwind | Static review or disposable build sandbox |
| High | TencentDB Agent Memory, AirLLM, Supervision, pdf-inspector, LoopX, agent-skills, superpowers, Uber ADR, Next.js | Isolated branch and disposable environment with strict limits |
| Critical | Cloudflare Computer, Reasonix | Synthetic-only sandbox, explicit owner gate, zero credentials and no private mounts |

## Release vetoes

A candidate is rejected or deferred when any of these remains unresolved:

- unknown or incompatible license;
- unbounded shell, browser, filesystem or network authority;
- no reproducible uninstall;
- secret or private-data requirement for the first canary;
- duplicate control-plane ownership;
- resource demand above the declared node ceiling;
- missing tenant isolation, telemetry minimization or deletion semantics;
- public/private boundary failure;
- vulnerability without accepted mitigation;
- no owner-approved exact release target.
