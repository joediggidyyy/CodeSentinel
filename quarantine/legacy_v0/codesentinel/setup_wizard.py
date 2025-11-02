#!/usr/bin/env python3
"""
CodeSentinel Installation Wizard
===============================

SECURITY > EFFICIENCY > MINIMALISM

Interactive setup wizard for CodeSentinel configuration and environment setup.
Guides users through environment variables, alert system configuration, IDE integration,
and optional features setup.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import getpass
import urllib.request
import urllib.error


class CodeSentinelSetupWizard:
    """Interactive setup wizard for CodeSentinel configuration."""

    def __init__(self, install_location: Optional[Path] = None):
        # Determine installation approach
        if install_location:
            self.install_location = install_location
            self.standalone_mode = True
        else:
            self.install_location = self.detect_install_location()
            self.standalone_mode = False

        # Check if we're in a git repository
        self.is_git_repo = self.check_git_repository()
        self.git_root = self.find_git_root() if self.is_git_repo else None

        # Setup directories based on installation type
        if self.standalone_mode:
            self.config_dir = self.install_location / "config"
            self.log_dir = self.install_location / "logs"
            self.codesentinel_dir = self.install_location
        else:
            # Repository-integrated mode
            self.config_dir = self.install_location / "tools" / "config"
            self.log_dir = self.install_location / "tools" / "codesentinel" / "logs"
            self.codesentinel_dir = self.install_location / "tools" / "codesentinel"

        # Setup colors for better UX
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m'
        }

        # Configuration collected during setup
        self.config = {
            'environment': {},
            'alerts': {},
            'ide': {},
            'github': {},
            'optional': {}
        }

    def detect_install_location(self) -> Path:
        """Detect the best installation location."""
        # First, check if we're in a repository with CodeSentinel already
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "tools" / "codesentinel").exists():
                return parent

        # If not found, check if we're in a git repository
        if self.check_git_repository():
            git_root = self.find_git_root()
            if git_root:
                return git_root

        # Default to current directory
        return Path.cwd()

    def check_git_repository(self) -> bool:
        """Check if current directory is in a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def find_git_root(self) -> Optional[Path]:
        """Find the git repository root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def find_repo_root(self) -> Path:
        """Find the repository root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "tools" / "codesentinel").exists():
                return parent
        raise RuntimeError("Could not find CodeSentinel repository root")

    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{self.colors['bold']}{self.colors['cyan']}{'='*60}{self.colors['reset']}")
        print(f"{self.colors['bold']}{self.colors['cyan']}{title.center(60)}{self.colors['reset']}")
        print(f"{self.colors['bold']}{self.colors['cyan']}{'='*60}{self.colors['reset']}\n")

    def print_step(self, step_num: int, title: str):
        """Print a step header."""
        print(f"{self.colors['bold']}{self.colors['yellow']}[Step {step_num}]{self.colors['reset']} {title}")

    def print_success(self, message: str):
        """Print a success message."""
        print(f"{self.colors['green']}✓{self.colors['reset']} {message}")

    def print_warning(self, message: str):
        """Print a warning message."""
        print(f"{self.colors['yellow']}⚠{self.colors['reset']} {message}")

    def print_error(self, message: str):
        """Print an error message."""
        print(f"{self.colors['red']}✗{self.colors['reset']} {message}")

    def prompt_yes_no(self, question: str, default: bool = True) -> bool:
        """Prompt user for yes/no input."""
        default_text = "(Y/n)" if default else "(y/N)"
        while True:
            response = input(f"{question} {default_text}: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes', 'true']:
                return True
            if response in ['n', 'no', 'false']:
                return False
            print("Please enter 'y' or 'n'")

    def prompt_choice(self, question: str, options: List[str], default: int = 0) -> int:
        """Prompt user to choose from a list of options."""
        print(f"\n{question}")
        for i, option in enumerate(options):
            marker = ">" if i == default else " "
            print(f"  {marker} {i+1}. {option}")

        while True:
            try:
                response = input(f"\nEnter choice (1-{len(options)}) [default: {default+1}]: ").strip()
                if not response:
                    return default
                choice = int(response) - 1
                if 0 <= choice < len(options):
                    return choice
                print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")

    def prompt_input(self, question: str, default: str = "", password: bool = False) -> str:
        """Prompt user for text input."""
        if password:
            return getpass.getpass(f"{question}: ")
        else:
            default_text = f" [{default}]" if default else ""
            response = input(f"{question}{default_text}: ").strip()
            return response if response else default

    def check_system_requirements(self) -> bool:
        """Check if system meets minimum requirements."""
        self.print_step(1, "Checking System Requirements")

        issues = []

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 13):
            issues.append(f"Python {python_version.major}.{python_version.minor} detected. CodeSentinel requires Python 3.13+")

        # Check if we're in the right directory
        if not self.codesentinel_dir.exists():
            issues.append("CodeSentinel directory not found. Please run from repository root.")

        # Check if package is installed
        try:
            import codesentinel
        except ImportError:
            issues.append("CodeSentinel package not installed. Run 'pip install -e tools/' first.")

        if issues:
            for issue in issues:
                self.print_error(issue)
            return False

        self.print_success("System requirements met")
        return True

    def setup_environment_variables(self):
        """Setup environment variables."""
        self.print_step(2, "Environment Variables Setup")

        print("\nCodeSentinel uses environment variables for configuration.")
        print("These can be set globally or in your shell profile.\n")

        # Setup PATH for CLI commands
        self.setup_path_configuration()

        # PYTHONPATH
        pythonpath = os.environ.get('PYTHONPATH', '')
        codesentinel_path = str(self.codesentinel_dir)

        if codesentinel_path not in pythonpath:
            self.config['environment']['PYTHONPATH'] = f"{codesentinel_path}:{pythonpath}".rstrip(':')
            self.print_success(f"Added CodeSentinel to PYTHONPATH: {codesentinel_path}")
        else:
            self.print_success("PYTHONPATH already configured")

        # Config directory
        config_env = f"CODESENTINEL_CONFIG_DIR={self.config_dir}"
        self.config['environment']['CODESENTINEL_CONFIG_DIR'] = str(self.config_dir)
        self.print_success(f"Set config directory: {self.config_dir}")

        # Log directory
        log_dir = self.codesentinel_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        self.config['environment']['CODESENTINEL_LOG_DIR'] = str(log_dir)
        self.print_success(f"Set log directory: {log_dir}")

    def setup_path_configuration(self):
        """Setup PATH to include Python scripts directory."""
        print("Configuring PATH for CLI commands...")
        
        # Import and use the PATH configurator
        try:
            from .path_configurator import PathConfigurator
            
            configurator = PathConfigurator()
            if configurator.scripts_dir:
                print(f"Found Python scripts directory: {configurator.scripts_dir}")
                
                if not configurator.is_in_path(configurator.scripts_dir):
                    if self.prompt_yes_no(f"Add Python scripts directory to PATH?\n  {configurator.scripts_dir}", True):
                        # Add to current session
                        configurator.add_to_current_session(configurator.scripts_dir)
                        
                        # Store for permanent configuration
                        self.config['environment']['PATH_ADDITION'] = str(configurator.scripts_dir)
                        self.config['environment']['PATH_INSTRUCTIONS'] = True
                        
                        # Provide permanent setup instructions
                        configurator.provide_permanent_setup_instructions()
                        self.print_success("PATH configuration completed")
                    else:
                        self.print_warning("Skipping PATH configuration - CLI commands may require full paths")
                        self.config['environment']['PATH_SKIP'] = True
                        
                        # Show alternatives
                        configurator.show_alternative_commands()
                else:
                    self.print_success("Python scripts directory already in PATH")
            else:
                self.print_warning("Could not detect Python scripts directory")
                self.config['environment']['PATH_DETECTION_FAILED'] = True
                
                # Show alternative usage methods
                print("\nAlternative ways to run CodeSentinel:")
                print("  python -c \"from codesentinel.cli import main; main()\" --help")
                print("  python -c \"from tools.codesentinel.setup_wizard import main; main()\"")
                print("  python tools/codesentinel/scheduler.py --help")
                
        except ImportError as e:
            self.print_error(f"Could not import PATH configurator: {e}")
            self.config['environment']['PATH_CONFIGURATOR_ERROR'] = str(e)

    def detect_python_scripts_directory(self) -> Optional[Path]:
        """Detect where Python installs console scripts."""
        try:
            # Try to find the scripts directory by checking common locations
            import sysconfig
            
            # Method 1: Use sysconfig to get scripts directory
            scripts_dir = sysconfig.get_path('scripts')
            if scripts_dir and Path(scripts_dir).exists():
                return Path(scripts_dir)
            
            # Method 2: Check user scripts directory
            user_scripts = sysconfig.get_path('scripts', scheme='posix_user')
            if user_scripts and Path(user_scripts).exists():
                return Path(user_scripts)
            
            # Method 3: Try to find where pip installs scripts
            try:
                import pip
                pip_location = Path(pip.__file__).parent.parent
                scripts_candidates = [
                    pip_location / "Scripts",  # Windows
                    pip_location / "bin",      # Unix
                ]
                for candidate in scripts_candidates:
                    if candidate.exists():
                        return candidate
            except ImportError:
                pass
            
            # Method 4: Check for CodeSentinel executable directly
            import shutil
            codesentinel_exec = shutil.which('codesentinel')
            if codesentinel_exec:
                return Path(codesentinel_exec).parent
                
        except Exception as e:
            self.print_warning(f"Error detecting scripts directory: {e}")
        
        return None

    def provide_path_setup_instructions(self, scripts_dir: Path):
        """Provide platform-specific instructions for setting up PATH."""
        system = platform.system().lower()
        
        print(f"\n{self.colors['bold']}PATH Setup Instructions:{self.colors['reset']}")
        
        if system == "windows":
            print(f"\n{self.colors['yellow']}Windows - Choose one method:{self.colors['reset']}")
            print("\n1. PowerShell (Current Session):")
            print(f"   $env:PATH += \";{scripts_dir}\"")
            
            print("\n2. PowerShell Profile (Permanent):")
            print("   notepad $PROFILE")
            print(f"   Add: $env:PATH += \";{scripts_dir}\"")
            
            print("\n3. System Environment Variables:")
            print("   - Open 'Environment Variables' in System Properties")
            print("   - Edit PATH variable")
            print(f"   - Add: {scripts_dir}")
            
            print("\n4. Command Prompt (Current Session):")
            print(f"   set PATH=%PATH%;{scripts_dir}")
            
        elif system == "darwin":  # macOS
            print(f"\n{self.colors['yellow']}macOS:{self.colors['reset']}")
            print(f"Add to ~/.bash_profile, ~/.zshrc, or ~/.profile:")
            print(f"export PATH=\"{scripts_dir}:$PATH\"")
            
        else:  # Linux and other Unix-like
            print(f"\n{self.colors['yellow']}Linux/Unix:{self.colors['reset']}")
            print(f"Add to ~/.bashrc, ~/.zshrc, or ~/.profile:")
            print(f"export PATH=\"{scripts_dir}:$PATH\"")
        
        print(f"\n{self.colors['cyan']}After setting PATH, restart your terminal or run:{self.colors['reset']}")
        print("  codesentinel --help")
        print("  codesentinel-setup --help")
        print("  codesentinel-setup-gui")

    def setup_alert_system(self):
        """Setup alert system configuration."""
        self.print_step(3, "Alert System Configuration")

        print("\nCodeSentinel can send alerts for critical issues via multiple channels.\n")

        # Load existing config or create default
        alerts_config = self.config_dir / "alerts.json"
        if alerts_config.exists():
            with open(alerts_config, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "enabled": True,
                "channels": {
                    "console": {"enabled": True},
                    "file": {"enabled": True, "log_file": "tools/codesentinel/alerts.log"},
                    "email": {"enabled": False},
                    "slack": {"enabled": False}
                },
                "alert_rules": {
                    "critical_security_issues": True,
                    "task_failures": True,
                    "dependency_vulnerabilities": True
                }
            }

        # Console alerts
        config["channels"]["console"]["enabled"] = self.prompt_yes_no(
            "Enable console alerts (immediate feedback in terminal)?", True
        )

        # File logging
        config["channels"]["file"]["enabled"] = self.prompt_yes_no(
            "Enable file logging for alerts?", True
        )

        # Email alerts
        if self.prompt_yes_no("Configure email alerts for critical notifications?", False):
            config["channels"]["email"]["enabled"] = True

            print("\nEmail Configuration:")
            config["channels"]["email"]["smtp_server"] = self.prompt_input(
                "SMTP server", "smtp.gmail.com"
            )
            config["channels"]["email"]["smtp_port"] = int(self.prompt_input(
                "SMTP port", "587"
            ))
            config["channels"]["email"]["username"] = self.prompt_input(
                "Email username"
            )
            config["channels"]["email"]["password"] = self.prompt_input(
                "Email password (use app password for Gmail)", password=True
            )
            config["channels"]["email"]["from_email"] = self.prompt_input(
                "From email address", config["channels"]["email"]["username"]
            )

            emails = []
            while True:
                email = self.prompt_input("Recipient email address (leave empty to finish)")
                if not email:
                    break
                emails.append(email)
            config["channels"]["email"]["to_emails"] = emails

            # Test email configuration
            if self.test_email_config(config["channels"]["email"]):
                self.print_success("Email configuration tested successfully")
            else:
                self.print_warning("Email configuration test failed - check settings")

        # Slack alerts
        if self.prompt_yes_no("Configure Slack alerts?", False):
            config["channels"]["slack"]["enabled"] = True

            config["channels"]["slack"]["webhook_url"] = self.prompt_input(
                "Slack webhook URL"
            )
            config["channels"]["slack"]["channel"] = self.prompt_input(
                "Slack channel", "#maintenance-alerts"
            )
            config["channels"]["slack"]["username"] = self.prompt_input(
                "Bot username", "CodeSentinel"
            )

            # Test Slack configuration
            if self.test_slack_config(config["channels"]["slack"]):
                self.print_success("Slack configuration tested successfully")
            else:
                self.print_warning("Slack configuration test failed - check webhook URL")

        # Alert rules
        print("\nAlert Rules:")
        config["alert_rules"]["critical_security_issues"] = self.prompt_yes_no(
            "Alert on critical security issues?", True
        )
        config["alert_rules"]["task_failures"] = self.prompt_yes_no(
            "Alert on maintenance task failures?", True
        )
        config["alert_rules"]["dependency_vulnerabilities"] = self.prompt_yes_no(
            "Alert on dependency vulnerabilities?", True
        )

        # Save configuration
        with open(alerts_config, 'w') as f:
            json.dump(config, f, indent=2)

        self.config['alerts'] = config
        self.print_success(f"Alert configuration saved to {alerts_config}")

    def test_email_config(self, email_config: Dict) -> bool:
        """Test email configuration."""
        try:
            import smtplib
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.quit()
            return True
        except Exception as e:
            self.print_error(f"Email test failed: {e}")
            return False

    def test_slack_config(self, slack_config: Dict) -> bool:
        """Test Slack configuration."""
        try:
            test_message = {
                "text": "CodeSentinel setup test",
                "channel": slack_config["channel"],
                "username": slack_config["username"]
            }

            data = json.dumps(test_message).encode('utf-8')
            req = urllib.request.Request(
                slack_config["webhook_url"],
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except Exception as e:
            self.print_error(f"Slack test failed: {e}")
            return False

    def setup_ide_integration(self):
        """Setup IDE integration."""
        self.print_step(4, "IDE Integration Setup")

        print("\nCodeSentinel can integrate with your IDE for easier access.\n")

        # Detect IDE
        ide_options = ["VS Code", "Other/None"]
        ide_choice = self.prompt_choice("Which IDE do you use primarily?", ide_options)

        if ide_choice == 0:  # VS Code
            self.setup_vscode_integration()
        else:
            self.print_success("Skipping IDE integration")

    def setup_vscode_integration(self):
        """Setup VS Code integration."""
        vscode_dir = self.repo_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        # Check for existing settings
        settings_file = vscode_dir / "settings.json"
        tasks_file = vscode_dir / "tasks.json"

        # Update settings
        settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            except json.JSONDecodeError:
                # VS Code settings.json may contain comments (JSONC), skip reading existing settings
                self.print_warning("Existing VS Code settings contain comments, creating new settings")
                settings = {}

        # Add CodeSentinel settings
        settings.update({
            "codesentinel.enabled": True,
            "codesentinel.configDir": str(self.config_dir),
            "codesentinel.logDir": str(self.codesentinel_dir / "logs")
        })

        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

        # Create/update tasks
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "CodeSentinel: Run Daily Maintenance",
                    "type": "shell",
                    "command": "codesentinel-scheduler",
                    "args": ["--schedule", "daily"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "CodeSentinel: Run Weekly Maintenance",
                    "type": "shell",
                    "command": "codesentinel-scheduler",
                    "args": ["--schedule", "weekly"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "CodeSentinel: Test Alert System",
                    "type": "shell",
                    "command": "codesentinel-alert-system",
                    "args": ["--test"],
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    }
                }
            ]
        }

        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)

        self.config['ide']['vscode'] = {
            'settings_updated': True,
            'tasks_created': True
        }

        self.print_success("VS Code integration configured")
        self.print_success(f"Settings updated: {settings_file}")
        self.print_success(f"Tasks created: {tasks_file}")

    def setup_optional_features(self):
        """Setup optional features."""
        self.print_step(5, "Optional Features Setup")

        print("\nCodeSentinel has several optional features you can enable.\n")

        # Cron jobs for automated scheduling
        if self.prompt_yes_no("Setup automated cron jobs for scheduled maintenance?", False):
            self.setup_cron_jobs()

        # Git hooks
        if self.prompt_yes_no("Setup Git hooks for pre-commit checks?", False):
            self.setup_git_hooks()

        # CI/CD integration
        if self.prompt_yes_no("Setup CI/CD integration templates?", False):
            self.setup_ci_cd_integration()

    def setup_cron_jobs(self):
        """Setup cron jobs for automated maintenance."""
        system = platform.system().lower()

        if system == "windows":
            self.print_warning("Cron jobs on Windows require Task Scheduler setup")
            self.print_warning("Please see documentation for manual Task Scheduler configuration")
        else:
            # Unix-like systems
            cron_jobs = []

            if self.prompt_yes_no("Schedule daily maintenance (2 AM)?", True):
                cron_jobs.append("0 2 * * * codesentinel-scheduler --schedule daily")

            if self.prompt_yes_no("Schedule weekly maintenance (Monday 3 AM)?", True):
                cron_jobs.append("0 3 * * 1 codesentinel-scheduler --schedule weekly")

            if self.prompt_yes_no("Schedule monthly maintenance (1st of month 4 AM)?", True):
                cron_jobs.append("0 4 1 * * codesentinel-scheduler --schedule monthly")

            if cron_jobs:
                print("\nAdd these lines to your crontab (run 'crontab -e'):")
                print("# CodeSentinel automated maintenance")
                for job in cron_jobs:
                    print(job)
                print()

                self.config['optional']['cron_jobs'] = cron_jobs
                self.print_success("Cron job configuration displayed above")

    def setup_git_hooks(self):
        """Setup Git hooks for pre-commit checks."""
        git_hooks_dir = self.repo_root / ".git" / "hooks"

        if not git_hooks_dir.exists():
            self.print_warning("Git repository not initialized - skipping Git hooks setup")
            return

        # Pre-commit hook
        pre_commit_hook = git_hooks_dir / "pre-commit"

        hook_content = """#!/bin/bash
# CodeSentinel pre-commit hook

echo "Running CodeSentinel pre-commit checks..."

# Run dependency check
if command -v codesentinel-dependency-suggester &> /dev/null; then
    codesentinel-dependency-suggester --check
    if [ $? -ne 0 ]; then
        echo "Dependency check failed - fix issues before committing"
        exit 1
    fi
else
    echo "CodeSentinel dependency suggester not available"
fi

echo "Pre-commit checks passed"
"""

        with open(pre_commit_hook, 'w') as f:
            f.write(hook_content)

        # Make executable
        pre_commit_hook.chmod(0o755)

        self.config['optional']['git_hooks'] = ['pre-commit']
        self.print_success(f"Pre-commit hook installed: {pre_commit_hook}")

    def setup_ci_cd_integration(self):
        """Setup CI/CD integration templates."""
        ci_cd_dir = self.repo_root / ".github" / "workflows"
        ci_cd_dir.mkdir(parents=True, exist_ok=True)

        # GitHub Actions workflow
        workflow_content = """name: CodeSentinel Maintenance

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
    - cron: '0 3 * * 1'  # Weekly on Monday at 3 AM UTC
    - cron: '0 4 1 * *'  # Monthly on 1st at 4 AM UTC
  workflow_dispatch:

jobs:
  maintenance:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install CodeSentinel
      run: |
        pip install -e tools/

    - name: Run maintenance
      run: |
        if [ "${{ github.event.schedule }}" == "0 2 * * *" ]; then
          codesentinel-scheduler --schedule daily
        elif [ "${{ github.event.schedule }}" == "0 3 * * 1" ]; then
          codesentinel-scheduler --schedule weekly
        elif [ "${{ github.event.schedule }}" == "0 4 1 * *" ]; then
          codesentinel-scheduler --schedule monthly
        else
          codesentinel-scheduler --schedule daily
        fi
      env:
        CODESENTINEL_CONFIG_DIR: tools/config
        CODESENTINEL_LOG_DIR: tools/codesentinel/logs
"""

        workflow_file = ci_cd_dir / "codesentinel-maintenance.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)

        self.config['optional']['ci_cd'] = ['github-actions']
        self.print_success(f"GitHub Actions workflow created: {workflow_file}")

    def generate_setup_summary(self):
        """Generate and display setup summary."""
        self.print_header("Setup Complete!")

        print("CodeSentinel has been successfully configured for your environment.\n")

        # Environment variables
        if self.config['environment']:
            print(f"{self.colors['bold']}Environment Variables:{self.colors['reset']}")
            for var, value in self.config['environment'].items():
                print(f"  export {var}={value}")
            print()

        # Alert system
        if self.config['alerts']:
            print(f"{self.colors['bold']}Alert System:{self.colors['reset']}")
            channels = [k for k, v in self.config['alerts'].get('channels', {}).items() if v.get('enabled')]
            print(f"  Enabled channels: {', '.join(channels)}")
            print()

        # IDE integration
        if self.config['ide']:
            print(f"{self.colors['bold']}IDE Integration:{self.colors['reset']}")
            if 'vscode' in self.config['ide']:
                print("  VS Code: Tasks and settings configured")
            print()

        # GitHub integration
        if self.config['github']:
            print(f"{self.colors['bold']}GitHub Integration:{self.colors['reset']}")
            if 'copilot' in self.config['github']:
                print("  Copilot: Integration configured")
            if 'api' in self.config['github']:
                print("  API: Advanced features enabled")
            if 'repository' in self.config['github']:
                print("  Repository: Issue templates and workflows created")
            print()

        # Optional features
        if self.config['optional']:
            print(f"{self.colors['bold']}Optional Features:{self.colors['reset']}")
            if 'cron_jobs' in self.config['optional']:
                print("  Cron jobs: Scheduled for automated maintenance")
            if 'git_hooks' in self.config['optional']:
                print("  Git hooks: Pre-commit checks enabled")
            if 'ci_cd' in self.config['optional']:
                print("  CI/CD: GitHub Actions workflow created")
            print()

        print(f"{self.colors['bold']}Next Steps:{self.colors['reset']}")
        print("1. Set the environment variables in your shell profile")
        print("2. Test the system: codesentinel-scheduler --schedule daily --dry-run")
        print("3. Test alerts: codesentinel-alert-system --test")
        print("4. Review documentation: docs/MAINTENANCE_WORKFLOW.md")
        print()

        self.print_success("CodeSentinel setup wizard completed successfully!")

    def setup_github_integration(self):
        """Setup GitHub integration including Copilot and repository features."""
        self.print_step(5, "GitHub Integration Setup")

        if not self.is_git_repo:
            self.print_success("Not in a git repository - skipping GitHub integration")
            return

        print(f"\nGitHub repository detected: {self.git_root}")
        print("CodeSentinel can integrate with GitHub for enhanced features.\n")

        # GitHub Copilot integration
        if self.prompt_yes_no("Setup GitHub Copilot integration?", True):
            self.setup_github_copilot_integration()

        # GitHub API integration
        if self.prompt_yes_no("Configure GitHub API access for advanced features?", False):
            self.setup_github_api_integration()

        # Repository-specific features
        if self.prompt_yes_no("Enable repository-specific features (issue tracking, PR monitoring)?", True):
            self.setup_github_repository_features()

    def setup_github_copilot_integration(self):
        """Setup GitHub Copilot integration."""
        print("\nGitHub Copilot Integration:")
        print("CodeSentinel can work alongside GitHub Copilot to provide:")
        print("- Automated code review suggestions")
        print("- Security vulnerability detection")
        print("- Performance optimization recommendations")
        print("- Integration with Copilot chat commands")

        # Create .github/copilot-instructions.md if in a git repository
        if self.git_root:
            copilot_dir = self.git_root / ".github"
            copilot_dir.mkdir(exist_ok=True)

            copilot_instructions = """# CodeSentinel + GitHub Copilot Integration

This repository uses CodeSentinel for automated maintenance and security monitoring.

## Copilot Commands

You can use these commands in Copilot Chat:

### Maintenance
- `/maintenance status` - Check current maintenance status
- `/maintenance run daily` - Execute daily maintenance tasks
- `/maintenance alerts` - View recent alerts and issues

### Security
- `/security scan` - Run security vulnerability scan
- `/security audit` - Perform comprehensive security audit
- `/security dependencies` - Check for vulnerable dependencies

### Code Quality
- `/quality format` - Apply code formatting
- `/quality lint` - Run linting checks
- `/quality review` - Request code review suggestions

## Integration Features

- **Automated PR Reviews**: CodeSentinel automatically reviews pull requests
- **Security Alerts**: Immediate notifications for security issues
- **Performance Monitoring**: Continuous performance tracking
- **Dependency Updates**: Automated dependency vulnerability detection

## Best Practices

1. Always run maintenance before committing: `codesentinel-scheduler --schedule daily`
2. Check alerts after major changes: `codesentinel-alert-system --check-results`
3. Review security scans weekly: `codesentinel-scheduler --schedule weekly`
4. Monitor performance metrics monthly: `codesentinel-scheduler --schedule monthly`

## Configuration

CodeSentinel is configured in `tools/config/` with:
- Alert settings in `alerts.json`
- Maintenance schedules in `scheduler.json`
- Security policies in `security.json`

For help, run: `codesentinel-setup --help`
"""

            copilot_file = copilot_dir / "copilot-instructions.md"
            with open(copilot_file, 'w') as f:
                f.write(copilot_instructions)

            self.config['github']['copilot'] = {
                'instructions_file': str(copilot_file),
                'enabled': True
            }

            self.print_success(f"GitHub Copilot integration configured: {copilot_file}")
        else:
            self.print_success("GitHub Copilot integration configured (stand-alone mode)")
            self.config['github']['copilot'] = {
                'enabled': True,
                'stand_alone_mode': True
            }

    def setup_github_api_integration(self):
        """Setup GitHub API integration."""
        print("\nGitHub API Integration:")
        print("This enables advanced features like:")
        print("- Automated issue creation for critical alerts")
        print("- Pull request monitoring and reviews")
        print("- Repository statistics and analytics")
        print("- Integration with GitHub Actions")

        # GitHub token setup
        token = self.prompt_input(
            "GitHub Personal Access Token (leave empty to skip)",
            password=True
        )

        if token:
            # Test the token
            if self.test_github_token(token):
                # Store token securely
                github_config = {
                    'token': token,
                    'features': {
                        'issue_creation': True,
                        'pr_monitoring': True,
                        'actions_integration': True,
                        'statistics': True
                    }
                }

                # Save to config
                github_config_file = self.config_dir / "github.json"
                with open(github_config_file, 'w') as f:
                    json.dump(github_config, f, indent=2)

                self.config['github']['api'] = {
                    'enabled': True,
                    'config_file': str(github_config_file),
                    'features': github_config['features']
                }

                self.print_success("GitHub API integration configured successfully")
            else:
                self.print_error("GitHub token validation failed")
        else:
            self.print_success("GitHub API integration skipped")

    def test_github_token(self, token: str) -> bool:
        """Test GitHub token validity."""
        try:
            import requests

            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.print_error(f"GitHub token test failed: {e}")
            return False

    def setup_github_repository_features(self):
        """Setup repository-specific GitHub features."""
        print("\nRepository Features:")
        print("Enabling repository-specific monitoring and automation.")

        if not self.git_root:
            self.print_success("Repository features skipped (not in a git repository)")
            return

        # Create GitHub workflows directory
        workflows_dir = self.git_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create issue templates
        issue_templates_dir = self.git_root / ".github" / "ISSUE_TEMPLATE"
        issue_templates_dir.mkdir(parents=True, exist_ok=True)

        # Security vulnerability report template
        security_template = """---
name: Security Vulnerability Report
about: Report a security vulnerability in CodeSentinel
title: "[SECURITY] "
labels: security, vulnerability
assignees: ''

---

## Vulnerability Description

A clear and concise description of the security vulnerability.

## Impact

What is the impact of this vulnerability?

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Additional Context

Any additional information about the vulnerability.

## CodeSentinel Version

Version of CodeSentinel where this was discovered:

## Environment

- OS: [e.g., Windows 11, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g., 3.13]
- GitHub Repository: [if applicable]
"""

        security_file = issue_templates_dir / "security-vulnerability.md"
        with open(security_file, 'w') as f:
            f.write(security_template)

        # Maintenance issue template
        maintenance_template = """---
name: Maintenance Issue
about: Report a maintenance or automation issue
title: "[MAINTENANCE] "
labels: maintenance, automation
assignees: ''

---

## Issue Description

Describe the maintenance issue or automation problem.

## Expected Behavior

What should happen?

## Actual Behavior

What actually happened?

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Environment

- CodeSentinel Version: [run `codesentinel-scheduler --version`]
- OS: [e.g., Windows 11, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g., 3.13]

## Logs

Please include relevant log output:

```
[PASTE LOGS HERE]
```

## Additional Context

Any additional information that might be helpful.
"""

        maintenance_file = issue_templates_dir / "maintenance-issue.md"
        with open(maintenance_file, 'w') as f:
            f.write(maintenance_template)

        self.config['github']['repository'] = {
            'issue_templates': [str(security_file), str(maintenance_file)],
            'workflows_dir': str(workflows_dir),
            'enabled': True
        }

        self.print_success("Repository features configured")
        self.print_success(f"Security issue template: {security_file}")
        self.print_success(f"Maintenance issue template: {maintenance_file}")

    def setup_github_integration_non_interactive(self):
        """Setup GitHub integration with defaults (non-interactive)."""
        if not self.is_git_repo:
            return

        self.print_step(4, "GitHub Integration Setup")

        # Setup Copilot integration by default
        self.setup_github_copilot_integration()

        # Skip API integration in non-interactive mode
        self.print_success("GitHub Copilot integration configured (API integration skipped in non-interactive mode)")

        # Setup repository features
        self.setup_github_repository_features()

    def run_wizard(self) -> bool:
        """Run the complete interactive setup wizard."""
        self.print_header("CodeSentinel Setup Wizard")

        print("Welcome to the CodeSentinel setup wizard!")
        print("This will guide you through configuring CodeSentinel for your environment.\n")

        # Step 1: Install location
        if not self.prompt_install_location():
            return False

        # Step 2: Check system requirements
        if not self.check_system_requirements():
            self.print_error("System requirements not met. Please fix issues and try again.")
            return False

        # Step 3: Environment setup
        self.setup_environment_variables()

        # Step 4: Alert system
        self.setup_alert_system()

        # Step 5: GitHub integration (if in git repo)
        if self.is_git_repo:
            self.setup_github_integration()

        # Step 6: IDE integration
        self.setup_ide_integration()

        # Step 7: Optional features
        self.setup_optional_features()

        self.generate_setup_summary()
        return True

    def prompt_install_location(self) -> bool:
        """Prompt user for installation location."""
        self.print_step(1, "Installation Location")

        print(f"Current directory: {Path.cwd()}")
        print(f"Detected install location: {self.install_location}")

        if self.is_git_repo:
            print(f"Git repository detected: {self.git_root}")
            if self.standalone_mode:
                print("Standalone mode: CodeSentinel will be installed in the specified location")
            else:
                print("Repository mode: CodeSentinel will be integrated into the repository")
        else:
            print("Not in a git repository - standalone mode")

        # Ask if they want to change the location
        if self.prompt_yes_no("Use detected location?", True):
            self.print_success(f"Using install location: {self.install_location}")
            return True
        else:
            new_location = self.prompt_input("Enter new install location")
            if new_location:
                self.install_location = Path(new_location).expanduser().resolve()
                # Re-initialize directories
                if self.standalone_mode or not self.is_git_repo:
                    self.config_dir = self.install_location / "config"
                    self.log_dir = self.install_location / "logs"
                    self.codesentinel_dir = self.install_location
                else:
                    self.config_dir = self.install_location / "tools" / "config"
                    self.log_dir = self.install_location / "tools" / "codesentinel" / "logs"
                    self.codesentinel_dir = self.install_location / "tools" / "codesentinel"
                self.print_success(f"Updated install location: {self.install_location}")
                return True
            else:
                self.print_error("No location specified")
                return False

    def run_non_interactive_setup(self) -> bool:
        """Run setup with default values (non-interactive)."""
        self.print_header("CodeSentinel Non-Interactive Setup")

        print("Running CodeSentinel setup with default values...\n")

        # Run setup steps with defaults
        if not self.check_system_requirements():
            self.print_error("System requirements not met.")
            return False

        self.setup_environment_variables()
        self.setup_alert_system_non_interactive()

        # GitHub integration (if in git repo)
        if self.is_git_repo:
            self.setup_github_integration_non_interactive()

        self.setup_ide_integration_non_interactive()
        self.setup_optional_features_non_interactive()

        self.generate_setup_summary()
        return True

    def setup_alert_system_non_interactive(self):
        """Setup alert system with defaults (non-interactive)."""
        self.print_step(3, "Alert System Configuration")

        # Load existing config or create default
        alerts_config = self.config_dir / "alerts.json"
        if alerts_config.exists():
            with open(alerts_config, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "enabled": True,
                "channels": {
                    "console": {"enabled": True},
                    "file": {"enabled": True, "log_file": "tools/codesentinel/alerts.log"},
                    "email": {"enabled": False},
                    "slack": {"enabled": False}
                },
                "alert_rules": {
                    "critical_security_issues": True,
                    "task_failures": True,
                    "dependency_vulnerabilities": True
                }
            }

        # Save configuration
        with open(alerts_config, 'w') as f:
            json.dump(config, f, indent=2)

        self.config['alerts'] = config
        self.print_success(f"Alert configuration saved to {alerts_config}")

    def setup_ide_integration_non_interactive(self):
        """Setup IDE integration with defaults (non-interactive)."""
        self.print_step(4, "IDE Integration Setup")

        # Auto-detect VS Code
        base_dir = self.git_root if self.is_git_repo else self.install_location
        if base_dir is None:
            self.print_success("Skipping IDE integration (no valid base directory)")
            return

        vscode_dir = base_dir / ".vscode"
        if vscode_dir.exists() or (base_dir / ".vscode").mkdir(exist_ok=True):
            self.setup_vscode_integration()
        else:
            self.print_success("Skipping IDE integration (VS Code not detected)")

    def setup_optional_features_non_interactive(self):
        """Setup optional features with defaults (non-interactive)."""
        self.print_step(5, "Optional Features Setup")

        # Skip optional features in non-interactive mode
        self.print_success("Skipping optional features (non-interactive mode)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CodeSentinel Setup Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codesentinel-setup              # Run interactive setup wizard
  codesentinel-setup --help       # Show this help message
        """
    )

    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run setup with default values (non-interactive mode)'
    )

    parser.add_argument(
        '--install-location',
        type=str,
        help='Specify installation location (default: auto-detect)'
    )

    args = parser.parse_args()

    try:
        install_location = Path(args.install_location) if args.install_location else None
        wizard = CodeSentinelSetupWizard(install_location)
        if args.non_interactive:
            # Run with defaults
            success = wizard.run_non_interactive_setup()
        else:
            success = wizard.run_wizard()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()