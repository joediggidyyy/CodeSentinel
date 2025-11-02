#!/usr/bin/env python3
"""
CodeSentinel Maintenance Scheduler
==================================

SECURITY > EFFICIENCY > MINIMALISM

This script coordinates the maintenance workflow, ensuring that change detection
and auto-fixes run BEFORE any other scheduled tasks to maintain workflow integrity.

Execution Order:
1. Change Detection & Auto-Fix (this script ensures it runs first)
2. Formatting workflows
3. Testing and validation
4. Reporting and cleanup
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

class MaintenanceScheduler:
    """
    Coordinates daily maintenance tasks with proper dependency management.

    Ensures change detection runs first to fix any broken workflows before
    other maintenance tasks execute.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.log_dir = repo_root / "tools" / "monitoring" / "scheduler"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Load configuration
        self.config = self.load_config()

        # Task definitions
        self.tasks = self.define_tasks()

    def setup_logging(self):
        """Setup logging for scheduler"""
        log_file = self.log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"

        self.logger = logging.getLogger('MaintenanceScheduler')
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def load_config(self) -> Dict:
        """Load scheduler configuration"""
        config_file = self.repo_root / "tools" / "config" / "scheduler.json"

        default_config = {
            "schedules": {
                "daily": {
                    "execution_order": [
                        "change_detection",
                        "startup_audit",
                        "formatting",
                        "r_formatting",
                        "testing",
                        "reporting"
                    ],
                    "enabled": True,
                    "cron_expression": "0 2 * * *",  # Daily at 2 AM
                    "timezone": "America/New_York"
                },
                "weekly": {
                    "execution_order": [
                        "weekly_maintenance"
                    ],
                    "enabled": True,
                    "cron_expression": "0 3 * * 1",  # Weekly on Monday at 3 AM
                    "timezone": "America/New_York"
                },
                "monthly": {
                    "execution_order": [
                        "monthly_maintenance"
                    ],
                    "enabled": True,
                    "cron_expression": "0 4 1 * *",  # Monthly on 1st at 4 AM
                    "timezone": "America/New_York"
                }
            },
            "task_timeout_seconds": 1800,  # 30 minutes
            "fail_fast": True,
            "continue_on_error": False,
            "log_level": "INFO",
            "notifications": {
                "enabled": False,
                "email_on_failure": False,
                "slack_webhook_url": None
            }
        }

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Deep merge user config
                self._deep_update(default_config, user_config)
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid config file: {config_file}")

        return default_config

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def define_tasks(self) -> Dict[str, Dict]:
        """Define maintenance tasks and their dependencies"""
        return {
            "change_detection": {
                "name": "Change Detection & Auto-Fix",
                "script": "tools/monitoring/change_detection.py",
                "description": "Detect filesystem changes and apply automatic fixes",
                "priority": 1,
                "timeout": 600,  # 10 minutes
                "required": True,
                "args": []
            },
            "startup_audit": {
                "name": "Startup Audit",
                "script": "tools/monitoring/startup_audit.ps1",
                "description": "Audit VS Code startup metrics, extensions, and environment status",
                "priority": 2,
                "timeout": 180,  # 3 minutes
                "required": False,
                "args": []
            },
            "formatting": {
                "name": "Code Formatting",
                "script": "tools/formatting/reformat_notebooks.py",
                "description": "Apply consistent code formatting across repository",
                "priority": 3,
                "timeout": 900,  # 15 minutes
                "required": False,
                "args": ["--dry-run=false"]
            },
            "r_formatting": {
                "name": "R Code Formatting",
                "script": "tools/formatting/run_fix_r_cells.py",
                "description": "Apply R code formatting and style fixes",
                "priority": 4,
                "timeout": 600,  # 10 minutes
                "required": False,
                "args": ["--review", "--git-commit"]
            },
            "testing": {
                "name": "Automated Testing",
                "script": "tools/monitoring/run_tests.py",
                "description": "Run automated test suites",
                "priority": 5,
                "timeout": 1200,  # 20 minutes
                "required": False,
                "args": []
            },
            "reporting": {
                "name": "Generate Reports",
                "script": "tools/monitoring/generate_daily_report.py",
                "description": "Generate daily maintenance and status reports",
                "priority": 6,
                "timeout": 300,  # 5 minutes
                "required": False,
                "args": []
            },
            "weekly_maintenance": {
                "name": "Weekly Maintenance Suite",
                "script": "tools/monitoring/weekly_maintenance.py",
                "description": "Run comprehensive weekly maintenance tasks (security, dependencies, logs, performance)",
                "priority": 7,
                "timeout": 1800,  # 30 minutes
                "required": False,
                "args": []
            },
            "monthly_maintenance": {
                "name": "Monthly Maintenance Suite",
                "script": "tools/monitoring/monthly_maintenance.py",
                "description": "Run comprehensive monthly maintenance tasks (full scan, GitHub review, backup, security)",
                "priority": 8,
                "timeout": 3600,  # 60 minutes
                "required": False,
                "args": []
            }
        }

    def check_task_dependencies(self, task_name: str) -> bool:
        """Check if task dependencies are satisfied"""
        task = self.tasks[task_name]

        # Change detection must always run first
        if task_name == "change_detection":
            return True

        # Check if change detection has run recently
        state_file = self.repo_root / "tools" / "monitoring" / "change_detection" / "detection_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                last_run = state.get("last_run")
                if last_run:
                    last_run_dt = datetime.fromisoformat(last_run)
                    # Must have run within last 24 hours
                    if datetime.now() - last_run_dt < timedelta(hours=24):
                        return True
            except Exception:
                pass

        self.logger.warning(f"Change detection dependency not satisfied for {task_name}")
        return False

    def run_task(self, task_name: str) -> Tuple[bool, str]:
        """Run a specific maintenance task"""
        task = self.tasks[task_name]

        if not self.check_task_dependencies(task_name):
            return False, f"Dependencies not satisfied for {task_name}"

        script_path = self.repo_root / task["script"]
        if not script_path.exists():
            return False, f"Script not found: {script_path}"

        self.logger.info(f"Starting task: {task['name']}")

        try:
            # Prepare command based on script type
            if script_path.suffix.lower() == '.ps1':
                # PowerShell script
                cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + task["args"]
            else:
                # Python script (default)
                cmd = [sys.executable, str(script_path)] + task["args"]

            # Run with timeout
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=task["timeout"]
            )

            if result.returncode == 0:
                self.logger.info(f"Task completed successfully: {task['name']}")
                return True, result.stdout
            else:
                error_msg = f"Task failed: {task['name']} - {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"Task timed out: {task['name']}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Task execution failed: {task['name']} - {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def run_daily_maintenance(self) -> Dict[str, Any]:
        """Run the complete daily maintenance workflow"""
        self.logger.info("Starting UNC Daily Maintenance Workflow")
        self.logger.info(f"Repository: {self.repo_root}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks_run": [],
            "success_count": 0,
            "failure_count": 0,
            "total_runtime_seconds": 0,
            "errors": []
        }

        start_time = datetime.now()

        # Execute tasks in priority order
        for task_name in self.config["execution_order"]:
            if task_name not in self.tasks:
                self.logger.warning(f"Unknown task: {task_name}")
                continue

            task_start = datetime.now()
            success, output = self.run_task(task_name)
            task_end = datetime.now()

            task_result = {
                "task": task_name,
                "name": self.tasks[task_name]["name"],
                "success": success,
                "runtime_seconds": (task_end - task_start).total_seconds(),
                "output": output if len(output) < 1000 else output[:1000] + "..."
            }

            results["tasks_run"].append(task_result)

            if success:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["errors"].append(output)

                # Fail fast if configured
                if self.config.get("fail_fast", True):
                    self.logger.error("Failing fast due to task failure")
                    break

        end_time = datetime.now()
        results["total_runtime_seconds"] = (end_time - start_time).total_seconds()

        # Log summary
        self.log_summary(results)

        return results

    def log_summary(self, results: Dict):
        """Log execution summary"""
        self.logger.info("=== Daily Maintenance Summary ===")
        self.logger.info(f"Total runtime: {results['total_runtime_seconds']:.1f} seconds")
        self.logger.info(f"Tasks completed: {results['success_count']}")
        self.logger.info(f"Tasks failed: {results['failure_count']}")

        for task_result in results["tasks_run"]:
            status = "✓" if task_result["success"] else "✗"
            self.logger.info(f"  {status} {task_result['name']} ({task_result['runtime_seconds']:.1f}s)")

        if results["errors"]:
            self.logger.error("Errors encountered:")
            for error in results["errors"]:
                self.logger.error(f"  - {error[:200]}...")

    def save_results(self, results: Dict):
        """Save execution results to file"""
        results_file = self.log_dir / f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"Results saved to: {results_file}")
            return results_file
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return None

    def run_alert_system(self, results: Dict):
        """Run alert system to check for critical issues"""
        try:
            # Import alert system here to avoid circular imports
            from alert_system import MaintenanceAlertSystem

            alert_system = MaintenanceAlertSystem(self.repo_root)

            # Save results first to get the file path
            results_file = self.save_results(results)
            if not results_file:
                self.logger.error("Failed to save results for alert system")
                return

            # Run alert check
            success = alert_system.check_results_and_alert(results_file)
            if success:
                self.logger.info("Alert system completed successfully")
            else:
                self.logger.warning("Alert system encountered issues")

        except ImportError:
            self.logger.warning("Alert system not available - install required dependencies")
        except Exception as e:
            self.logger.error(f"Failed to run alert system: {e}")

    def run_weekly_maintenance(self) -> Dict[str, Any]:
        """Run the complete weekly maintenance workflow"""
        self.logger.info("Starting UNC Weekly Maintenance Workflow")
        self.logger.info(f"Repository: {self.repo_root}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "schedule": "weekly",
            "tasks_run": [],
            "success_count": 0,
            "failure_count": 0,
            "total_runtime_seconds": 0,
            "errors": []
        }

        start_time = datetime.now()

        # Execute weekly tasks
        weekly_tasks = self.config["schedules"]["weekly"]["execution_order"]

        for task_name in weekly_tasks:
            if task_name not in self.tasks:
                self.logger.warning(f"Unknown task: {task_name}")
                continue

            task_start = datetime.now()
            success, output = self.run_task(task_name)
            task_end = datetime.now()

            task_result = {
                "task": task_name,
                "name": self.tasks[task_name]["name"],
                "success": success,
                "runtime_seconds": (task_end - task_start).total_seconds(),
                "output": output if len(output) < 1000 else output[:1000] + "..."
            }

            results["tasks_run"].append(task_result)

            if success:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["errors"].append(output)

        end_time = datetime.now()
        results["total_runtime_seconds"] = (end_time - start_time).total_seconds()

        # Log summary
        self.log_summary(results)

        return results

    def run_monthly_maintenance(self) -> Dict[str, Any]:
        """Run the complete monthly maintenance workflow"""
        self.logger.info("Starting UNC Monthly Maintenance Workflow")
        self.logger.info(f"Repository: {self.repo_root}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "schedule": "monthly",
            "tasks_run": [],
            "success_count": 0,
            "failure_count": 0,
            "total_runtime_seconds": 0,
            "errors": []
        }

        start_time = datetime.now()

        # Execute monthly tasks
        monthly_tasks = self.config["schedules"]["monthly"]["execution_order"]

        for task_name in monthly_tasks:
            if task_name not in self.tasks:
                self.logger.warning(f"Unknown task: {task_name}")
                continue

            task_start = datetime.now()
            success, output = self.run_task(task_name)
            task_end = datetime.now()

            task_result = {
                "task": task_name,
                "name": self.tasks[task_name]["name"],
                "success": success,
                "runtime_seconds": (task_end - task_start).total_seconds(),
                "output": output if len(output) < 1000 else output[:1000] + "..."
            }

            results["tasks_run"].append(task_result)

            if success:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["errors"].append(output)

        end_time = datetime.now()
        results["total_runtime_seconds"] = (end_time - start_time).total_seconds()

        # Log summary
        self.log_summary(results)

        return results

    def save_results(self, results: Dict):
        """Save execution results to file"""
        results_file = self.log_dir / f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"Results saved to: {results_file}")
            return results_file
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return None

    def run_alert_system(self, results: Dict):
        """Run alert system to check for critical issues"""
        try:
            # Import alert system here to avoid circular imports
            from alert_system import MaintenanceAlertSystem

            alert_system = MaintenanceAlertSystem(self.repo_root)

            # Save results first to get the file path
            results_file = self.save_results(results)
            if not results_file:
                self.logger.error("Failed to save results for alert system")
                return

            # Run alert check
            success = alert_system.check_results_and_alert(results_file)
            if success:
                self.logger.info("Alert system completed successfully")
            else:
                self.logger.warning("Alert system encountered issues")

        except ImportError:
            self.logger.warning("Alert system not available - install required dependencies")
        except Exception as e:
            self.logger.error(f"Failed to run alert system: {e}")

