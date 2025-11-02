# CodeSentinel

`SECURITY > EFFICIENCY > MINIMALISM`

A comprehensive suite of automated maintenance and security tools for development environments.
CodeSentinel provides secure, automated, self-healing capabilities for any development workflow.

## Overview

The CodeSentinel provides automated maintenance workflows that ensure development environment health, security, and performance. The system follows a multi-schedule approach with built-in alerting for critical issues.

### Key Features

- **Multi-Schedule Automation**: Daily, weekly, and monthly maintenance workflows
- **Security-First Design**: Comprehensive security audits and vulnerability detection
- **Alert System**: Multi-channel notifications for critical issues
- **Platform Independent**: Works on Windows, macOS, and Linux
- **Python 3.13/3.14 Compatible**: Modern Python with backward compatibility
- **Dependency Management**: Automated package update suggestions

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/joediggidyyy/UNC.git
cd UNC/tools

# Install the package
pip install -e .
```

### Requirements

- Python 3.13 or 3.14
- Git
- Basic system utilities (grep, find, etc.)

## Components

### MaintenanceScheduler

Central orchestration system for all maintenance tasks.

```python
from codesentinel import MaintenanceScheduler

scheduler = MaintenanceScheduler(repo_root)
results = scheduler.run_daily_maintenance()
```

### MaintenanceAlertSystem

Automated alerting for critical maintenance issues.

```python
from codesentinel import MaintenanceAlertSystem

alert_system = MaintenanceAlertSystem(repo_root)
alert_system.check_results_and_alert(results_file)
```

### WeeklyMaintenance

Comprehensive weekly security and health checks.

```python
from codesentinel import WeeklyMaintenance

weekly = WeeklyMaintenance(repo_root)
results = weekly.run_all_tasks()
```

### MonthlyMaintenance

Deep system analysis and dependency management.

```python
from codesentinel import MonthlyMaintenance

monthly = MonthlyMaintenance(repo_root)
results = monthly.run_all_tasks()
```

### DependencySuggester

Automated package update recommendations.

```python
from codesentinel import DependencySuggester

suggester = DependencySuggester(repo_root)
analysis = suggester.analyze_dependencies()
```

## Command Line Usage

### Scheduler

```bash
# Run daily maintenance
codesentinel-scheduler --schedule daily

# Run weekly maintenance
codesentinel-scheduler --schedule weekly

# Run monthly maintenance
codesentinel-scheduler --schedule monthly

# Dry run to see what would execute
codesentinel-scheduler --schedule daily --dry-run
```

### Alert System

```bash
# Test alert system
codesentinel-alert-system --test

# Check maintenance results for alerts
codesentinel-alert-system --check-results path/to/results.json
```

### Weekly Maintenance

```bash
# Run all weekly tasks
codesentinel-weekly-maintenance

# Run specific task
codesentinel-weekly-maintenance --task security
```

### Monthly Maintenance

```bash
# Run all monthly tasks
codesentinel-monthly-maintenance

# Run dependency analysis only
codesentinel-monthly-maintenance --task deps
```

### Dependency Suggester

```bash
# Analyze dependencies
codesentinel-dependency-suggester
```

## Configuration

### Alert Configuration (`tools/config/alerts.json`)

```json
{
  "enabled": true,
  "channels": {
    "console": {"enabled": true},
    "file": {"enabled": true, "log_file": "tools/monitoring/alerts.log"},
    "email": {"enabled": false},
    "slack": {"enabled": false}
  },
  "alert_rules": {
    "critical_security_issues": true,
    "task_failures": true,
    "dependency_vulnerabilities": true
  }
}
```

### Scheduler Configuration (`tools/config/scheduler.json`)

```json
{
  "version": "2.0.0",
  "schedules": {
    "daily": {
      "cron": "0 2 * * *",
      "execution_order": ["change_detection", "startup_audit", "formatting", "r_formatting", "testing", "reporting"],
      "timezone": "UTC"
    },
    "weekly": {
      "cron": "0 3 * * 1",
      "execution_order": ["weekly_maintenance"],
      "timezone": "UTC"
    },
    "monthly": {
      "cron": "0 4 1 * *",
      "execution_order": ["monthly_maintenance"],
      "timezone": "UTC"
    }
  }
}
```

## Maintenance Schedules

### Daily Schedule (2:00 AM UTC)

1. **Change Detection & Auto-Fix** - Monitors for workflow-breaking changes
2. **Startup Audit** - VS Code startup metrics and extension status
3. **Code Formatting** - Applies consistent formatting across Python/R notebooks
4. **R Code Formatting** - R code style fixes and formatting
5. **Automated Testing** - Runs test suites and validation checks
6. **Report Generation** - Generates daily maintenance and status reports

### Weekly Schedule (Monday 3:00 AM UTC)

- **Security Audit** - Comprehensive vulnerability scanning
- **Dependency Analysis** - Package version and security checks
- **Log Analysis** - Review of all system and application logs
- **Performance Validation** - System performance and resource checks
- **Configuration Verification** - Settings and policy compliance

### Monthly Schedule (1st of month 4:00 AM UTC)

- **Full Repository Scan** - Complete codebase security and quality scan
- **GitHub Integration Review** - API security and access token validation
- **Backup System Verification** - Data integrity and recovery testing
- **Dependency Analysis** - Automated package update suggestions
- **Tool Version Updates** - Automated tool and dependency updates
- **Security Policy Audit** - Comprehensive security posture assessment

## Alert Types

- **CRITICAL**: Security vulnerabilities, system compromises
- **HIGH**: Dependency vulnerabilities, major failures
- **WARNING**: Task failures, performance issues
- **INFO**: Status updates, informational alerts

## Development

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=codesentinel

# Run specific test
pytest tests/test_scheduler.py
```

### Code Quality

```bash
# Format code
black codesentinel/

# Lint code
ruff check codesentinel/

# Type checking
mypy codesentinel/
```

### Building

```bash
# Build package
python -m build

# Install locally for testing
pip install -e .
```

## Security Considerations

- All tools follow the **SECURITY > EFFICIENCY > MINIMALISM** directive
- No hardcoded credentials or tokens
- Path validation and sanitization
- Safe subprocess execution
- Comprehensive error handling
- Audit logging for all operations

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure security considerations are addressed
5. Test on multiple platforms when possible

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

- GitHub Issues: <https://github.com/joediggidyyy/UNC/issues>
- Documentation: <https://github.com/joediggidyyy/UNC/docs/MAINTENANCE_WORKFLOW.md>

---

`CodeSentinel - Secure Automated Self-Healing Development Environment`
