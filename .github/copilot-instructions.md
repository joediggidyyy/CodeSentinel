<!-- 
This file is auto-organized by the instruction defragmentation utility.
Last organized: 2025-11-13 (Updated by agent analysis)
-->

CANONICAL_PROJECT_VERSION: "1.1.2"

````instructions
# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with SEAM Protection™:
**Security, Efficiency, And Minimalism** (with Security taking absolute priority).

## Project Architecture

CodeSentinel follows a **dual-architecture pattern** with clear separation of concerns:

### Core Package (`codesentinel/`)
- **Purpose**: Installable Python package (distributed via PyPI)
- **Entry Points**: 
  - `codesentinel` → `codesentinel.cli:main`
  - `codesentinel-setup` → `codesentinel.launcher:main`
  - `codesentinel-setup-gui` → `codesentinel.gui_launcher:main`
- **Structure**:
  - `cli/`: Command-line interface with modular `*_utils.py` pattern (see below)
  - `core/`: Business logic (DevAudit, CodeSentinel main class)
  - `utils/`: Shared utilities (session_memory, root_policy, ORACL™ components)
  - `gui/`: GUI components (setup wizard, project setup)

### Automation Layer (`tools/codesentinel/`)
- **Purpose**: Standalone maintenance and automation scripts
- **Key Scripts**:
  - `root_cleanup.py`: Root directory policy enforcement
  - `scheduler.py`: Automated task scheduling
  - `manage_satellites.py`: Distributed agent instruction management
  - `report_workflow.py`: Report generation and archival

### CLI Modularization Pattern
The CLI follows a **utility-based pattern** to avoid monolithic files:

```python
# codesentinel/cli/__init__.py (main entry point)
from .scan_utils import handle_scan_command
from .test_utils import handle_test_command
from .update_utils import perform_update
from .doc_utils import verify_documentation_branding
from .dev_audit_utils import run_tool_audit
# ... delegates to specialized utility modules

# Example: codesentinel/cli/scan_utils.py
def handle_scan_command(args, sentinel):
    """Handle 'codesentinel scan' command."""
    # Focused implementation for scan operations
```

**Pattern to Follow**: When adding CLI functionality, create or extend a `*_utils.py` module rather than adding hundreds of lines to `__init__.py`.

## ORACL™ Intelligence System

**ORACL™** (Omniscient Recommendation Archive & Curation Ledger) provides 3-tier intelligent context:

### Tier 1: Session Memory (ALWAYS USE FIRST)
- **Module**: `codesentinel/utils/session_memory.py`
- **Purpose**: In-memory cache for current task (0-60 min lifetime)
- **Usage Pattern**:
  ```python
  from codesentinel.utils.session_memory import SessionMemory
  
  session = SessionMemory()
  session.log_task(task_id=1, title="Task", status="in-progress")
  
  # Check cache before reading files
  cached = session.get_file_context("path/to/file.py")
  if cached:
      content = cached['content']
  else:
      content = read_file("path/to/file.py")
      session.cache_file_context("path/to/file.py", {"summary": "..."}, content)
  
  session.log_decision(decision="What", rationale="Why", related_files=["file.py"])
  session.log_task(task_id=1, title="Task", status="completed")
  ```
- **Performance Target**: >60% cache hit rate, <2MB session size

### Tier 2: Context Tier
- **Module**: `codesentinel/utils/oracl_context_tier.py`
- **Purpose**: 7-day rolling window of recent session summaries
- **Use Case**: Understanding recent work context across sessions

### Tier 3: Intelligence Tier
- **Modules**: `archive_decision_provider.py`, `archive_index_manager.py`
- **Purpose**: Long-term pattern recognition and strategic recommendations
- **Use Case**: High-impact decisions requiring historical wisdom

**Rule**: Start with Tier 1 (session memory) for ALL multi-step tasks. Only query higher tiers when you need broader context.

## Core Principles (SEAM Protection™)

### SECURITY (Priority #1)
- No hardcoded credentials - Environment variables or config files only
- All operations logged with timestamps to `logs/` directory
- Configuration validation with auto-creation of secure defaults
- Automated vulnerability detection via `codesentinel scan`

