"""
Retrieval Quality Evaluation Suite
Calculates Recall@K, Precision@K, and Mean Reciprocal Rank (MRR)
comparing Lexical BM25, Dense Semantic, and Hybrid RAG retrieval on IT incident queries.
"""
import json
import os
from typing import Any, Dict, List

from app.retrieval.hybrid_retriever import HybridRetriever

# Evaluation ground truth: Realistic IT operations queries mapped to expected runbook IDs
BENCHMARK_QUERIES = [
    {
        "query": "HTTP 502 Bad Gateway and 500 internal server error spike after latest deployment",
        "expected_ids": ["RB-5XX-001", "RB-OPS-006"],
    },
    {
        "query": "database connection pool timeout QueuePool limit of size 20 overflow reached",
        "expected_ids": ["RB-DB-002"],
    },
    {
        "query": "upstream connection timed out 110 high p95 latency on API gateway",
        "expected_ids": ["RB-LAT-003"],
    },
    {
        "query": "JWT signature has expired 401 unauthorized token rotation failure",
        "expected_ids": ["RB-AUTH-004"],
    },
    {
        "query": "worker queue backlog Celery pending tasks high memory consumption",
        "expected_ids": ["RB-JOB-005"],
    },
    {
        "query": "abort production rollout and revert service to last stable release",
        "expected_ids": ["RB-OPS-006"],
    },
    {
        "query": "Sev-1 critical outage communication cadence and on-call escalation SLA",
        "expected_ids": ["RB-ESC-007"],
    },
    {
        "query": "null pointer exception crash loop in order database handler",
        "expected_ids": ["RB-5XX-001", "RB-DB-002"],
    },
    {
        "query": "scale worker pool background job queue starvation",
        "expected_ids": ["RB-JOB-005"],
    },
    {
        "query": "expired service account LDAP credentials causing auth outage",
        "expected_ids": ["RB-AUTH-004"],
    },
]

def calculate_precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """Computes Precision@K: fraction of retrieved items in top-K that are relevant."""
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_retrieved = sum(1 for item in top_k if item in relevant_ids)
    return relevant_retrieved / k

def calculate_recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """Computes Recall@K: fraction of relevant items that were successfully retrieved in top-K."""
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    relevant_retrieved = sum(1 for item in top_k if item in relevant_ids)
    return relevant_retrieved / len(relevant_ids)

def calculate_reciprocal_rank(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """Computes Reciprocal Rank (1/rank) of the first relevant document."""
    for rank, item in enumerate(retrieved_ids, start=1):
        if item in relevant_ids:
            return 1.0 / rank
    return 0.0

def evaluate_retriever(
    retriever: HybridRetriever,
    benchmark_queries: List[Dict[str, Any]] = BENCHMARK_QUERIES,
    k_values: List[int] = [1, 3, 5]
) -> Dict[str, Any]:
    """
    Runs automated evaluation across BM25, Semantic, and Hybrid retrieval methods.
    Calculates Mean Reciprocal Rank (MRR), Recall@K, and Precision@K.
    """
    methods = ["BM25", "SEMANTIC", "HYBRID"]
    results: Dict[str, Any] = {}

    for method in methods:
        mrr_sum = 0.0
        recall_sums = {k: 0.0 for k in k_values}
        precision_sums = {k: 0.0 for k in k_values}
        query_details = []

        for item in benchmark_queries:
            query = item["query"]
            expected = item["expected_ids"]

            hits = retriever.search(query, top_k=max(k_values), method=method)
            retrieved_ids = [hit["id"] for hit in hits]

            rr = calculate_reciprocal_rank(retrieved_ids, expected)
            mrr_sum += rr

            recalls = {}
            precisions = {}
            for k in k_values:
                r_k = calculate_recall_at_k(retrieved_ids, expected, k)
                p_k = calculate_precision_at_k(retrieved_ids, expected, k)
                recall_sums[k] += r_k
                precision_sums[k] += p_k
                recalls[f"recall@{k}"] = round(r_k, 3)
                precisions[f"precision@{k}"] = round(p_k, 3)

            query_details.append({
                "query": query,
                "expected": expected,
                "retrieved": retrieved_ids,
                "reciprocal_rank": round(rr, 3),
                "metrics": {**recalls, **precisions}
            })

        total_q = len(benchmark_queries)
        results[method] = {
            "mrr": round(mrr_sum / total_q, 4) if total_q > 0 else 0.0,
            "recall": {f"recall@{k}": round(recall_sums[k] / total_q, 4) for k in k_values},
            "precision": {f"precision@{k}": round(precision_sums[k] / total_q, 4) for k in k_values},
            "query_evaluations": query_details
        }

    return results

def run_and_save_evaluation(knowledge_dir: str, output_path: str) -> Dict[str, Any]:
    """Initializes retriever with real runbooks, executes evaluation, and saves structured JSON results."""
    retriever = HybridRetriever()
    retriever.load_from_directory(knowledge_dir)
    results = evaluate_retriever(retriever)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results
