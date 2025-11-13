# ORACL Integration Architecture: How Upgrades Enhance Existing Operations

This document explains how the DHIS system, Advise Mode, and semantic CLI refactoring integrate with current ORACL™ operations (Session Tier, Context Tier, Intelligence Tier) and how confidence ranking works across all layers.

---

## Current ORACL Architecture (Foundation)

### Tier 1: Session Memory

- **Purpose:** In-memory cache for current task
- **Lifetime:** 0-60 minutes (current session)
- **Data:** File contexts, decisions, task state
- **API:** `SessionMemory.cache_file_context()`, `log_decision()`

### Tier 2: Context Tier

- **Purpose:** Weekly summaries from completed sessions
- **Lifetime:** 7 days (rolling window)
- **Data:** Session summaries, patterns, cross-refs
- **API:** `get_weekly_summaries()`, `search_recent_work()`

### Tier 3: Intelligence Tier

- **Purpose:** Long-term strategic patterns and historical wisdom
- **Lifetime:** Permanent
- **Data:** Decision outcomes, success rates, pattern recommendations
- **API:** `get_decision_context_provider()`, `report_decision_outcome()`

---

## How DHIS Integrates with ORACL Tiers

### Layer 1: Domain History (New - Feeds all Tiers)

**Data Flow:**

```
SessionMemory (Tier 1)
    ↓
    Logs work to: docs/domains/{domain}/history.jsonl
    ↓
Context Tier (Tier 2)
    ↓
    Weekly consolidation reads JSONL
    Generates: docs/domains/{domain}/INDEX.json
    ↓
Intelligence Tier (Tier 3)
    ↓
    Monthly analysis reads INDEX.json
    Extracts patterns, confidence scores
    Promotes to archive_index_manager
```

**Implementation:**

```python
# codesentinel/utils/session_memory.py (ENHANCED)

class SessionMemory:
    def log_domain_activity(self, domain: str, activity_data: dict):
        """NEW: Log work to domain history (feeds DHIS)."""
        
        # Step 1: Create session record
        session_record = {
            'timestamp': datetime.now().isoformat(),
            'domain': domain,
            'activity': activity_data,
            'session_id': self.session_id,
            'agent_id': get_agent_id(),
            'success': activity_data.get('success', True)
        }
        
        # Step 2: Write to domain history (append-only)
        history_file = Path(f"docs/domains/{domain}/history.jsonl")
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(session_record) + '\n')
        
        # Step 3: Also store in SessionMemory for Tier 1 access
        self._domain_activities.append(session_record)
        
        # Step 4: Log decision with confidence (for audit)
        self.log_decision(
            decision=f"Logged {domain} activity",
            rationale="Auto-populated by SessionMemory for DHIS",
            related_files=[str(history_file)]
        )
```

**Confidence Ranking Flow:**

```python
# In consolidation task (Tier 2 → Tier 3 promotion)

def consolidate_domain_history(domain: str):
    """Read domain history and compute confidence scores."""
    
    # Step 1: Load all sessions for domain
    history_file = Path(f"docs/domains/{domain}/history.jsonl")
    sessions = [json.loads(line) for line in history_file.read_text().splitlines()]
    
    # Step 2: Compute confidence metrics
    total_sessions = len(sessions)
    successful = sum(1 for s in sessions if s.get('success', True))
    success_rate = successful / total_sessions if total_sessions > 0 else 0
    
    # Step 3: Compute velocity
    time_span = (sessions[-1]['timestamp'] - sessions[0]['timestamp']).total_seconds() / 86400
    velocity = total_sessions / time_span if time_span > 0 else 0
    
    # Step 4: Generate INDEX entry with CONFIDENCE
    index_entry = {
        'domain': domain,
        'last_updated': datetime.now().isoformat(),
        'statistics': {
            'total_sessions': total_sessions,
            'success_rate': success_rate,  # Confidence metric #1
            'velocity': velocity,
            'recent_sessions': sessions[-5:]
        },
        'patterns': analyze_patterns(sessions),
        'recommendations': generate_recommendations(sessions),
        
        # CONFIDENCE SCORES (new)
        'confidence': {
            'success_rate': success_rate,        # 0.0-1.0
            'pattern_strength': compute_pattern_strength(sessions),  # How consistent
            'recency': compute_recency(sessions[-1]['timestamp']),   # How fresh
            'sample_size': min(total_sessions / 30, 1.0),  # Normalized count
            
            # COMPOSITE CONFIDENCE (weighted average)
            'overall': (
                success_rate * 0.40 +
                compute_pattern_strength(sessions) * 0.30 +
                compute_recency(sessions[-1]['timestamp']) * 0.20 +
                min(total_sessions / 30, 1.0) * 0.10
            )
        },
        
        # Cross-refs to related operations (for Advise Mode)
        'related_integration_ops': find_related_ops(domain, sessions),
        'critical_junctions': detect_junctions(sessions)
    }
    
    return index_entry
```

