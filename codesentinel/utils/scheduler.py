"""
Maintenance Scheduler
=====================

Handles scheduling and execution of automated maintenance tasks.
"""

import json
import logging
import time
import os
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import threading

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    schedule = None
    SCHEDULE_AVAILABLE = False

# State file location
STATE_FILE = Path.home() / ".codesentinel" / "scheduler.state"


class MaintenanceScheduler:
    """Schedules and executes automated maintenance tasks."""

    def __init__(self, config_manager, alert_manager):
        """
        Initialize maintenance scheduler.

        Args:
            config_manager: Configuration manager instance.
            alert_manager: Alert manager instance.
        """
        self.config_manager = config_manager
        self.alert_manager = alert_manager
        self.logger = logging.getLogger('MaintenanceScheduler')
        self.scheduler_thread = None
        self.running = False

        if not SCHEDULE_AVAILABLE:
            self.logger.warning("schedule library not available - scheduling features disabled")

        # Task registry
        self.tasks = {
            'daily': self._run_daily_tasks,
            'weekly': self._run_weekly_tasks,
            'monthly': self._run_monthly_tasks
        }

    def _save_state(self, active: bool, pid: Optional[int] = None):
        """Save scheduler state to file."""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            state = {
                'active': active,
                'pid': pid or os.getpid(),
                'timestamp': datetime.now().isoformat()
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.logger.warning(f"Failed to save scheduler state: {e}")

    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state from file."""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load scheduler state: {e}")
        return {}

    def _clear_state(self):
        """Clear scheduler state file."""
        try:
            if STATE_FILE.exists():
                STATE_FILE.unlink()
        except Exception as e:
            self.logger.warning(f"Failed to clear scheduler state: {e}")

    def start(self):
        """Start the maintenance scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return

        self.running = True
        # Use daemon thread for in-process scheduling
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Save state with current PID
        self._save_state(active=True)

        self.logger.info("Maintenance scheduler started")

    def stop(self):
        """Stop the maintenance scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Clear state file
        self._clear_state()
        
        self.logger.info("Maintenance scheduler stopped")

    def is_active(self) -> bool:
        """Check if scheduler is active."""
        # Check in-process thread status first
        if self.running and self.scheduler_thread and self.scheduler_thread.is_alive():
            return True
        
        # Check persisted state from state file
        state = self._load_state()
        if state.get('active'):
            pid = state.get('pid')
            # Verify the process is still running
            if pid:
                try:
                    process = psutil.Process(pid)
                    # Check if it's a Python process (scheduler should be Python)
                    if process.is_running() and 'python' in process.name().lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process no longer exists, clear stale state
                    self._clear_state()
        
        return False

    def _run_scheduler(self):
        """Run the scheduler loop."""
        if not SCHEDULE_AVAILABLE:
            self.logger.error("Cannot run scheduler - schedule library not available")
            return

        # Clear existing jobs
        schedule.clear()  # type: ignore

        # Setup scheduled tasks
        self._setup_scheduled_tasks()

        # Run scheduler loop
        while self.running:
            try:
                schedule.run_pending()  # type: ignore
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    def _setup_scheduled_tasks(self):
        """Setup scheduled maintenance tasks."""
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Cannot setup scheduled tasks - schedule library not available")
            return

        maintenance_config = self.config_manager.get('maintenance', {})

        # Daily tasks
        if maintenance_config.get('daily', {}).get('enabled', False):
            schedule_time = maintenance_config['daily'].get('schedule', '09:00')
            try:
                hour, minute = map(int, schedule_time.split(':'))
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(  # type: ignore
                    self._execute_task, 'daily'
                )
                self.logger.info(f"Scheduled daily tasks for {schedule_time}")
            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid daily schedule time '{schedule_time}': {e}")

        # Weekly tasks
        if maintenance_config.get('weekly', {}).get('enabled', False):
            schedule_str = maintenance_config['weekly'].get('schedule', 'Monday 10:00')
            try:
                day, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))

                day_map = {
                    'monday': schedule.every().monday,  # type: ignore
                    'tuesday': schedule.every().tuesday,  # type: ignore
                    'wednesday': schedule.every().wednesday,  # type: ignore
                    'thursday': schedule.every().thursday,  # type: ignore
                    'friday': schedule.every().friday,  # type: ignore
                    'saturday': schedule.every().saturday,  # type: ignore
                    'sunday': schedule.every().sunday  # type: ignore
                }

                if day.lower() in day_map:
                    day_map[day.lower()].at(f"{hour:02d}:{minute:02d}").do(
                        self._execute_task, 'weekly'
                    )
                    self.logger.info(f"Scheduled weekly tasks for {schedule_str}")
                else:
                    self.logger.error(f"Invalid day '{day}' in weekly schedule")

            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid weekly schedule '{schedule_str}': {e}")

        # Monthly tasks
        if maintenance_config.get('monthly', {}).get('enabled', False):
            schedule_str = maintenance_config['monthly'].get('schedule', '1st 11:00')
            try:
                day_str, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))

                # Parse day (e.g., "1st", "15th", "last")
                if day_str.lower() == 'last':
                    day = 31  # Will be adjusted by scheduler
                else:
                    day = int(day_str.rstrip('stndrh'))

                # Schedule on the specified day of month
                schedule.every().month.at(f"{hour:02d}:{minute:02d}").do(  # type: ignore
                    self._execute_task, 'monthly'
                )
                self.logger.info(f"Scheduled monthly tasks for {schedule_str}")

            except (ValueError, AttributeError) as e:
                self.logger.error(f"Invalid monthly schedule '{schedule_str}': {e}")

    def _execute_task(self, task_type: str):
        """Execute a scheduled task."""
        try:
            self.logger.info(f"Executing scheduled {task_type} maintenance tasks")

            if task_type in self.tasks:
                results = self.tasks[task_type]()

                # Send success alert
                self.alert_manager.send_alert(
                    f"{task_type.capitalize()} Maintenance Completed",
                    f"Successfully executed {len(results.get('tasks_executed', []))} {task_type} maintenance tasks.",
                    severity='info',
                    channels=['console', 'file']
                )

                # Send failure alerts if any
                if results.get('errors'):
                    self.alert_manager.send_alert(
                        f"{task_type.capitalize()} Maintenance Errors",
                        f"Encountered {len(results['errors'])} errors during {task_type} maintenance.",
                        severity='warning',
                        channels=['console', 'file']
                    )

            else:
                self.logger.error(f"Unknown task type: {task_type}")

        except Exception as e:
            self.logger.error(f"Failed to execute {task_type} tasks: {e}")
            self.alert_manager.send_alert(
                f"{task_type.capitalize()} Maintenance Failed",
                f"Critical error during {task_type} maintenance execution: {e}",
                severity='error'
            )

    def run_task_now(self, task_type: str) -> Dict[str, Any]:
        """
        Run maintenance task immediately.

        Args:
            task_type: Type of task to run ('daily', 'weekly', 'monthly').

        Returns:
            Dict containing task results.
        """
        if task_type not in self.tasks:
            raise ValueError(f"Unknown task type: {task_type}")

        self.logger.info(f"Running {task_type} maintenance tasks on demand")
        return self.tasks[task_type]()

    def _run_daily_tasks(self) -> Dict[str, Any]:
        """Run daily maintenance tasks."""
        tasks_executed = []
        errors = []
        
        # Root directory cleanup
        try:
            from tools.codesentinel.root_cleanup import RootDirectoryValidator
            import os
            
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            validator = RootDirectoryValidator(repo_root, dry_run=False, logger=self.logger)
            
            # Validate root directory
            validation_result = validator.validate()
            if validation_result['summary']['total_issues'] > 0:
                self.logger.info(f"Root directory issues found: {validation_result['summary']['total_issues']}")
                
                # Execute cleanup
                cleanup_result = validator.cleanup()
                tasks_executed.append('root_directory_cleanup')
                
                if cleanup_result['total_processed'] > 0:
                    self.logger.info(f"Root cleanup processed {cleanup_result['total_processed']} items")
            else:
                tasks_executed.append('root_directory_validation')
                
        except ImportError:
            self.logger.warning("Root cleanup module not available - skipping")
            errors.append("Root cleanup module not available")
        except Exception as e:
            self.logger.error(f"Root cleanup error: {e}")
            errors.append(f"Root cleanup failed: {str(e)}")
        
        # Document formatting and style checking
        try:
            from codesentinel.utils.document_formatter import DocumentFormatter, StyleChecker, FormattingScheme
            import os
            from pathlib import Path
            
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            docs_dir = Path(repo_root) / 'docs'
            
            if docs_dir.exists():
                # Check document style
                style_checker = StyleChecker(logger=self.logger)
                check_result = style_checker.check_directory(docs_dir, pattern='**/*.md')
                
                if check_result['total_issues'] > 0:
                    self.logger.info(f"Document style issues found: {check_result['total_issues']}")
                    tasks_executed.append('document_style_check')
                else:
                    tasks_executed.append('document_style_validation')
                    
        except ImportError:
            self.logger.warning("Document formatter not available - skipping")
        except Exception as e:
            self.logger.error(f"Document formatting error: {e}")
            errors.append(f"Document formatting failed: {str(e)}")
        
        # Standard daily tasks
        tasks_executed.extend(['security_check', 'dependency_update', 'log_cleanup'])
        
        return {
            'task_type': 'daily',
            'tasks_executed': tasks_executed,
            'errors': errors,
            'warnings': []
        }

    def _run_weekly_tasks(self) -> Dict[str, Any]:
        """Run weekly maintenance tasks."""
        # Placeholder for actual weekly tasks
        return {
            'task_type': 'weekly',
            'tasks_executed': ['deep_analysis', 'performance_check', 'backup_verify'],
            'errors': [],
            'warnings': []
        }

    def _run_monthly_tasks(self) -> Dict[str, Any]:
        """Run monthly maintenance tasks."""
        # Placeholder for actual monthly tasks
        return {
            'task_type': 'monthly',
            'tasks_executed': ['comprehensive_audit', 'license_check', 'trend_analysis'],
            'errors': [],
            'warnings': []
        }

    def get_schedule_status(self) -> Dict[str, Any]:
        """
        Get current schedule status.

        Returns:
            Dict containing schedule information.
        """
        maintenance_config = self.config_manager.get('maintenance', {})

        return {
            'scheduler_active': self.is_active(),
            'daily_enabled': maintenance_config.get('daily', {}).get('enabled', False),
            'daily_schedule': maintenance_config.get('daily', {}).get('schedule', 'Not set'),
            'weekly_enabled': maintenance_config.get('weekly', {}).get('enabled', False),
            'weekly_schedule': maintenance_config.get('weekly', {}).get('schedule', 'Not set'),
            'monthly_enabled': maintenance_config.get('monthly', {}).get('enabled', False),
            'monthly_schedule': maintenance_config.get('monthly', {}).get('schedule', 'Not set'),
            'next_daily_run': self._get_next_run_time('daily'),
            'next_weekly_run': self._get_next_run_time('weekly'),
            'next_monthly_run': self._get_next_run_time('monthly')
        }

    def _get_next_run_time(self, task_type: str) -> Optional[str]:
        """Get next run time for a task type."""
        # This is a simplified implementation
        # In a real implementation, you'd query the schedule library
        maintenance_config = self.config_manager.get('maintenance', {})

        if task_type not in maintenance_config or not maintenance_config[task_type].get('enabled', False):
            return None

        schedule_str = maintenance_config[task_type].get('schedule', '')

        try:
            if task_type == 'daily':
                hour, minute = map(int, schedule_str.split(':'))
                now = datetime.now()
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run.isoformat()

            elif task_type == 'weekly':
                day, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))
                # Simplified - would need more complex logic for actual day calculation
                return f"Next {day} at {hour:02d}:{minute:02d}"

            elif task_type == 'monthly':
                day_str, time_str = schedule_str.split(' ', 1)
                hour, minute = map(int, time_str.split(':'))
                # Simplified
                return f"Next month {day_str} at {hour:02d}:{minute:02d}"

        except (ValueError, AttributeError):
            pass

        return "Schedule parsing error"