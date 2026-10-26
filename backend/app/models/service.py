from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    environment = Column(String(50), default="production", nullable=False)
    current_status = Column(String(20), default="HEALTHY", nullable=False)  # HEALTHY, DEGRADED, OUTAGE
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    incidents = relationship("Incident", back_populates="service", cascade="all, delete-orphan")
    logs = relationship("LogEntry", back_populates="service", cascade="all, delete-orphan")
    metrics = relationship("MetricSample", back_populates="service", cascade="all, delete-orphan")
    deployments = relationship("DeploymentEvent", back_populates="service", cascade="all, delete-orphan")
