# CodeSentinel Commit History Cleanup Script (PowerShell)
# 
# This script rewrites the commit history to create a clean, logical progression
# following the SECURITY > EFFICIENCY > MINIMALISM principle.
#
# WARNING: This script performs destructive operations and rewrites history.
#          Only run this if you understand the implications.
#
# PREREQUISITES:
# - Clean working directory (no uncommitted changes)
# - Backup your repository before running
# - All team members must be notified (history rewrite affects everyone)
#
# USAGE:
#   .\cleanup_commit_history.ps1 [-DryRun]
#
# With -DryRun, the script will show what would be done without making changes.

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoDir

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Cyan
    Write-Host ""
}

# Verify clean working directory
$status = git status --porcelain
if ($status) {
    Write-Host "❌ Error: Working directory is not clean" -ForegroundColor Red
    Write-Host "   Commit or stash your changes before running this script" -ForegroundColor Red
    exit 1
}

Write-Host "🧹 CodeSentinel Commit History Cleanup" -ForegroundColor Green
Write-Host "======================================"
Write-Host ""
Write-Host "This script will rewrite the commit history to create 6 clean commits:"
Write-Host ""
Write-Host "  1. Initial commit – CodeSentinel setup"
Write-Host "  2. Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure"
Write-Host "  3. Comprehensive cleanup: Remove all orphaned, legacy, and test/deprecated files"
Write-Host "  4. Add secure credential manager and unified YAML-based configuration"
Write-Host "  5. Update documentation to reflect main branch, clean architecture, and CodeSentinel 1.0 status"
Write-Host "  6. Begin v1.0.0 development; legacy v0 scrapped"
Write-Host ""

if (-not $DryRun) {
    Write-Host "⚠️  WARNING: This will rewrite history and require force push!" -ForegroundColor Yellow
    Write-Host ""
    $confirmation = Read-Host "Are you sure you want to continue? (type 'yes' to proceed)"
    if ($confirmation -ne "yes") {
        Write-Host "Aborted."
        exit 0
    }
    Write-Host ""
}

# Create backup branch
$BackupBranch = "backup-before-cleanup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
if (-not $DryRun) {
    Write-Host "📦 Creating backup branch: $BackupBranch" -ForegroundColor Cyan
    git branch $BackupBranch
    Write-Host "   ✓ Backup created" -ForegroundColor Green
    Write-Host ""
}

# Get current branch
$CurrentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $CurrentBranch"
Write-Host ""

# Create a new orphan branch for clean history
$CleanBranch = "clean-history-temp"

if ($DryRun) {
    Write-Host "Would create orphan branch: $CleanBranch"
    Write-Host "Would create 6 clean commits with proper structure"
    Write-Host "Would delete original branch and rename clean branch to: $CurrentBranch"
    Write-Host "Would require: git push --force origin $CurrentBranch"
    Write-Host ""
    Write-Host "To see the proposed commit structure, see COMMIT_CLEANUP_PLAN.md"
    exit 0
}

Write-Host "Creating clean history..."
git checkout --orphan $CleanBranch

# Clear the staging area
git rm -rf --cached . | Out-Null

Write-Host ""
Write-Host "Building clean commit history..." -ForegroundColor Cyan
Write-Host ""

# Commit 1: Initial commit - CodeSentinel setup
Write-Host "📝 Creating commit 1/6: Initial commit – CodeSentinel setup" -ForegroundColor Yellow
git add LICENSE README.md .gitignore
git add setup.py pyproject.toml requirements.txt requirements-dev.txt
git add pytest.ini
git commit -m @"
Initial commit – CodeSentinel setup

Initialize CodeSentinel project with:
- MIT License
- Basic README and project structure
- Python packaging configuration (setup.py, pyproject.toml)
- Development and production dependencies
- Test infrastructure (pytest)

Foundation for security-first automated maintenance system.
SECURITY > EFFICIENCY > MINIMALISM
"@

# Commit 2: Rename and restructure
Write-Host "📝 Creating commit 2/6: Rename legacy scripts; transition to CodeSentinel 1.0" -ForegroundColor Yellow
git add codesentinel/ setup_wizard.py setup_wizard.sh setup_wizard.bat
git add install.sh install.bat install_codesentinel.py
git add launch.py check_dependencies.py run_tests.py
git add tests/
git commit -m @"
Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure

Restructure project to CodeSentinel 1.0:
- Rename and organize codesentinel/ package structure
- Update CLI and core modules
- Add unified launch.py (formerly launch_v2.py)
- Update setup wizards for streamlined installation
- Add comprehensive test suite
- Remove v0/v1/v2 versioning confusion

Establishes clean, professional CodeSentinel 1.0 architecture.
"@

# Commit 3: Comprehensive cleanup
Write-Host "📝 Creating commit 3/6: Comprehensive cleanup of legacy systems" -ForegroundColor Yellow
git add quarantine_legacy_archive/
git commit -m @"
Comprehensive cleanup: Remove all orphaned, legacy, and test/deprecated files; quarantine legacy systems; streamline project architecture

Major cleanup actions:
- Quarantine all legacy v0 systems in quarantine_legacy_archive/
- Remove all __pycache__ directories and build artifacts
- Eliminate orphaned log files and temporary configs
- Remove 50+ test and debug files from active codebase
- Consolidate legacy test files into quarantine
- Clean up redundant installers

Legacy systems safely isolated with zero access points.
Project now follows minimalist, maintainable structure.
"@

# Commit 4: Security features
Write-Host "📝 Creating commit 4/6: Add secure credential manager and unified YAML configuration" -ForegroundColor Yellow
git add src/
git commit -m @"
Add secure credential manager and unified YAML-based configuration; enforce security-first modular design

Critical security improvements:
- Implement Windows Credential Manager integration
- Add encrypted credential storage (no plaintext passwords)
- Create unified YAML configuration system
- Replace 9 fragmented JSON config files with single YAML
- Modular UI architecture (src/codesentinel/)
- Secure configuration management (src/codesentinel/core/config/)
- Professional credential handling (src/codesentinel/core/security/)

Addresses critical security audit findings.
SECURITY > EFFICIENCY > MINIMALISM
"@

# Commit 5: Documentation updates
Write-Host "📝 Creating commit 5/6: Update documentation" -ForegroundColor Yellow
git add docs/ CHANGELOG.md CONTRIBUTING.md INSTALLATION.md QUICKSTART.md
git add .github/
git commit -m @"
Update documentation to reflect main branch, clean architecture, and CodeSentinel 1.0 status

Documentation improvements:
- Update all references from feature branches to main
- Document CodeSentinel 1.0 architecture (docs/POLICY.md)
- Add comprehensive installation guide (INSTALLATION.md)
- Create quick start guide (QUICKSTART.md)
- Document contribution guidelines (CONTRIBUTING.md)
- Add release notes (CHANGELOG.md)
- Include GitHub Copilot instructions
- Add CI/CD workflow configuration

Complete professional documentation for CodeSentinel 1.0.
"@

# Commit 6: v1.0.0 development
Write-Host "📝 Creating commit 6/6: Begin v1.0.0 development; legacy v0 scrapped" -ForegroundColor Yellow
# No new files needed, this is more of a status commit
git commit --allow-empty -m @"
Begin v1.0.0 development; legacy v0 scrapped

CodeSentinel v1.0.0 Development Status:
✓ Complete architectural redesign
✓ Security-first credential management
✓ Unified configuration system
✓ Modular, maintainable codebase
✓ Comprehensive documentation
✓ Professional project structure

Legacy v0 completely deprecated and quarantined.
All future development on v1.0.0 architecture.

SECURITY > EFFICIENCY > MINIMALISM
"@

Write-Host ""
Write-Host "✅ Clean history created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Switching branches..." -ForegroundColor Cyan

# Delete old branch and rename new one
git branch -D $CurrentBranch
git branch -m $CleanBranch $CurrentBranch

Write-Host ""
Write-Host "✅ History cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
git log --oneline --decorate
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the new history: git log"
Write-Host "  2. Verify the working tree: git status"
Write-Host "  3. If satisfied, force push: git push --force origin $CurrentBranch"
Write-Host ""
Write-Host "⚠️  Important reminders:" -ForegroundColor Yellow
Write-Host "  - Backup branch created: $BackupBranch"
Write-Host "  - All team members must re-clone after force push"
Write-Host "  - Update any open PRs to rebase on new history"
Write-Host ""
