# Agent Metrics & Performance Tracking System

## Overview

Comprehensive tracking infrastructure for agent operations, CLI commands, errors, and ORACL learning curve. Designed for **zero data loss** with intelligent elevation thresholds.

**Key Principle:** ALL events are logged. Security threshold determines what's *shown* to user, not what's *tracked*.

---

## Architecture

### Data Storage

```
docs/metrics/
├── agent_operations.jsonl      # All operations (append-only)
├── security_events.jsonl        # Security events (elevated + noted)
├── error_patterns.jsonl         # Error tracking and recovery
└── performance_summary.json     # Daily rollup (generated)
```

### Event Types

1. **CLI Commands** - Every command execution tracked
2. **Agent Decisions** - Recommendations, user actions, outcomes
3. **ORACL Queries** - Intelligence queries with confidence scores
4. **Security Events** - Policy violations, credential leaks, vulnerabilities
5. **Error Patterns** - Failures, recovery attempts, success rates
6. **Performance Metrics** - Cache hits, latencies, efficiency gains

---

## Usage Examples

### 1. Track CLI Commands (Automatic with Decorator)

```python
from codesentinel.utils.metrics_wrapper import track_cli_command

@track_cli_command('clean')
def handle_clean_command(args, codesentinel):
    # Command implementation
    files_processed = clean_root_directory()
    
    return {
        'files_processed': files_processed,
        'success': True
    }
```

**Logged automatically:**

- Command name and arguments
- Success/failure status
- Execution duration
- Metadata (files_processed, etc.)

### 2. Track Security Events (Elevation Logic)

```python
from codesentinel.utils.metrics_wrapper import track_security_event

# Example: Credential detected
elevated = track_security_event(
    event_type='credential_leak',
    severity='high',  # high severity
    description='AWS key detected in config.py',
    threshold='medium',  # User threshold
    metadata={'file': 'config.py', 'line': 42}
)

if elevated:
    print("[WARN] AWS key detected - please review")
# ALWAYS logged, even if not elevated!
```

**Severity Levels:**

- `low` - Info/advisory (e.g., weak pattern detected)
- `medium` - Should review (e.g., TODO with security keyword)
- `high` - Action required (e.g., hardcoded credential)
- `critical` - Immediate action (e.g., active vulnerability)

**Threshold Behavior:**

```
User threshold = 'medium'
Event severity = 'low'     → logged as "noted" (not shown to user)
Event severity = 'medium'  → logged as "elevated" (shown to user)
Event severity = 'high'    → logged as "elevated" (shown to user)
```

### 3. Track Agent Decisions (ORACL Learning)

```python
from codesentinel.utils.metrics_wrapper import track_agent_decision

# Get ORACL recommendation
context = oracl_provider.get_decision_context(
    decision_type='policy_violation_handling',
    current_state={'violation_type': 'unauthorized_file'}
)

recommendation = context.recommended_actions[0]  # "archive"
confidence = context.confidence_score  # 0.87

# User makes decision
user_choice = input("Accept recommendation? (y/n): ")
user_action = 'accepted' if user_choice == 'y' else 'rejected'

# Execute and track outcome
if user_action == 'accepted':
    success = execute_recommendation(recommendation)
    outcome = 'success' if success else 'failure'
else:
    outcome = 'rejected'

# Log decision (builds learning curve)
track_agent_decision(
    decision_type='policy_violation_handling',
    recommendation=recommendation,
    user_action=user_action,
    confidence=confidence,
    outcome=outcome,
    metadata={'violation_type': 'unauthorized_file'}
)
```

**Learning Curve Analysis:**

- Tracks confidence scores over time
- Measures user acceptance rate
- Identifies successful patterns
- Feeds back into ORACL intelligence

### 4. Track ORACL Queries (Performance Monitoring)

```python
from codesentinel.utils.metrics_wrapper import track_oracl_query
import time

start_time = time.time()

# Query ORACL
context = oracl_provider.get_decision_context(
    decision_type='cleanup_strategy',
    search_radius_days=30
)

latency_ms = (time.time() - start_time) * 1000

# Track query
track_oracl_query(
    query_type='decision_context',
    confidence=context.confidence_score,
    cache_hit=context.from_cache,
    latency_ms=latency_ms,
    result_count=len(context.recommended_actions),
    metadata={'decision_type': 'cleanup_strategy'}
)
```

### 5. Track Performance Metrics (Efficiency Gains)

