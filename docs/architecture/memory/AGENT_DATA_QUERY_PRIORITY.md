# Agent Data Query Priority Directive

**DIRECTIVE**: Prioritize local cache, domain tracking, and ORACL memory checking before querying git when data can be obtained locally and overhead would not be increased.

---

## Priority Query Sequence (MANDATORY)

### TIER 1: Session Memory Cache (CHECK FIRST)

**Latency**: <10ms | **Location**: `.agent_session/`

```python
from codesentinel.utils.session_memory import SessionMemory

session = SessionMemory()

# ✅ DO THIS FIRST: Check cache before ANY file read
cached = session.get_file_context("path/to/file.py")
if cached:
    # Cache hit - use existing data
    content = cached['content']
    summary = cached['summary']
else:
    # Cache miss - read file and cache
    content = read_file("path/to/file.py")
    session.cache_file_context("path/to/file.py", {"analyzed": True}, content)
```

**When to use**:

- Before reading ANY file in multi-step operations
- Before re-analyzing code already seen this session
- Before re-computing data from earlier in workflow

**Expected performance**: 60-74% reduction in file I/O

---

### TIER 2a: Domain History Index (QUERY SECOND)

**Latency**: ~20ms | **Location**: `docs/domains/{domain}/INDEX.json`

```python
from codesentinel.utils.domain_consolidator import get_domain_guidance

# ✅ Query domain patterns before deep analysis
guidance = get_domain_guidance('process')  # or 'root', 'cli', etc.

# Use domain intelligence
if guidance['confidence'] > 0.7:
    success_rate = guidance['patterns']['success_rate']
    most_common_op = list(guidance['patterns']['action_frequency'].keys())[0]
    # Make informed decision based on historical patterns
```

**When to use**:

- Domain-specific operations (process, root, cli, policy)
- Need success rate baselines
- Need action frequency patterns
- Need performance benchmarks

**Available domains**: cli, core, utils, process, root, policy

---

### TIER 2b: Context Tier (QUERY THIRD)

**Latency**: <100ms | **Location**: `.agent_sessions/context_tier/`

```python
from codesentinel.utils.oracl_context_tier import get_weekly_summaries

# ✅ Check recent context for similar tasks
summaries = get_weekly_summaries(workspace_root)

# Filter for relevant context
recent_root_ops = [s for s in summaries if 'root' in s.get('task_summary', '')]
if recent_root_ops:
    # Learn from recent successful operations
    last_success = recent_root_ops[0]
    key_decisions = last_success['key_decisions']
    # Apply similar strategy
```

**When to use**:

- Multi-day workflows (resume context)
- Check recent similar tasks
- Verify recent decisions worked
- Avoid repeating recent mistakes

**Retention**: 7 days rolling window

---

### TIER 3: Intelligence Tier (QUERY FOR HIGH-IMPACT ONLY)

**Latency**: <500ms | **Location**: `archive/`

```python
from codesentinel.utils.archive_decision_provider import get_decision_context_provider

# ✅ Query ONLY for strategic, high-impact decisions
provider = get_decision_context_provider()
context = provider.get_decision_context(
    decision_type="policy_violation_handling",  # Strategic decision type
    current_state={"violation_type": "unauthorized_file_in_root"}
)

# Use if high confidence
if context and context.confidence_score > 0.7:
    recommended_action = context.recommended_actions[0]
    # Execute with confidence
else:
    # Fall back to domain guidance or defaults
    pass
```

**When to use** (HIGH-IMPACT ONLY):

- Policy violation handling
- Cleanup strategy selection
- Dependency update decisions
- Large-scale refactoring
- Recurring issue resolution

**DON'T use for**:

- Simple file operations
- Read-only queries
- Trivial decisions
- Operations <5 seconds

---

### TIER 4: Git Operations (LAST RESORT)

**Latency**: 500ms-5s | **Use ONLY when local data unavailable**

```python
# ❌ AVOID: Querying git for data available locally
# BAD:
run_in_terminal("git log --oneline -10")  # To check recent commits
# GOOD: Check domain history or context tier instead

# ✅ OK: Querying git when data truly unavailable locally
# GOOD:
run_in_terminal("git fetch origin")  # Need remote branch status
run_in_terminal("git remote -v")  # Need remote URLs
```

**When git IS appropriate**:

- Remote branch operations
- Fetching PR data
- Checking remote repository state
- Git-specific metadata (branch names, remotes, etc.)

**When git is NOT appropriate**:

- File change detection (use SessionMemory hash comparison)
- Recent activity logs (use domain history)
- Code analysis (use cached file context)
- Decision history (use Context Tier or Intelligence Tier)

---

## Complete Example: Agent Root Cleanup Decision

**CORRECT priority sequence:**

```python
from codesentinel.utils.session_memory import SessionMemory
from codesentinel.utils.domain_consolidator import get_domain_guidance
from codesentinel.utils.oracl_context_tier import get_weekly_summaries
from codesentinel.utils.archive_decision_provider import get_decision_context_provider

# ============================================
# STEP 1: Session Memory (Tier 1) - <10ms
# ============================================
session = SessionMemory()

# Check if we've already analyzed root_policy.py this session
cached_policy = session.get_file_context("codesentinel/utils/root_policy.py")
if cached_policy:
    policy = cached_policy['summary']  # CACHE HIT - saved 100ms file read
else:
    policy_content = read_file("codesentinel/utils/root_policy.py")
    policy = parse_policy(policy_content)
    session.cache_file_context("codesentinel/utils/root_policy.py", policy, policy_content)

# ============================================
# STEP 2: Domain History (Tier 2a) - ~20ms
# ============================================
domain_guidance = get_domain_guidance('root')

print(f"Domain confidence: {domain_guidance['confidence']:.0%}")
print(f"Success rate: {domain_guidance['patterns']['success_rate']:.0%}")

if domain_guidance['confidence'] > 0.7:
    # HIGH CONFIDENCE - domain has reliable patterns
    print(f"Guidance: {domain_guidance['guidance']}")
    # Use domain-informed strategy

# ============================================
# STEP 3: Context Tier (Tier 2b) - <100ms
# ============================================
recent_summaries = get_weekly_summaries(workspace_root)

# Find recent root cleanup operations
recent_cleanups = [
    s for s in recent_summaries 
    if 'root_cleanup' in s.get('task_summary', '').lower()
]

if recent_cleanups:
    last_cleanup = recent_cleanups[0]
    print(f"Last cleanup: {last_cleanup['timestamp']}")
    print(f"Outcome: {last_cleanup['outcome']}")
    # Learn from recent success/failure

# ============================================
# STEP 4: Intelligence Tier (Tier 3) - <500ms
# ============================================
# ONLY query for high-impact policy decision
provider = get_decision_context_provider()
context = provider.get_decision_context(
    decision_type="policy_violation_handling",
    current_state={"violation_type": "unauthorized_directory"}
)

if context and context.confidence_score > 0.7:
    # HIGH CONFIDENCE from historical patterns
    action = context.recommended_actions[0]
    print(f"ORACL recommends: {action} (confidence: {context.confidence_score:.0%})")
else:
    # FALLBACK to domain guidance
    action = "archive_with_confirmation"

# ============================================
# STEP 5: Execute Decision (NO GIT NEEDED)
# ============================================
session.log_decision(
    decision=f"Archive unauthorized directory using {action}",
    rationale=f"ORACL: {context.confidence_score:.0%}, Domain: {domain_guidance['patterns']['success_rate']:.0%} success"
)

# Execute cleanup
execute_action(action)

# Report outcome for future learning
provider.report_decision_outcome(
    decision_type="policy_violation_handling",
    action=action,
    outcome="success",
    reason="Directory archived successfully"
)

# ============================================
# TOTAL QUERY TIME: ~630ms
# - Session cache: <10ms
# - Domain guidance: ~20ms
# - Context tier: ~100ms
# - Intelligence tier: ~500ms
# NO GIT OPERATIONS NEEDED
# ============================================
```

---

## Anti-Patterns: What NOT to Do

### ❌ WRONG: Skipping Session Cache

```python
# BAD: Reading same file multiple times without caching
for iteration in range(10):
    config = read_file("config.json")  # Re-reads every time!
    process(config)

# WASTED: 10 file reads × 100ms = 1000ms
```

### ✅ RIGHT: Using Session Cache

```python
# GOOD: Cache once, reuse
session = SessionMemory()
cached = session.get_file_context("config.json")
if cached:
    config = cached['content']
else:
    config = read_file("config.json")
    session.cache_file_context("config.json", {"parsed": True}, config)

for iteration in range(10):
    process(config)  # Uses cached data

# SAVED: 9 file reads × 100ms = 900ms saved
```

