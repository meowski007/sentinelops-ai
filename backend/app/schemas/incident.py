from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    status: str = "TRIGGERED"  # TRIGGERED, ACKNOWLEDGED, INVESTIGATING, MITIGATED, RESOLVED
    affected_service_id: str
    source: str = "ANOMALY_DETECTOR"
    trigger_rule: Optional[str] = None

class IncidentCreate(IncidentBase):
    id: str

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    resolution_timestamp: Optional[datetime] = None

class IncidentOut(IncidentBase):
    id: str
    detection_timestamp: datetime
    resolution_timestamp: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimelineItem(BaseModel):
    timestamp: datetime
    type: str  # DEPLOYMENT, LOG_ANOMALY, DETECTION, INVESTIGATION, REMEDIATION, STATUS_CHANGE
    title: str
    description: str
    severity: Optional[str] = None
    source_id: Optional[str] = None
