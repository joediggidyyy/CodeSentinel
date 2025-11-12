# [AGENT-USE] Tools Satellite Instructions

> **Purpose:** Agent-intended operational instructions for tools satellite domain.
> This file provides domain-specific guidance for agent remediation and maintenance operations.

# Tools Satellite Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: Maintenance automation, scheduler tasks, background jobs in tools/ directory  
**Target Users**: Agents implementing automated maintenance workflows  
**Last Updated**: November 7, 2025  
**Version**: 1.0

---

## Quick Authority Reference

**Who can create, modify, delete automation tasks?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create scheduler task | Agent | Yes (user verification) |
| Create maintenance job | Agent | Yes (user verification) |
| Modify task timing | Agent | Yes (user verification) |
| Modify task logic | Agent | No (bug fixes), Yes (major changes) |
| Delete task | Agent | Yes (explicit user instruction) |
| Add task dependency | Agent | Yes (user verification) |
| Change task priority | Agent | Yes (user verification) |
| Add alerting to task | Agent | No |
| Modify alert thresholds | Agent | Yes (impacts operations) |
| Schedule new job type | Agent | Yes (user verification) |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Authority matrices for infrastructure code

---

## Domain Overview

The `tools/` directory contains CodeSentinel automation infrastructure including:

- **Scheduler** (`scheduler.py`) - Task scheduling and execution
- **Maintenance Jobs** - Daily, weekly, monthly tasks
- **Background Processes** - Long-running automation
- **Configuration** (`tools/config/`) - Automation settings and policies
- **Monitoring** - Task execution tracking and alerting

**Core Scheduler Tasks** (Always Running):

1. **Daily Maintenance** - Configuration validation, cleanup
2. **Security Scan** - Dependency vulnerability checking (weekly)
3. **Dependency Update** - Check for updates and patches (weekly)
4. **Backup** - Archive backup operations (daily)
5. **Config Validation** - Policy compliance checking (daily)
6. **Metadata Update** - Archive metadata refresh (daily)

**Key Principles for This Domain**:

- Non-disruptive (background execution)
- Comprehensive logging (all actions logged)
- Error handling (failures logged and reported)
- Scheduling precision (timers accurate)
- Task isolation (independent execution)
- Alerting integration (failures alert users)
- Policy compliance (verify SECURITY > EFFICIENCY > MINIMALISM)

---

## Common Procedures

### Procedure 1: Add New Scheduler Task

**When**: New automated operation needed (daily, weekly, or monthly)

**Steps**:

1. **Verify Authority**: Get user approval for new task 

2. **Define Task Requirements**:
   - What should the task do?
   - How often should it run? (daily, weekly, monthly)
   - What time(s) should it run?
   - What's the timeout (max execution time)?
   - What resources will it use?
   - What can fail safely?

3. **Design Task Implementation**:
   - Create function: `def task_[name](config_manager, alert_manager):`
   - Parameters: Config manager, alert manager (standard)
   - Return: Execution result (success/failure with details)
   - Error handling: All exceptions caught and logged
   - Logging: Important events logged with timestamps

4. **Implement Task Function**:

   ```python
   def task_my_maintenance(config_manager, alert_manager):
       """
       Perform my maintenance operation.
       
       Runs: Daily at 2 AM
       Timeout: 5 minutes
       """
       logger = logging.getLogger(__name__)
       try:
           logger.info("Starting my maintenance task")
           # Perform work here
           result = perform_operation()
           logger.info(f"Completed successfully: {result}")
           return {"status": "success", "details": result}
       except Exception as e:
           logger.error(f"Task failed: {e}")
           alert_manager.send_alert("Task Failed", f"my_maintenance: {e}")
           return {"status": "failed", "error": str(e)}
   ```

5. **Register Task with Scheduler**:
   - Add to tasks registry in scheduler
   - Define schedule: `schedule.every().day.at("02:00").do(task_my_maintenance)`
   - Set timeout: `timeout = 300  # 5 minutes`
   - Document in scheduler configuration

6. **Add Configuration**:
   - Add to `tools/config/scheduling.json`
   - Document schedule, timeout, dependencies
   - Document success criteria
   - Document failure conditions

7. **Add Monitoring**:
   - Add to metrics tracking
   - Define success condition
   - Define alert conditions
   - Configure alert recipients

8. **Testing**:
   - Test in isolation (without scheduler)
   - Test with actual data/conditions
   - Test error conditions
   - Verify logging output
   - Test alert generation
   - Verify task timeout works

9. **Deployment**:
   - Add to scheduler on startup
   - Monitor first few executions
   - Verify timing accurate
   - Verify logging complete
   - Adjust if needed

10. **Validation**:
    - Task executes on schedule 
    - Logging shows all actions 
    - Alerts trigger appropriately 
    - No resource leaks 
    - Complies with policies 

