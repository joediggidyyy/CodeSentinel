# ORACall Implementation Proposal

**Classification**: Tier-2 / Internal Use Only  
**Date**: 2025-11-14  
**Owner**: ORACL Operations  
**Scope**: Execution blueprint for the three accepted recommendations (integration scaffolding, dual-report SLAs, partner exposure feed).

---

## Execution Order (Most Efficient Path)

1. **Integration Scaffolding Foundations**  
   Build the `IncidentSyncAdapter` abstraction, null adapter, and configuration hooks first. These changes are low-risk, unblock future connectors, and do not depend on SLA logic or partner feeds.

2. **Dual-Report SLA Enforcement**  
   Once severity metadata is guaranteed by the scaffolding, wire SLA tracking into the CLI, scheduler, and templates. This ensures ORACall output honors security priorities while adapters remain dormant.

3. **Partner Exposure Feed Preparation**  
   Finally, extend report exports with metadata headers and generate the `oracall_feed.jsonl` stream. This depends on severity data (for downstream consumers) and benefits from the adapter logging format already established.

---

## Workstreams & Deliverables

### 1. Integration Scaffolding Foundations

- **Code**  
  - `codesentinel/utils/integrations/incident_sync_adapter.py`: Define abstract base class with `prepare_payload(event)`, `push_event(payload)`, `audit_log(response)` methods using Python 3.8-compatible typing.  
  - `codesentinel/utils/integrations/null_incident_adapter.py`: No-op implementation that logs outbound intent and always succeeds.
- **Configuration**  
  - Extend `codesentinel.json` schema with `integrations.jira` and `integrations.servicenow` toggles (disabled by default).  
  - Update ConfigManager validation to surface friendly errors if malformed.
- **ORACall Hooks**  
  - Inside the ORACall ingestion pipeline (CLI utilities), instantiate the configured adapter and call `prepare_payload` / `push_event` only when both the integration flag and severity threshold are met.

### 2. Dual-Report SLA Enforcement

- **CLI Enhancements**  
  - Update `codesentinel/cli/oracall_utils.py` (or equivalent scaffold handler) to require a `severity` selection (Critical, High, Medium, Low).  
  - Annotate generated report stubs with SLA targets using placeholders (e.g., `{{ analytic_due }}`, `{{ action_due }}`).
- **Scheduler + Alerts**  
  - Extend `tools/codesentinel/report_workflow.py` or a new `sla_monitor.py` to watch pending ORACall reports, comparing current timestamps against SLA windows.  
  - Trigger alert manager notifications at 75% and 90% consumption of the SLA window.
- **Templates & Docs**  
  - Embed SLA reminders in `docs/reports/templates/oracl_incident_report.md` and `oracl_job_completion.md`.  
  - Document policy in `docs/reports/README.md` and the ORACall proposal appendix.

### 3. Partner Exposure Feed Preparation

- **Metadata Headers**  
  - Update Markdown/JSON export routines to include `distribution_level`, `cache_expiry`, `severity`, and `feed_id` headers to keep file drops self-describing.
- **JSONL Feed**  
  - Create `docs/reports/feeds/oracall_feed.jsonl` writer invoked after each ORACall event. Each entry should include event metadata, signed hash, and pointer to the stored reports.  
  - Design feed rotation policy aligning with archive rules (e.g., rotate daily, compress after 7 days).
- **Future API Prep**  
  - Define a simple schema file (`docs/planning/oracall_feed_schema.json`) and include mTLS/auth placeholders so later API work reuses the same format.

### Placeholder Tracking

All scaffolding and inactive infrastructure referenced above (adapters, config toggles, signing placeholders, feed headers) are registered in `docs/planning/PLACEHOLDER_REGISTRY.md` under IDs PL-001 through PL-005. New placeholders created during implementation **must** append an entry to that registry to keep humans and agents aligned with future decisions.

---

## Resource & Timeline Estimate

| Workstream | Effort | Dependencies |
|------------|--------|--------------|
| Integration scaffolding | 1 engineer-day | None |
| SLA enforcement | 2 engineer-days | Severity metadata + adapter logging |
| Partner exposure feed | 1.5 engineer-days | SLA data for feeds |

---

## Risks & Mitigations

- **Scope Creep**: Keep adapters limited to interface + null implementation until Phase 3 approvals.  
- **Alert Noise**: Configure SLA monitor thresholds carefully and allow per-severity overrides in config.  
- **Data Integrity**: Include Ed25519 signatures in the JSONL feed from day one to avoid rework when the API arrives.

---

## Approval & Next Steps

1. Confirm plan acceptance with ORACL Operations lead.  
2. Kick off Workstream 1 immediately; log progress in SessionMemory for traceability.  
3. After Workstream 1 PR merges, proceed sequentially through Workstreams 2 and 3, updating this file with status notes.
