# ORACall / PEI Implementation Plan

**Classification**: PEI-Control / SEAM Tier 1 Execution  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Architecture Overview

| Layer | Responsibility | Existing Component Reuse |
|-------|----------------|--------------------------|
| Ingestion CLI/API | Parse ORACall grammar, enforce dual reports, capture signatures | Extend `codesentinel cli` with `oracall ingest`, reuse metrics wrapper |
| Validation & Caching | SessionMemory for short-lived context, ORACL Context tier for 7-day rolling summaries | `codesentinel/utils/session_memory.py`, `.../oracl_context_tier.py` |
| Persistence | Append-only JSONL log + TRIAD index + archive rotations | `docs/metrics/*`, `quarantine_legacy_archive/` |
| Analytics | TRIAD-backed queries feeding ORACL Intelligence tier | Archive decision/provider modules |

---

## 2. Implementation Phases

1. **Schema Finalization (Week 1)**
   - Publish EBNF + JSON schema in `docs/architecture/ORACALL_SCHEMA.md`.
   - Add Pydantic (or dataclasses) models under `codesentinel/utils/oracall_schema.py`.
2. **Ingestion Tooling (Week 2–3)**
   - Add `codesentinel oracall ingest` CLI subcommand with these flags:
     - `--event-id`, `--adverse-event`, `--stage`, `--definition-ref`, `--report-primary`, `--report-secondary`, `--signature`.
   - Provide helper `codesentinel oracall scaffold` to create dual report stubs in `docs/reports/pei/`.
3. **Storage + Indexing (Week 3)**
   - Implement TRIAD indexer service:
     - Tree: `data/oracall/YYYY/MM/prefix/` directories.
     - Radix files: sorted JSONL with offset/length metadata.
     - Delta cache: LMDB/SQLite for hot data.
   - Integrate with archive rotation policy.
4. **Security Controls (Week 4)**
   - Embed Ed25519 signing/verification using workspace key vault.
   - Extend `docs/metrics/security_events.jsonl` logging for every ingestion, success/failure, and tamper detection.
5. **Testing & Calamum Harness (Week 5)**
   - Unit + integration tests (see Section 4).
   - Launch `calamum test --target oracall` prototype with scripted injections.
6. **Rollout (Week 6)**
   - Update `ADVANCED_ANALYTICS_FRAMEWORK.md` to reference ORACall pipeline.
   - Provide onboarding runbook for operators.

---

## 3. Security & SEAM Controls

- **Security**
  - Mandatory signatures and timestamped hashes per event.
  - Role-based ACLs for ingestion/query commands (operators vs observers).
  - Automated alerts if dual reports missing after configurable SLA.
- **Efficiency**
  - Shared schema + validators reused across CLI, API, and pipelines.
  - SessionMemory caching of recent PEI contexts to avoid re-reading large logs.
  - TRIAD indexing minimizes lookup cost while aligning with existing archive tree.
- **Minimalism**
  - All new code consolidated in `codesentinel/cli/oracall_utils.py` + `codesentinel/utils/oracall_schema.py`.
  - Reports stored under `docs/reports/pei/<event_id>/` with relative references.
  - Reuse existing metrics/logging streams instead of creating new file types.

---

## 4. Testing & Validation Strategy

| Layer | Tests |
|-------|-------|
| Unit | Schema validation, signature verification, grammar parser (valid/invalid tokens) |
| Integration | End-to-end ingest → log → TRIAD lookup → archive rotation |
| Security | Tamper attempts (modified payload, replay, missing report) logged as failures |
| Performance | Load test ingestion at 100 events/minute; ensure TRIAD lookup < 50ms |
| Calamum Harness | `calamum test --target oracall` runs scripted attacks (flood, malformed grammar, duplicate IDs) |

---

## 5. Integration Points

- **CLI**: Extend `codesentinel cli` with `oracall` command group leveraging existing global metrics tracking.
- **SessionMemory**: Log PEI tasks and decisions to maintain 60%+ cache hit rate for operators.
- **Metrics**: Append events to `docs/metrics/agent_operations.jsonl` (command success), `security_events.jsonl` (tamper alerts).
- **Archive**: Rotate monthly to `quarantine_legacy_archive/oracall/YYYY/MM/` using existing archive-first policy.
- **Process Monitoring**: Hook into `memory process snapshot` outputs for correlation (PEI event ↔ process anomalies).

---

## 6. Scalability & Maintenance

- TRIAD index supports millions of events via radix sharding; compaction job runs nightly.
- Old data (>180 days) compressed via Zstandard and referenced through archive manifest.
- Maintenance CLI command `codesentinel oracall compact` manages delta merges and integrity checks.
- Monitoring dashboards (Grafana) visualize ingestion rate, backlog, tamper alerts.

---

## 7. Improvement Backlog

1. Integrate with external ticketing (ServiceNow/Jira) for adverse-event references.
2. Add optional third report (“lessons learned”) for critical events.
3. Provide API webhooks so satellites can subscribe to new PEI events.
4. Extend Calamum harness with fuzzing for grammar tokens.

---

## 8. Sign-off Checklist

- [ ] Schema + plan reviewed by SEAM board.
- [ ] Security sign-off (signatures, ACLs, alerts).
- [ ] Calamum harness validated.
- [ ] Documentation linked from `SESSION_TIMELINE_20251113.md` update.
