# CLI Refactor Audit Plan

**Created**: 2025-11-13  
**Status**: Planning Phase  
**Strategy**: Incremental, measurable improvements (NOT mass refactoring)

---

## Executive Summary

### Current State

- **Total CLI Code**: 9,627 lines across 17 files
- **Main File**: `__init__.py` at 3,486 lines (36% of total code)
- **Largest Utilities**: test_utils (1,405), update_utils (850), dev_audit_utils (499)
- **Recurring Issue**: Command hang/slowness symptoms

### Strategy

Small, measurable changes with ranked priorities. Address one pipeline at a time with clear before/after metrics.

---

## Issue Tracking: Command Hang Detection

### Current Symptoms

- User reports recurring "hanging command" issues
- Not related to orphan processes (ProcessMonitor shows zero hits)
- Previous diagnosis: File I/O overhead from metrics buffering (70% improvement achieved)
- **Question**: Are we tracking hang frequency and patterns?

### Proposed Enhancement: Hang Detection Tracking

**Goal**: Automatically detect and log slow/hanging commands

**Implementation**:

```python
# In agent_metrics.py - Add hang detection thresholds
PERFORMANCE_THRESHOLDS = {
    'normal': 1000,      # < 1s = normal
    'slow': 3000,        # 1-3s = slow
    'very_slow': 10000,  # 3-10s = very slow
    'hang': 30000        # > 30s = potential hang
}

def log_cli_command(..., duration_ms):
    # Classify performance
    if duration_ms > PERFORMANCE_THRESHOLDS['hang']:
        severity = 'critical'
        classification = 'hang'
    elif duration_ms > PERFORMANCE_THRESHOLDS['very_slow']:
        severity = 'high'
        classification = 'very_slow'
    elif duration_ms > PERFORMANCE_THRESHOLDS['slow']:
        severity = 'medium'
        classification = 'slow'
    else:
        severity = 'low'
        classification = 'normal'
    
    # Log with classification
    record['performance_classification'] = classification
    record['severity'] = severity
    
    # Alert on hangs
    if classification in ['hang', 'very_slow']:
        self.log_security_event(
            event_type='performance_degradation',
            severity=severity,
            description=f"Command '{command}' took {duration_ms}ms ({classification})",
            metadata={'args': args, 'duration_ms': duration_ms}
        )
```

**Benefits**:

- Automatic detection of slow commands
- Historical trend analysis (which commands hang most?)
- Correlation with specific arguments/conditions
- Alerts on severe performance degradation

**Effort**: 1-2 hours  
**Priority**: P0 (Immediate - diagnostic infrastructure)

---

## File Size Analysis

### Distribution

```
File                                        Lines    % of Total
==============================================================================
__init__.py                                  3486        36.2%  [CRITICAL]
test_utils.py                                1405        14.6%  [HIGH]
update_utils.py                               850         8.8%  [MEDIUM]
dev_audit_utils.py                            499         5.2%
document_formatter_cli.py                     478         5.0%
root_clean_utils.py                           442         4.6%
scan_utils.py                                 434         4.5%
doc_utils.py                                  412         4.3%
process_utils.py                              338         3.5%  [REFERENCE: Good size]
clean_utils.py                                333         3.5%
agent_utils.py                                203         2.1%
alert_utils.py                                192         2.0%
dev_audit_review.py                           187         1.9%
memory_utils.py                               140         1.5%  [REFERENCE: Good size]
dev_audit_remediation.py                      134         1.4%
command_utils.py                               90         0.9%
__main__.py                                     4         0.0%
==============================================================================
TOTAL                                        9627       100.0%
```

### Size Categories

- **REFERENCE (Good)**: 100-350 lines - `process_utils.py`, `memory_utils.py` (newer style)
- **ACCEPTABLE**: 350-500 lines - Most utility modules
- **LARGE**: 500-1000 lines - `update_utils.py`, `dev_audit_utils.py`
- **CRITICAL**: 1000+ lines - `__init__.py` (3,486), `test_utils.py` (1,405)

