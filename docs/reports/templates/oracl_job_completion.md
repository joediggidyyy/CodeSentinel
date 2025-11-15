# ORACL Job Completion Report Template

**Classification**: Tier-2 / Internal Use Only  
**Visibility**: Internal  
**Sensitive**: trackable  
**Owner**: ORACL Operations  
**File Path**: `docs/reports/templates/oracl_job_completion.md`
  
**Generated:** {{ timestamp }}

---

## 1. Work Summary

- **Job ID / Name**: {{ job_id }}
- **Severity Alignment**: {{ severity }}
- **Analytic Report Due**: {{ analytic_due }}
- **Action Report Due**: {{ action_due }}
- **Timeframe**: {{ timeframe }}
- **Engineer(s)**: {{ engineers }}
- **Requested Mode**: {{ requested_mode }}
- **Actual Mode Timeline**: {{ mode_timeline }}
- **Aggression Range**: {{ aggression_range }}

## 2. Scope & Deliverables

| Deliverable | Path | Status | Validation Completed |
|-------------|------|--------|----------------------|
| | | | |
| | | | |

**Deliverable Notes**: {{ deliverable_notes }}

## 3. Decision & Hallucination Ledger

| Step | Recommendation | Action Taken | Confidence | Outcome | Notes |
|------|----------------|--------------|------------|---------|-------|
| 1 | | | | | |
| 2 | | | | | |

**Decision Summary**: {{ decision_summary }}

## 4. Compliance Checklist

- [ ] All SEAM priorities satisfied (Security > Efficiency > Minimalism)
- [ ] Mode resets to `flex3`
- [ ] Reports/Docs updated (list)
- [ ] Tests run (list commands + results)

**Documentation Updates**: {{ reports_updated }}  
**Test Coverage Summary**: {{ tests_run }}  
**SEAM Compliance Notes**: {{ seam_status }}

## 5. Metrics Snapshot

- **Collaboration Index (avg)**: {{ collaboration_index }}
- **Compliments Logged**: {{ compliments_logged }}
- **Rewards / Punishments Applied**: {{ rewards_applied }}
- **Follow-on Tasks**: {{ follow_on_tasks }}

---

> Store completed reports under `docs/reports/PHASE_REPORTS/JOB-YYYYMMDD-###.md` or the phase-specific directory referenced by the task charter.
