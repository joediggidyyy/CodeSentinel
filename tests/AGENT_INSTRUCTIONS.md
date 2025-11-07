# Testing & Validation Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: Test creation, validation procedures, quality assurance workflows in tests/ directory  
**Target Users**: Agents implementing tests and validation procedures  
**Last Updated**: November 7, 2025  
**Version**: 1.0

---

## Quick Authority Reference

**Who can create, modify, delete in this domain?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create new test file | Agent | No |
| Create new test cases | Agent | No |
| Modify test code | Agent | No |
| Delete test (unused) | Agent | No |
| Delete test (working) | Agent | Yes (verification) |
| Add test fixture | Agent | No |
| Add test helper | Agent | No |
| Change test framework | Agent | Yes (major decision) |
| Modify pytest.ini | Agent | Yes (major impact) |
| Add test dependency | Agent | Yes (always) |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Tier 4 Agent Documentation authority matrix

---

## Domain Overview

The `tests/` directory contains all test code for CodeSentinel including:

- **Unit Tests** (`test_*.py`) - Individual module testing
- **Integration Tests** - Multi-module workflows
- **Test Configuration** (`pytest.ini`) - Test framework settings
- **Test Fixtures** - Shared test data and utilities
- **Performance Tests** - Optional performance benchmarks

**Key Principles for This Domain**:
- 100% code coverage target for new code
- Tests should be fast and isolated
- No external dependencies without mocking
- Clear test names describing what they test
- Comprehensive error case coverage
- Non-destructive testing (no permanent changes)

---

## Common Procedures

### Procedure 1: Create Unit Test for New Code

**When**: Every new module or function in codesentinel/

**Steps**:

1. **Verify Coverage Plan**: Ensure the code being tested is new/untested ✅

2. **Identify Test Cases**:
   - Success case (normal operation)
   - Error case (invalid input)
   - Edge case (boundary conditions)
   - State case (multiple calls/persistence)
   - Integration case (with other modules if applicable)

3. **Create Test File** (if needed):
   - File: `tests/test_[module_name].py`
   - Import unittest or use pytest
   - Follow existing test patterns
   - Include docstrings explaining test intent

4. **Implement Unit Tests**:
   - One test per scenario
   - Descriptive test names: `test_[function]_[condition]_[expected_result]`
   - Use assertions to verify behavior
   - Mock external dependencies
   - No hardcoded paths or configuration

5. **Test Setup/Teardown**:
   - Use fixtures for shared test data
   - Clean up resources after tests
   - Isolate tests (no interdependencies)
   - Use temporary directories for file operations

6. **Run Tests**:
   - Run with pytest: `pytest tests/test_[module].py`
   - Verify all tests pass
   - Check coverage: `pytest --cov=codesentinel tests/`
   - Target: 100% coverage for new code

7. **Validation**:
   - All tests pass ✅
   - Coverage is 100% for new code ✅
   - No external dependencies without mocking ✅
   - Test runs in < 1 second (unless integration) ✅

8. **Commit**:
   - Message: `test: add unit tests for [module/function]`
   - Include test file and any fixtures
   - Commit with code being tested

---

### Procedure 2: Test an Existing Feature (Regression Test)

**When**: Bug discovered or existing behavior needs verification

**Steps**:

1. **Understand Behavior**:
   - What should the code do?
   - What is it currently doing wrong?
   - Create minimal reproduction case

2. **Check Existing Tests**:
   - Look for existing test coverage
   - Identify what tests are missing
   - Plan gap coverage

3. **Write Failing Test First**:
   - Create test that demonstrates the bug/gap
   - Test should fail with current code
   - Use descriptive test name
   - Document expected vs. actual behavior in test

4. **Implement Fix**:
   - Make minimal change to fix issue
   - Verify test now passes
   - Run full test suite to verify no regressions
   - Add comments if fix is complex

5. **Add Edge Case Tests**:
   - What other conditions could break this?
   - Add tests for related scenarios
   - Test error conditions
   - Test boundary values

6. **Validation**:
   - New test passes ✅
   - All existing tests still pass ✅
   - Coverage increased or maintained ✅
   - No performance regression ✅

7. **Commit**:
   - Message: `test: add regression test for [issue]`
   - Include both test and fix in same commit or separate

---

### Procedure 3: Integration Test for Multi-Module Workflow

**When**: Feature involves multiple modules or components

**Steps**:

1. **Define Workflow**:
   - What is the end-to-end scenario?
   - Which modules are involved?
   - What are the success criteria?

2. **Plan Test Structure**:
   - Create test in existing `tests/test_integration.py` or new file
   - Use fixtures for setup
   - Test complete workflow
   - Verify final state

3. **Create Test**:
   - Setup all required dependencies
   - Call workflow with test data
   - Assert expected results
   - Clean up resources

4. **Mock External Services** (if any):
   - Don't call real APIs
   - Mock network calls
   - Mock file system (if possible)
   - Keep test isolated and fast

5. **Test Error Paths**:
   - What if module A fails?
   - What if module B times out?
   - Recovery mechanisms tested?
   - Error propagation correct?

6. **Performance Check**:
   - Is test running in reasonable time? (< 10 seconds unless long-running)
   - Any obvious performance issues?
   - Memory usage acceptable?

7. **Validation**:
   - Integration test passes ✅
   - All unit tests still pass ✅
   - Coverage not decreased ✅
   - Test is maintainable and clear ✅

8. **Commit**:
   - Message: `test: add integration test for [feature]`
   - Include all related fixes/changes

---

### Procedure 4: Add Test Fixture for Shared Data

**When**: Multiple tests need same setup data or objects

**Steps**:

1. **Identify Shared Needs**:
   - What setup is repeated across tests?
   - What test data is common?
   - What resources need cleanup?

