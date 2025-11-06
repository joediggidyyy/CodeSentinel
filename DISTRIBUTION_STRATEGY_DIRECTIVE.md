# CodeSentinel Distribution & PyPI Strategy

**Classification**: LOW-LEVEL DIRECTIVE (Persistent Workflow Requirement)  
**Effective Date**: November 6, 2025  
**Status**: ✅ ACTIVE & ENFORCED  
**Last Updated**: November 6, 2025  

---

## 🔑 CRITICAL DIRECTIVE

### Distribution Credentials & PyPI Strategy

**Status**: ✅ PyPI credentials ARE configured  
**Access Level**: Active and operational  
**Publication Strategy**: Beta versions published to PyPI  
**Persistence**: This directive persists across all sessions and is non-negotiable  

---

## 📦 CURRENT DISTRIBUTION STATE

### PyPI Publication History

| Version | Type | Status | Location |
|---------|------|--------|----------|
| v1.0.1 | Release | ✅ Published to PyPI | PyPI (current stable) |
| v1.0.3b0 | Beta | ✅ Published to PyPI | PyPI (test version) |
| v1.0.3b1 | Beta | ✅ Published to PyPI | PyPI (latest beta) |
| v1.0.3 | Release | ⏳ PENDING | Local dist/ directory |

### Where CodeSentinel Is Available

- ✅ **PyPI** - pip install codesentinel (stable releases + beta versions)
- ✅ **GitHub** - <https://github.com/joediggidyyy/CodeSentinel>
- ✅ **Local Dist** - `dist/` directory in repository

---

## 🔄 DISTRIBUTION WORKFLOW

### Standard Release Process

1. **Beta Testing Phase**
   - Build beta version (e.g., v1.0.3b1)
   - Publish to PyPI immediately
   - Collect feedback and test
   - Monitor via pip: `pip install codesentinel==1.0.3b1`

2. **Production Release Phase**
   - Finalize release version (e.g., v1.0.3)
   - Create official tag on GitHub
   - Push code to GitHub
   - **Publish to PyPI** (MUST be done for production releases)

3. **Post-Release Monitoring**
   - Track issues on GitHub
   - Monitor PyPI stats
   - Prepare for next beta/release cycle

---

## 📋 AGENT RESPONSIBILITIES

### Tracking Distribution Strategy

**At Every Release**:

- ✅ Document current PyPI publication status
- ✅ Verify credentials are configured
- ✅ Note which versions are on PyPI
- ✅ Track publication strategy (beta vs release)
- ✅ Update this directive if strategy changes

**Before Each Publication**:

- ✅ Confirm PyPI credentials exist
- ✅ Verify build artifacts in `dist/`
- ✅ Check PyPI versions already published
- ✅ Plan publication approach (beta/release)

**After Each Publication**:

- ✅ Verify on PyPI: `pip install codesentinel==VERSION`
- ✅ Document in release notes
- ✅ Update distribution tracking
- ✅ Announce via GitHub releases

---

## 🚀 CURRENT ACTION REQUIRED

### v1.0.3 Production Release - PyPI Publication

**Status**: NOT YET PUBLISHED  
**Action**: PUBLISH TO PyPI  
**Command**:

```bash
twine upload dist/codesentinel-1.0.3b1-py3-none-any.whl dist/codesentinel-1.0.3b1.tar.gz
```

**Note**: v1.0.3 release should be published to PyPI to make it available to users via:

```bash
pip install codesentinel==1.0.3
```

---

## 🔐 CREDENTIALS CONFIGURATION

### PyPI Access

**Status**: ✅ Configured and Active  
**Configuration Method**: `.pypirc` or environment variables (verified working)  
**Publication Tool**: `twine` (recommended)  
**Backup Method**: `python setup.py upload` (legacy)

### Verification

To verify credentials are working:

```bash
twine check dist/codesentinel-1.0.3b1*
twine upload --dry-run dist/codesentinel-1.0.3b1*
```

---

## 📊 DISTRIBUTION TRACKING

### What Must Be Tracked

| Item | Status | Update Frequency |
|------|--------|------------------|
| PyPI credentials | ✅ Configured | Every session (verify) |
| Latest version on PyPI | v1.0.3b1 (beta) | After each release |
| GitHub tag status | ✅ v1.0.3 live | Continuous |
| Build artifacts | ✅ Ready in dist/ | After build |
| Publication strategy | Beta → Release cycle | Per release |

### Information Must Include

- Which versions are published to PyPI
- Publication status (beta vs production)
- PyPI availability for each release
- User installation commands
- Distribution channel status

---

## 📝 WORKFLOW INTEGRATION

### Before Any Release Decision

**Ask Yourself**:

1. ✅ Are PyPI credentials configured? (YES - confirmed)
2. ✅ Have beta versions been published? (YES - v1.0.3b0, v1.0.3b1)
3. ✅ What's the current PyPI version? (v1.0.3b1)
4. ✅ Should this release go to PyPI? (YES - production releases must)
5. ✅ Are build artifacts ready? (CHECK `dist/` directory)

### Persistence Checklist

- ✅ **Session Persistence**: This applies to ALL sessions
- ✅ **Permanent Policy**: Not a temporary guideline
- ✅ **Mandatory Tracking**: Distribution strategy is core workflow
- ✅ **Non-Negotiable**: Must be followed on every release
- ✅ **Documentation**: Always document PyPI status

---

## 🎯 CLASSIFICATION

### Directive Level: LOW-LEVEL (Persistent)

**Meaning**:

- Applies to all operations
- Persists across sessions
- Not overrideable by higher-level decisions
- Part of core workflow

**Equivalent To**:

- Version control best practices
- Security policies
- Build system requirements
- Testing standards

---

## 🔔 KEY REMINDERS

### MUST DO

1. ✅ Track PyPI credentials status (they ARE configured)
2. ✅ Note all version publications (beta AND production)
3. ✅ Publish production releases to PyPI
4. ✅ Document distribution strategy in release notes
5. ✅ Verify each publication works via pip

### MUST NOT DO

1. ❌ Assume PyPI isn't available
2. ❌ Skip publishing production releases
3. ❌ Forget to track which versions are on PyPI
4. ❌ Ignore distribution strategy in planning
5. ❌ Lose this directive across sessions

---

## 📞 REFERENCE

### Quick Links

- **PyPI Profile**: <https://pypi.org/project/codesentinel/>
- **Install Latest Beta**: `pip install codesentinel==1.0.3b1`
- **Install Stable**: `pip install codesentinel` (v1.0.1 currently)
- **GitHub Repository**: <https://github.com/joediggidyyy/CodeSentinel>

### Commands

```bash
# Check what's on PyPI
pip index versions codesentinel

# Upload to PyPI (requires credentials)
twine upload dist/codesentinel-1.0.3b1*

# Install specific version
pip install codesentinel==1.0.3b1

# Verify installation
pip show codesentinel
```

---

## ✅ DOCUMENTATION COMPLETE

**Directive**: Distribution & PyPI Strategy  
**Classification**: Low-Level (Persistent)  
**Status**: ✅ Documented and Active  
**Effective**: Immediate and Ongoing  

This directive persists as part of the core CodeSentinel workflow and must be tracked and considered in all release and distribution decisions.

---

**Document Created**: November 6, 2025  
**Classification**: LOW-LEVEL DIRECTIVE  
**Persistence**: PERMANENT  
**Enforcement**: MANDATORY
