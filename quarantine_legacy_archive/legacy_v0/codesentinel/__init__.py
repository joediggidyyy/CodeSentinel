"""
CodeSentinel
============

SECURITY > EFFICIENCY > MINIMALISM

A comprehensive suite of automated maintenance and security tools for development environments.
CodeSentinel provides secure, automated, self-healing capabilities for any development workflow.

Components:
- Scheduler: Automated task orchestration with multi-schedule support
- Alert System: Critical issue notification through multiple channels
- Weekly Maintenance: Comprehensive weekly security and health checks
- Monthly Maintenance: Deep system analysis and dependency management
- Dependency Suggester: Automated package update recommendations

All tools follow security-first principles and are platform-independent.
"""

__version__ = "1.0.0"
__author__ = "Joe Waller"
__email__ = "rellawj@unc.edu"

from .scheduler import MaintenanceScheduler
from .alert_system import MaintenanceAlertSystem
from .weekly_maintenance import WeeklyMaintenance
from .monthly_maintenance import MonthlyMaintenance
from .dependency_suggester import DependencySuggester

__all__ = [
    "MaintenanceScheduler",
    "MaintenanceAlertSystem",
    "WeeklyMaintenance",
    "MonthlyMaintenance",
    "DependencySuggester",
]