---

## How Advise Mode Integrates with ORACL

### Junction Detection Uses Confidence Scores

**Tier 1 (Session):** Real-time junction detection

```python
# During current session
session = SessionMemory()

# Check for junctions using live data
junctions = AdviseMode.detect_junctions(
    domain='process',
    current_analysis=session.get_domain_analysis(),
    severity_level=2
)

# Advise Mode uses session data + confidence
for junction in junctions:
    if junction.confidence >= 0.7:  # High confidence
        session.log_decision(
            decision="Junction detected",
            rationale=f"Confidence: {junction.confidence:.0%}",
            related_files=junction.related_files
        )
```

**Tier 2 (Context):** Weekly pattern confidence

```python
# Weekly consolidation
def compute_pattern_strength(sessions):
    """Measure confidence in detected patterns."""
    
    # How consistently does pattern appear?
    pattern_frequency = count_pattern_occurrences(sessions)
    consistency = pattern_frequency / len(sessions)
    
    # Confidence depends on consistency + recency + sample size
    return {
        'frequency': pattern_frequency,
        'consistency': consistency,          # 0.0-1.0
        'confidence': consistency * 0.8 + min(len(sessions)/10, 1.0) * 0.2
    }
```

**Tier 3 (Intelligence):** Historical junction correlation

```python
# Monthly historical analysis
def analyze_junction_patterns():
    """Correlate junctions with outcomes for future prediction."""
    
    # Load historical junctions and their outcomes
    history = load_junction_outcomes(days=90)
    
    correlations = {}
    for junction_type in JunctionType:
        outcomes = [h for h in history if h['type'] == junction_type]
        
        if outcomes:
            success_rate = sum(1 for o in outcomes if o['outcome'] == 'positive') / len(outcomes)
            avg_impact = statistics.mean([o['impact_score'] for o in outcomes])
            
            correlations[junction_type] = {
                'success_rate': success_rate,
                'avg_impact': avg_impact,
                'prediction_confidence': min(success_rate * 0.7 + len(outcomes)/50 * 0.3, 1.0)
            }
    
    return correlations
```

### Advise Mode Confidence Ranking

```python
class AdviseMode:
    def rank_advice(self, advice_list: List[Advice]) -> List[Advice]:
        """Rank advice by confidence × impact."""
        
        for advice in advice_list:
            # Confidence from ORACL tiers
            junction_confidence = advice.junction.confidence  # From DHIS
            pattern_confidence = advice.pattern_strength      # From Tier 2/3
            
            # Combined confidence
            advice.confidence = (
                junction_confidence * 0.6 +
                pattern_confidence * 0.4
            )
            
            # Rank: confidence × impact
            advice.rank_score = advice.confidence * advice.impact_score
        
        advice_list.sort(key=lambda a: a.rank_score, reverse=True)
        return advice_list
```

---

## Integration Points: CLI Architecture with ORACL

