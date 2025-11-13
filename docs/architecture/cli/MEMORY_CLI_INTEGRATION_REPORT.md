# Memory Process CLI - Implementation Report & Integration Opportunities

## Completed: Option B Refactoring ✅ (100% Complete)

### What Was Changed

**CLI Architecture Refactor:**

- **Before:** 6 flat flags (`--show`, `--show-orphans`, `--show-all`, `--show-ALL`, `--show-instance`, `--team-up`)
- **After:** 6 semantic subcommands organized into 4 logical tiers

**New Subcommand Structure:**

```bash
codesentinel memory process {subcommand} [options]

LIFECYCLE Tier (Process Management)
  ├─ status              Show tracked processes (replaces --show)
  └─ history [--limit]   Show cleanup history (replaces --show-orphans)

DISCOVERY Tier (System Observation)
  ├─ instances [-v]      Show all instances (replaces --show-all)
  └─ system [--limit]    Top system processes (replaces --show-ALL)

INTELLIGENCE Tier (Diagnostics)
  └─ info                Full instance diagnostics

COORDINATION Tier (IPC, Future)
  └─ coordinate          Inter-ORACL communication
```

**Backward Compatibility:**

- Legacy `--status`, `--stop`, `--restart`, `--interval` flags still work
- Old flags marked as deprecated in help text
- Seamless migration path for users

**Code Changes:**

- `process_utils.py`: 6 renamed handlers + improved output formatting + --limit/--verbose options
- `__init__.py`: Process subparsers with help organization + updated routing logic
- **All 60 existing tests pass** ✅

---

## Integration Opportunities Discovered

### 1. JSON Output Format 🎯 **[P0 - v1.1.3]**

**Current State:** All output is human-readable tables.

**Opportunity:** Add `--output json` for machine parsing.

```bash
codesentinel memory process status --output json
# Returns: [{"pid": 1234, "name": "python.exe", "status": "running"}]
```

**Implementation:**

- Add `--output {table,json,csv,yaml}` option to all subcommands
- Reuse existing `_get_process_details()` for consistency
- JSON schema validation in tests
- Enables: Scripting, log aggregation, streaming to external systems

---

### 2. Health Check Subcommand 🏥 **[P1 - v1.2]**

**Current State:** Commands show state but no overall health assessment.

**Opportunity:** Add dedicated `health-check` subcommand.

```bash
codesentinel memory process health-check
# [OK]   Process monitor running
# [OK]   No orphaned processes
# [WARN] 2 instances >400MB memory
# [FAIL] Cleanup spike: 5 forced kills
```

**Implementation:**

- Check: Monitor running, tracked PIDs healthy, cleanup rate normal, no stale instances
- Output: Structured pass/fail/warn/unknown
- Useful for: Kubernetes probes, monitoring dashboards, alerting

---

### 3. Monitoring Export - Prometheus 📊 **[P1 - v1.2]**

**Current State:** All commands show live data but don't export metrics.

**Opportunity:** Add `--export-metrics` flag for external monitoring.

```bash
codesentinel memory process system --export-metrics
# Output: Prometheus format
# codesentinel_process_memory_bytes{pid="1234"} 35700000
```

**Implementation:**

- Helper function `_export_prometheus_metrics()` → Prometheus format
- Exportable from all DISCOVERY and INTELLIGENCE commands
- Lightweight JSON export as fallback
- Compatible with: Prometheus scrape, InfluxDB, CloudWatch

---

### 4. Batch/Bulk Operations 🔄 **[P1 - v1.2]**

**Current State:** Each command queries current state; no action support.

**Opportunity:** Add command to bulk-manage instances.

```bash
codesentinel memory process instances --filter "memory > 400MB" --restart graceful
codesentinel memory process instances --filter "runtime > 48h" --kill
```

**Implementation:**

- Add `--action {restart,stop,signal}` flag
- Safety: Require `--force` and show confirmation first
- Implement via file-based IPC (send RESTART message to target instance)
- Useful for: Canary restarts, resource reclamation, emergency cleanup

---

### 5. Audit Logging Integration 🔍 **[P2 - v1.2]**

**Current State:** Each command prints to stdout but doesn't write to audit logs.

**Opportunity:** Add optional `--audit` flag for structured logging.

```bash
codesentinel memory process instances --audit
# Writes to: logs/audit/discovery_instances_{timestamp}.json
```

**Implementation:**

- Create `_audit_discovery()` helper in process_utils.py
- Log: timestamp, source PID, targets found, usernames, memory totals
- Output: JSON for machine parsing, plaintext for humans
- Useful for: Compliance, debugging multi-instance issues, performance tracking

---

### 6. Filtering & Aggregation Engine 🔧 **[P2 - v1.2]**

**Current State:** All commands show raw lists; users manually filter.

**Opportunity:** Add query language for filtering results.

```bash
codesentinel memory process instances --filter "memory > 50MB"
codesentinel memory process system --filter "username=admin AND memory > 100MB"
```

**Implementation:**

