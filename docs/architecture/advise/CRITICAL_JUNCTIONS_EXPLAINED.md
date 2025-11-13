# Critical Junctions: How Advise Mode Detects Decision Points

The Advise Mode auto-detects 6 types of **critical junctions** - moments when strategic guidance is most valuable. These are decision points where the agent should pause and consider options.

---

## 1. Feature Clustering

**What It Detects:**
Multiple related features/tasks ready to implement simultaneously in the same timeframe.

**Detection Algorithm:**

```python
def detect_feature_clustering(analysis):
    """Find when multiple related features converge."""
    
    # Scan last 7 days of domain history
    recent_work = analysis['last_7_days']
    
    # Group by domain + integration opportunity ID
    clusters = {}
    for session in recent_work:
        domain = session['domain']
        if domain not in clusters:
            clusters[domain] = []
        clusters[domain].append(session)
    
    # Identify clustering: >2 related ops in same domain, <3 days apart
    for domain, sessions in clusters.items():
        if len(sessions) >= 2:
            time_span = max_date - min_date
            if time_span < 3_days:
                # CLUSTERING DETECTED
                return {
                    'type': 'feature_clustering',
                    'domain': domain,
                    'count': len(sessions),
                    'related_ops': [s['op_id'] for s in sessions],
                    'time_span': time_span
                }
```

**Example Scenario:**

```
Last 7 days:
  Day 1: Implemented Health Check (#2) - process domain
  Day 2: Tested Monitoring Export (#3) - process domain
  Day 3: Ready for batch operations (#4) - process domain

JUNCTION DETECTED: Feature clustering in "process"
  Related ops: [2, 3, 4]
  Advice: "Should these 3 monitoring features be consolidated into a single 
           'monitoring' subcommand, or phased sequentially to reduce risk?"
```

**Why It Matters:**

- Identifies opportunities for cross-feature optimization
- Prevents fragmented implementations (e.g., 3 separate monitoring commands vs. 1 unified interface)
- Allows agent to consider scope consolidation before implementation

---

## 2. Technical Debt Spike

**What It Detects:**
Rapid accumulation of efficiency violations, code duplication, or minimalism issues.

**Detection Algorithm:**

```python
def detect_tech_debt_spike(analysis):
    """Track efficiency violations over time."""
    
    # Load historical metrics
    history = analysis['domain_history']
    
    # Calculate 7-day average violations
    weekly_avg = calculate_average(history[-7:], metric='violation_count')
    
    # Calculate today's rate
    today_rate = history[-1]['violation_count']
    
    # Spike = today's rate > 1.5x weekly average
    if today_rate > weekly_avg * 1.5:
        acceleration = (today_rate - weekly_avg) / weekly_avg * 100
        
        return {
            'type': 'tech_debt_spike',
            'acceleration_percent': acceleration,
            'today_violations': today_rate,
            'weekly_average': weekly_avg,
            'violation_types': categorize_violations(history[-1])
        }
```

**Example Scenario:**

```
Last 7 days violation counts:
  Day 1: 2 violations
  Day 2: 1 violation
  Day 3: 3 violations
  Day 4: 2 violations
  Day 5: 2 violations
  Day 6: 1 violation
  Day 7: 1 violation  <- Average: 1.7/day

Today (Day 8): 8 violations (DRY violations + code duplication detected)

SPIKE DETECTED: 4.7x increase (370% acceleration)
  Recent violations:
    - Duplicated process_utils code in 3 files
    - Repeated patterns not extracted
    - Constants defined in 2+ places

Advice: "Technical debt accelerating rapidly. Recommend scheduling debt paydown
         in next sprint before velocity drops further. Quick wins available:
         1. Extract duplicated patterns (2 hours)
         2. Centralize constants (1 hour)
         3. Create shared utility module (3 hours)"
```

**Why It Matters:**

- Identifies when velocity will degrade if debt isn't addressed
- Allows agent to schedule preventive work before crisis
- Enables data-driven arguments for refactoring vs. new features

---

## 3. Security Drift

