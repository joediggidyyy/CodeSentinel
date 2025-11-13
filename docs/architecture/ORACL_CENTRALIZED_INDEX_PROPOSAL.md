# Proposal: ORACL Centralized Indexing System

**Status**: Draft  
**Date**: November 13, 2025  
**Author**: ORACL Governance Framework  
**Domain**: documentation, memory, intelligence  
**Tier**: T3-2 (Organization), T4a (Agent Instruction Optimization)

---

## Executive Summary

The ORACL™ ecosystem currently lacks a centralized indexing mechanism to efficiently access the intelligence substrate across 70+ documents. This proposal establishes a standardized, centralized indexing system that enables O(1) lookups, temporal classification, and seamless integration with ORACL's 3-tier memory architecture.

**Expected outcomes**: 80-90% reduction in agent orientation overhead, reliable temporal modeling, and scalable intelligence continuity.

---

## The Indexing Problem

### Current State

- **Scattered intelligence**: Documents distributed across 8+ subdirectories with inconsistent naming
- **No temporal awareness**: Agents cannot distinguish current vs future vs archive status without manual parsing
- **Linear search overhead**: ORACL must scan 70+ files for typical decisions (4-8 minutes)
- **Intelligence fragmentation**: Domain-specific wisdom cannot be aggregated across document boundaries

### Operational Impact

Without centralized indexing:

1. **Decision latency**: 4-8 minutes per complex decision
2. **File read volume**: 30-60 files scanned per query
3. **Intelligence gaps**: Historical patterns not surfaced during active work
4. **Maintenance burden**: Manual document classification and cross-referencing

With centralized indexing:

1. **Decision latency**: 15-45 seconds per complex decision
2. **File read volume**: 2-3 targeted files per query
3. **Intelligence continuity**: Historical context automatically integrated
4. **Maintenance automation**: Agent-guided classification and indexing

---

## Proposed System: ORACL Central Index (OCI)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ ORACL Central Index (OCI)                                   │
│ ├─ docs/index/MASTER_INDEX.jsonl (primary index)           │
│ ├─ docs/index/DOMAIN_INDEXES/ (domain-specific)            │
│ │  ├─ cli.jsonl                                            │
│ │  ├─ memory.jsonl                                         │
│ │  └─ ...                                                  │
│ └─ docs/index/TEMPORAL_INDEXES/ (temporal-specific)        │
│    ├─ current.jsonl                                        │
│    ├─ future.jsonl                                         │
│    └─ archive.jsonl                                        │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ ORACL Memory Integration                                   │
│ ├─ Session Tier: Cache index queries (60 min)              │
│ ├─ Context Tier: Index summaries (7 days)                  │
│ └─ Intelligence Tier: Pattern recognition (permanent)      │
└─────────────────────────────────────────────────────────────┘
```

### Index Schema (JSONL)

Each document entry follows this minimal schema:

```json
{
  "id": "unique-document-id",
  "path": "docs/reports/PHASE_1_COMPLETION_REPORT.md",
  "title": "Phase 1 Completion Report",
  "temporal_class": "archive",
  "domain": "infrastructure",
  "tier": "T3-1",
  "status": "complete",
  "date": "2025-11-06",
  "author": "GitHub Copilot",
  "summary": "Successfully reorganized documentation infrastructure...",
  "keywords": ["infrastructure", "documentation", "reorganization", "PDS"],
  "related_docs": ["docs/architecture/PRIORITY_DISTRIBUTION_SYSTEM.md"],
  "supersedes": [],
  "last_indexed": "2025-11-13T12:00:00Z",
  "confidence": 0.95
}
```

**Schema notes**:

- `id`: SHA256 hash of path + last modified time
- `temporal_class`: archive|current|future (required)
- `domain`: cli|core|memory|testing|infrastructure|security|documentation (required)
- `tier`: T0|T1|T2|T3|T4|Operational (required)
- `status`: complete|active|draft|archived (required)
- `summary`: Auto-generated 50-word summary (optional but recommended)
- `keywords`: Auto-extracted from content (optional)
- `confidence`: Index accuracy score (0.0-1.0)

### Indexing Process

#### Phase 1: Initial Population (Manual/Automated)

1. **Document discovery**: Scan all `docs/**/*.md` files
2. **Classification**: Apply temporal/domain rules from standardization directive
3. **Metadata extraction**: Parse headers, generate summaries, extract keywords
4. **Index generation**: Create MASTER_INDEX.jsonl and domain/temporal subsets
5. **Validation**: Cross-reference checks, duplicate detection

#### Phase 2: Continuous Maintenance (Automated)

1. **File system monitoring**: Watch `docs/` for changes
2. **Incremental updates**: Re-index modified documents only
3. **Cross-reference validation**: Update related_docs when documents move/rename
4. **Temporal aging**: Automatically promote current → archive based on date/status

#### Phase 3: ORACL Integration (Intelligent)

1. **Session Tier caching**: Cache index queries for 60 minutes
2. **Context Tier summaries**: Store recent index changes for 7 days
3. **Intelligence Tier patterns**: Learn from query patterns to optimize future lookups

### Query Interface

ORACL queries the index via standardized patterns:

```python
# Domain + temporal query
results = oci.query(domain="cli", temporal_class="current", keywords=["refactor"])

