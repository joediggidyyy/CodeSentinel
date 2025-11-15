# Placeholder & Future Expansion Registry

**Classification**: Tier-2 / Internal Use Only  
**Date**: 2025-11-14  
**Owner**: ORACL Operations  
**Purpose**: Central catalog for inactive scaffolding, feature placeholders, and future-expansion hooks so engineers and agents can trace pending decisions quickly.

---

## Policy

1. **Modular Placement**  
   - Runtime placeholders live beside their eventual production modules (e.g., under `codesentinel/utils/integrations/`) to preserve cohesion.  
   - Configuration toggles and schema stubs stay in the canonical config or planning directories.
2. **Registration Requirement**  
   - Every placeholder or inactive infrastructure element **must** have an entry in this registry, including activation criteria and owner.  
   - When the placeholder graduates to active code, update the entry status (e.g., `retired`, `replaced`) instead of deleting it for historical traceability.
3. **Decision Pipeline Hooks**  
   - Each entry references the strategy/decision doc that governs its activation so agents can route decisions upstream.  
   - SessionMemory notes should link back to the relevant entry ID when discussing placeholder work.

---

## Current Entries

| ID | Placeholder | Location | Purpose | Activation Criteria / Notes |
|----|-------------|----------|---------|-----------------------------|
| PL-001 | `IncidentSyncAdapter` abstract + interfaces | `codesentinel/utils/integrations/incident_sync_adapter.py` | Defines the modular contract for outbound Jira/ServiceNow sync before real connectors ship. | Activate when an external tracker requires live pushes. Pair with concrete adapter module and update `codesentinel.json` toggles. |
| PL-002 | `NullIncidentSyncAdapter` | `codesentinel/utils/integrations/null_incident_adapter.py` | Safe default adapter that logs intent without sending data, keeping call sites stable. | Retire once at least one production adapter is enabled globally. |
| PL-003 | Integration config toggles | `codesentinel.json -> integrations.*` (validated via `ConfigManager`) | Disabled-by-default hooks for Jira/ServiceNow plus severity threshold. | Flip `enabled` flags only after adapters are wired, and document the decision in Change Control. |
| PL-004 | ORACall feed signature placeholder (`signature": "pending-ed25519"`) | `tools/codesentinel/oracall_manager.py` feed writer + `docs/reports/feeds/oracall_feed.jsonl` | Reserves the signing field until Ed25519 keys are issued. | Replace with live signer/ms vault pointer once key management policy is approved. |
| PL-005 | ORACall distribution headers | Markdown templates under `docs/reports/templates/` | Cache metadata + severity markers embedded even though partner API is not yet live. | Becomes mandatory for API launch; update headers to include final URI tokens. |
| PL-006 | Equity allocation framework | `docs/planning/ORACALL_INVESTMENT_EQUITY_BRIEF.md` | Placeholder for tier-specific equity/ROI compensation structure pending finance & legal review. | Populate with capitalization table + ESOP schedules before presenting to investors or staff. |

---

## Adding a New Placeholder

1. Implement the code/config/doc stub within the correct module tree.  
2. Append a new row to the table above. Use the next sequential ID.  
3. Link to the controlling decision doc (proposal, ADR, etc.).  
4. Mention the entry in relevant planning or implementation notes so agents can find it quickly.

---

## Related References

- `docs/planning/ORACALL_IMPLEMENTATION_PROPOSAL.md` — outlines how placeholders PL-001 through PL-005 support ORACall scaling.  
- `docs/reports/README.md` — documents metadata headers and feed locations for ORACall exports.  
- `docs/checkpoints/.checkpoint_oracl_integration_complete.md` — latest merge-ready snapshot confirming registry coverage (PL-001–PL-006) and activation priorities.

---

## Machine-Readable Manifest

- `docs/planning/placeholder_manifest.json` — canonical source for automation. Each entry mirrors the table above (ID, files, decision docs, checkpoint anchor). Update the manifest whenever this registry changes so CLI tools and SessionMemory logs stay in sync.
