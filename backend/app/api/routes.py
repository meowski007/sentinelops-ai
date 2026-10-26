"""
SentinelOps AI REST API Routes
Implements OpenAPI-documented, validated endpoints for IT operations, telemetry, RAG, and remediation.
"""
import json
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.agents.investigator import IncidentInvestigator
from app.agents.tools import InvestigationTools
from app.core.security import sanitize_untrusted_text
from app.db.session import get_db
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.knowledge import KnowledgeDocument
from app.models.log import LogEntry
from app.models.remediation import RemediationRequest
from app.models.service import Service
from app.monitoring.detector import AnomalyDetector
from app.retrieval.hybrid_retriever import HybridRetriever
from app.schemas.audit import AuditEventOut
from app.schemas.incident import IncidentOut, IncidentUpdate, TimelineItem
from app.schemas.investigation import InvestigationCreateRequest
from app.schemas.knowledge import KnowledgeDocumentOut, KnowledgeSearchRequest, KnowledgeSearchResult
from app.schemas.log import LogEntryOut
from app.schemas.metric import MetricSampleOut, MetricsOverviewResponse
from app.schemas.remediation import (
    RemediationApproveRequest,
    RemediationExecuteRequest,
    RemediationOut,
    RemediationProposeRequest,
    RemediationRejectRequest,
)
from app.schemas.service import ServiceOut
from app.services.audit_service import AuditService
from app.services.incident_service import IncidentService
from app.services.metrics_service import MetricsService
from app.services.remediation_service import RemediationService

router = APIRouter(prefix="/api")

# Cached hybrid retriever for knowledge search
_retriever: Optional[HybridRetriever] = None

def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        cur = os.path.abspath(__file__)
        for _ in range(4):
            cur = os.path.dirname(cur)
        knowledge_dir = os.path.join(cur, "knowledge", "runbooks")
        _retriever = HybridRetriever()
        if os.path.exists(knowledge_dir):
            _retriever.load_from_directory(knowledge_dir)
    return _retriever

# -------------------------------------------------------------
# SERVICES
# -------------------------------------------------------------
@router.get("/services", response_model=List[ServiceOut], summary="List monitored services")
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()

