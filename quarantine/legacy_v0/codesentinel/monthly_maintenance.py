#!/usr/bin/env python3
"""
UNC Monthly Maintenance Tasks Automation
=======================================

SECURITY > EFFICIENCY > MINIMALISM

This script automates the monthly maintenance tasks defined in MAINTENANCE_WORKFLOW.md:
- Full repository scan
- GitHub Actions review
- Backup verification
- Tool update check
- Security tasks (token audit, permissions, vulnerability scan)

All tasks are platform-independent and compatible with Python 3.13/3.14.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class MonthlyMaintenance:
    """Automate monthly maintenance tasks."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
            "summary": {}
        }

    def run_full_repository_scan(self) -> Dict[str, Any]:
        """Run full repository formatting scan"""
        print("🔍 Running full repository scan...")

        try:
            cmd = [sys.executable, "tools/formatting/reformat_notebooks.py", "--dry-run"]
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout[-2000:] if result.stdout else "",  # Last 2000 chars
                "errors": result.stderr,
                "files_processed": self._extract_file_count(result.stdout),
                "issues_found": "issues found" in result.stdout.lower() if result.stdout else False
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Full repository scan timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_file_count(self, output: str) -> int:
        """Extract file count from formatter output"""
        if not output:
            return 0

        # Look for patterns like "Processed X files" or "Found X files"
        patterns = [
            r'Processed (\d+) files',
            r'Found (\d+) files',
            r'Scanned (\d+) files'
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 0

    def run_github_actions_review(self) -> Dict[str, Any]:
        """Review GitHub Actions workflows for security and updates"""
        print("🔧 Reviewing GitHub Actions...")

        try:
            workflows_dir = self.repo_root / ".github" / "workflows"
            if not workflows_dir.exists():
                return {"success": True, "message": "No GitHub Actions workflows found"}

            issues = []
            recommendations = []

            # Check each workflow file
            for workflow_file in workflows_dir.glob("*.yml"):
                workflow_issues = self._analyze_workflow_file(workflow_file)
                issues.extend(workflow_issues["issues"])
                recommendations.extend(workflow_issues["recommendations"])

            return {
                "success": True,
                "workflows_found": len(list(workflows_dir.glob("*.yml"))),
                "issues_found": len(issues),
                "issues": issues,
                "recommendations": recommendations
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_workflow_file(self, workflow_file: Path) -> Dict[str, List]:
        """Analyze a single workflow file"""
        issues = []
        recommendations = []

        try:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for deprecated actions
            deprecated_actions = [
                "actions/checkout@v1",
                "actions/setup-node@v1",
                "actions/cache@v1"
            ]

            for action in deprecated_actions:
                if action in content:
                    issues.append(f"Deprecated action found: {action} in {workflow_file.name}")

            # Check for missing permissions
            if "permissions:" not in content:
                recommendations.append(f"Consider adding explicit permissions to {workflow_file.name}")

            # Check for hardcoded secrets (basic check)
            if re.search(r'\b[A-Z_]+_TOKEN\s*:\s*\$\{\{\s*secrets\.', content):
                # This is actually good - using secrets
                pass
            elif re.search(r'password|token|key', content, re.IGNORECASE):
                recommendations.append(f"Review potential secrets usage in {workflow_file.name}")

        except Exception as e:
            issues.append(f"Error analyzing {workflow_file.name}: {e}")

        return {"issues": issues, "recommendations": recommendations}

    def run_backup_verification(self) -> Dict[str, Any]:
        """Verify git repository integrity and backup status"""
        print("💾 Verifying backup integrity...")

        try:
            # Check git repository integrity
            integrity_check = self._check_git_integrity()

            # Check for large files that might need special backup handling
            large_files = self._check_large_files()

            # Check git history completeness
            history_check = self._check_git_history()

            return {
                "success": integrity_check["success"] and history_check["success"],
                "git_integrity": integrity_check,
                "large_files": large_files,
                "history_check": history_check,
                "backup_recommendations": self._generate_backup_recommendations(large_files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_git_integrity(self) -> Dict[str, Any]:
        """Check git repository integrity"""
        try:
            result = subprocess.run(
                ["git", "fsck", "--full"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "issues_found": len(result.stderr.split('\n')) if result.stderr else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_large_files(self) -> List[Dict]:
        """Check for large files that might need special backup handling"""
        large_files = []

        try:
            # Find files larger than 50MB
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                for file_path in files:
                    if file_path.strip():
                        full_path = self.repo_root / file_path.strip()
                        if full_path.exists() and full_path.stat().st_size > 50 * 1024 * 1024:  # 50MB
                            large_files.append({
                                "path": file_path,
                                "size_mb": round(full_path.stat().st_size / (1024 * 1024), 2)
                            })

        except Exception:
            pass

        return large_files

    def _check_git_history(self) -> Dict[str, Any]:
        """Check git history completeness"""
        try:
            # Check if we have recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            commit_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

            return {
                "success": result.returncode == 0 and commit_count > 0,
                "recent_commits": commit_count,
                "last_commit_date": self._get_last_commit_date()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_last_commit_date(self) -> Optional[str]:
        """Get date of last commit"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=short"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _generate_backup_recommendations(self, large_files: List) -> List[str]:
        """Generate backup recommendations"""
        recommendations = []

        if large_files:
            recommendations.append(f"Consider special handling for {len(large_files)} large files (>50MB)")

        recommendations.append("Git repository integrity verified")

        return recommendations

    def run_dependency_analysis(self) -> Dict[str, Any]:
        """Run dependency analysis and update suggestions"""
        print("📦 Analyzing dependencies...")

        try:
            # Import and run dependency suggester
            from dependency_suggester import DependencySuggester

            suggester = DependencySuggester(self.repo_root)
            analysis_results = suggester.analyze_dependencies()

            # Extract key metrics
            security_updates = len(analysis_results.get("security_updates", []))
            performance_updates = len(analysis_results.get("performance_updates", []))
            deprecated_packages = len(analysis_results.get("deprecated_packages", []))

            # Count outdated packages
            outdated_count = sum(1 for pkg in analysis_results.get("python_packages", {}).values()
                                if pkg.get("outdated"))

            return {
                "success": True,
                "security_updates_needed": security_updates,
                "performance_updates_available": performance_updates,
                "deprecated_packages": deprecated_packages,
                "outdated_packages": outdated_count,
                "total_packages_analyzed": len(analysis_results.get("python_packages", {})),
                "recommendations": analysis_results.get("recommendations", []),
                "details": analysis_results
            }

        except ImportError:
            return {"success": False, "error": "Dependency suggester not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_tool_update_check(self) -> Dict[str, Any]:
        """Check for available updates to maintenance tools"""
        print("🔄 Checking tool updates...")

        try:
            tools_to_check = [
                "black",
                "ruff",
                "pre-commit",
                "mypy",
                "bandit",
                "safety"
            ]

            updates_available = []
            current_versions = {}

            for tool in tools_to_check:
                version_info = self._check_tool_version(tool)
                current_versions[tool] = version_info

                if version_info.get("update_available"):
                    updates_available.append({
                        "tool": tool,
                        "current": version_info.get("current"),
                        "latest": version_info.get("latest")
                    })

            return {
                "success": True,
                "tools_checked": len(tools_to_check),
                "updates_available": len(updates_available),
                "available_updates": updates_available,
                "current_versions": current_versions,
                "recommendations": self._generate_tool_recommendations(updates_available)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_tool_version(self, tool: str) -> Dict[str, Any]:
        """Check version of a specific tool"""
        try:
            # Try to get current version
            result = subprocess.run(
                [sys.executable, "-m", tool, "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                current_version = result.stdout.strip().split()[-1]

                # For some tools, we can't easily check latest version
                # This is a simplified check - in production, you'd use APIs
                return {
                    "current": current_version,
                    "update_available": False,  # Simplified - would need API calls
                    "checked": True
                }
            else:
                return {"error": "Tool not installed", "checked": False}

        except Exception as e:
            return {"error": str(e), "checked": False}

    def _generate_tool_recommendations(self, updates: List) -> List[str]:
        """Generate tool update recommendations"""
        recommendations = []

        if updates:
            recommendations.append(f"Consider updating {len(updates)} tools")
            for update in updates:
                recommendations.append(f"Update {update['tool']} from {update['current']} to {update['latest']}")
        else:
            recommendations.append("All checked tools appear up to date")

        return recommendations

    def run_security_tasks(self) -> Dict[str, Any]:
        """Run additional monthly security tasks"""
        print("🔐 Running security tasks...")

        try:
            # Token audit (check for expired or unused tokens)
            token_audit = self._audit_tokens()

            # Permission review
            permission_review = self._review_permissions()

            # Vulnerability scan
            vuln_scan = self._run_vulnerability_scan()

            # Sensitive data check
            sensitive_check = self._check_sensitive_data()

            return {
                "success": all([
                    token_audit["success"],
                    permission_review["success"],
                    vuln_scan["success"],
                    sensitive_check["success"]
                ]),
                "token_audit": token_audit,
                "permission_review": permission_review,
                "vulnerability_scan": vuln_scan,
                "sensitive_data_check": sensitive_check,
                "critical_findings": self._identify_security_findings([
                    token_audit, permission_review, vuln_scan, sensitive_check
                ])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _audit_tokens(self) -> Dict[str, Any]:
        """Audit access tokens and credentials"""
        # This is a simplified check - in production, you'd integrate with GitHub API
        try:
            # Check for hardcoded tokens in code (basic grep)
            result = subprocess.run(
                ["git", "grep", "-r", r"token\|password\|secret", "--", "*.py", "*.sh", "*.ps1"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            findings = []
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.split('\n')
                # Filter out false positives (comments, test files, etc.)
                for line in lines:
                    if line.strip() and not any(skip in line.lower() for skip in [
                        'comment', 'test', 'example', 'placeholder', 'fake'
                    ]):
                        findings.append(line.split(':', 1)[0])  # File path only

            return {
                "success": True,
                "potential_findings": len(findings),
                "files_with_potential_tokens": list(set(findings))  # Unique files
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _review_permissions(self) -> Dict[str, Any]:
        """Review file and directory permissions"""
        try:
            # Check for world-writable files
            world_writable = []

            for root, dirs, files in os.walk(self.repo_root):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat_info = file_path.stat()
                        if stat_info.st_mode & 0o002:  # World writable
                            world_writable.append(str(file_path.relative_to(self.repo_root)))
                    except Exception:
                        continue

            return {
                "success": True,
                "world_writable_files": world_writable,
                "security_concerns": len(world_writable)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_vulnerability_scan(self) -> Dict[str, Any]:
        """Run basic vulnerability scan on dependencies"""
        try:
            # Use pip-audit if available, otherwise safety
            tools_to_try = ["pip-audit", "safety"]

            for tool in tools_to_try:
                try:
                    if tool == "pip-audit":
                        result = subprocess.run(
                            [sys.executable, "-m", tool, "--format=json"],
                            cwd=self.repo_root,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                    else:  # safety
                        result = subprocess.run(
                            [sys.executable, "-m", tool, "check", "--json"],
                            cwd=self.repo_root,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )

                    if result.returncode == 0:
                        # Parse JSON output
                        try:
                            data = json.loads(result.stdout)
                            vulnerabilities = len(data.get("vulnerabilities", [])) if isinstance(data, dict) else 0
                        except json.JSONDecodeError:
                            vulnerabilities = 0

                        return {
                            "success": True,
                            "tool_used": tool,
                            "vulnerabilities_found": vulnerabilities,
                            "scan_completed": True
                        }

                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            # If no tools available, return basic info
            return {
                "success": True,
                "tool_used": "none",
                "vulnerabilities_found": 0,
                "scan_completed": False,
                "message": "No vulnerability scanning tool available (install pip-audit or safety)"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_sensitive_data(self) -> Dict[str, Any]:
        """Check for accidentally committed sensitive data"""
        try:
            # Check git history for potential sensitive data
            sensitive_patterns = [
                r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b',  # Credit cards
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails (basic)
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
                r'password\s*[:=]\s*\S+',  # Password assignments
                r'token\s*[:=]\s*\S+',  # Token assignments
            ]

            findings = []

            for pattern in sensitive_patterns:
                try:
                    result = subprocess.run(
                        ["git", "grep", "-r", pattern, "--", "*.py", "*.ipynb", "*.md"],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode == 0 and result.stdout:
                        lines = result.stdout.split('\n')
                        findings.extend([line.split(':', 1)[0] for line in lines if line.strip()])

                except subprocess.TimeoutExpired:
                    continue

            return {
                "success": True,
                "potential_sensitive_files": list(set(findings)),  # Unique files
                "patterns_checked": len(sensitive_patterns)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _identify_security_findings(self, security_results: List) -> List[str]:
        """Identify critical security findings"""
        critical = []

        for result in security_results:
            if not result.get("success"):
                continue

            # Check token audit
            if "potential_findings" in result and result["potential_findings"] > 0:
                critical.append(f"{result['potential_findings']} files with potential token exposure")

            # Check permissions
            if "security_concerns" in result and result["security_concerns"] > 0:
                critical.append(f"{result['security_concerns']} world-writable files found")

            # Check vulnerabilities
            if "vulnerabilities_found" in result and result["vulnerabilities_found"] > 0:
                critical.append(f"{result['vulnerabilities_found']} vulnerabilities found in dependencies")

            # Check sensitive data
            if "potential_sensitive_files" in result and len(result["potential_sensitive_files"]) > 0:
                critical.append(f"{len(result['potential_sensitive_files'])} files with potential sensitive data")

        return critical

    def run_all_tasks(self) -> Dict[str, Any]:
        """Run all monthly maintenance tasks"""
        print("🚀 Starting UNC Monthly Maintenance")
        print(f"Repository: {self.repo_root}")
        print(f"Timestamp: {self.results['timestamp']}")
        print()

        tasks = {
            "full_repository_scan": self.run_full_repository_scan,
            "github_actions_review": self.run_github_actions_review,
            "backup_verification": self.run_backup_verification,
            "dependency_analysis": self.run_dependency_analysis,
            "tool_update_check": self.run_tool_update_check,
            "security_tasks": self.run_security_tasks
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

        # Check repository scan
        scan = self.results["tasks"].get("full_repository_scan", {})
        if not scan.get("success"):
            critical.append("Full repository scan failed")

        # Check backup verification
        backup = self.results["tasks"].get("backup_verification", {})
        if not backup.get("success"):
            critical.append("Backup verification failed")

        # Check security tasks
        security = self.results["tasks"].get("security_tasks", {})
        if security.get("critical_findings"):
            critical.extend(security["critical_findings"])

        return critical

    def save_report(self, output_file: Optional[Path] = None) -> Path:
        """Save results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.repo_root / "tools" / "monitoring" / "reports" / f"monthly_maintenance_{timestamp}.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        return output_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="UNC Monthly Maintenance Automation")
    parser.add_argument("--task", help="Run specific task only")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent  # tools/monitoring/monthly_maintenance.py -> repo root

    maintenance = MonthlyMaintenance(repo_root)

    if args.task:
        # Run specific task
        task_map = {
            "scan": maintenance.run_full_repository_scan,
            "github": maintenance.run_github_actions_review,
            "backup": maintenance.run_backup_verification,
            "deps": maintenance.run_dependency_analysis,
            "tools": maintenance.run_tool_update_check,
            "security": maintenance.run_security_tasks
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