**What It Detects:**
Degradation of security posture - policy violations accumulating, credentials trending exposed, compliance issues.

**Detection Algorithm:**

```python
def detect_security_degradation(analysis):
    """Monitor security policy violations."""
    
    security_events = analysis['security_audit_log']
    
    # Count violations per type (last 14 days)
    violations_by_type = {}
    for event in security_events[-14:]:
        vtype = event['violation_type']  # e.g., "hardcoded_credential", "policy_violation"
        violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1
    
    # Trending check: are violations increasing?
    week1 = len([e for e in security_events[-14:-7] if e['severity'] >= 'medium'])
    week2 = len([e for e in security_events[-7:] if e['severity'] >= 'medium'])
    
    if week2 > week1:  # Worsening trend
        return {
            'type': 'security_drift',
            'trend': 'worsening',
            'violations_week1': week1,
            'violations_week2': week2,
            'critical_issues': violations_by_type,
            'recommendation': 'IMMEDIATE_ACTION'
        }
```

**Example Scenario:**

```
Security audit (last 14 days):
  Week 1 (Days 1-7):   1 medium violation (hardcoded DB password)
  Week 2 (Days 8-14):  4 medium violations (config hardcoding, API key exposure, etc.)

DRIFT DETECTED: 3x increase in security violations
  Trend: WORSENING
  Critical Issues:
    - hardcoded_credentials: 3 instances
    - policy_violations: 2 instances
    - unvalidated_config: 1 instance

Advice: "ALERT: Security posture degrading. Immediate action required.
         1. [CRITICAL] Remove hardcoded credentials from config (now)
         2. [HIGH] Implement config validation (today)
         3. [MEDIUM] Audit all env variables for exposure (this week)
         
         Do not proceed with feature work until security issues resolved."
```

**Why It Matters:**

- Security violations can't be ignored - SEAM Protection™ puts Security first
- Early detection prevents accumulation to critical state
- Forces prioritization of security fixes before feature work
- Mandatory for compliance and production readiness

---

## 4. Architecture Boundary Crossing

**What It Detects:**
Work spanning multiple domains simultaneously, indicating potential design issues or coupling problems.

**Detection Algorithm:**

```python
def detect_cross_domain_work(analysis):
    """Identify work crossing domain boundaries."""
    
    # Scan recent sessions
    domains_touched = set()
    sessions = analysis['last_7_days']
    
    for session in sessions:
        domains_touched.add(session['domain'])
        # Also track file changes across domains
        for file in session['files_modified']:
            file_domain = extract_domain(file)  # e.g., "cli", "utils", "core"
            domains_touched.add(file_domain)
    
    # Boundary crossing: >2 domains in single session
    if len(domains_touched) > 2:
        return {
            'type': 'architecture_boundary_crossing',
            'domains_involved': list(domains_touched),
            'count': len(domains_touched),
            'sessions': len(sessions),
            'question': 'Are domains properly separated?'
        }
```

**Example Scenario:**

```
Last 7 days work spans:
  Domain 1: codesentinel/cli/ (CLI command refactoring)
  Domain 2: codesentinel/utils/ (Process monitoring)
  Domain 3: codesentinel/core/ (Instance manager)

Sessions touching multiple domains:
  Session 1: Modified cli/__init__.py AND utils/process_monitor.py
  Session 2: Modified utils/instance_manager.py AND core/instance.py
  Session 3: Modified cli/process_utils.py AND utils/process_monitor.py

JUNCTION DETECTED: Work heavily crossing boundaries
  Pattern: CLI layer tightly coupled to Utils layer

Questions:
  1. Should CLI be decoupled from Utils?
  2. Are domain responsibilities clear?
  3. Should we introduce abstraction layer?

Recommendations:
  1. Review domain separation strategy
  2. Consider facade/adapter pattern for cli-utils boundary
  3. Document expected cross-domain interactions
```

**Why It Matters:**

- High cross-domain coupling increases complexity
- Makes future changes risky (changing one domain breaks another)
- Identifies when architectural refactoring would pay off
- Helps maintain SEAM Protection™ principle of modularity and reuse