- Use `pyparsing` or simple lexer to build WHERE clause
- Apply filter before display (reduces output noise)
- Output summary: "Found 15 total, 3 matching filter"
- Useful for: Script automation, quick diagnostics, capacity planning

---

### 7. Alert Thresholds & Watch Mode ⚠️ **[P1 - v1.3]**

**Current State:** Commands show current state; no trend analysis.

**Opportunity:** Add `--watch` mode that detects anomalies.

```bash
codesentinel memory process system --watch --threshold "memory > 500MB" --window 5m
codesentinel memory process history --watch --alert-on "cleanups_per_minute > 2"
```

**Implementation:**

- Add `--watch` flag (continuous monitoring mode, updates every 10s)
- Define thresholds in config
- Write alerts to: `logs/alerts/{severity}_{timestamp}.json`
- Integration points: Slack webhook, email, PagerDuty

---

### 8. Historical Data Persistence & Trending 📈 **[P2 - v1.3]**

**Current State:** Cleanup history kept in memory (lost on restart); no trend analysis.

**Opportunity:** Persist history to SQLite and show trends.

```bash
codesentinel memory process history --window 24h --graph
codesentinel memory process history --export-csv history.csv
codesentinel memory process history --top-orphans 10
```

**Implementation:**

- Create `codesentinel/utils/metrics_db.py`: SQLite backend for history
- Schema: `cleanup_events(timestamp, pid, name, action, instance_pid)`
- Keep last 30 days (configurable retention)
- Dashboard ready: JSON export for Grafana plugin

---

### 9. Instance Grouping & Tagging 🏷️ **[P3 - post-v1.2]**

**Current State:** Instances shown as flat list; no organization by function/tier.

**Opportunity:** Add optional `--group-by` to categorize instances.

```bash
codesentinel memory process instances --group-by role
codesentinel memory process instances --group-by username
codesentinel memory process instances --group-by memory
```

**Implementation:**

- Detect role from process name/command line
- Support built-in groupers: username, role, memory_tier, runtime, region
- Output: Grouped table with subtotals per group
- Extensible: User-defined groupers in config

---

### 10. Configuration Profiles ⚙️ **[P3 - v1.3+]**

**Current State:** Default behavior fixed (limits, intervals, thresholds).

**Opportunity:** Add named profiles for different deployment scenarios.

```bash
codesentinel memory process instances --profile dev
codesentinel memory process system --profile prod
```

**Implementation:**

- Add `codesentinel/config/profiles/` directory
- Pre-built profiles: `dev.yaml`, `prod.yaml`, `minimal.yaml`, `debug.yaml`
- User profiles in: `~/.codesentinel/profiles/`
- Applied via `--profile` flag or `CODESENTINEL_PROFILE` env var

---

## Priority Matrix

| Feature | Impact | Effort | Priority | Target |
|---------|--------|--------|----------|--------|
| JSON Output | 🔴 High | 🟢 Low | **P0** | v1.1.3 |
| Health Check | 🔴 High | 🟡 Medium | **P1** | v1.2 |
| Monitoring Export | 🔴 High | 🟡 Medium | **P1** | v1.2 |
| Batch Operations | 🔴 High | 🟡 Medium | **P1** | v1.2 |
| Alert Thresholds | 🔴 High | 🟠 High | **P1** | v1.3 |
| Logging Integration | 🟡 Medium | 🟢 Low | **P2** | v1.2 |
| Filtering Engine | 🟡 Medium | 🟡 Medium | **P2** | v1.2 |
| Historical Trending | 🟡 Medium | 🟡 Medium | **P2** | v1.3 |
| Instance Grouping | 🟢 Low | 🟡 Medium | **P3** | post-v1.2 |
| Config Profiles | 🟢 Low | 🟡 Medium | **P3** | v1.3+ |

---

## Implementation Roadmap

### Phase 1: v1.1.3 (Patch)

- ✅ Refactor CLI to subcommands [COMPLETE]
- [ ] Add `--output json` to all subcommands
- [ ] Add `--limit` where missing
- [ ] Tests + documentation

### Phase 2: v1.2 (Major)

- [ ] Health check subcommand
- [ ] Monitoring export (Prometheus format)
- [ ] Batch/bulk operations on instances
- [ ] Audit logging integration
- [ ] Filtering engine

### Phase 3: v1.3 (Major)

- [ ] Alert thresholds & anomaly detection
- [ ] Historical data persistence & trending
- [ ] Configuration profiles
- [ ] Watch mode for continuous monitoring

### Post-v1.3

- [ ] Instance grouping/tagging
- [ ] Advanced analytics dashboard
- [ ] ML-based anomaly detection

---

## Summary

The refactoring from flags to subcommands provides an excellent foundation for future features. The 10 integration opportunities identified are all low-hanging fruit and would significantly improve operational visibility, compliance, and automation capabilities.

**Recommended immediate next steps:**

1. **This sprint:** Add `--output json` flag (v1.1.3 patch)
2. **Next sprint:** Health check + monitoring export (v1.2)
3. **Following sprint:** Alert thresholds + batch operations (v1.2+)
4. **Q1 2026:** Historical trending + advanced analytics (v1.3+)
