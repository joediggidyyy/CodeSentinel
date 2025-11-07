# CodeSentinel Core Package Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: CLI development, core module updates, feature additions in codesentinel/ directory  
**Target Users**: Agents working on CodeSentinel core functionality  
**Last Updated**: November 7, 2025  
**Version**: 1.0

---

## Quick Authority Reference

**Who can create, modify, delete in this domain?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create new CLI command | Agent | Yes (user verification) |
| Create new core module | Agent | Yes (user verification) |
| Create utility script | Agent | Yes (user verification) |
| Modify existing code | Agent | No (minor), Yes (major) |
| Delete code/features | Agent | Yes (always) |
| Add dependencies | Agent | Yes (always) |
| Update **init**.py | Agent | No (minor), Yes (major) |
| Create test coverage | Agent | No |
| Fix bugs/issues | Agent | No |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Tier 4 Agent Documentation authority matrix

---

## Domain Overview

The `codesentinel/` directory contains the core CodeSentinel Python package including:

- **CLI Interface** (`cli/`) - Command-line tools and user interactions
- **Core Functionality** (`core/`) - Main processing and business logic
- **GUI** (`gui/`) - Graphical user interface (optional)
- **Utilities** (`utils/`) - Configuration, alerting, scheduling, logging

This is **core infrastructure** for CodeSentinel. Changes here affect the entire system and require thoughtful implementation.

**Key Principles for This Domain**:

- SECURITY > EFFICIENCY > MINIMALISM (always)
- Non-destructive changes required
- Feature preservation mandatory
- Backward compatibility important
- Full test coverage for new code

---

## Common Procedures

### Procedure 1: Add New CLI Command

**When**: User requests new command or automation detects missing functionality

**Steps**:

1. **Verify Authority**: Check if user has approved this feature ✅
2. **Plan Structure**: Determine CLI command name and arguments
   - Follow existing command patterns in `cli/__init__.py`
   - Use consistent argument naming (e.g., `--config`, `--output`)
   - Document usage in docstring

3. **Implement Command**:
   - Create handler function in appropriate `cli/` submodule
   - Add argument parsing with help text
   - Implement core logic with error handling
   - Return exit code (0 for success, non-zero for failure)

4. **Add Tests**:
   - Create test in `tests/test_cli.py`
   - Test successful execution
   - Test error conditions
   - Test with invalid arguments
   - Aim for 100% code coverage

5. **Update Documentation**:
   - Add command to README.md (Quick Start section)
   - Create procedure guide if complex
   - Classify as Tier 2 (Informative)

6. **Validation**:
   - All tests pass ✅
   - Manual testing of command ✅
   - Help text is clear and accurate ✅
   - No breaking changes to existing commands ✅
   - No hardcoded secrets or credentials ✅

7. **Commit**:
   - Message: `feat(cli): add [command name] command`
   - Include test and documentation commits

---

### Procedure 2: Add New Core Module

**When**: Major new functionality requires new processing module

**Steps**:

1. **Verify Authority**: Check user approval ✅

2. **Design Module**:
   - Plan class/function structure
   - Identify dependencies on other modules
   - Consider Tier 1 infrastructure requirements
   - Document public API clearly

3. **Implement Module**:
   - Create file in `core/[module_name].py`
   - Follow Python best practices and CodeSentinel style
   - Include comprehensive docstrings
   - Handle errors gracefully
   - Use logging for important events
   - No hardcoded configuration

4. **Integration**:
   - Add imports to `core/__init__.py`
   - Ensure proper module exposure
   - Test integration with other core modules
   - Update any dependency documentation

5. **Testing**:
   - Create `tests/test_[module_name].py`
   - Unit tests for all public methods
   - Integration tests with related modules
   - Error condition testing
   - Aim for 100% coverage

6. **Documentation**:
   - Add to architecture documentation
   - Document public API
   - Create usage examples if complex
   - Classify as Tier 2 (Informative)

7. **Validation**:
   - All tests pass ✅
   - Module is properly exposed in `__init__.py` ✅
   - No circular dependencies ✅
   - Compatible with existing code ✅
   - Performance acceptable ✅

8. **Commit**:
   - Message: `feat(core): add [module name] module`
   - Include all tests and documentation

---

### Procedure 3: Update Dependency

**When**: Security patch, bug fix, or new feature requires dependency update

**Steps**:

1. **Verify Authority**: Dependency changes require user approval ✅

2. **Research Update**:
   - Check changelog for breaking changes
   - Review security advisories if applicable
   - Test compatibility with existing code
   - Document why update is needed

3. **Update Version**:
   - Modify version in `requirements.txt` or `pyproject.toml`
   - Follow semantic versioning best practices
   - Document version pinning rationale if pinning specific version

4. **Test Compatibility**:
   - Run full test suite
   - Test on multiple Python versions if applicable
   - Test with dependent modules
   - Check for deprecated API usage

5. **Update Code if Needed**:
   - Update code for API changes if required
   - Deprecate old approaches if needed
   - Update imports if module names changed
   - Add compatibility shims if necessary

6. **Documentation**:
   - Document breaking changes if any
   - Update API documentation if affected
   - Note dependency version changes in CHANGELOG.md

7. **Validation**:
   - All tests pass with new version ✅
   - No new warnings or deprecations ✅
   - Backward compatibility verified ✅
   - Performance not negatively impacted ✅

