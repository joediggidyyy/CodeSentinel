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
├── requirements/                      (dev requirements)
│   └── requirements-dev.txt
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
│   ├── audit/                         (audit reports)
│   ├── reports/                       (completion and summary reports)
│   ├── planning/                      (roadmaps, plans, strategies)
│   ├── quick_reference/               (one-page reference cards)
│   ├── ADVANCED_ANALYTICS_FRAMEWORK.md
│   ├── ENTERPRISE_INTEGRATION_GUIDE.md
│   ├── V1_0_3_DISTRIBUTION_REPORT.md
│   ├── V1_0_3_BETA_TEST_REPORT.md
│   ├── PYPI_PUBLICATION_GUIDE.md
│   └── [other reference files]
│
├── logs/                              (integrity and operational logs)
│   ├── .codesentinel_integrity.json
│   ├── .test_integrity.json
│   └── codesentinel.log
│
├── scripts/                           (utility scripts)
│   └── publish_to_pypi.py
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
- **Audit Reports**: All audit and phase completion reports are now in `docs/audit/` and `docs/reports/`.
- **Planning Documents**: Roadmaps, strategies, and plans are in `docs/planning/`.

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

## Compliance Policy: Intelligent Duplicate Handling

CodeSentinel enforces a non-destructive, security-first compliance workflow for all documentation and operational files:

- **Intelligent Duplicate Analysis**: For every file type, root and subdirectory copies are compared. If identical, only the subdirectory copy is kept and the root duplicate is deleted. If different, files are merged intelligently (latest, most complete, or manual review if ambiguous).
- **Archiving**: Legacy or ambiguous versions are archived before any deletion, preserving audit trails and preventing data loss.
- **Placement and Cleanup**: The correct, merged, or latest file is placed in the appropriate subdirectory. Redundant root copies are deleted after verification.
- **Documentation Update**: README and .gitignore are updated to reflect this policy and ensure transparency.

This policy guarantees repo hygiene, auditability, and alignment with CodeSentinel's core principles: SECURITY > EFFICIENCY > MINIMALISM.

## Permanent Global Policy Amendment: Duplication Mitigation

- Duplicates are to be merged or deleted if and only if:
  - Data preservation is guaranteed (no unique content lost).
  - Minimalism is enforced (no unnecessary files or redundancy).
- Intelligent analysis (automated or manual) must be performed before any merger or deletion.
- Legacy or ambiguous versions are archived if needed, but redundant files are removed to maintain a clean, minimal, and secure codebase.
- This amendment is permanent and global, superseding previous non-destructive-only rules where duplication is present.
- See [docs/architecture/POLICY.md](docs/architecture/POLICY.md) for full details (Constitutional Tier).

**Integration:**

- All CodeSentinel satellites, domains, and governance tiers must comply.
- All automation, audits, and agent-driven workflows must implement this policy.
- The system remains whole, secure, and improved, with minimalism as a core principle.
