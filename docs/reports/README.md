# CodeSentinel Reporting System

## Overview

The CodeSentinel Reporting System provides automated, scheduled report generation for security audits, performance monitoring, code quality analysis, and development progress tracking. Reports follow the SEAM Protection™ framework (Security, Efficiency, And Minimalism).

## Report Schedule

### Daily Reports (9:00 AM)

- **Security Scan** (JSON) - Vulnerability assessment and credential checks
- **Performance Health** (JSON) - System resource monitoring (CPU, memory, I/O)
- **Error Digest** (JSON) - Consolidated error reporting with trends

### Weekly Reports (Monday 9:00 AM)

- **Sprint Progress** (Markdown) - Development velocity, completed tasks, blockers
- **Code Quality Audit** (Markdown) - DRY violations, duplication analysis, import optimization
- **Dependency Security** (Markdown) - Package vulnerabilities and update recommendations
- **Performance Trends** (JSON) - Week-over-week performance analysis
- **Root Compliance** (Markdown) - Root directory policy adherence
- **ORACL Weekly Engineer** (Markdown) - Tier-2 engineer compliance + incentive snapshot stored under `MEASUREMENT_REPORTS/weekly`

### Bi-Weekly Reports (Friday 5:00 PM)

- **Security Audit** (Markdown) - Comprehensive security assessment
- **Efficiency Analysis** (Markdown) - Code reuse metrics, technical debt assessment
- **Minimalism Compliance** (Markdown) - Archive cleanup status, deprecated code identification
- **Integration Tests** (JSON) - Cross-component functionality validation

### Monthly Reports (Last Business Day 4:00 PM)

- **System Health Overview** (Markdown) - 30-day performance trends and reliability metrics
- **Codebase Metrics** (JSON) - Lines of code, complexity analysis, maintainability scores

### Quarterly Reports (Quarterly 5:00 PM)

- **ORACL Quarterly Engineer** (Markdown) - Tier-2 engineer performance review stored under `MEASUREMENT_REPORTS/quarterly`

### Release-Triggered Reports

- **Pre-Release Testing** (Markdown) - Comprehensive test coverage and regression analysis
- **Distribution & Packaging** (Markdown) - Build artifacts, metadata validation, installation testing
- **Security Assessment** (Markdown) - Final security review and vulnerability status
- **Performance Impact** (JSON) - Performance benchmarks vs. previous versions

### Feature-Triggered Reports

- **Implementation Docs** (Markdown) - Feature overview, usage examples, configuration changes
- **Code Review Summary** (Markdown) - Architecture decisions, SEAM compliance verification
- **Integration Impact** (Markdown) - Performance implications, dependency changes

## Configuration

### Main Configuration File

Location: `tools/config/reporting.json`

```json
{
  "reporting": {
    "enabled": true,
    "base_path": "docs/reports",
    "archive_path": "docs/reports/archive",
    "retention": {
      "daily": 30,
      "weekly": 26,
      "biweekly": 26,
      "monthly": -1,
      "releases": -1,
      "features": -1
    },
    "compression": {
      "enabled": true,
      "after_days": 30,
      "format": "tar.gz"
    }
  }
}
```

### Scheduler Configuration

Location: `codesentinel.json`

```json
{
  "maintenance": {
    "enabled": true,
    "daily": {
      "enabled": true,
      "schedule": "09:00"
    },
    "weekly": {
      "enabled": true,
      "schedule": "Monday 09:00"
    },
    "biweekly": {
      "enabled": true,
      "schedule": "Friday 17:00"
    },
    "monthly": {
      "enabled": true,
      "schedule": "last 16:00"
    }
  }
}
```

## Directory Structure

```text
docs/reports/
├── daily/              # Daily report outputs
├── weekly/             # Weekly report outputs
├── biweekly/           # Bi-weekly report outputs
├── monthly/            # Monthly report outputs
├── quarterly/          # Quarterly schedule outputs
├── releases/           # Release-specific reports
├── features/           # Feature-specific reports
├── INCIDENT_REPORTS/   # ORACL incident reports
├── PHASE_REPORTS/      # ORACL job completion reports
├── MEASUREMENT_REPORTS/
│   ├── weekly/         # ORACL weekly engineer reports
│   └── quarterly/      # ORACL quarterly engineer reviews
├── templates/          # Report templates (Markdown & JSON)
└── archive/            # Archived reports (retention policy)
```

## Usage

### Manual Report Generation

#### Using Workflow Script

