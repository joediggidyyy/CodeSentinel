"""
CodeSentinel - Unified Configuration Manager

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Replaces the 9 separate JSON configuration files with a single,
secure, and unified configuration system.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from .security.credential_manager import credential_manager

@dataclass
class AlertConfig:
    """Alert system configuration."""
    console_enabled: bool = True
    file_enabled: bool = True
    email_enabled: bool = False
    slack_enabled: bool = False
    log_file: str = "codesentinel.log"
    
    # Alert rules
    security_alerts: bool = True
    task_failure_alerts: bool = True
    dependency_alerts: bool = True

@dataclass
class EmailConfig:
    """Email configuration for alerts."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    from_email: str = ""
    recipients: list = None
    
    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []

@dataclass
class SlackConfig:
    """Slack configuration for alerts."""
    webhook_url: str = ""
    channel: str = "#maintenance-alerts"
    username: str = "CodeSentinel"

@dataclass
class GitHubConfig:
    """GitHub integration configuration."""
    copilot_enabled: bool = True
    api_enabled: bool = False
    repo_features_enabled: bool = True
    auto_pr_reviews: bool = False

@dataclass
class MaintenanceConfig:
    """Maintenance scheduling configuration."""
    daily_enabled: bool = True
    weekly_enabled: bool = True
    monthly_enabled: bool = True
    
    # Schedule (cron-like)
    daily_time: str = "02:00"
    weekly_day: str = "monday"
    weekly_time: str = "03:00"
    monthly_day: int = 1
    monthly_time: str = "04:00"

@dataclass
class SecurityConfig:
    """Security settings configuration."""
    vulnerability_scanning: bool = True
    dependency_auditing: bool = True
    credential_encryption: bool = True
    audit_logging: bool = True

@dataclass
class CodeSentinelConfig:
    """Main CodeSentinel configuration."""
    version: str = "2.0.0"
    install_location: str = ""
    installation_mode: str = "repository"  # repository or standalone
    
    # Sub-configurations
    alerts: AlertConfig = None
    email: EmailConfig = None
    slack: SlackConfig = None
    github: GitHubConfig = None
    maintenance: MaintenanceConfig = None
    security: SecurityConfig = None
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = AlertConfig()
        if self.email is None:
            self.email = EmailConfig()
        if self.slack is None:
            self.slack = SlackConfig()
        if self.github is None:
            self.github = GitHubConfig()
        if self.maintenance is None:
            self.maintenance = MaintenanceConfig()
        if self.security is None:
            self.security = SecurityConfig()

