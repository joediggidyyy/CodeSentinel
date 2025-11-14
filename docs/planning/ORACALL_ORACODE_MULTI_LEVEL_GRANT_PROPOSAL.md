# ORACall / ORACode Multi-Level Grant Proposal

**Classification**: Strategic Funding Proposal (Internal)  
**Prepared For**: Joe Waller (CEO / CTO / Board Chair)  

---

## 1. Corporate Philosophy (Short Creed)

This proposal is grounded in the core CodeSentinel philosophies captured in `CORPORATE_PHILOSOPHY_AND_ENGINEERING_VALUES.md`. In condensed form, the creed is:

1. **Non-destructive operations (archive-first)** – We never delete without a recovery path.
1. **All data has value potential** – Operational history and metadata are future intelligence, not waste.
1. **Improve the world, make it more free** – Technology should increase autonomy, transparency, and resilience.
1. **Technology and information belong to us all; personal data belongs to the individual** – Infrastructure and knowledge should be widely accessible; personal data is sovereign.
1. **Deliberate, sustainable growth (not blitzscale at all costs)** – We scale only when it improves long-term resilience, security, and freedom.

Funding levels, hiring plans, and roadmap choices in this document should be explainable by pointing back to one or more of these principles.

For detailed implications and engineering practices, see `CORPORATE_PHILOSOPHY_AND_ENGINEERING_VALUES.md`.

---

## 2. Compensation and Payroll Assumptions

- CEO / CTO / Board Chair (Joe Waller): 220,000
- Senior Software Engineer: 180,000
- SRE: 170,000
- Security Engineer: 185,000
- Product / Program Manager: 150,000

Payroll load (benefits, taxes, overhead) is approximated as 25 percent on top of base salary. Effective annual planning costs are therefore:

- CEO / CTO / Board Chair (Joe Waller): 275,000
- Senior Software Engineer: 225,000
- SRE: 212,500
- Security Engineer: 231,250
- Product / Program Manager: 187,500

All figures are illustrative and must be validated before use in contracts or offers.

---

## 4. Investment Tiers Overview

### 4.1 Headcount Mix by Tier

The FTE mix per tier is aligned with `MARKET_NEEDS_COSTS_AND_ADOPTION_ESTIMATES.md`:

| Role | Tier 1 FTE | Tier 2 FTE | Tier 3 FTE |
|------|------------|------------|------------|
| CEO / CTO / Board Chair (Joe Waller) | 0.4 | 0.6 | 0.8 |
| Senior Software Engineer | 1.0 | 2.0 | 4.0 |
| SRE | 0.5 | 1.0 | 2.0 |
| Security Engineer | 0.5 | 1.0 | 2.0 |
| Product / Program Manager | 0.2 | 0.6 | 1.5 |

### 4.2 Annual Payroll by Tier (Summary)

Using the effective annual costs and FTE mix above, approximate annual payroll per tier is:

- **Tier 1 (Modest)**: Approximately 594,000
- **Tier 2 (Adequate)**: Approximately 1,171,000
- **Tier 3 (Aggressive)**: Approximately 2,288,750

More detailed breakdowns are available in `MARKET_NEEDS_COSTS_AND_ADOPTION_ESTIMATES.md`.

---

## 5. Tier 1 — Modest Investment Plan

### 5.1 Scope

- Implement core ORACall PEI protocol with production-ready schema, ingestion CLI, and TRIAD indexing.
- Implement minimum viable ORACode semantics with a central vocabulary registry and basic annotation commands.
- Integrate Calamum for baseline performance and security regression testing (limited scenario coverage).
- Provide documentation and basic operator runbooks for dual reports, signatures, and archive-first workflows.

### 5.2 Timeline (Indicative)

- Months 0–3: Core ORACall implementation, schema, and ingestion pipeline.
- Months 3–6: ORACode minimal semantics, baseline Calamum scenarios, documentation polish.

### 5.3 Staffing and Payroll

- FTE allocation from Section 4.1.
- Annual payroll estimate: approximately 594,000 (including 25 percent payroll load).
- Funding ask for a 12-month Tier 1 program: 594,000 plus infrastructure costs described in `MARKET_NEEDS_COSTS_AND_ADOPTION_ESTIMATES.md`.

### 5.4 Key Deliverables

- `codesentinel oracall` CLI with production-ready PEI ingestion.
- `codesentinel oracode` minimal semantics commands and registry.
- Calamum baseline scenarios and performance benchmarks.
- Updated documentation and runbooks.

### 5.5 Risks and Mitigations

- **Risk**: Limited automation may slow adoption.  
  **Mitigation**: Focus on rock-solid core functionality and clear documentation.

- **Risk**: Reduced Calamum coverage.  
  **Mitigation**: Prioritize critical security and performance scenarios.

### 5.6 Impact and ROI (Tier 1)

- **Impact**:
  - Establishes a secure, signed PEI trail for engineering work inside a single organization.
  - Reduces incident investigation time by improving structure and searchability of historical changes.
  - Lays the foundation for future automation and analytics without committing to more complex centralization.

