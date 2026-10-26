"""
Reproducible Synthetic IT Incident Dataset Generator
Generates realistic but explicitly synthetic enterprise microservice telemetry,
logs, metrics, deployment records, runbooks, and audit events with a fixed seed.
"""
import json
import os
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, init_db
from app.models.audit import AuditEvent
from app.models.deployment import DeploymentEvent
from app.models.incident import Incident
from app.models.knowledge import KnowledgeDocument
from app.models.log import LogEntry
from app.models.metric import MetricSample
from app.models.service import Service
from app.retrieval.hybrid_retriever import HybridRetriever


def seed_database(db: Session, seed: int = 42, base_time: datetime = None):
    """Populates the database with a reproducible synthetic IT operations dataset."""
    random.seed(seed)
    if base_time is None:
        base_time = datetime.utcnow()

    # Clear existing data in reverse dependency order
    db.query(AuditEvent).delete()
    db.query(LogEntry).delete()
    db.query(MetricSample).delete()
    db.query(DeploymentEvent).delete()
    db.query(Incident).delete()
    db.query(KnowledgeDocument).delete()
    db.query(Service).delete()
    db.commit()

    # 1. Enterprise Services
    services_data = [
        {
            "id": "api-gateway",
            "name": "API Gateway & Ingress Proxy",
            "environment": "production",
            "current_status": "DEGRADED",
            "description": "Handles client TLS termination, rate limiting, and route proxying.",
        },
        {
            "id": "order-db",
            "name": "Order Transaction Database",
            "environment": "production",
            "current_status": "DEGRADED",
            "description": "Primary transactional PostgreSQL cluster for orders and checkout state.",
        },
        {
            "id": "worker-queue",
            "name": "Background Task Processor",
            "environment": "production",
            "current_status": "DEGRADED",
            "description": "Distributed Celery / Redis asynchronous worker fleet for batch processing.",
        },
        {
            "id": "auth-service",
            "name": "Authentication & IAM Service",
            "environment": "production",
            "current_status": "OUTAGE",
            "description": "OAuth2 / JWT issuing, SSO token verification, and user identity directory.",
        },
        {
            "id": "notification-service",
            "name": "Notification Dispatcher",
            "environment": "production",
            "current_status": "HEALTHY",
            "description": "Dispatches transactional emails, SMS alerts, and mobile push notifications.",
        },
    ]

    services = []
    for s_info in services_data:
        srv = Service(**s_info, created_at=base_time - timedelta(days=90))
        db.add(srv)
        services.append(srv)
    db.commit()

    # 2. Deployment Events
    deployments_data = [
        {
            "service_id": "api-gateway",
            "deployment_timestamp": base_time - timedelta(minutes=28),
            "version": "v2.4.1",
            "change_description": "Upgrade connection pooling library and refactor auth route filter pipeline.",
            "deployment_status": "SUCCESS",
        },
        {
            "service_id": "api-gateway",
            "deployment_timestamp": base_time - timedelta(days=5),
            "version": "v2.4.0",
            "change_description": "Stable release: ingress rate limiting and payload validation updates.",
            "deployment_status": "SUCCESS",
        },
        {
            "service_id": "order-db",
            "deployment_timestamp": base_time - timedelta(hours=3),
            "version": "v1.12.0",
            "change_description": "Migration 0042_add_order_indexing applied to production replicas.",
            "deployment_status": "SUCCESS",
        },
        {
            "service_id": "worker-queue",
            "deployment_timestamp": base_time - timedelta(days=2),
            "version": "v3.1.0",
            "change_description": "Updated Redis connection client and increased prefetch count to 64.",
            "deployment_status": "SUCCESS",
        },
        {
            "service_id": "auth-service",
            "deployment_timestamp": base_time - timedelta(days=14),
            "version": "v1.8.2",
            "change_description": "Minor patch: updated token encryption cypher suite.",
            "deployment_status": "SUCCESS",
        },
    ]

    for d in deployments_data:
        dep = DeploymentEvent(**d)
        db.add(dep)
    db.commit()

    # 3. Incidents
    incidents_data = [
        {
            "id": "INC-2026-001",
            "title": "Elevated HTTP 502/500 Errors on API Gateway Post-Deployment",
            "description": "API Gateway error rate spiked to 14.8% following deployment v2.4.1. Clients experiencing intermittent 502 Bad Gateway responses.",
            "severity": "CRITICAL",
            "status": "TRIGGERED",
            "affected_service_id": "api-gateway",
            "detection_timestamp": base_time - timedelta(minutes=20),
            "source": "ANOMALY_DETECTOR",
            "trigger_rule": "ERROR_RATE_THRESHOLD_EXCEEDED",
            "created_at": base_time - timedelta(minutes=20),
        },
        {
            "id": "INC-2026-002",
            "title": "Order Database Connection Pool Saturation and Latency Spike",
            "description": "Order DB connection pool limit reached. p95 latency degraded from 45ms to 4200ms. Cascading timeouts across checkout API.",
            "severity": "HIGH",
            "status": "ACKNOWLEDGED",
            "affected_service_id": "order-db",
            "detection_timestamp": base_time - timedelta(minutes=45),
            "source": "METRIC_MONITOR",
            "trigger_rule": "LATENCY_P95_THRESHOLD_EXCEEDED",
            "created_at": base_time - timedelta(minutes=45),
        },
        {
            "id": "INC-2026-003",
            "title": "Background Job Queue Starvation and Backlog Accumulation",
            "description": "Queue depth on worker-queue exceeded 14,000 pending tasks. Worker CPU and memory saturation causing slow task drain.",
            "severity": "HIGH",
            "status": "INVESTIGATING",
            "affected_service_id": "worker-queue",
            "detection_timestamp": base_time - timedelta(minutes=75),
            "source": "ANOMALY_DETECTOR",
            "trigger_rule": "QUEUE_DEPTH_THRESHOLD_EXCEEDED",
            "created_at": base_time - timedelta(minutes=75),
        },
        {
            "id": "INC-2026-004",
            "title": "Authentication Token Signing Certificate Expired",
            "description": "Auth service rejecting 68% of token verification requests. JWT signature validation failures observed across all microservices.",
            "severity": "CRITICAL",
            "status": "TRIGGERED",
            "affected_service_id": "auth-service",
            "detection_timestamp": base_time - timedelta(minutes=15),
            "source": "SYSLOG_ALERT",
            "trigger_rule": "AUTH_FAILURE_RATE_EXCEEDED",
            "created_at": base_time - timedelta(minutes=15),
        },
    ]

    for inc in incidents_data:
        incident_obj = Incident(**inc)
        db.add(incident_obj)
    db.commit()

    # 4. Metric Samples (Simulated time series over last 2 hours in 5-minute buckets)
    for m in range(24):
        t = base_time - timedelta(minutes=(23 - m) * 5)
        # Healthy service: notification-service
        db.add(MetricSample(service_id="notification-service", timestamp=t, metric_name="error_rate", value=round(random.uniform(0.01, 0.08), 3), unit="percent"))
        db.add(MetricSample(service_id="notification-service", timestamp=t, metric_name="latency_p95", value=round(random.uniform(65, 88), 1), unit="ms"))
        db.add(MetricSample(service_id="notification-service", timestamp=t, metric_name="cpu_percent", value=round(random.uniform(22, 35), 1), unit="percent"))

        # Scenario 1: api-gateway (normal before T-25m, then spikes)
        if m < 19:
            err = random.uniform(0.1, 0.4)
            lat = random.uniform(110, 140)
            cpu = random.uniform(30, 45)
        else:
            err = random.uniform(13.5, 16.2)
            lat = random.uniform(850, 1250)
            cpu = random.uniform(65, 82)
        db.add(MetricSample(service_id="api-gateway", timestamp=t, metric_name="error_rate", value=round(err, 2), unit="percent"))
        db.add(MetricSample(service_id="api-gateway", timestamp=t, metric_name="latency_p95", value=round(lat, 1), unit="ms"))
        db.add(MetricSample(service_id="api-gateway", timestamp=t, metric_name="cpu_percent", value=round(cpu, 1), unit="percent"))

        # Scenario 2: order-db (normal until T-45m)
        if m < 15:
            lat_db = random.uniform(35, 55)
            pool_conn = random.uniform(10, 16)
        else:
            lat_db = random.uniform(3800, 4400)
            pool_conn = random.uniform(28, 30)  # Max capacity
        db.add(MetricSample(service_id="order-db", timestamp=t, metric_name="latency_p95", value=round(lat_db, 1), unit="ms"))
        db.add(MetricSample(service_id="order-db", timestamp=t, metric_name="active_connections", value=round(pool_conn, 0), unit="count"))
        db.add(MetricSample(service_id="order-db", timestamp=t, metric_name="error_rate", value=round(0.2 if m < 15 else 4.8, 2), unit="percent"))

        # Scenario 3: worker-queue (queue accumulates over time)
        depth = 120 + (m * 620) if m > 6 else 110
        cpu_w = 40 + (m * 2.2) if m > 6 else 38
        db.add(MetricSample(service_id="worker-queue", timestamp=t, metric_name="queue_depth", value=float(depth), unit="count"))
        db.add(MetricSample(service_id="worker-queue", timestamp=t, metric_name="cpu_percent", value=round(min(cpu_w, 94.0), 1), unit="percent"))

        # Scenario 4: auth-service (failure rate spikes at T-15m)
        auth_err = random.uniform(0.05, 0.2) if m < 20 else random.uniform(62.0, 71.0)
        db.add(MetricSample(service_id="auth-service", timestamp=t, metric_name="auth_failure_rate", value=round(auth_err, 2), unit="percent"))
        db.add(MetricSample(service_id="auth-service", timestamp=t, metric_name="latency_p95", value=round(random.uniform(90, 130), 1), unit="ms"))

    db.commit()

    # 5. Application and Error Logs
    logs_data = [
        # api-gateway normal & incident logs
        {
            "service_id": "api-gateway",
            "timestamp": base_time - timedelta(minutes=27),
            "log_level": "INFO",
            "message": "Deployment v2.4.1 initialized. Ingress route handlers reloaded.",
            "metadata_json": json.dumps({"version": "v2.4.1", "action": "deploy"}),
            "incident_id": None,
        },
        {
            "service_id": "api-gateway",
            "timestamp": base_time - timedelta(minutes=24),
            "log_level": "ERROR",
            "message": "NullPointerException: AuthMiddlewareHandler.forwardRequest failed to resolve route context for path /api/v1/orders",
            "metadata_json": json.dumps({"status_code": 500, "route": "/api/v1/orders", "trace_id": "tr-7f9a12"}),
            "incident_id": "INC-2026-001",
        },
        {
            "service_id": "api-gateway",
            "timestamp": base_time - timedelta(minutes=22),
            "log_level": "ERROR",
            "message": "HTTP 502 Bad Gateway: Upstream response header parse error from handler proxy",
            "metadata_json": json.dumps({"status_code": 502, "service": "api-gateway", "trace_id": "tr-8b3c41"}),
            "incident_id": "INC-2026-001",
        },
        {
            "service_id": "api-gateway",
            "timestamp": base_time - timedelta(minutes=18),
            "log_level": "WARN",
            "message": "Error budget alert: HTTP 5xx error rate exceeded 10% threshold in rolling 5m window",
            "metadata_json": json.dumps({"current_error_rate": "14.8%"}),
            "incident_id": "INC-2026-001",
        },

        # order-db pool saturation logs
        {
            "service_id": "order-db",
            "timestamp": base_time - timedelta(minutes=44),
            "log_level": "WARN",
            "message": "ConnectionPoolWarning: Connection pool approaching capacity (26/30 slots in use)",
            "metadata_json": json.dumps({"pool_size": 20, "max_overflow": 10}),
            "incident_id": "INC-2026-002",
        },
        {
            "service_id": "order-db",
            "timestamp": base_time - timedelta(minutes=41),
            "log_level": "ERROR",
            "message": "TimeoutError: QueuePool limit of size 20 overflow 10 reached, connection checkout timed out after 30.00s",
            "metadata_json": json.dumps({"active_queries": 30, "error_code": "POOL_EXHAUSTED"}),
            "incident_id": "INC-2026-002",
        },
        {
            "service_id": "order-db",
            "timestamp": base_time - timedelta(minutes=39),
            "log_level": "ERROR",
            "message": "Transaction rollback: Deadlock detected waiting for lock on relation order_items",
            "metadata_json": json.dumps({"pid": 14208, "blocked_by": 14199}),
            "incident_id": "INC-2026-002",
        },

        # worker-queue starvation logs
        {
            "service_id": "worker-queue",
            "timestamp": base_time - timedelta(minutes=72),
            "log_level": "WARN",
            "message": "QueueBacklogNotice: Redis queue tasks:default exceeded 5,000 pending messages",
            "metadata_json": json.dumps({"queue": "tasks:default", "depth": 5420}),
            "incident_id": "INC-2026-003",
        },
        {
            "service_id": "worker-queue",
            "timestamp": base_time - timedelta(minutes=68),
            "log_level": "ERROR",
            "message": "WorkerProcessStarvation: Pending queue depth exceeds threshold (14,250 tasks), worker heartbeat timed out",
            "metadata_json": json.dumps({"worker_id": "celery@node-04", "memory_rss_mb": 1850}),
            "incident_id": "INC-2026-003",
        },

        # auth-service certificate logs
        {
            "service_id": "auth-service",
            "timestamp": base_time - timedelta(minutes=14),
            "log_level": "ERROR",
            "message": "JWTExpiredError: Token signing certificate expired at 2026-10-26T20:00:00Z. Verification failed.",
            "metadata_json": json.dumps({"status_code": 401, "key_id": "auth-rsa-2025-01"}),
            "incident_id": "INC-2026-004",
        },
        {
            "service_id": "auth-service",
            "timestamp": base_time - timedelta(minutes=12),
            "log_level": "ERROR",
            "message": "UnauthorizedRequestFlood: 401 response volume spiked to 3,400 req/min across ingress endpoints",
            "metadata_json": json.dumps({"status_code": 401, "failure_rate": "68%"}),
            "incident_id": "INC-2026-004",
        },

        # notification-service healthy logs
        {
            "service_id": "notification-service",
            "timestamp": base_time - timedelta(minutes=10),
            "log_level": "INFO",
            "message": "Batch notification batch_id=9812 delivered successfully to 4,200 recipients.",
            "metadata_json": json.dumps({"delivered": 4200, "duration_ms": 312}),
            "incident_id": None,
        },
    ]

    for log_item in logs_data:
        log_obj = LogEntry(**log_item)
        db.add(log_obj)
    db.commit()

    # 6. Load Knowledge Documents from runbooks directory
    cur = os.path.abspath(__file__)
    for _ in range(4):
        cur = os.path.dirname(cur)
    knowledge_dir = os.path.join(cur, "knowledge", "runbooks")
    if os.path.exists(knowledge_dir):
        retriever = HybridRetriever()
        docs = retriever.load_from_directory(knowledge_dir)
        for doc in docs:
            k_doc = KnowledgeDocument(
                id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                source=doc["source"],
                version="1.0",
                created_at=base_time - timedelta(days=60),
            )
            db.add(k_doc)
        db.commit()

    # 7. Initial Audit Events
    audit_data = [
        {
            "event_type": "INCIDENT_DETECTED",
            "actor": "system:anomaly_detector",
            "resource_type": "incident",
            "resource_id": "INC-2026-001",
            "action_summary": "Detected critical error spike on api-gateway (14.8% HTTP 5xx rate)",
            "timestamp": base_time - timedelta(minutes=20),
            "metadata_json": json.dumps({"rule": "ERROR_RATE_THRESHOLD_EXCEEDED", "service": "api-gateway"}),
        },
        {
            "event_type": "INCIDENT_DETECTED",
            "actor": "system:anomaly_detector",
            "resource_type": "incident",
            "resource_id": "INC-2026-002",
            "action_summary": "Detected high latency violation on order-db (p95 latency 4200ms)",
            "timestamp": base_time - timedelta(minutes=45),
            "metadata_json": json.dumps({"rule": "LATENCY_P95_THRESHOLD_EXCEEDED", "service": "order-db"}),
        },
        {
            "event_type": "INCIDENT_ACKNOWLEDGED",
            "actor": "operator@sentinelops.local",
            "resource_type": "incident",
            "resource_id": "INC-2026-002",
            "action_summary": "Incident acknowledged by on-call engineer",
            "timestamp": base_time - timedelta(minutes=35),
            "metadata_json": json.dumps({"assigned_to": "operator@sentinelops.local"}),
        },
    ]

    for a in audit_data:
        audit_obj = AuditEvent(**a)
        db.add(audit_obj)
    db.commit()

    return {
        "services_seeded": len(services_data),
        "deployments_seeded": len(deployments_data),
        "incidents_seeded": len(incidents_data),
        "logs_seeded": len(logs_data),
        "seed": seed,
    }

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        res = seed_database(db)
        print("Database seeded successfully:", res)
    finally:
        db.close()
