from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class EvidenceReference(BaseModel):
    source_type: str  # LOG, METRIC, DEPLOYMENT, RUNBOOK
    source_id: str    # e.g., "LOG-1042", "METRIC-LATENCY-P95", "DEPLOY-2", "RUNBOOK-5XX-001"
    summary: str
    relevance_score: Optional[float] = None
    data_snippet: Optional[str] = None

class RootCauseHypothesis(BaseModel):
    hypothesis: str
    likelihood: str  # HIGH, MEDIUM, LOW
    supporting_evidence_keys: List[str] = []
    justification: str

class RecommendedAction(BaseModel):
    action_name: str
    action_type: str  # DIAGNOSTIC, REMEDIATION
    risk_level: str   # LOW, MEDIUM, HIGH
    requires_approval: bool
    description: str
    suggested_params: Dict[str, Any] = {}

class InvestigationCreateRequest(BaseModel):
    force_refresh: bool = False
    include_extended_logs: bool = True

class InvestigationOut(BaseModel):
    id: int
    incident_id: str
    summary: str
    severity: str
    affected_service: str
    timeline: List[str] = []
    findings: List[str]
    root_cause_hypothesis: str
    hypotheses: List[RootCauseHypothesis] = []
    confidence: str  # HIGH, MEDIUM, LOW
    confidence_justification: Optional[str] = None
    supporting_evidence: List[EvidenceReference]
    recommended_actions: List[RecommendedAction]
    suggested_remediation: Optional[str] = None
    requires_approval: bool = True
    missing_information: List[str] = []
    limitations: List[str] = []
    investigation_mode: str  # LOCAL_DETERMINISTIC, EXTERNAL_LLM
    execution_time_ms: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
