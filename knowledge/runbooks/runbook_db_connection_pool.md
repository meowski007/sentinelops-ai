# RB-DB-002: Resolving Database Connection Pool Exhaustion

## Summary
Procedures for identifying and mitigating database connection pool saturation, connection timeouts, and deadlock conditions in transactional data services.

## Symptoms
- Logs reporting `ConnectionTimeoutError: Pool exhausted`, `QueuePool limit of size 20 overflow 10 reached`, or `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
- Service response latency spikes dramatically (p95 > 3500ms) while CPU remains moderate.
- Cascading timeouts in upstream API gateway and checkout services.

## Root Causes
1. Long-running or unindexed analytical queries locking rows or holding connections open.
2. Connection leak in application code failing to release sessions in `finally` blocks.
3. Sudden surge in concurrent client connections exceeding max pool size.

## Triage & Verification
1. Inspect `log_entries` for database service with queries containing `PoolTimeout`, `idle in transaction`, or `deadlock detected`.
2. Check `metric_samples` for database service: verify active connection count and p95 latency.
3. Determine whether any rogue background batch job was started simultaneously.

## Remediation Actions
- **Immediate Mitigation:** Request approval for `drain_connection_pool` or `restart_service` on the database connection proxy.
- **Worker Throttling:** Temporarily scale down non-essential worker jobs consuming connections.
- **Post-Incident:** Optimize connection pool sizing (`pool_size`, `max_overflow`), and add pool checkout timeout alarms.
