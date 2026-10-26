from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    id: str
    name: str
    environment: str = "production"
    current_status: str = "HEALTHY"
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    current_status: Optional[str] = None
    description: Optional[str] = None

class ServiceOut(ServiceBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
