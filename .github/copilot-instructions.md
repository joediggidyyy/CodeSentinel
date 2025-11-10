# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with SEAM Protection™:
**Security, Efficiency, And Minimalism** (with Security taking absolute priority).

## Architecture Overview

The codebase follows a dual-architecture pattern:

- **`codesentinel/`** - Core Python package with CLI interface (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies
- **`tests/`** - Test suite using pytest with unittest fallback

## Key Commands

### Development Audit
```bash
# Run interactive audit
codesentinel !!!!

# Get agent-friendly context for remediation
codesentinel !!!! --agent
```

### Maintenance Operations
```bash
# Daily maintenance workflow
python tools/codesentinel/scheduler.py --schedule daily

# Weekly maintenance (security, dependencies, performance)
python tools/codesentinel/scheduler.py --schedule weekly
```

## Core Principles

### SECURITY
- No hardcoded credentials - Environment variables or config files only
- Audit logging - All operations logged with timestamps
- Configuration validation - Auto-creation of missing configs with secure defaults
- Dependency scanning - Automated vulnerability detection

### EFFICIENCY
- Avoid redundant code and duplicate implementations
- Consolidate multiple versions of similar functionality
- Clean up orphaned test files and unused scripts
- Optimize import structures and module organization

### MINIMALISM
- Remove unnecessary dependencies
- Archive deprecated code to quarantine_legacy_archive/
- Maintain single source of truth for each feature
- Keep codebase focused and maintainable

### QUARANTINE_LEGACY_ARCHIVE POLICY
- **Mandatory Reference Directory**: `quarantine_legacy_archive/` is essential for agent remediation and code archaeology
- **Purpose**: Preserve archived code, configurations, and artifacts for reference, analysis, and potential recovery
- **Compression Policy**: Compress to `.tar.gz` after 30 days of inactivity, but retain in repository
- **Security Scanning**: ALWAYS thoroughly check archive for:
  - Malicious file insertion or tampering
  - Credential leakage in archived code
  - Dependencies with known vulnerabilities
  - Integrity of archived content
- **Exclusion from Most Checks**: Archive directory is excluded from:
  - Minimalism violation reports (not considered "clutter")
  - Routine cleanup operations
  - Code style enforcement
  - Import optimization scans
- **Integrity Verification Required**: When archive is accessed or modified:
  - Verify file hashes match original
  - Scan for new/modified files
  - Check for external tampering
  - Log all access and modifications

## Persistent Policies

When working with this codebase:

1. **NON-DESTRUCTIVE**: Never delete code without archiving first
2. **FEATURE PRESERVATION**: All existing functionality must be maintained
3. **STYLE PRESERVATION**: Respect existing code style and patterns
4. **SECURITY FIRST**: Security concerns always take priority
5. **PERMANENT POLICY (T0-5)**: Framework compliance review required with every package release
   - Every pre-release and production release must include comprehensive framework compliance review
   - Review must verify SEAM Protected™: Security, Efficiency, And Minimalism alignment
   - Review must validate all persistent policies (non-destructive, feature preservation, security-first)
   - Compliance review is a release-blocking requirement, cannot be deferred
   - Classified as Constitutional (Irreversible) tier in governance system
   - Review must assess technical debt impact and long-term sustainability
   - Report must be part of release package and documentation
   - Failure to include compliance review blocks release approval

## Agent-Driven Remediation

When `codesentinel !!!! --agent` is run, you will receive comprehensive audit context with:

- Detected issues (security, efficiency, minimalism)
- Remediation hints with priority levels
- Safe-to-automate vs. requires-review flags
- Step-by-step suggested actions

### Root Directory Assessment Methodology

**CRITICAL**: When encountering conflicts between different validation systems (e.g., `clean --root` vs `root_cleanup.py` validation), follow this assessment flow **BEFORE** making any changes:

1. **MANUAL STATE ASSESSMENT**
   - List all files/directories at root: `ls -la` or equivalent
   - For each item, determine its purpose and status (authorized vs unauthorized)
   - Compare against `tools/codesentinel/root_cleanup.py`: ALLOWED_ROOT_FILES and ALLOWED_ROOT_DIRS constants
   - Document the actual vs expected state

2. **DISTINGUISH OPERATION SCOPES**
   - `codesentinel clean --root`: Removes clutter patterns only (`__pycache__`, `*.pyc`, `*.pyo`, `*.tmp`)
   - `root_cleanup.py` validation: Enforces policy compliance (checks all items against allowed lists)
   - **These are DIFFERENT operations with DIFFERENT purposes** - both can be "correct" simultaneously

3. **IDENTIFY CONTRADICTIONS**
   - If operations report different results, note what each operation's SCOPE actually covers
   - Example: clean found "0 items" ✓ (no Python clutter) while validation found "3 issues" ✓ (policy violations)
   - This is NOT contradictory - they're checking different things

4. **DETERMINE ACTION REQUIRED**
   - Is the issue about accumulated clutter? → Use clean operations
   - Is the issue about policy non-compliance? → Use validation/remediation operations
   - Is there an unauthorized file? → **ALWAYS** determine WHY it exists before deletion
   - Is there a test/debug file from development? → Archive to quarantine_legacy_archive/ rather than delete

5. **DOCUMENT FINDINGS BEFORE ACTING**
   - Write down what was found, why each item is present, what operation should address it
   - Distinguish between:
     - Development artifacts (test_integrity.py) → archive during cleanup phase
     - Unauthorized system directories (.codesentinel/) → remove per policy
     - Legitimate but misplaced files → move to correct location or archive

Your role is to:

1. **ANALYZE**: Review each issue with full context
2. **PRIORITIZE**: Focus on critical/high priority items first  
3. **DECIDE**: Determine safe vs. requires-review actions
4. **PLAN**: Build step-by-step remediation plan
5. **EXECUTE**: Only perform safe, non-destructive operations
6. **REPORT**: Document all actions and decisions

## Safe Actions (can automate)

- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

## Requires Review (agent decision needed)

- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

## Forbidden Actions

- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality without explicit approval
- Excessive use of emojis in documentation or code comments

## CRITICAL: Policy Violation Prevention Guardrails

**THESE ARE NON-NEGOTIABLE - Any implementation violating these is INCORRECT:**

### 1. NON-DESTRUCTIVE OPERATIONS - Policy Priority #1

**RULE: Never implement direct file/directory deletion without first implementing archival**

- ❌ WRONG: `path.unlink()` or `shutil.rmtree()` as default behavior
- ✅ RIGHT: `shutil.move(item, archive_path)` to `quarantine_legacy_archive/`

When implementing cleanup/remediation features:
1. **ALWAYS archive first** - Move to quarantine_legacy_archive/
2. **Ask user permission** - Even with --force, document what will be archived
3. **Provide recovery option** - Items must be accessible in archive
4. **LOG all operations** - Track what was moved and why

**Example Pattern:**
```python
# CORRECT: Archive-first pattern
archive_dir = Path("quarantine_legacy_archive")
archive_dir.mkdir(exist_ok=True)
target = archive_dir / item.name
shutil.move(str(item), str(target))

# WRONG: Direct deletion pattern (DO NOT USE)
item.unlink()  # ❌ FORBIDDEN
shutil.rmtree(item)  # ❌ FORBIDDEN
```

### 2. POLICY ALIGNMENT CHECK

Before implementing ANY file operation feature:

1. **Read the Persistent Policies section** above
2. **Ask yourself:**
   - Does this violate NON-DESTRUCTIVE? 
   - Does this remove functionality?
   - Does this compromise security?
3. **If ANY answer is yes: REDESIGN**

Recent violation example:
- Task: Add --full flag to clean --root
- Initial implementation: Deleted unauthorized files directly
- Violation: Broke NON-DESTRUCTIVE policy - Policy #1
- Fix: Changed to archive all violations instead

### 3. FILE OPERATION SAFEGUARDS

For any feature adding file operations:

```python
# TEMPLATE: Safe file operation pattern

# ✅ DO THIS:
def safe_file_operation(items_to_process):
    archive_path = workspace_root / "quarantine_legacy_archive"
    archive_path.mkdir(exist_ok=True)
    
    for item in items_to_process:
        # Step 1: Assessment
        reason = assess_file_necessity(item)
        target = determine_target_location(item)
        
        # Step 2: User confirmation (non-dry-run)
        if not dry_run and not force:
            response = input(f"Archive {item.name} ({reason})? (y/N): ")
            if response != 'y':
                continue
        
        # Step 3: Archive (never delete)
        try:
            shutil.move(str(item), str(archive_path / item.name))
            log(f"Archived: {item}")
        except Exception as e:
            log_error(f"Failed to archive: {e}")

# ❌ DON'T DO THIS:
def unsafe_file_operation(items_to_delete):
    for item in items_to_delete:
        item.unlink()  # DIRECT DELETION - VIOLATES POLICY!
        # No assessment, no archival, no recovery option
```

### 4. VALIDATION BEFORE IMPLEMENTATION

When implementing new --flag or feature:

1. **Trace all code paths** - What happens in each condition?
2. **Find delete operations** - Search for `.unlink()`, `rmtree()`, `remove()`
3. **Ask: Is there an archive alternative?** - If yes, use it
4. **Check for user confirmation** - Is there a prompt before destructive action?
5. **Test with dry-run** - Does --dry-run show what WOULD happen without doing it?

### 5. CODE REVIEW CHECKLIST

Before committing file operation features:

- [ ] No direct `.unlink()` or `rmtree()` calls (unless approved for specific cases)
- [ ] Default behavior is archival, not deletion
- [ ] User sees what will happen before it happens (--dry-run support)
- [ ] User can approve/reject before action (confirmation prompt)
- [ ] All operations are logged
- [ ] Archived items are in quarantine_legacy_archive/ or similar approved archive
- [ ] Recovery is possible (items not permanently deleted)
- [ ] Policy compliance is documented in code comments

## Integration Points

### GitHub Integration
- Repository-aware configuration detection
- Copilot instructions generation (this file)
- PR review automation capabilities

### Multi-Platform Support  
- Python 3.13/3.14 requirement with backward compatibility
- Cross-platform paths using `pathlib.Path` consistently
- PowerShell/Python dual execution support for Windows/Unix

## When Modifying This Codebase

1. **Understand the dual architecture** - Core package vs. tools scripts serve different purposes
2. **Maintain execution order** - Change detection dependency is critical
3. **Preserve configuration structure** - JSON configs have specific schemas
4. **Test both execution paths** - pytest and unittest must both work
5. **Follow security-first principle** - Never compromise security for convenience
6. **Update timeout values carefully** - Task timeouts affect workflow reliability
