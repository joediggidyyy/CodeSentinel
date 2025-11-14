# CodeSentinel Packaging Pipeline Directive

**Version**: 1.0  
**Date**: 2025-11-13  
**Status**: ACTIVE  
**Classification**: Operational (Core Release Process)

---

## Executive Summary

This directive defines the complete CodeSentinel packaging pipeline from pre-package validation through post-push verification. It establishes mandatory safety checks, verification points, and rollback procedures for all release operations.

**Pipeline Phases**: 6 sequential stages with 18 distinct validation checkpoints.

---

## Pipeline Architecture

```
PHASE 1: PRE-PACKAGE VALIDATION
    ↓
PHASE 2: BUILD EXECUTION
    ↓
PHASE 3: ARTIFACT VERIFICATION
    ↓
PHASE 4: ROOT DIRECTORY VALIDATION
    ↓
PHASE 5: GIT OPERATIONS (Commit → Tag → Push)
    ↓
PHASE 6: POST-PUSH VERIFICATION
```

---

## Phase 1: PRE-PACKAGE VALIDATION

**Objective**: Ensure codebase is clean, tested, and ready for packaging.

### 1.1 Version Synchronization Check

**Command**:

```bash
# Verify all version files match
grep -r "VERSION_STRING" pyproject.toml setup.py codesentinel/__init__.py
```

**Files to Verify**:

- `pyproject.toml` (line 11): `version = "X.X.X"`
- `setup.py` (line 30): `version="X.X.X"`
- `codesentinel/__init__.py` (line 26): `__version__ = "X.X.X"`

**Validation**: All three files must have identical version strings.

**Failure Action**: ABORT - Correct version mismatch before proceeding.

### 1.2 CHANGELOG Documentation

**Files to Verify**:

- `CHANGELOG.md`: Header section must contain `## [vX.X.X] - YYYY-MM-DD`

**Validation**:

- Version in header matches target version
- Date stamp is current
- Organized sections exist: Added, Changed, Fixed, Deprecated, Removed, Security
- Minimum 5 items documented

**Failure Action**: ABORT - Update CHANGELOG before proceeding.

### 1.3 Test Suite Execution

**Command**:

```bash
python -m pytest tests/ -v --ignore=tests/manual/ --tb=short
```

**Validation**:

- All core tests pass (100% pass rate required)
- No failures in excluded manual tests
- Short traceback format for clear error diagnosis

**Failure Action**: ABORT - Fix test failures before proceeding.

### 1.4 Security Audit

**Command**:

```bash
codesentinel scan
```

**Validation**:

- No critical or high-severity findings
- All security issues documented or whitelisted
- Dependency vulnerability scan passed

**Failure Action**: ABORT - Resolve security issues before proceeding.

### 1.5 Code Quality Audit

**Command**:

```bash
codesentinel !!!
```

**Validation**:

- Dev audit completes successfully
- All false positives verified and documented
- No critical or high-severity findings
- Low-priority efficiency/minimalism warnings acceptable

**Failure Action**: ABORT for critical findings; warn for low-priority.

### 1.6 Root Directory Pre-Check

**Command**:

```bash
python tools/codesentinel/root_cleanup.py --dry-run
```

**Validation**:

- No unauthorized files/directories at root
- Output shows `total_issues: 0` or pre-approved exceptions only
- Build artifacts (`build/`, `*.egg-info`) absent

**Failure Action**: WARN - Root cleanup recommended before packaging.

---

## Phase 2: BUILD EXECUTION

**Objective**: Create distribution artifacts (source + wheel).

### 2.1 Clean Previous Builds

**Command**:

```bash
Remove-Item -Path dist/ -Recurse -Force 2>$null
Remove-Item -Path build/ -Recurse -Force 2>$null
Remove-Item -Path *.egg-info -Recurse -Force 2>$null
```

**Validation**: Previous artifacts removed successfully.

**Failure Action**: CONTINUE (manual cleanup may be needed afterward).

### 2.2 Build Distribution Packages

**Command**:

```bash
python -m build --sdist --wheel
```

**Validation**:

- Both source distribution (`.tar.gz`) and wheel (`.whl`) created
- No build errors or warnings (setuptools warnings acceptable)
- Output indicates "Successfully built..."

**Expected Output**:

```
Successfully built codesentinel-X.X.X.tar.gz and codesentinel-X.X.X-py3-none-any.whl
```

**Failure Action**: ABORT - Debug build issues, consult setuptools output.

### 2.3 Verify Build Artifacts Exist

**Command**:

```bash
ls dist/codesentinel-X.X.X*
```