---

## 5. Resource Mismatch

**What It Detects:**
Velocity misalignment with available capacity - either backlog building up or idle capacity.

**Detection Algorithm:**

```python
def detect_velocity_deviation(analysis):
    """Monitor velocity vs. capacity."""
    
    # Calculate 30-day velocity
    historical_velocity = analyze_velocity(analysis['last_30_days'])
    
    # Current capacity (tasks ready to work on)
    backlog = count_ready_tasks()
    in_progress = count_in_progress_tasks()
    
    # Expected completion time
    current_pace = count_completed_today()
    days_to_clear = (backlog + in_progress) / current_pace if current_pace > 0 else float('inf')
    
    # Deviation detection
    if days_to_clear > 14:  # More than 2 weeks backlog
        return {
            'type': 'resource_mismatch',
            'issue': 'backlog_accumulation',
            'backlog_size': backlog,
            'current_velocity': current_pace,
            'historical_velocity': historical_velocity,
            'days_to_clear': days_to_clear,
            'recommendation': 'increase_capacity_or_reduce_scope'
        }
    
    elif days_to_clear < 2 and backlog == 0:  # Idle capacity
        return {
            'type': 'resource_mismatch',
            'issue': 'excess_capacity',
            'backlog_size': backlog,
            'recommendation': 'prioritize_new_features_or_tech_debt'
        }
```

**Example Scenario:**

```
Last 30 days velocity: 2.5 features/week

Current state:
  Backlog: 8 tasks ready
  In Progress: 2 tasks
  Total: 10 tasks
  Today's completion rate: 0.3 tasks/day

MISMATCH DETECTED: Resource allocation misaligned
  Current pace would clear backlog in: 33 days
  Expected pace would clear it in: 10 days
  Gap: 3x slower than historical velocity

Possible causes:
  1. Team capacity reduced
  2. Tasks larger/more complex than expected
  3. Blocking dependencies
  4. Decreased focus/priority

Options:
  A. Reduce scope (prioritize top 3-5 tasks only)
  B. Increase capacity (add team members or adjust allocation)
  C. Break down tasks (make them smaller/parallel-able)
  D. Extend timeline (adjust expectations)

Recommendation: Review capacity constraints, then choose A-D.
```

**Why It Matters:**

- Prevents timeline surprises
- Allows data-driven resource allocation decisions
- Identifies when timeline adjustments are needed early
- Enables proactive capacity planning

---

## 6. Pattern Repetition

**What It Detects:**
Same type of issue being resolved multiple times, indicating a need for permanent/systematic fix.

**Detection Algorithm:**

```python
def detect_repeated_issues(analysis):
    """Identify recurring problems that need systematic fixes."""
    
    # Load issue history
    issues = analysis['issue_history']
    
    # Group by pattern (e.g., "hardcoded_config", "missing_test_coverage")
    patterns = {}
    for issue in issues[-30:]:  # Last 30 days
        pattern = issue['pattern_type']
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(issue)
    
    # Repetition: same pattern >2x in 30 days
    repeated = {p: issues for p, issues in patterns.items() if len(issues) >= 3}
    
    if repeated:
        return {
            'type': 'pattern_repetition',
            'patterns': repeated,
            'recommendation': 'implement_systematic_fix'
        }
```

**Example Scenario:**

```
Last 30 days issue history:
  Day 3:  "Hardcoded database URL in config" - FIXED manually
  Day 8:  "Hardcoded API key in process_utils.py" - FIXED manually
  Day 14: "Hardcoded secret in test file" - FIXED manually
  Day 22: "Hardcoded token in instance_manager.py" - FIXED manually

PATTERN DETECTED: Hardcoded secrets appearing repeatedly
  Occurrences: 4 instances
  Manual fixes: 4 times
  Time spent: ~4 hours total

Systematic Fix Options:
  1. Config validation tool (catch at build time)
  2. Pre-commit hook (detect before commit)
  3. Static analysis (automated scanning)
  4. Template enforcement (prevent in templates)

Recommendation: Implement option 3 (static analysis) + option 4 (templates)
  Timeline: 4 hours (one-time investment)
  ROI: Eliminates 4+ hours/month of manual fixes
  
Advice: "This pattern will repeat unless we implement systematic fix.
         Recommend scheduling static analysis implementation this week."
```

