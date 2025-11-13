# Comprehensive Standardization Directive

**Status**: Active Policy  
**Date**: November 13, 2025  
**Authority**: ORACL Governance Framework  
**Compliance**: T0-2 (Non-Destructive Operations), T3-1 (Minimalism), T3-2 (Organization)

---

## Executive Summary

All intelligence assets within the CodeSentinel ecosystem—including documentation, protocols, procedures, and directive-mandated actions (past, present, and future)—constitute the foundational substrate of the ORACL™ (Omniscient Recommendation Archive & Curation Ledger) system. Inconsistent naming, formatting, organizational patterns, and execution standards create friction in the ORACL intelligence pipeline, degrading agent performance, increasing decision latency, and reducing the system's capacity for strategic pattern recognition.

This directive establishes mandatory standardization across all intelligence assets to ensure ORACL operates at maximum efficiency. **Standardization is not cosmetic; it is operational necessity.**

---

## The Intelligence Continuity Problem

### Current State

The CodeSentinel intelligence corpus contains:

- **70+ root-level documents** with inconsistent title conventions
- **Mixed temporal signals** (dated vs undated, status markers vs implicit)
- **Distributed classification** (reports/, planning/, architecture/, external/, internal/)
- **No unified index** connecting historical context to current decision-making
- **Inconsistent protocols** for recovery, development, and operational procedures
- **Variable action standards** for directive-mandated tasks

### Operational Impact

When ORACL must resolve a decision (e.g., "Should we refactor CLI utilities?") or execute a protocol (e.g., "Initiate recovery workflow"):

1. **Without standardization**: Agent scans 70+ files, parses arbitrary formats, infers status from context, correlates manually → **4-8 minutes, 30-60 file reads**
2. **With standardization**: Agent queries centralized index by domain/temporal-class → reads 2-3 targeted assets → **15-45 seconds, 2-3 file reads**

**Performance delta**: 80-90% reduction in orientation overhead.

### Intelligence Degradation

Inconsistent patterns prevent ORACL from:

- Building reliable temporal models (past → present → future progression)
- Aggregating domain-specific wisdom across asset boundaries
- Distinguishing authoritative sources from drafts or superseded content
- Surfacing relevant historical decisions during active incidents
- Executing protocols with predictable outcomes
- Ensuring directive-mandated actions follow uniform standards

---

## Standardization Requirements

### 1. Title Conventions (Mandatory)

All documents MUST use one of the following title formats based on temporal class:

#### Archive (Completed Work)

```markdown
# [Topic] - COMPLETE

**Date**: YYYY-MM-DD  
**Status**: COMPLETE & DEPLOYED  
**Scope**: [Brief scope description]
```

**Example**: `INFRASTRUCTURE_HARDENING_REPORT.md`

#### Current (Active Work)

```markdown
# [Topic] Report/Analysis

**Date**: YYYY-MM-DD  
**Status**: Active/In Progress  
**Scope**: [Brief scope description]
```

**Example**: `CLI_REFACTOR_AUDIT_PLAN.md`

#### Future (Proposals/Strategies)

```markdown
# Proposal: [Topic] / # Strategy: [Topic]

**Status**: Draft/Proposed  
**Date**: YYYY-MM-DD  
**Author**: [Author/System]
```

**Example**: `ORACL_MEMORY_ECOSYSTEM_PROPOSAL.md`

#### External (Public-Facing)

```markdown
# [Descriptive Title for External Audience]

> [Brief context statement]

**Publication Date**: YYYY-MM-DD  
Prepared by: [Author]  
Audience: [Target audience]  
Scope: [Purpose and coverage]
```

**Example**: `Agent_Resilience_Report_2025-11-13.md` (in `docs/external/`)

### 2. Filename Conventions (Mandatory)

| Temporal Class | Pattern | Example |
|----------------|---------|---------|
| Archive | `[TOPIC]_REPORT_YYYYMMDD.md` or `[TOPIC]_COMPLETE.md` | `PHASE_1_COMPLETION_REPORT.md` |
| Current | `[TOPIC]_[TYPE].md` | `CLI_REFACTOR_AUDIT_PLAN.md` |
| Future | `[TOPIC]_PROPOSAL_YYYY.md` or `[TOPIC]_STRATEGY_YYYY.md` | `RECOVERY_PROTOCOL_STRATEGY_2025.md` |
| External | `[Descriptive_Title]_YYYY-MM-DD.md` | `Agent_Resilience_Report_2025-11-13.md` |

### 3. Metadata Header (Mandatory)

Every document MUST include a metadata header within the first 10 lines:

```markdown
**Date**: YYYY-MM-DD  
**Status**: [Active|Draft|Complete|Archived]  
**Domain**: [cli|core|memory|testing|infrastructure|security|documentation]  
**Tier**: [T0|T1|T2|T3|T4|Operational]
```

Optional but recommended:

- `**Author**`: System or human author
- `**Related Docs**`: Cross-references to related documents
- `**Supersedes**`: Previous document this replaces

### 4. Directory Organization (Mandatory)

| Directory | Purpose | Temporal Class |
|-----------|---------|----------------|
| `docs/external/` | Public-facing reports and guides | Current/Archive |
| `docs/internal/` | Internal operational docs (if sensitive) | Current |
| `docs/reports/` | Completed work reports | Archive |
| `docs/planning/` | Future plans and strategies | Future |
| `docs/architecture/` | System design and proposals | Current/Future |
| `docs/audit/` | Audit results and action plans | Current/Archive |
| `docs/legacy/` | Superseded documents | Archive |