---

## Refactor Opportunities (Ranked)

### Priority 0: Diagnostics & Measurement (Week 1)

#### R0.1: Add Hang Detection Tracking

- **Goal**: Track slow/hanging commands automatically
- **Files**: `codesentinel/utils/agent_metrics.py`, `metrics_wrapper.py`
- **Effort**: 1-2 hours
- **Metrics**:
  - Before: No hang tracking
  - After: All commands classified (normal/slow/very_slow/hang)
  - KPI: Hang detection log entries created
- **Deliverable**: Performance classification in agent_operations.jsonl

#### R0.2: Baseline Performance Audit

- **Goal**: Measure current performance of all CLI commands
- **Method**:

  ```bash
  # Test each command 3x, record avg latency
  codesentinel status
  codesentinel memory show
  codesentinel clean --dry-run
  # etc.
  ```

- **Files**: Create `docs/metrics/baseline_performance.json`
- **Effort**: 2-3 hours
- **Deliverable**: Baseline performance report with:
  - Avg latency per command
  - Slowest commands identified
  - Hang incidents (if any)

---

### Priority 1: Low-Hanging Fruit (Week 1-2)

#### R1.1: Extract Documentation Helpers from **init**.py

- **Problem**: Lines 42-770+ in `__init__.py` are documentation utilities
- **Solution**: Move to `doc_utils.py` (currently 412 lines)
- **Functions to Extract**:
  - `verify_documentation_branding()` (42-99)
  - `verify_documentation_headers_footers()` (101-168)
  - `apply_branding_fixes()` (170-228)
  - `apply_header_footer_fixes()` (230-282)
  - `detect_project_info()` (284-432)
  - `get_header_templates()` (434-465)
  - `get_footer_templates()` (467-499)
  - `show_template_options()` (501-549)
  - `set_header_for_file()` (551-601)
  - `set_footer_for_file()` (603-652)
  - `edit_headers_interactive()` (654-712)
  - `edit_footers_interactive()` (714-770)
- **Lines Reduced**: ~730 lines from `__init__.py`
- **Effort**: 3-4 hours
- **Metrics**:
  - Before: 3,486 lines in **init**.py, 412 in doc_utils.py
  - After: 2,756 lines in **init**.py (-21%), 1,142 in doc_utils.py
- **Risk**: LOW - These are independent utility functions with clear boundaries
- **Testing**: Run `codesentinel update` commands to verify

#### R1.2: Extract Agent Context Builders from **init**.py

- **Problem**: Lines 772-855 are agent context utilities
- **Solution**: Move to `agent_utils.py` (currently 203 lines)
- **Functions to Extract**:
  - `_build_dev_audit_context()` (772-807)
  - `_build_scan_context()` (809-855)
- **Lines Reduced**: ~84 lines from `__init__.py`
- **Effort**: 1 hour
- **Metrics**:
  - Before: 2,756 lines in **init**.py (after R1.1)
  - After: 2,672 lines in **init**.py (-3%), 287 in agent_utils.py
- **Risk**: LOW - Clear separation, minimal dependencies
- **Testing**: Run `codesentinel !!!!` to verify agent context

#### R1.3: Consolidate Duplicate Import Patterns

- **Problem**: Multiple files import same utilities differently
- **Solution**: Create consistent import patterns, remove redundant imports
- **Analysis Needed**: Scan for duplicate imports across all CLI files
- **Effort**: 2-3 hours
- **Metrics**:
  - Import statements reduced by X%
  - Load time improvement (measure with timing)
- **Risk**: MEDIUM - Import changes can break functionality if not careful

---

### Priority 2: Medium Complexity (Week 2-3)

#### R2.1: Refactor Clean Command (470+ lines inline)