**Validation**:

- Two files present: `.tar.gz` and `.whl`
- File sizes reasonable (> 100KB)
- Timestamps current

**Failure Action**: ABORT - Build output missing.

---

## Phase 3: ARTIFACT VERIFICATION

**Objective**: Validate distribution package contents and integrity.

### 3.1 Extract Source Distribution Contents

**Command**:

```bash
tar -tzf dist/codesentinel-X.X.X.tar.gz | head -20
```

**Validation**:

- Top-level directory: `codesentinel-X.X.X/`
- Core files present: `setup.py`, `pyproject.toml`, `README.md`, `LICENSE`
- Source code directory: `codesentinel/`
- Test files included: `tests/`

**Failure Action**: WARN - Inspect archive manually with full contents listing.

### 3.2 Inspect Wheel Contents

**Command**:

```bash
unzip -l dist/codesentinel-X.X.X-py3-none-any.whl | head -30
```

**Validation**:

- Package directory: `codesentinel/`
- Metadata directory: `codesentinel-X.X.X.dist-info/`
- Entry points configured
- LICENSE file included

**Failure Action**: WARN - Verify wheel structure manually.

### 3.3 Package Metadata Validation

**Command**:

```bash
python -m build --sdist --wheel --outdir /tmp
unzip -p /tmp/codesentinel-X.X.X-py3-none-any.whl codesentinel-X.X.X.dist-info/METADATA | head -20
```

**Validation**:

- Metadata Name matches: `codesentinel`
- Version matches target: `X.X.X`
- Author, License, URLs present
- Dependencies listed correctly

**Failure Action**: WARN - Inspect METADATA file directly.

---

## Phase 4: ROOT DIRECTORY VALIDATION

**Objective**: Ensure root directory is clean before committing to git.

**CRITICAL**: This phase is mandatory and prevents git hook rejection.

### 4.1 Dry-Run Validation

**Command**:

```bash
python tools/codesentinel/root_cleanup.py --dry-run
```

**Validation**:

- Output shows `total_issues: 0` OR
- All issues are pre-approved and documented
- No unauthorized files/directories listed

**Failure Action**:

- If issues found: Proceed to 4.2
- If dry-run fails: ABORT and debug cleanup tool

### 4.2 Execute Root Cleanup (If Needed)

**Command**:

```bash
python tools/codesentinel/root_cleanup.py
```

**Validation**: Returns exit code 0, output confirms cleanup.

**Failure Action**: ABORT - Manual cleanup required.

### 4.3 Post-Cleanup Verification

**Command**:

```bash
python tools/codesentinel/root_cleanup.py --dry-run
```

**Validation**:

- Must show `total_issues: 0` with message "Root directory is clean"
- No unauthorized items remaining

**Failure Action**: ABORT - Manual review of root directory required.

---

## Phase 5: GIT OPERATIONS

**Objective**: Commit changes, create release tag, push to remote.

### 5.1 Stage Changes

**Command**:

```bash
git add -A
```

**Validation**: All modified files staged (verify with `git status`).

### 5.2 Commit Release

**Command**:

```bash
git commit -m "chore: Version X.X.X release - [comprehensive change summary]"
```

**Commit Message Format**:

```
chore: Version X.X.X release - [feature], [bugfix], [improvement]
```

**Validation**:

- Commit created successfully
- Message includes version number
- All staged files included in commit

**Failure Action**: WARN - Amend commit if needed with `git commit --amend`.

### 5.3 Verify Commit

**Command**:

```bash
git log -1 --oneline
```

**Validation**: Latest commit shows correct version in message.

### 5.4 Create Annotated Tag

**Command**:

```bash
git tag -a vX.X.X -m "CodeSentinel vX.X.X - [Release description]"
```

**Tag Message Format**:

```
CodeSentinel vX.X.X - [Beta/Stable] release with [key improvements]
```

**Validation**: Tag created successfully.

**Failure Action**: ABORT - Use `git tag -d vX.X.X` to delete and retry.

### 5.5 Verify Tag

**Command**:

```bash
git tag -l vX.X.X
git show vX.X.X
```

**Validation**:

- Tag exists in local repo
- Tag points to correct commit
- Tag message correct

**Failure Action**: ABORT - Investigate tag configuration.

### 5.6 Push Commit to Remote

**Command**:

```bash
git push origin main
```

**Validation**:

- Output shows commit pushed
- No rejected commits
- Remote branch updated

**Failure Action**: ABORT - Resolve push conflicts or authentication issues.

### 5.7 Push Tag to Remote

**Command**:

```bash
git push origin vX.X.X
```

