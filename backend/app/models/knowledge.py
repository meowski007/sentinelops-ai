from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from app.db.base import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # RUNBOOK, ARCHITECTURE, ESCALATION
    content = Column(Text, nullable=False)
    source = Column(String(200), nullable=False)  # file path or origin
    version = Column(String(20), default="1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
