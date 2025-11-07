# T4b - Infrastructure & Procedural Agent Documentation

**DOCUMENT_CLASSIFICATION**: T4b - Infrastructure & Procedural Agent Documentation
**SATELLITE_DOMAIN**: Infrastructure Operations
**EFFECTIVE_DATE**: 2025-11-25
**VERSION**: 1.0
**STATUS**: ACTIVE
**NEXT_REVIEW_DATE**: 2026-02-25
**OWNER**: System Architect

---

## 1. Introduction

This document provides operational instructions for the **Infrastructure Operations Satellite**. Its purpose is to govern all activities related to Infrastructure as Code (IaC), cloud resource management, and environment provisioning. All operations must adhere to the core principles of **SECURITY > EFFICIENCY > MINIMALISM**.

This satellite is the single source of truth for managing the application's underlying infrastructure. It ensures that all environments (development, staging, production) are provisioned, configured, and managed consistently and securely.

---

## 2. Authority Matrix

All infrastructure operations require strict adherence to this authority matrix. Any operation not listed here requires **L4 (Architect)** approval.

| Operation ID | Description | Authority Level | Approval Required | Automated | Non-Destructive |
| :--- | :--- | :--- | :--- | :--- | :--- |
| INFRA-OP-01 | **Plan Infrastructure Changes** | L2 (Agent) | L3 (Senior Dev) | Yes | Yes |
| INFRA-OP-02 | **Apply Staging Changes** | L2 (Agent) | L3 (Senior Dev) | Yes | No |
| INFRA-OP-03 | **Apply Production Changes** | L3 (Senior Dev) | L4 (Architect) | No | No |
| INFRA-OP-04 | **Create New IaC Module** | L2 (Agent) | L3 (Senior Dev) | Yes | Yes |
| INFRA-OP-05 | **Manage Terraform State** | L3 (Senior Dev) | L4 (Architect) | No | No |
| INFRA-OP-06 | **Provision New Environment** | L3 (Senior Dev) | L4 (Architect) | No | Yes |
| INFRA-OP-07 | **Decommission Resource** | L3 (Senior Dev) | L4 (Architect) | No | No |
| INFRA-OP-08 | **Update Provider Versions** | L2 (Agent) | L3 (Senior Dev) | Yes | Yes |
| INFRA-OP-09 | **Run Security Scans (e.g., tfsec)** | L1 (Junior Dev) | None | Yes | Yes |
| INFRA-OP-10 | **Handle State Drift** | L3 (Senior Dev) | L4 (Architect) | No | No |

---

## 3. Procedures

Follow these procedures for all standard infrastructure operations.

### Procedure 1: Plan and Apply Infrastructure Changes

**Objective**: To safely plan and apply infrastructure changes using IaC principles.

1. **Verify Authority**: Confirm you have **L2 (Agent)** authority for planning and **L3 (Senior Dev)** for staging applies.
2. **Create Feature Branch**: Create a new branch for the change (e.g., `feature/infra-update-s3-policy`).
3. **Modify IaC Code**: Make the necessary changes to the Terraform (`.tf`) files.
4. **Format and Validate**: Run `terraform fmt -recursive` and `terraform validate`.
5. **Generate Plan**: Run `terraform plan -out=tfplan`. Review the plan carefully for unintended changes.
6. **Submit for Review**: Commit the code and the plan output to the feature branch and open a Pull Request. An **L3 (Senior Dev)** must review and approve the plan.
7. **Apply Change**: Once approved, apply the change to the target environment (staging first). For production, an **L4 (Architect)** must approve.

### Procedure 2: Create a Reusable IaC Module

**Objective**: To create a new, reusable Terraform module that follows best practices.

1. **Verify Authority**: Confirm you have **L2 (Agent)** authority.
2. **Define Module Scope**: Clearly define the module's purpose, inputs (variables), and outputs.
3. **Create Directory Structure**: Create a new directory under `infrastructure/modules/`.
4. **Implement Module**: Create `main.tf`, `variables.tf`, and `outputs.tf`. Add a `README.md` explaining its usage.
5. **Add Example Usage**: Create an `examples/` directory showing how to use the module.
6. **Test Module**: Write a simple test configuration that provisions the module's resources in a temporary workspace.
7. **Submit for Review**: Open a PR for an **L3 (Senior Dev)** to review the module for correctness, security, and reusability.

### Procedure 3: Manage Terraform State

**Objective**: To handle Terraform state operations safely, as they are highly destructive.

1. **Verify Authority**: Confirm you have **L3 (Senior Dev)** authority. All state operations require **L4 (Architect)** approval.
2. **NEVER Modify State Manually**: State files should not be edited by hand. Use `terraform state` commands.
3. **Backup State**: Before any state operation, ensure a backup of the remote state exists.
4. **Use Workspaces**: Use Terraform workspaces to manage different environments (e.g., `staging`, `production`).
5. **State Locking**: Ensure remote state backend supports locking to prevent concurrent modifications.
6. **Importing Resources**: When importing existing infrastructure, use `terraform import` and verify the generated state.
7. **Review and Approve**: All state manipulation plans must be reviewed and approved by an **L4 (Architect)**.