**Validation**:

- Output shows `[new tag] vX.X.X -> vX.X.X`
- Tag successfully transferred to remote

**Failure Action**: ABORT - Verify remote access and retry.

---

## Phase 6: POST-PUSH VERIFICATION

**Objective**: Validate release is complete and properly reflected on remote.

**CRITICAL**: This phase confirms the release is publicly available.

### 6.1 Verify Remote Commit

**Command**:

```bash
git log -1 origin/main --oneline
```

**Validation**:

- Remote HEAD matches local commit
- Version number visible in commit message
- Timestamp reflects current push time

**Failure Action**: WARN - Investigate push completion, retry if needed.

### 6.2 Verify Remote Tag

**Command**:

```bash
git ls-remote origin | grep vX.X.X
```

**Validation**:

- Tag appears in remote refs
- Output format: `[commit_hash]  refs/tags/vX.X.X`

**Failure Action**: WARN - Tag push may have failed, verify on GitHub.

### 6.3 Verify README Version on Remote

**Command**:

```bash
git show origin/main:README.md | Select-String "X.X.X" | Select-Object -First 3
```

**Validation**:

- Version badge shows correct version: `version-X.X.X`
- Multiple occurrences found (header, badge, metadata)

**Failure Action**: WARN - Version may not have been committed, verify locally.

### 6.4 Verify CHANGELOG on Remote

**Command**:

```bash
git show origin/main:CHANGELOG.md | Select-String "## \[vX.X.X\]"
```

**Validation**:

- CHANGELOG header found: `## [vX.X.X]`
- Date matches release date

**Failure Action**: WARN - CHANGELOG not updated in commit.

### 6.5 GitHub Workflow Trigger Verification

**Command**:

```bash
# Check GitHub Actions status via API or web interface
# API: GET https://api.github.com/repos/joediggidyyy/CodeSentinel/actions
```

**Validation**:

- GitHub Actions workflow triggered on tag push
- Status checks visible on GitHub
- CI/CD pipeline running

**Failure Action**: WARN - Review GitHub Actions logs manually.

### 6.6 Distribution Artifacts Available

**Command**:

```bash
# Verify artifacts in dist/ directory still exist
ls -lh dist/codesentinel-X.X.X*
```

**Validation**:

- Both `.tar.gz` and `.whl` present
- File sizes > 100KB
- Timestamps reflect build time

**Failure Action**: WARN - Artifacts may be needed for PyPI upload.

### 6.7 Release Notes Availability

**Verification**:

- GitHub Release page created (automatic with annotated tag)
- Release description includes version, date, key changes
- Assets section shows build artifacts (if uploaded)

**Action**: Monitor GitHub for release creation (may take minutes).

---

## Safety Checkpoints & Rollback Procedures

### Checkpoint: Build Artifact Issues

**Trigger**: Validation fails in Phases 2 or 3  
**Action**:

1. STOP pipeline
2. Run `python -m build --verbose` for detailed output
3. Fix build issues (dependencies, setup.py, MANIFEST.in)
4. Restart from Phase 2.1 (clean builds)

### Checkpoint: Root Directory Violation

**Trigger**: Phase 4 fails  
**Action**:

1. STOP pipeline
2. Review root_cleanup.py output
3. Remove unauthorized files manually if cleanup fails
4. Restart from Phase 4.1
5. **Cannot proceed to git operations without clean root**

### Checkpoint: Git Operation Failure

**Trigger**: Phase 5 fails  
**Action**:

1. STOP pipeline
2. Diagnose git error (authentication, conflicts, remote issues)
3. If commit failed: Amend and retry
4. If tag failed: Delete tag with `git tag -d vX.X.X` and retry
5. If push failed: Resolve conflicts and retry
6. Restart from Phase 5.1 after resolution

### Checkpoint: Post-Push Verification Fails

**Trigger**: Phase 6 validation fails  
**Action**:

1. WARN but DO NOT abort
2. Investigate specific failure:
   - Remote commit mismatch: Verify GitHub webhook delays
   - Tag not on remote: Retry `git push origin vX.X.X`
   - Version mismatch: Check if correct commit was pushed
3. Manual verification on GitHub
4. Retry individual verification steps as needed
5. **Release is complete if git operations succeeded, even if some verifications timeout**

---

## Pipeline Execution Command (Full)

