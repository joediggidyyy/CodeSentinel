# ORACode Semantics Framework Proposal (Preliminary)

**Classification**: PEI-Control / Proposal  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Mission Statement

Deliver a semantics layer (ORACode) that sits atop ORACall and provides consistent meaning, inference rules, and automation hooks for PEI events, enabling agents and satellites to reason about context, severity, and remediation pathways.

---

## 2. Objectives

- Define a lightweight domain-specific language (DSL) for annotating ORACall records with semantic tags, relationships, and policy constraints.
- Ensure ORACode tokens align with SEAM principles—explicit, auditable, ASCII-safe, and versioned.
- Empower ORACL Context/Intelligence tiers to perform reasoning (e.g., detect repeated failure modes) without bespoke parsers per satellite.

---

## 3. Conceptual Layers

| Layer | Purpose | Example |
|-------|---------|---------|
| Lexical | Token definitions (e.g., `PEI.STAGE.PLAN`, `IMPACT.SEV.CRITICAL`) | ASCII keywords + version metadata |
| Structural | How tokens compose into semantic graphs referencing ORACall events | `event_id -> { tags: [...], relations: [...] }` |
| Runtime APIs | Functions to query/update semantics | `oracode annotate --event <id> --tag IMPACT.SEV.HIGH` |

---

## 4. Integration with Existing Infrastructure

- **ORACall Bridge**: Each ORACall record includes a `semantics_ref` pointing to ORACode annotations stored in `docs/metrics/oracode_semantics.jsonl`.
- **SessionMemory**: Cache semantic annotations for in-progress investigations to avoid repeated disk IO.
- **ORACL Context Tier**: Promote aggregated semantics (e.g., “3 PEI events tagged IMPACT.SEV.HIGH in last 24h”) for rapid situational awareness.
- **Archive**: Semantic files follow the same archive-first policy and reference the corresponding ORACall entries.

---

## 5. Security & Governance

- All annotations signed by the originating agent; optional co-sign for high-severity changes.
- Access control lists define who can read vs modify semantics.
- Change history logged to `docs/metrics/security_events.jsonl` with diff summaries.
- Automated linting ensures only approved tokens (from the lexical registry) are accepted.

---

## 6. Roadmap Snapshot

| Phase | Deliverable |
|-------|-------------|
| P1 | Lexical registry + validation tooling |
| P2 | CLI commands (`oracode annotate`, `oracode query`) |
| P3 | Integration with ORACall ingestion + ORACL Context tier |
| P4 | Advanced analytics (reasoning rules, alerting) |

---

## 7. Open Questions (Resolution Plan)

### 7.1 Vocabulary Governance

- **Central Curation Mandate**: ORACode vocabularies remain centrally curated by the SEAM board and ORACL-prime maintainers. Community/agent proposals enter via pull requests but are not accepted without two maintainer signatures and a security desk review.
- **Extension Workflow**: Custom tags can be staged locally for experimentation, yet ingestion/annotation commands will refuse to persist them until a signed registry update ships. This keeps unaudited tokens from leaking into production logs while still enabling prototyping.
- **Offline & Non-Agent Operation**: The canonical registry is distributed as a versioned ASCII file checked into the repo (`docs/metrics/oracode_registry_v*.txt`), guaranteeing that satellites without live agent integrations can operate deterministically.
- **Scalability Hooks**: Registry releases bundle diff manifests so downstream tooling can update incrementally even as vocabulary size scales into tens of thousands of tokens.

### 7.2 Conflict Resolution Framework

