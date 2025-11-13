# DHIS Implementation: Q&A and Design Decisions

## Q0: Did We Fork a Branch?

**Answer:** No, we are currently on `main` branch (not a feature branch).

**Current Branch State:**

```
✓ main (current)
  ├─ feature/aegis-shield
  ├─ feature/phase-3-extended-satellites  
  ├─ feature/vault-secure-credentials
  └─ remotes/origin/* (upstream)
```

**Recommendation for DHIS work:**

We should create a feature branch for this work:

```bash
git checkout -b feature/dhis-domain-history-system
```

**Rationale:**

- DHIS is foundational (affects SessionMemory, scheduler, agent behavior)
- Allows parallel work on other features
- Can be reviewed before merge to main
- Can be reverted if needed

---

## Q1: What is the Mechanism for Generating 'Related Integration Opportunities'?

### Current State (Manual)

In `MEMORY_CLI_INTEGRATION_REPORT.md`, we manually identified 10 opportunities and assigned priorities. This is static.

### Proposed Automated Mechanism

**Data-Driven Generation via 3 Heuristics:**

#### Heuristic 1: Domain Co-Location

```python
# If two features were worked on in same domain/day, they're related
related_ops = find_operations_worked_today_in_domain(domain)

Example:
  Today: CLI refactoring + Monitor enhancement (same domain)
  → These share context, recommend together
```

#### Heuristic 2: File Dependency Graph

```python
# If two features touch overlapping files, they're related
graph = build_file_dependency_graph()
related_ops = find_ops_sharing_files(domain)

Example:
  Health Check (#2) needs process_monitor.py
  Monitoring Export (#3) also needs process_monitor.py
  → These are related (shared dependency)
```

#### Heuristic 3: Code Pattern Matching

```python
# If new code uses patterns established by previous ops, link them
related_ops = find_pattern_matches(new_code, historical_patterns)

Example:
  New PR for Health Check uses get_status() pattern
  → Previous work established get_status() API (Process Monitor #5)
  → Link as: "Health Check builds on Monitor work"
```

### Implementation in INDEX.json

```json
{
  "process": {
    "related_integration_ops": {
      "2": {
        "title": "Health Check Subcommand",
        "reason": "builds_on_monitor",
        "dependencies": [5],
        "shared_files": ["process_monitor.py"],
        "co_workers": ["3", "4"],
        "confidence": 0.92
      },
      "3": {
        "title": "Monitoring Export",
        "reason": "parallel_feature",
        "dependencies": [],
        "shared_files": ["process_utils.py"],
        "co_workers": ["2", "4"],
        "confidence": 0.88
      }
    }
  }
}
```

### Code Implementation

```python
# codesentinel/utils/domain_history.py

class DomainAnalyzer:
    def find_related_opportunities(self, op_id: int) -> List[int]:
        """Find related integration opportunities using 3 heuristics."""
        
        op = self.get_integration_op(op_id)
        related = []
        
        # Heuristic 1: Domain co-location
        domain_related = self._find_domain_colocated(op)
        
        # Heuristic 2: File dependencies
        file_related = self._find_file_dependent(op)
        
        # Heuristic 3: Pattern matching
        pattern_related = self._find_pattern_matched(op)
        
        # Merge with confidence scores
        related_ops = self._merge_with_confidence(
            domain_related, file_related, pattern_related
        )
        
        return related_ops
    
    def _find_domain_colocated(self, op) -> List[Tuple[int, float]]:
        """Find ops in same domain + similar time period."""
        domain = op["domain"]
        time_window = 7  # days
        
        colocated = []
        for history in self.load_domain_history(domain):
            if is_within_timewindow(history, time_window):
                confidence = 1.0 - (days_apart / time_window)
                colocated.append((history.op_id, confidence))
        
        return colocated
```

**Result:** Related ops auto-detected, updated daily in INDEX.json.

---

## Q2: Will '*PROPOSAL*.md' Documents be Considered During Preparation?

**Answer:** YES - Critical distinction needed.

### Document Categories

**Tier 1: Live Instructions (Agent-Read)**

- `codesentinel/AGENT_INSTRUCTIONS.md` (satellite docs)
- `docs/AGENT_INSTRUCTIONS.md`
- `deployment/AGENT_INSTRUCTIONS.md`
- Agent loads these every session (actively used)

**Tier 2: Architecture & Design Docs (Reference)**

- `docs/architecture/*.md` (policies, classifications)
- `POLICY.md`
- Agent reads if needed (not on hot path)

**Tier 3: Proposal Documents (Planning)**

