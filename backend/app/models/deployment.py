from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class DeploymentEvent(Base):
    __tablename__ = "deployment_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(String(50), ForeignKey("services.id"), nullable=False, index=True)
    deployment_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    change_description = Column(Text, nullable=False)
    deployment_status = Column(String(20), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, ROLLED_BACK

    # Relationships
    service = relationship("Service", back_populates="deployments")
