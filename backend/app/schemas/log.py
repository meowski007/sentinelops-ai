from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LogEntryOut(BaseModel):
    id: int
    timestamp: datetime
    service_id: str
    log_level: str
    message: str
    metadata_json: Optional[str] = None
    incident_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LogFilterParams(BaseModel):
    service_id: Optional[str] = None
    level: Optional[str] = None
    query: Optional[str] = None
    limit: int = 100
    offset: int = 0
