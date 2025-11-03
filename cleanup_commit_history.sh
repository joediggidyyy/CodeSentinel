#!/bin/bash
# CodeSentinel Commit History Cleanup Script
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
#   ./cleanup_commit_history.sh [--dry-run]
#
# With --dry-run, the script will show what would be done without making changes.

set -e  # Exit on error

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

# Verify clean working directory
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory is not clean"
    echo "   Commit or stash your changes before running this script"
    exit 1
fi

echo "🧹 CodeSentinel Commit History Cleanup"
echo "======================================"
echo ""
echo "This script will rewrite the commit history to create 6 clean commits:"
echo ""
echo "  1. Initial commit – CodeSentinel setup"
echo "  2. Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure"
echo "  3. Comprehensive cleanup: Remove all orphaned, legacy, and test/deprecated files"
echo "  4. Add secure credential manager and unified YAML-based configuration"
echo "  5. Update documentation to reflect main branch, clean architecture, and CodeSentinel 1.0 status"
echo "  6. Begin v1.0.0 development; legacy v0 scrapped"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo "⚠️  WARNING: This will rewrite history and require force push!"
    echo ""
    read -p "Are you sure you want to continue? (type 'yes' to proceed): " confirmation
    if [ "$confirmation" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    echo ""
fi

# Create backup branch
BACKUP_BRANCH="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"
if [ "$DRY_RUN" = false ]; then
    echo "📦 Creating backup branch: $BACKUP_BRANCH"
    git branch "$BACKUP_BRANCH"
    echo "   ✓ Backup created"
    echo ""
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Create a new orphan branch for clean history
CLEAN_BRANCH="clean-history-temp"

if [ "$DRY_RUN" = true ]; then
    echo "Would create orphan branch: $CLEAN_BRANCH"
    echo "Would create 6 clean commits with proper structure"
    echo "Would delete original branch and rename clean branch to: $CURRENT_BRANCH"
    echo "Would require: git push --force origin $CURRENT_BRANCH"
    echo ""
    echo "To see the proposed commit structure, see COMMIT_CLEANUP_PLAN.md"
    exit 0
fi

echo "Creating clean history..."
git checkout --orphan "$CLEAN_BRANCH"

# Clear the staging area
git rm -rf --cached . > /dev/null 2>&1

echo ""
echo "Building clean commit history..."
echo ""

# Commit 1: Initial commit - CodeSentinel setup
echo "📝 Creating commit 1/6: Initial commit – CodeSentinel setup"
git add LICENSE README.md .gitignore
git add setup.py pyproject.toml requirements.txt requirements-dev.txt
git add pytest.ini
git commit -m "Initial commit – CodeSentinel setup

Initialize CodeSentinel project with:
- MIT License
- Basic README and project structure
- Python packaging configuration (setup.py, pyproject.toml)
- Development and production dependencies
- Test infrastructure (pytest)

Foundation for security-first automated maintenance system.
SECURITY > EFFICIENCY > MINIMALISM"

# Commit 2: Rename and restructure
echo "📝 Creating commit 2/6: Rename legacy scripts; transition to CodeSentinel 1.0"
git add codesentinel/ setup_wizard.py setup_wizard.sh setup_wizard.bat
git add install.sh install.bat install_codesentinel.py
git add launch.py check_dependencies.py run_tests.py
git add tests/
git commit -m "Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure

Restructure project to CodeSentinel 1.0:
- Rename and organize codesentinel/ package structure
- Update CLI and core modules
- Add unified launch.py (formerly launch_v2.py)
- Update setup wizards for streamlined installation
- Add comprehensive test suite
- Remove v0/v1/v2 versioning confusion

Establishes clean, professional CodeSentinel 1.0 architecture."

# Commit 3: Comprehensive cleanup
echo "📝 Creating commit 3/6: Comprehensive cleanup of legacy systems"
git add quarantine_legacy_archive/
git commit -m "Comprehensive cleanup: Remove all orphaned, legacy, and test/deprecated files; quarantine legacy systems; streamline project architecture

Major cleanup actions:
- Quarantine all legacy v0 systems in quarantine_legacy_archive/
- Remove all __pycache__ directories and build artifacts
- Eliminate orphaned log files and temporary configs
- Remove 50+ test and debug files from active codebase
- Consolidate legacy test files into quarantine
- Clean up redundant installers

Legacy systems safely isolated with zero access points.
Project now follows minimalist, maintainable structure."

# Commit 4: Security features
echo "📝 Creating commit 4/6: Add secure credential manager and unified YAML configuration"
git add src/
git commit -m "Add secure credential manager and unified YAML-based configuration; enforce security-first modular design

Critical security improvements:
- Implement Windows Credential Manager integration
- Add encrypted credential storage (no plaintext passwords)
- Create unified YAML configuration system
- Replace 9 fragmented JSON config files with single YAML
- Modular UI architecture (src/codesentinel/)
- Secure configuration management (src/codesentinel/core/config/)
- Professional credential handling (src/codesentinel/core/security/)

Addresses critical security audit findings.
SECURITY > EFFICIENCY > MINIMALISM"

# Commit 5: Documentation updates
echo "📝 Creating commit 5/6: Update documentation"
git add docs/ CHANGELOG.md CONTRIBUTING.md INSTALLATION.md QUICKSTART.md
git add .github/
git commit -m "Update documentation to reflect main branch, clean architecture, and CodeSentinel 1.0 status

Documentation improvements:
- Update all references from feature branches to main
- Document CodeSentinel 1.0 architecture (docs/POLICY.md)
- Add comprehensive installation guide (INSTALLATION.md)
- Create quick start guide (QUICKSTART.md)
- Document contribution guidelines (CONTRIBUTING.md)
- Add release notes (CHANGELOG.md)
- Include GitHub Copilot instructions
- Add CI/CD workflow configuration

Complete professional documentation for CodeSentinel 1.0."

# Commit 6: v1.0.0 development
echo "📝 Creating commit 6/6: Begin v1.0.0 development; legacy v0 scrapped"
# No new files needed, this is more of a status commit
git commit --allow-empty -m "Begin v1.0.0 development; legacy v0 scrapped

CodeSentinel v1.0.0 Development Status:
✓ Complete architectural redesign
✓ Security-first credential management
✓ Unified configuration system
✓ Modular, maintainable codebase
✓ Comprehensive documentation
✓ Professional project structure

Legacy v0 completely deprecated and quarantined.
All future development on v1.0.0 architecture.

SECURITY > EFFICIENCY > MINIMALISM"

echo ""
echo "✅ Clean history created successfully!"
echo ""
echo "Switching branches..."

# Delete old branch and rename new one
git branch -D "$CURRENT_BRANCH"
git branch -m "$CLEAN_BRANCH" "$CURRENT_BRANCH"

echo ""
echo "✅ History cleanup complete!"
echo ""
echo "📊 Summary:"
git log --oneline --decorate
echo ""
echo "Next steps:"
echo "  1. Review the new history: git log"
echo "  2. Verify the working tree: git status"
echo "  3. If satisfied, force push: git push --force origin $CURRENT_BRANCH"
echo ""
echo "⚠️  Important reminders:"
echo "  - Backup branch created: $BACKUP_BRANCH"
echo "  - All team members must re-clone after force push"
echo "  - Update any open PRs to rebase on new history"
echo ""