### Procedure 4: Handle Infrastructure Security Scans

**Objective**: To proactively identify and remediate security issues in IaC.

1. **Verify Authority**: Confirm you have **L1 (Junior Dev)** authority or higher.
2. **Integrate Scanner**: Integrate a static analysis tool like `tfsec` or `checkov` into the CI/CD pipeline.
3. **Run Scans**: Scans should run automatically on every Pull Request that modifies `.tf` files.
4. **Review Findings**: Triage the findings based on severity (CRITICAL, HIGH, MEDIUM, LOW).
5. **Remediate Critical/High Issues**: All CRITICAL and HIGH severity findings must be fixed before merging.
6. **Document False Positives**: If a finding is a false positive, document the justification in the code or a separate policy file.
7. **Regular Audits**: Perform full repository scans on a quarterly basis to catch any new vulnerabilities.

---

## 4. Quick Decision Tree

Use this tree to determine the correct procedure for common tasks.

- **Is the task a change to existing infrastructure?**
  - **YES**: Go to **Procedure 1: Plan and Apply Infrastructure Changes**.
- **Is the task creating a new, reusable component?**
  - **YES**: Go to **Procedure 2: Create a Reusable IaC Module**.
- **Does the task involve `terraform state` commands or importing resources?**
  - **YES**: Go to **Procedure 3: Manage Terraform State**. This is a high-risk operation.
- **Is the task related to checking for security vulnerabilities?**
  - **YES**: Go to **Procedure 4: Handle Infrastructure Security Scans**.

---

## 5. Validation Checklist

Before submitting any infrastructure-related Pull Request, ensure it meets these criteria.

**Code Quality**:

- [ ] `terraform fmt -recursive` has been run.
- [ ] `terraform validate` passes.
- [ ] Variables and outputs are well-documented.
- [ ] No hardcoded secrets or sensitive values.
- [ ] Code is modular and follows DRY principles.

**Security**:

- [ ] `tfsec` or equivalent scan passes with no CRITICAL/HIGH findings.
- [ ] IAM policies follow the principle of least privilege.
- [ ] Security groups are restrictive and expose no unnecessary ports.
- [ ] Data is encrypted at rest and in transit.
- [ ] Logging and monitoring are enabled for all resources.

**Documentation**:

- [ ] PR description clearly explains the "what" and "why" of the change.
- [ ] `terraform plan` output is included in the PR.
- [ ] Any new modules have a `README.md` with usage examples.
- [ ] Complex logic is commented in the code.

**Compliance**:

- [ ] Changes adhere to global policies (e.g., `POLICY.md`).
- [ ] Resources are tagged according to the organization's tagging policy.
- [ ] The change does not violate any compliance frameworks (e.g., SOC2, GDPR).

---

## 6. Q&A / Common Questions

**Q: What should I do if `terraform plan` shows unexpected changes?**

**A**: Do NOT apply the plan. Investigate the root cause. It could be due to a provider update, manual changes in the cloud console (state drift), or incorrect code. Re-run the plan until it shows only the intended changes.

**Q: How do I manage secrets like API keys or database passwords?**

**A**: Use a dedicated secrets management tool like HashiCorp Vault or AWS Secrets Manager. Terraform should reference these secrets, not store them in state or version control.

**Q: Can I make a "quick fix" in the cloud console?**

**A**: No. All changes must go through the IaC workflow. Manual changes create state drift, are not peer-reviewed, and are not auditable. If an emergency fix is required, it must be immediately followed by a PR to codify the change.

**Q: What's the difference between a module and a resource?**

**A**: A resource is a single infrastructure object (e.g., an AWS S3 bucket). A module is a collection of resources that are used together to create a reusable component (e.g., a module to create a secure S3 bucket with logging and encryption).

**Q: How do we handle provider updates?**

**A**: Provider updates should be handled cautiously in a separate PR. Run `terraform plan` after updating the provider version to check for any breaking changes. Apply to staging first and run a full suite of integration tests.

---

## 7. References

This satellite is the **single source of truth** for infrastructure operations.

**Policy & Governance**:

- Global Policy: `POLICY.md`
- Document Classification: `DOCUMENT_CLASSIFICATION.md`
- Agent Instruction Strategy: `AGENT_INSTRUCTION_STRATEGY.md`

**Tools & Documentation**:

- Terraform: <https://www.terraform.io/docs>
- tfsec: <https://github.com/aquasecurity/tfsec>
- Checkov: <https://www.checkov.io/>

**CodeSentinel References**:

- Repository: <https://github.com/joediggidyyy/CodeSentinel>
- Deployment Satellite: `deployment/AGENT_INSTRUCTIONS.md`
- GitHub Satellite: `github/AGENT_INSTRUCTIONS.md`
