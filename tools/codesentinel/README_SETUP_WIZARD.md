# CodeSentinel Setup Wizard

The CodeSentinel Setup Wizard provides an interactive guide to configure CodeSentinel for your development environment.

## Quick Start

```bash
# Install CodeSentinel
pip install codesentinel

# Run the setup wizard
codesentinel-setup
```

## Features

- **System Requirements Check**: Validates Python version and package installation
- **Environment Variables**: Automatically configures necessary environment variables
- **Alert System Configuration**: Interactive setup for email, Slack, console, and file alerts
- **IDE Integration**: Configures VS Code tasks and settings for easy access
- **Optional Features**: Cron jobs, Git hooks, and CI/CD integration templates

## Usage

### Interactive Setup (Recommended)

Run the interactive wizard for guided setup:

```bash
codesentinel-setup
```

### Non-Interactive Setup

For automated environments:

```bash
codesentinel-setup --non-interactive
```

### Help

```bash
codesentinel-setup --help
```

## What Gets Configured

### Environment Variables

- `PYTHONPATH`: Adds CodeSentinel to Python path
- `CODESENTINEL_CONFIG_DIR`: Points to configuration directory
- `CODESENTINEL_LOG_DIR`: Sets log file location

### Alert System

- Console Alerts: Immediate terminal feedback
- File Logging: Persistent alert history
- Email Alerts: SMTP notifications (optional)
- Slack Alerts: Webhook notifications (optional)

### IDE Integration

- VS Code Tasks: Build tasks for running maintenance
- Settings: CodeSentinel-specific configuration

### Optional Features

- Cron Jobs: Automated scheduling (Unix systems)
- Git Hooks: Pre-commit validation
- CI/CD Templates: GitHub Actions workflows

## Configuration Files Created

- `tools/config/alerts.json`: Alert system configuration
- `.vscode/settings.json`: VS Code settings
- `.vscode/tasks.json`: VS Code tasks
- `.github/workflows/codesentinel-maintenance.yml`: CI/CD workflow
- `.git/hooks/pre-commit`: Git pre-commit hook

## Security Notes

- Email passwords are stored in configuration files
- Use app passwords for Gmail instead of main passwords
- Slack webhooks should be kept secure
- Review generated configuration files before committing
