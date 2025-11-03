#!/usr/bin/env python3
"""
CodeSentinel Alert System
==========================

SECURITY > EFFICIENCY > MINIMALISM

Monitors maintenance results and sends alerts for critical issues.
Supports multiple notification channels (console, file, email, Slack).

Usage: python tools/codesentinel/alert_system.py --check-results <results_file>
"""

import argparse
import json
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.error


class MaintenanceAlertSystem:
    """Alert system for maintenance critical issues."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_file = repo_root / "tools" / "config" / "alerts.json"
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load alert configuration"""
        default_config = {
            "enabled": True,
            "channels": {
                "console": {"enabled": True},
                "file": {
                    "enabled": True,
                    "log_file": "tools/codesentinel/alerts.log"
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_emails": []
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#maintenance-alerts"
                }
            },
            "alert_rules": {
                "critical_security_issues": True,
                "task_failures": True,
                "performance_degradation": True,
                "dependency_vulnerabilities": True
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # Deep merge
                self._deep_update(default_config, user_config)
            except json.JSONDecodeError:
                print(f"Warning: Invalid alert config file: {self.config_file}")

        return default_config

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def check_results_and_alert(self, results_file: Path) -> bool:
        """Check maintenance results and send alerts if needed"""
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except Exception as e:
            print(f"Error reading results file: {e}")
            return False

        # Analyze results for alert conditions
        alerts = self.analyze_results_for_alerts(results)

        if not alerts:
            return True  # No alerts needed

        # Send alerts through configured channels
        success = True
        for alert in alerts:
            if not self.send_alert(alert):
                success = False

        return success

    def analyze_results_for_alerts(self, results: Dict) -> List[Dict]:
        """Analyze maintenance results for alert conditions"""
        alerts = []

        # Check for task failures
        if self.config["alert_rules"]["task_failures"] and results.get("failure_count", 0) > 0:
            alerts.append({
                "level": "WARNING",
                "title": "Maintenance Task Failures",
                "message": f"{results['failure_count']} maintenance tasks failed",
                "details": {
                    "schedule": results.get("schedule", "unknown"),
                    "failures": results.get("failure_count", 0),
                    "errors": results.get("errors", [])
                }
            })

        # Check for critical security issues
        if self.config["alert_rules"]["critical_security_issues"]:
            critical_issues = results.get("summary", {}).get("critical_issues", [])
            if critical_issues:
                alerts.append({
                    "level": "CRITICAL",
                    "title": "Critical Security Issues Detected",
                    "message": f"{len(critical_issues)} critical security issues found",
                    "details": {
                        "issues": critical_issues,
                        "schedule": results.get("schedule", "unknown")
                    }
                })

        # Check for dependency vulnerabilities (from monthly maintenance)
        if self.config["alert_rules"]["dependency_vulnerabilities"]:
            vuln_count = 0
            for task_result in results.get("tasks", []):
                if task_result.get("name") == "Monthly Maintenance Suite":
                    # Check the monthly maintenance results for vulnerabilities
                    task_output = task_result.get("output", "")
                    if "vulnerabilities_found" in task_output:
                        try:
                            # Try to extract vulnerability count
                            if "vulnerabilities_found\": " in task_output:
                                vuln_str = task_output.split("vulnerabilities_found\": ")[1].split(",")[0]
                                vuln_count = int(vuln_str)
                        except:
                            vuln_count = 1  # Assume vulnerabilities if parsing fails

            if vuln_count > 0:
                alerts.append({
                    "level": "HIGH",
                    "title": "Dependency Vulnerabilities Found",
                    "message": f"{vuln_count} security vulnerabilities in dependencies",
                    "details": {
                        "vulnerability_count": vuln_count,
                        "recommendation": "Run 'pip-audit' or 'safety check' for details"
                    }
                })

        return alerts

    def send_alert(self, alert: Dict) -> bool:
        """Send alert through all configured channels"""
        success = True

        # Console alert (always enabled for debugging)
        if self.config["channels"]["console"]["enabled"]:
            self._send_console_alert(alert)

        # File alert
        if self.config["channels"]["file"]["enabled"]:
            if not self._send_file_alert(alert):
                success = False

        # Email alert
        if self.config["channels"]["email"]["enabled"]:
            if not self._send_email_alert(alert):
                success = False

        # Slack alert
        if self.config["channels"]["slack"]["enabled"]:
            if not self._send_slack_alert(alert):
                success = False

        return success

    def _send_console_alert(self, alert: Dict):
        """Send alert to console"""
        level_colors = {
            "CRITICAL": "\033[91m",  # Red
            "HIGH": "\033[93m",     # Yellow
            "WARNING": "\033[94m",  # Blue
            "INFO": "\033[92m"      # Green
        }
        reset_color = "\033[0m"

        color = level_colors.get(alert["level"], "")
        print(f"{color}[{alert['level']}] {alert['title']}{reset_color}")
        print(f"  {alert['message']}")

    def _send_file_alert(self, alert: Dict) -> bool:
        """Send alert to log file"""
        try:
            log_file = self.repo_root / self.config["channels"]["file"]["log_file"]
            log_file.parent.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp} [{alert['level']}] {alert['title']}: {alert['message']}\n"

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            return True
        except Exception as e:
            print(f"Failed to write alert to file: {e}")
            return False

    def _send_email_alert(self, alert: Dict) -> bool:
        """Send alert via email"""
        try:
            email_config = self.config["channels"]["email"]

            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = f"CodeSentinel Alert: {alert['title']}"

            body = f"""
CodeSentinel Maintenance Alert

Level: {alert['level']}
Title: {alert['title']}
Message: {alert['message']}

Timestamp: {datetime.now().isoformat()}

Details:
{json.dumps(alert.get('details', {}), indent=2)}

This is an automated message from the CodeSentinel maintenance system.
"""

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            text = msg.as_string()
            server.sendmail(email_config["from_email"], email_config["to_emails"], text)
            server.quit()

            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def _send_slack_alert(self, alert: Dict) -> bool:
        """Send alert to Slack"""
        try:
            slack_config = self.config["channels"]["slack"]

            payload = {
                "channel": slack_config["channel"],
                "username": "CodeSentinel Bot",
                "icon_emoji": ":warning:",
                "attachments": [{
                    "color": self._get_slack_color(alert["level"]),
                    "title": alert["title"],
                    "text": alert["message"],
                    "fields": [
                        {
                            "title": "Level",
                            "value": alert["level"],
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        }
                    ]
                }]
            }

            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                slack_config["webhook_url"],
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                return response.status == 200

        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False

    def _get_slack_color(self, level: str) -> str:
        """Get Slack color for alert level"""
        colors = {
            "CRITICAL": "danger",
            "HIGH": "warning",
            "WARNING": "warning",
            "INFO": "good"
        }
        return colors.get(level, "warning")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CodeSentinel Alert System")
    parser.add_argument("--check-results", required=False,
                       help="Path to maintenance results JSON file")
    parser.add_argument("--config", help="Path to alert config file")
    parser.add_argument("--test", action="store_true",
                       help="Test alert system with sample alert")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent

    alert_system = MaintenanceAlertSystem(repo_root)

    if args.test:
        # Send test alert
        test_alert = {
            "level": "INFO",
            "title": "Test Alert",
            "message": "This is a test of the CodeSentinel alert system",
            "details": {"test": True, "timestamp": datetime.now().isoformat()}
        }
        success = alert_system.send_alert(test_alert)
        print(f"Test alert {'sent successfully' if success else 'failed'}")
        sys.exit(0 if success else 1)

    if not args.check_results:
        parser.error("--check-results is required unless --test is specified")

    # Check results file
    results_file = Path(args.check_results)
    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        sys.exit(1)

    success = alert_system.check_results_and_alert(results_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()