from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class RemediationRequest(Base):
    __tablename__ = "remediation_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    proposed_action = Column(String(100), nullable=False)
    action_parameters_json = Column(Text, nullable=True)  # JSON-encoded parameters
    reason_summary = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=False)
    risk_level = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    approval_status = Column(String(30), default="PENDING_APPROVAL", nullable=False, index=True)  # PENDING_APPROVAL, APPROVED, REJECTED, NOT_REQUIRED
    approver_id = Column(String(100), nullable=True)  # demo actor
    execution_status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, EXECUTED, FAILED, CANCELLED
    execution_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="remediations")