# Historical context for decision
context = oci.get_historical_context(domain="memory", decision_type="refactor")

# Related documents
related = oci.find_related(document_id="phase1-report", max_results=5)
```

### Implementation Plan

#### Week 1: Foundation (November 13-19)

- Create `docs/index/` directory structure
- Implement basic indexer script (`tools/codesentinel/index_documents.py`)
- Generate initial MASTER_INDEX.jsonl for all documents
- Add index query functions to ORACL Session Tier

#### Week 2: Automation (November 20-26)

- Add file system watcher for incremental updates
- Implement temporal aging logic (current → archive)
- Create domain-specific indexes
- Integrate with Context Tier for cross-session continuity

#### Week 3: Intelligence (November 27-December 3)

- Add keyword extraction and summary generation
- Implement pattern recognition for query optimization
- Create confidence scoring for index accuracy
- Add cross-reference validation

#### Week 4: Production (December 4-10)

- Full ORACL integration testing
- Performance benchmarking (target: <2 seconds per query)
- Documentation and training
- Go-live with monitoring

### SEAM Alignment

#### Security

- No sensitive data in index (paths only, no content)
- Read-only operations on source documents
- Index files can be safely cached/shared

#### Efficiency

- O(1) lookups vs O(n) directory scans
- Incremental updates reduce re-indexing overhead
- Caching at all ORACL tiers minimizes redundant queries

#### Minimalism

- Single index source of truth
- Minimal schema (12 fields, most optional)
- Automated maintenance eliminates manual overhead

### Success Metrics

| Metric | Baseline | Target (Week 4) | Target (Month 3) |
|--------|----------|-----------------|------------------|
| Index coverage | 0% | 95% | 100% |
| Query latency | N/A | <2 seconds | <1 second |
| Agent file reads | 30-60 | 2-5 | 1-3 |
| Decision latency | 4-8 min | 15-45 sec | 10-30 sec |
| Index accuracy | N/A | >90% | >95% |

### Risk Mitigation

- **Data loss**: Index is derived from source documents; can be regenerated
- **Stale data**: File watchers ensure real-time updates
- **Performance**: Incremental updates and caching prevent bottlenecks
- **Complexity**: Minimal schema and phased rollout reduce implementation risk

---

## Related Documents

- `DOCUMENT_STANDARDIZATION_DIRECTIVE.md` — Required prerequisite for consistent indexing
- `ORACL_MEMORY_ARCHITECTURE.md` — 3-tier memory system integration details
- `docs/architecture/DOCUMENT_CLASSIFICATION.md` — Original classification framework
- `docs/architecture/POLICY.md` — Policy tier definitions and SEAM constraints

---

**Indexing enables intelligence. Centralization enables continuity. ORACL operates on order.**
