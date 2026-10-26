# SentinelOps AI - REST API Guide

The SentinelOps AI backend exposes a REST API built with FastAPI and OpenAPI 3.1. Interactive API documentation is available at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.

---

## 1. System Health

### `GET /health`
System uptime probe and database health verification.

```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "SentinelOps AI",
  "version": "1.0.0",
  "environment": "development",
  "database": "healthy",
  "ai_engine_mode": "LOCAL_DETERMINISTIC",
  "uptime_seconds": 124.5,
  "timestamp": "2026-10-26T17:00:00Z"
}
```

---

## 2. Services & Telemetry

### `GET /api/services`
Lists all monitored microservices and current health statuses.

### `GET /api/metrics/overview`
Aggregated telemetry overview for dashboard metrics and charts.

**Response (200 OK):**
```json
{
  "timestamp": "2026-10-26T17:00:00Z",
  "active_incidents_count": 4,
  "critical_count": 2,
  "services": [
    {
      "service_id": "api-gateway",
      "service_name": "API Gateway & Ingress Proxy",
      "status": "DEGRADED",
      "error_rate": 14.8,
      "latency_p95_ms": 1150.0,
      "cpu_percent": 74.0,
      "request_volume": 6160,
      "samples": [...]
    }
  ]
}
```

---

## 3. Incidents Management

### `GET /api/incidents`
Queries incidents with optional filtering.

**Query Parameters:**
- `severity` (optional): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `status` (optional): `TRIGGERED`, `ACKNOWLEDGED`, `INVESTIGATING`, `MITIGATED`, `RESOLVED`
- `service_id` (optional): `api-gateway`, `order-db`, etc.
- `search` (optional): Text search query

### `PATCH /api/incidents/{incident_id}`
Updates incident status.

```bash
curl -X PATCH http://localhost:8000/api/incidents/INC-2026-001 \
  -H "Content-Type: application/json" \
  -d '{"status": "ACKNOWLEDGED"}'
```

### `GET /api/incidents/{incident_id}/timeline`
Reconstructs chronological timeline of deployments, error logs, detections, investigations, and remediations.

---

## 4. AI Investigation Assistant

### `POST /api/incidents/{incident_id}/investigate`
Triggers an automated multi-tool investigation.

```bash
curl -X POST http://localhost:8000/api/incidents/INC-2026-001/investigate \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "incident_id": "INC-2026-001",
  "summary": "Automated analysis identified root cause for INC-2026-001: Regression introduced in deployment v2.4.1...",
  "severity": "CRITICAL",
  "affected_service": "api-gateway",
  "root_cause_hypothesis": "Regression introduced in deployment v2.4.1 causing null pointer exceptions in ingress routing",
  "confidence": "HIGH",
  "confidence_justification": "Direct temporal correlation between deployment v2.4.1 (T-28m) and 14.8% error rate spike...",
  "supporting_evidence": [
    {
      "source_type": "DEPLOYMENT",
      "source_id": "DEPLOY-1",
      "summary": "Release v2.4.1: Upgrade connection pooling library and refactor auth route filter pipeline.",
      "relevance_score": 0.95
    },
    {
      "source_type": "METRIC",
      "source_id": "METRIC-api-gateway-error_rate",
      "summary": "Error rate spiked to 14.8%",
      "relevance_score": 0.92
    }
  ],
  "suggested_remediation": "rollback_deployment",
  "requires_approval": true,
  "investigation_mode": "LOCAL_DETERMINISTIC",
  "execution_time_ms": 32.4
}
```

---

## 5. Remediation Gating

### `POST /api/incidents/{incident_id}/remediations`
Proposes an eligible simulated remediation action.

```bash
curl -X POST http://localhost:8000/api/incidents/INC-2026-001/remediations \
  -H "Content-Type: application/json" \
  -d '{
    "proposed_action": "rollback_deployment",
    "reason_summary": "Revert release v2.4.1 due to null pointer exception in auth routing",
    "expected_impact": "Normalize error rate to baseline (< 0.5%)",
    "risk_level": "HIGH",
    "action_parameters": {"target_version": "v2.4.0"}
  }'
```

### `POST /api/remediations/{remediation_id}/approve`
Signs off on a pending remediation request.

```bash
curl -X POST http://localhost:8000/api/remediations/1/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approver_id": "lead-operator@sentinelops.local",
    "approval_notes": "Emergency rollback authorized"
  }'
```

### `POST /api/remediations/{remediation_id}/execute`
Executes an approved simulated remediation.

```bash
curl -X POST http://localhost:8000/api/remediations/1/execute \
  -H "Content-Type: application/json" \
  -d '{"operator_id": "operator@sentinelops.local"}'
```

---

## 6. Hybrid RAG Runbook Search

### `POST /api/knowledge/search`
Searches knowledge base runbooks with BM25, Semantic, or Hybrid RRF ranking.

```bash
curl -X POST http://localhost:8000/api/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "HTTP 502 bad gateway deployment rollback",
    "method": "HYBRID",
    "top_k": 3
  }'
```
