from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    findings = Column(Text, nullable=False)  # JSON-encoded array of key findings
    root_cause_hypothesis = Column(Text, nullable=False)
    confidence = Column(String(20), default="MEDIUM", nullable=False)  # HIGH, MEDIUM, LOW
    confidence_justification = Column(Text, nullable=True)
    supporting_evidence = Column(Text, nullable=False)  # JSON-encoded array of verified evidence references
    recommended_actions = Column(Text, nullable=False)  # JSON-encoded list of actions
    missing_information = Column(Text, nullable=True)  # JSON-encoded list of missing data points
    limitations = Column(Text, nullable=True)  # JSON-encoded limitations/assumptions
    investigation_mode = Column(String(50), default="LOCAL_DETERMINISTIC", nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="investigations")