- **Problem**: Lines 1616-2085 in `__init__.py` are massive inline clean logic
- **Solution**: Move to `clean_utils.py` (currently 333 lines)
- **Current State**: Clean command has:
  - Inline argument processing
  - Multiple cleanup target handlers (cache, temp, logs, build, test, git, root, emojis)
  - Archive-first behavior (compliant with NON-DESTRUCTIVE policy)
  - 470+ lines of inline code
- **Functions to Extract**:
  - `get_size(path)` helper
  - `is_older_than(path, days)` helper
  - Each cleanup target handler (8 targets)
  - Archive session management
  - Git optimization handler
  - Emoji cleaning logic
- **Proposed Structure**:

  ```python
  # clean_utils.py
  class CleanupTarget:
      """Base class for cleanup targets."""
      def scan(self, workspace_root, verbose): pass
      def execute(self, items, dry_run, force, verbose): pass
  
  class CacheCleanup(CleanupTarget): pass
  class TempCleanup(CleanupTarget): pass
  class LogCleanup(CleanupTarget): pass
  # etc.
  
  def handle_clean_command(args, codesentinel):
      """Orchestrate cleanup command."""
      targets = get_enabled_targets(args)
      for target in targets:
          items = target.scan(workspace_root, args.verbose)
          target.execute(items, args.dry_run, args.force, args.verbose)
  ```

- **Lines Reduced**: ~470 lines from `__init__.py`
- **Effort**: 6-8 hours (largest refactor)
- **Metrics**:
  - Before: 2,672 lines in **init**.py, 333 in clean_utils.py
  - After: 2,202 lines in **init**.py (-17.6%), 803 in clean_utils.py
- **Risk**: MEDIUM-HIGH - Complex logic with many paths, archive-first policy critical
- **Testing**:
  - Run all clean variants: `--cache`, `--temp`, `--logs`, `--build`, `--test`, `--git`, `--root`, `--emojis`, `--all`
  - Verify archive-first behavior (NON-DESTRUCTIVE policy)
  - Check dry-run mode
  - Test force mode

#### R2.2: Refactor Integrate Command (575+ lines inline)

- **Problem**: Lines 2086-2660 in `__init__.py` are integrate command logic
- **Solution**: Create `integrate_utils.py` (new file) or enhance existing utility
- **Current State**: Complex AST parsing, scheduler injection, interactive wizard
- **Lines Reduced**: ~575 lines from `__init__.py`
- **Effort**: 5-7 hours
- **Metrics**:
  - Before: 2,202 lines in **init**.py
  - After: 1,627 lines in **init**.py (-26.1%), new integrate_utils.py
- **Risk**: HIGH - Complex code generation, AST parsing, file modification
- **Testing**: Run integrate command with various scenarios

#### R2.3: Optimize test_utils.py (1,405 lines)

- **Problem**: Second-largest file, potentially contains inline handlers
- **Analysis Needed**: Read file to identify extraction opportunities
- **Effort**: TBD after analysis
- **Risk**: TBD

---

### Priority 3: Structural Improvements (Week 3-4)

#### R3.1: Argument Parser Modularization

- **Problem**: Argument parser setup is ~1,500 lines in main() function
- **Solution**: Create parser builder functions
- **Proposed Structure**:

  ```python
  # cli/parser_builders.py
  def build_scan_parser(subparsers): pass
  def build_clean_parser(subparsers): pass
  def build_update_parser(subparsers): pass
  # etc.
  
  # __init__.py main()
  subparsers = parser.add_subparsers(...)
  build_scan_parser(subparsers)
  build_clean_parser(subparsers)
  build_update_parser(subparsers)
  ```

- **Lines Reduced**: ~500 lines from `__init__.py`
- **Effort**: 4-5 hours
- **Metrics**:
  - Before: 1,627 lines in **init**.py (after R2.1, R2.2)
  - After: 1,127 lines in **init**.py (-30.7%), new parser_builders.py
