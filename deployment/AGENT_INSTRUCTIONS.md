# CI/CD & Deployment Agent Instructions

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Scope**: Deployment automation, CI/CD pipeline management, release procedures, rollback operations  
**Target Users**: Agents managing CodeSentinel deployments and release workflows  
**Last Updated**: November 7, 2025  
**Version**: 1.0  

---

## Quick Authority Reference

**Who can create, modify, delete in this domain?**

| Operation | Authority | Requires Approval |
|-----------|-----------|-------------------|
| Create deployment pipeline | Agent | Yes (DevOps) |
| Configure build stages | Agent | Yes (DevOps) |
| Manage secrets/credentials | Agent | Yes (security) |
| Deploy to staging | Agent | Yes (maintainer) |
| Deploy to production | Agent | Yes (release manager) |
| Execute rollback | Agent | Yes (incident) |
| Configure health checks | Agent | Yes (DevOps) |
| Set up monitoring | Agent | Yes (ops) |
| Handle deployment failures | Agent | No (operational) |
| Create release artifacts | Agent | No (automated) |

**Reference**: See `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Tier 4 Agent Documentation authority matrix

---

## Domain Overview

The CI/CD and deployment domain encompasses all automated build, test, and deployment workflows including:

- **Pipeline Automation** - Build stages, triggers, automated testing
- **Staging Deployment** - Pre-production environment testing
- **Production Deployment** - Safe, controlled production releases
- **Monitoring & Health** - System health checks, alerting
- **Incident Response** - Failure detection and rollback procedures
- **Release Management** - Artifact creation and distribution

This is the **critical path for code reaching production**. Reliability, safety, and auditability are paramount.

**Key Principles for This Domain**:

- SECURITY > EFFICIENCY > MINIMALISM (always)
- Non-destructive operations preferred
- All deployments logged and auditable
- Automated testing gates all deployments
- Health checks verify successful deployment
- Rollback procedures always ready
- Clear escalation paths for failures

---

## Common Procedures

### Procedure 1: Set Up a Deployment Pipeline

**When**: A new CI/CD pipeline is required for a new service, or an existing pipeline needs a significant architectural change.

**Steps**:

1. **Pipeline Planning & Design**:
    - **Define Stages**: Map out the required jobs (e.g., `build`, `test`, `security-scan`, `deploy-staging`, `deploy-production`). Use the `needs` context to establish a clear, sequential dependency graph.
    - **Define Triggers**: Specify the exact triggers. For the main pipeline, this is typically `on: push: branches: [ main ]`. For PR validation, use `on: pull_request: branches: [ main ]`. Also, add `workflow_dispatch` to allow for manual runs.
    - **Use Reusable Workflows**: For common sequences (like building and testing), create a reusable workflow (`workflow_call` trigger). This keeps the main pipeline clean and DRY.
    - **Plan for Failure**: Define a notification strategy. Use a dedicated job with `if: failure()` to send alerts to a Slack channel or trigger a PagerDuty incident.

2. **Secure Authentication & Secrets**:
    - **Use OIDC**: For authenticating with cloud providers (AWS, Azure, GCP), use OpenID Connect. This is a short-lived, token-based method that is far more secure than storing long-lived static credentials as secrets.
    - **GitHub Environments**: Store environment-specific secrets and variables (e.g., `STAGING_DB_URL`, `PROD_API_KEY`) in GitHub Environments. This scopes them to the correct deployment job.
    - **Secret Scanning**: Ensure the repository has secret scanning enabled to automatically detect any accidentally committed credentials.

3. **Implementation in YAML**:
    - Create the workflow file in `.github/workflows/`.
    - Use a matrix strategy (`strategy: matrix:`) for the `test` job to run tests against multiple Python versions and operating systems.
    - Use `actions/cache` to cache dependencies (like Pip packages) to speed up subsequent runs.
    - Define clear `name` attributes for each step for readable logs.

4. **Testing and Validation**:
    - Develop and test the workflow on a feature branch. Use the `pull_request` trigger to validate it.
    - Manually trigger the workflow using `workflow_dispatch` to test specific scenarios.
    - Verify that all jobs execute in the correct order and that artifacts are passed between them correctly using `actions/upload-artifact` and `actions/download-artifact`.
    - Test failure conditions to ensure that error handling and notification jobs work as expected.

5. **Documentation**:
    - Create a `README.md` in the `.github/workflows/` directory or update the main project documentation.
    - The documentation must explain the pipeline's purpose, its triggers, the jobs it runs, and all required secrets and their environments.
    - Include a simple diagram showing the flow of jobs.

---

### Procedure 2: Deploy to Staging Environment

**When**: Code ready for pre-production testing before production release

**Steps**:

1. **Pre-Deployment Checklist**:
   - All tests passing ✅
   - Code review completed ✅
   - No security issues identified ✅
   - Deployment documentation reviewed ✅
   - Team notified of upcoming deployment ✅

2. **Build Preparation**:
   - Verify artifact is built correctly
   - Check artifact integrity (checksums)
   - Verify all dependencies included
   - Test artifact locally if possible

3. **Staging Deployment**:
   - Trigger staging deployment
   - Monitor deployment logs
   - Verify no errors during deployment
   - Check service startup

4. **Smoke Tests**:
   - Run health checks
   - Verify critical endpoints responding
   - Test key workflows
   - Check error logs for issues
   - Validate database connectivity

5. **Validation**:
   - All smoke tests passed ✅
   - Error logs clean ✅
   - Performance baseline established ✅
   - No security issues ✅
   - Ready for production ✅

6. **Approval**:
   - Get sign-off from QA if needed
   - Team lead approves
   - Ready for production deployment

7. **Post-Staging**:
   - Document any issues found
   - Monitor for 24-48 hours
   - Collect performance metrics
   - Prepare production deployment

---

### Procedure 3: Execute a Production Deployment

**When**: The staging deployment has been verified, and the release has been approved by the Release Manager.

**Steps**:

1. **Pre-Deployment Final Check**:
   - **Confirm Staging Verification**: Ensure the staging deployment was successful and that all smoke tests passed. Reference the successful workflow run.
   - **Obtain Production Approval**: The production deployment job is gated by a GitHub Environment rule that requires approval from a designated Release Manager. Confirm this approval has been given.
   - **Schedule and Announce**: Announce the production deployment in the `#releases` Slack channel, specifying the version and expected timeline. Schedule it during a low-traffic window if possible.

