# CodeSentinel Non-Destructive Policy and `!!!!` Trigger

Principle: SECURITY > EFFICIENCY > MINIMALISM

The `!!!!` trigger is a development-audit accelerator. It MUST:

- Never remove features or reduce capability.
- Resolve conflicts and duplications safely.
- Enforce security, efficiency, and minimalism.
- Operate in non-destructive, feature-preserving mode by default.

Implementation details:

- Config carries a persistent `policy` section with:
  - `non_destructive: true`
  - `feature_preservation: true`
  - `conflict_resolution: "merge-prefer-existing"`
  - `principles: ["SECURITY", "EFFICIENCY", "MINIMALISM"]`
- Config also carries `dev_audit.trigger_tokens` including `!!!!` and `dev_audit.enforce_policy: true`.
- DevAudit reads and reports policy, and does not perform any destructive operations.
- Future automation invoked by `!!!!` MUST respect this policy; destructive actions (deletions, irreversible changes) are out-of-scope.

This policy is persistent and loaded on every run, guaranteeing that `!!!!` never results in feature loss.
