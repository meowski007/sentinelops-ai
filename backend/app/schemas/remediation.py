from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RemediationProposeRequest(BaseModel):
    proposed_action: str
    action_parameters: Optional[Dict[str, Any]] = None
    reason_summary: str
    expected_impact: str
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH

class RemediationApproveRequest(BaseModel):
    approver_id: str = Field(..., min_length=3, description="Identifier of the approving operator/lead")
    approval_notes: Optional[str] = None

class RemediationRejectRequest(BaseModel):
    approver_id: str = Field(..., min_length=3, description="Identifier of the rejecting operator/lead")
    rejection_reason: str = Field(..., min_length=5, description="Reason for rejecting the proposed remediation")

class RemediationExecuteRequest(BaseModel):
    operator_id: str = Field(..., min_length=3)

class RemediationOut(BaseModel):
    id: int
    incident_id: str
    proposed_action: str
    action_parameters_json: Optional[str] = None
    reason_summary: str
    expected_impact: str
    risk_level: str
    approval_status: str  # PENDING_APPROVAL, APPROVED, REJECTED, NOT_REQUIRED
    approver_id: Optional[str] = None
    execution_status: str  # PENDING, EXECUTED, FAILED, CANCELLED
    execution_result: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