2. **Trigger and Monitor the Production Workflow**:
   - The production deployment is typically a manual workflow (`workflow_dispatch`) or triggered by creating a GitHub release.
   - Monitor the deployment progress in the "Actions" tab. Pay close attention to the `deploy-production` job.
   - The deployment strategy should be either blue-green or canary.
     - **Blue-Green**: The new version (green) is deployed alongside the old version (blue). Traffic is switched only after the green environment is verified.
     - **Canary**: A small percentage of traffic (e.g., 5%) is routed to the new version. Monitor error rates and performance metrics before gradually increasing traffic.

3. **Post-Deployment Health Checks**:
   - The workflow will automatically run health checks against the production environment.
   - Manually verify the application's health endpoint and check for any errors in the logs.
   - Confirm that the monitoring dashboard (e.g., Grafana, Datadog) shows the new version running and that key metrics (CPU, memory, error rate) are within normal bounds.

4. **Handle Deployment Outcomes**:
   - **On Success**: Once the new version is stable and handling 100% of traffic, announce the successful completion in the `#releases` channel. The old version (blue environment or previous canary) can be decommissioned.
   - **On Failure (Rollback)**: If health checks fail or critical errors are detected, immediately trigger the `rollback` procedure. The workflow should have a dedicated, one-click rollback job that redeploys the previous stable version.

5. **Documentation and Reporting**:
   - The workflow automatically generates a deployment report, which is attached to the GitHub release.
   - Update the release notes with any observations from the deployment.
   - Ensure the deployment status is accurately reflected in any integrated systems like Jira.

---

### Procedure 4: Execute a Rollback

**When**: A production deployment has failed, or a critical, user-impacting bug is discovered post-release.

**Steps**:

1. **Initiate the Rollback**:
   - **Decision**: The decision to roll back is made by the on-call engineer or Incident Commander. This is an emergency procedure; do not delay seeking approval.
   - **Trigger**: Use the one-click `rollback` job in the production deployment workflow. This job is pre-configured to redeploy the last known stable version of the application.
   - **Communication**: Announce the rollback in the `#incidents` Slack channel immediately. State the reason and link to the failed deployment workflow.

2. **Monitor the Rollback Deployment**:
   - Watch the rollback deployment job to ensure it completes successfully. It follows the same deployment process but uses the previous version's artifact.
   - Verify that the application's health endpoint returns to a healthy state.
   - Check the logs to confirm the previous version has started up correctly.

