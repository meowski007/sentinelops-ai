"""
Audit Trail Service
Records and retrieves immutable audit logs for operational transparency and compliance.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def get_events(
        self,
        event_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditEvent]:
        q = self.db.query(AuditEvent)
        if event_type:
            q = q.filter(AuditEvent.event_type == event_type)
        if resource_id:
            q = q.filter(AuditEvent.resource_id == resource_id)
        return q.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
