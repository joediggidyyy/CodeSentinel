# CodeSentinel - Quick Start

## Security-First Automated Maintenance and Monitoring

## Installation Options

### Option 1: From Source Code (Current)

**You have the CodeSentinel source code** - use the setup wizard:

```bash
python setup_wizard.py
```

**Windows:** Double-click `setup_wizard.bat`  
**Unix/Linux/macOS:** Run `./setup_wizard.sh`

### Option 2: Standalone Dependencies Only

**You need just the dependencies** - use the standalone installer:

```bash
python install_codesentinel.py
```

This installs PyYAML, keyring, cryptography without requiring source code.

## What Each Installer Does

### setup_wizard.py (Source Installation)

1. ✓ Checks system requirements (Python 3.7+)
2. ✓ Installs dependencies (PyYAML, keyring, cryptography)  
3. ✓ Installs CodeSentinel from source (`pip install -e .`)
4. ✓ Launches project configuration

### install_codesentinel.py (Standalone)

1. ✓ Checks system requirements (Python 3.7+)
2. ✓ Installs dependencies only
3. ✓ Provides next steps for manual setup

## Manual Installation

If you prefer command line:

```bash
# Install dependencies only
pip install PyYAML keyring cryptography

# If you have source code, install CodeSentinel
pip install -e .

# Run project setup
python launch.py
```

## Architecture

**SECURITY > EFFICIENCY > MINIMALISM**

---

*For detailed documentation, see the full README.md*