```bash
# Phase 1: Pre-Package Validation
## 1.1 Version Check
grep "1.1.3.b1" pyproject.toml setup.py codesentinel/__init__.py

## 1.2 CHANGELOG
grep "v1.1.3.b1" CHANGELOG.md

## 1.3 Tests
python -m pytest tests/ -v --ignore=tests/manual/ --tb=short

## 1.4 Security Audit
codesentinel scan

## 1.5 Code Quality
codesentinel !!!

## 1.6 Root Pre-Check
python tools/codesentinel/root_cleanup.py --dry-run

# Phase 2: Build
## 2.1 Clean
Remove-Item -Path dist/, build/, *.egg-info -Recurse -Force -ErrorAction SilentlyContinue

## 2.2 Build
python -m build --sdist --wheel

## 2.3 Verify
ls dist/codesentinel-*.tar.gz dist/codesentinel-*.whl

# Phase 4: Root Validation (BEFORE GIT)
## 4.1 Dry-run
python tools/codesentinel/root_cleanup.py --dry-run

## 4.2 Execute (if issues found)
python tools/codesentinel/root_cleanup.py

## 4.3 Verify clean
python tools/codesentinel/root_cleanup.py --dry-run

# Phase 5: Git Operations
## 5.1 Commit
git add -A
git commit -m "chore: Version 1.1.3.b1 release - keyboard interrupt fixes, false positive elimination, comprehensive testing"

## 5.4 Tag
git tag -a v1.1.3.b1 -m "CodeSentinel v1.1.3.b1 - Beta release with SEAM-tight CLI improvements"

## 5.6-5.7 Push
git push origin main
git push origin v1.1.3.b1

# Phase 6: Post-Push Verification
## 6.1 Remote commit
git log -1 origin/main --oneline

## 6.2 Remote tag
git ls-remote origin | Select-String "v1.1.3.b1"

## 6.3 README version on remote
git show origin/main:README.md | Select-String "1.1.3.b1" | Select-Object -First 3

## 6.4 CHANGELOG on remote
git show origin/main:CHANGELOG.md | Select-String "v1.1.3.b1"

## 6.6 Local artifacts
ls -lh dist/codesentinel-1.1.3.b1*
```

---

## Pipeline Entry Points

### Full Pipeline (Complete Release)

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
```

### Quick Verify (No Changes)

```
Phase 6 only - verify remote state
```

### Hotfix Release

```
Phase 1 (skip tests if urgent) → Phase 4 → Phase 5 → Phase 6
```

### Test Package Build

```
Phase 2.1 → Phase 2.2 → Phase 2.3 (stop, don't commit)
```

---

## Integration with CLI Suite

### Planned Commands

```bash
# Execute full pipeline
codesentinel package --release 1.1.3.b1

# Execute pipeline with options
codesentinel package --release 1.1.3.b1 --skip-tests --dry-run
codesentinel package --release 1.1.3.b1 --phase build
codesentinel package --release 1.1.3.b1 --verify-only

# Query pipeline status
codesentinel package --status
codesentinel package --last-release

# Rollback support
codesentinel package --rollback v1.1.3.b1
codesentinel package --list-releases
```

### GUI Dashboard Elements (Future)

1. **Pipeline Executor**: Visual step-by-step progression
2. **Checkpoint Monitor**: Real-time validation status
3. **Artifact Browser**: View and manage distribution packages
4. **Git Operations Panel**: Commit, tag, push controls
5. **Verification Dashboard**: Post-push validation results
6. **Release History**: Track past releases with status

---

## Mandatory Compliance

This directive is **CONSTITUTIONAL-TIER** (Non-Negotiable):

1. **Every release must follow all 6 phases** in sequence
2. **Phase 4 (Root Validation) is blocking** - Cannot skip
3. **Phase 6 post-push verification is mandatory** - Confirms release completion
4. **All checkpoints must pass** - Exceptions require explicit approval
5. **Dry-run before execute** - Always preview before action
6. **Validate after execute** - Always verify results

**Deviation Policy**: Only authorized for critical security hotfixes with documented justification.

---

## Success Criteria

A release is **COMPLETE** when:

✅ Phase 1: All validation checks pass  
✅ Phase 2: Both distribution artifacts created  
✅ Phase 3: Artifacts pass integrity checks  
✅ Phase 4: Root directory is clean  
✅ Phase 5: Commit, tag, and push successful  
✅ Phase 6: Post-push verification confirms remote state  

**Release Status**: READY FOR DISTRIBUTION

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | CodeSentinel Agent | Initial directive: 6 phases, 18 checkpoints, complete pipeline |

---

## References

- `codesentinel/cli/` - Future CLI implementation
- `tools/codesentinel/root_cleanup.py` - Root validation tool
- `CHANGELOG.md` - Release documentation
- `.github/workflows/` - GitHub Actions CI/CD configuration
