# RB-OPS-006: Safe Deployment Rollback Standard Operating Procedure

## Summary
Enterprise standard operating procedure for safely aborting and rolling back a software release or configuration update during an active incident.

## Pre-Conditions for Rollback
- Incident is actively causing customer-facing degradation (Severity CRITICAL or HIGH).
- Telemetry shows error rates or latency spiked within 30 minutes following a new deployment version.
- Database schema migrations from the release are backward-compatible.

## Rollback Protocol
1. **Identify Stable Target Version:** Check the last known good deployment event in `deployment_events` table (status `SUCCESS`).
2. **Submit Remediation Request:** Propose `rollback_deployment` with the target version and affected service ID.
3. **Risk Level:** Classified as HIGH risk because it alters running binary and configuration state in production.
4. **Approval Gate:** Must be approved by Incident Commander, Tech Lead, or authorized Senior Operator.
5. **Execution & Health Check:** Verify the simulated rollout completes, pods report healthy status, and error rate drops below 1%.