### EFFICIENCY (Priority #2)
- **DRY Principle**: MANDATORY code reuse and modularization
  - Consolidate duplicate implementations into shared utilities (`codesentinel/utils/`)
  - Extract common patterns into reusable functions
  - Import from single source of truth (e.g., `root_policy.py` for root directory policy)
- Session memory caching reduces file re-reads by 60-74%

### MINIMALISM (Priority #3)
- Archive deprecated code to `quarantine_legacy_archive/` (NEVER delete directly)
- Single source of truth for each feature
- Remove unnecessary dependencies
- `codesentinel clean` commands for artifact removal

## Critical Policies (NON-NEGOTIABLE)

### 1. Non-Destructive Operations
**RULE**: Never delete files/directories without archiving first.

```python
# ✅ CORRECT: Archive-first pattern
archive_dir = Path("quarantine_legacy_archive")
archive_dir.mkdir(exist_ok=True)
shutil.move(str(item), str(archive_dir / item.name))

# ❌ FORBIDDEN: Direct deletion
item.unlink()  # NEVER DO THIS
shutil.rmtree(item)  # NEVER DO THIS
```

All file operations must:
- Archive to `quarantine_legacy_archive/` first
- Ask user permission (unless `--force` with clear documentation)
- Provide recovery option
- Log all operations

### 2. Python 3.8+ Type Annotation Compatibility
**CRITICAL**: CodeSentinel supports Python 3.8+. Use uppercase generic types from `typing` module.

```python
# ✅ CORRECT (Python 3.8 compatible)
from typing import Tuple, List, Dict, Set, Optional

def func() -> Tuple[bool, List[str]]:
    return True, ["item"]

# ❌ FORBIDDEN (Python 3.9+ only, breaks 3.8)
def func() -> tuple[bool, list[str]]:  # TypeError in Python 3.8
    return True, ["item"]
```

### 3. Cross-Platform Output (ASCII-Only Console)
**RULE**: NEVER use Unicode symbols in `print()` or `logger.*()` statements.

**Why**: Windows console (cp1252) cannot display Unicode, causing `UnicodeEncodeError` crashes.

```python
# ✅ APPROVED symbols
print("[OK] Success")
print("[FAIL] Error")
print("[WARN] Warning")
print("-> Processing")

# ❌ FORBIDDEN symbols (cause crashes on Windows)
print("✓ Success")  # NEVER
print("✗ Error")    # NEVER
print("→ Processing")  # NEVER
```

**Exception**: Markdown files (`.md`) and file content CAN use UTF-8/Unicode safely.

### 4. Repository-Relative Paths
All user-facing output must show paths relative to repository root with repo name prefix:

```python
# ✅ CORRECT
print("Report: CodeSentinel/docs/reports/audit.md")

# ❌ WRONG
print("Report: C:\\Users\\joedi\\Documents\\CodeSentinel\\docs\\reports\\audit.md")
```

## Development Workflows

### Build and Test
```bash
# Run tests (pytest preferred, unittest fallback)
python run_tests.py
# OR
pytest tests/ --tb=short --verbose

# Build package
python -m build

# Install in development mode
pip install -e .
```

### Interactive Beta Testing
```bash
# Run interactive test wizard (8-step protocol)
codesentinel test --interactive

# Automated CI/CD mode
codesentinel test --automated
```

Test suite generates reports in `tests/beta_testing/{version}/iterations/` with session management and state persistence.

### Root Directory Policy
Root directory policy is centralized in `codesentinel/utils/root_policy.py`:

```python
from codesentinel.utils.root_policy import (
    ALLOWED_ROOT_FILES,  # Set of allowed filenames
    ALLOWED_ROOT_DIRS,   # Set of allowed directory names
    FILE_MAPPINGS        # Pattern → target directory mapping
)
```

**DON'T** duplicate these constants elsewhere. Import from `root_policy.py`.

### Development Audit Command
```bash
# Interactive audit with detailed report
codesentinel !!!!

# Agent-friendly context for remediation (JSON output)
codesentinel !!!! --agent
```