```python
from codesentinel.utils.metrics_wrapper import track_performance_metric

# Baseline: Pre-ORACL cache
baseline_latency = 250.0  # ms

# Measured: With ORACL Tier 1 cache
measured_latency = 45.0  # ms

track_performance_metric(
    metric_type='cache_latency',
    value=measured_latency,
    unit='ms',
    baseline=baseline_latency,
    metadata={'cache_tier': 'tier_1'}
)

# Improvement calculated automatically: (250-45)/250 = 82% improvement
```

---

## Performance Report Generation

### Generate Report (CLI)

```bash
# 7-day summary
python -m codesentinel.utils.agent_metrics --days 7

# 30-day with learning curve
python -m codesentinel.utils.agent_metrics --days 30 --learning-curve
```

### Programmatic Report

```python
from codesentinel.utils.agent_metrics import AgentMetrics

metrics = AgentMetrics()
report = metrics.generate_performance_report(days=7)

print(f"CLI Success Rate: {report['cli_metrics']['success_rate'] * 100:.1f}%")
print(f"ORACL Cache Hit Rate: {report['oracl_metrics']['cache_hit_rate'] * 100:.1f}%")
print(f"Avg Confidence: {report['oracl_metrics']['avg_confidence'] * 100:.0f}%")
```

### Sample Report Output

```
================================================================================
AGENT PERFORMANCE SUMMARY (7 days)
================================================================================

CLI Commands:
  Total: 142
  Success Rate: 97.2%
  Avg Duration: 385.32ms

ORACL Intelligence:
  Total Queries: 58
  Cache Hit Rate: 74.1%
  Avg Confidence: 86%
  Avg Latency: 42.18ms

Agent Decisions:
  Total: 23
  Accepted: 19
  Rejected: 4

Security Events:
  Elevated (shown to user): 3
  Noted (logged only): 12
  Total Tracked: 15

Errors:
  Total: 8
  Top Patterns:
    - file_not_found: 3
    - permission_denied: 2
    - timeout: 2
    - invalid_config: 1

================================================================================
```

---

## ORACL Learning Curve Visualization

```bash
python -m codesentinel.utils.agent_metrics --learning-curve --days 30
```

**Output:**

```
ORACL Learning Curve:
============================================================
Date         Avg Confidence  Trend
------------------------------------------------------------
2025-11-01     72.0% ████████████████████████
2025-11-02     74.5% ██████████████████████████
2025-11-03     78.2% ███████████████████████████████
2025-11-04     81.0% ████████████████████████████████
2025-11-05     83.5% █████████████████████████████████
2025-11-06     85.2% ██████████████████████████████████
2025-11-07     87.0% ███████████████████████████████████
============================================================
```

**Insights:**

- Shows ORACL confidence improvement over time
- Validates learning algorithm effectiveness
- Identifies optimal confidence thresholds for automation

---

## Integration Points

### 1. CLI Main Function

Wrap all command handlers with `@track_cli_command` decorator:

```python
@track_cli_command('clean')
def handle_clean(args, codesentinel):
    # existing code
    pass
```

### 2. Security Scanning

Replace direct print statements with tracking:

```python
# OLD:
if credential_found:
    print("[WARN] Credential detected")

# NEW:
if credential_found:
    elevated = track_security_event(
        event_type='credential_leak',
        severity='high',
        description=f"Credential in {file_path}",
        metadata={'file': file_path}
    )
    if elevated:
        print("[WARN] Credential detected")
    # Always logged for later analysis
```

### 3. ORACL Decision Workflow

Integrate into decision-making:

```python
# Get recommendation
context = oracl_provider.get_decision_context(...)

# Present to user
print(f"ORACL recommends: {context.recommended_actions[0]} (confidence: {context.confidence_score:.0%})")

# Track user response
user_action = get_user_decision()
outcome = execute_if_accepted(user_action)

# Log for learning
track_agent_decision(
    decision_type='...',
    recommendation=context.recommended_actions[0],
    user_action=user_action,
    confidence=context.confidence_score,
    outcome=outcome
)
```

### 4. Scheduler Integration

Add daily report generation:

```python
def _run_daily_tasks(self):
    # ... existing tasks ...
    
    # Generate metrics report
    try:
        from codesentinel.utils.agent_metrics import AgentMetrics
        metrics = AgentMetrics()
        report = metrics.generate_performance_report(days=7)
        tasks_executed.append('metrics_report_generation')
        self.logger.info(f"Metrics report generated: {report['cli_metrics']['total_commands']} commands tracked")
    except Exception as e:
        self.logger.error(f"Metrics report generation failed: {e}")
        errors.append(f"Metrics generation failed: {str(e)}")
```

