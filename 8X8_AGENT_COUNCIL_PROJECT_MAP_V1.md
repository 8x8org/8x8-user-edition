# 8x8 Agent Council Project Map — V1

## Purpose

This document maps each representative council to its agent, canonical repository, project namespace, active missions, and current status. It serves as the human-readable companion to `8X8_AGENT_PROJECT_REGISTRY_V1.json`.

Expand to the full 123+ fleet only after the registry and receipts pass validation.

---

## Council index

| # | Council | Lead Agent | Agent ID | Lane | Health |
|---|---------|-----------|----------|------|--------|
| 1 | Architecture | Arch Prime | 8x8-agent-arch-001 | public_present | ✅ healthy |
| 2 | Security | Sentinel | 8x8-agent-sec-001 | public_present | ✅ healthy |
| 3 | Memory | Mnemos | 8x8-agent-mem-001 | public_present | ✅ healthy |
| 4 | Infrastructure | Fabric | 8x8-agent-infra-001 | public_present | ✅ healthy |
| 5 | Public Product | Prism | 8x8-agent-product-001 | public_present | ✅ healthy |
| 6 | World and Spatial | Atlas | 8x8-agent-world-001 | public_present | ✅ healthy |
| 7 | Studio and Media | Canvas | 8x8-agent-studio-001 | public_present | ✅ healthy |
| 8 | Research and Future Powers | Lumen | 8x8-agent-research-001 | future_lab | ✅ healthy |

---

## 1 · Architecture Council

**Lead:** Arch Prime 🏗️  
**Agent ID:** `8x8-agent-arch-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/architecture`  
**Active missions:** MSG230, MSG231  
**Capabilities:** system_design, api_review, dependency_graph, event_schema  
**Lane:** public_present

Responsibilities: system topology, API contracts, event bus schema, dependency graph, cross-council integration reviews.

---

## 2 · Security Council

**Lead:** Sentinel 🛡️  
**Agent ID:** `8x8-agent-sec-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/security`  
**Active missions:** MSG231  
**Capabilities:** vulnerability_scan, secret_detection, boundary_enforcement, codeql  
**Lane:** public_present

Responsibilities: public information boundary enforcement, CodeQL scanning, secret detection, credential remediation gates, security release verification.

---

## 3 · Memory Council

**Lead:** Mnemos 🧠  
**Agent ID:** `8x8-agent-mem-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/memory`  
**Active missions:** MSG231  
**Capabilities:** context_snapshot, knowledge_graph, retrieval, digest_verification  
**Lane:** public_present

Responsibilities: context snapshot generation and distribution, knowledge graph maintenance, retrieval routing, digest verification.

---

## 4 · Infrastructure Council

**Lead:** Fabric 🕸️  
**Agent ID:** `8x8-agent-infra-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/infrastructure`  
**Active missions:** MSG230, MSG231  
**Capabilities:** ci_cd, deployment, health_probe, rollback  
**Lane:** public_present

Responsibilities: CI/CD pipeline maintenance, deployment lane management, health monitoring, rollback orchestration.

---

## 5 · Public Product Council

**Lead:** Prism 🔷  
**Agent ID:** `8x8-agent-product-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/product`  
**Active missions:** MSG228, MSG229, MSG231  
**Capabilities:** release_train, feature_flag, ux_review, public_safe_projection  
**Lane:** public_present

Responsibilities: public release train, feature flag management, UX review, public-safe projection of agent registry.

---

## 6 · World and Spatial Council

**Lead:** Atlas 🌍  
**Agent ID:** `8x8-agent-world-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/world`  
**Active missions:** MSG231  
**Capabilities:** spatial_modeling, geospatial, world_graph  
**Lane:** public_present

Responsibilities: spatial computing, world modeling, geospatial data integration, Three-Reality Event Bus spatial layer.

---

## 7 · Studio and Media Council

**Lead:** Canvas 🎨  
**Agent ID:** `8x8-agent-studio-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/studio`  
**Active missions:** MSG229, MSG231  
**Capabilities:** visual_design, media_production, art_board, visual_council  
**Lane:** public_present

Responsibilities: visual design system, art board, media production, Visual Council registry (MSG229).

---

## 8 · Research and Future Powers Council

**Lead:** Lumen 🔭  
**Agent ID:** `8x8-agent-research-001`  
**Repository:** `8x8org/8x8-user-edition`  
**Namespace:** `8x8org/8x8-user-edition/projects/research`  
**Active missions:** MSG231  
**Capabilities:** research, hypothesis_testing, capability_intake, future_lab  
**Lane:** future_lab

Responsibilities: emergent capability research, future lab experimentation, MSG197 external-capability intake, hypothesis testing.

---

## Expansion policy

1. Registry schema (`8X8_AGENT_PROJECT_SCHEMA_V1.json`) must pass validation.
2. All eight representative council agents must have receipt hashes.
3. No standalone repositories are created until registry validation passes.
4. Full fleet expansion (123+ agents) requires owner gate and receipt-verified baseline above 50/100.

---

## Handoff

This map was produced as part of MSG231. The next coordinator should:
1. Verify receipt hashes against `MSG231_SHA256SUMS.txt`.
2. Update `sha256:pending` context snapshot digests after first verified context load.
3. Continue Public Present release train as documented in `PUBLIC_PRESENT_RELEASE_TRAIN_STATUS_V1.json`.
