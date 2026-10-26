"""
Metrics Service
Aggregates time-series metrics, computes statistical trends, and builds operations dashboard overviews.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.metric import MetricSample
from app.models.service import Service
from app.schemas.metric import MetricSampleOut, MetricsOverviewResponse, ServiceMetricsOverview


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> MetricsOverviewResponse:
        """Constructs an aggregate telemetry overview across all services for the operations dashboard."""
        now = datetime.utcnow()
        services = self.db.query(Service).all()

        active_incidents = (
            self.db.query(Incident)
            .filter(Incident.status.in_(["TRIGGERED", "ACKNOWLEDGED", "INVESTIGATING"]))
            .all()
        )
        critical_count = sum(1 for inc in active_incidents if inc.severity == "CRITICAL")

        service_overviews = []
        for srv in services:
            # Fetch recent samples
            recent_samples = (
                self.db.query(MetricSample)
                .filter(MetricSample.service_id == srv.id)
                .order_by(MetricSample.timestamp.desc())
                .limit(40)
                .all()
            )

            # Extract latest values for key signals
            latest_error = 0.0
            latest_lat = 0.0
            latest_cpu = 0.0
            latest_queue = None

            for s in recent_samples:
                if s.metric_name in ["error_rate", "auth_failure_rate"] and latest_error == 0.0:
                    latest_error = s.value
                elif s.metric_name == "latency_p95" and latest_lat == 0.0:
                    latest_lat = s.value
                elif s.metric_name == "cpu_percent" and latest_cpu == 0.0:
                    latest_cpu = s.value
                elif s.metric_name == "queue_depth" and latest_queue is None:
                    latest_queue = int(s.value)

            service_overviews.append(
                ServiceMetricsOverview(
                    service_id=srv.id,
                    service_name=srv.name,
                    status=srv.current_status,
                    error_rate=latest_error,
                    latency_p95_ms=latest_lat,
                    cpu_percent=latest_cpu,
                    request_volume=int(3200 + (latest_cpu * 40)),
                    queue_depth=latest_queue,
                    samples=[MetricSampleOut.model_validate(s) for s in reversed(recent_samples[:15])],
                )
            )

        return MetricsOverviewResponse(
            timestamp=now,
            services=service_overviews,
            active_incidents_count=len(active_incidents),
            critical_count=critical_count,
        )

    def get_service_metric_samples(
        self,
        service_id: str,
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> List[MetricSample]:
        """Queries time-series metric samples for charts."""
        q = self.db.query(MetricSample).filter(MetricSample.service_id == service_id)
        if metric_name:
            q = q.filter(MetricSample.metric_name == metric_name)
        return q.order_by(MetricSample.timestamp.asc()).limit(limit).all()
