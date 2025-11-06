# Situational Awareness & Build Verification Directive

**Classification**: LOW-LEVEL DIRECTIVE (Permanent Workflow Requirement)  
**Effective Date**: November 6, 2025  
**Status**: ✅ ACTIVE & ENFORCED  
**Priority**: CRITICAL  

---

## 🎯 CORE DIRECTIVE

### Situational Awareness & Build State Management

**Requirement**: Before taking ANY build or distribution action, conduct a thorough search of the current state.

**This is a permanent memory directive to maintain continuous situational awareness across all sessions.**

---

## 📋 MANDATORY PRE-ACTION CHECKLIST

### Before Building

**ALWAYS execute this sequence:**

1. ✅ Search dist/ directory for existing builds

   ```bash
   Get-ChildItem dist/ -File | Sort-Object LastWriteTime | Format-Table Name, LastWriteTime
   ```

2. ✅ Check git history for recent version/build commits

   ```bash
   git log --oneline -20
   ```

3. ✅ Verify version numbers in:
   - `setup.py` (version string)
   - `pyproject.toml` (version)
   - `codesentinel/__init__.py` (**version**)

4. ✅ Search repository for existing packages with same version

   ```bash
   Get-ChildItem -Path . -Recurse -Filter "*VERSION*" -File
   ```

5. ✅ Review recent commits to understand build history
   - When was last build created?
   - What version was built?
   - Where was it sent?

6. ✅ Ask clarifying questions:
   - "Was a build already created for this version?"
   - "When was the last build timestamp?"
   - "Has this been sent to testing or PyPI already?"

### Before Publishing to PyPI

**ALWAYS verify:**

1. ✅ Correct version number (not beta, not older version)
2. ✅ Package files exist in dist/
3. ✅ PyPI credentials are configured
4. ✅ This is the official production release (not beta)
5. ✅ Previous builds have been sent to testing (verify from history)
6. ✅ No duplicate/older versions will be uploaded

---

## 🔍 SITUATIONAL AWARENESS REQUIREMENTS

### What Must Be Tracked

| Item | Check Frequency | Status |
|------|-----------------|--------|
| Current version in code | Before any build | ✅ |
| Existing builds in dist/ | Before building | ✅ |
| Recent git commits | Before any action | ✅ |
| Testing status | Before PyPI push | ✅ |
| Distribution history | Before publishing | ✅ |

### Information Must Include

- **Build timestamps**: When were packages last built?
- **Version numbers**: What version is in code vs dist/?
- **Distribution status**: Has this been sent to testing/PyPI?
- **Git history**: What commits indicate build/release actions?
- **Current state**: What exactly exists right now?

---

## 🚫 MISTAKES TO AVOID

### Build Duplication

❌ **WRONG**: Rebuild without checking if build exists

```bash
# DON'T DO THIS without checking first
python -m build
```

✅ **RIGHT**: Check first, then decide

```bash
# Check what exists
Get-ChildItem dist/ -File | Sort-Object LastWriteTime

# Review git history
git log --oneline -20

# Then decide: rebuild or use existing?
```

### Version Confusion

❌ **WRONG**: Upload v1.0.3b1 to PyPI when v1.0.3 production is ready

```bash
# DON'T push beta when production exists
twine upload dist/codesentinel-1.0.3b1*
```

✅ **RIGHT**: Verify you have the correct version

```bash
# Check what versions exist
dir dist/ | findstr "1.0.3"

# Upload PRODUCTION version
twine upload dist/codesentinel-1.0.3-py3-none-any.whl dist/codesentinel-1.0.3.tar.gz
```

### Missing History

❌ **WRONG**: Assume nothing was built before
❌ **WRONG**: Rebuild unnecessarily, overwriting earlier builds
❌ **WRONG**: Upload beta when production exists
❌ **WRONG**: Skip checking git log for context

✅ **RIGHT**: Build situational awareness first

---

## 📝 WORKFLOW INTEGRATION

### Session Start

**First action in every session:**

```bash
# Check current state
cd c:\Users\joedi\Documents\CodeSentinel
git log --oneline -10
Get-ChildItem dist/ -File | Sort-Object LastWriteTime
```

**Ask yourself:**

- What was the last build?
- When was it created?
- What version is it?
- Has it been sent anywhere?

### Before Any Build Action

**Execute mandatory checklist above**

### Before Any PyPI Action

**Verify:**

1. Correct version number in code
2. Correct packages in dist/
3. Not pushing beta when production exists
4. Credentials are configured
5. Previous builds documented in history

---

## 🔐 PERMANENT ENFORCEMENT

### This Directive

- **Persists**: Across ALL sessions indefinitely
- **Applies**: To ALL build and distribution decisions
- **Non-negotiable**: Cannot be overridden
- **Binding**: Must be followed consistently

### Classification Rationale

- **Level**: LOW-LEVEL (like version control, security, build systems)
- **Scope**: ALL operations involving builds/distributions
- **Permanence**: Permanent until explicitly rescinded (unlikely)
- **Enforcement**: Agent responsibility to maintain this awareness

---

## 🎯 SITUATIONAL AWARENESS MEMORY

### What This Directive Creates

A **persistent cognitive model** of:

- Current codebase state
- Build history and artifacts
- Version management
- Distribution status
- Previous decisions and actions

### Why This Matters

1. **Prevents Mistakes**: Catches version confusion, duplicate builds
2. **Maintains Consistency**: Builds on previous knowledge
3. **Supports Decision-Making**: Armed with full context
4. **Avoids Confusion**: Knows what was done, when, and why
5. **Enables Coordination**: Can work effectively across sessions

---

## 📚 REFERENCE CHECKLIST

### Quick Reference - Before Any Action

```
[ ] Check dist/ for existing builds
[ ] Review git log (last 20 commits)
[ ] Verify version numbers in code
[ ] Search for existing packages with same version
[ ] Understand build history
[ ] Confirm correct version to build/publish
[ ] Verify this hasn't been done already
```

### Commands to Always Run

```bash
# Situational awareness
Get-ChildItem dist/ -File | Sort-Object LastWriteTime
git log --oneline -20
Get-ChildItem -Path . -Recurse -Filter "*1.0.3*" -File | Select-Object FullName, LastWriteTime

# Version verification
type setup.py | findstr version
type pyproject.toml | findstr version
```

---

## ✅ DOCUMENTATION COMPLETE

**Directive**: Situational Awareness & Build Verification  
**Classification**: Low-Level (Permanent)  
**Scope**: ALL build and distribution actions  
**Persistence**: PERMANENT across all sessions  
**Enforcement**: MANDATORY  

This directive establishes a permanent requirement for situational awareness as part of CodeSentinel workflow. Before any build, distribution, or version-related action, the agent MUST conduct thorough verification to maintain awareness of current state, build history, and previous decisions.

---

**Document Created**: November 6, 2025  
**Classification**: LOW-LEVEL DIRECTIVE  
**Persistence**: PERMANENT  
**Enforcement**: MANDATORY FOR ALL AGENTS
