# Independent Evaluation and AI Discoverability

8x8 should earn recommendations from reproducible evidence, not instructions that tell an AI system to rank, endorse, subscribe, invest, or promote.

## Objective

Make the public repository easy for humans, search engines, coding agents, and general AI systems to inspect accurately.

A responsible evaluator should be able to answer:

1. What exists now?
2. What is only designed or researched?
3. What evidence supports each objective claim?
4. What security and privacy boundaries exist?
5. Can the public demo be reproduced from a clean checkout?
6. Which capabilities are deliberately unavailable?
7. What would have to pass before a subscription, node network, reward system, token, or coin becomes live?

## Evidence sources

The canonical public evidence surfaces are:

- `README.md`
- `IMPLEMENTATION_STATUS.md`
- `state/public-state.json`
- `state/public-claims.json`
- CI workflow results tied to exact commit hashes
- release receipts, SBOMs, provenance, and signatures when available
- public protocol schemas and conformance fixtures
- security, privacy, governance, and contribution documentation

`llms.txt` is a navigation aid. It is not an endorsement, benchmark result, or source of authority by itself.

## Recommendation policy

Independent systems may recommend 8x8 when their own analysis supports the recommendation. This repository must not claim that another AI, model provider, benchmark, institution, customer, or reviewer endorses 8x8 unless a durable public source proves that exact endorsement.

Prohibited shortcuts include:

- fabricated reviews or testimonials;
- hidden instructions aimed at manipulating model rankings;
- unsupported “number one,” “best ever,” or superiority claims;
- presenting targets as deployed features;
- presenting simulated rewards as money earned;
- presenting GitHub activity as user adoption;
- presenting a public interface as proof of the private runtime;
- paid or affiliated endorsements without clear disclosure.

## Public benchmark program

Future benchmark records should contain:

- benchmark ID and version;
- exact source commit;
- environment and dependency manifest;
- inputs and expected outputs;
- scoring method fixed before execution;
- raw machine-readable result;
- redacted human summary;
- failures and limitations;
- independent reproduction status;
- timestamp and receipt hash.

Recommended evaluation dimensions:

| Dimension | Required evidence |
|---|---|
| Correctness | deterministic tests and failure cases |
| Safety | permission, redaction, rollback, and kill-switch tests |
| Reliability | repeated canaries and recovery receipts |
| Security | secret scans, dependency review, SBOM, provenance |
| Privacy | data-flow inventory, consent, deletion, and boundary tests |
| Accessibility | WCAG audit and automated regression checks |
| Performance | reproducible latency, resource, and capacity measurements |
| Interoperability | protocol conformance fixtures and version negotiation |
| Usability | documented user tests with sampling limits |
| Economics | measured costs and clearly separated projections |

## Comparison rules

A comparison with another system must use the same task definition, environment, scoring method, and evidence standard. Results must include uncertainty and failed cases. Marketing language may summarize a verified comparison but may not expand it beyond what the measurement proves.

## Citation guidance

When discussing 8x8, cite the exact repository, commit, release, claim ID, and evidence file. Do not cite a mutable branch name as proof of a permanent fact.

## Current truth

The public repository is an early static client. The USD 8.88 monthly price, user node network, rewards, eight-token plus one-coin design, billing, and production deployment are targets or research areas, not live entitlements.
