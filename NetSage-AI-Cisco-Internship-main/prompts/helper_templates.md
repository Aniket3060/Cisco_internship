# NetSage AI: Helper Templates & Human Review Prompts

This document provides auxiliary prompt templates for the Human-in-the-Loop review workflow and post-fix validation.

---

## 1. Human Reviewer Verdict Form Template

When a human network engineer reviews a NetSage AI diagnosis, the following evaluation schema is recorded into the project audit log:

```markdown
### NetSage AI Review Ticket: [CASE-XXX]

**1. Incident Overview:**
- Symptom: [Brief description]
- Primary Suspect Component: [Device & Interface]

**2. AI Diagnosis Evaluation:**
- AI Proposed Root Cause: [Summary of AI output]
- AI Proposed OSI Layer: [Layer 2/3/4/7]
- AI Confidence: [High / Medium / Low]

**3. Human Reviewer Verdict:**
- [ ] **ACCEPTED**: Diagnosis is 100% accurate; proposed fix is correct and safe to apply.
- [ ] **EDITED**: Root cause was generally correct, but command syntax, subinterface ID, or sequence was corrected by the reviewer.
- [ ] **REJECTED**: AI misdiagnosed the fault or suggested an incorrect/unsafe action.

**4. Engineering Rationale / Corrections:**
- Reviewer Notes: [Explain why diagnosis was accepted, edited, or rejected]
- Corrected Commands (if applicable):
  ```text
  [Insert corrected CLI commands]
  ```

**5. Post-Remediation Status:**
- Verification Ping / Test: [Pass / Fail]
- Final State: [Resolved / Escalated]
- Reviewer Signature & Date: [Reviewer Name, Date]
```

---

## 2. Post-Remediation Verification Prompt

```markdown
Review the following post-remediation Cisco show command outputs to verify if the incident has been successfully resolved.

### Applied Configuration Changes:
```text
{{APPLIED_COMMANDS}}
```

### Post-Fix Verification Show Commands:
```text
{{POST_FIX_SHOW_OUTPUTS}}
```

### Required JSON Verification Response:
```json
{
  "resolution_status": "RESOLVED | UNRESOLVED | PARTIAL",
  "verification_evidence": "Description of why ping, routing table, or interface status confirms success",
  "remaining_anomalies": [],
  "rollback_required": false
}
```
```
