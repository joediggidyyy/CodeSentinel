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

1. **Verify Authority & Branch Strategy**:
    - Ensure you have permissions to create branches and PRs.
    - Create a new branch from the latest `main`: `git checkout -b feature/my-new-feature`.
    - Use a descriptive naming convention: `feature/[name]`, `bugfix/[issue-id]`, `docs/[topic]`.
    - Keep the branch focused on a single, atomic concern to simplify review.

2. **Code Quality & Pre-Commit Hooks**:
    - Run all local tests and validation: `pytest`.
    - Ensure code follows project style by running linters and formatters.
    - **Best Practice**: Use pre-commit hooks (`.pre-commit-config.yaml`) to automate these checks before every commit.
    - Include comprehensive unit tests for all new functionality, aiming for 100% coverage.
    - Update any related documentation (`docs/`) or docstrings.
    - Verify **no hardcoded secrets or credentials** have been added.

3. **Commit Best Practices**:
    - Write clear, descriptive commit messages using the conventional commit format: `type(scope): description`.
    - *Example*: `feat(cli): add new '--verbose' flag to audit command`.
    - This format is critical for automated changelog generation and version bumping.
    - Group related file changes into logical, atomic commits.

4. **Push and Create PR**:
    - Keep your branch up-to-date with `main` by rebasing periodically: `git pull --rebase origin main`.
    - Push the feature branch to the remote repository: `git push origin feature/my-new-feature`.
    - Create the Pull Request using the GitHub UI or `gh pr create`.
    - Write a **comprehensive description**:
        - **What**: A summary of the changes.
        - **Why**: The business reason or problem being solved.
        - **How**: A brief technical overview of the implementation.
        - Link to related issues (e.g., `Closes #123`).
    - Add appropriate labels (`bug`, `enhancement`) and request review from code owners.

5. **Automated Validation & Review**:
    - Ensure all CI/CD status checks (GitHub Actions) pass successfully. A green checkmark (✅) is required.
    - Actively monitor the PR for feedback from reviewers. Respond to comments and push updates as needed.
    - If changes are requested, push new commits to the same branch. The PR will update automatically.

6. **Final Merge**:
    - Once all reviews are approved and checks are passing, the PR is ready to merge.
    - Use the "Squash and merge" option to create a single, clean commit on the `main` branch. This keeps the git history tidy.
    - Ensure the feature branch is deleted after the merge to keep the repository clean.
    - Verify that the post-merge CI/CD pipeline (e.g., deployment to staging) runs successfully.

---

### Procedure 2: Review and Merge Pull Request

**When**: A Pull Request is ready for code review and merge decision.

**Steps**:

1.  **Initial Triage & Pre-Review Checklist**:
    -   Read the PR description to understand its purpose (**What**, **Why**, **How**).
    -   Verify that it's linked to a relevant issue and has appropriate labels.
    -   Check the CI/CD status checks. If they are failing, do not proceed with a review. The author must fix them first. Note any special requirements or risks.

2.  **Systematic Code Review**:
    -   Fetch the branch and run it locally if the change is complex: `git fetch origin pull/[PR-ID]/head:pr-[PR-ID] && git checkout pr-[PR-ID]`.
    -   **Security First**: Scrutinize for security vulnerabilities. Look for hardcoded secrets, injection risks (SQL, command), and insecure dependencies.
    -   **Correctness**: Does the code do what it says it does? Does it handle edge cases and invalid inputs gracefully?
    -   **Maintainability**: Is the code clean, readable, and well-documented? Does it follow existing project patterns and the SOLID principles?
    -   **Test Coverage**: Are the tests adequate? They should cover the success path, error conditions, and edge cases. A high-quality PR includes high-quality tests.

3.  **Provide Actionable Feedback**:
    -   Use GitHub's review feature to comment directly on lines of code.
    -   Be specific and constructive. Instead of "this is wrong," say "this approach might lead to a race condition under these circumstances. Could we use a lock here instead?"
    -   Use the "Request changes" option if the PR is not ready to be merged. This blocks merging until the author addresses the feedback.
    -   Approve the PR if it meets all quality and security standards.

4.  **Merge Decision & Execution**:
    -   Confirm all required reviews are complete and all status checks have passed.
    -   Ensure the branch is up-to-date with `main`. If not, ask the author to rebase.
    -   **Use "Squash and merge"**. This is the repository's standard. It condenses the feature branch's history into a single, clean commit on `main`.
    -   The commit message should follow the conventional commit standard, summarizing the entire PR.
    -   Ensure the "Delete branch" option is checked to maintain repository hygiene.

5.  **Post-Merge Validation**:
    -   After merging, monitor the post-merge CI/CD pipeline (e.g., deployment to staging).
    -   Verify that the change has been successfully integrated and has not caused any regressions.
    -   If issues arise, be prepared to revert the PR or coordinate a hotfix.

---

### Procedure 3: Manage GitHub Actions Workflow

**When**: A CI/CD pipeline requires creation, modification, or debugging.

**Steps**:

1.  **Workflow Planning & Design**:
    -   **Define Triggers**: Clearly specify what events will trigger the workflow (e.g., `on: [push, pull_request, workflow_dispatch]`).
    -   **Plan Jobs & Stages**: Break the workflow into logical jobs (e.g., `build`, `test`, `deploy`). Use the `needs` keyword to create dependencies between jobs, forming a pipeline.
    -   **Identify Secrets**: List all required secrets (e.g., `PYPI_TOKEN`, `AWS_ACCESS_KEY_ID`). These must be stored in GitHub's encrypted secrets storage, never in the repository.
    -   **Design for Failure**: Plan for how the workflow should behave on failure. Use `if: failure()` or `if: always()` to define cleanup or notification steps.

2.  **Secure Secrets Management**:
    -   Navigate to repository **Settings > Secrets and variables > Actions**.
    -   Store all sensitive data as encrypted secrets. Use environment-specific secrets (e.g., `STAGING_DB_PASSWORD`) for enhanced security.
    -   **Never commit credentials, tokens, or API keys directly into the code.**
    -   Implement a secret rotation policy and audit access regularly.

3.  **Workflow Implementation**:
    -   Create the workflow file in `.github/workflows/my-workflow.yml`.
    -   Use reusable actions (e.g., `actions/checkout@v3`, `actions/setup-python@v4`) to keep the workflow clean and maintainable.
    -   Add descriptive names to each step (`name: Run unit tests`) for clear logging.
    -   Implement robust error handling for each critical step.

4.  **Environment and Concurrency**:
    -   Use a matrix strategy (`strategy: matrix:`) to test across multiple versions or operating systems (e.g., `python-version: [3.9, 3.10, 3.11]`).
    -   Define environment variables using the `env` context.
    -   Control concurrent runs using `concurrency: group: ${{ github.workflow }}-${{ github.ref }}` to prevent race conditions on feature branches.

5.  **Testing and Debugging**:
    -   Test the workflow on a feature branch before merging to `main`.
    -   To debug a failed run, examine the workflow logs for specific error messages.
    -   For highly complex issues, consider using an action like `mxschmitt/action-tmate@v3` to get temporary SSH access to the runner for live debugging.
    -   Verify that all expected artifacts are created and stored correctly using `actions/upload-artifact`.

6.  **Documentation**:
    -   Add a section to the relevant documentation (e.g., a `README.md` in `.github/workflows/`) explaining the workflow's purpose, triggers, and required secrets.
    -   Comment complex or non-obvious steps directly within the YAML file.

---

### Procedure 4: Handle Release and Versioning

**When**: The `main` branch is stable and ready for a new production release.

**Steps**:

1.  **Pre-Release Verification**:
    -   Ensure all tests are passing on the `main` branch.
    -   Confirm that all documentation has been updated and the `CHANGELOG.md` file accurately reflects all changes since the last release.
    -   Verify that the version number in the project's configuration (e.g., `pyproject.toml`) has been correctly incremented following **Semantic Versioning (major.minor.patch)**.

2.  **Create a Release Branch**:
    -   Create a release branch from `main`: `git checkout -b release/v1.2.0`.
    -   This branch is used for final preparations and is a stable point from which to tag. No new features should be added here; only critical bug fixes are allowed.

3.  **Tag the Release**:
    -   Create an annotated Git tag for the new version: `git tag -a v1.2.0 -m "Release version 1.2.0"`.
    -   Push the tag to the remote repository: `git push origin v1.2.0`. This is a critical step that makes the tag available to CI/CD systems.

4.  **Build and Test Release Artifacts**:
    -   The CI/CD pipeline, triggered by the new tag, should automatically build the release artifacts (e.g., Python wheels, source distributions).
    -   The pipeline must verify the integrity of these artifacts, for example, by testing that the package can be installed and its basic functions run correctly.

5.  **Publish the Release**:
    -   **Automated**: The CI/CD pipeline should publish the artifacts to the package repository (e.g., PyPI).
    -   **Manual (if required)**: If manual publication is necessary, use a secure tool like `twine` and an API token stored in GitHub Secrets.
    -   Create a corresponding **GitHub Release**. The release notes should be generated from the `CHANGELOG.md` and should link to the milestone and all included PRs.

6.  **Post-Release Monitoring & Hotfixes**:
    -   Closely monitor production systems for any new errors or performance regressions.
    -   If a critical bug is discovered, create a hotfix branch from the release tag (`hotfix/v1.2.1`).
    -   Implement the fix, merge it back into `main`, and then cherry-pick the commit into the `main` branch to ensure the fix is included in future releases. A new patch release (e.g., `v1.2.1`) must be created.

7.  **Rollback Plan**:
    -   A rollback is a last resort. The primary strategy is to roll forward with a hotfix.
    -   If a rollback is unavoidable, the procedure involves reverting the deployment to the previously known good version (e.g., `v1.1.0`). This is typically handled by the deployment system (see `deployment/AGENT_INSTRUCTIONS.md`).

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
