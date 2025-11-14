# Calamum Test Harness Overview

**Classification**: PEI-Control / Testing Infrastructure  
**Date**: 2025-11-14  
**Version**: 0.1-draft

---

## 1. Purpose

Calamum is the planned adversarial and regression test harness for CodeSentinel. Its mission is to exercise SEAM-protected workflows (Security, Efficiency, And Minimalism) under realistic and hostile conditions, with a focus on:

- ORACall PEI event ingestion (planning–execution–iteration pipeline).
- ORACode semantics (annotation, query, conflict resolution).
- Agent and non-agent operation paths.

Calamum scenarios simulate burst traffic, malformed inputs, tampering attempts, and operational edge cases so that regressions and security gaps are caught before deployment.

---

## 2. Role in the CodeSentinel Ecosystem

- **For ORACall**: Calamum drives scripted PEI events through `codesentinel oracall` commands to validate:
  - Schema and grammar enforcement.
  - Dual-report requirements and SLA adherence.
  - Signature verification and archive-first storage.
  - TRIAD index integrity and lookup performance.
- **For ORACode**: Calamum issues semantic annotations and queries to verify:
  - Registry-enforced vocabulary usage.
  - Conflict-detection and auditor workflows.
  - Semantics storage performance and integrity.
- **For Agents**: Calamum provides repeatable scenarios for evaluating:
  - Agent-assisted ingestion and retrieval speed.
  - Token usage and SessionMemory hit rates.
  - Agent compliance with SEAM rules (no Unicode in console output, no bypass of signatures/ACLs).

Calamum is a test harness only. It does not process production traffic.

---

## 3. Core Concepts

### 3.1 Scenario

A **scenario** is a named, versioned test case that defines:

- Preconditions (for example, existing metrics files, registry versions).
- A sequence of CLI commands and, optionally, agent calls.
- Expected outputs, metrics, or state transitions.

Scenarios are expressed in a simple, repository-local format (for example, YAML or JSON). Future work will define the exact schema.

### 3.2 Profiles

A **profile** is a collection of scenarios grouped by intent, such as:

- `ingestion` — throughput, latency, and error handling for ORACall.
- `semantics` — annotation density, conflict frequency, and query performance for ORACode.
- `security` — tamper attempts, replay attacks, and missing-reports simulations.

Profiles are invoked via CLI flags (for example, `--profile ingestion`).

### 3.3 Targets

A **target** is the subsystem under test. Initial targets include:

- `oracall` — ORACall ingestion pipeline.
- `oracode` — ORACode semantics pipeline.

Additional targets may be added as new features land.

---

## 4. CLI Integration (Planned)

Calamum will be exposed through the `codesentinel` CLI as a dedicated command group:

- `codesentinel calamum test --target <name> [--profile <name>] [--scenario <id>]`
- `codesentinel calamum list --target <name>`

Examples (planned):

- `codesentinel calamum test --target oracall --profile ingestion`
- `codesentinel calamum test --target oracode --profile semantics`

These commands will:

1. Load the selected profile and scenarios from repository-local configuration.
2. Execute the scenarios using the existing CLI commands (for example, `codesentinel oracall ingest`).
3. Record metrics and results in `docs/metrics/calamum/*.jsonl` for later analysis.

Calamum must be fully functional without any agent integration; agents are an optional enhancement layer.

---

## 5. Metrics and Reporting

Calamum is tightly coupled to the performance audit requirements described in `ORACALL_ORACODE_COMPREHENSIVE_PROPOSAL.md`:

- **Performance Metrics**:
  - Ingestion latency and throughput (events per minute).
  - Retrieval latency for typical queries.
  - Storage overhead for indexes and metadata.
  - Operator effort (approximated by scripted step counts).
- **Agent Metrics** (when agents are enabled):
  - Token usage per scenario and per profile.
  - SessionMemory hit rates.
  - Any agent-specific errors or policy violations.
- **Security Metrics**:
  - Tamper attempts detected vs missed.
  - Signature and ACL failures.
  - Archive integrity checks for rotated logs.

Calamum writes JSONL outputs so that ORACL tiers and analytics tools can consume them without new parsers.

---

## 6. SEAM Alignment

Calamum itself must follow SEAM principles:

- **Security**:
  - Never modifies production data; operates only on test artifacts or sandboxed copies.
  - All destructive actions (for example, cleanup of test data) use archive-first policies.
  - Logs all operations with repository-relative paths.
- **Efficiency**:
  - Reuses existing CLI commands and metrics infrastructure.
  - Avoids bespoke test runners where possible.
- **Minimalism**:
  - Uses a single scenario format for all targets.
  - Stores results in a small set of JSONL streams under `docs/metrics/calamum/`.

---

## 7. Relationship to ORACall and ORACode Plans

The ORACall and ORACode planning documents reference Calamum as the harness used to:

- Validate ORACall schema, ingestion, and TRIAD indexing under load.
- Exercise ORACode semantics, storage, and conflict-resolution routines.
- Enforce performance and security regression gates defined in the comprehensive proposal.

This overview serves as the initial specification for Calamum. Implementation details (scenario schema, configuration files, and CLI wiring) will be added as the ORACall and ORACode pipelines are implemented.
