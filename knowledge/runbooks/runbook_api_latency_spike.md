# RB-LAT-003: Triaging Downstream API Dependency Latency

## Summary
Troubleshooting guide for sudden increases in round-trip latency and 504 Gateway Timeouts caused by degraded internal or external upstream microservices.

## Symptoms
- API Gateway p95 latency exceeds 2000ms (normal SLA baseline < 150ms).
- Client requests timing out at edge proxy.
- Thread or connection exhaustion in ingress containers.

## Investigation Workflow
1. Check latency distribution breakdown across services in `metrics_overview`.
2. Inspect log entries for `upstream timed out (110: Connection timed out)` or `HttpClientTimeoutException`.
3. Check deployment history: verify if a dependency rollout altered timeout configurations.
4. Verify circuit breaker metrics: check if circuit breakers are tripping or remaining half-open.

## Remediation Protocol
- **Enable Dependency Circuit Breaker / Fallback:** Divert traffic to fallback cached responses or degraded mode.
- **Scale Worker/Proxy Capacity:** If load has exceeded normal throughput, request approval to `scale_worker_pool`.
- **Escalate to Dependency Team:** If the external partner API is degraded, engage on-call vendor contact.