- **ROI Framing**:
  - For teams with high downtime or incident costs, even modest reductions in mean time to resolution can offset a significant portion of the Tier 1 investment.
  - Converts existing, informal processes into a reusable data asset that supports compliance and future AI use cases.

---

## 6. Tier 2 — Adequate Investment Plan

### 6.1 Scope

- All Tier 1 deliverables.
- Expanded ORACode semantics, including richer DSL constructs and conflict resolution tooling.
- Comprehensive Calamum scenario coverage for ORACall and ORACode, including agent and non-agent flows.
- Single-organization centralization layer as described in `SCALABILITY_AND_CENTRALIZATION_ROADMAP.md` (Phase 2).
- Deeper integration with ORACL tiers and performance regression gating in CI.

### 6.2 Timeline (Indicative)

- Months 0–3: Tier 1 activities.
- Months 3–9: Expanded semantics, Calamum scenarios, central aggregator, dashboards.

### 6.3 Staffing and Payroll

- FTE allocation from Section 4.1.
- Annual payroll estimate: approximately 1,171,000.
- Funding ask for a 12-month Tier 2 program: 1,171,000 plus infrastructure and tooling costs.

### 6.4 Key Deliverables

- Full ORACall / ORACode feature set as defined in the comprehensive proposal.
- Calamum suite exercising conflict resolution, adversarial inputs, and performance extremes.
- Central aggregation and dashboarding for a single organization.
- Automated regression gates enforced in continuous integration.

### 6.5 Risks and Mitigations

- **Risk**: Centralization increases operational complexity.  
  **Mitigation**: Reuse existing observability tooling; follow roadmap guidelines for Phase 2.

- **Risk**: Higher upfront spend.  
  **Mitigation**: Phased milestones with clear success criteria and go/no-go gates.

### 6.6 Impact and ROI (Tier 2)

- **Impact**:
  - Moves from foundational logging to an operational platform with central views, rich semantics, and full Calamum coverage.
  - Standardizes workflows and regression gates, reducing repetitive manual work and catching issues earlier in the lifecycle.
  - Provides organization-wide visibility into reliability and security trends, enabling better prioritization.

- **ROI Framing**:
  - Improved reliability and reduced incident frequency/severity can yield substantial savings in lost revenue and engineering time.
  - Standardization and automation reduce the opportunity cost of senior engineers performing manual coordination and forensics.
  - Creates a platform foundation that can be extended toward revenue-generating offerings (Tier 3) without rework.

---

## 7. Tier 3 — Aggressive Investment Plan

### 7.1 Scope

- All Tier 1 and Tier 2 deliverables.
- Federated, multi-tenant deployment capabilities as outlined in Phase 3 of `SCALABILITY_AND_CENTRALIZATION_ROADMAP.md`.
- Advanced analytics on top of ORACall / ORACode data (for example, organizational risk heatmaps, semantic trend analysis).
- Extended Calamum test suites and fuzzing for federated scenarios.
- Preparatory work for external integrations (for example, customer-facing analytics, partner pipelines).

### 7.2 Timeline (Indicative)

- Months 0–6: Tier 2 scope.
- Months 6–18: Federation, advanced analytics, extended Calamum suites, and external integration pilots.

### 7.3 Staffing and Payroll

- FTE allocation from Section 4.1.
- Annual payroll estimate: approximately 2,288,750.
- Funding ask for a 18-month Tier 3 program: pro-rated payroll plus infrastructure and additional analytics costs.

### 7.4 Key Deliverables

- Federated, multi-tenant ORACall / ORACode infrastructure.
- Advanced analytics dashboards and reports.
- Comprehensive Calamum coverage including federated and cross-tenant scenarios.
- Pilot external integrations with selected partners or customers.

### 7.5 Risks and Mitigations

- **Risk**: Complexity of multi-tenant security and isolation.  
  **Mitigation**: Strict SEAM controls, independent audits, and extensive Calamum coverage.

- **Risk**: Market timing and adoption uncertainty.  
  **Mitigation**: Stage-gated rollout and pilot programs with early adopters.

### 7.6 Impact and ROI (Tier 3)

- **Impact**:
  - Elevates ORACall / ORACode from an internal platform to a multi-tenant service capable of supporting multiple organizations.
  - Enables advanced analytics across deployments (subject to SEAM constraints), such as cross-org risk heatmaps and trend analyses.
  - Opens a path to external offerings, including managed services or enterprise subscriptions.

- **ROI Framing**:
  - Provides clear revenue opportunities through platform commercialization, in addition to internal efficiency and risk-reduction gains.
  - Aggregated learning across tenants can improve resilience and detection for all participants, increasing long-term value.
  - The incremental cost from Tier 2 to Tier 3 is focused on capabilities that can directly drive external value, rather than purely internal productivity.

---

## 8. Engineering Values, Methodologies, and Metrics