8. **Commit**:
   - Message: `deps: update [dependency] to v[version]`
   - Include reason for update
   - Include test results summary

---

### Procedure 4: Fix Bug in Core Module

**When**: Bug reported or discovered during development

**Steps**:

1. **Understand Bug**:
   - Create minimal reproduction case
   - Identify root cause
   - Determine scope of impact
   - Check if it affects multiple areas

2. **Write Test First**:
   - Create failing test that reproduces bug
   - Test should demonstrate the problem clearly
   - Add to existing test file or create new one

3. **Implement Fix**:
   - Make minimal change to fix the bug
   - Avoid scope creep
   - Follow existing code patterns
   - Add comments if fix is non-obvious

4. **Verify Fix**:
   - Reproducer test now passes ✅
   - All other tests still pass ✅
   - No new warnings introduced ✅
   - Fix is minimal and focused ✅

5. **Check Impact**:
   - Identify if other code might be affected
   - Update related code if necessary
   - Consider if documentation needs updates

6. **Validation**:
   - All tests passing ✅
   - Manual verification of fix ✅
   - No side effects observed ✅
   - Performance not negatively impacted ✅

7. **Commit**:
   - Message: `fix(core): [description of bug fix]`
   - Reference issue number if applicable
   - Include test in same commit

---

## Quick Classification Decision Tree

**Is this a document (not code)?**

- If YES → Check docs/AGENT_INSTRUCTIONS.md instead
- If NO → Continue

**Is this code in codesentinel/ directory?**

- If YES → Follow procedures above (Core Package)
- If NO → Check relevant satellite instructions

**What type of change?**

- New feature? → Use appropriate procedure (New CLI, New Module, or Update Dependency)
- Bug fix? → Use "Fix Bug" procedure
- Dependency update? → Use "Update Dependency" procedure
- Code improvement? → Check if tests cover, modify tests if needed, then implement

**Approval needed?**

- User-initiated feature? → YES (requires approval)
- Agent-initiated improvement? → NO (unless it's major structural change)
- Bug fix? → NO
- Dependency update? → YES

---

## Validation Checklist (Before Commit)

**Code Quality**:

- [ ] All new code has docstrings
- [ ] No commented-out code
- [ ] No hardcoded credentials/secrets
- [ ] No TODO comments without context
- [ ] Consistent with existing code style

**Testing**:

- [ ] All tests pass locally
- [ ] New code has test coverage
- [ ] Error cases tested
- [ ] Integration tests pass
- [ ] No test failures on unrelated code

**Dependencies**:

- [ ] No new security vulnerabilities
- [ ] All imports are used
- [ ] No circular dependencies
- [ ] Dependency versions documented

**Documentation**:

- [ ] Docstrings are clear and complete
- [ ] README updated if needed
- [ ] CHANGELOG.md entry added
- [ ] API documentation updated
- [ ] New procedures documented

**Compliance**:

- [ ] No feature deletions without archive
- [ ] Non-destructive changes only
- [ ] SECURITY > EFFICIENCY > MINIMALISM maintained
- [ ] No permanent deletions without user approval
- [ ] Archive strategy followed if archiving

**Commit Quality**:

- [ ] Commit message is clear and descriptive
- [ ] Commit includes related tests
- [ ] Commit includes related documentation
- [ ] No unrelated changes mixed in
- [ ] Commit is focused and atomic

---

## Common Decisions

### Q: Can I modify an existing utility function?

**A**: Yes, with these constraints:

- If backward compatible → No approval needed
- If breaking change → User approval required
- If removing code → Archive first, then delete (non-destructive)
- If deprecating → Leave compatibility shim for one release

### Q: Should I add a new CLI flag to existing command?

**A**: Yes, if:

- Flag is optional (doesn't break existing usage)
- Flag is well-documented
- Help text clearly explains purpose
- Tests cover new flag
- Backward compatible

### Q: What if I find code to delete/refactor?

**A**: Always:

1. Check what depends on it
2. Create tests for current behavior (before changes)
3. If deleting → Archive to quarantine first
4. If refactoring → Change gradually with tests passing at each step
5. Never delete without verification

### Q: Can I update dependencies automatically?

**A**: No. Dependency updates:

- Require user verification first
- Need security advisory checking
- Require full test suite pass
- Must document breaking changes
- Should be in separate commit

### Q: How do I handle a Python version upgrade?

**A**: Follow standard dependency update procedure:

1. Get user approval
2. Check compatibility of all dependencies
3. Update CI/CD if needed
4. Run full test suite on new version
5. Document any required code changes

---

## References & Links

**Core Documentation**:

- Global Policy: `docs/architecture/POLICY.md`
- Classification Framework: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
- General Strategy: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

**Codebase Structure**:

- CLI Module: `codesentinel/cli/`
- Core Module: `codesentinel/core/`
- Utilities: `codesentinel/utils/`
- Tests: `tests/`

**Key Files**:

- Package Entry: `codesentinel/__init__.py`
- CLI Entry: `codesentinel/cli/__init__.py`
- Dependencies: `requirements.txt`, `pyproject.toml`
- Tests Config: `pytest.ini`

---

## Quick Links

- When to archive code: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Lifecycle section
- Testing framework: `pytest` with full documentation in README.md
- Code style: Follow existing patterns in codesentinel/
- Documentation standards: See `docs/architecture/POLICY.md` - Professional Standards

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents working in codesentinel/ domain  
**Update Frequency**: When core procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)