- **Risk**: LOW - Mechanical refactor, easy to test
- **Testing**: Run `codesentinel --help` and all subcommand helps

#### R3.2: Command Router Extraction

- **Problem**: Command routing is if/elif chain (~800 lines)
- **Solution**: Create command registry/dispatcher
- **Proposed Structure**:

  ```python
  # cli/command_registry.py
  COMMAND_HANDLERS = {
      'status': handle_status_command,
      'scan': handle_scan_command,
      'clean': handle_clean_command,
      # etc.
  }
  
  def dispatch_command(command, args, codesentinel):
      handler = COMMAND_HANDLERS.get(command)
      if handler:
          return handler(args, codesentinel)
      else:
          print(f"Unknown command: {command}")
  ```

- **Lines Reduced**: ~800 lines from `__init__.py`
- **Effort**: 3-4 hours
- **Metrics**:
  - Before: 1,127 lines in **init**.py
  - After: 327 lines in **init**.py (-71%), new command_registry.py
- **Risk**: LOW - Clear separation, minimal logic change
- **Testing**: Run all CLI commands to verify routing

---

### Priority 4: Style Harmonization (Week 4-5)

#### R4.1: Adopt process_utils.py Style Standards

- **Reference**: `process_utils.py` (338 lines) - Clean, modular, well-documented
- **Standards to Apply**:
  1. **Handler Functions**: Each subcommand = one handler function
  2. **Helper Functions**: Prefix with `_` for internal helpers
  3. **Docstrings**: Clear purpose, Args, Returns
  4. **ASCII-Safe Output**: No emojis in console output (use `[BRACKETED]` labels)
  5. **DHIS Integration**: Log domain activity at end of each handler
  6. **Session Memory**: Use session memory for multi-step operations
  7. **Format Helpers**: Extract formatting logic (`_format_bytes`, etc.)
- **Effort**: 2-3 hours per file (apply to ~5 files)
- **Metrics**: Style consistency score (subjective but trackable)

#### R4.2: Consistent Error Handling Patterns

- **Goal**: All commands use same error handling pattern
- **Standard Pattern**:

  ```python
  @track_cli_command('command_name')
  def handle_command(args, codesentinel):
      start_time = time.time()
      try:
          # Command logic
          result = perform_operation()
          
          # Log success
          session = SessionMemory()
          session.log_domain_activity('domain_name', {
              'action': 'operation_name',
              'success': True,
              'duration_ms': int((time.time() - start_time) * 1000),
              'metadata': {'result': result}
          })
          
          return result
      except Exception as e:
          # Log failure
          logger.error(f"Command failed: {e}")
          session = SessionMemory()
          session.log_domain_activity('domain_name', {
              'action': 'operation_name',
              'success': False,
              'duration_ms': int((time.time() - start_time) * 1000),
              'error': str(e)
          })
          raise
  ```

- **Effort**: 1-2 hours per file
- **Metrics**: Error handling consistency (% of commands following pattern)

---

## Implementation Plan

### Week 1: Diagnostics & Quick Wins

- [ ] R0.1: Add hang detection tracking (1-2h)
- [ ] R0.2: Baseline performance audit (2-3h)
- [ ] R1.1: Extract documentation helpers (3-4h)
- [ ] R1.2: Extract agent context builders (1h)

**Expected Outcome**:

- Hang tracking operational
- Baseline metrics established
- `__init__.py` reduced from 3,486 to ~2,670 lines (-23%)
- All tests passing

### Week 2: Medium Complexity Refactors

- [ ] R1.3: Consolidate duplicate imports (2-3h)
- [ ] R2.1: Refactor clean command (6-8h)

**Expected Outcome**:

- `__init__.py` reduced from 2,670 to ~2,200 lines (-17.6%)
- Clean command fully modularized
- Import overhead reduced

### Week 3: Large Refactors

