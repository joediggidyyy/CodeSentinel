# CodeSentinel Utils

This directory contains utility modules that provide core functionality for CodeSentinel.

## Modules

### alerts.py

Alert system management for multi-channel notifications (console, file, email, Slack).

### config.py

Configuration file management and validation.

### scheduler.py

Maintenance task scheduling and automation.

### path_resolver.py

Path resolution utilities for cross-platform compatibility.

### process_monitor.py ⚠️ PERMANENT

**This is a permanent core function that must never be removed.**

Low-cost daemon for monitoring and cleaning up orphan processes. This module:

- Automatically starts with CodeSentinel initialization
- Runs in background thread with minimal resource usage
- Prevents resource leaks from orphaned processes
- Cleans up zombie/defunct processes
- Required dependency: `psutil`

**Critical**: This functionality prevents security and efficiency issues by ensuring
no orphaned processes consume system resources. It is integrated into the core
CodeSentinel class and CLI, and must persist through all versions.

See `docs/PROCESS_MONITOR.md` for detailed documentation.

## Permanent Functions

Modules marked with ⚠️ PERMANENT are critical infrastructure that must be maintained
in all versions of CodeSentinel. These are documented in:

- `.github/copilot-instructions.md`
- Individual module docstrings
- `docs/` directory

When refactoring or updating CodeSentinel:

1. Never remove permanent core functions
2. Maintain backward compatibility for these modules
3. Document any configuration changes
4. Ensure tests cover permanent functionality