1. **Detection**: The ingestion pipeline flags events where multiple annotations touch the same tuple (`event_id`, `tag`) or where severity vectors disagree beyond configured tolerances.
2. **Redundant Independent Auditors**: Two isolated agent instances (“Auditor-A” and “Auditor-B”) replay the event data without seeing each other’s verdicts. They rely solely on archived artifacts to stay unbiased.
3. **Verdict Submission**: Each auditor produces a signed `oracode_conflict_report` (JSONL) capturing reasoning, recommended severity, and hashes of referenced artifacts. Reports are written to `docs/metrics/oracode_conflict_queue.jsonl`.
4. **ORACL-prime Review**: ORACL-prime ingest service reads both reports, verifies signatures, performs consistency checks, and either (a) auto-resolves when both auditors match or (b) escalates to the SEAM board if they diverge. Escalations spawn a third reviewer path but still rely on archived evidence to stay SEAM-tight.
5. **Outcome Propagation**: Once resolved, the authoritative annotation is re-signed, conflicting entries are superseded (never deleted), and a tamper-proof audit trail is appended to `security_events.jsonl`. Operators without agent integrations can read these outcomes directly from the metrics files, preserving full functionality in offline deployments.

### 7.3 Storage Format Study

The storage decision will follow a structured study emphasizing SEAM priorities and future large-scale scalability (millions of PEI events/month). The study plan:

| Candidate | Strengths | Concerns | Initial Hypothesis |
|-----------|-----------|----------|--------------------|
| **JSONL (current default)** | Human-readable, append-only friendly, works with existing tooling, trivial archive rotation | Larger footprint, slower random lookups, relies on external index for speed | Likely continue for ingestion log due to simplicity; pair with stronger indexing |
| **SQLite (file-based SQL)** | ACID semantics, indexes, query flexibility, mature tooling | Requires mutex handling for concurrent writers, larger attack surface if WAL mishandled | Promising for query mirror; needs hardened access controls |
| **LMDB/Lightning DB** | Memory-mapped speed, crash-resistant, key-value simplicity | Requires careful sizing, Windows mmap nuances | Candidate for TRIAD “delta cache” tier |

Study steps:

1. **Benchmark Harness**: Build deterministic workloads (ingest, query, conflict replay) executable via `codesentinel oracode bench --profile <target>` so results do not depend on agent presence.
2. **Security Review**: For each candidate, catalogue attack surfaces (file tamper, lock poisoning, injection vectors) and ensure Ed25519 signature verification remains first-class.
3. **Efficiency Metrics**: Record ingest latency (p95), query latency (p95), storage overhead, and CPU/RAM usage. Target <50ms query latency and ≤10% metadata overhead.
4. **Minimalism Audit**: Confirm we can reuse shared utilities (TRIAD index, archive policy) without bespoke daemons.
5. **Decision Report**: Publish findings to `docs/planning/ORACODE_STORAGE_STUDY.md`, including explicit go/no-go guidance for each format.

#### Proprietary Format Feasibility

- **Concept**: Evaluate a bespoke “SEAMLog” container—an append-only file with native Merkle proofs, deterministic block headers, and built-in dual-report references. Blocks encapsulate both ORACall identifiers and ORACode semantics, enabling offline validation without auxiliary indexes.
- **Advantages**: Tailored for cryptographic integrity (on-write hash tree), predictable storage layout for cold archive streaming, and baked-in metadata for conflict detection. Native compatibility with CodeSentinel tooling avoids translation layers.
- **Challenges**: Requires custom reader/writer libraries (Python + future Golang/Rust bindings), formal specification, and exhaustive cross-platform testing. Any flaw becomes a single point of failure, so the development budget must include formal verification passes.
- **Feasibility Approach**:
  1. Draft a minimal spec (block header, payload, checksum, signature fields) and prototype writer/reader under `codesentinel/utils/seamlog.py`.
  2. Compare performance/security metrics against JSONL/SQLite baselines using the same benchmark harness.
  3. Validate that SEAMLog files can be consumed by automation layers without agent assistance (CLI-only verification mode).
  4. If benefits exceed 20% improvement in both security posture (integrity proofs) and performance (query p95), promote SEAMLog to pilot phase; otherwise, shelve until additional resources free up.

This study path keeps security first, ensures current protocols remain fully functional without agent integrations, and lays groundwork for seamless scaling as PEI volume expands.
