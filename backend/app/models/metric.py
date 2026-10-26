from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class MetricSample(Base):
    __tablename__ = "metric_samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(String(50), ForeignKey("services.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metric_name = Column(String(50), nullable=False, index=True)  # error_rate, latency_p50, latency_p95, cpu_percent, queue_depth
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # percent, ms, count, etc.

    # Relationships
    service = relationship("Service", back_populates="metrics")
