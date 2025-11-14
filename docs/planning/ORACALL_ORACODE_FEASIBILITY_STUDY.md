# ORACall + ORACode Joint Feasibility Study

**Classification**: PEI-Control / Feasibility Assessment  
**Prepared By**: CodeSentinel Agent Team  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Executive Summary

ORACall (PEI protocol enforcement) and ORACode (semantic overlay) share infrastructure touchpoints (CLI, SessionMemory, ORACL tiers, archive pipeline). A combined rollout is feasible within a six-week window provided that schema work (ORACall) precedes semantic registry design (ORACode) by one sprint. No critical blockers identified; primary risks relate to signature management, vocabulary drift, and storage scaling. Recommended path: proceed with phased implementation using shared governance board.

---

## 2. Evaluation Scope

| Domain | Included Elements | Excluded Elements |
|--------|-------------------|-------------------|
| Technical | CLI commands, schema validators, TRIAD indexing, semantic registry | External SIEM exports, hardware roots of trust |
| Operational | Process monitoring hooks, documentation, training, Calamum harness | Third-party certification, user-facing GUIs |
| Governance | SEAM controls, signature policies, archive compliance | Corporate legal alignment (future review) |

---

## 3. Methodology & Scoring Model

- **Scoring Scale**: 1 (high risk) to 5 (low risk / high readiness).
- **Criteria**: Architecture readiness, resource availability, dependency clarity, security impact, delivery speed.
- **Approach**: Workshops with CLI + ORACL maintainers, review of planning docs, delta analysis between ORACall and ORACode components.

| Criterion | ORACall Score | ORACode Score | Notes |
|-----------|---------------|---------------|-------|
| Architecture Readiness | 4 | 3 | ORACall schema outlined; ORACode DSL still conceptual. |
| Resource Availability | 4 | 4 | Same dev pod can handle both with staggered sprints. |
| Dependency Clarity | 3 | 3 | Need finalized schema to unblock semantic references. |
| Security Impact | 5 | 4 | Controls reusable; ORACode needs ACL extension. |
| Delivery Speed | 4 | 3 | CLI groundwork exists; semantics tooling net-new. |

---

## 4. Technical Feasibility Analysis

1. **Shared Infrastructure**: SessionMemory, ORACL tiers, and TRIAD index satisfy both efforts without redesign; code reuse >70% expected for persistence/logging.
2. **Schema Dependency**: ORACode requires stable ORACall identifiers and stage taxonomy. Once `oracall_schema.py` lands, semantic tagging can reference it via import.
3. **Tooling**: Existing CLI modular pattern (`*_utils.py`) supports new command groups (`oracall`, `oracode`) with minimal boilerplate.
4. **Data Stores**: JSONL + TRIAD index scale adequately; semantic annotations add <10% storage overhead assuming compressed JSON fragments.
5. **Testing**: Calamum harness can extend to both features by parameterizing scenario templates.

---

## 5. Operational Readiness

- **Process Alignment**: Newly added process-management commands (detail/kill/snapshot) already provide telemetry hooks required for PEI incidence correlation.
- **Documentation**: Pre-implementation brief, implementation plan, and proposals exist; need to link feasibility study into `SESSION_TIMELINE` doc.
- **Training**: Operator onboarding runbooks pending but can reuse CLI quick reference format.

---

## 6. Schedule & Milestones

| Week | Milestone | Dependencies |
|------|-----------|--------------|
| Week 1 | Finalize ORACall schema + JSON models | None (in-flight) |
| Week 2 | Build `oracall ingest` + scaffold commands | Schema complete |
| Week 3 | Implement TRIAD index + archive wiring | CLI ingestion ready |
| Week 4 | Develop ORACode lexical registry + validator | ORACall identifiers stable |
| Week 5 | Implement `oracode annotate/query` CLI + SessionMemory caching | Registry complete |
| Week 6 | Integration tests + Calamum harness, documentation sign-off | Both pipelines functional |

---

## 7. Resource & Tooling Estimate

| Role | Effort (person-weeks) | Notes |
|------|----------------------|-------|
| Lead Engineer | 3.0 | Oversees schema, TRIAD, CLI integration |
| Security Engineer | 1.5 | Signature policy, ACL extensions |
| Documentation Specialist | 0.5 | Runbooks, operator guides |
| QA / Calamum Author | 1.0 | Test harness scenarios |
| Total | 6.0 | Fits within two-sprint window with overlapping tasks |

Tooling impacts: no new third-party dependencies; reuse Ed25519 libs already approved. Optional: SQLite or LMDB for TRIAD delta cache (already vetted).

---

## 8. Risk Register & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Signature key sprawl | Medium | High | Centralize keys in workspace vault, enforce rotation job. |
| Vocabulary drift between ORACall stages and ORACode tokens | Medium | Medium | Create shared taxonomy file and lint both pipelines against it. |
| Storage hot spots under TRIAD radix | Low | Medium | Add nightly compaction + telemetry alert if shard exceeds threshold. |
| Operator adoption lag | Medium | Low | Deliver training runbook + screencast during Week 5. |
| Dual-report SLA violations | Low | High | CLI guardrails + Calamum scenario to simulate missing reports. |

---

## 9. Dependency Alignment

- **SessionMemory Enhancements**: No changes required; ensure cache invalidation hooks exposed for semantic updates.
- **ORACL Context Tier**: Needs minor update to ingest ORACode aggregated metrics (stories sized <0.5 PW).
- **Archive Policy**: Existing archive-first enforcement sufficient; add manifest entries for semantics references.
- **Metrics Streams**: `docs/metrics/agent_operations.jsonl` and `security_events.jsonl` gain new event types; schema updates included in Week 2 deliverables.

---

## 10. Decision Gates & Success Metrics

| Gate | Criteria | Owner |
|------|----------|-------|
| G1 — Schema Sign-off | ORACall EBNF + JSON schema approved by SEAM board | Lead Engineer |
| G2 — Security Controls | Key management, ACL policies validated | Security Engineer |
| G3 — Integrated Demo | CLI ingest + annotate flow demoed with Calamum tests | QA Lead |
| G4 — Documentation Complete | Runbooks + planning docs linked in `SESSION_TIMELINE` | Documentation Specialist |

**Success Metrics**:

- 100% PEI events contain dual reports + semantics reference.
- TRIAD lookup latency < 50ms at 95th percentile.
- ≥90% operator tasks resolved via SessionMemory cache hits.
- Zero unresolved tamper alerts during pilot week.

---

## 11. Recommendations & Next Actions

1. Approve combined rollout pending Gate G1 completion.
2. Spin up shared taxonomy working group (CLI + ORACL maintainers) during Week 1.
3. Begin authoring Calamum scenarios early to validate guardrails concurrently.
4. Schedule operator training session for Week 5 once CLI syntax finalized.

---

## 12. Appendices

- Related docs: `ORACALL_PEI_PREIMPLEMENTATION_BRIEF.md`, `ORACALL_PEI_IMPLEMENTATION_PLAN.md`, `ORACALL_FRAMEWORK_PROPOSAL.md`, `ORACODE_SEMANTICS_PROPOSAL.md`.
- All new files adhere to ASCII-only console requirements; Markdown may include UTF-8 but currently uses ASCII.