The `!!!!` command provides SEAM-aligned audit results with:
- Security violations (high priority)
- Efficiency issues (duplicate code, bloat)
- Minimalism violations (unnecessary files)
- Remediation hints with confidence scores

## Key File Locations

### Configuration
- `codesentinel.json`: User-editable main config (created by setup wizard)
- `tools/config/`: JSON configs for alerts, scheduling, policies

### Code Organization
- `codesentinel/cli/*_utils.py`: CLI command implementations (modular pattern)
- `codesentinel/utils/`: Shared utilities (import from here, don't duplicate)
- `tools/codesentinel/`: Standalone automation scripts
- `quarantine_legacy_archive/`: Archived code (excluded from cleanup checks)

### Documentation
- `docs/architecture/`: Architecture decisions and design docs
- `docs/reports/`: Generated reports and audit results
- `docs/guides/`: User guides and reference material
- `README.md`: Primary user-facing documentation

### Testing
- `tests/`: Test suite (pytest framework)
- `tests/beta_testing/`: Interactive test wizard sessions and reports
- `run_tests.py`: Test runner with pytest/unittest fallback

## Common Tasks

### Adding a New CLI Command
1. Create or extend a `codesentinel/cli/*_utils.py` module
2. Implement handler function: `def handle_X_command(args, sentinel):`
3. Import and call from `codesentinel/cli/__init__.py` main parser
4. Add argparse subcommand and route to handler

### Adding Shared Utility
1. Check if similar functionality exists in `codesentinel/utils/`
2. If consolidating duplicate code, create new module in `utils/`
3. Import and use from single location (maintain DRY principle)
4. Add type hints using Python 3.8 compatible syntax

### Working with Session Memory
1. Initialize at task start: `session = SessionMemory()`
2. Check cache before file reads: `cached = session.get_file_context(path)`
3. Log decisions: `session.log_decision(decision, rationale, related_files)`
4. Track tasks: `session.log_task(id, title, status)`
5. Session auto-saves and promotes to Context Tier on exit

### Implementing Cleanup Operation
1. NEVER delete directly - archive to `quarantine_legacy_archive/`
2. Implement `--dry-run` flag for preview
3. Add user confirmation prompt (unless `--force`)
4. Log all operations to audit trail
5. Provide recovery instructions

## Integration Points

### GitHub Integration
- `.github/copilot-instructions.md`: This file (auto-organized by defragmentation utility)
- Repository-aware configuration detection
- PR review automation capabilities (future)

### VS Code Integration
- Copilot reads this file for context-aware suggestions
- Process monitor tracks background tasks
- Alert system supports file-based notifications

### Multi-Platform Support
- Windows, macOS, Linux compatibility
- PowerShell/cmd.exe/bash/zsh support
- Cross-platform paths using `pathlib.Path` consistently
- ASCII-only console output for universal compatibility

## Version Management

Current version: **1.1.2** (synchronized across):
- `pyproject.toml`
- `setup.py`
- `codesentinel/__init__.py`
- `CHANGELOG.md`

Update version with: `codesentinel update version --set-version X.Y.Z`

---

## Quick Reference

| What | Command/Module |
|------|---------------|
| Run audit | `codesentinel !!!!` |
| Security scan | `codesentinel scan` |
| Clean artifacts | `codesentinel clean --cache --test --build` |
| Root cleanup | `codesentinel clean --root` |
| Session memory | `from codesentinel.utils.session_memory import SessionMemory` |
| Root policy | `from codesentinel.utils.root_policy import ALLOWED_ROOT_FILES` |
| Interactive test | `codesentinel test --interactive` |
| Build package | `python -m build` |
| Run tests | `python run_tests.py` |

---

**Remember**: 
1. Session memory for multi-step tasks (ALWAYS)
2. Archive before delete (NEVER skip)
3. ASCII-only console output (Windows compatibility)
4. Python 3.8+ type annotations (uppercase generics)
5. DRY principle (import, don't duplicate)

---
````
```