---

### ❌ WRONG: Using Git for File Change Detection

```python
# BAD: Shelling out to git to check if file changed
result = run_in_terminal("git diff --name-only HEAD")
if "config.py" in result:
    config = read_file("config.py")

# OVERHEAD: 500-1000ms git operation
```

### ✅ RIGHT: Using Session Memory Hash Comparison

```python
# GOOD: Use file hash for change detection
session = SessionMemory()
cached = session.get_file_context("config.py")

if cached:
    current_hash = session._get_file_hash(Path("config.py"))
    if current_hash == cached['hash']:
        config = cached['content']  # File unchanged, use cache
    else:
        config = read_file("config.py")  # File changed, re-read
        session.cache_file_context("config.py", {"parsed": True}, config)

# SAVED: <10ms hash check vs 500ms git operation
```

---

### ❌ WRONG: Querying Intelligence Tier for Simple Operations

```python
# BAD: Using ORACL for trivial file read
from codesentinel.utils.archive_decision_provider import get_decision_context_provider

provider = get_decision_context_provider()
context = provider.get_decision_context(
    decision_type="file_read_strategy",  # TOO TRIVIAL
    current_state={"file": "config.py"}
)

# OVERHEAD: 500ms for <1ms decision
```

### ✅ RIGHT: Using Session Cache for Simple Operations

```python
# GOOD: Session cache for simple operations
session = SessionMemory()
cached = session.get_file_context("config.py")
if cached:
    use_cached_data(cached['content'])

# SAVED: <10ms vs 500ms
```

---

## Performance Monitoring

**Always measure cache effectiveness:**

```python
# After multi-step operation
stats = session.get_cache_stats()

print(f"Cache Performance:")
print(f"  Hit rate: {stats['hit_rate']:.1%}")
print(f"  Files cached: {stats['cached_files']}")
print(f"  Decisions logged: {stats['logged_decisions']}")

# TARGET: >60% cache hit rate
# If lower, check:
# - Are you calling get_file_context() before reads?
# - Are files changing frequently?
# - Is cache being cleared unnecessarily?
```

---

## Decision Tree: Which Tier to Query?

```
START: Need information for decision
│
├─ Q: Is this from a file I might have read this session?
│  └─ YES → CHECK SESSION CACHE (Tier 1) <10ms
│     ├─ Cache hit? → USE CACHED DATA (done)
│     └─ Cache miss? → Read file, cache it, continue
│
├─ Q: Is this domain-specific info (success rates, patterns)?
│  └─ YES → QUERY DOMAIN GUIDANCE (Tier 2a) ~20ms
│     ├─ Confidence >0.7? → USE DOMAIN STRATEGY (done)
│     └─ Confidence <0.7? → Continue to next tier
│
├─ Q: Did I do something similar in last 7 days?
│  └─ YES → QUERY CONTEXT TIER (Tier 2b) <100ms
│     ├─ Found similar? → APPLY RECENT STRATEGY (done)
│     └─ Not found? → Continue to next tier
│
├─ Q: Is this a high-impact strategic decision?
│  └─ YES → QUERY INTELLIGENCE TIER (Tier 3) <500ms
│     ├─ Confidence >0.7? → USE ORACL RECOMMENDATION (done)
│     └─ Confidence <0.7? → Use default strategy
│
└─ Q: Is this data ONLY available via git?
   └─ YES → QUERY GIT (Tier 4) 500ms-5s
      └─ Otherwise: USE DEFAULT STRATEGY (done)
```

---

## Summary: Priority Rules

1. **ALWAYS** check Session Memory cache before file reads
2. **PREFER** Domain History for domain-specific intelligence
3. **USE** Context Tier for recent similar operations
4. **RESERVE** Intelligence Tier for high-impact decisions
5. **AVOID** Git operations when data available locally
6. **MEASURE** cache hit rates to optimize performance
7. **LOG** all decisions to build future intelligence

**Goal**: <100ms query latency for 95% of operations

**Current Performance**:

- Session cache: <10ms (99% of operations)
- Domain guidance: ~20ms (domain-specific ops)
- Context queries: <100ms (multi-day workflows)
- Intelligence queries: <500ms (strategic decisions only)

**The system is optimized for speed - use it.**
