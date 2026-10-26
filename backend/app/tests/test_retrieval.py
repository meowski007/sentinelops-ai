from app.retrieval.bm25 import BM25Retriever
from app.retrieval.embeddings import SemanticRetriever
from app.retrieval.evaluator import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_reciprocal_rank,
)
from app.retrieval.hybrid_retriever import HybridRetriever

SAMPLE_DOCS = [
    {
        "id": "RB-5XX-001",
        "title": "Investigating High HTTP 5xx Server Error Spikes",
        "category": "RUNBOOK",
        "content": "Check deployment events within 30 minutes. If error rate exceeds 5 percent, consider deployment rollback.",
    },
    {
        "id": "RB-DB-002",
        "title": "Resolving Database Connection Pool Exhaustion",
        "category": "RUNBOOK",
        "content": "QueuePool limit reached. Check active connections, drain connection pool or restart proxy.",
    },
    {
        "id": "RB-AUTH-004",
        "title": "Remediation for Expired Authentication Signing Keys",
        "category": "RUNBOOK",
        "content": "JWT token verification signature expired. Propose refresh service credentials and cache flush.",
    },
]

def test_bm25_retriever():
    retriever = BM25Retriever()
    retriever.index(SAMPLE_DOCS)
    results = retriever.search("HTTP 5xx server error deployment rollback", top_k=1)
    assert len(results) == 1
    doc, score = results[0]
    assert doc["id"] == "RB-5XX-001"
    assert score > 0

def test_semantic_retriever():
    retriever = SemanticRetriever()
    retriever.index(SAMPLE_DOCS)
    results = retriever.search("database connection timeout pool size", top_k=1)
    assert len(results) == 1
    doc, score = results[0]
    assert doc["id"] == "RB-DB-002"
    assert score > 0

def test_hybrid_retriever():
    hybrid = HybridRetriever()
    hybrid.index_documents(SAMPLE_DOCS)
    results = hybrid.search("JWT token expired signing keys", top_k=1, method="HYBRID")
    assert len(results) == 1
    assert results[0]["id"] == "RB-AUTH-004"
    assert "relevance_score" in results[0]

def test_metric_calculations():
    retrieved = ["A", "B", "C", "D"]
    expected = ["B", "E"]

    # In top 2: ["A", "B"], 1 is relevant -> recall is 1/2 = 0.5, precision is 1/2 = 0.5
    recall_2 = calculate_recall_at_k(retrieved, expected, k=2)
    prec_2 = calculate_precision_at_k(retrieved, expected, k=2)
    assert recall_2 == 0.5
    assert prec_2 == 0.5

    # First relevant item is at rank 2 ("B") -> reciprocal rank is 1/2 = 0.5
    rr = calculate_reciprocal_rank(retrieved, expected)
    assert rr == 0.5
