# ORACall Internal Recommendation Report

**Classification**: Tier-2 / Internal Use Only  
**Date**: 2025-11-14  
**Owner**: ORACL Operations  
**Scope**: Responses to outstanding ORACall framework questions (external tracker integration, dual-report SLA policy, partner exposure strategy)

---

## 1. External Incident Tracker Integration (Jira/ServiceNow)

**Recommendation**: Defer mandatory push connectors until the ORACall platform completes Phase 2 (storage & indexing). Instead, prepare the groundwork now:

1. **Placeholder Interfaces**  
   - Define an abstract `IncidentSyncAdapter` in `codesentinel/utils/integrations/` with `prepare_payload`, `push_event`, and `audit_log` methods.  
   - Maintain a `null-adapter` implementation that simply logs the intent; this keeps the call sites stable while real connectors are in development.
2. **Config Hooks**  
   - Reserve configuration keys in `codesentinel.json` (e.g., `"integrations": { "jira": {"enabled": false}, "servicenow": {"enabled": false} }`).  
   - Default them to disabled to preserve SEAM minimalism while allowing easy activation later.
3. **Schema Readiness**  
   - Ensure ORACall events capture canonical IDs, severity, and affected asset lists so that future connectors can map fields without reformatting upstream data.

**Rationale**: This approach keeps structure consistent for future scaling while avoiding premature complexity. Once we begin scaling, we can plug concrete Jira/ServiceNow implementations into the prepared adapter layer without touching upstream ingestion or storage.

---

## 2. Dual-Report SLA by Severity

**Recommendation**: Adopt tiered SLAs tied to the incident severity declared in the ORACall payload. Proposed timeline matrix:

| Severity | Analytic Report SLA | Action Report SLA | Notes |
|----------|--------------------|-------------------|-------|
| Critical | 2 hours | 4 hours | Immediate escalation, alert channel paging, requires leadership approval to extend. |
| High | 6 hours | 12 hours | Include remediation checklist; automation may draft analytic report from template. |
| Medium | 24 hours | 48 hours | Default for most PEI events; leverage scheduler reminders. |
| Low | 3 business days | 5 business days | Suitable for advisory findings; can batch via weekly job. |

Implementation considerations:

- Add `severity` field validation in `codesentinel oracall scaffold` so both report stubs inherit the SLA metadata.
- Update maintenance scheduler to monitor pending reports and emit alerts when SLA windows approach expiration (e.g., 75% threshold warning, 90% critical alert).
- Document the matrix in `docs/reports/templates/oracl_incident_report.md` and `docs/reports/templates/oracl_job_completion.md` so authors see their target timeline when filling placeholders.

**Rationale**: Aligns effort with risk, protects Security priority within SEAM, and gives automation clearer thresholds for paging and reminders.

---

## 3. Exposure to Partner Satellites (API vs File Drop)

**Recommendation**: Plan for a phased strategy while remaining file-drop compatible in the near term.

1. **Short Term (Current Phase)**  
   - Continue producing signed Markdown/JSON bundles under `docs/reports/PEI/` and `docs/reports/MEASUREMENT_REPORTS/` for satellites to ingest via secure file replication.  
   - Add metadata headers specifying `distribution_level` and `cache_expiry` to streamline downstream import.
2. **Mid-Term Preparation**  
   - Design an internal `oracall_feed.jsonl` stream with strict schema plus Ed25519 signatures. This feed can be exposed later through an authenticated API without changing upstream writers.
3. **Long-Term (Scaling)**  
   - Stand up a minimal REST gateway (`/api/oracall/events`) with mTLS and token auth once partner demand warrants live pulls.  
   - Provide webhook subscriptions for satellites that prefer push delivery.

**Rationale**: The file-drop model satisfies current capacity while keeping compliance logging simple. Building the JSONL feed now lets us “flip the switch” to an API later with minimal rework, ensuring we stay ready for scaling timelines.

---

## Next Steps

1. Log these recommendations in SessionMemory + ORACL Context Tier for continuity.  
2. Schedule engineering spikes for: (a) IncidentSyncAdapter skeleton, (b) SLA enforcement hooks in the scheduler, (c) oracall_feed proof-of-concept.  
3. Revisit the report after Phase 2 milestones to finalize connector commitments and external exposure timelines.