This grant proposal is not only about what we build, but how we build it. Our engineering approach is governed by the philosophies in `CORPORATE_PHILOSOPHY_AND_ENGINEERING_VALUES.md`. For planning and hiring purposes, the key points are:

1. **Non-destructive operations in practice**
   - All cleanup and restructuring work (for example, root policy enforcement, archive compaction) must follow an archive-first, rollback-friendly pattern.
   - CLI commands affecting repositories, archives, or logs must support `--dry-run` where practical and log actions for later review.

1. **Data as a long-term asset**
   - ORACall schemas are preferred over ad-hoc logs for critical events.
   - ORACode semantics are applied first to flows that matter for security, reliability, and compliance.
   - We measure success by how often existing PEI data is sufficient to answer incident and audit questions.

1. **Freedom, openness, and personal data stewardship**
   - Protocols and file formats are documented as if they will be made public.
   - Personal data is minimized and, where present, separated from PEI and operational data.
   - Design reviews explicitly call out personal-data handling and retention.

1. **Sustainable, incremental growth**
   - Major capabilities (for example, federation, external analytics) are gated on clear decision points, Calamum results, and SEAM reviews.
   - We prefer staged rollouts (feature flags, pilot tenants) over big-bang launches.

Indicative metrics we will track as part of this grant include:

- Ratio of archive-first operations to permanent deletions in cleanup workflows.
- Percentage of major incidents where existing ORACall / ORACode data was sufficient for root cause analysis.
- Number of features implemented with zero personal data collection.
- Ratio of staged rollouts to big-bang changes.
- Number of regressions caught by Calamum and CI before reaching production.

These metrics inform both internal governance (Section 8) and external reporting obligations, and they are intended to align engineering incentives with SEAM Protection.

---

## 9. Governance and Decision Gates

- All tiers require explicit SEAM and security review prior to major milestone transitions.
- Decision gates mirror those in the feasibility study (schema sign-off, security validation, integrated demo, documentation completion).
- The injected objective proposal governs how new goals are introduced without destabilizing existing plans.

---

## 10. Request and Next Steps

- Proceed with **Tier 2 (Adequate Investment)** as the default target for internal planning and execution.
- Preserve **Tier 1 (Modest Investment)** as a contingency plan in case of constrained funding.
- Treat **Tier 3 (Aggressive Investment)** as a graduation track: expand from Tier 2 to Tier 3 once Tier 2 milestones and decision gates are met.
- Align funding timelines with the indicative schedules per tier.
- Use pilot deployments and Calamum metrics to refine actual costs and adoption trajectories.
- Update this proposal as compensation data and infrastructure pricing evolve.

---

## 11. Appendix A — Suggested Slide Deck Outline

This appendix captures a recommended slide-by-slide outline for external presentations to investors and engineers. It is derived from this proposal and related planning documents.

1. **Title Slide**

- ORACall / ORACode: SEAM-Compliant PEI & Semantics Platform.
- Prepared by: Joe Waller (CEO / CTO / Board Chair).
- Date.

1. **Problem & Opportunity**

- The lack of cryptographically verifiable, semantically rich histories of engineering work.
- Difficulty proving reliability and security to regulators and customers.
- The need for safe, governed context for AI agents.

1. **Solution Overview**

- ORACall: PEI event capture (dual reports, signatures, archive-first).
- ORACode: semantic overlay (central vocabularies, conflict resolution).
- Calamum: adversarial and regression harness.

1. **Architecture & SEAM Principles**

- High-level architecture diagram (conceptual).
- SEAM: Security, Efficiency, And Minimalism.
- Agent-aware but not agent-dependent.

1. **Roadmap Snapshot**

- Phase 1: Repo-local deployments.
- Phase 2: Organization-level centralization (Tier 2 target).
- Phase 3: Federated, multi-tenant platform (Tier 3).

1. **Investment Tiers Overview**

- Table with Tier 1 / Tier 2 / Tier 3, scope summary, indicative duration, and high-level payroll bands.
- Call out that Tier 2 is the current internal target.

1. **Tier 1 — Core Foundation**

- Scope and key deliverables.
- Impact and ROI highlights from Section 5.6.
- Annual payroll estimate and indicative timeline.

1. **Tier 2 — Platform Maturity (Current Target)**

- Scope and key deliverables.
- Impact and ROI highlights from Section 6.6.
- Annual payroll estimate and indicative timeline.

1. **Tier 3 — Federated Platform (Graduation Path)**

- Scope and key deliverables.
- Impact and ROI highlights from Section 7.6.
- Annual payroll estimate and indicative timeline.

1. **Governance & Risk Management**

- SEAM controls and archive-first policies.
- Calamum coverage and regression gates.
- Decision gates and injected objective governance.

1. **Team & Roles**

- Joe Waller as CEO / CTO / Board Chair.
- Engineering, SRE, Security, and Product roles.

1. **Ask & Next Steps**

- Proposed starting point at Tier 2 with option to graduate to Tier 3.
- Pilot deployments and metrics-driven refinement.
- Follow-up sessions (deep technical dives, hiring discussions).
