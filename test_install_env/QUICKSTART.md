# Quick Start Guide - Clean Installation Test

## Windows (PowerShell)

```powershell
cd test_install_env
.\test_install.ps1
```

### With Options

```powershell
# Verbose output
.\test_install.ps1 -Verbose

# Keep environment after test
.\test_install.ps1 -KeepEnvironment
```

## Linux/macOS (Bash)

```bash
cd test_install_env
./test_install.sh
```

## What Happens

1. ✓ Removes any existing test environment
2. ✓ Creates fresh Python virtual environment
3. ✓ Installs latest pip
4. ✓ Installs CodeSentinel in editable mode
5. ✓ Verifies package installation
6. ✓ Tests CLI entry points (`codesentinel`, `codesentinel-setup`)
7. ✓ Verifies module imports
8. ✓ Checks all dependencies (psutil, requests, tkinter)
9. ✓ Generates detailed test report

## Results Location

All test results are saved in `test_results/` with timestamps:

- Installation logs
- Test reports
- Configuration snapshots

## Manual Testing After Automated Tests

Once automated tests pass, manually test:

```powershell
# Activate the test environment
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/macOS

# Launch GUI wizard
codesentinel-setup-gui

# Test CLI commands
codesentinel --help
codesentinel !!!!
```

## Cleanup

```powershell
# Remove test environment
Remove-Item -Path .venv -Recurse -Force
Remove-Item -Path test_results -Recurse -Force
```

## Expected Output

```
============================================================
CLEAN INSTALLATION TEST STARTING
============================================================
[HH:MM:SS] Test directory: ...\test_install_env
[HH:MM:SS] Testing: Remove old virtual environment
[HH:MM:SS] ✓ PASS: Remove old virtual environment
...
[HH:MM:SS] ✓ ALL TESTS PASSED - Installation successful!

Next steps:
  1. Run: codesentinel-setup-gui
  2. Complete the setup wizard
  3. Test: codesentinel !!!!
```

## Troubleshooting

### Python Not Found

Ensure Python 3.13+ is installed and in PATH:

```powershell
python --version
```

### Permission Denied (Linux/macOS)

Make script executable:

```bash
chmod +x test_install.sh
```

### Virtual Environment Creation Failed

Check Python venv module:

```bash
python -m venv --help
```

### Import Errors

Ensure all dependencies install:

```bash
pip list
pip show codesentinel
```
