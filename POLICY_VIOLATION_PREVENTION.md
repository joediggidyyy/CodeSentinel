# Policy Violation Prevention# Policy Violation Prevention - Implementation Guide

**Date:** November 10, 2025  **Date:** November 10, 2025  

**Status:** Guardrails Implemented**Status:** Guardrails Implemented

------

## What Happened## What Happened

An initial implementation of `codesentinel clean --root --full` violated CodeSentinel's NON-DESTRUCTIVE policy by allowing direct file/directory deletion without archival. This was corrected and prevented from recurring.An initial implementation of the `codesentinel clean --root --full` command violated CodeSentinel's core NON-DESTRUCTIVE policy by:

---1. Allowing direct file/directory deletion without archival

2. Not assessing files for proper placement before removal

## How It Was Fixed3. Making deletion the default behavior instead of archival

Changed from deletion to archival:**Example of violation:**

```python```python

# WRONG - Initial implementation# ❌ WRONG - This was the initial implementation

if violation['action'] == 'delete':if violation['action'] == 'delete':

    items_to_delete.append(...)    items_to_delete.append(...)  # Direct deletion without archival

```

# CORRECT - Fixed implementation

archive_dir = workspace_root / 'quarantine_legacy_archive'---

shutil.move(str(item['path']), str(target_path))

```## How It Was Fixed



---The implementation was corrected to follow the NON-DESTRUCTIVE policy:



## Prevention Guardrails1. **Archive First** - All unauthorized files are moved to `quarantine_legacy_archive/`

2. **Assess Each Item** - Files are categorized (test files, docs, configs) before action

Updated `.github/copilot-instructions.md` with **5 enforcement layers:**3. **User Approval** - Requires confirmation before archiving (unless --force used)

4. **Preserve Recovery** - Archived items remain accessible

#### Layer 1: NON-DESTRUCTIVE OPERATIONS

**Example of corrected implementation:**

- RULE: Never delete without archiving first

- Code pattern templates showing correct vs. forbidden approaches```python

# ✅ CORRECT - Archive-first pattern

#### Layer 2: POLICY ALIGNMENT CHECKarchive_dir = workspace_root / 'quarantine_legacy_archive'

archive_dir.mkdir(parents=True, exist_ok=True)

- Required questions before implementation:

  - Does this violate NON-DESTRUCTIVE?for item in policy_violations:

  - Does this remove functionality?    target_path = archive_dir / item['name']

  - Does this compromise security?    shutil.move(str(item['path']), str(target_path))

    # Items preserved, recoverable

#### Layer 3: FILE OPERATION SAFEGUARDS```



- Template provided for safe file operations---

- Steps: Assessment → User Confirmation → Archive (never delete)

## Prevention Guardrails (Now Enforced)

#### Layer 4: VALIDATION BEFORE IMPLEMENTATION

Updated `.github/copilot-instructions.md` with **5-layer policy enforcement**:

- Pre-implementation checklist:

  - Trace all code paths### Layer 1: NON-DESTRUCTIVE OPERATIONS (Policy Priority #1)

  - Find delete operations

  - Check for archive alternatives- **RULE:** Never delete without archiving first

  - Verify user confirmation prompts- **Enforcement:** Code pattern templates showing ✅ CORRECT and ❌ FORBIDDEN approaches

  - Test with --dry-run- **Example Forbidden:** `item.unlink()`, `shutil.rmtree()` as default



#### Layer 5: CODE REVIEW CHECKLIST### Layer 2: POLICY ALIGNMENT CHECK



- Pre-commit requirements:- **Required Questions Before Implementation:**

  - No direct `.unlink()` or `rmtree()` calls  - Does this violate NON-DESTRUCTIVE?

  - Default behavior is archival  - Does this remove functionality?

  - User sees what happens first  - Does this compromise security?

  - Items remain recoverable- **Decision:** If ANY answer is YES → REDESIGN

  - Policy compliance documented

### Layer 3: FILE OPERATION SAFEGUARDS

---

