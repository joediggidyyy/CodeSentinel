# Commit History Cleanup Plan

## Overview

This document outlines the plan to clean up the CodeSentinel repository's commit history, transforming 12 messy commits with intermediate states, deleted file references, and confusing progression into 6 clean, logical commits that tell a clear story.

## Current State (12 commits on main branch)

The current commit history includes:

1. `7ca048b` - Initial commit (GitHub-generated)
2. `f057045` - Initial commit - CodeSentinel setup (duplicate)
3. `5dd95ea` - Resolve merge conflicts and add functionality mapping
4. `06b0d6e` - feat: Initialize CodeSentinel v2.0 architecture
5. `325011f` - docs: Add v2.0 launcher and documentation
6. `3b0b611` - fix: Improve graceful handling of missing requirements
7. `87dc848` - feat: Rename v2 to main version - CodeSentinel 1.0
8. `4abcfb3` - docs: Update architecture to reflect main branch status
9. `66b58ce` - feat: Complete audit and quarantine of all legacy v0 systems
10. `7cd901f` - chore: Complete cleanup of orphans and testing artifacts
11. `56a01b0` - AUDIT: Remove redundant installers
12. `ed5c8ef` - v0 scrapped; v1.0.0 in development

## Problems with Current History

- **Duplicate initial commits**: Two separate "Initial commit" entries
- **References to deleted files**: Commits mention files that were later removed
- **Intermediate states preserved**: Shows v2 naming, then renaming to v1, causing confusion
- **Unclear progression**: Merge conflicts, fixes, and architectural changes interleaved
- **Redundant commit messages**: Multiple commits doing similar cleanup tasks
- **Version confusion**: References to v0, v1, v2 when only v1.0 is the current version

## Proposed Clean History (6 commits)

### Commit 1: Initial commit – CodeSentinel setup
**Files**: LICENSE, README.md, .gitignore, setup.py, pyproject.toml, requirements.txt, requirements-dev.txt, pytest.ini

**Purpose**: Establish the project foundation with licensing, basic configuration, and dependency management.

**Message**:
```
Initial commit – CodeSentinel setup

Initialize CodeSentinel project with:
- MIT License
- Basic README and project structure  
- Python packaging configuration (setup.py, pyproject.toml)
- Development and production dependencies
- Test infrastructure (pytest)

Foundation for security-first automated maintenance system.
SECURITY > EFFICIENCY > MINIMALISM
```

### Commit 2: Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure
**Files**: codesentinel/, setup_wizard.py, setup_wizard.sh, setup_wizard.bat, install.sh, install.bat, install_codesentinel.py, launch.py, check_dependencies.py, run_tests.py, tests/

**Purpose**: Establish the main codesentinel package structure and installation/launch scripts. This commit represents the transition from any legacy naming to the clean CodeSentinel 1.0 structure.

**Message**:
```
Rename legacy scripts and folders; transition to CodeSentinel 1.0 structure

Restructure project to CodeSentinel 1.0:
- Rename and organize codesentinel/ package structure
- Update CLI and core modules
- Add unified launch.py (formerly launch_v2.py)
- Update setup wizards for streamlined installation
- Add comprehensive test suite
- Remove v0/v1/v2 versioning confusion

Establishes clean, professional CodeSentinel 1.0 architecture.
```

### Commit 3: Comprehensive cleanup - Remove all orphaned, legacy, and test/deprecated files; quarantine legacy systems
**Files**: quarantine_legacy_archive/

**Purpose**: Isolate all legacy systems, test files, and deprecated code into a quarantine directory. This represents the consolidation of all cleanup operations (removes __pycache__, legacy configs, orphaned files, test/debug files).

**Message**:
```
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
```

### Commit 4: Add secure credential manager and unified YAML-based configuration; enforce security-first modular design
**Files**: src/

**Purpose**: Implement the security-first architecture with encrypted credential storage and unified configuration. This addresses critical security audit findings.

**Message**:
```
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
```

### Commit 5: Update documentation to reflect main branch, clean architecture, and CodeSentinel 1.0 status
**Files**: docs/, CHANGELOG.md, CONTRIBUTING.md, INSTALLATION.md, QUICKSTART.md, .github/

**Purpose**: Provide comprehensive documentation reflecting the current state of the project, including architecture, installation, contribution guidelines, and CI/CD configuration.

**Message**:
```
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
```

### Commit 6: Begin v1.0.0 development; legacy v0 scrapped
**Files**: (empty commit - status marker)

**Purpose**: Mark the official start of v1.0.0 development with all legacy versions deprecated. This is a milestone commit that clearly states the project status.

**Message**:
```
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
```

## Benefits of Clean History

1. **Clear progression**: Logical flow from setup → structure → cleanup → security → documentation → milestone
2. **No intermediate states**: Each commit represents a complete, logical state
3. **No deleted file references**: Only references to files that exist in that commit
4. **Professional presentation**: Clean history suitable for open source project
5. **Easy to understand**: New contributors can understand project evolution
6. **Atomic commits**: Each commit represents a complete unit of work
7. **Searchable history**: Clear commit messages make it easy to find specific changes

## Implementation Method

The cleanup will be performed using:

1. **Git orphan branch**: Create a new branch with no history
2. **Manual commit construction**: Build each of the 6 commits with appropriate files
3. **Branch replacement**: Replace the main branch with the clean history
4. **Force push**: Update remote repository (requires coordination)

## Execution

### Automated Script
Run the provided script to automatically perform the cleanup:

```bash
./cleanup_commit_history.sh --dry-run  # Preview changes
./cleanup_commit_history.sh            # Execute cleanup
```

### Manual Steps

If you prefer manual control:

```bash
# 1. Backup current state
git branch backup-original-history

# 2. Create orphan branch
git checkout --orphan clean-history
git rm -rf --cached .

# 3. Build commits (see commit structure above)
# Add files for each commit and create with appropriate message

# 4. Replace main branch
git branch -D main
git branch -m clean-history main

# 5. Force push (coordinate with team!)
git push --force origin main
```

## Risks and Mitigation

### Risks
- History rewrite affects all contributors
- Open PRs will need rebasing
- CI/CD may need reconfiguration
- Local clones become out of sync

### Mitigation
- Create backup branch before cleanup
- Notify all team members before force push  
- Document the change in CHANGELOG.md
- Provide clear instructions for team members to update their clones
- Schedule cleanup during low-activity period
- Test the cleanup on a fork first

## Post-Cleanup Actions

After the cleanup is complete:

1. **Update local clones**:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

2. **Rebase open PRs**:
   ```bash
   git rebase origin/main
   git push --force
   ```

3. **Update documentation**: Ensure all references to old commits are updated

4. **Verify CI/CD**: Check that all automated workflows still function

5. **Communicate**: Inform all stakeholders of the history rewrite

## Approval Required

This cleanup requires:
- [ ] Repository owner approval
- [ ] Backup created and verified
- [ ] Team notification sent
- [ ] CI/CD impact assessed
- [ ] Dry run executed and verified
- [ ] Execution scheduled

## References

- Original issue: [Link to issue describing the cleanup requirement]
- Backup branch: Will be created automatically by cleanup script
- Script location: `cleanup_commit_history.sh`
- This document: `COMMIT_CLEANUP_PLAN.md`

---

**SECURITY > EFFICIENCY > MINIMALISM**
