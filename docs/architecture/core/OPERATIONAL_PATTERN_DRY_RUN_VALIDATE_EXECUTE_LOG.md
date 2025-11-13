# OPERATIONAL PATTERN: DRY-RUN → VALIDATE → EXECUTE → LOG

## Critical Principle: ALL DATA HAS VALUE POTENTIAL

This document codifies the correct operational pattern for all CodeSentinel maintenance and remediation operations.

---

## The Pattern

### 1. DRY-RUN

- **Purpose:** Predict outcomes without modifying system
- **Output:** Complete report of proposed changes
- **Data:** All predictions captured (cleanup_preview.json)
- **User Action:** Review recommendations

### 2. VALIDATE

- **Purpose:** User approval of proposed changes
- **Process:** User confirms dry-run output is correct
- **Data:** User decisions recorded (decisions logged)
- **Go/No-Go:** Proceed or modify config and re-run

### 3. EXECUTE

- **Purpose:** Implement approved changes
- **Process:** Apply operations one by one, verify each
- **Data:** Every operation logged (operations_log.jsonl)
- **Key:** ALL data preserved, nothing destroyed, all archived
- **Archival:** Deleted files move to `quarantine_legacy_archive/` not removed
- **Verification:** Checksums, file counts, timestamps recorded

### 4. LOG (Implied)

- **Purpose:** Create complete audit trail
- **Captured:** All dry-run, validate, execute data
- **Storage:**
  - JSONL for append-only operations
  - JSON for summaries and metrics
  - Domain histories auto-populated
- **Value:** Feeds DHIS, ORACL, intelligence system

---

## Why ALL Data Matters

```
Every operation generates intelligent input:

DRY-RUN data
  └─ Shows what COULD happen (predictor accuracy)

VALIDATE data
  └─ Shows what user APPROVES (decision patterns)

EXECUTE data
  └─ Shows what ACTUALLY happens (reliability metrics)

LOG data
  └─ Complete record (audit trail + learning)

Together: Enables automation decisions based on data
```

---

## Why This Matters for Root Cleanup

The pre-commit hook failure you encountered demonstrates the pattern:

1. **Git commit triggered**
2. **DRY-RUN:** `.git/hooks/pre-commit` auto-ran with dry_run=True
   - Predicted: 11 violations (2 unauthorized, 1 misplaced, 8 unknown)
   - Data: Captured in validation report
3. **VALIDATE:** System validated and decided this requires user review
   - Found: Tier 3 (unknown files) requiring human judgment
   - Data: Issue categories recorded
4. **EXECUTE:** User must manually handle Tier 3 before proceeding
   - When user approves decisions: operations logged
   - All decisions and outcomes recorded
5. **LOG:** Complete audit trail maintained
   - What was proposed, what was approved, what was done
   - All data feeds downstream intelligence

---

## Current Implementation Status

✓ DRY-RUN exists (already works)
✓ VALIDATE exists (pre-commit hook validates)
✓ EXECUTE exists (manual via CLI)
✓ LOG exists (partially - operations_log.jsonl captured)

**Enhancement Opportunity:** Tier 1-2 auto-fix during pre-commit

- Tier 1 (unauthorized dirs): Safe to auto-delete to quarantine
- Tier 2 (misplaced files): Safe to auto-move if target known
- Tier 3 (unknown files): Still require user review

---

## Design Principle: Non-Destructive Operations

**Critical:** Nothing is ever truly deleted. All operations follow this pattern:

```
Delete Operation
├─ Appears to: Remove file from filesystem
└─ Actually:
   ├─ Move to quarantine_legacy_archive/{original_path}
   ├─ Record metadata (original location, reason, timestamp)
   ├─ Log in audit trail
   └─ File remains recoverable indefinitely

Move Operation
├─ Move file to intended location
├─ Update all references
├─ Log source → destination mapping
└─ All original data preserved

Result: 100% data preservation, complete audit trail
```

---

## Why You Saw Manual Instructions in the Error Message

When your git commit failed, the pre-commit hook printed:

```
To fix these issues:
1. Run: python tools/codesentinel/root_cleanup.py --dry-run
2. Review the proposed changes
3. Run: python tools/codesentinel/root_cleanup.py
4. Stage the changes: git add
5. Commit again: git commit
```

This is correct because:

1. **DRY-RUN** (step 1): Already happened in pre-commit hook
   - But user should see it explicitly to understand changes

2. **VALIDATE** (step 2): User reviews dry-run output
   - Ensures user approves before real changes

3. **EXECUTE** (step 3): User runs cleanup to apply changes
   - This is where operations actually happen
   - All logged to operations_log.jsonl

4. **LOG** (implied): Audit trail created automatically
   - All data captured for downstream use

5. **RETRY** (step 5): Commit succeeds with data preserved
   - Or new unknown files created during cleanup, retry VALIDATE

---

## Next Steps: Smart Pre-Commit Enhancement

**Phase 1:** Auto-fix Tier 1-2 in pre-commit hook

- Unauthorized dirs: auto-delete to quarantine
- Misplaced files: auto-move if target known
- Unknown files: still require user review

**Phase 2:** Maintain complete data pipeline

- All operations logged automatically
- Feeds domain histories
- DHIS consolidation reads and analyzes
- ORACL tiers build confidence scores

**Phase 3:** Enable agent automation

- Agent queries ORACL confidence
- "Is it safe to auto-fix Tier 1-2?" → Yes (99%+ confidence)
- Agent enables automated cleanup
- All decisions logged and tracked

---

## Summary: The Philosophy

**Zero-Loss Operations:** Nothing discarded, everything archived
**Complete Logging:** Every stage recorded for audit + intelligence  
**Data-Driven Decisions:** Use historical data to improve automation
**Feedback Loop:** More data → better confidence → safer automation → more data

This is how CodeSentinel learns and improves over time.