class ConfigurationManager:
    """
    Unified configuration manager that replaces multiple JSON files
    with a single, secure configuration system.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / "codesentinel_config.yaml"
        self._config: Optional[CodeSentinelConfig] = None
    
    @property
    def config(self) -> CodeSentinelConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> CodeSentinelConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Convert dict to dataclass
                return self._dict_to_config(data)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return CodeSentinelConfig()
        else:
            # Create default configuration
            return CodeSentinelConfig()
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save
            config_dict = asdict(self.config)
            
            # Remove sensitive data before saving
            safe_config = credential_manager.export_config_safe(config_dict)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(safe_config, f, default_flow_style=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _dict_to_config(self, data: Dict[str, Any]) -> CodeSentinelConfig:
        """Convert dictionary to CodeSentinelConfig dataclass."""
        # Extract nested configurations
        alerts_data = data.get('alerts', {})
        email_data = data.get('email', {})
        slack_data = data.get('slack', {})
        github_data = data.get('github', {})
        maintenance_data = data.get('maintenance', {})
        security_data = data.get('security', {})
        
        return CodeSentinelConfig(
            version=data.get('version', '2.0.0'),
            install_location=data.get('install_location', ''),
            installation_mode=data.get('installation_mode', 'repository'),
            alerts=AlertConfig(**alerts_data),
            email=EmailConfig(**email_data),
            slack=SlackConfig(**slack_data),
            github=GitHubConfig(**github_data),
            maintenance=MaintenanceConfig(**maintenance_data),
            security=SecurityConfig(**security_data)
        )
    
    def update_alerts(self, **kwargs) -> None:
        """Update alert configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.alerts, key):
                setattr(self.config.alerts, key, value)
    
    def update_email(self, **kwargs) -> None:
        """Update email configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.email, key):
                setattr(self.config.email, key, value)
    
    def update_slack(self, **kwargs) -> None:
        """Update Slack configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.slack, key):
                setattr(self.config.slack, key, value)
    
    def update_github(self, **kwargs) -> None:
        """Update GitHub configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.github, key):
                setattr(self.config.github, key, value)
    
    def update_maintenance(self, **kwargs) -> None:
        """Update maintenance configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.maintenance, key):
                setattr(self.config.maintenance, key, value)
    
    def update_security(self, **kwargs) -> None:
        """Update security configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.security, key):
                setattr(self.config.security, key, value)
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            # Check email configuration if enabled
            if self.config.alerts.email_enabled:
                if not self.config.email.username or not self.config.email.smtp_server:
                    print("Error: Email alerts enabled but configuration incomplete")
                    return False
                
                # Test SMTP credentials
                if not credential_manager.validate_smtp_credentials(
                    self.config.email.smtp_server,
                    self.config.email.smtp_port,
                    self.config.email.username
                ):
                    print("Error: SMTP credentials validation failed")
                    return False
            
            # Check GitHub configuration if API enabled
            if self.config.github.api_enabled:
                if not credential_manager.test_github_token():
                    print("Error: GitHub API enabled but token validation failed")
                    return False
            
            # Check Slack configuration if enabled
            if self.config.alerts.slack_enabled:
                if not self.config.slack.webhook_url:
                    print("Error: Slack alerts enabled but webhook URL missing")
                    return False
            
            return True
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False
    
    def get_legacy_config_path(self, config_name: str) -> Optional[Path]:
        """Get path to legacy configuration file for migration."""
        legacy_paths = {
            'alerts': Path('tools/config/alerts.json'),
            'scheduler': Path('tools/config/scheduler.json'),
            'change_detection': Path('tools/config/change_detection.json'),
            'main': Path('codesentinel.json')
        }
        return legacy_paths.get(config_name)
    
    def migrate_from_legacy(self) -> bool:
        """Migrate configuration from legacy JSON files."""
        try:
            # Try to load from main legacy config
            legacy_main = self.get_legacy_config_path('main')
            if legacy_main and legacy_main.exists():
                with open(legacy_main, 'r') as f:
                    legacy_data = json.load(f)
                
                # Map legacy structure to new structure
                self._migrate_legacy_data(legacy_data)
                
            # Save migrated configuration
            return self.save_config()
        except Exception as e:
            print(f"Legacy migration error: {e}")
            return False
    
    def _migrate_legacy_data(self, legacy_data: Dict[str, Any]) -> None:
        """Map legacy configuration data to new structure."""
        # Migrate alerts configuration
        if 'alerts' in legacy_data:
            alerts_data = legacy_data['alerts']
            if 'channels' in alerts_data:
                channels = alerts_data['channels']
                self.config.alerts.console_enabled = channels.get('console', {}).get('enabled', True)
                self.config.alerts.file_enabled = channels.get('file', {}).get('enabled', True)
                self.config.alerts.email_enabled = channels.get('email', {}).get('enabled', False)
                self.config.alerts.slack_enabled = channels.get('slack', {}).get('enabled', False)
        
        # Migrate GitHub configuration
        if 'github' in legacy_data:
            github_data = legacy_data['github']
            self.config.github.copilot_enabled = github_data.get('copilot', {}).get('enabled', True)
            self.config.github.api_enabled = github_data.get('api', {}).get('enabled', False)
    
    def export_summary(self) -> Dict[str, Any]:
        """Export configuration summary for display."""
        return {
            "version": self.config.version,
            "installation": {
                "location": self.config.install_location,
                "mode": self.config.installation_mode
            },
            "alerts": {
                "console": self.config.alerts.console_enabled,
                "file": self.config.alerts.file_enabled,
                "email": self.config.alerts.email_enabled,
                "slack": self.config.alerts.slack_enabled
            },
            "integrations": {
                "github_copilot": self.config.github.copilot_enabled,
                "github_api": self.config.github.api_enabled
            },
            "maintenance": {
                "daily": self.config.maintenance.daily_enabled,
                "weekly": self.config.maintenance.weekly_enabled,
                "monthly": self.config.maintenance.monthly_enabled
            },
            "security": {
                "vulnerability_scanning": self.config.security.vulnerability_scanning,
                "credential_encryption": self.config.security.credential_encryption
            }
        }


# Global configuration manager instance
config_manager = ConfigurationManager()