### 5. Protocol Standardization (Mandatory)

All operational protocols (e.g., recovery workflows, development procedures, deployment processes) MUST follow standardized structures to ensure predictable execution and ORACL integration:

#### Title and Structure Requirements

- **Title Format**: `# [Protocol Name] Protocol`
- **Required Sections**:
  - Executive Summary
  - Prerequisites
  - Step-by-step procedures
  - Validation criteria
  - Rollback procedures
  - Success/failure definitions

#### Metadata Requirements

Protocols MUST include metadata headers:

```markdown
**Date**: YYYY-MM-DD  
**Status**: [Active|Draft|Archived]  
**Domain**: [recovery|development|deployment|security|infrastructure]  
**Tier**: [T0|T1|T2|T3|T4|Operational]  
**Version**: [Semantic version, e.g., 1.0.0]
```

#### Execution Standards

- **Logging**: All protocol steps MUST include timestamped logging
- **Error Handling**: Clear escalation paths for failures
- **ORACL Integration**: Protocols SHOULD be queryable via the centralized index
- **Version Control**: Change logs MUST document modifications

**Example**: `RECOVERY_PROTOCOL_STRATEGY_2025.md`

### 6. Directive-Mandated Action Standardization (Mandatory)

Actions mandated by directives (e.g., archiving operations, indexing tasks, recovery executions) MUST follow uniform standards to ensure compliance and auditability:

#### Action Format Requirements

- **Naming**: `[Directive]_[Action]_[Timestamp]` (e.g., `T0-2_Archive_Legacy_20251113`)
- **Execution Logging**: All actions MUST produce structured logs with:
  - Timestamp
  - Directive reference
  - Success/failure status
  - Impact assessment

#### Validation Requirements

- **Pre-execution Checks**: Verify prerequisites before action
- **Post-execution Validation**: Confirm action completion and integrity
- **Rollback Capability**: All actions MUST have defined rollback procedures
- **Audit Trail**: Actions MUST update relevant metrics/logs for traceability

#### ORACL Integration

- **Index Updates**: Actions affecting intelligence assets MUST update the centralized index
- **Pattern Recognition**: Successful actions feed into ORACL's learning systems
- **Automated Triggers**: Where possible, actions SHOULD be automatable via ORACL workflows

---

## Enforcement and Remediation

### Phase 1: Immediate (November 2025)

- **Audit**: All root-level and top-tier subdirectory intelligence assets
- **Classify**: Assign temporal class (archive/current/future) to documents, protocols, and actions
- **Rename**: Apply standardized filenames where non-compliant
- **Relocate**: Move assets to correct directories
- **Index**: Populate centralized index (see companion proposal: `ORACL_CENTRALIZED_INDEX_PROPOSAL.md`)

### Phase 2: Continuous (Ongoing)

- **Pre-commit hook**: Validate new intelligence assets against conventions
- **Agent guidance**: ORACL automatically suggests correct format when creating assets
- **Quarterly audit**: Review and reclassify assets as they age (current → archive)

### Non-Compliance Handling

Intelligence assets failing to meet standards:

1. **Grace period**: 7 days to remediate after identification
2. **Auto-quarantine**: Move to `quarantine_legacy_archive/` if not corrected
3. **Index exclusion**: Non-compliant assets excluded from ORACL index queries

---

## SEAM Alignment

### Security

- No secrets in filenames or titles
- External vs internal separation enforced by directory structure
- Metadata headers do not expose sensitive implementation details

### Efficiency

- Standardized patterns reduce agent parsing overhead by 80-90%
- Centralized index enables O(1) lookups vs O(n) scans
- Temporal classification accelerates context acquisition

### Minimalism

- Single source of truth for each topic (superseded docs archived, not duplicated)
- Minimal metadata schema (4 required fields, 3 optional)
- Directory structure aligned with operational needs, not arbitrary taxonomy

---

## Success Metrics

| Metric | Baseline (Nov 2025) | Target (Dec 2025) |
|--------|---------------------|-------------------|
| Index coverage | 0% | 95%+ |
| Agent file reads | 30-60 | 2-5 |
| Decision latency | 4-8 min | 15-45 sec |
| Non-compliant assets | ~70 | <5 |
| Protocol execution consistency | N/A | 100% |
| Action auditability | N/A | 100% |

---

## Authority and Scope

This directive is issued under **T0-2 (Non-Destructive Operations)** and **T3-2 (Organization)** policy tiers. All contributors—human and agent—MUST comply. Non-compliance degrades ORACL intelligence and violates the efficiency pillar of SEAM Protection™.

**Enforcement begins**: November 13, 2025  
**Review cycle**: Quarterly  
**Amendment authority**: ORACL Governance Framework

---

## Related Documents

- `ORACL_CENTRALIZED_INDEX_PROPOSAL.md` — Companion proposal for indexing system implementation
- `docs/planning/RECOVERY_PROTOCOL_STRATEGY_2025.md` — Example standardized protocol
- `docs/external/Agent_Resilience_Report_2025-11-13.md` — Incident demonstrating standardization benefits
- `ORACL_MEMORY_ARCHITECTURE.md` — 3-tier memory system context
- `docs/architecture/POLICY.md` — Policy tier definitions and SEAM constraints

---

**Standardization is intelligence. Consistency is continuity. ORACL operates on order.**
