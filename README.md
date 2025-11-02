# CodeSentinel

**SECURITY > EFFICIENCY > MINIMALISM**

CodeSentinel is an automated maintenance and security monitoring system for development projects. It provides comprehensive monitoring capabilities with multi-channel alerting, scheduled maintenance tasks, and seamless integration with development workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## Features

### 🔒 Security Monitoring

- Automated vulnerability scanning
- Dependency analysis and security audits
- Real-time security alerts
- Compliance checking

### 🔧 Automated Maintenance

- Scheduled maintenance tasks (daily/weekly/monthly)
- Code quality analysis
- Performance monitoring
- Automated cleanup operations

### 📢 Multi-Channel Alerting

- **Email**: SMTP-based notifications with multiple recipients
- **Slack**: Webhook integration for team notifications
- **Console**: Terminal output for immediate feedback
- **File**: Persistent logging for audit trails

### 🔗 Ecosystem Integration

- **GitHub**: Copilot integration, API access, repository features
- **VS Code**: IDE integration with tasks and settings
- **Git**: Repository-aware configuration and workflows

### 🎨 User Experience

- **Terminal Wizard**: Command-line setup with guided prompts
- **GUI Wizard**: Graphical setup with modern interface
- **CLI Tools**: Command-line operations for automation
- **Configuration Management**: JSON-based config with validation

## Quick Start

### System Requirements

CodeSentinel requires:

- **Python 3.13+**
- **pip** (Python package installer)
- **Git** (for repository features)

### Dependency Check

Before installation, run the dependency checker to ensure your system is ready:

```bash
# Quick check
python check_dependencies.py --quiet

# Full dependency report
python check_dependencies.py

# JSON output for automation
python check_dependencies.py --json
```

### Installation

```bash
# Option 1: Automated installer (recommended)
python install.py

# Option 2: Platform-specific installers
# Windows:
install.bat

# Unix/Linux/macOS:
chmod +x install.sh
./install.sh

# Option 3: Manual installation
pip install -e .
```

### Setup

```bash
# Interactive terminal setup
codesentinel-setup

# GUI setup (if tkinter available)
codesentinel-setup --gui

# Non-interactive setup with defaults
codesentinel-setup --non-interactive
```

### Basic Usage

```bash
# Check status
codesentinel status

# Run security scan
codesentinel scan

# Run daily maintenance
codesentinel maintenance daily

# Send test alert
codesentinel alert "System check completed"

# Start maintenance scheduler
codesentinel schedule start
```

## Architecture

```
codesentinel/
├── core/           # Main engine and orchestration
├── cli/            # Command-line interface
├── gui/            # Graphical interface components
└── utils/          # Configuration, alerts, scheduling

tools/              # Setup and utility scripts
docs/               # Documentation
tests/              # Test suite
scripts/            # Installation scripts
```

## Configuration

CodeSentinel uses JSON-based configuration with support for environment variables:

```json
{
  "version": "1.0.0",
  "enabled": true,
  "alerts": {
    "channels": {
      "console": {"enabled": true},
      "email": {"enabled": false},
      "slack": {"enabled": false}
    }
  },
  "github": {
    "copilot": {"enabled": false},
    "api": {"enabled": false}
  }
}
```

## Alert Channels

### Email Configuration

```bash
# Setup wizard will guide you through:
# - SMTP server and port
# - Authentication credentials
# - Multiple recipient addresses
# - Connection testing
```

### Slack Integration

```bash
# Configure webhook URL and channel
# Automatic message formatting
# Real-time delivery
```

## GitHub Integration

### Copilot Integration

- Creates `.github/copilot-instructions.md`
- Provides maintenance and security commands
- Integrates with GitHub Copilot chat

### API Features

- Automated issue creation
- Pull request monitoring
- Repository statistics
- Workflow automation

## Maintenance Scheduling

CodeSentinel supports automated maintenance with configurable schedules:

- **Daily**: Security checks, dependency updates, log cleanup
- **Weekly**: Deep analysis, performance checks, backup verification
- **Monthly**: Comprehensive audits, license checks, trend analysis

## Development

### Prerequisites

- Python 3.13+
- Git (for repository features)
- Optional: tkinter (for GUI), requests (for Slack), schedule (for scheduling)

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linting
python -m flake8 codesentinel/

# Build documentation
cd docs && make html
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Documentation

- [Setup Guide](docs/setup.md)
- [Configuration Reference](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## Security

CodeSentinel takes security seriously:

- No external network calls without explicit configuration
- Secure credential handling with environment variables
- Comprehensive logging for audit trails
- Regular security updates and vulnerability scanning

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/joediggidyyy/CodeSentinel/issues)
- 💬 [Discussions](https://github.com/joediggidyyy/CodeSentinel/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**CodeSentinel** - Keeping your codebase secure and efficient, automatically.