3. **Verify System Stability**:
   - Once the rollback is complete, perform the same health checks and manual verification steps as a normal deployment.
   - Confirm that monitoring dashboards show the system has returned to its pre-deployment state and that error rates have subsided.
   - Announce in the `#incidents` channel that the system is stable and the rollback was successful.

4. **Post-Mortem and Investigation**:
   - **Isolate the Faulty Version**: Mark the failed release artifact as "bad" in the artifact repository to prevent accidental redeployment.
   - **Create a Post-Mortem Report**: A formal post-mortem is required. Create a new GitHub issue using the "Post-Mortem" template.
   - **Investigate Root Cause**: The issue must be investigated to understand why the failure occurred and was not caught in staging. The faulty code must be reverted from the `main` branch. Do not attempt a new deployment until the root cause is fixed and a new version is created.

5. **Prevent Recurrence**:
   - Identify and implement corrective actions. This could include adding new tests, improving health checks, or refining the deployment process.
   - Update documentation if necessary to reflect any changes in procedure.

---

## Quick Deployment Decision Tree

**I need to**...

- **Deploy to staging?** → Use "Deploy to Staging" procedure
- **Deploy to production?** → Use "Production Deployment" procedure
- **Fix a broken deployment?** → Use "Handle Deployment Failures" procedure
- **Set up new pipeline?** → Use "Setup Pipeline" procedure
- **Configure something?** → Check relevant documentation
- **Something else?** → Reference Common Questions section

---

## Validation Checklist (Before Deployment)

**Pre-Deployment**:

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] CHANGELOG entry added

**Staging**:

- [ ] Staging deployment successful
- [ ] Smoke tests passing
- [ ] Error logs clean
- [ ] Performance acceptable
- [ ] Team approval obtained

**Production**:

- [ ] Staging confirmed healthy
- [ ] All checks passed
- [ ] Rollback plan ready
- [ ] Team notified
- [ ] Incident response ready

**Monitoring**:

- [ ] Health checks configured
- [ ] Metrics being collected
- [ ] Alerts configured
- [ ] Escalation paths clear
- [ ] Team on standby (critical deployments)

**Post-Deployment**:

- [ ] Service responding normally
- [ ] Error rates normal
- [ ] Performance baseline met
- [ ] No critical issues
- [ ] Successfully communicated

---

## Common Questions

### Q: How do I set up environment-specific secrets?

**A**:

1. For staging environment:
   - Create GitHub secret: `STAGING_API_KEY`
   - Create GitHub secret: `STAGING_DB_URL`
   - Reference in workflow: `${{ secrets.STAGING_API_KEY }}`

2. For production environment:
   - Create GitHub secret: `PROD_API_KEY`
   - Create GitHub secret: `PROD_DB_URL`
   - Use in production stage only

3. Best practices:
   - Never commit secrets
   - Rotate regularly
   - Audit access
   - Use separate secrets per environment
   - Document in non-sensitive format

### Q: How do I implement blue-green deployments?

**A**:

1. **Infrastructure Setup**:
   - Maintain two identical environments (Blue, Green)
   - Load balancer directs traffic to active environment
   - Both receive updates, only one serves traffic

2. **Deployment Process**:
   - Deploy new version to inactive environment (Green)
   - Run full test suite on Green
   - Perform smoke tests
   - If all pass, switch traffic from Blue to Green
   - Keep Blue ready for instant rollback

3. **Workflow**:
   - Check which is active (Blue or Green)
   - Deploy to inactive
   - Run tests
   - Switch traffic via load balancer
   - Monitor for issues

4. **Rollback**:
   - Detect issue or operator detects issue
   - Switch traffic back to previous environment
   - Investigation while previous version serves users

### Q: How do I handle database migrations during deployment?

**A**:

1. **Forward Migrations**:
   - Make database schema backward compatible
   - Deploy new code that supports new schema
   - Run migration
   - Remove old code path in next release

2. **Workflow**:
   - Stage 1: Deploy code supporting both old and new schema
   - Stage 2: Run migration
   - Stage 3: Deploy code using new schema only

3. **Safety**:
   - Always backup database before migration
   - Test migration on copy of production data
   - Have rollback plan (backup restore)
   - Monitor for migration issues

4. **Automated Approach**:
   - Use migrations tool (Alembic, Liquibase, etc.)
   - Version control migrations
   - Run migrations in deployment pipeline
   - Automate rollback if needed

### Q: How do I implement canary deployments?

**A**:

1. **Setup**:
   - Deploy to small subset of infrastructure (e.g., 1-5% traffic)
   - Monitor metrics (error rate, latency, etc.)
   - Gradually increase percentage

2. **Process**:
   - Deploy to canary (5%)
   - Monitor for 10-30 minutes
   - If healthy, increase to 10%
   - Monitor again
   - Continue doubling until 100%

3. **Automation**:
   - Use service mesh (Istio) for traffic splitting
   - Use deployment controller for gradual rollout
   - Automated metrics collection and decision

4. **Rollback**:
   - If error rate spikes, immediately rollback canary
   - Revert to previous version
   - Investigate issue
   - Plan fix

### Q: How do I collect metrics during deployment?

**A**:

1. **Before Deployment**:
   - Record baseline metrics (error rate, latency, etc.)
   - Take snapshot of performance

2. **During Deployment**:
   - Continuously monitor error rate
   - Track response times
   - Monitor resource usage (CPU, memory)
   - Check for timeout spikes

3. **Comparison**:
   - Compare post-deployment to baseline
   - Flag if any metric worse than threshold
   - Alert if anomalies detected

4. **Tools**:
   - Prometheus for metrics collection
   - Grafana for dashboards
   - DataDog, New Relic for APM
   - CloudWatch for AWS

### Q: How do I handle secrets rotation?

**A**:

1. **Process**:
   - Generate new secret
   - Update GitHub Secrets with new value
   - Redeploy (workflow uses new secret)
   - Monitor for issues
   - Document old secret as rotated

2. **Timing**:
   - Rotate regularly (e.g., quarterly)
   - Immediately if compromised
   - Before staff changes

3. **Audit**:
   - Log all secret accesses
   - Monitor for unusual access patterns
   - Review access regularly

### Q: How do I rollback quickly if needed?

**A**:

1. **Manual Rollback**:
   - Identify previous good version
   - Deploy previous version artifact
   - Verify service recovery
   - Investigate issue

2. **Automated Rollback**:
   - Keep previous version deployment config ready
   - Have one-click rollback button
   - Automated health checks determine if needed

3. **Emergency Procedure**:
   - For critical issues
   - Skip testing, deploy immediately
   - Have manual backup (restore from backup)

### Q: How do I handle deployment conflicts?

**A**:

1. **Conflict Scenarios**:
   - Multiple teams deploying
   - Infrastructure changes during deployment
   - Resource contention

2. **Prevention**:
   - Use queued deployments (one at a time)
   - Lock infrastructure during deployment
   - Schedule deployments

3. **Resolution**:
   - If conflict detected, fail deployment
   - Wait for previous deployment complete
   - Retry deployment
   - Manual coordination if needed

### Q: How do I monitor post-deployment?

**A**:

1. **Immediate** (0-5 minutes):
   - Verify service is up
   - Check error rates
   - Verify responses are correct

2. **Short-term** (5 minutes - 1 hour):
   - Monitor error trends
   - Check performance metrics
   - Monitor customer reports
   - Check logs for warnings

3. **Medium-term** (1-24 hours):
   - Verify stability continues
   - Collect performance baselines
   - Monitor all system metrics
   - Document any anomalies

---

## References & Links

**Global Policies**:

- `docs/architecture/POLICY.md` - Core policies and principles
- `docs/architecture/DOCUMENT_CLASSIFICATION.md` - Classification system
- `docs/architecture/AGENT_INSTRUCTION_STRATEGY.md` - Instruction framework

**Deployment Tools**:

- GitHub Actions: <https://github.com/features/actions>
- Docker: <https://www.docker.com>
- Kubernetes: <https://kubernetes.io>

**Related Satellites**:

- `github/AGENT_INSTRUCTIONS.md` - GitHub operations
- `infrastructure/AGENT_INSTRUCTIONS.md` - Infrastructure as Code procedures
- `tools/AGENT_INSTRUCTIONS.md` - Automation procedures
- `docs/AGENT_INSTRUCTIONS.md` - Documentation procedures

**CodeSentinel References**:

- Repository: <https://github.com/joediggidyyy/CodeSentinel>
- CHANGELOG: `CHANGELOG.md` in root
- Release notes: GitHub releases page

---

**Classification**: T4b - Infrastructure & Procedural Agent Documentation  
**Authority**: Guidelines for agents managing deployments  
**Update Frequency**: When deployment procedures or policies change  
**Last Updated**: November 7, 2025  
**Next Review**: December 7, 2025 (quarterly satellite audit)  

---

# CI/CD & Deployment Satellite Complete ✅