### Semantic Subcommands Inform Confidence

The new semantic CLI hierarchy (LIFECYCLE, DISCOVERY, INTELLIGENCE, COORDINATION) maps to ORACL tiers:

```
CLI Tier               ORACL Tier         Purpose
────────────────────────────────────────────────────────────────
LIFECYCLE      →   Session (Tier 1)    Track current processes
DISCOVERY      →   Session (Tier 1)    Discover current state
INTELLIGENCE   →   Context/Archive     Query historical patterns
COORDINATION   →   Intelligence        Multi-instance strategy
```

**Mapping:**

```python
# codesentinel/cli/process_utils.py (ENHANCED for ORACL)

def handle_lifecycle_status(args):
    """[LIFECYCLE] Status of current processes (Tier 1)."""
    session = SessionMemory()
    
    # Query Tier 1 (Session)
    status = session.get_domain_analysis('process')
    
    # Log to domain history
    session.log_domain_activity('process', {
        'action': 'status_check',
        'timestamp': datetime.now().isoformat()
    })
    
    return format_output(status)

def handle_intelligence_info(args):
    """[INTELLIGENCE] Query historical patterns (Tier 3)."""
    
    # Query Tier 3 (Intelligence)
    provider = get_decision_context_provider()
    context = provider.get_decision_context(
        decision_type="process_monitoring",
        search_radius_days=30
    )
    
    # Include confidence scores
    return {
        'recommendation': context.recommended_actions[0],
        'confidence': context.confidence_score,  # ORACL confidence
        'based_on': context.historical_patterns
    }

def handle_coordination_coordinate(args):
    """[COORDINATION] Multi-instance strategy (Tier 3 + Intelligence)."""
    
    # Query all instances + historical coordination data
    instances = find_instances()
    
    # Get historical coordination patterns
    provider = get_decision_context_provider()
    patterns = provider.search_patterns(
        pattern_type="multi_instance_coordination",
        confidence_threshold=0.7  # Only high-confidence patterns
    )
    
    # Recommend strategy
    strategy = recommend_coordination_strategy(instances, patterns)
    
    return {
        'strategy': strategy,
        'confidence': compute_strategy_confidence(patterns),
        'instances': len(instances),
        'based_on_historical_patterns': len(patterns)
    }
```

---

## Confidence Ranking Across All Components

### Complete Confidence Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ORACL CONFIDENCE RANKING SYSTEM                                         │
│ How confidence flows through Session → Context → Intelligence tiers     │
└─────────────────────────────────────────────────────────────────────────┘

INPUT: New agent starting work in "process" domain

STEP 1: Session Tier (Real-time)
  ├─ Check SessionMemory cache
  ├─ Compute immediate confidence:
  │  ├─ Current context availability: 85% (cache hit)
  │  ├─ File recency: 92% (files modified today)
  │  └─ Session confidence: 88%
  └─ Log: "Session started: confidence 88%"

STEP 2: Context Tier (Weekly)
  ├─ Query last 7 days of "process" work
  ├─ Compute pattern confidence:
  │  ├─ Success rate: 95% (19/20 tasks succeeded)
  │  ├─ Pattern consistency: 78% (patterns appear in 78% of sessions)
  │  ├─ Sample size confidence: 85% (20 sessions adequate)
  │  └─ Weekly pattern confidence: 86%
  └─ Result: "Weekly patterns strong (86% confidence)"

STEP 3: Intelligence Tier (Historical)
  ├─ Query 90-day history for "process" patterns
  ├─ Compute strategic confidence:
  │  ├─ Historical success rate: 92% (long-term average)
  │  ├─ Pattern recurrence: 89% (patterns appear across multiple months)
  │  ├─ Prediction accuracy: 84% (historical predictions correct 84% of time)
  │  └─ Strategic confidence: 88%
  └─ Result: "Strategic patterns reliable (88% confidence)"

