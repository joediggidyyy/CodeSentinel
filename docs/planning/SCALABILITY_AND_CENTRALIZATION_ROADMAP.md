# Scalability, Centralization, and Data Collection Roadmap

**Classification**: PEI-Control / Strategic Planning  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Objectives

This roadmap describes how ORACall and ORACode will scale from early deployments to large, multi-tenant environments while preserving SEAM (Security, Efficiency, And Minimalism) and non-destructive policies. It focuses on:

- Storage and query scalability for ORACall/ORACode data.
- Centralized observability and data collection across satellites.
- Evolution from repo-local artifacts to optional central services.
- Timelines and effort estimates for each phase.

Assumptions and estimates are explicitly stated and intended for iteration, not rigid commitment.

---

## 2. Scalability Phases

### Phase 1 (0–6 months): Repository-Local Foundations

### Phase 1 Scope

- Single-team or small multi-team deployments.
- ORACall and ORACode operate against repository-local JSONL logs and TRIAD indexes.
- Calamum harness validates performance under target loads (hundreds of events per day).

### Phase 1 Key Capabilities

- Append-only JSONL logs for ORACall and ORACode data.
- TRIAD indexing with nightly compaction.
- SessionMemory for per-operator caching.
- Minimal metrics aggregation via JSONL streams in `docs/metrics/`.

### Phase 1 Effort & Timeline

- Already covered by the initial six-week ORACall/ORACode implementation plan.
- No additional infrastructure beyond the current repo and CI is required.

### Phase 2 (6–18 months): Consolidated Organization-Level View

### Phase 2 Scope

- Multiple repositories and teams within a single organization.
- Need for consolidated reporting on PEI events and semantics across projects.

### Phase 2 Key Capabilities

- **Central Aggregation Service (Optional)**:
  - Periodically ingests JSONL and TRIAD metadata from multiple repos.
  - Builds organization-level dashboards (e.g., Grafana) for PEI events, semantics, and security incidents.
- **Standardized Export Pipelines**:
  - CLI commands (`codesentinel oracall export`, `codesentinel oracode export`) to produce sanitized bundles.
  - Signed manifests to guarantee integrity across transports.

### Phase 2 Effort & Timeline

- 3–4 person-months for a small team to:
  - Define export formats and signing requirements.
  - Implement aggregation service (initially read-only).
  - Add basic dashboards and alerts.
- This phase can be staged on top of Phase 1 without disrupting existing workflows.

### Phase 3 (18–36 months): Federated, Multi-Tenant Centralization

### Phase 3 Scope

- Multiple organizations or business units sharing central services.
- Requirements for tenant isolation, access control, and cross-tenant analytics.

### Phase 3 Key Capabilities

- **Federated Indexing Layer**:
  - Logical view across multiple TRIAD and SEAMLog stores.
  - Query router ensures tenant boundaries and rate limits.
- **Central Policy Engine**:
  - Defines global SEAM policies, vocabulary registries, and conflict-resolution templates.
- **Streaming Integration** (Optional):
  - Real-time event forwarding to central services for near-real-time analytics.

### Phase 3 Effort & Timeline

- 6–9 person-months, including:
  - Design and implementation of the federated index.
  - Hardening of authentication and authorization layers.
  - Performance testing for cross-tenant workloads.

These durations assume a small, focused team and can be parallelized with feature work.

---

## 3. Data Collection and Centralization Strategy

### 3.1 Near-Term (Phase 1)

- Rely on repository-local JSONL and TRIAD indexes.
- Use Calamum to validate that performance targets are met under expected loads.
- Provide simple, documented patterns for exporting slices of logs for external analysis.

### 3.2 Mid-Term (Phase 2)

- Introduce standardized export commands with signed manifests.
- Define a minimal central aggregator:
  - Reads exports from multiple repos.
  - Produces organization-level metrics and alerts.
- Maintain the ability to operate in "local-only" mode for sensitive deployments.

### 3.3 Long-Term (Phase 3)

- Implement federated indexing and optional real-time streaming.
- Introduce a central policy engine and registry replication for ORACode semantics.
- Maintain SEAM by ensuring that centralization never requires abandoning archive-first or non-destructive policies.

---

## 4. Resource and Cost Considerations

All estimates below assume a blended engineering cost (for example, a notional rate) and should be refined with organization-specific data.

| Phase | Duration (months) | Core Roles | Notes |
|------|-------------------|-----------|-------|
| 1 | 0–6 (already planned) | Existing ORACall/ORACode team | No extra infra beyond current repo and CI |
| 2 | 6–18 | 2–3 engineers, 1 SRE, 0.5 product | Build central aggregator and export tooling |
| 3 | 18–36 | 3–4 engineers, 1–2 SRE, 1 security architect | Design federated index and policy engine |

Cost drivers:

- Storage and compute for central aggregation (cloud or on-premises).
- SRE and security time for hardening and monitoring.
- Maintenance of schema and registry compatibility as volume grows.

---

## 5. Risks and Challenges

- **Data Volume Growth**: Rapid increase in PEI events may outpace initial TRIAD configurations.
  - Mitigation: Monitor volume early; plan shard and compression strategies.
- **Centralization Risk**: Single aggregation service may become a critical dependency.
  - Mitigation: Design for graceful degradation; keep local-only paths viable.
- **Policy Drift**: Different teams may interpret semantics or PEI stages differently.
  - Mitigation: Use a central registry and linting; promote shared vocabulary governance.
- **Cross-Tenant Isolation**: In multi-tenant deployments, risks of data leakage.
  - Mitigation: Tenancy-aware index routing, strict ACLs, and dedicated Calamum scenarios.

---

## 6. Market Expansion and Adoption (High-Level)

- **Early Adopters (0–12 months)**:
  - Security-focused teams and regulated organizations.
  - Primary value: Strong audit trails and SEAM-aligned PEI reporting.
- **Growth Stage (12–24 months)**:
  - Broader engineering and operations teams seeking integrated PEI analytics.
  - Value: Consolidated dashboards and federated reasoning across projects.
- **Mature Stage (24–36 months)**:
  - Multi-tenant deployments across business units or external customers.
  - Value: Central policy engine, cross-tenant insights, and advanced analytics.

These stages align with the technical phases and can be adjusted as real adoption data becomes available.

---

## 7. Next Steps

1. Finalize ORACall and ORACode implementation (Phase 1 baseline).
2. Design export schemas and signing workflow for Phase 2.
3. Prototype a minimal aggregation service and dashboards.
4. Use Calamum to stress-test centralization components under realistic workloads.
5. Reassess timelines and resource needs as adoption and data volume become clearer.
