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

### Procedure 1: Set Up Deployment Pipeline

**When**: Creating new CI/CD pipeline or significant pipeline restructuring

**Steps**:

1. **Pipeline Planning**:
   - Define stages (build, test, staging, production)
   - Identify triggers (push, PR, schedule, manual)
   - Plan failure handling and notifications
   - Document approval requirements

2. **Stage Configuration**:
   - Build stage: Compile, package, artifact creation
   - Test stage: Unit tests, integration tests, linting
   - Security stage: Dependency scanning, secret scanning
   - Staging stage: Deploy to staging, smoke tests
   - Production stage: Deploy with health checks

3. **Environment Setup**:
   - Define environment variables
   - Configure secrets management
   - Set resource limits and timeouts
   - Configure concurrency settings

4. **Trigger Configuration**:
   - Set branch filters (e.g., only main branch)
   - Configure webhook settings
   - Set schedule if applicable
   - Allow manual trigger for emergencies

5. **Failure Handling**:
   - Define failure scenarios
   - Set up retry logic where appropriate
   - Configure notifications (Slack, email)
   - Plan manual intervention steps

6. **Testing**:
   - Trigger pipeline manually
   - Verify each stage executes correctly
   - Check logs for errors
   - Validate artifacts created
   - Test failure scenarios

7. **Documentation**:
   - Document pipeline flow
   - List required secrets
   - Note environment variables
   - Document manual intervention points
   - Reference troubleshooting guide

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

### Procedure 3: Production Deployment

**When**: Ready to release code to end users

**Steps**:

1. **Pre-Production Verification**:
   - Staging deployment successful ✅
   - All tests passing ✅
   - Security audit complete ✅
   - Rollback plan documented ✅
   - Team lead approval obtained ✅

2. **Communication**:
   - Notify all stakeholders
   - Document deployment window
   - Provide rollback contact info
   - Note maintenance implications

3. **Gradual Rollout** (if supported):
   - Deploy to 5% of infrastructure first
   - Monitor metrics (errors, latency)
   - If healthy, increase to 10%, then 25%, 50%, 100%
   - If issues detected, immediately rollback

4. **Deployment**:
   - Trigger production deployment
   - Monitor deployment progress
   - Check logs for errors
   - Verify all instances updated
   - Confirm service availability

5. **Health Verification**:
   - Run health checks
   - Verify critical endpoints
   - Test user workflows
   - Monitor error rates
   - Check performance metrics

6. **Monitoring**:
   - Watch metrics for 1-4 hours
   - Check error logs continuously
   - Monitor customer reports
   - Keep team on alert
   - Have rollback ready

7. **Completion**:
   - All checks passing
   - Metrics normal
   - No critical issues
   - Document successful deployment
   - Notify stakeholders

---

### Procedure 4: Handle Deployment Failures

**When**: Deployment fails or issues detected post-deployment

**Steps**:

1. **Identify Issue**:
   - Determine what failed
   - Check error logs
   - Understand scope (all users or partial)
   - Assess severity (critical, high, medium, low)

2. **Initial Response**:
   - Page on-call team if critical
   - Declare incident if needed
   - Create incident ticket
   - Start incident communication channel

3. **Diagnosis**:
   - Collect relevant logs
   - Check recent changes
   - Review deployment process
   - Identify root cause
   - Understand impact

4. **Rollback Decision**:
   - Critical issue? → Immediate rollback
   - High issue? → Rollback or hotfix decision
   - Medium/Low? → Fix forward decision
   - Prioritize user impact

5. **Execute Rollback** (if needed):
   - Trigger rollback workflow
   - Verify previous version deploying
   - Confirm service recovering
   - Run health checks
   - Document rollback time

6. **Verify Recovery**:
   - All services healthy
   - Users able to access
   - Error rates normalized
   - Performance baseline restored
   - No lingering issues

7. **Post-Incident**:
   - Collect logs and metrics
   - Document timeline
   - Identify root cause
   - Plan preventive measures
   - Share learning with team
   - Close incident ticket

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
