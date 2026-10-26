from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(20), default="TRIGGERED", nullable=False, index=True)  # TRIGGERED, ACKNOWLEDGED, INVESTIGATING, MITIGATED, RESOLVED
    affected_service_id = Column(String(50), ForeignKey("services.id"), nullable=False, index=True)
    detection_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolution_timestamp = Column(DateTime, nullable=True)
    source = Column(String(100), default="ANOMALY_DETECTOR", nullable=False)  # ANOMALY_DETECTOR, SYSLOG_ALERT, SYNTHETIC_MONITOR
    trigger_rule = Column(String(100), nullable=True)  # e.g., ERROR_RATE_THRESHOLD_EXCEEDED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    service = relationship("Service", back_populates="incidents")
    logs = relationship("LogEntry", back_populates="incident")
    investigations = relationship("Investigation", back_populates="incident", cascade="all, delete-orphan")
    remediations = relationship("RemediationRequest", back_populates="incident", cascade="all, delete-orphan")
