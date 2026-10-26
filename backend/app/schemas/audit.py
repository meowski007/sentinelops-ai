from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditEventCreate(BaseModel):
    event_type: str
    actor: str = "system"
    resource_type: str
    resource_id: str
    action_summary: str
    metadata_json: Optional[str] = None

class AuditEventOut(BaseModel):
    id: int
    event_type: str
    actor: str
    resource_type: str
    resource_id: str
    action_summary: str
    timestamp: datetime
    metadata_json: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
