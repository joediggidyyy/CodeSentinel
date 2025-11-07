# CodeSentinel Non-Destructive Policy and `!!!!` Trigger

## Fundamental Policy Hierarchy

**Priority Distribution (Descending Importance):**

1. **CORE CONCEPTS** (Absolute Priority)
   - SECURITY > EFFICIENCY > MINIMALISM
   - These three principles guide ALL decisions
   - Higher priority concept always overrides lower priority

2. **PERMANENT DIRECTIVES**
   - Non-negotiable security rules (credential management, audit logging)
   - Cannot be violated under any circumstances
   - Always in effect

3. **PERSISTENT POLICIES**
   - Non-destructive operations, feature preservation, style preservation
   - Can be overridden ONLY when they explicitly violate Core Concepts or Permanent Directives

**This hierarchy is fundamental to CodeSentinel's operating policy.**

## Development Audit Execution

The `!!!!` trigger is a development-audit accelerator that:

- **Executes thoroughly and comprehensively** - Always complete analysis
- **Focuses heavily on the three core concepts** - Security, Efficiency, Minimalism
- **Complies with all directives and policies** - EXCEPT where they would explicitly violate a core concept
- **Never removes features or reduces capability** - Unless security demands it
- **Resolves conflicts and duplications safely** - Following the hierarchy
- **Operates in non-destructive, feature-preserving mode by default**

Implementation details:

- Config carries a persistent `policy` section with:
  - `non_destructive: true`
  - `feature_preservation: true`
  - `conflict_resolution: "merge-prefer-existing"`
  - `principles: ["SECURITY", "EFFICIENCY", "MINIMALISM"]`
  - `hierarchy: ["CORE_CONCEPTS", "PERMANENT_DIRECTIVES", "PERSISTENT_POLICIES"]`
- Config also carries `dev_audit.trigger_tokens` including `!!!!` and `dev_audit.enforce_policy: true`.
- DevAudit reads and reports policy, and does not perform any destructive operations.
- Future automation invoked by `!!!!` MUST respect this policy hierarchy

This policy is persistent and loaded on every run, guaranteeing that `!!!!` never results in feature loss unless absolutely required by security concerns.

---

## Documentation Standards & Professional Branding (T2-Permanent Directive)

**Classification**: T2 - Permanent Directive  
**Effective Date**: November 2025  
**Scope**: All CodeSentinel documentation, comments, and public-facing content  
**Authority**: Core Principle - Elegant Professionalism

### Directive Statement

**All documentation will maintain professional elegance through consistent styling:**

1. **Emoji Usage Policy**
   - Use checkmarks and X marks only when they add clarity to conditions or acceptance criteria
   - Use other emojis ONLY when they meaningfully help visualize conditions or states
   - Avoid decorative emoji that does not serve functional purpose
   - Never use emoji that adds visual clutter or reduces professional presentation
   - All emoji must pass the "elegant professionalism" test: Does this enhance understanding or detract from it?

2. **Formatting Standards**
   - All documentation formatted cleanly and uniformly
   - Projects competence, clarity, and attention to detail
   - Consistent heading hierarchy throughout
   - Proper spacing and visual separation of concepts
   - No excessive decoration or unnecessary embellishment

3. **Professional Branding**
   - Subtle branding that reflects CodeSentinel's security-first, professional identity
   - Language that demonstrates expertise and reliability
   - Consistent tone across all documentation
   - Architecture and structure that shows careful thought and planning

4. **Character Encoding Requirements**
   - All documentation in UTF-8 encoding (no BOM)
   - No corrupted or garbled characters
   - Tree structures rendered as clean ASCII (├──, └──, │) not Unicode box-drawing
   - All non-ASCII characters must be intentional and serve a purpose

### Enforcement

- Code reviews will verify documentation meets these standards
- CI/CD pipeline will validate UTF-8 encoding and character integrity
- Policy applies to README files, architectural documents, code comments, and API documentation
- Violations identified during `!!!!` audits will be flagged for correction

### Rationale

Professional documentation builds trust with enterprise users and demonstrates security-first competence. Elegant simplicity in presentation reflects the same care applied to code security and reliability. This directive reinforces CodeSentinel's commitment to professionalism alongside its security principles.