def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent.parent  # tools/codesentinel/scheduler.py -> repo root

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="CodeSentinel Maintenance Scheduler")
    parser.add_argument("--task", help="Run specific task only")
    parser.add_argument("--schedule", choices=["daily", "weekly", "monthly"],
                       default="daily", help="Maintenance schedule to run (default: daily)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be run without executing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Initialize scheduler
    scheduler = MaintenanceScheduler(repo_root)

    if args.verbose:
        scheduler.logger.setLevel(logging.DEBUG)

    if args.task:
        # Run specific task
        if args.task not in scheduler.tasks:
            print(f"Unknown task: {args.task}")
            print(f"Available tasks: {', '.join(scheduler.tasks.keys())}")
            sys.exit(1)

        if args.dry_run:
            print(f"Would run task: {args.task}")
            print(f"Description: {scheduler.tasks[args.task]['description']}")
            print(f"Script: {scheduler.tasks[args.task]['script']}")
            print(f"Args: {scheduler.tasks[args.task]['args']}")
        else:
            success, output = scheduler.run_task(args.task)
            if success:
                print(f"Task completed successfully: {args.task}")
            else:
                print(f"Task failed: {args.task}")
                print(f"Error: {output}")
                sys.exit(1)
    else:
        # Run maintenance based on schedule
        if args.dry_run:
            schedule_config = scheduler.config["schedules"][args.schedule]
            print(f"Would run {args.schedule} maintenance workflow:")
            for task_name in schedule_config["execution_order"]:
                if task_name in scheduler.tasks:
                    task = scheduler.tasks[task_name]
                    print(f"  {task['priority']}. {task['name']} - {task['script']}")
                else:
                    print(f"  ? Unknown task: {task_name}")
        else:
            results = None
            # Run the appropriate maintenance schedule
            if args.schedule == "daily":
                results = scheduler.run_daily_maintenance()
            elif args.schedule == "weekly":
                results = scheduler.run_weekly_maintenance()
            elif args.schedule == "monthly":
                results = scheduler.run_monthly_maintenance()
            else:
                print(f"Unknown schedule: {args.schedule}")
                sys.exit(1)

            if results:
                scheduler.save_results(results)

                # Run alert system to check for critical issues
                scheduler.run_alert_system(results)

                # Exit with appropriate code
                if results["failure_count"] > 0:
                    sys.exit(1)
                else:
                    sys.exit(0)

if __name__ == "__main__":
    main()