STEP 4: DHIS Junction Analysis
  ├─ Detect critical junctions in domain
  ├─ Compute junction confidence:
  │  ├─ Feature clustering detected: 92% confidence
  │  ├─ Tech debt spike: 76% confidence
  │  ├─ Security drift: 98% confidence (always high for security)
  │  └─ Average junction confidence: 89%
  └─ Result: "3 junctions detected, average 89% confidence"

STEP 5: Advise Mode Recommendation
  ├─ Synthesize all confidence sources
  ├─ Rank advice by: confidence × impact
  │  ├─ Recommendation A: "Address tech debt" 
  │  │  └─ Confidence: 76% × Impact: 7/10 = Score 53.2
  │  ├─ Recommendation B: "Consolidate features"
  │  │  └─ Confidence: 92% × Impact: 5/10 = Score 46.0
  │  └─ Recommendation C: "Security review"
  │     └─ Confidence: 98% × Impact: 9/10 = Score 88.2
  └─ Output ranked by confidence × impact

FINAL OUTPUT:
  Priority 1 (Confidence 88%, Impact 9): Security review
  Priority 2 (Confidence 92%, Impact 7): Feature consolidation
  Priority 3 (Confidence 76%, Impact 7): Tech debt paydown
```

### Confidence Source Weighting

```python
# Master confidence computation

class OracleConfidenceAggregator:
    def compute_overall_confidence(self, domain: str, decision_type: str) -> float:
        """Compute overall confidence from all ORACL sources."""
        
        # Get confidence from each tier
        session_confidence = self._get_session_confidence(domain)      # Tier 1
        context_confidence = self._get_context_confidence(domain)      # Tier 2
        intelligence_confidence = self._get_intelligence_confidence(domain)  # Tier 3
        
        # Get confidence from DHIS junctions
        junction_confidence = self._get_junction_confidence(domain)
        
        # Get confidence from historical patterns
        pattern_confidence = self._get_pattern_confidence(domain, decision_type)
        
        # Weighted average (depends on decision type)
        weights = self._get_weights_for_decision(decision_type)
        
        overall = (
            session_confidence * weights['session'] +
            context_confidence * weights['context'] +
            intelligence_confidence * weights['intelligence'] +
            junction_confidence * weights['junction'] +
            pattern_confidence * weights['pattern']
        )
        
        return min(overall, 1.0)  # Cap at 100%
    
    def _get_weights_for_decision(self, decision_type: str) -> dict:
        """Weights vary by decision type."""
        
        # For IMMEDIATE decisions (start of session)
        if decision_type == "session_startup":
            return {
                'session': 0.50,        # Most weight on current state
                'context': 0.20,
                'intelligence': 0.10,
                'junction': 0.10,
                'pattern': 0.10
            }
        
        # For STRATEGIC decisions (multi-week planning)
        elif decision_type == "strategic_planning":
            return {
                'session': 0.10,        # Little weight on current moment
                'context': 0.20,
                'intelligence': 0.40,   # Most weight on history
                'junction': 0.20,
                'pattern': 0.10
            }
        
        # For SECURITY decisions (always weighted high)
        elif decision_type == "security_check":
            return {
                'session': 0.30,
                'context': 0.15,
                'intelligence': 0.25,
                'junction': 0.20,       # Security junctions = high weight
                'pattern': 0.10
            }
        
        # Default: balanced
        else:
            return {
                'session': 0.25,
                'context': 0.25,
                'intelligence': 0.25,
                'junction': 0.15,
                'pattern': 0.10
            }
```

---

## Example: Full Integration Flow

### Scenario: Agent Starts Work in "process" Domain at 08:00

```
TIME: 08:00 - Agent starts work

┌─ STEP 1: SessionMemory Initialization (Tier 1)
│  Agent: "codesentinel advise --domain process --severity 2"
│  ├─ Session created with ID: sess_20251112_0800_a1b2c3d4
│  ├─ Load domain context: docs/domains/process/
│  └─ Session confidence: 88% (cache hit on recent work)

