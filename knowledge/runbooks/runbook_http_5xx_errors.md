# RB-5XX-001: Investigating High HTTP 5xx Server Error Spikes

## Summary
This runbook guides IT Operations and SRE teams in diagnosing sudden surges in HTTP 500, 502, and 503 response codes across microservices and API gateways.

## Symptoms
- Elevated error rate exceeding 5% of total request volume.
- Upstream gateway logging HTTP 500 "Internal Server Error" or 502 "Bad Gateway".
- Spike in application exception stack traces (`NullPointerException`, `KeyError`, `UnhandledPromiseRejection`).

## Immediate Triage Steps
1. **Correlate with Recent Deployments:** Check `deployment_events` within the last 30 minutes for the affected service. Over 70% of 5xx spikes immediately follow code or configuration rollouts.
2. **Inspect Application Error Logs:** Search logs filtered by `log_level=ERROR` and look for stack traces containing route handlers or configuration parsing errors.
3. **Check Downstream Dependencies:** Verify if downstream database or authorization services are degraded or returning network timeouts.
4. **Evaluate Traffic Spikes:** Confirm whether total request volume has doubled, indicating denial of service or unexpected batch traffic.

## Remediation Procedures
- **If caused by recent deployment:** Execute simulated `rollback_deployment` to the previous stable release version. Requires Incident Commander / Lead approval.
- **If caused by transient unhandled crash:** Perform a controlled simulated `restart_service` to clear corrupt memory state.
- **Post-remediation:** Monitor error rate for 5 consecutive minutes until it drops below the 1.0% healthy baseline threshold.
