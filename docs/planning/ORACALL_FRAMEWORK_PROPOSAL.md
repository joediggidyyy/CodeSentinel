# ORACall Framework Proposal (Preliminary)

**Classification**: PEI-Control / Proposal  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Vision & Goals

- Establish ORACall as the canonical event-recording protocol for PEI investigations across CodeSentinel and CodeSecant satellites.
- Guarantee SEAM (Security, Efficiency, And Minimalism) alignment from ingestion to archival.
- Enable downstream analytics (ORACL tiers, Calamum harness) through deterministic structure and rich metadata.

---

## 2. Core Components

| Component | Description | Existing Reuse |
|-----------|-------------|----------------|
| Grammar & Schema | Formal definition of ORACall tokens mapped to JSON schema & dataclasses | Reuse planning work in `ORACALL_PEI_PREIMPLEMENTATION_BRIEF.md` |
| Ingestion CLI/API | `codesentinel oracall ingest` command enforcing dual reports and signatures | Extend existing CLI + metrics wrapper |
| Storage & Indexing | Append-only log + TRIAD index (Tree-Radix-Delta) + archive rotation | Reuse metrics folder + archive policy |
| Reporting | Auto-generated dual reports stored under `docs/reports/pei/` | Hook into document formatter utilities |

---

## 3. Workflow Overview

1. Investigator triggers `codesentinel oracall scaffold` to create report stubs.
2. PEI data captured via `oracall ingest`, which validates grammar, ensures dual reports, signs payload.
3. Record persisted to canonical log, indexed via TRIAD, metrics emitted, and archive rotation scheduled.
4. ORACL Context tier ingests the event for cross-session intelligence; Calamum harness uses data for pen-test simulations.

---

## 4. Security & Compliance

- Ed25519 signatures over canonical payload + timestamp.
- Role-based access for ingestion vs read-only queries.
- Tamper detection alerts through `security_events.jsonl` + optional Slack/email via alert utils.
- Non-destructive archival to `quarantine_legacy_archive/oracall/YYYY/MM/`.

---

## 5. Integration Points

- **SessionMemory**: cache PEI task list and decisions (automatically logged via CLI).
- **Process Monitoring**: correlate ORACall events with process anomalies using `memory process snapshot` outputs.
- **Metrics**: `agent_operations.jsonl` (success/failure), `error_patterns.jsonl` (schema violations), `security_events.jsonl` (tamper alerts).
- **Documentation**: `ADVANCED_ANALYTICS_FRAMEWORK.md` Section 6 references ORACall pipeline.

---

## 6. Roadmap Snapshot

| Phase | Deliverable |
|-------|-------------|
| P1 | Schema/grammar finalized, CLI scaffolding ready |
| P2 | Storage, TRIAD indexing, archive integration |
| P3 | Security hardening (signatures, ACLs), Calamum harness |
| P4 | Full rollout + dashboards + external hooks |

---

## 7. Open Questions

1. Do we require integration with external incident trackers at launch?
2. Should dual-report SLA vary by severity level?
3. How should ORACall entries be exposed to partner satellites (API vs file drop)?
