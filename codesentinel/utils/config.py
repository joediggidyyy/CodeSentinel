"""
Configuration Management
========================

Handles loading, validation, and management of CodeSentinel configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigManager:
    """Manages CodeSentinel configuration files."""

    def __init__(self, config_path: Path):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.config = {}
        self.config_loaded = False

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Dict containing configuration data.
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                self.config_loaded = True
            else:
                # Create default configuration
                self.config = self._create_default_config()
                self.save_config()

        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            self.config = self._create_default_config()

        return self.config

    def save_config(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            raise Exception(f"Could not save config to {self.config_path}: {e}")

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            "version": "1.0.0",
            "enabled": True,
            "alerts": {
                "enabled": True,
                "channels": {
                    "console": {"enabled": True},
                    "file": {"enabled": True, "log_file": "codesentinel.log"},
                    "email": {"enabled": False},
                    "slack": {"enabled": False}
                },
                "alert_rules": {
                    "critical_security_issues": True,
                    "task_failures": True,
                    "dependency_vulnerabilities": True
                }
            },
            "github": {
                "copilot": {"enabled": False},
                "api": {"enabled": False},
                "repository": {"enabled": False}
            },
            "ide": {
                "vscode": {"enabled": False}
            },
            "maintenance": {
                "daily": {"enabled": True, "schedule": "09:00"},
                "weekly": {"enabled": True, "schedule": "Monday 10:00"},
                "monthly": {"enabled": True, "schedule": "1st 11:00"}
            },
            "logging": {
                "level": "INFO",
                "file": "codesentinel.log",
                "max_size": "10MB",
                "retention": "30 days"
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (dot-separated for nested keys).
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key (dot-separated for nested keys).
            value: Value to set.
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def validate_config(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of validation error messages.
        """
        errors = []

        # Check required fields
        required_fields = ['version', 'enabled', 'alerts']
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required field: {field}")

        # Validate alert channels
        if 'alerts' in self.config:
            alerts = self.config['alerts']
            if 'channels' in alerts:
                channels = alerts['channels']
                for channel_name, channel_config in channels.items():
                    if not isinstance(channel_config, dict):
                        errors.append(f"Invalid channel config for {channel_name}")
                    elif 'enabled' not in channel_config:
                        errors.append(f"Missing 'enabled' field for channel {channel_name}")

        return errors