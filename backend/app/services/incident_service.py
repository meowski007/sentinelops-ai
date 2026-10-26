"""
Incident Management Service
Handles querying, filtering, lifecycle state transitions, and timeline reconstruction.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent
from app.models.deployment import DeploymentEvent
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.log import LogEntry
from app.models.remediation import RemediationRequest
from app.schemas.incident import TimelineItem


class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def get_incidents(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        service_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Incident]:
        """Queries incidents with optional filtering by severity, status, service, and text search."""
        q = self.db.query(Incident)

        if severity:
            q = q.filter(Incident.severity == severity.upper())
        if status:
            q = q.filter(Incident.status == status.upper())
        if service_id:
            q = q.filter(Incident.affected_service_id == service_id)
        if search:
            q = q.filter(
                (Incident.title.ilike(f"%{search}%")) |
                (Incident.description.ilike(f"%{search}%")) |
                (Incident.id.ilike(f"%{search}%"))
            )

        return q.order_by(Incident.detection_timestamp.desc()).offset(offset).limit(limit).all()

    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def update_incident_status(
        self,
        incident_id: str,
        new_status: str,
        actor: str = "operator@sentinelops.local"
    ) -> Incident:
        """Updates incident status with state validation and audit event."""
        valid_statuses = ["TRIGGERED", "ACKNOWLEDGED", "INVESTIGATING", "MITIGATED", "RESOLVED"]
        if new_status.upper() not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of: {valid_statuses}")

        incident = self.get_incident_by_id(incident_id)
        if not incident:
            raise ValueError(f"Incident '{incident_id}' not found.")

        old_status = incident.status
        incident.status = new_status.upper()

        if new_status.upper() == "RESOLVED" and not incident.resolution_timestamp:
            incident.resolution_timestamp = datetime.utcnow()

        # Record audit event
        audit = AuditEvent(
            event_type=f"INCIDENT_STATUS_{new_status.upper()}",
            actor=actor,
            resource_type="incident",
            resource_id=incident_id,
            action_summary=f"Changed incident status from {old_status} to {new_status.upper()}",
            timestamp=datetime.utcnow(),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def build_incident_timeline(self, incident_id: str) -> List[TimelineItem]:
        """
        Reconstructs a chronological timeline of events surrounding the incident:
        deployments, detection, critical error logs, investigations, and remediation actions.
        """
        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return []

        timeline: List[TimelineItem] = []

        # 1. Incident Detection Event
        timeline.append(TimelineItem(
            timestamp=incident.detection_timestamp,
            type="DETECTION",
            title=f"Incident Detected: {incident.title}",
            description=f"Rule '{incident.trigger_rule or incident.source}' triggered alert.",
            severity=incident.severity,
            source_id=incident.id,
        ))

        # 2. Correlated Deployments within 2 hours
        deployments = (
            self.db.query(DeploymentEvent)
            .filter(DeploymentEvent.service_id == incident.affected_service_id)
            .order_by(DeploymentEvent.deployment_timestamp.desc())
            .limit(3)
            .all()
        )
        for dep in deployments:
            timeline.append(TimelineItem(
                timestamp=dep.deployment_timestamp,
                type="DEPLOYMENT",
                title=f"Deployment {dep.version} ({dep.deployment_status})",
                description=dep.change_description,
                severity=None,
                source_id=f"DEPLOY-{dep.id}",
            ))

        # 3. Related Application Error Logs
        logs = (
            self.db.query(LogEntry)
            .filter(
                (LogEntry.incident_id == incident_id) |
                ((LogEntry.service_id == incident.affected_service_id) & (LogEntry.log_level.in_(["ERROR", "FATAL"])))
            )
            .order_by(LogEntry.timestamp.desc())
            .limit(5)
            .all()
        )
        for log in logs:
            timeline.append(TimelineItem(
                timestamp=log.timestamp,
                type="LOG_ANOMALY",
                title=f"Log: {log.log_level}",
                description=log.message[:140],
                severity=log.log_level,
                source_id=f"LOG-{log.id}",
            ))

        # 4. Investigations
        investigations = (
            self.db.query(Investigation)
            .filter(Investigation.incident_id == incident_id)
            .order_by(Investigation.created_at.asc())
            .all()
        )
        for inv in investigations:
            timeline.append(TimelineItem(
                timestamp=inv.created_at,
                type="INVESTIGATION",
                title="AI Investigation Completed",
                description=f"Root Cause: {inv.root_cause_hypothesis} (Confidence: {inv.confidence})",
                severity=None,
                source_id=str(inv.id),
            ))

        # 5. Remediation Actions
        remediations = (
            self.db.query(RemediationRequest)
            .filter(RemediationRequest.incident_id == incident_id)
            .order_by(RemediationRequest.created_at.asc())
            .all()
        )
        for rem in remediations:
            timeline.append(TimelineItem(
                timestamp=rem.created_at,
                type="REMEDIATION",
                title=f"Remediation Proposed: {rem.proposed_action}",
                description=f"Status: {rem.approval_status} -> {rem.execution_status}",
                severity=rem.risk_level,
                source_id=str(rem.id),
            ))

        # Sort chronological
        timeline.sort(key=lambda x: x.timestamp)
        return timeline
