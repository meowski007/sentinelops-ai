from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)
    actor = Column(String(100), default="system", nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # incident, investigation, remediation, service
    resource_id = Column(String(100), nullable=False, index=True)
    action_summary = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded extra context
