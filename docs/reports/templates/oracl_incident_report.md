# ORACL Incident Report Template

**Classification**: Tier-2 / Internal Use Only  
**Visibility**: Internal  
**Sensitive**: trackable  
**Owner**: ORACL Operations  
**File Path**: `docs/reports/templates/oracl_incident_report.md`
  
**Generated:** {{ timestamp }}

---

## 1. Snapshot

- **Incident ID**: {{ incident_id }}
- **Severity**: {{ severity }}
- **Analytic Report Due**: {{ analytic_due }}
- **Action Report Due**: {{ action_due }}
- **Date / Time Range**: {{ time_range }}
- **Primary Engineer**: {{ primary_engineer }}
- **Active Mode**: {{ active_mode }}
- **Aggression Level**: {{ aggression_level }}
- **Advise Level**: {{ advise_level }}
- **Confidence at Detection**: {{ confidence_at_detection }}

## 2. Timeline

| Step | Timestamp | Action | Mode / Aggression | Confidence | Notes |
|------|-----------|--------|-------------------|------------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## 3. Root Cause & Impact

- **Trigger**: {{ trigger }}
- **Affected Assets / Files**: {{ affected_assets }}
- **Observed Impact**: {{ observed_impact }}
- **Fortunate Hallucination?** {{ hallucination_flag }}

## 4. Corrective Actions

- [ ] Immediate containment steps completed
- [ ] Documentation updated (paths)
- [ ] Mode/Aggression reset to default (`flex3`)
- **Follow-up Tasks**:
  1. `task`
  2. `task`

## 5. Compliance Feedback

- **Collaboration Index Before / After**: {{ collaboration_shift }}
- **Reward or Punishment Applied**: {{ reward_action }}
- **Report Filed By**: {{ report_filed_by }}
- **Report Approved By**: {{ report_approved_by }}

---

> Store completed reports under `docs/reports/INCIDENT_REPORTS/INC-YYYYMMDD-###.md` with Tier-2 protections.