- [ ] R2.2: Refactor integrate command (5-7h)
- [ ] R2.3: Analyze and optimize test_utils.py (TBD)

**Expected Outcome**:

- `__init__.py` reduced from 2,200 to ~1,625 lines (-26%)
- Complex commands extracted to utilities

### Week 4: Structural Improvements

- [ ] R3.1: Argument parser modularization (4-5h)
- [ ] R3.2: Command router extraction (3-4h)

**Expected Outcome**:

- `__init__.py` reduced from 1,625 to ~325 lines (-80% total)
- Modern architecture with clear separation

### Week 5: Style Harmonization

- [ ] R4.1: Apply process_utils style standards (10-15h across files)
- [ ] R4.2: Consistent error handling patterns (8-10h across files)

**Expected Outcome**:

- Consistent code style across all CLI modules
- Improved maintainability and readability

---

## Success Metrics

### Quantitative

- **Lines in **init**.py**: 3,486 → ~325 (-91%)
- **Avg Command Latency**: < 1000ms for all commands
- **Hang Incidents**: Tracked and trending down
- **Test Pass Rate**: 100% maintained throughout
- **Import Load Time**: Reduced by X%

### Qualitative

- **Code Readability**: Improved (subjective, team feedback)
- **Maintainability**: Easier to find and modify command logic
- **Consistency**: All commands follow same patterns
- **Documentation**: Each utility module has clear purpose

---

## Testing Strategy

### Per-Refactor Testing

1. **Unit Tests**: Extracted functions maintain same behavior
2. **Integration Tests**: Commands produce same output
3. **Performance Tests**: Latency does not increase
4. **Regression Tests**: Run full CLI test suite

### Continuous Validation

- Run `pytest` after every refactor
- Manually test affected commands
- Check metrics for performance regressions
- Verify NON-DESTRUCTIVE policy maintained (clean command)

### Final Validation (End of Week 5)

- [ ] All CLI commands working as before
- [ ] Performance baseline met or improved
- [ ] No test failures
- [ ] Code review passed
- [ ] Documentation updated

---

## Risk Management

### High-Risk Areas

1. **Clean Command** (R2.1) - Archive-first policy critical
   - Mitigation: Extensive testing of archive behavior
   - Fallback: Keep original inline implementation commented
2. **Integrate Command** (R2.2) - Complex code generation
   - Mitigation: Add integration tests for scheduler injection
   - Fallback: Defer if complexity too high
3. **Import Consolidation** (R1.3) - Can break imports
   - Mitigation: Incremental changes, test after each file
   - Fallback: Revert specific imports if issues arise

### Rollback Plan

- Each refactor = separate commit
- Keep original code commented during transition
- Tag each working state: `v1.1.2-refactor-R0.1`, etc.
- Can revert individual commits if issues arise

---

## Open Questions

1. **Hang Detection**: What threshold should trigger alerts? (Proposed: 30s)
2. **Test Utils**: Should we analyze this file now or defer? (Defer to P2 pending analysis)
3. **Integrate Command**: Can we defer this complex refactor to later? (Suggested: Yes, it's high-risk)
4. **Performance Testing**: Automate baseline comparison or manual? (Suggested: Manual initially, automate later)

---

## Next Steps

1. **Immediate** (This Session):
   - [ ] User approval of audit plan
   - [ ] Implement R0.1: Hang detection tracking (1-2h)
   - [ ] Run R0.2: Baseline performance audit (2-3h)

2. **This Week** (Week 1):
   - [ ] Execute R1.1: Extract documentation helpers (3-4h)
   - [ ] Execute R1.2: Extract agent context builders (1h)
   - [ ] Review baseline metrics, identify anomalies

3. **Planning** (Continuous):
   - Update this document with completed refactors
   - Track metrics in `docs/metrics/refactor_progress.json`
   - Report findings and adjust priorities as needed

---

**END OF AUDIT PLAN**