- `*PROPOSAL*.md` (DHIS_PROPOSAL.md, MEMORY_CLI_INTEGRATION_REPORT.md)
- `*ANALYSIS*.md` (MEMORY_CLI_ANALYSIS.md)
- Agent reads during planning, not during execution

### Mechanism: Preparation Phase

**When agent starts work:**

```python
if agent.mode == "planning":
    # Load relevant PROPOSAL docs
    proposals = semantic_search("related PROPOSAL docs")
    context = proposals + instructions + history
    
    # Agent analyzes proposals
    agent.log("Reviewing integration opportunities from MEMORY_CLI_INTEGRATION_REPORT.md")
    
    # Agent generates plan informed by proposals
    plan = agent.generate_plan(context)
    
    agent.mode = "execution"

elif agent.mode == "execution":
    # Load live instructions (fast path)
    instructions = load_agent_instructions(domain)
    history = get_domain_guidance(domain)
    
    # Don't load proposals (not needed)
    # Focus on execution
```

### How This Works in Practice

**Scenario: Agent implements Health Check (#2)**

1. **Planning Phase:**
   - Load `MEMORY_CLI_INTEGRATION_REPORT.md` → sees Health Check described
   - Load `MEMORY_CLI_INTEGRATION_REPORT.md` → sees it's P1 (next sprint)
   - Load `DHIS_PROPOSAL.md` → understands how decision-making works
   - Load domain history → sees recent monitor work
   - Agent generates implementation plan

2. **Execution Phase:**
   - Loads `codesentinel/AGENT_INSTRUCTIONS.md` (satellite)
   - Loads `process_utils.py` patterns
   - Executes implementation
   - Ignores proposal docs (not needed)

3. **Post-Execution Phase:**
   - Logs work to `docs/domains/process/history.jsonl`
   - INDEX.json updates tomorrow
   - Next agent benefits from this work

### Configuration

```yaml
# In codesentinel/config/agent_config.yaml

agent:
  planning_phase:
    include_proposals: true          # Yes, read PROPOSAL docs
    include_analysis: true           # Yes, read ANALYSIS docs
    proposal_search_depth: "semantic"  # Deep search
    
  execution_phase:
    include_proposals: false         # No, skip for speed
    include_analysis: false          # No, skip for speed
    instructions_only: true          # Fast path
```

---

## Q3: Should We Create a Scheduled Task to Organize and Consolidate Collected Data?

**Answer:** YES - Essential for DHIS to work.

### Current Scheduler Architecture

```
tools/codesentinel/scheduler.py
├─ Daily Tasks (02:00)
│  ├─ config_validation
│  ├─ backup_operations
│  └─ metadata_update
├─ Weekly Tasks (Sunday 03:00)
│  ├─ security_scan
│  └─ dependency_update
└─ [Custom Tasks]
```

### New Task: Domain Index Consolidation

```python
# In tools/codesentinel/scheduler.py

SCHEDULED_TASKS = {
    # Existing tasks...
    
    "domain_index_consolidation": {
        "schedule": "daily",
        "time": "02:30",  # After backup, before metadata
        "priority": "high",
        "task": ConsolidateDomainIndex(),
        "timeout": 300,  # 5 minutes max
        "retry": 3,
        "log_level": "info"
    }
}
```

### Implementation

```python
# codesentinel/utils/domain_consolidator.py

class ConsolidateDomainIndex:
    """Nightly task: consolidate domain history + generate INDEX.json"""
    
    def execute(self):
        """Run consolidation pipeline."""
        
        # Step 1: Scan all domain history files
        domains = self.scan_domain_directories()
        
        for domain in domains:
            # Step 2: Load history (JSONL)
            history = self.load_jsonl(f"docs/domains/{domain}/history.jsonl")
            
            # Step 3: Analyze patterns
            patterns = self._detect_patterns(history)
            velocity = self._compute_velocity(history)
            trends = self._identify_trends(history)
            
            # Step 4: Find related ops
            related_ops = self._find_related_operations(domain, history)
            
            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(domain, analysis)
            
            # Step 6: Write to INDEX.json
            index_entry = {
                "domain": domain,
                "last_updated": datetime.now().isoformat(),
                "summary": {
                    "total_sessions": len(history),
                    "velocity": velocity,
                    "recent_work": history[-5:],
                    "patterns": patterns,
                    "trends": trends
                },
                "related_integration_ops": related_ops,
                "recommendations": recommendations,
                "cross_domain_refs": self._find_cross_refs(domain)
            }
            
            self.write_index(domain, index_entry)
        
        # Step 7: Consolidate all domains into master INDEX.json
        master_index = self._consolidate_all_domains(domains)
        self.write_master_index(master_index)
        
        # Step 8: Cleanup old history (optional)
        self._cleanup_old_entries(retention_days=90)
        
        logger.info(f"Domain consolidation complete: {len(domains)} domains")
```

### Task Configuration

```yaml
# In tools/config/scheduler_tasks.yaml

consolidation_task:
  enabled: true
  schedule: "0 2 * * *"          # 02:00 daily
  parallelism: 4                 # Process 4 domains in parallel
  batch_size: 50                 # Process 50 history entries per batch
  retention_days: 90             # Keep 90 days of history
  
  outputs:
    index_location: "docs/domains/INDEX.json"
    master_index: "docs/domains/INDEX_MASTER.json"
    stats_location: "logs/consolidation_stats.json"
  
  alerts:
    on_failure: true
    email_to: "maintainer@example.com"
    slack_webhook: "${SLACK_CONSOLIDATION_WEBHOOK}"
```

### Validation

```python
# Verify consolidation ran successfully

def validate_consolidation():
    """Ensure INDEX.json is fresh and valid."""
    
    checks = [
        ("INDEX.json exists", os.path.exists("docs/domains/INDEX.json")),
        ("INDEX.json is valid JSON", is_valid_json("docs/domains/INDEX.json")),
        ("All domains present", all_domains_in_index()),
        ("Recent activity logged", is_recent_timestamp(index["last_updated"])),
        ("No stale entries >90 days", cleanup_validated())
    ]
    
    for check_name, result in checks:
        logger.info(f"[{'OK' if result else 'FAIL'}] {check_name}")
    
    return all(result for _, result in checks)
```

---

## Q4: Advise Mode - Strategic Guidance System

This is EXCELLENT. Let me propose a comprehensive "Advise Mode" with severity scaling.

### Core Concept: Advise Mode

**What It Does:**

- Analyzes project progression continuously
- Identifies critical junctions (decision points, risks, opportunities)
- Offers strategic advice at right moments
- Severity scaling controls "aggressiveness" of recommendations

### Severity Matrix

```
┌─────────────────────────────────────────────────────────────┐
│ SEVERITY SCALE (Adjustable via config)                      │
├─────────────────────────────────────────────────────────────┤
│ LEVEL 0: Silent (No advice)                                 │
│   └─ No proactive recommendations                            │
│                                                              │
│ LEVEL 1: Passive (Alerts only on critical issues)           │
│   └─ Security: Always alert                                  │
│   └─ Efficiency: Alert if >30% waste detected                │
│   └─ Risk: Alert if critical path blocked                    │
│                                                              │
│ LEVEL 2: Balanced (Guided recommendations)                  │
│   └─ Security: Alert + recommend fix                         │
│   └─ Efficiency: Suggest improvements                        │
│   └─ Risk: Flag approaching problems                         │
│   └─ Opportunity: Recommend quick wins                       │
│                                                              │
│ LEVEL 3: Aggressive (Proactive strategic advice)            │
│   └─ All of Level 2, PLUS:                                   │
│   └─ Suggest architecture improvements                       │
│   └─ Recommend refactoring opportunities                     │
│   └─ Propose new features based on patterns                  │
│   └─ Strategic tech debt paydown                             │
│   └─ Cross-domain optimization opportunities                 │
│                                                              │
│ LEVEL 4: Expert (Deep strategic analysis)                   │
│   └─ All of Level 3, PLUS:                                   │
│   └─ Long-term roadmap guidance                              │
│   └─ Multi-quarter planning recommendations                  │
│   └─ Architectural debt analysis                             │
│   └─ Resource allocation optimization                        │
│   └─ Risk mitigation strategies                              │
└─────────────────────────────────────────────────────────────┘
```

### Advice Categories

```python
class AdviceCategory(Enum):
    SECURITY = "security"           # Non-negotiable
    EFFICIENCY = "efficiency"        # Performance, DRY
    MINIMALISM = "minimalism"        # Simplicity, focus
    RISK = "risk"                    # Project risks
    OPPORTUNITY = "opportunity"      # Quick wins
    STRATEGY = "strategy"            # Long-term planning
    REFACTORING = "refactoring"      # Tech debt
    CROSS_DOMAIN = "cross_domain"    # Multi-area opportunities
```

### Implementation Architecture

```python
# codesentinel/core/advise_mode.py

class AdviseMode:
    def __init__(self, severity_level: int = 2):
        """
        severity_level: 0 (silent) to 4 (expert)
        """
        self.severity = severity_level
        self.categories = self._configure_categories()
    
    def _configure_categories(self) -> Dict[str, bool]:
        """Enable/disable advice categories based on severity."""
        return {
            AdviceCategory.SECURITY: True,         # Always on
            AdviceCategory.EFFICIENCY: self.severity >= 1,
            AdviceCategory.MINIMALISM: self.severity >= 1,
            AdviceCategory.RISK: self.severity >= 1,
            AdviceCategory.OPPORTUNITY: self.severity >= 2,
            AdviceCategory.STRATEGY: self.severity >= 3,
            AdviceCategory.REFACTORING: self.severity >= 3,
            AdviceCategory.CROSS_DOMAIN: self.severity >= 3,
        }
    
    def analyze_and_advise(self, context: Dict) -> List[Advice]:
        """Main entry point: analyze project and generate advice."""
        
        advice_list = []
        
        # 1. Analyze current state
        analysis = self._deep_analysis(context)
        
        # 2. Identify critical junctions
        junctions = self._identify_junctions(analysis)
        
        # 3. Generate advice for each junction
        for junction in junctions:
            advice = self._generate_advice_for_junction(junction)
            
            # Filter by severity level
            if self._passes_severity_filter(advice):
                advice_list.append(advice)
        
        # 4. Rank by impact
        advice_list.sort(key=lambda a: a.impact_score, reverse=True)
        
        return advice_list
```

### Trigger Mechanisms

**Mechanism 1: Instance Event (Triggered)**

```bash
# Agent can request advice at any time
codesentinel advise --severity 3

# Outputs strategic guidance for current work
```

**Mechanism 2: Continuous Mode (Automated)**

```bash
# Turn on advise monitoring
codesentinel advise --continuous --severity 2

# Runs in background, alerts agent at junctions
# Logs: docs/logs/advise_mode_{date}.log
```

**Mechanism 3: Scheduled Analysis**

```python
# In scheduler (daily)
daily_tasks.add(
    "strategic_analysis",
    time="03:00",
    severity=3,  # Expert level analysis nightly
    task=AnalyzeProjectProgression()
)
```

### Critical Junctions (Auto-Detected)

```python
class CriticalJunction:
    """A decision point where advice is valuable."""
    
    PATTERNS = [
        {
            "name": "Feature Clustering",
            "detection": "Multiple related features ready concurrently",
            "advice": "Consider: Should these be consolidated or phased?"
        },
        {
            "name": "Technical Debt Spike",
            "detection": "Efficiency violations accumulating rapidly",
            "advice": "Recommend: Schedule debt paydown before velocity drops"
        },
        {
            "name": "Architecture Boundary",
            "detection": "Work spanning multiple domains",
            "advice": "Consider: Are domains properly separated?"
        },
        {
            "name": "Security Drift",
            "detection": "Config or policy violations trending",
            "advice": "Alert: Security posture degrading, immediate action needed"
        },
        {
            "name": "Resource Mismatch",
            "detection": "Velocity misaligned with capacity",
            "advice": "Recommend: Adjust timeline or scope"
        },
        {
            "name": "Pattern Recognition",
            "detection": "Similar issues resolved multiple times",
            "advice": "Recommend: Implement permanent fix for pattern"
        }
    ]
```

### Example Outputs

**Severity 1 (Passive)**

```
[ALERT] Security policy violation detected
  File: codesentinel/cli/__init__.py
  Issue: Hardcoded value found
  Action: Review and extract to config
  Severity: Critical
```

**Severity 2 (Balanced)**

```
[ADVICE] Efficiency opportunity identified
  Category: Cross-domain integration
  Observation: Both CLI and process domains use similar help formatting
  Recommendation: Consolidate into shared utility (save ~50 lines)
  Impact: Medium
  Effort: 2 hours
```

**Severity 3 (Aggressive)**

```
[STRATEGY] Architecture improvement opportunity
  Observation: 10 integration opportunities clustered around monitoring
  Pattern: Heavy focus on observability in v1.2
  Recommendation: Consider monitoring as first-class feature
  Actions:
    1. Extract monitoring to separate module
    2. Create monitoring plugin interface
    3. Plan for metrics export v1.2
  Impact: High (enables future work)
  Timeline: 2-3 sprints
```

**Severity 4 (Expert)**

```
[LONG-TERM] Project direction analysis
  Analysis Period: Last 3 months
  Trends:
    - Security: Improving (100% compliance)
    - Efficiency: Stable (slight optimization focus)
    - Minimalism: Strong (focus on clean architecture)
  
  Strategic Observations:
    1. ORACL™ memory system becoming central (good alignment)
    2. Agent instruction pattern scaling well (satellite docs working)
    3. Domain separation proving valuable (reduces coupling)
  
  Recommended Focus (Next 2 quarters):
    1. Production readiness (v1.2)
    2. Monitoring/observability (high ROI)
    3. Multi-instance coordination (foundation laid, ready to build)
  
  Risk Assessment:
    - Low: Core architecture stable
    - Medium: Feature scope expanding
    - Monitor: Technical debt accumulation
```

### Configuration

```yaml
# codesentinel/config/advise_mode.yaml

advise_mode:
  enabled: true
  default_severity: 2
  
  severity_0:
    name: "Silent"
    description: "No advice"
    categories: []
  
  severity_1:
    name: "Passive"
    categories:
      - security       # Always
      - risk           # > 50% impact
  
  severity_2:
    name: "Balanced"
    categories:
      - security
      - efficiency     # > 20% waste
      - minimalism     # > 10% duplication
      - risk
      - opportunity    # Quick wins
  
  severity_3:
    name: "Aggressive"
    categories: [security, efficiency, minimalism, risk, opportunity, strategy, refactoring, cross_domain]
    frequency: "per_session"
    depth: "deep"      # Analyzes patterns, history
  
  severity_4:
    name: "Expert"
    categories: [all]
    frequency: "daily"
    depth: "comprehensive"  # Multi-period analysis
    
    long_term_analysis:
      enabled: true
      lookback_months: 3
      forecast_months: 6
      
  triggers:
    instance_request:
      command: "codesentinel advise"
      severity_override: null   # Use default
    
    continuous_mode:
      enabled: false           # Agent sets with --continuous
      check_interval: 300      # Check every 5 min
    
    scheduled_analysis:
      enabled: true
      schedule: "0 3 * * *"   # Daily at 03:00
      severity: 3              # Expert level nightly
```

### Junction Detection Algorithm

```python
def identify_critical_junctions(self, analysis: Dict) -> List[CriticalJunction]:
    """Detect decision points and advice opportunities."""
    
    junctions = []
    
    # 1. Feature clustering
    if self._detect_feature_clustering(analysis):
        junctions.append(
            CriticalJunction(
                type="feature_clustering",
                severity="medium",
                message="Multiple related features ready - consolidate or phase?"
            )
        )
    
    # 2. Technical debt spike
    if self._detect_debt_acceleration(analysis):
        junctions.append(...)
    
    # 3. Security drift
    if self._detect_security_degradation(analysis):
        junctions.append(...)
    
    # 4. Architecture boundary crossing
    if self._detect_cross_domain_work(analysis):
        junctions.append(...)
    
    # 5. Pattern repetition
    if self._detect_repeated_issues(analysis):
        junctions.append(...)
    
    # 6. Resource mismatch
    if self._detect_velocity_deviation(analysis):
        junctions.append(...)
    
    return junctions
```

### Security Consideration

```python
# Advise mode respects SEAM Protection™

class AdviseModeSecurity:
    """Ensure Advise Mode aligns with core principles."""
    
    def __init__(self):
        # Security: Always non-negotiable
        self.security_always_on = True
        
        # Efficiency: Can be dialed up/down
        self.efficiency_tunable = True
        
        # Minimalism: Can be dialed up/down
        self.minimalism_tunable = True
    
    def validate_advice(self, advice: Advice) -> bool:
        """Ensure advice doesn't violate core principles."""
        
        # Check: Does advice violate security?
        if advice.violates_security:
            logger.error(f"Advice rejected (security): {advice}")
            return False
        
        # Check: Does advice violate existing decisions?
        if advice.contradicts_policy:
            logger.warning(f"Advice modified to align with policy: {advice}")
            advice = self._align_with_policy(advice)
        
        return True
```

---

## Summary: Your Questions Answered

| Q | Answer | Implementation |
|---|--------|-----------------|
| 0 | No branch created yet | Should create `feature/dhis-domain-history-system` |
| 1 | 3 heuristics: co-location, file deps, patterns | Auto-detect in daily consolidation task |
| 2 | YES - proposal docs read during planning phase | Planning vs execution phase separation |
| 3 | YES - need scheduled consolidation task | Daily 02:30 consolidation pipeline |
| 4 | Advise Mode with 5-level severity scale | Junctions trigger contextual guidance |

---

## Next Steps

Ready to implement all 4 components?

1. Create `feature/dhis-domain-history-system` branch
2. Implement Phase 1 (SessionMemory + directory structure)
3. Add scheduled consolidation task
4. Implement Advise Mode with severity scaling

**Proceed? YES / NO**
