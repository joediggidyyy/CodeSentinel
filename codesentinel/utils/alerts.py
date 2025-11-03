"""
Alert Management System
=======================

Handles sending alerts through various channels (email, Slack, console, file).
"""

import json
import smtplib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import requests
except ImportError:
    requests = None


class AlertManager:
    """Manages alert notifications across multiple channels."""

    def __init__(self, config_manager):
        """
        Initialize alert manager.

        Args:
            config_manager: Configuration manager instance.
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger("AlertManager")

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        channels: Optional[List[str]] = None,
    ):
        """
        Send alert through configured channels.

        Args:
            title: Alert title.
            message: Alert message.
            severity: Alert severity ('info', 'warning', 'error', 'critical').
            channels: List of channels to send to. If None, uses all enabled channels.
        """
        config = self.config_manager.get("alerts.channels", {})

        if channels is None:
            channels = [ch for ch, cfg in config.items() if cfg.get("enabled", False)]

        self.logger.info(f"Sending {severity} alert: {title}")

        results = {}
        for channel in channels:
            try:
                if channel == "console":
                    results[channel] = self._send_console_alert(
                        title, message, severity
                    )
                elif channel == "file":
                    results[channel] = self._send_file_alert(title, message, severity)
                elif channel == "email":
                    results[channel] = self._send_email_alert(title, message, severity)
                elif channel == "slack":
                    results[channel] = self._send_slack_alert(title, message, severity)
                else:
                    self.logger.warning(f"Unknown alert channel: {channel}")
                    results[channel] = False
            except Exception as e:
                self.logger.error(f"Failed to send {channel} alert: {e}")
                results[channel] = False

        return results

    def _send_console_alert(self, title: str, message: str, severity: str) -> bool:
        """Send alert to console."""
        severity_colors = {
            "info": "\033[94m",  # Blue
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "critical": "\033[95m",  # Magenta
        }

        color = severity_colors.get(severity, "\033[94m")
        reset = "\033[0m"

        print(f"{color}[{severity.upper()}] {title}{reset}")
        print(f"{color}{message}{reset}")
        print()

        return True

    def _send_file_alert(self, title: str, message: str, severity: str) -> bool:
        """Send alert to log file."""
        config = self.config_manager.get("alerts.channels.file", {})
        log_file = config.get("log_file", "codesentinel.log")

        try:
            with open(log_file, "a") as f:
                timestamp = json.dumps({"timestamp": None}, default=str)[1:-1].split(
                    '"'
                )[1]
                f.write(f"[{timestamp}] [{severity.upper()}] {title}: {message}\n")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write to log file {log_file}: {e}")
            return False

    def _send_email_alert(self, title: str, message: str, severity: str) -> bool:
        """Send alert via email."""
        config = self.config_manager.get("alerts.channels.email", {})

        if not config.get("enabled", False):
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = config.get("from_email", config.get("username", ""))
            msg["To"] = ", ".join(config.get("to_emails", []))
            msg["Subject"] = f"[CodeSentinel] {severity.upper()}: {title}"

            body = f"Severity: {severity.upper()}\n\n{message}"
            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False

    def _send_slack_alert(self, title: str, message: str, severity: str) -> bool:
        """Send alert to Slack."""
        if requests is None:
            self.logger.error("requests library not available for Slack alerts")
            return False

        config = self.config_manager.get("alerts.channels.slack", {})

        if not config.get("enabled", False):
            return False

        try:
            # Use simple text markers instead of emojis
            prefix_map = {
                "info": "[INFO]",
                "warning": "[WARNING]",
                "error": "[ERROR]",
                "critical": "[CRITICAL]",
            }

            prefix = prefix_map.get(severity, "[ALERT]")
            slack_message = {
                "channel": config.get("channel", "#general"),
                "username": config.get("username", "CodeSentinel"),
                "text": f"{prefix} *{title}*\n{message}",
                "mrkdwn": True,
            }

            response = requests.post(
                config["webhook_url"], json=slack_message, timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
            return False

    def test_channel(self, channel: str) -> Dict[str, Any]:
        """
        Test alert channel configuration.

        Args:
            channel: Channel to test ('email', 'slack').

        Returns:
            Dict with test results.
        """
        result = {"channel": channel, "success": False, "message": ""}

        try:
            if channel == "email":
                success = self._test_email_config()
                result["success"] = success
                result["message"] = (
                    "Email configuration test successful"
                    if success
                    else "Email test failed"
                )
            elif channel == "slack":
                success = self._test_slack_config()
                result["success"] = success
                result["message"] = (
                    "Slack configuration test successful"
                    if success
                    else "Slack test failed"
                )
            else:
                result["message"] = f"Testing not supported for channel: {channel}"

        except Exception as e:
            result["message"] = f"Test failed: {e}"

        return result

    def _test_email_config(self) -> bool:
        """Test email configuration."""
        config = self.config_manager.get("alerts.channels.email", {})

        try:
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.quit()
            return True
        except Exception:
            return False

    def _test_slack_config(self) -> bool:
        """Test Slack configuration."""
        if requests is None:
            return False

        config = self.config_manager.get("alerts.channels.slack", {})

        try:
            test_message = {"text": "CodeSentinel test message"}
            response = requests.post(
                config["webhook_url"], json=test_message, timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
