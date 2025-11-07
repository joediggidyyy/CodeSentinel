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

**When**: Any change to existing infrastructure is required, from a simple security group update to a major resource modification.

**Steps**:

1. **Branch and Scope**:
    - Create a new, descriptively named feature branch from `main` (e.g., `feature/infra-update-rds-encryption`).
    - Clearly define the scope of the change. A single PR should address a single logical change.

2. **Modify IaC Code**:
    - Locate and modify the relevant Terraform (`.tf`) files in the `infrastructure/` directory.
    - Adhere to the principle of least privilege. For IAM roles or security groups, only grant the minimum necessary permissions.

3. **Local Validation and Formatting**:
    - Run `terraform fmt -recursive` to ensure all code is correctly formatted.
    - Run `terraform validate` to check for syntax errors and internal consistency.

4. **Generate and Analyze the Plan**:
    - Run `terraform plan -out=tfplan`. This is the most critical step.
    - **Scrutinize the output**: Carefully review every proposed `create`, `update`, and `destroy` action. Ensure there are no unintended or collateral changes. If the plan is not 100% expected, do not proceed. Investigate and fix the code.

5. **Submit for Peer Review**:
    - Commit the modified `.tf` files and the `tfplan` output to your branch.
    - Open a Pull Request. The PR description must include:
        - A clear explanation of *what* the change is and *why* it is needed.
        - The full output of the `terraform plan`.
        - Any potential risks or impacts.
    - An **L3 (Senior Dev)** must review and approve the PR. For production changes, an **L4 (Architect)** must also approve.

6. **Apply to Staging**:
    - Once the PR is approved, merge it into `main`.
    - The CI/CD pipeline will automatically apply the plan to the **staging** environment.
    - Monitor the `apply` job and verify that the changes were deployed successfully. Run integration tests to confirm the environment is healthy.

7. **Promote to Production**:
    - Production applies are **manual**. After staging has been verified, a user with **L4 (Architect)** privileges must approve the production deployment job in the CI/CD pipeline.
    - This manual gate ensures a final review before impacting users.

---

### Procedure 2: Create a Reusable IaC Module

**When**: A pattern of resources is being repeated across the infrastructure, and creating a standardized, reusable component would improve consistency and maintainability.

**Steps**:

1. **Define the Module Contract**:
    - Clearly define the module's purpose and boundaries.
    - **Inputs (`variables.tf`)**: Define all configurable parameters. Provide descriptions, types, and sensible defaults where possible.
    - **Outputs (`outputs.tf`)**: Define the values the module will expose to its consumers (e.g., resource IDs, DNS names).

2. **Develop the Module**:
    - Create a new directory for the module under `infrastructure/modules/` (e.g., `secure-s3-bucket`).
    - Implement the core logic in `main.tf`.
    - **Add a `README.md`**: This is mandatory. The README must contain:
        - A description of what the module does.
        - All input variables and their purpose.
        - All outputs.
        - A clear example of how to use the module.

3. **Implement Versioning and Tagging**:
    - Add a `versions.tf` file to pin the required Terraform and provider versions.
    - Ensure all resources created by the module are tagged with the module's name and version for traceability.

4. **Write Tests and Examples**:
    - Create an `examples/` directory within the module folder.
    - Provide at least one working example of how to instantiate the module.
    - Use a simple test framework or a separate Terraform configuration to provision and destroy the module's resources to ensure it works as expected.

5. **Submit for Review**:
    - Open a Pull Request. An **L3 (Senior Dev)** must review the module for:
        - **Correctness**: Does it provision the correct resources?
        - **Security**: Does it follow the principle of least privilege? Are resources secure by default?
        - **Reusability**: Is it generic enough to be used in different contexts?
        - **Documentation**: Is the `README.md` clear and complete?

### Procedure 3: Manage Terraform State

**When**: A high-risk operation is required that directly manipulates the Terraform state file, such as importing an existing resource or resolving state drift. These operations are dangerous and require architect-level approval.

**Steps**:

1. **Emergency and Approval**:
    - State manipulation is an emergency-only procedure. It should never be part of a standard workflow.
    - Obtain explicit approval from an **L4 (Architect)** before proceeding. The justification must be documented in a GitHub issue.

2. **Backup the State**:
    - Before any operation, manually create a backup of the remote state file. The remote backend (e.g., S3 bucket) should have versioning enabled, but a manual backup provides an extra layer of safety.

3. **Use a Dedicated, Locked Workspace**:
    - Perform the state operation on a clean, isolated machine or container.
    - Ensure state locking is active to prevent anyone else from running `apply` while you are manipulating the state.

4. **Execute the State Command**:
    - Use the appropriate `terraform state` subcommand (e.g., `mv`, `rm`, `replace-provider`).
    - **For `terraform import`**:
        - Write the resource configuration block in your `.tf` code first.
        - Run `terraform import <RESOURCE_ADDRESS> <RESOURCE_ID>`.
        - Run `terraform plan` immediately after to verify that Terraform now sees the imported resource as being under its control and that there are no differences.

5. **Verify and Document**:
    - After the operation, run `terraform plan` to confirm the state file accurately reflects the desired reality and that no further changes are planned.
    - Document the entire procedure, including the commands run and the reasons for the operation, in the corresponding GitHub issue.

---

### Procedure 4: Handle Infrastructure Security Scans

**When**: A security vulnerability is detected in the IaC code, either by the automated CI pipeline scanner or a manual audit.

**Steps**:

1. **Automated Scanning in CI**:
    - The CI pipeline is configured to run a static analysis security scanner (e.g., `tfsec`, `checkov`) on every Pull Request that modifies `.tf` files.
    - The pipeline will fail if any **CRITICAL** or **HIGH** severity vulnerabilities are detected.

2. **Triage and Prioritize Findings**:
    - Review the scanner's output in the failed CI job.
    - **CRITICAL/HIGH**: These must be remediated immediately. The PR cannot be merged until they are fixed.
    - **MEDIUM/LOW**: Create a GitHub issue to track the finding. These should be addressed in a timely manner but do not block the merge unless they violate a specific policy.

3. **Remediate the Vulnerability**:
    - Modify the IaC code to fix the issue. This often involves:
        - Applying more restrictive IAM policies.
        - Closing open ports in security groups.
        - Enabling encryption or logging on resources.
    - Push the fix to the PR branch. The CI pipeline will re-run, and the scan should now pass.

4. **Handling False Positives**:
    - If a finding is determined to be a false positive, you must explicitly ignore it.
    - Add a comment directly above the resource in the `.tf` file (e.g., `#tfsec:ignore:aws-s3-enable-bucket-logging`).
    - The comment must include a clear justification for why the finding is being ignored. This creates an auditable record.

5. **Regular Audits**:
    - In addition to PR scans, a full scan of the `main` branch is run on a weekly schedule.
    - This process ensures that new vulnerability definitions from the scanner are applied to the existing codebase and helps catch anything that might have been missed. Any findings from this audit are tracked as new GitHub issues.

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
