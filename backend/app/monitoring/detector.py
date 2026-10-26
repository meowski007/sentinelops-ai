"""
Incident Monitoring and Anomaly Detector
Scans telemetry, detects threshold violations, groups signals, and triggers explainable incidents.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.metric import MetricSample
from app.models.service import Service
from app.monitoring.rules import DEFAULT_DETECTION_RULES, DetectionRule, calculate_time_window_stats


class AnomalyDetector:
    def __init__(self, rules: List[DetectionRule] = None):
        self.rules = rules or DEFAULT_DETECTION_RULES

    def scan_service_telemetry(
        self,
        db: Session,
        service_id: str,
        lookback_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Scans recent metrics for a given service and identifies any active rule violations.
        """
        now = datetime.utcnow()
        since = now - timedelta(minutes=lookback_minutes)

        samples = (
            db.query(MetricSample)
            .filter(MetricSample.service_id == service_id, MetricSample.timestamp >= since)
            .order_by(MetricSample.timestamp.desc())
            .all()
        )

        # Group values by metric name
        grouped: Dict[str, List[float]] = {}
        for s in samples:
            grouped.setdefault(s.metric_name, []).append(s.value)

        violations = []
        for rule in self.rules:
            if rule.metric_name in grouped:
                values = grouped[rule.metric_name]
                latest_value = values[0]  # Most recent value
                stats = calculate_time_window_stats(values)

                if rule.evaluate(latest_value):
                    violations.append({
                        "service_id": service_id,
                        "rule_id": rule.rule_id,
                        "metric_name": rule.metric_name,
                        "latest_value": latest_value,
                        "threshold": rule.threshold,
                        "severity": rule.severity,
                        "description": rule.description,
                        "stats": stats,
                        "detected_at": now.isoformat(),
                    })

        return violations

    def run_detection_cycle(self, db: Session) -> List[Dict[str, Any]]:
        """
        Evaluates all active services across the enterprise environment.
        If an open incident already exists for a service violation, links to it;
        otherwise flags the detection.
        """
        services = db.query(Service).all()
        all_violations = []

        for srv in services:
            service_violations = self.scan_service_telemetry(db, srv.id)
            for v in service_violations:
                # Check if an unresolved incident is already tracking this service & trigger rule
                existing = (
                    db.query(Incident)
                    .filter(
                        Incident.affected_service_id == srv.id,
                        Incident.status.in_(["TRIGGERED", "ACKNOWLEDGED", "INVESTIGATING"]),
                    )
                    .first()
                )

                v["associated_incident_id"] = existing.id if existing else None
                all_violations.append(v)

        return all_violations
