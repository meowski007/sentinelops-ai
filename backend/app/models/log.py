from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    service_id = Column(String(50), ForeignKey("services.id"), nullable=False, index=True)
    log_level = Column(String(20), nullable=False, index=True)  # INFO, WARN, ERROR, FATAL
    message = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded extra context (status_code, trace_id, error_code, etc.)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True, index=True)

    # Relationships
    service = relationship("Service", back_populates="logs")
    incident = relationship("Incident", back_populates="logs")
