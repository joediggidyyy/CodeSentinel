# ORACall + ORACode Comprehensive Proposal Package

**Classification**: PEI-Control / Integrated Proposal  
**Prepared By**: CodeSentinel Agent Team  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## Table of Contents

- [ORACall + ORACode Comprehensive Proposal Package](#oracall--oracode-comprehensive-proposal-package)
  - [Table of Contents](#table-of-contents)
  - [1. Executive Summary](#1-executive-summary)
  - [2. Source Document Inventory](#2-source-document-inventory)
  - [3. Integrated Consistency Review](#3-integrated-consistency-review)
    - [3.1 Mission \& Scope Alignment](#31-mission--scope-alignment)
    - [3.2 Timeline \& Dependencies](#32-timeline--dependencies)
    - [3.3 Security Posture](#33-security-posture)
    - [3.4 Offline \& Non-Agent Operation](#34-offline--non-agent-operation)
  - [4. Risk, Assumption, and Issue Register](#4-risk-assumption-and-issue-register)
  - [5. ORACall Pre-Implementation Baseline](#5-oracall-pre-implementation-baseline)
  - [6. ORACall Implementation Plan Snapshot](#6-oracall-implementation-plan-snapshot)
  - [7. ORACall Framework Overview](#7-oracall-framework-overview)
  - [8. ORACode Semantics \& Storage Strategy](#8-oracode-semantics--storage-strategy)
  - [9. Feasibility \& Resourcing Summary](#9-feasibility--resourcing-summary)
  - [10. Performance Audit (Agent and Non-Agent Modes)](#10-performance-audit-agent-and-non-agent-modes)
    - [10.1 Objectives](#101-objectives)
    - [10.2 Scope](#102-scope)
    - [10.3 Metrics (Baseline Targets)](#103-metrics-baseline-targets)
    - [10.4 Test Harnesses](#104-test-harnesses)
    - [10.5 Security-Focused Performance Checks](#105-security-focused-performance-checks)
    - [10.6 Reporting and Regression Gates](#106-reporting-and-regression-gates)
  - [11. Calamum Test Harness Integration](#11-calamum-test-harness-integration)
    - [11.1 Role in ORACall](#111-role-in-oracall)
    - [11.2 Role in ORACode](#112-role-in-oracode)
    - [11.3 Agent and Non-Agent Scenarios](#113-agent-and-non-agent-scenarios)
    - [11.4 Security and SEAM Alignment](#114-security-and-seam-alignment)
  - [12. Appendices](#12-appendices)
    - [Appendix A — Document Summaries & Links](#appendix-a--document-summaries--links)
    - [Appendix B — Security Justifications](#appendix-b--security-justifications)
    - [Appendix C — Outstanding Decisions & Follow-Ups](#appendix-c--outstanding-decisions--follow-ups)

---

## 1. Executive Summary

A holistic review of the ORACall (PEI event capture) and ORACode (semantic overlay) artifacts confirms that the mission, scope, and timelines remain internally consistent. Security-first design is evident across all documents—dual-report requirements, Ed25519 signatures, ACL-based command gating, conflict auditing, and archive-first storage. Remaining open items cluster around execution details (key vault ops, external integrations, storage format selection, SEAMLog evaluation). No blocking contradictions or hidden assumptions were identified; however, several decisions require formal sign-off before development begins. Proceeding with the outlined six-week rollout is feasible if the highlighted actions in Section 4 are tracked to completion.

---

## 2. Source Document Inventory

| Document | Purpose | Owner | Notes |
|----------|---------|-------|-------|
| `ORACALL_PEI_PREIMPLEMENTATION_BRIEF.md` | Establish objectives, scope, dependencies, and risks before implementation | SEAM Board Liaison | Defines dual-report, schema, and archival requirements |
| `ORACALL_PEI_IMPLEMENTATION_PLAN.md` | Detail architecture layers, phased execution, testing, and SEAM controls | Lead Engineer | Six-week plan including TRIAD index + Calamum harness |
| `ORACALL_FRAMEWORK_PROPOSAL.md` | Describe framework vision, core components, workflow, and roadmap | ORACL Program Manager | Lists open questions on integrations and SLAs |
| `ORACODE_SEMANTICS_PROPOSAL.md` | Outline semantics mission, governance, conflict resolution, storage study | ORACode Working Group | Includes SEAMLog feasibility track |
| `ORACALL_ORACODE_FEASIBILITY_STUDY.md` | Score viability, schedule, resources, and risks for joint rollout | Strategy & Ops Team | Confirms combined plan is achievable in six weeks |

_All original documents remain unchanged in `docs/planning/`._

---

## 3. Integrated Consistency Review

### 3.1 Mission & Scope Alignment

- All artifacts target SEAM-compliant PEI recording (ORACall) plus semantic enrichment (ORACode).
- Both initiatives rely on shared infrastructure (CLI modular pattern, SessionMemory, ORACL Context/Intelligence tiers, TRIAD indexing, archive policy) ensuring minimal duplication.

### 3.2 Timeline & Dependencies

- Pre-implementation brief, implementation plan, and feasibility study each describe a six-week rollout with identical milestone ordering (schema → ingestion → storage → security → testing → rollout).
- ORACode tasks explicitly depend on ORACall schema completion, matching the dependency analysis in the feasibility study.

### 3.3 Security Posture

- Dual-report enforcement, Ed25519 signatures, ACLs, tamper logging, and archive-first policies are reiterated in every document.
- ORACode proposal adds independent auditor conflict resolution plus centrally curated vocabularies, aligning with SEAM priorities.

### 3.4 Offline & Non-Agent Operation

- Semantics registry distribution, TRIAD logs, and metrics files are all repo-hosted, enabling full functionality without live agent integrations—consistent across all documents.

_No conflicting directives were found. Outstanding questions are tracked in Section 4 and Appendix C._

---

## 4. Risk, Assumption, and Issue Register

| ID | Item | Impact | Current Mitigation / Action |
|----|------|--------|-----------------------------|
| R1 | Key management & rotation specifics for Ed25519 signing not yet codified | High | Define vault workflow + rotation cadence before Week 2; add to security checklist |
| R2 | Vocabulary release automation (diff manifest generation) unspecified | Medium | Assign tooling update in Week 1 alongside registry creation |
| R3 | External incident tracker integration decision pending (Framework Q1) | Medium | Evaluate during Week 4 once ingestion stabilizes; can remain optional if APIs not ready |
| R4 | Dual-report SLA by severity (Framework Q2) | Medium | Policy board to set SLA matrix; defaults to universal SLA until decided |
| R5 | Partner satellite exposure method (API vs file drop) unresolved (Framework Q3) | Medium | Pilot with repo-based file drops; revisit API after rollout |
| R6 | Storage format study + SEAMLog evaluation outstanding | Medium | Execute study plan in P2–P4; document results in `ORACODE_STORAGE_STUDY.md` |
| R7 | Calamum harness scenarios for ORACode conflict replay not yet authored | Medium | QA lead to script scenarios during Week 5 |
| R8 | `codesentinel oracall compact` operational procedures undefined | Low | Document CLI behavior in runbooks before enabling command |

_No critical security holes identified; risks focus on execution clarity._

---

## 5. ORACall Pre-Implementation Baseline

Key takeaways from `ORACALL_PEI_PREIMPLEMENTATION_BRIEF.md`:

- **Objectives**: Enforce SEAM handling of PEI records, provide canonical grammar/schema, and ensure dual reports with cryptographic integrity while maximizing reuse of existing tooling.
- **Scope Boundaries**: Focus on internal grammar, storage, reporting, and security; defer external standards and regulatory filings.
- **Dependencies**: SessionMemory, ORACL tiers, metrics JSONL streams, archive policy, and enhanced CLI process tooling.
- **Assumptions**: Stable PEI definitions, unique event IDs, dual report archival, authenticated operators.
- **Risks**: Ambiguous grammar tokens, missing reports, tampering, storage bloat—each mitigated via schema validation, CLI scaffolds, signatures, and TRIAD indexing.
- **Success Criteria**: Schema merged, ingestion prototype within 2s, 100% dual-report capture, archive integrity checks.

No contradictions detected; assumptions remain valid but require continued verification during development.

---

## 6. ORACall Implementation Plan Snapshot

Highlights from `ORACALL_PEI_IMPLEMENTATION_PLAN.md`:

- **Architecture Layers**: Ingestion CLI/API, validation + caching, persistence, analytics—each mapped to existing components.
- **Phased Plan (Weeks 1–6)**: Schema finalization, ingestion tooling, storage/indexing, security controls, testing/Calamum harness, rollout.
- **Security & SEAM Controls**: Mandatory signatures, role-based ACLs, dual-report alerts, shared validators, SessionMemory caching, TRIAD-centric minimalism.
- **Testing Strategy**: Unit, integration, security, performance, and Calamum harness targeting 100 events/min ingestion and <50ms lookup.
- **Integration Points**: CLI, SessionMemory, metrics, archive rotations, process monitoring.
- **Scalability & Maintenance**: Nightly compaction, Zstandard archival, `oracall compact` command, Grafana dashboards.
- **Backlog**: External ticketing, third report option, webhooks, Calamum fuzzing.

Plan remains consistent with pre-implementation assumptions. Pending decisions listed in Section 4 should be resolved prior to development gates.

---

## 7. ORACall Framework Overview

Based on `ORACALL_FRAMEWORK_PROPOSAL.md`:

- **Vision**: Make ORACall the canonical PEI protocol with deterministic metadata for analytics and SEAM compliance.
- **Core Components**: Grammar/schema, ingestion CLI/API, storage/indexing, reporting automation.
- **Workflow**: Scaffold → ingest (validate + sign) → persist/index → feed ORACL tiers + Calamum.
- **Security & Compliance**: Ed25519 signatures, RBAC, tamper alerts, archive-first handling.
- **Integration Points**: SessionMemory, process monitoring, metrics streams, documentation references.
- **Roadmap**: Schema, storage, security, rollout.
- **Open Questions**: External tracker integration, SLA variations, partner satellite exposure—tracked as issues R3–R5.

This framework aligns with the implementation plan; no conflicting directives found.

---

## 8. ORACode Semantics & Storage Strategy

Key elements from `ORACODE_SEMANTICS_PROPOSAL.md`:

- **Mission & Objectives**: Provide semantic DSL, enforce SEAM-compliant tokens, empower ORACL reasoning without bespoke parsers.
- **Conceptual Layers**: Lexical registry, structural graphs, runtime APIs.
- **Integration**: ORACall bridge via `semantics_ref`, SessionMemory caching, ORACL context ingestion, archive linkage.
- **Security & Governance**: Central curation, signed annotations, ACLs, change logs, linting.
- **Roadmap**: Registry → CLI commands → ORACall integration → analytics.
- **Open Questions (Resolved)**: Central curation mandated; conflict resolution employs redundant auditors + ORACL-prime review; storage study compares JSONL/SQLite/LMDB and evaluates proprietary SEAMLog.
- **Storage Study Plan**: Benchmark harness, security review, efficiency metrics, minimalism audit, decision report; SEAMLog feasibility path defined with success criteria.

No security gaps identified; success depends on executing the study and capturing tooling automation (issues R2 & R6).

---

## 9. Feasibility & Resourcing Summary

Derived from `ORACALL_ORACODE_FEASIBILITY_STUDY.md`:

- **Executive Insight**: Combined rollout is feasible within six weeks if ORACall schema precedes ORACode registry by one sprint.
- **Evaluation Scope**: Technical (CLI, schema, indexing, semantics), operational (process monitoring, docs, training), governance (SEAM controls).
- **Scoring**: Architecture readiness 4/3 (ORACall/ORACode), resource availability 4/4, dependency clarity 3/3, security impact 5/4, delivery speed 4/3.
- **Technical Findings**: Shared infrastructure reuse >70%, JSONL+TRIAD adequate, CLI pattern supports new commands, storage overhead manageable.
- **Operational Readiness**: Process commands already live; documentation foundation in place; training pending.
- **Schedule & Resources**: Weeks 1–6 milestones align with implementation plan; total 6 person-weeks across engineering, security, docs, QA.
- **Risk Register**: Signature key sprawl, vocabulary drift, storage hot spots, adoption lag, dual-report SLA enforcement—reflected in Section 4.
- **Decision Gates**: Schema sign-off, security controls validation, integrated demo, documentation completion.

Conclusion: No feasibility blockers; proceed once decision gates are satisfied.

---

## 10. Performance Audit (Agent and Non-Agent Modes)

This section defines how ORACall and ORACode will be evaluated for speed, efficiency, token usage, and security in both agent-integrated and non-agent modes.

### 10.1 Objectives

- Confirm that agent-integrated flows (CLI + agents + ORACL tiers) provide materially better usability and efficiency than manual-only operation, while remaining SEAM-tight.
- Ensure that non-agent flows (CLI + files only) remain fully functional, predictable, and secure.
- Provide measurable, repeatable metrics covering ingestion, cataloging, retrieval, and conflict resolution.

### 10.2 Scope

- ORACall ingestion and cataloging (TRIAD index, archive rotations).
- ORACode annotation, query, and conflict-resolution workflows.
- Agent interactions with SessionMemory and ORACL tiers (for example, auto-summarization and cross-event correlation).

### 10.3 Metrics (Baseline Targets)

| Dimension | Non-Agent Target | Agent-Integrated Target | Notes |
|----------|------------------|-------------------------|-------|
| Ingestion Latency (p95) | Less than 2 seconds per event end-to-end | Less than 1 second per event with agent-assisted scaffolding | Measured from CLI invocation to durable write and index update |
| Retrieval Latency (p95) | Less than 50 milliseconds for common queries | Less than 40 milliseconds with agent prefetch and caching | Includes TRIAD plus in-memory caches |
| Cataloging Overhead | Ten percent or less storage for indexes and metadata | Same or lower via optimized compaction schedules | Measured as metadata bytes versus payload bytes |
| Operator Effort | Baseline (manual entry and lookup) | At least thirty percent reduction in manual steps | Derived from scripted Calamum workflows |
| Token Usage (Agent) | Not applicable | Bounded by per-session budgets defined in policy | Periodic audit of prompts, responses, and summaries |
| Security Events | Zero unhandled tamper incidents | Zero unhandled tamper incidents | Agent usage must not increase risk profile |

### 10.4 Test Harnesses

- Calamum scenarios extended to simulate both manual and agent-assisted flows for:
  - Burst ingestion (more than one hundred events per minute).
  - High-churn annotation workloads.
  - Conflict resolution under load.
- Planned benchmark commands, such as:
  - `codesentinel oracall bench --profile ingestion`
  - `codesentinel oracode bench --profile semantics`
- Agent-specific checks:
  - Validate that agents respect repository-relative paths and ASCII-only console output.
  - Verify that SessionMemory hit rate improves (target at least seventy percent in agent-heavy scenarios).

### 10.5 Security-Focused Performance Checks

- Ensure that enabling agent features never bypasses signatures, ACL checks, or archive-first rules.
- Confirm that additional agent-driven queries do not expose sensitive metrics or create unreviewed timing side channels.
- Require that any SEAMLog or storage-optimization feature passes:
  - Integrity verification (hash trees and signatures) under high load.
  - Rollback and replay protections.

### 10.6 Reporting and Regression Gates

- Store benchmark results under `docs/metrics/performance/oracall_oracode_bench.jsonl` with:
  - Scenario name, build identifier, and timestamp.
  - Non-agent and agent metrics shown side by side.
- Introduce regression gates in continuous integration:
  - Block merges if ingestion or query latency regress beyond configured thresholds.
  - Flag unusual token-usage spikes when agent integration is enabled.

---

## 11. Calamum Test Harness Integration

Calamum is the planned adversarial and regression test harness for CodeSentinel. It is responsible for validating the ORACall and ORACode pipelines under realistic and hostile conditions, and for enforcing the performance and security regression gates defined in this proposal.

### 11.1 Role in ORACall

- Drives scripted PEI events through `codesentinel oracall` commands.
- Verifies schema and grammar enforcement, dual-report requirements, signature checks, and archive-first storage.
- Exercises TRIAD indexing and lookup paths under load to ensure the performance targets in Section 10 are met.

### 11.2 Role in ORACode

- Issues semantic annotations and queries against ORACode APIs.
- Validates registry-enforced vocabulary usage and conflict-detection flows.
- Replays conflict scenarios to test independent auditor workflows and ORACL-prime resolution.

### 11.3 Agent and Non-Agent Scenarios

- Non-agent scenarios use only CLI and file-based artifacts, proving that ORACall and ORACode are fully operational without agents.
- Agent-enhanced scenarios add automation, prefetching, and summarization while measuring improvements in ingestion latency, retrieval latency, operator effort, and SessionMemory hit rates.
- All agent scenarios must respect SEAM rules: no Unicode console output, no bypass of signatures or ACLs, and strict archive-first behavior.

### 11.4 Security and SEAM Alignment

- Calamum operates only on test or sandboxed data and follows archive-first policies for any cleanup.
- All destructive actions are simulated or performed against archived copies; production data is never modified.
- Results are written as JSONL streams under `docs/metrics/calamum/`, enabling ORACL analytics without adding new parsers.

Additional details and future extensions are documented in `docs/tools/CALAMUM_HARNESS_OVERVIEW.md`.

---

## 12. Appendices

### Appendix A — Document Summaries & Links

1. **Pre-Implementation Brief** (`docs/planning/ORACALL_PEI_PREIMPLEMENTATION_BRIEF.md`): Baseline objectives, scope, dependencies, risks.
2. **Implementation Plan** (`docs/planning/ORACALL_PEI_IMPLEMENTATION_PLAN.md`): Detailed architecture, phases, SEAM controls, testing.
3. **Framework Proposal** (`docs/planning/ORACALL_FRAMEWORK_PROPOSAL.md`): Vision, components, workflow, open questions.
4. **Semantics Proposal** (`docs/planning/ORACODE_SEMANTICS_PROPOSAL.md`): DSL design, governance, conflict resolution, storage study.
5. **Feasibility Study** (`docs/planning/ORACALL_ORACODE_FEASIBILITY_STUDY.md`): Scoring, schedule, resource estimates, risks.
6. **Calamum Harness Overview** (`docs/tools/CALAMUM_HARNESS_OVERVIEW.md`): Purpose, architecture, and SEAM alignment for the planned test harness.
7. **Scalability and Centralization Roadmap** (`docs/planning/SCALABILITY_AND_CENTRALIZATION_ROADMAP.md`): Phased plan for scaling, centralization, and data collection.
8. **Market Needs, Costs, and Adoption Estimates** (`docs/planning/MARKET_NEEDS_COSTS_AND_ADOPTION_ESTIMATES.md`): Preliminary analysis of user needs, cost patterns, and adoption trajectories.
9. **Injected Objective Proposal** (`docs/planning/ORACALL_ORACODE_INJECTED_OBJECTIVE_PROPOSAL.md`): Encapsulates new strategic objectives and describes how to integrate them without destabilizing existing SEAM-aligned designs.
10. **Multi-Level Grant Proposal** (`docs/planning/ORACALL_ORACODE_MULTI_LEVEL_GRANT_PROPOSAL.md`): Presents modest, adequate, and aggressive funding tiers aligned with technical scope, staffing, and SEAM constraints.

### Appendix B — Security Justifications

- **Dual Reports**: Guarantees redundant evidence chains; enforced via CLI scaffolding and ingestion validation.
- **Ed25519 Signatures + Audit Trails**: Provide tamper detection; pairing with `security_events.jsonl` ensures traceability.
- **SessionMemory & ORACL Integration**: Maintain >60% cache hit rate, reducing redundant reads and attack surface from repeated IO.
- **Archive-First Policy**: Prevents destructive operations; aligns with SEAM minimalism and recovery goals.
- **Conflict Resolution Auditors**: Independent, blinded auditors plus ORACL-prime review eliminate bias and detect malicious annotations.

### Appendix C — Outstanding Decisions & Follow-Ups

| Topic | Description | Owner | Target |
|-------|-------------|-------|--------|
| Key Vault Workflow | Document key generation, storage, rotation | Security Engineer | Before Week 2 |
| Vocabulary Diff Automation | Tooling to publish registry diffs | Tooling Engineer | Week 1 |
| External Tracker Integration | Decide on ServiceNow/Jira hooks | Program Mgmt | Week 4 |
| SLA Matrix | Define severity-based dual-report timelines | SEAM Board | Week 3 |
| Satellite Exposure Path | Choose API vs file drop for partners | ORACL Ops | Week 4 |
| Storage Format Decision | Complete benchmark + SEAMLog evaluation | ORACode WG | Week 5 |
| Calamum Scenario Coverage | Add ORACode conflict cases | QA Lead | Week 5 |
| `oracall compact` SOP | Write operator runbook for compaction command | Lead Engineer | Week 6 |

---

End of proposal package.
