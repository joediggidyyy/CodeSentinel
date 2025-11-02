# CodeSentinel Installation Pipeline Documentation

## Overview

CodeSentinel now has a comprehensive installation pipeline that handles all dependencies, PATH configuration, and provides multiple installation methods.

## Installation Components

### Core Installers

1. **`install.py`** - Main enhanced installer with 8-step process:
   - Python version checking (3.13+)
   - Automatic pip installation via ensurepip
   - Core dependency validation
   - Requirements installation
   - Package installation in development mode
   - PATH configuration
   - Installation testing
   - Usage instructions

2. **`install.bat`** (Windows) and **`install.sh`** (Unix) - Platform-specific wrappers

3. **`check_dependencies.py`** - Standalone dependency checker with:
   - Python version validation
   - pip availability checking
   - Core module verification (20 modules)
   - Required package checking (requests, schedule)
   - Optional package detection (pytest, mypy, black, flake8)
   - Build tool verification (setuptools, wheel)
   - System tool detection (git, python)
   - Multiple output formats (normal, quiet, JSON)

### Configuration Tools

4. **`tools/codesentinel/path_configurator.py`** - Comprehensive PATH management:
   - Automatic scripts directory detection
   - Current session PATH configuration
   - Permanent setup instructions for all shells
   - Platform-specific handling (Windows/Unix)

5. **`tools/codesentinel/gui_setup_wizard.py`** - GUI configuration wizard (tkinter-based)

### Requirements Management

6. **`requirements.txt`** - Core runtime dependencies:
   - requests>=2.25.0 (HTTP/Slack alerts)
   - schedule>=1.1.0 (automation)
   - pathlib2>=2.3.0 (Python <3.4 compatibility)

7. **`requirements-dev.txt`** - Development dependencies:
   - Testing: pytest, pytest-cov, pytest-mock
   - Code quality: flake8, black, mypy
   - Documentation: sphinx, sphinx-rtd-theme
   - Build tools: twine, wheel, setuptools

## Installation Methods

### Method 1: Enhanced Installer (Recommended)

```bash
python install.py
```

- Handles all dependencies automatically
- Configures PATH
- Provides comprehensive error messages
- Tests installation completion

### Method 2: Platform-Specific Scripts

```bash
# Windows
install.bat

# Unix/Linux/macOS
chmod +x install.sh
./install.sh
```

### Method 3: Dependency Check First

```bash
# Check system readiness
python check_dependencies.py

# If all clear, run installer
python install.py
```

### Method 4: Manual Installation

```bash
pip install -e .
python tools/codesentinel/path_configurator.py
```

## Dependency Resolution

### Automatic pip Installation

The installer now uses Python's built-in `ensurepip` module to automatically install pip if it's missing, resolving the primary blocking issue.

### Core Dependency Matrix

| Component | Package | Required | Auto-Install | Fallback |
|-----------|---------|----------|--------------|----------|
| HTTP/Alerts | requests | Yes | Yes | Manual |
| Scheduling | schedule | No | Yes | Limited functionality |
| GUI | tkinter | No | Built-in | CLI only |
| Testing | pytest | No | Dev only | unittest |
| Formatting | black | No | Dev only | Manual |
| Linting | flake8 | No | Dev only | Manual |

### Build Dependencies

- pip (auto-installed via ensurepip)
- setuptools (upgraded automatically)
- wheel (installed automatically)

## PATH Configuration

### Current Session

The installer automatically adds Python Scripts directory to the current session PATH, enabling immediate CLI usage.

### Permanent Configuration

Provides shell-specific instructions for:

- **Windows**: PowerShell profile, Command Prompt registry
- **Unix/Linux**: .bashrc, .zshrc, .profile
- **macOS**: .bash_profile, .zshrc

## Error Handling & Troubleshooting

### Common Issues Resolved

1. **Missing pip**: Auto-installed via ensurepip
2. **PATH not configured**: Automatic detection and setup
3. **Import errors**: Package structure fixes with **init**.py files
4. **Permission issues**: Provides --user installation guidance
5. **Platform differences**: Unified cross-platform handling

### Diagnostic Tools

- `check_dependencies.py --quiet` for CI/automation
- `check_dependencies.py --json` for programmatic integration
- Comprehensive error messages with specific remediation steps

## Testing & Validation

### Installation Testing

The installer validates:

- Package import capability
- CLI command availability
- Setup wizard functionality
- GUI wizard accessibility

### Continuous Integration

- Exit codes for automation (0 = success, 1 = failure)
- JSON output for parsing
- Quiet mode for minimal output

## Next Steps

After successful installation:

1. Run setup wizard: `codesentinel-setup` or `codesentinel-setup-gui`
2. Configure alerts: Edit `tools/config/alerts.json`
3. Set maintenance schedule: Edit `tools/config/scheduler.json`
4. Test functionality: `codesentinel status`

## Architecture Integration

This installation pipeline integrates with CodeSentinel's dual architecture:

- **Core package** (`codesentinel/`) gets proper CLI entry points
- **Tools scripts** (`tools/codesentinel/`) become accessible via PATH
- **Configuration files** (`tools/config/`) are created with defaults
- **Testing framework** works with both pytest and unittest

The installation system ensures that regardless of the user's Python environment state, CodeSentinel can be successfully installed and configured for immediate use.
