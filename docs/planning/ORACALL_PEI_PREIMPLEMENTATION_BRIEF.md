# ORACall / PEI Pre-Implementation Brief

**Classification**: PEI-Control / SEAM Tier 0 Preparation  
**Prepared By**: CodeSentinel Agent Team  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Purpose

Establish the foundational assumptions, dependencies, and security posture required before implementing the ORACall protocol for PEI (Planning–Execution–Iteration) events within the CodeSentinel ecosystem.

---

## 2. Objectives

- Guarantee SEAM-tight (Security, Efficiency, And Minimalism) handling of PEI records from ingestion through archival.
- Provide a canonical grammar and schema mapping that can be consumed by ORACL tiers and CodeSecant satellites.
- Ensure every PEI event is backed by dual reports (initial + validation) with cryptographic integrity.
- Reuse existing infrastructure (SessionMemory, ORACL tiers, archive index, metrics) to minimize net-new surface area.

---

## 3. Scope & Boundaries

| Item | In Scope | Out of Scope |
|------|----------|--------------|
| Grammar formalization | ✅ ORACall token-to-schema mapping | ❌ Alternate PEI standards |
| Storage | ✅ Append-only logs, archive integration | ❌ External SIEM connectors (future phase) |
| Reporting | ✅ Dual reports, metrics links | ❌ Automated external regulatory filings |
| Security | ✅ Signatures, ACLs, tamper detection | ❌ Hardware attestation |

---

## 4. Dependencies & Inputs

- `codesentinel/utils/session_memory.py` (Tier 1 cache for task context).
- ORACL Context + Intelligence tiers (`codesentinel/utils/oracl_context_tier.py`, archive providers).
- `docs/metrics/*` JSONL streams for agent operations, security events, error patterns.
- `quarantine_legacy_archive/` policy for non-destructive storage.
- CLI memory/process enhancements (detail, kill, snapshot) to reuse logging pipeline.

---

## 5. Assumptions

1. PEI definition provided is representative but may evolve; schema must support versioning.
2. Every ORACall record references a unique `event_id` and `adverse_event_ref`.
3. Dual reports can reference Markdown, PDF, or external URLs but must resolve to archive-relative paths.
4. All participating agents have authenticated CLI access and can sign payloads.

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ambiguous grammar tokens (`defw`, `dtype`) | Parser drift, inconsistent records | Publish EBNF + JSON schema before coding; enforce via tests |
| Missing reporting artifacts | Compliance breach | CLI scaffolds auto-generate report stubs and block submission until both paths are supplied |
| Tampering / replay | False investigations | Ed25519 signatures tied to event hash + timestamped append-only log |
| Storage bloat | Inefficient queries | Apply TRIAD indexing (Tree-Radix-Delta) with periodic compaction |

---

## 7. Success Criteria

- ✅ Formal schema merged into repo docs and referenced by CLI.
- ✅ Prototype ingestion command creates canonical record + dual report placeholders within 2s.
- ✅ Metrics show 100% capture of dual-report requirement.
- ✅ Archive integrity check verifies hashes for each rotation.

---

## 8. Approval Checklist

- [ ] Schema + grammar validated by ORACL maintainers.
- [ ] Security review signed off (SEAM board).
- [ ] Documentation (this brief + implementation plan) stored under `docs/planning/` and referenced in `SESSION_TIMELINE` report.
