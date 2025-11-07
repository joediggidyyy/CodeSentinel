# GitHub Operations Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: GitHub repository operations, PR management, issue automation, GitHub Actions workflows  
**Target Users**: Agents working on CodeSentinel GitHub repository management  
**Last Updated**: November 7, 2025  
**Version**: 1.0  

---

## Quick Authority Reference

**Who can create, modify, delete in this domain?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create pull request | Agent | No (minor), Yes (major) |
| Review and merge PR | Agent | Yes (code owner) |
| Manage GitHub Actions | Agent | Yes (admin) |
| Create release | Agent | Yes (release manager) |
| Manage repository settings | Agent | Yes (admin) |
| Handle branch protection | Agent | Yes (admin) |
| Manage labels/milestones | Agent | Yes (maintainer) |
| GitHub issue automation | Agent | No (minor), Yes (major) |
| Integrate external systems | Agent | Yes (security) |
| Handle API errors | Agent | No (operational) |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Tier 4 Agent Documentation authority matrix

---

## Domain Overview

The GitHub operations domain encompasses all interactions with the CodeSentinel GitHub repository including:

- **Pull Requests** - Creating, reviewing, merging code changes
- **Issues** - Managing bug reports, features, enhancement requests
- **GitHub Actions** - CI/CD workflows, automated testing, deployment
- **Releases** - Version management, release notes, artifact publishing
- **Repository Settings** - Branch protection, access control, automation
- **Integration** - External system connections, API interactions

This is the **enterprise integration point** for CodeSentinel. Changes here affect the entire team workflow and public repository.

**Key Principles for This Domain**:

- SECURITY > EFFICIENCY > MINIMALISM (always)
- Non-destructive changes (no force pushes, no history rewrites)
- Code review requirements maintained
- Automated testing must pass before merge
- Clear commit messages and PR descriptions
- Enterprise readiness and scalability

---

## Common Procedures

### Procedure 1: Create Well-Structured Pull Request

**When**: New feature, bug fix, or enhancement ready for integration

**Steps**:

1. **Verify Authority**: Confirm you have merge permissions ✅
   - Check repository settings for access level
   - Verify branch protection rules
   - Understand approval requirements

2. **Branch Strategy**:
   - Create feature branch from latest `main`
   - Use naming convention: `feature/[name]`, `bugfix/[name]`, `docs/[name]`
   - Keep branch focused on single concern
   - Rebase on main if outdated

3. **Code Quality**:
   - Run local tests and validation
   - Follow project code style (linting, formatting)
   - Include unit tests for new functionality
   - Update documentation if needed
   - Verify no hardcoded secrets or credentials

4. **Commit Best Practices**:
   - Clear, descriptive commit messages
   - One feature per commit when possible
   - Use conventional commit format: `type(scope): description`
   - Group related changes logically