```bash
# Generate all daily reports
python tools/codesentinel/report_workflow.py daily

# Generate all weekly reports
python tools/codesentinel/report_workflow.py weekly

# Generate quarterly ORACL engineer review
python tools/codesentinel/report_workflow.py quarterly

# Generate specific report type
python tools/codesentinel/report_workflow.py single --report-type security_scan

# Generate ORACL incident shell
python tools/codesentinel/report_workflow.py single --report-type oracl_incident_report

# Generate ORACL job completion summary
python tools/codesentinel/report_workflow.py single --report-type oracl_job_completion

# Generate release report
python tools/codesentinel/report_workflow.py single --report-type pre_release_testing --version 1.2.0

# List available report types
python tools/codesentinel/report_workflow.py list

# Clean up old reports
python tools/codesentinel/report_workflow.py cleanup
```

#### Using Python API

```python
from tools.codesentinel.report_workflow import ReportWorkflow

workflow = ReportWorkflow()

# Generate daily reports
result = workflow.generate_daily_reports()

# Generate specific report
result = workflow.generate_single_report('security_scan')

# Clean up old reports
workflow.cleanup_old_reports()
```

### Automated Scheduling

Reports are automatically generated by the CodeSentinel maintenance scheduler:

```bash
# Start scheduler (runs reports according to schedule)
codesentinel scheduler start

# Check scheduler status
codesentinel scheduler status

# Stop scheduler
codesentinel scheduler stop
```

### CLI Integration

Reports can be triggered through CLI commands:

```bash
# Run daily maintenance (includes daily reports)
codesentinel scheduler run daily

# Run weekly maintenance (includes weekly reports)
codesentinel scheduler run weekly

# Run bi-weekly maintenance (includes bi-weekly reports)
codesentinel scheduler run biweekly

# Run monthly maintenance (includes monthly reports)
codesentinel scheduler run monthly
```

## ORACall Automation

Use `tools/codesentinel/oracall_manager.py` to scaffold Tier-2 ORACall dual reports, enforce SLAs, and populate the partner feed.

```bash
# Create analytic + action stubs for a critical event
python tools/codesentinel/oracall_manager.py scaffold --title "Cache Poisoning" --engineer "oracl.ops" --severity critical

# Evaluate SLA windows without firing alerts
python tools/codesentinel/oracall_manager.py sla-check --warn-only

# Mark the analytic report complete after review
python tools/codesentinel/oracall_manager.py complete ORACALL-20251114-001 --report analytic

# Inspect the latest feed entries that satellites will ingest
python tools/codesentinel/oracall_manager.py feed --tail 3
```

Key directories/files:

- `docs/reports/oracall/events/` — JSON metadata for every event (SLA targets, distribution level, report status)
- `docs/reports/INCIDENT_REPORTS/`, `docs/reports/PHASE_REPORTS/` — Markdown stubs generated from ORACL templates with severity + due markers
- `docs/reports/feeds/oracall_feed.jsonl` — Append-only JSONL stream (schema: `docs/planning/oracall_feed_schema.json`) used for partner ingestion

Future Jira/ServiceNow pushes can be toggled later via `codesentinel.json` → `integrations.*`; until then the manager routes events through a null adapter while preserving payload structure.

Every generated Markdown document now includes ASCII metadata headers (`distribution_level`, `cache_expiry_hours`, `feed_id`, `severity`, and SLA targets) to keep file-drop consumers aligned with the JSONL feed.

> Placeholder tracking: see `docs/planning/PLACEHOLDER_REGISTRY.md` (entries PL-001–PL-005) for the current inactive adapters, signing hooks, and metadata headers that support this workflow.

## Report Retention Policy

### Automatic Cleanup

- **Daily Reports**: Retained for 30 days, then moved to archive
- **Weekly/Bi-weekly Reports**: Retained for 26 weeks (6 months), then moved to archive
- **Monthly/Quarterly Reports**: Retained indefinitely
- **Release/Feature Reports**: Retained indefinitely, compressed after 1 year

### Archive Compression

Reports older than 30 days are compressed to `.tar.gz` format to save storage space while maintaining accessibility.

## Customization

### Creating Custom Report Templates

1. Create template file in `docs/reports/templates/`
2. Use template placeholders: `{{ variable_name }}`
3. Add report configuration to `tools/config/reporting.json`

Example Markdown template:

```markdown
# Custom Report

**Generated:** {{ timestamp }}

## Summary
{{ summary }}

## Details
{{ details }}
```

### ORACL Internal Templates

The following Tier-2 templates ship with this repository for ORACL-run reviews:

| Template | Purpose | Storage Target |
|----------|---------|----------------|
| `templates/oracl_incident_report.md` | Policy or execution incident timeline, corrective actions, compliance loopback | `docs/reports/INCIDENT_REPORTS/INC-YYYYMMDD-###.md` |
| `templates/oracl_job_completion.md` | Task bundle completion summary, hallucination ledger, compliance checklist | `docs/reports/PHASE_REPORTS/JOB-YYYYMMDD-###.md` |
| `templates/oracl_weekly_engineer.md` | Weekly engineer check-in (mode usage, metrics, risks) | `docs/reports/MEASUREMENT_REPORTS/weekly/YYYY-W##-name.md` |
| `templates/oracl_quarterly_engineer.md` | Quarterly engineer performance + reward/punishment log | `docs/reports/MEASUREMENT_REPORTS/quarterly/YYYY-Q#-name.md` |

Each template includes Tier metadata, compliance checklist, and placeholders for collaboration index plus Advise/Mode levels. Reference them directly or extend per the process above.

### Adding New Report Types

1. Edit `tools/config/reporting.json`:

```json
{
  "reports": {
    "custom_report": {
      "type": "markdown",
      "template": "templates/custom_report.md",
      "description": "Description of custom report",
      "output_subdir": "INCIDENT_REPORTS"
    }
  }
}
```

> `output_subdir` is optional. When omitted, the workflow stores the report under the schedule directory (daily/weekly/etc.).

1. Add generator method in `tools/codesentinel/report_generator.py`:

```python
def _generate_custom_report(self, **kwargs) -> Dict[str, Any]:
    """Generate custom report."""
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": "Report summary",
        "details": "Report details"
    }
```

1. Register in `_generate_report_data()` method:

```python
generators = {
    # ...existing generators...
    'custom_report': self._generate_custom_report,
}
```

## Security Considerations

### Report Content

- Reports may contain sensitive information (vulnerability details, system metrics)
- Store reports in secure locations with appropriate access controls
- Consider encrypting archived reports for long-term storage

### Archive Integrity

- Archived reports undergo security scanning during compression
- Hash verification ensures archive integrity
- Tamper detection alerts on unauthorized modifications

## Troubleshooting

### Reports Not Generating

1. Check scheduler status: `codesentinel scheduler status`
2. Verify configuration: `tools/config/reporting.json` exists and is valid
3. Check logs: `codesentinel.log` for error messages
4. Ensure required permissions for `docs/reports/` directory

### Missing Report Data

- Some reports require specific CLI commands to be available
- Ensure CodeSentinel is fully installed and configured
- Check that maintenance tasks are enabled in `codesentinel.json`

### Archive Issues

1. Verify archive directory exists: `docs/reports/archive/`
2. Check available disk space for compression operations
3. Review retention policy configuration

## API Reference

### ReportGenerator Class

Located in `tools/codesentinel/report_generator.py`

**Methods:**

- `generate_report(report_type, **kwargs)` - Generate single report
- `generate_scheduled_reports(schedule_type)` - Generate all reports for schedule
- `cleanup_old_reports()` - Apply retention policy and archive old reports

### ReportWorkflow Class

Located in `tools/codesentinel/report_workflow.py`

**Methods:**

- `generate_daily_reports()` - Generate all daily reports
- `generate_weekly_reports()` - Generate all weekly reports
- `generate_biweekly_reports()` - Generate all bi-weekly reports
- `generate_monthly_reports()` - Generate all monthly reports
- `generate_quarterly_reports()` - Generate all quarterly reports (ORACL engineer reviews)
- `generate_single_report(report_type, **kwargs)` - Generate specific report
- `cleanup_old_reports()` - Clean up according to retention policy
- `list_available_reports()` - List all available report types

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Generate Weekly Reports
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9:00 AM
jobs:
  generate-reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install CodeSentinel
        run: pip install -e .
      - name: Generate Weekly Reports
        run: python tools/codesentinel/report_workflow.py weekly
      - name: Commit Reports
        run: |
          git config user.name "CodeSentinel Bot"
          git config user.email "bot@codesentinel.dev"
          git add docs/reports/
          git commit -m "📊 Weekly reports generated"
          git push
```

## Best Practices

1. **Regular Review**: Review reports weekly to identify trends and issues
2. **Action Items**: Convert report findings into actionable tasks
3. **Baseline Metrics**: Establish baseline metrics for comparison
4. **Alert Thresholds**: Configure alerts for critical findings
5. **Archive Management**: Regularly verify archive integrity
6. **Template Updates**: Keep templates synchronized with codebase changes

## Support

For issues or questions about the reporting system:

- Review this documentation
- Check `codesentinel.log` for error details
- Consult SEAM Protection™ framework documentation
- Submit issues to CodeSentinel repository

---

**SEAM Protection™** - Security, Efficiency, And Minimalism
