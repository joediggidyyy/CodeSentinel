# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with the core principle: **SECURITY > EFFICIENCY > MINIMALISM**.

## Architecture Overview

The codebase follows a dual-architecture pattern:

- **`codesentinel/`** - Core Python package with CLI interface (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies
- **`tests/`** - Test suite using pytest with unittest fallback

## Key Components & Data Flow

### Maintenance System Architecture
- **MaintenanceScheduler** (`tools/codesentinel/scheduler.py`) - Central orchestration for daily/weekly/monthly tasks
- **AlertSystem** (`tools/codesentinel/alert_system.py`) - Multi-channel notifications (console, file, email, Slack)
- **Configuration Management** - JSON-based configs in `tools/config/` with environment variable support

### GUI Setup Wizard Enhancements
- **Enhanced Installation Location** (`tools/codesentinel/gui_setup_wizard.py`) - Step 2 improvements:
  - **Automatic Git repository detection** - Scans common development directories
  - **Quick repository selection** - One-click installation in detected Git repositories
  - **Intelligent path suggestions** - Displays relative paths and repository names
  - **Performance optimized** - Limited search depth and repository count
  - **Minimalist design** - Clean, intuitive interface with repository icons

- **Enhanced Alert System** (`tools/codesentinel/gui_setup_wizard.py`) - Step 5 improvements:
  - Fixed frame positioning issues causing next button to go out of frame
  - Added scrollable content area with mouse wheel support
  - Larger window size (800x700) for better visibility
  - Compact email configuration layout
  - Robust error handling with try-catch in navigation

- **Repository Integration Wizard** - Step 6 (GitHub Integration) major enhancement:
  - **Automatic repository detection** - Identifies non-git directories
  - **Three setup options**:
    1. **Initialize new Git repository** - Creates local repo + optional GitHub repo
    2. **Clone existing repository** - Downloads from GitHub URL
    3. **Connect existing repository** - Links local repo to GitHub remote
  - **GitHub repository creation** - Automated via GitHub CLI or manual instructions
  - **Complete workflow guidance** - Step-by-step instructions for GitHub.com integration
  - **Dynamic configuration display** - Changes based on selected option
  - **Error handling and validation** - Comprehensive error messages and fallbacks

- **Comprehensive IDE Integration** - Step 7 (IDE Integration) major enhancement:
  - **Multi-IDE detection** - Automatically detects 8 popular IDEs on the system
  - **Clear detection status** - Shows "✓ Detected" or "Not detected" for each IDE
  - **Installation assistance** - "Install Guide" buttons for undetected IDEs
  - **Supported IDEs**: VS Code, Visual Studio, PyCharm, IntelliJ IDEA, Sublime Text, Atom, Notepad++, Eclipse
  - **Installation guides** - Pop-up windows with step-by-step installation instructions
  - **Direct links** - "Open Website" buttons to official IDE download pages
  - **Extension recommendations** - Lists recommended CodeSentinel extensions for each IDE

- **Enhanced Optional Features** - Step 8 (Optional Features) major enhancement:
  - **Detailed feature explanations** - Comprehensive descriptions of each automation feature
  - **Smart recommendations** - Context-aware suggestions based on user's configuration
  - **Complexity indicators** - Beginner/Intermediate/Advanced labels for each feature
  - **Impact descriptions** - Clear explanations of what each feature accomplishes
  - **Expandable details** - Show/Hide toggles for feature descriptions
  - **Professional guidance** - Helps users make informed decisions about automation

### Task Execution Pipeline
1. **Change Detection** - Always runs first to fix broken workflows
2. **Formatting** - Code style and notebook formatting
3. **Testing** - Automated test suite execution  
4. **Reporting** - Status and maintenance reports
5. **Alerting** - Critical issue notifications

## Essential Development Commands

### GUI Setup Wizard Operations
```bash
# Launch enhanced GUI setup wizard
codesentinel-setup-gui

# Features include:
# - Scrollable interface for complex configurations
# - Repository setup wizard for non-git projects  
# - GitHub integration with automated repository creation
# - Email/Slack alert configuration with compact layout
```

### Repository Integration (GUI Step 6)
```bash
# Initialize new repository (if not in git repo)
# GUI wizard handles:
git init
git add .
git commit -m "Initial commit - CodeSentinel setup"
gh repo create <name> --public/--private --source . --push

# Clone existing repository
git clone <url> <directory>

# Connect to existing GitHub repository
git remote add origin <url>
git push -u origin main
```

### Maintenance Operations
```bash
# Daily maintenance workflow
python tools/codesentinel/scheduler.py --schedule daily

# Weekly maintenance (security, dependencies, performance)
python tools/codesentinel/scheduler.py --schedule weekly

# Monthly maintenance (comprehensive audit)
python tools/codesentinel/scheduler.py --schedule monthly

# Dry run to see what would execute
python tools/codesentinel/scheduler.py --schedule daily --dry-run

# Run specific task only
python tools/codesentinel/scheduler.py --task change_detection
```

### Alert System
```bash
# Check maintenance results and send alerts
python tools/codesentinel/alert_system.py --check-results <results_file>

# Test alert system configuration
python tools/codesentinel/alert_system.py --test
```

### Setup and Configuration
```bash
# Interactive terminal setup wizard
codesentinel-setup

# Enhanced GUI setup wizard (recommended)
codesentinel-setup-gui

# Core CLI operations
codesentinel status
codesentinel scan
```

## Configuration Files

### `tools/config/alerts.json`
Multi-channel alert configuration with SMTP, Slack, console, and file logging support. Contains actual email credentials (secured).

### `tools/config/scheduler.json`
Maintenance schedules with cron expressions, execution order, timeouts, and failure handling policies.

### Task Dependencies
- **Change detection MUST run first** - All other tasks depend on this
- **Fail-fast enabled** - Single task failure stops the entire workflow
- **Timeout protection** - Tasks have individual timeout limits (10-60 minutes)

## Development Patterns

### GUI Wizard Development
- **Scrollable content areas** - Use Canvas + Scrollbar for complex forms
- **Frame positioning** - Avoid relative positioning, use direct pack() calls
- **Error handling** - Wrap navigation methods in try-catch blocks
- **Dynamic content** - Use trace() on variables to update UI automatically
- **Repository integration** - Always check git status and provide setup options

### Testing Strategy
- **Primary**: pytest with `pytest.ini` configuration in project root
- **Fallback**: unittest via `run_tests.py` smart runner
- **Test discovery**: `test_*.py` files in `tests/` directory

### Error Handling & Logging
- Comprehensive logging with timestamps to `tools/monitoring/scheduler/`
- Task dependency validation before execution
- Graceful degradation for missing optional dependencies
- Multi-level logging (DEBUG, INFO, ERROR) with file rotation

### Security Conventions
- **No hardcoded credentials** - Environment variables or config files only
- **Audit logging** - All operations logged with timestamps
- **Configuration validation** - Auto-creation of missing configs with secure defaults
- **Dependency scanning** - Automated vulnerability detection

## Integration Points

### GitHub Integration
- Repository-aware configuration detection
- Copilot instructions generation (this file)
- PR review automation capabilities
- **Automated repository setup** - GUI wizard handles git init, GitHub repo creation, and remote configuration

### Multi-Platform Support  
- **Python 3.13/3.14 requirement** with backward compatibility
- **Cross-platform paths** using `pathlib.Path` consistently
- **PowerShell/Python dual execution** support for Windows/Unix

## GUI Wizard Usage Patterns

### Installation Location Configuration (Step 2)
- **Repository Detection**: Automatically scans ~/Documents, ~/Projects, ~/Code, and parent directories
- **Quick Selection**: One-click buttons for detected Git repositories
- **Smart Suggestions**: Shows repository names and relative paths
- **Performance Limits**: Searches max 10 repositories with 3-level depth
- **Fallback Options**: Manual directory selection and browse functionality

### Alert System Configuration (Step 5)
- **Email setup**: SMTP server, port, credentials, recipients
- **Slack integration**: Webhook URL, channel, bot name
- **Alert rules**: Security issues, task failures, dependency vulnerabilities
- **Compact layout**: Reduced form sizes to prevent overflow

### Repository Setup (Step 6)
- **Detection**: Automatically identifies non-git directories
- **Options**:
  - Initialize: Creates new local + GitHub repository
  - Clone: Downloads existing repository from URL
  - Connect: Links local repository to GitHub remote
- **GitHub CLI integration**: Automated repository creation when available
- **Fallback instructions**: Manual GitHub setup guidance when CLI unavailable

### IDE Integration (Step 7)
- **Automatic detection**: Scans system for 8 popular IDEs (VS Code, Visual Studio, PyCharm, IntelliJ, Sublime Text, Atom, Notepad++, Eclipse)
- **Detection feedback**: Clear status indicators for each IDE
- **Installation assistance**: Built-in guides for undetected IDEs
- **Extension recommendations**: Lists CodeSentinel-specific extensions for each IDE
- **Direct installation links**: One-click access to official IDE download pages

### Optional Features (Step 8)
- **Automated Maintenance Scheduling**: Cron jobs for daily/weekly/monthly maintenance tasks
- **Git Hooks Integration**: Pre-commit and pre-push validation (recommended for all developers)
- **CI/CD Workflow Templates**: GitHub Actions, GitLab CI, Azure DevOps pipeline templates
- **Smart Recommendations**: Context-aware suggestions based on user's Git repository and IDE setup
- **Complexity Guidance**: Beginner/Intermediate/Advanced labels help users choose appropriate features

## When Modifying This Codebase

1. **Understand the dual architecture** - Core package vs. tools scripts serve different purposes
2. **Maintain execution order** - Change detection dependency is critical
3. **Preserve configuration structure** - JSON configs have specific schemas
4. **Test both execution paths** - pytest and unittest must both work
5. **Update timeout values** carefully - Task timeouts affect workflow reliability
6. **Follow security-first principle** - Never compromise security for convenience
7. **GUI improvements** - Always test scrolling, navigation, and error handling
8. **Repository integration** - Ensure git operations are platform-compatible and error-resilient