├─ STEP 2: DHIS Context Loading (Bridge Tier 1→2→3)
│  ├─ Load: docs/domains/process/history.jsonl (last 50 entries)
│  ├─ Load: docs/domains/process/INDEX.json (yesterday's consolidation)
│  ├─ Analyze: Recent patterns in domain
│  ├─ Identify: 2 recent successful features, 1 debt item
│  └─ DHIS confidence: 86% (based on historical success rate)

├─ STEP 3: Junction Detection (Advise Mode)
│  ├─ Detect Feature Clustering: 92% confidence
│  │  └─ Features #2,3,4 ready simultaneously
│  ├─ Detect Tech Debt Spike: 76% confidence
│  │  └─ 370% acceleration in violations this week
│  ├─ Detect Security Drift: 98% confidence
│  │  └─ Hardcoded secrets accumulating (4 instances)
│  └─ Average junction confidence: 89%

├─ STEP 4: Intelligence Query (Tier 3)
│  ├─ Query: "What patterns worked in process domain?"
│  ├─ Results:
│  │  ├─ Multi-instance coordination pattern: 92% success rate
│  │  ├─ Feature consolidation pattern: 88% success rate
│  │  └─ Security remediation pattern: 95% success rate
│  └─ Intelligence confidence: 92% (based on 90-day history)

├─ STEP 5: Advise Mode Synthesis
│  ├─ Aggregate confidence sources:
│  │  ├─ Session: 88%
│  │  ├─ DHIS: 86%
│  │  ├─ Junctions: 89%
│  │  ├─ Intelligence: 92%
│  │  └─ Weighted overall: 89%
│  │
│  ├─ Rank recommendations by (confidence × impact):
│  │  #1. Security review: 98% × 0.9 = 0.88 (CRITICAL)
│  │  #2. Feature consolidation: 92% × 0.7 = 0.64 (HIGH)
│  │  #3. Tech debt paydown: 76% × 0.7 = 0.53 (MEDIUM)
│  │
│  └─ Output ranked list with confidence scores

└─ STEP 6: Log and Return
   Agent receives:
   ┌──────────────────────────────────────────────────────┐
   │ [ADVISE] Process Domain Analysis - Severity Level 2  │
   │                                                       │
   │ Overall Confidence: 89%                              │
   │ Analysis Sources: Session(88) + DHIS(86) +           │
   │                  Junctions(89) + Intelligence(92)    │
   │                                                       │
   │ Priority 1 [CRITICAL - 98% confidence]               │
   │ └─ Security Review: 4 hardcoded secrets found        │
   │    Action: Immediate remediation required            │
   │    Based on: Security junction detection + pattern   │
   │                                                       │
   │ Priority 2 [HIGH - 92% confidence]                   │
   │ └─ Feature Consolidation: Features #2,3,4 ready      │
   │    Suggestion: Combine into unified monitoring API   │
   │    Based on: Feature clustering + historical pattern │
   │                                                       │
   │ Priority 3 [MEDIUM - 76% confidence]                 │
   │ └─ Tech Debt Paydown: DRY violations accelerating    │
   │    Suggestion: Extract duplicate patterns (4h effort)│
   │    Based on: Debt spike junction + historical fix    │
   │                                                       │
   │ Next Steps: Address priorities in order              │
   │ (Security → Features → Tech Debt)                    │
   └──────────────────────────────────────────────────────┘
```

---

## How Confidence Enables Agent Automation

### Rule 1: High Confidence = Auto-Execute

```python
if recommendation.confidence >= 0.90:
    # Very high confidence - agent can proceed autonomously
    agent.log(f"Executing: {recommendation.action}")
    agent.execute_safely(recommendation)
else if recommendation.confidence >= 0.75:
    # Good confidence - ask for user approval
    user_approval = input(f"Proceed with {recommendation.action}? (y/N)")
    if user_approval == 'y':
        agent.execute(recommendation)
else:
    # Low confidence - present to user for decision
    user_decision = input(f"{recommendation.action}?\n1=Yes 2=No 3=Investigate")
    if user_decision == '1':
        agent.execute(recommendation)
```

### Rule 2: Security Always Blocks

```python
if recommendation.security_issue and recommendation.confidence >= 0.70:
    # Security issues with 70%+ confidence always block new work
    agent.log("SECURITY GATE: Blocking new features until issue resolved")
    agent.mode = "remediation"
    new_work_blocked = True
```

### Rule 3: Confidence Decay Over Time

```python
def apply_confidence_decay(confidence: float, hours_since_update: float) -> float:
    """Confidence decreases as data ages."""
    
    # Fresh data (< 1 hour): 100% confidence weight
    # 6 hours old: 80% weight
    # 24 hours old: 50% weight
    # 7 days old: 10% weight
    
    decay_factor = max(0.1, 1.0 - (hours_since_update / 168))  # 168 hours = 1 week
    return confidence * decay_factor
```

---

## Monitoring: Confidence Score Metrics

### Dashboard View (Hypothetical)

```
ORACL Confidence Metrics Dashboard
═════════════════════════════════════════════════════════════════

Domain: process
├─ Session Confidence:      88% ▓▓▓▓▓▓▓▓▓░ (9/10 items cached)
├─ Context Confidence:      86% ▓▓▓▓▓▓▓▓░░ (20 sessions, 95% success)
├─ Intelligence Confidence: 92% ▓▓▓▓▓▓▓▓▓░ (90-day history aligned)
├─ Junction Confidence:     89% ▓▓▓▓▓▓▓▓▓░ (3/3 junctions detected)
└─ Overall Confidence:      89% ▓▓▓▓▓▓▓▓▓░ [READY FOR HIGH-LEVEL DECISIONS]

Recommendations by Confidence:
├─ [98% ▓▓▓▓▓▓▓▓▓▓] Security review (CRITICAL)
├─ [92% ▓▓▓▓▓▓▓▓▓░] Feature consolidation (HIGH)
└─ [76% ▓▓▓▓▓▓▓▓░░] Tech debt paydown (MEDIUM)

Confidence Sources (Last 24h):
├─ Session hits: 156/200 (78%)
├─ Context tier queries: 12 (recent activity high)
├─ Intelligence queries: 4 (strategic decisions rare)
└─ Junction detections: 3 (all recent)

Action Thresholds:
├─ Auto-execute if confidence ≥ 90%: ✓ Enabled
├─ Manual approval if confidence 75-89%: ✓ Enabled
├─ Full investigation if confidence < 75%: ✓ Enabled
└─ Security override: ✓ ALWAYS blocks if issue detected
```

---

## Summary: Integration Framework

| Component | Feeds | Uses | Outputs |
|-----------|-------|------|---------|
| **SessionMemory** | Live work | Tier 1 cache | Domain history JSONL |
| **DHIS** | Domain history | Consolidation | INDEX.json + patterns |
| **Context Tier** | Weekly rollup | Tier 2 analysis | 7-day summaries |
| **Intelligence Tier** | Monthly rollup | Tier 3 storage | Strategic patterns |
| **Advise Mode** | All tiers + DHIS | Junction detection | Ranked recommendations |
| **CLI** | All components | Query API | Formatted output |
| **Confidence** | All sources | Weighting algorithm | 0.0-1.0 scores |

**Key Integration Points:**

1. SessionMemory auto-populates domain histories
2. Domain consolidation reads histories → generates INDEX.json
3. INDEX.json feeds DHIS junction detection
4. Junctions inform Advise Mode recommendations
5. All recommendations include confidence scores
6. Confidence scores enable safe automation

This creates a **virtuous cycle**: Each session teaches the system, histories build patterns, patterns inform decisions, decisions produce outcomes, outcomes improve confidence, high confidence enables automation.
