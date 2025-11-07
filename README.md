# CodeSentinel

*A Polymath Project*

CodeSentinel is a cross-platform application that integrates with VS Code or any major IDE to provide a secure, automated, self-healing development environment.

## Project Structure

```
CodeSentinel/
├── README.md                          (main documentation)
├── CHANGELOG.md                       (release notes)
├── QUICK_START.md                     (user installation guide)
├── PUBLISH_NOW.md                     (1.0.3: PyPI publication steps)
├── setup.py, pyproject.toml           (packaging configuration)
├── requirements.txt                   (dependencies)
├── SECURITY.md, CONTRIBUTING.md       (project guidelines)
├── INSTALL_CODESENTINEL_GUI.py        (cross-platform installer)
│
├── codesentinel/                      (package source)
│   ├── __init__.py                    (version: 1.0.3)
│   ├── cli/                           (command-line interface)
│   ├── core/                          (core functionality & auditing)
│   ├── gui/                           (GUI components)
│   └── utils/                         (utilities: config, alerts, scheduler, file integrity)
│
├── tests/                             (test suite: 22/22 passing)
│
├── dist/                              (distributions: sdist + wheel)
│
├── docs/                              (documentation & reference)
│   ├── V1_0_3_DISTRIBUTION_REPORT.md (technical overview with scheduling & customization)
│   ├── V1_0_3_BETA_TEST_REPORT.md    (all test results)
│   ├── PYPI_PUBLICATION_GUIDE.md     (detailed PyPI guide)
│   └── [20+ reference files]
│
└── .github/                           (GitHub configuration & CI/CD)
```

## Governance & Architecture

CodeSentinel is managed through a tiered documentation and governance system known as "satellites." This ensures that all operations are standardized, auditable, and aligned with the project's core principles.

### Tiered Documentation Strategy

- **T4a (Strategic Guides)**: High-level documents that define the "why" and "what" for cross-cutting concerns like analytics and enterprise integration.
  - `docs/ADVANCED_ANALYTICS_FRAMEWORK.md`
  - `docs/ENTERPRISE_INTEGRATION_GUIDE.md`
- **T4b (Procedural Satellites)**: Detailed, step-by-step instructions that codify the "how" for specific operational domains.
  - `github/AGENT_INSTRUCTIONS.md` (Source Control & PRs)
  - `deployment/AGENT_INSTRUCTIONS.md` (CI/CD & Deployments)
  - `infrastructure/AGENT_INSTRUCTIONS.md` (Infrastructure as Code)
- **T4c (Quick Reference Cards)**: Scannable, one-page summaries for engineers, providing at-a-glance information for common tasks.
  - `docs/quick_reference/`

This layered approach ensures that information is accessible at the right level of detail for every audience, from architects to on-call engineers.

## Core Features

- **Security-First Architecture**: Automated vulnerability scanning and security monitoring
- **Multi-Channel Alerts**: Console, file logging, email, and Slack integration
- **GitHub Integration**: Seamless GitHub and Copilot AI support
- **IDE Integration**: Support for VS Code, PyCharm, IntelliJ, Visual Studio, and more
- **Intelligent Audit**: Development audit with `!!!!` command for automated remediation
- **Process Monitoring**: Low-cost daemon prevents orphaned processes and resource leaks
- **Maintenance Automation**: Scheduled tasks for daily, weekly, and monthly operations

### Process Monitoring

Built-in background daemon that automatically:

- Tracks CodeSentinel-spawned processes
- Detects and terminates orphaned processes
- Cleans up zombie/defunct processes
- Minimal resource usage (<0.1% CPU, ~1-2MB memory)

Active whenever CodeSentinel is running to prevent resource leaks. See `docs/PROCESS_MONITOR.md` for details.

## Installation

```bash
pip install codesentinel
```

## Quick Start

```bash
# Run setup wizard
codesentinel-setup

# Check status
codesentinel status

# Run development audit
codesentinel !!!!
```

## Documentation

- [Installation Guide](INSTALLATION.md)
- [Security Policy](SECURITY.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Process Monitor](docs/PROCESS_MONITOR.md)
- [Changelog](CHANGELOG.md)

## Principles

**SECURITY > EFFICIENCY > MINIMALISM**

CodeSentinel follows a security-first approach with emphasis on efficiency and minimal overhead.