@router.get("/services/{service_id}", response_model=ServiceOut, summary="Get service by ID")
def get_service(service_id: str, db: Session = Depends(get_db)):
    srv = db.query(Service).filter(Service.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")
    return srv

# -------------------------------------------------------------
# INCIDENTS
# -------------------------------------------------------------
@router.get("/incidents", response_model=List[IncidentOut], summary="Query and filter incidents")
def list_incidents(
    severity: Optional[str] = Query(None, description="CRITICAL, HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="TRIGGERED, ACKNOWLEDGED, INVESTIGATING, MITIGATED, RESOLVED"),
    service_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    service = IncidentService(db)
    return service.get_incidents(
        severity=severity,
        status=status,
        service_id=service_id,
        search=search,
        limit=limit,
        offset=offset,
    )

@router.get("/incidents/{incident_id}", response_model=IncidentOut, summary="Get incident details")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    service = IncidentService(db)
    inc = service.get_incident_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return inc

@router.patch("/incidents/{incident_id}", response_model=IncidentOut, summary="Update incident status")
def update_incident(incident_id: str, payload: IncidentUpdate, db: Session = Depends(get_db)):
    service = IncidentService(db)
    try:
        updated = service.update_incident_status(
            incident_id=incident_id,
            new_status=payload.status or "ACKNOWLEDGED",
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/incidents/{incident_id}/logs", response_model=List[LogEntryOut], summary="Get logs for an incident")
def get_incident_logs(
    incident_id: str,
    level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    q = db.query(LogEntry).filter(
        (LogEntry.incident_id == incident_id) |
        (LogEntry.service_id == inc.affected_service_id)
    )
    if level:
        q = q.filter(LogEntry.log_level == level.upper())
    return q.order_by(LogEntry.timestamp.desc()).limit(limit).all()

@router.get("/incidents/{incident_id}/metrics", response_model=List[MetricSampleOut], summary="Get incident metric samples")
def get_incident_metrics(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    metrics_service = MetricsService(db)
    return metrics_service.get_service_metric_samples(inc.affected_service_id, limit=50)

@router.get("/incidents/{incident_id}/timeline", response_model=List[TimelineItem], summary="Get reconstructed incident timeline")
def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    service = IncidentService(db)
    return service.build_incident_timeline(incident_id)

# -------------------------------------------------------------
# AI INVESTIGATION ASSISTANT
# -------------------------------------------------------------
@router.post("/incidents/{incident_id}/investigate", summary="Trigger automated AI incident investigation")
def investigate_incident(
    incident_id: str,
    payload: Optional[InvestigationCreateRequest] = None,
    db: Session = Depends(get_db),
):
    retriever = get_retriever()
    tools = InvestigationTools(db, retriever)
    investigator = IncidentInvestigator(db, tools)

    try:
        report = investigator.investigate(incident_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")

@router.get("/incidents/{incident_id}/investigations", summary="Get historical investigations for incident")
def get_investigations_for_incident(incident_id: str, db: Session = Depends(get_db)):
    investigations = (
        db.query(Investigation)
        .filter(Investigation.incident_id == incident_id)
        .order_by(Investigation.created_at.desc())
        .all()
    )
    results = []
    for inv in investigations:
        results.append({
            "id": inv.id,
            "incident_id": inv.incident_id,
            "summary": inv.summary,
            "findings": json.loads(inv.findings or "[]"),
            "root_cause_hypothesis": inv.root_cause_hypothesis,
            "confidence": inv.confidence,
            "confidence_justification": inv.confidence_justification,
            "supporting_evidence": json.loads(inv.supporting_evidence or "[]"),
            "recommended_actions": json.loads(inv.recommended_actions or "[]"),
            "missing_information": json.loads(inv.missing_information or "[]"),
            "limitations": json.loads(inv.limitations or "[]"),
            "investigation_mode": inv.investigation_mode,
            "execution_time_ms": inv.execution_time_ms,
            "created_at": inv.created_at.isoformat(),
        })
    return results

# -------------------------------------------------------------
# REMEDIATION WORKFLOW
# -------------------------------------------------------------
@router.post("/incidents/{incident_id}/remediations", response_model=RemediationOut, summary="Propose remediation")
def propose_remediation(
    incident_id: str,
    payload: RemediationProposeRequest,
    db: Session = Depends(get_db),
):
    service = RemediationService(db)
    try:
        req = service.propose_remediation(
            incident_id=incident_id,
            proposed_action=payload.proposed_action,
            reason_summary=payload.reason_summary,
            expected_impact=payload.expected_impact,
            risk_level=payload.risk_level,
            action_parameters=payload.action_parameters,
        )
        return req
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/remediations/{remediation_id}", response_model=RemediationOut, summary="Get remediation request")
def get_remediation(remediation_id: int, db: Session = Depends(get_db)):
    req = db.query(RemediationRequest).filter(RemediationRequest.id == remediation_id).first()
    if not req:
        raise HTTPException(status_code=404, detail=f"Remediation #{remediation_id} not found")
    return req

@router.get("/incidents/{incident_id}/remediation-history", response_model=List[RemediationOut], summary="List remediations for incident")
def get_incident_remediations(incident_id: str, db: Session = Depends(get_db)):
    return (
        db.query(RemediationRequest)
        .filter(RemediationRequest.incident_id == incident_id)
        .order_by(RemediationRequest.created_at.desc())
        .all()
    )

@router.post("/remediations/{remediation_id}/approve", response_model=RemediationOut, summary="Approve remediation")
def approve_remediation(
    remediation_id: int,
    payload: RemediationApproveRequest,
    db: Session = Depends(get_db),
):
    service = RemediationService(db)
    try:
        return service.approve_remediation(
            remediation_id=remediation_id,
            approver_id=payload.approver_id,
            notes=payload.approval_notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/remediations/{remediation_id}/reject", response_model=RemediationOut, summary="Reject remediation")
def reject_remediation(
    remediation_id: int,
    payload: RemediationRejectRequest,
    db: Session = Depends(get_db),
):
    service = RemediationService(db)
    try:
        return service.reject_remediation(
            remediation_id=remediation_id,
            approver_id=payload.approver_id,
            rejection_reason=payload.rejection_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/remediations/{remediation_id}/execute", response_model=RemediationOut, summary="Execute approved remediation")
def execute_remediation(
    remediation_id: int,
    payload: RemediationExecuteRequest,
    db: Session = Depends(get_db),
):
    service = RemediationService(db)
    try:
        return service.execute_remediation(
            remediation_id=remediation_id,
            operator_id=payload.operator_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

# -------------------------------------------------------------
# AUDIT & METRICS OVERVIEW
# -------------------------------------------------------------
@router.get("/audit-events", response_model=List[AuditEventOut], summary="List audit events")
def list_audit_events(
    event_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    service = AuditService(db)
    return service.get_events(event_type=event_type, resource_id=resource_id, limit=limit, offset=offset)

@router.get("/metrics/overview", response_model=MetricsOverviewResponse, summary="Operations overview telemetry")
def get_metrics_overview(db: Session = Depends(get_db)):
    service = MetricsService(db)
    return service.get_overview()

# -------------------------------------------------------------
# KNOWLEDGE BASE & RUNBOOKS
# -------------------------------------------------------------
@router.get("/knowledge/runbooks", response_model=List[KnowledgeDocumentOut], summary="List all runbooks")
def list_runbooks(db: Session = Depends(get_db)):
    return db.query(KnowledgeDocument).all()

@router.post("/knowledge/search", response_model=List[KnowledgeSearchResult], summary="Search runbooks via hybrid RAG")
def search_knowledge(payload: KnowledgeSearchRequest):
    retriever = get_retriever()
    clean_q = sanitize_untrusted_text(payload.query)
    results = retriever.search(clean_q, top_k=payload.top_k, method=payload.method)
    return [
        KnowledgeSearchResult(
            id=r["id"],
            title=r["title"],
            category=r["category"],
            snippet=r["snippet"],
            source=r["source"],
            relevance_score=r["relevance_score"],
            retrieval_method=r.get("retrieval_method", payload.method),
        )
        for r in results
    ]

# -------------------------------------------------------------
# ANOMALY MONITORING & DETECTION
# -------------------------------------------------------------
@router.get("/monitoring/detections", summary="Scan telemetry and detect violations")
def scan_detections(db: Session = Depends(get_db)):
    detector = AnomalyDetector()
    return detector.run_detection_cycle(db)