2. **Create Fixture File** (if needed):
   - File: `tests/conftest.py` (pytest standard)
   - Define reusable fixtures
   - Include docstrings
   - Document fixture parameters

3. **Implement Fixture**:
   - Use pytest.fixture or unittest setUp
   - Create objects/data needed by tests
   - Include cleanup in teardown
   - Make fixture configurable if needed

4. **Use in Tests**:
   - Add fixture as parameter to test functions
   - Use fixture data in test
   - Verify fixture isolation (independent tests)
   - No state shared between test runs

5. **Documentation**:
   - Document what fixture provides
   - Document any side effects
   - Note when/why to use this fixture
   - Link to tests using it

6. **Validation**:
   - Tests using fixture pass ✅
   - Fixture properly cleans up ✅
   - Fixture is reusable across tests ✅
   - No test interdependencies created ✅

7. **Commit**:
   - Message: `test: add [fixture name] fixture`
   - Include fixture definition and tests using it

---

## Quick Test Classification Tree

**What are you testing?**

- New function/method? → Use "Unit Test" procedure
- New module? → Create test file with unit tests for all functions
- Existing feature (bug or regression)? → Use "Regression Test" procedure
- Multi-module workflow? → Use "Integration Test" procedure
- Shared test data? → Use "Test Fixture" procedure
- CLI command? → Create test in test_cli.py using mocking

**How complex is the test?**

- Single function call? → Unit test
- Multiple module interactions? → Integration test
- Long-running scenario? → Consider if it can be unit tested, separate integration tests
- External service call? → Mock it, don't call real service

**What test type to use?**

- Most tests: pytest with fixtures
- CLI tests: Mock subprocess calls, test with fixtures
- Configuration tests: Test with temp files, clean up after
- Database/file tests: Use temp directories and mocks

---

## Validation Checklist (Before Commit)

**Test Quality**:
- [ ] Test name clearly describes what is being tested
- [ ] Test has single responsibility/assertion group
- [ ] No hardcoded paths or configuration
- [ ] No external API calls (mocked instead)
- [ ] Setup and teardown properly handle resources

**Coverage**:
- [ ] Success case tested
- [ ] Error case tested
- [ ] Edge case tested
- [ ] New code has 100% coverage
- [ ] Overall coverage not decreased

**Performance**:
- [ ] Unit test completes < 1 second
- [ ] Integration test completes < 10 seconds
- [ ] No obvious performance issues
- [ ] No unnecessary loops or waits

**Isolation**:
- [ ] Test passes independently
- [ ] Test passes in any order
- [ ] Test doesn't depend on other tests
- [ ] No shared state between tests
- [ ] Cleanup properly removes side effects

**Compliance**:
- [ ] No permanent file modifications
- [ ] No external network calls
- [ ] No hardcoded credentials
- [ ] Proper temp file/directory usage
- [ ] Non-destructive testing maintained

**Documentation**:
- [ ] Test has clear docstring
- [ ] Test name is descriptive
- [ ] Complex test has comments
- [ ] Fixture documentation clear
- [ ] Linked to code being tested

**Framework**:
- [ ] Uses pytest (current standard)
- [ ] Follows existing test patterns
- [ ] Compatible with pytest.ini
- [ ] Works with continuous integration
- [ ] Doesn't require manual setup

---

## Common Questions

### Q: How do I test code that reads files?

**A**: Use temporary directories:
```python
import tempfile
from pathlib import Path

def test_read_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / 'test.json'
        config_file.write_text('{"test": true}')
        # Test your code with config_file
        result = read_config(config_file)
        assert result['test'] == True
```

### Q: How do I test code that calls external APIs?

**A**: Mock the API calls:
```python
from unittest.mock import patch

@patch('module.external_api.get_data')
def test_process_api_data(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = process_data()
    mock_api.assert_called_once()
```

### Q: How do I test CLI commands?

**A**: Use click testing or mock subprocess:
```python
from click.testing import CliRunner
from codesentinel.cli import main_command

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(main_command, ['--help'])
    assert result.exit_code == 0
```

### Q: What should I do if a test is slow?

**A**: 
1. Check if it's calling external services (mock instead)
2. Check for unnecessary loops or waits
3. Consider if it should be an integration test (separate from unit tests)
4. Profile the test to find the bottleneck
5. Optimize if possible; if not, mark as `@pytest.mark.slow`

### Q: How do I skip a test that I'm not ready for?

**A**: Use pytest markers:
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.xfail  # Expected to fail
def test_known_bug():
    pass
```

### Q: Can I test private methods (_method)?

**A**: Generally no - test public API. If you must:
1. Question if the method should be private
2. Consider if it should be extracted to separate module
3. If truly necessary, test through public interface
4. Document why testing private method is needed

---

## Running Tests

**Run all tests**:
```bash
pytest
```

**Run specific test file**:
```bash
pytest tests/test_cli.py
```

**Run with coverage**:
```bash
pytest --cov=codesentinel tests/
```

**Run only fast tests** (skip slow):
```bash
pytest -m "not slow"
```

**Run with verbose output**:
```bash
pytest -v
```

**Run and show print statements**:
```bash
pytest -s
```

---

## References & Links

**Core Documentation**:
- Global Policy: `docs/architecture/POLICY.md`
- Classification Framework: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
- General Strategy: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

**Test Framework**:
- pytest documentation: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest markers: https://docs.pytest.org/en/stable/how-to-specify-tests.html

**CodeSentinel Tests**:
- Test directory: `tests/`
- Test configuration: `pytest.ini`
- Existing tests: Study patterns in `tests/test_*.py`

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents creating and maintaining tests  
**Update Frequency**: When testing procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)
