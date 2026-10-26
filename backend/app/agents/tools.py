"""
Allowlisted Investigation Tools
Each tool performs validated, read-only data access against the local enterprise database and runbook index.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.security import sanitize_untrusted_text
from app.models.deployment import DeploymentEvent
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.metric import MetricSample
from app.monitoring.rules import calculate_time_window_stats
from app.retrieval.hybrid_retriever import HybridRetriever


class InvestigationTools:
    def __init__(self, db: Session, retriever: Optional[HybridRetriever] = None):
        self.db = db
        self.retriever = retriever

    def get_incident_details(self, incident_id: str) -> Dict[str, Any]:
        """Tool 1: Retrieves core incident metadata, severity, trigger rule, and affected service."""
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return {"error": f"Incident '{incident_id}' not found."}
        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "affected_service_id": incident.affected_service_id,
            "detection_timestamp": incident.detection_timestamp.isoformat(),
            "trigger_rule": incident.trigger_rule,
            "source": incident.source,
        }

    def get_service_metrics(
        self,
        service_id: str,
        window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Tool 2: Aggregates time-window metrics, statistical percentiles (p50, p95), and latest values."""
        now = datetime.utcnow()
        since = now - timedelta(minutes=window_minutes)

        samples = (
            self.db.query(MetricSample)
            .filter(MetricSample.service_id == service_id, MetricSample.timestamp >= since)
            .order_by(MetricSample.timestamp.asc())
            .all()
        )

        metrics_by_name: Dict[str, List[float]] = {}
        for s in samples:
            metrics_by_name.setdefault(s.metric_name, []).append(s.value)

        summaries = {}
        for name, vals in metrics_by_name.items():
            stats = calculate_time_window_stats(vals)
            summaries[name] = {
                "latest": vals[-1] if vals else 0.0,
                "p50": stats["p50"],
                "p95": stats["p95"],
                "min": stats["min"],
                "max": stats["max"],
                "sample_count": len(vals),
            }

        return {
            "service_id": service_id,
            "window_minutes": window_minutes,
            "metrics": summaries,
        }

    def search_logs(
        self,
        service_id: Optional[str] = None,
        level: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Tool 3: Queries simulated application logs with sanitization and filtering."""
        limit = min(max(1, limit), 100)
        q = self.db.query(LogEntry)

        if service_id:
            q = q.filter(LogEntry.service_id == service_id)
        if level:
            q = q.filter(LogEntry.log_level == level.upper())
        if query:
            clean_query = sanitize_untrusted_text(query)
            q = q.filter(LogEntry.message.ilike(f"%{clean_query}%"))

        logs = q.order_by(LogEntry.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": f"LOG-{log_item.id}",
                "timestamp": log_item.timestamp.isoformat(),
                "service_id": log_item.service_id,
                "level": log_item.log_level,
                "message": log_item.message,
                "metadata": log_item.metadata_json,
                "incident_id": log_item.incident_id,
            }
            for log_item in logs
        ]

    def get_recent_deployments(
        self,
        service_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Tool 4: Inspects recent deployments for the service to identify correlation with incidents."""
        limit = min(max(1, limit), 20)
        deployments = (
            self.db.query(DeploymentEvent)
            .filter(DeploymentEvent.service_id == service_id)
            .order_by(DeploymentEvent.deployment_timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": f"DEPLOY-{d.id}",
                "version": d.version,
                "timestamp": d.deployment_timestamp.isoformat(),
                "status": d.deployment_status,
                "description": d.change_description,
            }
            for d in deployments
        ]

    def search_runbooks(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Tool 5: Hybrid RAG retrieval over validated IT troubleshooting runbooks."""
        if not self.retriever:
            return []
        clean_query = sanitize_untrusted_text(query)
        results = self.retriever.search(clean_query, top_k=top_k, method="HYBRID")
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "category": r["category"],
                "snippet": r["snippet"],
                "relevance_score": r["relevance_score"],
            }
            for r in results
        ]

    def calculate_error_rate(
        self,
        service_id: str,
        window_minutes: int = 15
    ) -> Dict[str, Any]:
        """Tool 6: Computes the current and baseline error rates from metric samples."""
        now = datetime.utcnow()
        recent_since = now - timedelta(minutes=window_minutes)
        baseline_since = now - timedelta(hours=2)

        recent_samples = (
            self.db.query(MetricSample)
            .filter(
                MetricSample.service_id == service_id,
                MetricSample.metric_name.in_(["error_rate", "auth_failure_rate"]),
                MetricSample.timestamp >= recent_since,
            )
            .all()
        )
        baseline_samples = (
            self.db.query(MetricSample)
            .filter(
                MetricSample.service_id == service_id,
                MetricSample.metric_name.in_(["error_rate", "auth_failure_rate"]),
                MetricSample.timestamp >= baseline_since,
            )
            .all()
        )

        recent_rate = recent_samples[-1].value if recent_samples else 0.0
        baseline_rate = (
            round(sum(s.value for s in baseline_samples) / len(baseline_samples), 2)
            if baseline_samples else 0.0
        )

        return {
            "service_id": service_id,
            "current_error_rate": recent_rate,
            "baseline_error_rate": baseline_rate,
            "delta": round(recent_rate - baseline_rate, 2),
            "is_elevated": recent_rate > 5.0,
        }

    def get_related_incidents(self, service_id: str) -> List[Dict[str, Any]]:
        """Tool 7: Discovers related past or parallel incidents on the same service."""
        incidents = (
            self.db.query(Incident)
            .filter(Incident.affected_service_id == service_id)
            .order_by(Incident.detection_timestamp.desc())
            .limit(5)
            .all()
        )
        return [
            {
                "id": inc.id,
                "title": inc.title,
                "severity": inc.severity,
                "status": inc.status,
                "detection_timestamp": inc.detection_timestamp.isoformat(),
            }
            for inc in incidents
        ]
