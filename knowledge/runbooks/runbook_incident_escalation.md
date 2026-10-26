# RB-ESC-007: Enterprise Incident Triage and Escalation Policy

## Summary
Defines severity levels, communication cadences, escalation paths, and operational role responsibilities for IT incidents.

## Severity Classifications
- **CRITICAL (Sev-1):** Total outage of core user-facing functionality (e.g., auth-service down, payment checkout failing, global 5xx rate > 10%). SLA to engage: < 5 minutes.
- **HIGH (Sev-2):** Significant service degradation or failure of major subcomponent with partial redundancy (e.g., database connection pool saturated, p95 latency > 3000ms). SLA to engage: < 15 minutes.
- **MEDIUM (Sev-3):** Degraded background processing, non-blocking queue backlog, or elevated warnings without customer impact. SLA to engage: < 1 hour.
- **LOW (Sev-4):** Minor cosmetic or non-urgent infrastructure anomalies. SLA: Next business day.

## Escalation Workflow
1. Detector alerts trigger incident creation in `TRIGGERED` status.
2. On-call operator acknowledges incident (`ACKNOWLEDGED`), establishing ownership.
3. Automated investigation is launched to gather telemetry and formulate root-cause hypothesis.
4. If remediation requires state changes, operator submits remediation proposal and awaits Commander approval.
5. Once verified resolved, incident transitions to `RESOLVED` and post-mortem audit record is saved.