11. **Commit**:
    - Message: `feat(scheduler): add [task name] task`
    - Include task implementation
    - Include configuration
    - Include tests

---

### Procedure 2: Modify Task Schedule or Timeout

**When**: Task needs to run more/less often or timeout is incorrect

**Steps**:

1. **Verify Authority**: Get user verification for timing changes 

2. **Analyze Current Performance**:
   - How long does task typically take?
   - What's the current schedule?
   - How often is it timing out?
   - What's the resource usage pattern?

3. **Plan Changes**:
   - New schedule: Define exact time or interval
   - New timeout: Calculate based on performance
   - Document rationale for changes
   - Identify impact on other tasks

4. **Update Scheduler Config**:
   - Modify `tools/config/scheduling.json`
   - Update schedule definition
   - Update timeout value
   - Document previous values

5. **Update Task Implementation** (if needed):
   - Adjust task to meet new timeout
   - Optimize if necessary
   - Maintain functionality
   - No shortcuts that reduce quality

6. **Testing**:
   - Run task manually with new timeout
   - Verify completes within timeout
   - Monitor several executions with new schedule
   - Verify no conflicts with other tasks
   - Check resource usage

7. **Gradual Rollout**:
   - Test in non-production if possible
   - Monitor first week of changes
   - Watch for issues or conflicts
   - Adjust if necessary
   - Finalize configuration

8. **Documentation**:
   - Update schedule documentation
   - Note why change was made
   - Document new timing
   - Add to CHANGELOG

9. **Validation**:
    - Task runs on new schedule 
    - Completes within timeout 
    - No conflicts with other tasks 
    - Logging accurate 
    - Alerts still working 

10. **Commit**:
    - Message: `ops(scheduler): adjust [task] schedule/timeout`
    - Document old and new values
    - Note rationale

---

### Procedure 3: Debug Failed Scheduler Task

**When**: Task fails or doesn't produce expected results

**Steps**:

1. **Locate Task Logs**:
   - Check scheduler logs
   - Find task execution entries
   - Collect error messages
   - Note timing of failures
   - Identify pattern (always, sometimes, when?)

2. **Understand Failure**:
   - What was the task trying to do?
   - What went wrong?
   - Is it a logic error or environment issue?
   - Did task timeout?
   - Are dependencies missing?

3. **Reproduce Issue**:
   - Run task manually (if safe)
   - Use same inputs as scheduled run
   - Verify error reproduces
   - Document reproduction steps

4. **Diagnose Root Cause**:
   - Check logs for stack traces
   - Check dependencies (files, services, permissions)
   - Check configuration (values correct?)
   - Check resource availability (disk, memory)
   - Check for external factor impact

5. **Implement Fix**:
   - Fix identified issue
   - Update error handling if needed
   - Improve logging for visibility
   - Consider edge cases
   - Don't remove features

6. **Test Fix**:
   - Run task manually with fix
   - Verify it completes successfully
   - Run full test suite
   - Monitor several scheduled runs
   - Watch for side effects

7. **Alerting Adjustment** (if needed):
   - Update alert conditions if appropriate
   - Adjust thresholds if too sensitive
   - Ensure alerts still trigger on real failures
   - Document alert logic

8. **Validation**:
    - Task completes successfully 
    - Logging shows correct output 
    - No error alerts 
    - Dependencies available 
    - No timeout issues 

9. **Commit**:
    - Message: `fix(scheduler): resolve [task] failure`
    - Document root cause
    - Note fix applied
    - Reference logs if helpful

---

### Procedure 4: Add Task Dependencies or Prerequisites

**When**: Task requires other operations to complete first

**Steps**:

1. **Verify Authority**: Get user verification for dependency changes 

2. **Identify Dependencies**:
   - What must run before this task?
   - What's the execution order?
   - How is failure in dependency handled?
   - Are there circular dependencies?

3. **Design Dependency Handling**:
   - Hard dependency: Wait for completion
   - Soft dependency: Proceed but log warning
   - Conditional: Only run if dependency succeeded
   - Timeout: How long to wait for dependency?

4. **Implement Dependency Check**:
   - Add logic to check prerequisite status
   - Verify prerequisite completed successfully
   - Handle timeout scenarios
   - Log dependency status
   - Return appropriate status

5. **Update Scheduler Config**:
   - Document dependencies in config
   - Define execution order
   - Set timeout for dependency wait
   - Define failure handling

6. **Testing**:
   - Test with dependency succeeded
   - Test with dependency failed
   - Test with dependency timeout
   - Test execution order
   - Monitor integrated execution

7. **Documentation**:
   - Document dependency relationship
   - Explain why dependency exists
   - Document how failures handled
   - Add to task documentation

8. **Validation**:
    - Dependency respected 
    - Correct execution order 
    - Failure handling correct 
    - Logging shows dependencies 
    - No deadlocks 