**Why It Matters:**

- Identifies systemic issues needing permanent solutions
- Prevents endless manual fixes of same problem
- Enables proactive prevention vs. reactive repairs
- Improves long-term efficiency and code quality

---

## Junction Summary Table

| Junction | Triggers When | Typical Advice | Severity |
|----------|---------------|----------------|----------|
| Feature Clustering | 2+ related features in same domain <3 days apart | Consolidate or phase? | Medium |
| Tech Debt Spike | Violations spike >1.5x weekly average | Schedule paydown before velocity drops | High |
| Security Drift | Security violations trending worse | Immediate action required | CRITICAL |
| Architecture Boundary | Work spans >2 domains heavily | Review separation strategy | Medium |
| Resource Mismatch | Velocity misaligned with capacity | Adjust scope/timeline/capacity | Medium |
| Pattern Repetition | Same issue fixed 3+ times in 30 days | Implement systematic fix | High |

---

## Implementation Priority

**Phase 1 (v1.2):** Implement junctions 2, 3, 6 (highest impact)

- Tech Debt Spike (prevents crisis)
- Security Drift (mandatory for compliance)
- Pattern Repetition (improves efficiency)

**Phase 2 (v1.3):** Implement junctions 1, 4, 5

- Feature Clustering (optimization)
- Architecture Boundary (long-term health)
- Resource Mismatch (planning aid)

---

## How Agent Uses This Information

**Scenario: Agent starts new work in "process" domain**

```
Agent initialization:
  1. Load domain history for "process"
  2. Analyze junctions for domain
  3. If junctions detected:
     - Log advise mode findings
     - Offer guidance before starting work
  4. If security drift detected:
     - BLOCK new feature work
     - Force security remediation first
  5. If pattern repetition detected:
     - Suggest systematic fix before proceeding
     - Link to successful fixes from history

Example log output:
  [ADVISE] Junction Analysis for Domain: process
  
  [CLUSTER] Feature clustering detected
    → Related ops [2,3,4] ready simultaneously
    → Recommendation: Consolidate monitoring features?
  
  [DEBT] Tech debt spike: 370% acceleration
    → Quick wins: Extract patterns (2h), centralize constants (1h)
    → Recommend: Schedule debt sprint next week
  
  [SECURITY] No drift detected ✓
  
  [BOUNDARY] Architecture stable ✓
  
  [CAPACITY] Velocity aligned ✓
  
  [PATTERN] 4 hardcoded secrets in last month
    → Systematic fix needed: Implement config validation
    → Estimated: 4 hours one-time investment
  
  Proceed with confidence: All junctions analyzed, minor debt items noted.
```

---

## Configuration & Severity

```yaml
# codesentinel/config/junctions.yaml

junctions:
  feature_clustering:
    enabled: true
    threshold_count: 2
    threshold_days: 3
    severity: "medium"
    auto_alert: false
  
  tech_debt_spike:
    enabled: true
    threshold_acceleration: 1.5
    severity: "high"
    auto_alert: true    # Alert immediately
  
  security_drift:
    enabled: true
    threshold_worsening: true
    severity: "critical"
    auto_alert: true    # ALWAYS alert
    blocks_new_work: true
  
  architecture_boundary:
    enabled: true
    threshold_domains: 3
    severity: "medium"
    auto_alert: false
  
  resource_mismatch:
    enabled: true
    threshold_backlog_days: 14
    severity: "medium"
    auto_alert: true
  
  pattern_repetition:
    enabled: true
    threshold_occurrences: 3
    threshold_days: 30
    severity: "high"
    auto_alert: true
```

This explains how Advise Mode detects critical junctions and provides strategic guidance!