- **Template Provided:** Safe file operation pattern with 3 steps

## Key Lessons  1. Assessment of necessity and target location

  2. User confirmation (except with --force)

1. **Policy First** - Check Persistent Policies before implementation  3. Archive operation (never delete)

2. **Archive Pattern** - Make archival DEFAULT, deletion exception

3. **User Control** - Always ask for confirmation on destructive operations### Layer 4: VALIDATION BEFORE IMPLEMENTATION

4. **Documentation** - Guardrails in instructions prevent violations

5. **Code Review** - Checklists catch issues before commit- **Pre-Implementation Checklist:**

  1. Trace all code paths

---  2. Find delete operations (grep for `.unlink()`, `rmtree()`, `remove()`)

  3. Ask: "Is there an archive alternative?"

## Result  4. Check for user confirmation prompts

  5. Test with --dry-run

✅ Violation identified and corrected  

✅ Root cause fixed (direct deletion → archival)  ### Layer 5: CODE REVIEW CHECKLIST

✅ 5-layer prevention guardrails implemented  

✅ Documentation updated with explicit examples  - **Pre-Commit Requirements:**

✅ Code review checklist provided    - [ ] No direct `.unlink()` or `rmtree()` calls

  - [ ] Default behavior is archival, not deletion

The codebase is now protected from this class of violation.  - [ ] User sees what happens before it happens

  - [ ] User can approve/reject before action
  - [ ] All operations logged
  - [ ] Items recoverable in archive
  - [ ] Policy compliance documented

---

## Practical Impact

### Before (Violation)

```bash
$ codesentinel clean --root --full
# Would directly delete 4 items without warning
# No recovery option
# Violates NON-DESTRUCTIVE policy
```

### After (Policy-Compliant)

```bash
$ codesentinel clean --root --full --dry-run
🔍 Scanning root directory for clutter...
🔍 Scanning for policy violations (--full mode)...

⚠️  Found 4 policy violations:
All items will be ARCHIVED (not deleted) per NON-DESTRUCTIVE policy

  1. [DIRECTORY] .codesentinel
     Reason: unauthorized dot directory
     Action: Archive to quarantine_legacy_archive/
  [... etc ...]

[DRY-RUN] Would archive the items above

$ codesentinel clean --root --full
Archive these items to quarantine_legacy_archive/? (y/N): y
✓ Successfully archived 4/4 items
  Items are preserved in quarantine_legacy_archive/ for review
```

---

## Key Lessons

1. **Policy First** - Always check Persistent Policies before implementation
2. **Archive Pattern** - Make archival the DEFAULT, deletion the exception (with explicit review)
3. **User Control** - Always ask for confirmation on potentially destructive operations
4. **Documentation** - Explicit guardrails in agent instructions prevent future violations
5. **Code Review** - Checklists catch violations before commit

---

## How This Prevents Recurrence

| Prevention Layer | Mechanism | When Triggered |
|---|---|---|
| **Documentation** | Explicit guardrails in copilot-instructions.md | Before any file operation feature |
| **Code Pattern** | Template showing ✅/❌ examples | During implementation |
| **Validation** | Pre-implementation checklist | Before writing code |
| **Review** | Pre-commit checklist | Before committing changes |
| **Runtime** | Archive-first default behavior | During command execution |

---

## For Future Implementations

When adding ANY feature that modifies files:

1. **READ:** `.github/copilot-instructions.md` - CRITICAL section
2. **ASK:** Does this use `.unlink()` or `rmtree()`?
3. **ANSWER:** If yes, replace with archival pattern
4. **VERIFY:** Check all 5 layers of guardrails
5. **TEST:** Run with --dry-run first, then --force

**Golden Rule:** When in doubt, archive instead of delete.

---

## Conclusion

✅ Policy violation identified and corrected  
✅ Root cause fixed (direct deletion → archival)  
✅ Prevention guardrails implemented (5-layer enforcement)  
✅ Documentation updated with explicit examples  
✅ Code review checklist provided for future PRs  

The codebase is now protected from this class of violation.
