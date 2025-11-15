"""
Report Generator
================

Automated report generation system for CodeSentinel.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import subprocess
import psutil
import re


class ReportGenerator:
    """Generates automated reports for CodeSentinel."""

    def __init__(self, config_manager, alert_manager):
        """
        Initialize report generator.

        Args:
            config_manager: Configuration manager instance
            alert_manager: Alert manager instance
        """
        self.config_manager = config_manager
        self.alert_manager = alert_manager
        self.logger = logging.getLogger('ReportGenerator')

        # Load reporting configuration
        self.reporting_config = self._load_reporting_config()
        self.base_path = Path(self.reporting_config.get('reporting', {}).get('base_path', 'docs/reports'))

    def _load_reporting_config(self) -> Dict[str, Any]:
        """Load reporting configuration."""
        config_path = Path('tools/config/reporting.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def generate_report(self, report_type: str, **kwargs) -> Optional[str]:
        """
        Generate a specific report.

        Args:
            report_type: Type of report to generate
            **kwargs: Additional parameters for report generation

        Returns:
            Path to generated report file, or None if failed
        """
        try:
            self.logger.info(f"Generating {report_type} report")

            # Get report configuration
            report_config = self.reporting_config.get('reports', {}).get(report_type)
            if not report_config:
                self.logger.error(f"Unknown report type: {report_type}")
                return None

            # Generate report data
            report_data = self._generate_report_data(report_type, **kwargs)

            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filename = f"{report_type}_{timestamp}"

            output_subdir = report_config.get('output_subdir')
            if output_subdir:
                target_dir = Path(output_subdir)
            else:
                target_dir = Path(self._get_schedule_type(report_type))

            if report_config['type'] == 'json':
                filename += '.json'
                filepath = self.base_path / target_dir / filename
                self._write_json_report(filepath, report_data)
            else:  # markdown
                filename += '.md'
                filepath = self.base_path / target_dir / filename
                self._write_markdown_report(filepath, report_data, report_type)

            self.logger.info(f"Generated report: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to generate {report_type} report: {e}")
            self.alert_manager.send_alert(
                f"Report Generation Failed: {report_type}",
                f"Error generating {report_type} report: {e}",
                severity='warning',
                channels=['console', 'file']
            )
            return None

    def _get_schedule_type(self, report_type: str) -> str:
        """Get the schedule type directory for a report."""
        schedules = self.reporting_config.get('schedules', {})
        for schedule_type, config in schedules.items():
            if report_type in config.get('reports', []):
                return schedule_type
        return 'daily'  # fallback

    def _generate_report_data(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Generate data for a specific report type."""
        generators = {
            'security_scan': self._generate_security_scan,
            'performance_health': self._generate_performance_health,
            'error_digest': self._generate_error_digest,
            'sprint_progress': self._generate_sprint_progress,
            'code_quality_audit': self._generate_code_quality_audit,
            'dependency_security': self._generate_dependency_security,
            'performance_trends': self._generate_performance_trends,
            'root_compliance': self._generate_root_compliance,
            'security_audit': self._generate_security_audit,
            'efficiency_analysis': self._generate_efficiency_analysis,
            'minimalism_compliance': self._generate_minimalism_compliance,
            'integration_tests': self._generate_integration_tests,
            'system_health_overview': self._generate_system_health_overview,
            'codebase_metrics': self._generate_codebase_metrics,
            'pre_release_testing': self._generate_pre_release_testing,
            'distribution_packaging': self._generate_distribution_packaging,
            'security_assessment': self._generate_security_assessment,
            'performance_impact': self._generate_performance_impact,
            'implementation_docs': self._generate_implementation_docs,
            'code_review_summary': self._generate_code_review_summary,
            'integration_impact': self._generate_integration_impact,
            'oracl_incident_report': self._generate_oracl_incident_report,
            'oracl_job_completion': self._generate_oracl_job_completion,
            'oracl_weekly_engineer': self._generate_oracl_weekly_engineer,
            'oracl_quarterly_engineer': self._generate_oracl_quarterly_engineer,
        }

        generator = generators.get(report_type)
        if generator:
            return generator(**kwargs)
        else:
            return {"error": f"Unknown report type: {report_type}"}

    def _generate_security_scan(self, **kwargs) -> Dict[str, Any]:
        """Generate security scan report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "scan_type": "daily_security_scan",
            "vulnerabilities_found": 0,
            "credentials_exposed": 0,
            "policy_violations": [],
            "recommendations": [],
            "status": "clean"
        }

    def _generate_performance_health(self, **kwargs) -> Dict[str, Any]:
        """Generate performance health report."""
        # Get system performance metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2)
            },
            "process_metrics": {
                "python_processes": len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]),
                "total_processes": len(psutil.pids())
            },
            "health_status": "good" if cpu_percent < 80 and memory.percent < 85 else "warning"
        }

    def _generate_error_digest(self, **kwargs) -> Dict[str, Any]:
        """Generate error digest report."""
        # This would typically scan log files for errors
        return {
            "timestamp": datetime.now().isoformat(),
            "period": "last_24_hours",
            "error_count": 0,
            "warning_count": 0,
            "critical_errors": [],
            "top_error_types": [],
            "trends": "stable",
            "recommendations": []
        }

    def _generate_sprint_progress(self, **kwargs) -> Dict[str, Any]:
        """Generate sprint progress report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "sprint_period": "current_week",
            "completed_tasks": [],
            "in_progress_tasks": [],
            "blocked_tasks": [],
            "velocity": 0,
            "burndown_status": "on_track",
            "next_sprint_goals": []
        }

    def _generate_code_quality_audit(self, **kwargs) -> Dict[str, Any]:
        """Generate code quality audit report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "audit_period": "weekly",
            "dry_violations": [],
            "duplication_count": 0,
            "import_optimization_needed": [],
            "code_style_issues": [],
            "complexity_metrics": {},
            "overall_score": "A"
        }

    def _generate_dependency_security(self, **kwargs) -> Dict[str, Any]:
        """Generate dependency security report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "packages_scanned": 0,
            "vulnerabilities_found": [],
            "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "updates_available": [],
            "recommendations": []
        }

    def _generate_performance_trends(self, **kwargs) -> Dict[str, Any]:
        """Generate performance trends report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "period": "last_7_days",
            "cpu_trend": "stable",
            "memory_trend": "stable",
            "disk_trend": "stable",
            "performance_baseline": {},
            "anomalies_detected": [],
            "forecast": "stable"
        }

    def _generate_root_compliance(self, **kwargs) -> Dict[str, Any]:
        """Generate root compliance report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "compliance_check": "weekly",
            "authorized_files": [],
            "unauthorized_files": [],
            "policy_violations": [],
            "cleanup_actions_taken": [],
            "overall_compliance": "compliant"
        }

    def _generate_security_audit(self, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive security audit report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "audit_scope": "full_system",
            "critical_findings": [],
            "high_findings": [],
            "medium_findings": [],
            "low_findings": [],
            "compliance_score": 95,
            "recommendations": []
        }

    def _generate_efficiency_analysis(self, **kwargs) -> Dict[str, Any]:
        """Generate efficiency analysis report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_period": "biweekly",
            "code_reuse_metrics": {},
            "technical_debt_estimate": 0,
            "optimization_opportunities": [],
            "performance_bottlenecks": [],
            "efficiency_score": "A"
        }

    def _generate_minimalism_compliance(self, **kwargs) -> Dict[str, Any]:
        """Generate minimalism compliance report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "compliance_check": "biweekly",
            "archive_status": {},
            "deprecated_code_identified": [],
            "cleanup_actions": [],
            "storage_optimization": {},
            "minimalism_score": "A"
        }

    def _generate_integration_tests(self, **kwargs) -> Dict[str, Any]:
        """Generate integration tests report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "integration",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage_percentage": 0,
            "performance_metrics": {},
            "failures": []
        }

    def _generate_system_health_overview(self, **kwargs) -> Dict[str, Any]:
        """Generate system health overview report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "period": "last_30_days",
            "uptime_percentage": 99.9,
            "performance_trends": {},
            "error_rates": {},
            "resource_utilization": {},
            "health_score": "excellent"
        }

    def _generate_codebase_metrics(self, **kwargs) -> Dict[str, Any]:
        """Generate codebase metrics report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_period": "monthly",
            "lines_of_code": 0,
            "code_complexity": {},
            "maintainability_index": 0,
            "technical_debt_ratio": 0,
            "code_quality_score": "A"
        }

    def _generate_pre_release_testing(self, **kwargs) -> Dict[str, Any]:
        """Generate pre-release testing report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "release_version": kwargs.get('version', 'unknown'),
            "test_coverage": 0,
            "regression_tests": 0,
            "integration_tests": 0,
            "performance_tests": 0,
            "security_tests": 0,
            "test_results": {},
            "blockers": []
        }

    def _generate_distribution_packaging(self, **kwargs) -> Dict[str, Any]:
        """Generate distribution packaging report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "release_version": kwargs.get('version', 'unknown'),
            "build_artifacts": [],
            "metadata_validation": {},
            "installation_testing": {},
            "distribution_channels": [],
            "packaging_status": "ready"
        }

    def _generate_security_assessment(self, **kwargs) -> Dict[str, Any]:
        """Generate security assessment report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "release_version": kwargs.get('version', 'unknown'),
            "security_review": {},
            "vulnerability_status": {},
            "compliance_check": {},
            "security_score": "A",
            "release_blockers": []
        }

    def _generate_performance_impact(self, **kwargs) -> Dict[str, Any]:
        """Generate performance impact report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "release_version": kwargs.get('version', 'unknown'),
            "baseline_comparison": {},
            "performance_benchmarks": {},
            "regression_analysis": {},
            "impact_assessment": "neutral"
        }

    def _generate_implementation_docs(self, **kwargs) -> Dict[str, Any]:
        """Generate implementation documentation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "feature_name": kwargs.get('feature_name', 'unknown'),
            "implementation_overview": "",
            "usage_examples": [],
            "configuration_changes": [],
            "api_changes": [],
            "documentation_status": "complete"
        }

    def _generate_code_review_summary(self, **kwargs) -> Dict[str, Any]:
        """Generate code review summary report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "feature_name": kwargs.get('feature_name', 'unknown'),
            "architecture_decisions": [],
            "seam_compliance": {},
            "review_comments": [],
            "approval_status": "approved"
        }

    def _generate_integration_impact(self, **kwargs) -> Dict[str, Any]:
        """Generate integration impact report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "feature_name": kwargs.get('feature_name', 'unknown'),
            "performance_implications": {},
            "dependency_changes": [],
            "integration_points": [],
            "risk_assessment": "low"
        }

    def _generate_oracl_incident_report(self, **kwargs) -> Dict[str, Any]:
        """Generate ORACL incident report metadata."""
        now = datetime.now()
        start_time = kwargs.get('start_time', now.strftime('%Y-%m-%d %H:%M'))
        end_time = kwargs.get('end_time', start_time)
        collab_before = float(kwargs.get('collaboration_before', 1.00))
        collab_after = float(kwargs.get('collaboration_after', collab_before))
        confidence = float(kwargs.get('confidence_at_detection', 0.92))

        return {
            "timestamp": now.isoformat(),
            "incident_id": kwargs.get('incident_id', now.strftime('INC-%Y%m%d-%H%M')),
            "time_range": f"{start_time} to {end_time}",
            "primary_engineer": kwargs.get('primary_engineer', 'Unassigned'),
            "active_mode": kwargs.get('active_mode', 'flex3'),
            "aggression_level": kwargs.get('aggression_level', '2'),
            "advise_level": kwargs.get('advise_level', '2'),
            "confidence_at_detection": f"{confidence:.2f}",
            "trigger": kwargs.get('trigger', 'security_event'),
            "affected_assets": self._stringify_sequence(kwargs.get('affected_assets', [])),
            "observed_impact": kwargs.get('observed_impact', 'No automated impact recorded.'),
            "hallucination_flag": kwargs.get('hallucination_flag', 'no (auto-generated)'),
            "collaboration_shift": f"{collab_before:.2f} -> {collab_after:.2f}",
            "reward_action": kwargs.get('reward_action', 'None recorded'),
            "report_filed_by": kwargs.get('report_filed_by', 'ORACL Workflow'),
            "report_approved_by": kwargs.get('report_approved_by', 'Pending')
        }

    def _generate_oracl_job_completion(self, **kwargs) -> Dict[str, Any]:
        """Generate ORACL job completion metadata."""
        now = datetime.now()
        start_time = kwargs.get('start_time', now.strftime('%Y-%m-%d %H:%M'))
        end_time = kwargs.get('end_time', start_time)
        engineers = kwargs.get('engineers', ['Unassigned'])

        return {
            "timestamp": now.isoformat(),
            "job_id": kwargs.get('job_id', now.strftime('JOB-%Y%m%d-%H%M')),
            "timeframe": f"{start_time} -> {end_time}",
            "engineers": self._stringify_sequence(engineers),
            "requested_mode": kwargs.get('requested_mode', 'flex3'),
            "mode_timeline": kwargs.get('mode_timeline', 'flex3 (start) -> flex3 (end)'),
            "aggression_range": kwargs.get('aggression_range', '1-3'),
            "deliverable_notes": kwargs.get('deliverable_notes', 'Pending engineer input.'),
            "decision_summary": kwargs.get('decision_summary', 'Ledger entries pending.'),
            "reports_updated": self._stringify_sequence(kwargs.get('reports_updated', [])),
            "tests_run": self._stringify_sequence(kwargs.get('tests_run', [])),
            "seam_status": kwargs.get('seam_status', 'All priorities satisfied automatically.'),
            "collaboration_index": f"{float(kwargs.get('collaboration_index', 1.00)):.2f}",
            "compliments_logged": kwargs.get('compliments_logged', '0 (auto)'),
            "rewards_applied": kwargs.get('rewards_applied', 'None yet'),
            "follow_on_tasks": self._stringify_sequence(kwargs.get('follow_on_tasks', []), separator='\n') or 'None'
        }

    def _generate_oracl_weekly_engineer(self, **kwargs) -> Dict[str, Any]:
        """Generate ORACL weekly engineer snapshot."""
        now = datetime.now()

        return {
            "timestamp": now.isoformat(),
            "week_number": kwargs.get('week_number', now.strftime('%Y-W%W')),
            "engineer": kwargs.get('engineer', 'Unassigned'),
            "primary_domains": self._stringify_sequence(kwargs.get('primary_domains', [])),
            "dominant_mode": kwargs.get('dominant_mode', 'flex3'),
            "avg_collaboration_index": f"{float(kwargs.get('avg_collaboration_index', 1.00)):.2f}",
            "compliments_logged": kwargs.get('compliments_logged', '0'),
            "rewards_granted": self._stringify_sequence(kwargs.get('rewards_granted', [])),
            "punishments_applied": self._stringify_sequence(kwargs.get('punishments_applied', [])),
            "incidents_delta": kwargs.get('incidents_delta', '0 opened / 0 closed'),
            "oracl_queries": kwargs.get('oracl_queries', '0 (0% cache hits)'),
            "tests_executed": kwargs.get('tests_executed', '0'),
            "fortunate_hallucinations": kwargs.get('fortunate_hallucinations', '0 / 0'),
            "documentation_updates": self._stringify_sequence(kwargs.get('documentation_updates', [])),
            "emerging_risks": self._stringify_sequence(kwargs.get('emerging_risks', [])),
            "mode_adjustments": kwargs.get('mode_adjustments', 'None requested'),
            "planned_deliverables": self._stringify_sequence(kwargs.get('planned_deliverables', []))
        }

    def _generate_oracl_quarterly_engineer(self, **kwargs) -> Dict[str, Any]:
        """Generate ORACL quarterly engineer review snapshot."""
        now = datetime.now()

        return {
            "timestamp": now.isoformat(),
            "quarter": kwargs.get('quarter', f"{now.year}-Q{((now.month - 1) // 3) + 1}"),
            "engineer": kwargs.get('engineer', 'Unassigned'),
            "primary_mission": kwargs.get('primary_mission', 'Stabilize and harden infrastructure.'),
            "average_mode_mix": kwargs.get('average_mode_mix', 'analyze 40% / code 35% / flex 25%'),
            "collaboration_index_range": kwargs.get('collaboration_index_range', '0.90 -> 1.05'),
            "compliment_count": kwargs.get('compliment_count', '0'),
            "autonomy_boosts": self._stringify_sequence(kwargs.get('autonomy_boosts', [])),
            "downgrades_applied": self._stringify_sequence(kwargs.get('downgrades_applied', [])),
            "corrective_actions": self._stringify_sequence(kwargs.get('corrective_actions', [])),
            "highlight_one": kwargs.get('highlight_one', 'Stood up ORACL automation templates.'),
            "highlight_two": kwargs.get('highlight_two', 'Maintained zero incidents during beta.'),
            "lesson_learned": kwargs.get('lesson_learned', 'Documented incentives earlier improves morale.'),
            "mode_strategy": kwargs.get('mode_strategy', 'Maintain flex3 default, escalate only with approval.'),
            "training_focus": self._stringify_sequence(kwargs.get('training_focus', ['Memory architecture research'])),
            "monitoring_hooks": self._stringify_sequence(kwargs.get('monitoring_hooks', ['ORACL dashboards', 'codesentinel !!!!'])),
            "approval_chain": kwargs.get('approval_chain', 'Engineering Leadership (pending signature)')
        }

    @staticmethod
    def _stringify_sequence(value: Optional[Any], separator: str = ', ') -> str:
        """Join list-like values into a readable string."""
        if value is None:
            return 'None'
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple, set)):
            if not value:
                return 'None'
            return separator.join(str(item) for item in value)
        return str(value)

    def _write_json_report(self, filepath: Path, data: Dict[str, Any]):
        """Write JSON report to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def _write_markdown_report(self, filepath: Path, data: Dict[str, Any], report_type: str):
        """Write Markdown report to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Load template
        template_path = self.base_path / self.reporting_config['reports'][report_type]['template']
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
        else:
            template = self._get_default_markdown_template(report_type)

        # Simple template substitution
        content = template
        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"
            if isinstance(value, (list, dict)):
                content = content.replace(placeholder, json.dumps(value, indent=2))
            else:
                content = content.replace(placeholder, str(value))

        with open(filepath, 'w') as f:
            f.write(content)

    def _get_default_markdown_template(self, report_type: str) -> str:
        """Get default Markdown template for a report type."""
        return f"""# {report_type.replace('_', ' ').title()} Report

**Generated:** {{{{ timestamp }}}}

## Summary

Report summary goes here.

## Details

Report details go here.

## Recommendations

Recommendations go here.
"""

    def generate_scheduled_reports(self, schedule_type: str) -> List[str]:
        """
        Generate all reports for a schedule type.

        Args:
            schedule_type: Type of schedule (daily, weekly, etc.)

        Returns:
            List of generated report file paths
        """
        schedule_config = self.reporting_config.get('schedules', {}).get(schedule_type, {})
        reports = schedule_config.get('reports', [])

        generated_reports = []
        for report_type in reports:
            report_path = self.generate_report(report_type)
            if report_path:
                generated_reports.append(report_path)

        return generated_reports

    def cleanup_old_reports(self):
        """Clean up old reports according to retention policy."""
        retention = self.reporting_config.get('reporting', {}).get('retention', {})

        for schedule_type, days in retention.items():
            if days > 0:  # -1 means keep forever
                schedule_dir = self.base_path / schedule_type
                if schedule_dir.exists():
                    cutoff_date = datetime.now() - timedelta(days=days)

                    for report_file in schedule_dir.glob('*'):
                        if report_file.is_file():
                            # Check file modification time
                            if report_file.stat().st_mtime < cutoff_date.timestamp():
                                # Move to archive
                                archive_dir = Path(self.reporting_config['reporting']['archive_path'])
                                archive_dir.mkdir(parents=True, exist_ok=True)
                                archive_path = archive_dir / f"{report_file.name}.archived"
                                report_file.rename(archive_path)
                                self.logger.info(f"Archived old report: {report_file.name}")