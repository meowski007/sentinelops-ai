from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KnowledgeDocumentBase(BaseModel):
    id: str
    title: str
    category: str
    content: str
    source: str
    version: str = "1.0"

class KnowledgeDocumentOut(KnowledgeDocumentBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class KnowledgeSearchResult(BaseModel):
    id: str
    title: str
    category: str
    snippet: str
    source: str
    relevance_score: float
    retrieval_method: str  # BM25, SEMANTIC, HYBRID

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 3
    method: str = "HYBRID"  # BM25, SEMANTIC, HYBRID
