"""
Approval-Controlled Remediation Service
Enforces strict human-in-the-loop authorization gates, risk validation,
duplicate prevention, state transitions, and simulated action execution.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.security import check_actor_permission, requires_approval, validate_action_name
from app.models.audit import AuditEvent
from app.models.deployment import DeploymentEvent
from app.models.incident import Incident
from app.models.log import LogEntry
from app.models.remediation import RemediationRequest
from app.models.service import Service


class RemediationService:
    def __init__(self, db: Session):
        self.db = db

    def propose_remediation(
        self,
        incident_id: str,
        proposed_action: str,
        reason_summary: str,
        expected_impact: str,
        risk_level: str = "MEDIUM",
        action_parameters: Optional[Dict[str, Any]] = None,
        proposer_actor: str = "sentinelops-agent",
    ) -> RemediationRequest:
        """
        Submits a remediation proposal.
        Validates action against allowlist and initializes approval gates.
        """
        if not validate_action_name(proposed_action):
            raise ValueError(f"Action '{proposed_action}' is not in the approved remediation allowlist.")

        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident '{incident_id}' not found.")

        needs_approval = requires_approval(proposed_action, risk_level)
        initial_approval_status = "PENDING_APPROVAL" if needs_approval else "NOT_REQUIRED"

        req = RemediationRequest(
            incident_id=incident_id,
            proposed_action=proposed_action,
            action_parameters_json=json.dumps(action_parameters or {}),
            reason_summary=reason_summary,
            expected_impact=expected_impact,
            risk_level=risk_level.upper(),
            approval_status=initial_approval_status,
            execution_status="PENDING",
            created_at=datetime.utcnow(),
        )
        self.db.add(req)

        # Audit event for proposal
        audit = AuditEvent(
            event_type="REMEDIATION_PROPOSED",
            actor=proposer_actor,
            resource_type="remediation",
            resource_id=f"REM-pending-{incident_id}",
            action_summary=f"Proposed action '{proposed_action}' (Risk: {risk_level}) for {incident_id}",
            timestamp=datetime.utcnow(),
            metadata_json=json.dumps({
                "action": proposed_action,
                "needs_approval": needs_approval,
                "params": action_parameters,
            }),
        )
        self.db.add(audit)

        self.db.commit()
        self.db.refresh(req)
        return req

    def approve_remediation(
        self,
        remediation_id: int,
        approver_id: str,
        notes: Optional[str] = None
    ) -> RemediationRequest:
        """
        Records human approval for a pending remediation proposal.
        """
        if not check_actor_permission(approver_id):
            raise PermissionError("Invalid or unauthorized approver identifier.")

        req = self.db.query(RemediationRequest).filter(RemediationRequest.id == remediation_id).first()
        if not req:
            raise ValueError(f"Remediation request #{remediation_id} not found.")

        if req.approval_status == "APPROVED":
            raise ValueError(f"Remediation request #{remediation_id} is already approved.")
        if req.approval_status == "REJECTED":
            raise ValueError(f"Cannot approve already rejected remediation request #{remediation_id}.")
        if req.execution_status == "EXECUTED":
            raise ValueError(f"Remediation request #{remediation_id} has already been executed.")

        req.approval_status = "APPROVED"
        req.approver_id = approver_id

        # Record audit event
        audit = AuditEvent(
            event_type="REMEDIATION_APPROVED",
            actor=approver_id,
            resource_type="remediation",
            resource_id=str(remediation_id),
            action_summary=f"Approved remediation #{remediation_id} ({req.proposed_action}) for {req.incident_id}",
            timestamp=datetime.utcnow(),
            metadata_json=json.dumps({"notes": notes, "approver": approver_id}),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(req)
        return req

    def reject_remediation(
        self,
        remediation_id: int,
        approver_id: str,
        rejection_reason: str
    ) -> RemediationRequest:
        """
        Rejects a proposed remediation, cancelling execution.
        """
        if not check_actor_permission(approver_id):
            raise PermissionError("Invalid or unauthorized approver identifier.")

        req = self.db.query(RemediationRequest).filter(RemediationRequest.id == remediation_id).first()
        if not req:
            raise ValueError(f"Remediation request #{remediation_id} not found.")

        if req.execution_status == "EXECUTED":
            raise ValueError("Cannot reject an action that has already been executed.")

        req.approval_status = "REJECTED"
        req.execution_status = "CANCELLED"
        req.approver_id = approver_id
        req.execution_result = f"Rejected by {approver_id}: {rejection_reason}"

        audit = AuditEvent(
            event_type="REMEDIATION_REJECTED",
            actor=approver_id,
            resource_type="remediation",
            resource_id=str(remediation_id),
            action_summary=f"Rejected remediation #{remediation_id} ({req.proposed_action}): {rejection_reason}",
            timestamp=datetime.utcnow(),
            metadata_json=json.dumps({"reason": rejection_reason}),
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(req)
        return req

    def execute_remediation(
        self,
        remediation_id: int,
        operator_id: str
    ) -> RemediationRequest:
        """
        Executes an approved remediation action within the local simulation sandbox.
        Validates authorization gates, updates service health, appends verification logs,
        and transitions the incident state to MITIGATED or RESOLVED.
        """
        req = self.db.query(RemediationRequest).filter(RemediationRequest.id == remediation_id).first()
        if not req:
            raise ValueError(f"Remediation request #{remediation_id} not found.")

        # Backend authorization check: must be approved
        if req.approval_status not in ["APPROVED", "NOT_REQUIRED"]:
            raise PermissionError(
                f"Action '{req.proposed_action}' cannot be executed: approval status is '{req.approval_status}'."
            )

        if req.execution_status == "EXECUTED":
            raise ValueError(f"Remediation #{remediation_id} has already been executed (replay prevented).")

        incident = self.db.query(Incident).filter(Incident.id == req.incident_id).first()
        if not incident:
            raise ValueError(f"Incident '{req.incident_id}' not found.")

        service = self.db.query(Service).filter(Service.id == incident.affected_service_id).first()

        params = json.loads(req.action_parameters_json or "{}")
        action = req.proposed_action
        now = datetime.utcnow()

        # Simulated action execution handler
        if action == "rollback_deployment":
            target_version = params.get("target_version", "v2.4.0")
            req.execution_result = f"Simulated rollback to {target_version} completed successfully. Route caching reinitialized. Error rate normalized."
            if service:
                service.current_status = "HEALTHY"
            # Add rollback deployment event
            self.db.add(DeploymentEvent(
                service_id=incident.affected_service_id,
                deployment_timestamp=now,
                version=target_version,
                change_description=f"Automated rollback triggered by Remediation #{remediation_id}",
                deployment_status="ROLLED_BACK",
            ))

        elif action == "drain_connection_pool":
            req.execution_result = "Simulated connection pool drained. Stale idle sessions closed and active pool capacity restored to 0/20."
            if service:
                service.current_status = "HEALTHY"

        elif action == "restart_service":
            req.execution_result = f"Simulated graceful restart of '{incident.affected_service_id}' completed. Health probe 200 OK."
            if service:
                service.current_status = "HEALTHY"

        elif action == "scale_worker_pool":
            target_workers = params.get("target_workers", 12)
            req.execution_result = f"Worker pool concurrency scaled to {target_workers} workers. Backlog queue drain accelerated."
            if service:
                service.current_status = "HEALTHY"

        elif action == "refresh_service_credentials":
            key_id = params.get("key_id", "auth-rsa-2026")
            req.execution_result = f"Signing certificate rotated to key '{key_id}'. Public key cache purged. Token verification restored."
            if service:
                service.current_status = "HEALTHY"

        else:
            req.execution_result = f"Executed custom simulated action '{action}' successfully."
            if service:
                service.current_status = "HEALTHY"

        req.execution_status = "EXECUTED"
        req.executed_at = now

        # Update Incident state
        incident.status = "RESOLVED"
        incident.resolution_timestamp = now

        # Append resolution log
        self.db.add(LogEntry(
            service_id=incident.affected_service_id,
            timestamp=now,
            log_level="INFO",
            message=f"Remediation #{remediation_id} ({action}) executed by {operator_id}. Service recovered: {req.execution_result}",
            metadata_json=json.dumps({"remediation_id": remediation_id, "action": action}),
            incident_id=incident.id,
        ))

        # Record audit event
        audit = AuditEvent(
            event_type="REMEDIATION_EXECUTED",
            actor=operator_id,
            resource_type="remediation",
            resource_id=str(remediation_id),
            action_summary=f"Executed remediation #{remediation_id} ({action}) on {incident.affected_service_id}. Incident {incident.id} marked RESOLVED.",
            timestamp=now,
            metadata_json=json.dumps({"result": req.execution_result, "operator": operator_id}),
        )
        self.db.add(audit)

        self.db.commit()
        self.db.refresh(req)
        return req