5. **Push and Create PR**:
   - Push feature branch to origin
   - Create PR with comprehensive description
   - Link to related issues (#123, closes #456)
   - Add appropriate labels and milestone
   - Request review from code owners

6. **Validation**:
   - All CI/CD checks pass ✅
   - Code review completed ✅
   - Documentation updated ✅
   - No merge conflicts ✅
   - Tests passing ✅

7. **Merge**:
   - Squash commits if needed (per project preference)
   - Delete feature branch after merge
   - Verify CI/CD post-merge
   - Monitor for any related failures

---

### Procedure 2: Review and Merge Pull Request

**When**: PR received requiring code review and merge decision

**Steps**:

1. **Pre-Review Checklist**:
   - Verify PR has clear description
   - Check if CI/CD checks are passing
   - Review linked issues
   - Note any special requirements or risks

2. **Code Review**:
   - Read all changes carefully
   - Check for security issues (credentials, vulnerabilities)
   - Verify code follows project standards
   - Ensure tests are adequate
   - Look for edge cases and error handling
   - Comment on concerns and questions

3. **Request Changes** (if needed):
   - Provide specific, actionable feedback
   - Link to relevant documentation or policies
   - Allow author to respond and revise
   - Re-review when updated

4. **Approve**:
   - Confirm all issues resolved
   - Verify final state is acceptable
   - Approve through GitHub interface
   - Add any final notes

5. **Merge Decision**:
   - Confirm all required reviews completed
   - Verify branch is up to date with main
   - Choose merge strategy (merge commit, squash, rebase)
   - Add merge commit message if applicable

6. **Perform Merge**:
   - Click "Merge pull request"
   - Confirm merge completion
   - Monitor for post-merge issues
   - Delete feature branch (GitHub option)

7. **Post-Merge Validation**:
   - Verify CI/CD post-merge pipeline ✅
   - Check production deployment (if automated)
   - Monitor for related errors or issues ✅
   - Notify stakeholders if needed ✅

---

### Procedure 3: Manage GitHub Actions Workflow

**When**: CI/CD pipeline needs creation, modification, or debugging

**Steps**:

1. **Workflow Planning**:
   - Define workflow triggers (push, PR, schedule, manual)
   - Plan workflow stages (build, test, deploy)
   - Identify required secrets/credentials
   - Design failure recovery

2. **Secrets Management**:
   - Use GitHub Secrets for sensitive data
   - Never commit credentials or tokens
   - Rotate secrets regularly
   - Document which secrets are needed
   - Verify access restrictions

3. **Workflow Creation**:
   - Create `.github/workflows/[name].yml`
   - Define jobs and steps clearly
   - Use standard actions when possible
   - Handle errors gracefully
   - Add logging for debugging

4. **Environment Configuration**:
   - Set up matrix builds if needed
   - Configure environment variables
   - Define concurrency settings
   - Set resource limits appropriately

5. **Testing Workflow**:
   - Trigger manually to test
   - Verify all steps execute correctly
   - Check logs for errors
   - Validate artifacts created
   - Test failure scenarios

6. **Debugging Issues**:
   - Check workflow logs for errors
   - Verify secrets are properly configured
   - Test commands locally first
   - Check action versions are compatible
   - Review recent changes to workflow

7. **Documentation**:
   - Document workflow purpose
   - List required secrets
   - Document environment variables
   - Note any limitations or quirks
   - Link to related documentation

---

### Procedure 4: Handle Release and Versioning

**When**: Ready to release new version to production/PyPI

**Steps**:

1. **Pre-Release Verification**:
   - All tests passing ✅
   - Documentation updated ✅
   - CHANGELOG entries complete ✅
   - Version numbers updated ✅
   - No outstanding issues for this release ✅

2. **Version Management**:
   - Update version in `pyproject.toml` or `setup.py`
   - Follow semantic versioning (major.minor.patch)
   - Document what changed in CHANGELOG.md
   - Update README if needed

3. **Create Release**:
   - Tag commit with version: `v1.0.3`
   - Create GitHub Release with notes
   - Include changelog in release notes
   - Upload artifacts if applicable

4. **Build Artifacts**:
   - Build distribution packages (wheels, source)
   - Verify package contents
   - Test installation locally
   - Sign packages if required

5. **Publish**:
   - Push to PyPI or artifact repository
   - Verify package is accessible
   - Test installation from published source
   - Announce release to stakeholders

6. **Post-Release**:
   - Monitor for installation issues
   - Update documentation sites
   - Create post-release branch if needed
   - Plan next release cycle

7. **Rollback Plan** (if issues):
   - Document the issue clearly
   - Identify fix required
   - Create hotfix branch from release tag
   - Go through full release process again
   - Notify users of corrected version

---

## Quick GitHub Decision Tree

**I need to**...

- **Create a PR?** → Use "Create Well-Structured PR" procedure
- **Review a PR?** → Use "Review and Merge PR" procedure
- **Fix CI/CD?** → Use "Manage GitHub Actions" procedure
- **Release version?** → Use "Handle Release and Versioning" procedure
- **Manage settings?** → Check branch protection in repository settings
- **Something else?** → Reference Common Questions section

---

## Validation Checklist (Before Committing)

**Code Quality**:

- [ ] All tests passing locally
- [ ] No linting errors
- [ ] Code follows project style
- [ ] No hardcoded secrets
- [ ] Error handling complete

**Security**:

- [ ] No credentials in code
- [ ] No vulnerable dependencies
- [ ] Access control verified
- [ ] Secrets properly configured
- [ ] No breaking security changes

**Documentation**:

- [ ] Code commented where needed
- [ ] PR description clear and complete
- [ ] Issue links included
- [ ] Related docs updated
- [ ] CHANGELOG entry added

**Compliance**:

- [ ] Follows SECURITY > EFFICIENCY > MINIMALISM
- [ ] Non-destructive approach used
- [ ] No force pushes or history rewrites
- [ ] Branch protection rules respected
- [ ] Policy compliance verified

**Process**:

- [ ] Code owner review completed
- [ ] All CI/CD checks passing
- [ ] No merge conflicts
- [ ] Branch up to date with main
- [ ] Ready for production

---

## Common Questions

### Q: How do I handle merge conflicts?

**A**:

1. Pull latest main: `git pull origin main`
2. Fix conflicts in your editor
3. Stage resolved files: `git add [files]`
4. Complete merge: `git commit -m "Merge main into feature branch"`
5. Push to origin: `git push origin [branch]`
6. GitHub will show conflicts resolved
7. Proceed with code review and merge

### Q: How do I configure branch protection rules?

**A**:

1. Go to repository settings → Branches
2. Click "Add rule" under Branch protection rules
3. Enter branch name pattern (e.g., `main`)
4. Configure requirements:
   - ✓ Require pull request reviews
   - ✓ Dismiss stale reviews
   - ✓ Require status checks to pass
   - ✓ Require branches to be up to date
5. Save rules
6. Test by attempting to push directly to protected branch (should fail)

### Q: How do I manage GitHub secrets for CI/CD?

**A**:

1. Go to repository settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter name (e.g., `PYPI_TOKEN`) and value
4. Click "Add secret"
5. In workflow file, reference: `${{ secrets.PYPI_TOKEN }}`
6. Secret is masked in logs automatically
7. Rotate regularly by creating new secret with same name

### Q: How do I automate version updates?

**A**:

Option 1 (Manual):

- Update version file manually
- Commit with message: `chore: bump version to 1.0.4`
- Tag commit: `git tag v1.0.4`

Option 2 (Automated):

- Use tools like `bump-my-version` or similar
- Configure version file locations
- Run in CI/CD: `bump-my-version bump patch`
- Automatically commit and tag

Option 3 (Workflow):

- GitHub Action: `actions/create-release` with auto-version
- Use conventional commits to determine version
- Automatically generate changelog

### Q: How do I implement canary or blue-green deployments?

**A**:

Canary Deployment:

1. Deploy to small percentage of infrastructure (e.g., 5%)
2. Monitor error rates and metrics
3. If healthy, gradually increase to 10%, 25%, 50%, 100%
4. If issues detected, rollback to previous version
5. Automation: Use GitHub Actions with deployment gates

Blue-Green Deployment:

1. Maintain two identical production environments (Blue, Green)
2. Deploy to inactive environment (Green)
3. Run tests against Green
4. Switch traffic from Blue to Green
5. Keep Blue ready for rollback
6. Automation: Use load balancer switching in workflow

### Q: How do I roll back a bad deployment?

**A**:

1. Identify the issue and which version caused it
2. Note the previous good version tag (e.g., `v1.0.2`)
3. Revert production to previous version:
   - Manual: Deploy previous artifact/image
   - Automated: GitHub Action to deploy tag
4. Verify service is healthy
5. Create incident report documenting:
   - What failed
   - When detected
   - How recovered
   - Root cause analysis
   - Preventive measures
6. Create bugfix branch from current main
7. Fix issue and go through normal release process

### Q: How do I organize GitHub Actions workflows?

**A**:

Structure:

```
.github/
└── workflows/
    ├── ci.yml (tests on PR)
    ├── release.yml (version releases)
    ├── deploy.yml (deployments)
    ├── security.yml (security scans)
    └── scheduled.yml (nightly/weekly jobs)
```

Each workflow should:

- Have single clear purpose
- Be named descriptively
- Include comments explaining logic
- Handle errors gracefully
- Generate useful logs
- Have success/failure notifications

### Q: How do I manage access and permissions?

**A**:

1. Go to repository settings → Collaborators and teams
2. Invite users with appropriate role:
   - Read: Can view and clone
   - Triage: Can manage issues/PRs
   - Write: Can push changes
   - Maintain: Can manage settings
   - Admin: Full access
3. For teams: Go to organization and manage team membership
4. Use branch protection to enforce review requirements
5. Use CODEOWNERS file for automatic reviewer assignment

### Q: How do I handle pre-commit checks?

**A**:

1. Install pre-commit framework: `pip install pre-commit`
2. Create `.pre-commit-config.yaml` in repo root
3. Define hooks (linting, formatting, security checks)
4. Install hooks: `pre-commit install`
5. Hooks run automatically before commit
6. If hooks fail, fix issues and retry commit
7. Can bypass with `git commit --no-verify` (not recommended)

---

## Running GitHub Operations

**Common Commands**:

```bash
# Create feature branch
git checkout -b feature/my-feature

# Commit changes
git commit -m "feat(domain): description of change"

# Push to origin
git push origin feature/my-feature

# Create PR (opens browser)
gh pr create --title "PR Title" --body "Description"

# View PR status
gh pr view

# Merge PR (from command line)
gh pr merge --squash --delete-branch

# Create tag
git tag v1.0.3

# Create release
gh release create v1.0.3 -t "Version 1.0.3" -n "Release notes"
```

---

## References & Links

**Global Policies**:

- `docs/architecture/POLICY.md` - Core policies and principles
- `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Classification system
- `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md` - Instruction framework

**GitHub Documentation**:

- GitHub Docs: <https://docs.github.com>
- GitHub Actions: <https://github.com/features/actions>
- GitHub API: <https://docs.github.com/rest>

**CodeSentinel References**:

- Repository: <https://github.com/joediggidyyy/CodeSentinel>
- Issues: GitHub repository issues page
- Releases: GitHub repository releases page
- CHANGELOG: `CHANGELOG.md` in root

**Related Satellites**:

- `deployment/AGENT_INSTRUCTIONS.md` - CI/CD procedures (linked)
- `infrastructure/AGENT_INSTRUCTIONS.md` - Infrastructure as Code procedures
- `docs/AGENT_INSTRUCTIONS.md` - Documentation procedures
- `tools/AGENT_INSTRUCTIONS.md` - Automation procedures

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents managing GitHub operations  
**Update Frequency**: When GitHub workflows or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)  

---

# GitHub Operations Satellite Complete ✅