9. **Commit**:
    - Message: `ops(scheduler): add dependency for [task]`
    - Document dependency relationship

---

## Quick Scheduler Decision Tree

**What are you doing?**

- Adding new task? → Use "Add New Scheduler Task" procedure
- Changing task schedule? → Use "Modify Schedule/Timeout" procedure
- Task failed? → Use "Debug Failed Task" procedure
- Adding dependencies? → Use "Add Dependencies" procedure
- Monitoring task? → Check logs and metrics

**What type of task?**

- One-time operation? → Don't use scheduler (run manually)
- Daily operation? → Use `schedule.every().day.at("HH:MM")`
- Weekly operation? → Use `schedule.every().monday.at("HH:MM")`
- Monthly operation? → Use date-based scheduling
- Continuous polling? → Use background thread (not scheduler)

**What's the scope?**

- CodeSentinel-internal? → Implement in scheduler
- System-level? → May need cron/systemd
- External service? → May need API integration
- User-triggered? → Create CLI command instead

---

## Task Configuration Reference

**Standard Task Configuration** (`tools/config/scheduling.json`):

```json
{
  "tasks": [
    {
      "name": "daily_maintenance",
      "type": "scheduled",
      "schedule": "every().day.at('02:00')",
      "timeout": 300,
      "enabled": true,
      "logging": "info",
      "alerts_on_failure": true,
      "alert_recipients": ["admin@example.com"],
      "description": "Daily maintenance and cleanup operations"
    }
  ]
}
```

---

## Validation Checklist (Before Adding Task)

**Task Design**:

- [ ] Task purpose clearly defined
- [ ] Schedule requirements understood
- [ ] Resource requirements estimated
- [ ] Timeout calculated appropriately
- [ ] Success criteria defined

**Implementation**:

- [ ] Task function created with proper signature
- [ ] Error handling comprehensive
- [ ] Logging includes important events
- [ ] Config parameters used (not hardcoded)
- [ ] No credentials in code

**Testing**:

- [ ] Task runs standalone successfully
- [ ] Task completes within timeout
- [ ] Error handling tested
- [ ] Logging verified
- [ ] No resource leaks

**Integration**:

- [ ] Task registered with scheduler
- [ ] Configuration added
- [ ] Dependencies resolved
- [ ] No conflicts with other tasks
- [ ] Alert logic configured

**Compliance**:

- [ ] Policy compliance verified
- [ ] Non-disruptive execution
- [ ] Proper error reporting
- [ ] Audit trail maintained
- [ ] Documentation complete

---

## Common Scheduler Questions

### Q: How do I run a task on demand instead of scheduled?

**A**: Two approaches:

1. Create CLI command that calls task function directly
2. Manual trigger: Stop scheduler, run task, restart scheduler
3. Better: Create command-line option to run any task

### Q: What if a task fails consistently?

**A**: Debugging steps:

1. Check logs for actual error
2. Run task manually to reproduce
3. Verify dependencies are available
4. Check configuration values
5. Verify permissions and access
6. Adjust timeout if too aggressive
7. Report if unresolvable

### Q: Can multiple tasks run simultaneously?

**A**: By default:

- Python scheduler is single-threaded
- Tasks run sequentially
- Each waits for previous to complete
- If you need parallel: Use threading/multiprocessing (advanced)

### Q: How do I stop a runaway task?

**A**: Built-in safeguards:

1. Task timeout (default: task max time)
2. Process limits (OS-enforced)
3. Manual intervention: Stop scheduler, investigate
4. Monitor for long-running tasks

### Q: What should I log in a task?

**A**: Log these events:

1. Task start: "Starting [task name]"
2. Important milestones: "Completed phase X"
3. Errors: Complete error with context
4. Task end: "Completed successfully" or "Failed"
5. Summary: Key metrics/results

---

## References & Links

**Core Documentation**:

- Global Policy: `docs/architecture/POLICY.md`
- Classification Framework: `docs/architecture/DOCUMENT_CLASSIFICATION.md`
- General Strategy: `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md`

**Configuration Files**:

- Scheduling Config: `tools/config/scheduling.json`
- Alerts Config: `tools/config/alerts.json`
- Policies Config: `tools/config/policies.json`

**Scheduler Implementation**:

- Scheduler: `codesentinel/utils/scheduler.py`
- Config Manager: `codesentinel/utils/config.py`
- Alert Manager: `codesentinel/utils/alerts.py`

**Related Tasks**:

- Daily Maintenance: `codesentinel/utils/scheduler.py` - `_run_daily_tasks()`
- Weekly Tasks: `codesentinel/utils/scheduler.py` - `_run_weekly_tasks()`
- Monthly Tasks: `codesentinel/utils/scheduler.py` - `_run_monthly_tasks()`

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents managing automated maintenance  
**Update Frequency**: When scheduler procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)
