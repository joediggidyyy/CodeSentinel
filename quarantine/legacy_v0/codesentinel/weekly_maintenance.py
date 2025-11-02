#!/usr/bin/env python3
"""
UNC Weekly Maintenance Tasks Automation
======================================

SECURITY > EFFICIENCY > MINIMALISM

This script automates the weekly maintenance tasks defined in MAINTENANCE_WORKFLOW.md:
- Security audit
- Dependency check
- Log review
- Performance check

All tasks are platform-independent and compatible with Python 3.13/3.14.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class WeeklyMaintenance:
    """Automate weekly maintenance tasks."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
            "summary": {}
        }

    def run_security_audit(self) -> Dict[str, Any]:
        """Run security audit using existing workflow_audit.py"""
        print("🔒 Running security audit...")

        try:
            cmd = [sys.executable, "tools/monitoring/workflow_audit.py"]
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "issues_found": len(result.stdout.split('\n')) if result.stdout else 0
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Security audit timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_dependency_check(self) -> Dict[str, Any]:
        """Check for outdated dependencies in pyproject.toml"""
        print("📦 Checking dependencies...")

        try:
            # Check if pip-tools or similar is available
            outdated_packages = self._check_pip_outdated()

            # Check pyproject.toml for version constraints
            pyproject_issues = self._analyze_pyproject_versions()

            return {
                "success": True,
                "outdated_packages": outdated_packages,
                "pyproject_issues": pyproject_issues,
                "recommendations": self._generate_dependency_recommendations(outdated_packages, pyproject_issues)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_pip_outdated(self) -> List[Dict]:
        """Check for outdated pip packages"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            return []
        except Exception:
            return []

    def _analyze_pyproject_versions(self) -> List[str]:
        """Analyze pyproject.toml for version issues"""
        issues = []
        pyproject_path = self.repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            issues.append("pyproject.toml not found")
            return issues

        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)

            # Check for overly restrictive version pins
            dependencies = config.get("project", {}).get("dependencies", [])
            for dep in dependencies:
                if "==" in dep:  # Exact version pins
                    issues.append(f"Exact version pin found: {dep}")

        except ImportError:
            issues.append("tomllib not available (requires Python 3.11+)")
        except Exception as e:
            issues.append(f"Error parsing pyproject.toml: {e}")

        return issues

    def _generate_dependency_recommendations(self, outdated: List, issues: List) -> List[str]:
        """Generate dependency update recommendations"""
        recommendations = []

        if outdated:
            recommendations.append(f"Consider updating {len(outdated)} outdated packages")

        if issues:
            recommendations.extend([f"Address: {issue}" for issue in issues])

        if not outdated and not issues:
            recommendations.append("All dependencies appear up to date")

        return recommendations

    def run_log_review(self) -> Dict[str, Any]:
        """Review recent log files for errors and warnings"""
        print("📋 Reviewing logs...")

        try:
            log_files = [
                "tools/formatting/format_daemon.log",
                "tools/monitoring/scheduler/scheduler_*.log"
            ]

            issues = []
            warnings = []
            errors = []

            for log_pattern in log_files:
                for log_file in self.repo_root.glob(log_pattern):
                    if log_file.exists():
                        recent_issues = self._analyze_log_file(log_file)
                        issues.extend(recent_issues["issues"])
                        warnings.extend(recent_issues["warnings"])
                        errors.extend(recent_issues["errors"])

            return {
                "success": True,
                "total_issues": len(issues),
                "total_warnings": len(warnings),
                "total_errors": len(errors),
                "recent_issues": issues[-10:] if issues else [],  # Last 10 issues
                "recommendations": self._generate_log_recommendations(issues, warnings, errors)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_log_file(self, log_file: Path) -> Dict[str, List]:
        """Analyze a single log file for issues"""
        issues = []
        warnings = []
        errors = []

        try:
            # Read last 1000 lines to focus on recent activity
            result = subprocess.run(
                ["tail", "-1000", str(log_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if "ERROR" in line.upper() or "FAILED" in line.upper():
                        errors.append(line)
                    elif "WARNING" in line.upper() or "WARN" in line.upper():
                        warnings.append(line)
                    elif "ISSUE" in line.upper() or "PROBLEM" in line.upper():
                        issues.append(line)

        except subprocess.CalledProcessError:
            # tail command not available, read file directly
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-1000:]  # Last 1000 lines

                for line in lines:
                    line = line.strip()
                    if "ERROR" in line.upper() or "FAILED" in line.upper():
                        errors.append(line)
                    elif "WARNING" in line.upper() or "WARN" in line.upper():
                        warnings.append(line)
                    elif "ISSUE" in line.upper() or "PROBLEM" in line.upper():
                        issues.append(line)
            except Exception:
                pass

        return {"issues": issues, "warnings": warnings, "errors": errors}

    def _generate_log_recommendations(self, issues: List, warnings: List, errors: List) -> List[str]:
        """Generate log review recommendations"""
        recommendations = []

        if errors:
            recommendations.append(f"Address {len(errors)} error(s) found in logs")

        if warnings:
            recommendations.append(f"Review {len(warnings)} warning(s) found in logs")

        if issues:
            recommendations.append(f"Investigate {len(issues)} issue(s) found in logs")

        if not any([issues, warnings, errors]):
            recommendations.append("No significant issues found in recent logs")

        return recommendations

    def run_performance_check(self) -> Dict[str, Any]:
        """Run abbreviated performance check"""
        print("⚡ Running performance check...")

        try:
            cmd = [sys.executable, "tools/formatting/reformat_notebooks.py", "--abbreviated", "--dry-run"]
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
                "errors": result.stderr,
                "performance_ok": "completed successfully" in result.stdout.lower() if result.stdout else False
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Performance check timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_all_tasks(self) -> Dict[str, Any]:
        """Run all weekly maintenance tasks"""
        print("🚀 Starting UNC Weekly Maintenance")
        print(f"Repository: {self.repo_root}")
        print(f"Timestamp: {self.results['timestamp']}")
        print()

        tasks = {
            "security_audit": self.run_security_audit,
            "dependency_check": self.run_dependency_check,
            "log_review": self.run_log_review,
            "performance_check": self.run_performance_check
        }

        for task_name, task_func in tasks.items():
            print(f"Running {task_name.replace('_', ' ')}...")
            self.results["tasks"][task_name] = task_func()
            print("✓ Complete" if self.results["tasks"][task_name].get("success") else "✗ Failed")
            print()

        # Generate summary
        self._generate_summary()

        return self.results

    def _generate_summary(self):
        """Generate execution summary"""
        successful_tasks = sum(1 for task in self.results["tasks"].values() if task.get("success"))
        total_tasks = len(self.results["tasks"])

        self.results["summary"] = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "critical_issues": self._identify_critical_issues()
        }

    def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues requiring immediate attention"""
        critical = []

        # Check security audit
        security = self.results["tasks"].get("security_audit", {})
        if not security.get("success"):
            critical.append("Security audit failed - manual review required")

        # Check for errors in logs
        logs = self.results["tasks"].get("log_review", {})
        if logs.get("total_errors", 0) > 0:
            critical.append(f"{logs['total_errors']} errors found in logs")

        # Check performance
        perf = self.results["tasks"].get("performance_check", {})
        if not perf.get("success"):
            critical.append("Performance check failed")

        return critical

    def save_report(self, output_file: Optional[Path] = None) -> Path:
        """Save results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.repo_root / "tools" / "monitoring" / "reports" / f"weekly_maintenance_{timestamp}.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        return output_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="UNC Weekly Maintenance Automation")
    parser.add_argument("--task", help="Run specific task only")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent  # tools/monitoring/weekly_maintenance.py -> repo root

    maintenance = WeeklyMaintenance(repo_root)

    if args.task:
        # Run specific task
        task_map = {
            "security": maintenance.run_security_audit,
            "dependencies": maintenance.run_dependency_check,
            "logs": maintenance.run_log_review,
            "performance": maintenance.run_performance_check
        }

        if args.task not in task_map:
            print(f"Unknown task: {args.task}")
            print(f"Available tasks: {', '.join(task_map.keys())}")
            sys.exit(1)

        result = task_map[args.task]()
        if args.verbose:
            print(json.dumps(result, indent=2))
        elif result.get("success"):
            print(f"✓ {args.task.title()} completed successfully")
        else:
            print(f"✗ {args.task.title()} failed")
            sys.exit(1)
    else:
        # Run all tasks
        results = maintenance.run_all_tasks()

        # Save report
        report_file = maintenance.save_report(Path(args.output) if args.output else None)
        print(f"Report saved: {report_file}")

        # Print summary
        summary = results["summary"]
        print("\n📊 Summary:")
        print(f"  Tasks: {summary['successful_tasks']}/{summary['total_tasks']} successful")
        print(".1%")

        if summary["critical_issues"]:
            print("\n🚨 Critical Issues:")
            for issue in summary["critical_issues"]:
                print(f"  - {issue}")

        # Exit with appropriate code
        if summary["failed_tasks"] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()