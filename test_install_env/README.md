# CodeSentinel Clean Installation Test Environment

This directory simulates a clean user environment for testing CodeSentinel installation.

## Directory Structure

```
test_install_env/
├── README.md (this file)
├── .venv/           (isolated virtual environment)
├── test_install.ps1 (automated test script)
└── test_results/    (installation results and logs)
```

## Usage

### Quick Test

```powershell
cd test_install_env
.\test_install.ps1
```

### Manual Test

```powershell
# 1. Create fresh virtual environment
python -m venv .venv

# 2. Activate environment
.\.venv\Scripts\Activate.ps1

# 3. Install CodeSentinel from parent directory
pip install -e ..

# 4. Run setup wizard
codesentinel-setup-gui
```

## What Gets Tested

1. **Fresh Python Environment**: Clean venv with no existing packages
2. **Dependency Installation**: All required packages install correctly
3. **Entry Points**: CLI commands work (`codesentinel`, `codesentinel-setup`)
4. **GUI Launcher**: Setup wizard launches without errors
5. **Configuration Creation**: Config files created properly
6. **Package Installation**: Full installation workflow

## Test Results

Results are saved to `test_results/` with timestamps:

- `install_log_YYYYMMDD_HHMMSS.txt` - Installation output
- `config_snapshot_YYYYMMDD_HHMMSS.json` - Created configuration
- `test_report_YYYYMMDD_HHMMSS.txt` - Test summary

## Cleanup

To reset the test environment:

```powershell
Remove-Item -Path .venv -Recurse -Force
Remove-Item -Path test_results -Recurse -Force
```

## Notes

- This environment is isolated from the main development environment
- Uses editable install (`pip install -e`) to test current code
- Simulates first-time user experience
- Does not affect system-wide Python packages
