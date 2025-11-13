# Understanding SessionMemory vs Domain History

## TL;DR

**SessionMemory `show`/`stats` showing empty is CORRECT behavior.**

Your CLI commands ARE working - they're logging to **Domain History** (DHIS), which is separate from SessionMemory cache.

---

## Two Different Systems

### 1. SessionMemory Cache (What `codesentinel memory show/stats` displays)

**Purpose:** Speed up multi-step agent operations by caching file reads and decisions

**Contents:**

- File context cache (parsed code, summaries)
- Decision logs (analysis rationale)
- Task tracking (multi-step todos)

**When it's populated:**

- During long-running agent sessions
- When agent reads same file multiple times
- When agent makes decisions with rationale
- When agent tracks multi-step tasks

**Example workflow that WOULD populate it:**

```bash
# Agent reads config.py 5 times during analysis
# SessionMemory caches it after first read
# Subsequent reads are instant (cache hit)

codesentinel dev-audit !!!!
# During this command:
# - Agent reads files (cached)
# - Agent logs decisions (stored)
# - Agent tracks tasks (persisted)
```

**Why it's empty now:**

```bash
codesentinel memory process status
# This command:
# 1. Runs quickly (< 1 second)
# 2. Doesn't read/re-read files
# 3. Doesn't make analysis decisions
# 4. Doesn't track multi-step tasks
# → SessionMemory stays empty (CORRECT)
```

---

### 2. Domain History (DHIS) - What Actually Tracks CLI Commands

**Purpose:** Track ALL domain activity for pattern analysis and ORACL learning

**Contents:**

- Every CLI command execution
- Success/failure status
- Duration metrics
- Metadata (PIDs, counts, etc.)

**Where it's stored:**

```
docs/domains/process/history.jsonl  ← YOUR DATA IS HERE
```

**Verification:**

```bash
# Check domain history
type docs\domains\process\history.jsonl

# Output shows 3 operations logged:
# - lifecycle_status_check
# - lifecycle_history_query
# - discovery_instances_query
```

**Generate intelligence report:**

```bash
python codesentinel\utils\domain_consolidator.py --verbose

# Output:
# Domain: PROCESS
# Total Operations: 3
# Success Rate: 100.0%
# Avg Duration: 321.00ms
# Confidence: 56%
```

---

## When Would SessionMemory Show Data?

**Scenario 1: Multi-file agent analysis**

```bash
codesentinel dev-audit !!!!
# Agent performs comprehensive audit:
# - Reads 50+ files
# - Makes 20+ decisions
# - Tracks 10+ remediation tasks
# → SessionMemory FULL of cache data
```

**Scenario 2: Interactive session**

```python
from codesentinel.utils.session_memory import SessionMemory

session = SessionMemory()

# Log a task
session.log_task(1, "Analyze codebase", "in-progress")

# Cache a file
session.cache_file_context("config.py", {"imports": 5}, "content...")

# Log decision
session.log_decision("Archive duplicate", "Matches pattern from previous cleanup")

# NOW: codesentinel memory show
# → Shows 1 task, 1 cached file, 1 decision
```

**Scenario 3: Long-running maintenance**

```bash
codesentinel clean --root --full --dry-run
# During dry-run:
# - Agent analyzes each root item
# - Caches policy decisions
# - Tracks remediation tasks
# → SessionMemory populated during execution
```

---

## Current Status (Your System)

### ✅ WORKING CORRECTLY

1. **Domain History (DHIS)**
   - ✓ 3 operations logged to `docs/domains/process/history.jsonl`
   - ✓ Data includes timestamps, success status, durations
   - ✓ Consolidation generates INDEX.json with patterns

2. **SessionMemory Cache**
   - ✓ Initialized and ready
   - ✓ Empty because no multi-step operations yet (EXPECTED)
   - ✓ Would populate during complex agent workflows

3. **CLI Integration**
   - ✓ Commands are logging to domain history
   - ✓ Handlers are connected properly
   - ✓ `memory show`/`stats` work (showing correct empty state)

---

## Testing SessionMemory Population

**Quick test to see SessionMemory in action:**

```python
# Create test script: test_session_memory.py
from codesentinel.utils.session_memory import SessionMemory
from pathlib import Path

# Initialize session
session = SessionMemory()

# Simulate agent workflow
print("Simulating agent workflow...")

# Step 1: Track a task
session.log_task(
    task_id=1,
    title="Analyze configuration files",
    status="in-progress"
)

# Step 2: Cache file context
session.cache_file_context(
    file_path="config.py",
    analysis={"imports": 10, "functions": 5},
    full_content="# config file content..."
)

# Step 3: Log a decision
session.log_decision(
    decision="Move deprecated config to archive",
    rationale="Config format changed in v2.0, old format no longer needed"
)

# Step 4: Mark task complete
session.log_task(
    task_id=1,
    title="Analyze configuration files",
    status="completed"
)

# Persist to disk
session.persist()

print("\nSessionMemory populated!")
print("\nNow run: codesentinel memory show")
```

**Run the test:**

```bash
python test_session_memory.py
codesentinel memory show
# NOW it will show data!
```

---

## Conclusion

**Your system is working perfectly.** The difference is:

| System | Purpose | When Populated | Current State |
|--------|---------|----------------|---------------|
| **SessionMemory** | Agent efficiency cache | Multi-step workflows | Empty (no workflows yet) ✓ |
| **Domain History** | Operation tracking | Every CLI command | Has 3 entries ✓ |

**What you're seeing is correct:**

- `memory show/stats`: Empty (expected - no agent workflows)
- Domain history: Populated (expected - CLI commands logged)

**To see SessionMemory populate:**

- Run `codesentinel dev-audit !!!!` (comprehensive analysis)
- Run the test script above
- Do any multi-step operation that reads files repeatedly

**The handlers ARE connected properly.** Domain logging is working, SessionMemory is ready for when it's needed.