---

## Benefits for Reporting

### 1. Performance Gains Tracking

**Before ORACL:**

```json
{
  "avg_command_duration_ms": 520.0,
  "cache_hit_rate": 0.0,
  "query_latency_ms": 250.0
}
```

**After ORACL:**

```json
{
  "avg_command_duration_ms": 385.0,  # 26% improvement
  "cache_hit_rate": 0.741,            # 74% cache hits
  "query_latency_ms": 42.0            # 83% improvement
}
```

### 2. Learning Curve Evidence

- **Week 1:** 72% avg confidence → User accepts 65% of recommendations
- **Week 2:** 78% avg confidence → User accepts 73% of recommendations
- **Week 3:** 85% avg confidence → User accepts 82% of recommendations
- **Week 4:** 87% avg confidence → User accepts 88% of recommendations

**Demonstrates:** ORACL learns from user decisions and improves over time.

### 3. Error Pattern Analysis

```json
{
  "error_patterns": {
    "file_not_found": {
      "occurrences": 15,
      "recovery_attempted": 12,
      "recovery_success": 10,
      "recovery_rate": 0.833
    }
  }
}
```

**Enables:** Targeted improvement of error handling strategies.

### 4. Security Posture Tracking

```json
{
  "security_events": {
    "total_detected": 45,
    "elevated_to_user": 8,
    "noted_only": 37,
    "by_severity": {
      "critical": 1,
      "high": 7,
      "medium": 15,
      "low": 22
    }
  }
}
```

**Shows:** Comprehensive security monitoring without alert fatigue.

---

## Downstream Debugging Support

### Query Historical Data

```python
from codesentinel.utils.agent_metrics import AgentMetrics
import json

metrics = AgentMetrics()

# Find all errors for specific command
with open(metrics.error_patterns_log, 'r') as f:
    errors = [json.loads(line) for line in f if 'clean' in line]

for error in errors:
    print(f"[{error['timestamp']}] {error['error_type']}: {error['error_message']}")
    print(f"  Context: {error['context']}")
    print(f"  Recovery: {error['recovery_success']}")
```

### Trace Security Event Context

```python
# Find all security events for a specific file
with open(metrics.security_events_log, 'r') as f:
    events = [
        json.loads(line) 
        for line in f 
        if 'config.py' in line
    ]

for event in events:
    print(f"[{event['severity'].upper()}] {event['description']}")
    print(f"  Status: {'Elevated' if event['elevated'] else 'Noted only'}")
    print(f"  Metadata: {event['metadata']}")
```

### Analyze Decision Patterns

```python
# Get all decisions where user rejected high-confidence recommendations
with open(metrics.operations_log, 'r') as f:
    rejections = [
        json.loads(line)
        for line in f
        if json.loads(line).get('event_type') == 'agent_decision'
        and json.loads(line).get('user_action') == 'rejected'
        and json.loads(line).get('confidence', 0) > 0.8
    ]

print(f"Found {len(rejections)} high-confidence rejections")
for rejection in rejections:
    print(f"  {rejection['decision_type']}: {rejection['recommendation']}")
    print(f"  Confidence: {rejection['confidence']:.0%}")
    print(f"  Reason: {rejection.get('metadata', {}).get('rejection_reason', 'Not specified')}")
```

---

## Implementation Status

- [x] Core metrics tracking module (`agent_metrics.py`)
- [x] Metrics wrapper utilities (`metrics_wrapper.py`)
- [x] Security event elevation logic
- [x] ORACL learning curve tracking
- [x] Performance report generation
- [x] CLI report tool
- [ ] Integration with CLI command handlers (TODO)
- [ ] Integration with security scanners (TODO)
- [ ] Integration with ORACL decision workflow (TODO)
- [ ] Scheduler integration for daily reports (TODO)

---

## Next Steps

1. **Integrate with existing CLI commands** - Add `@track_cli_command` decorators
2. **Update security scanning** - Replace prints with `track_security_event()`
3. **Enhance ORACL workflow** - Add decision tracking to dev-audit command
4. **Scheduler integration** - Add metrics report generation to daily tasks
5. **Dashboard creation** - Build visualization UI for metrics (v1.3)

---

## SEAM Protection™ Alignment

**Security:** All security events logged with severity-based elevation
**Efficiency:** Tracks performance gains and ORACL learning curve
**And:** Zero data loss - everything preserved for analysis
**Minimalism:** Single source of truth for all metrics

**All data has value potential.**
