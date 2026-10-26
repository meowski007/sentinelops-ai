# SentinelOps AI - RAG Retrieval Quality Benchmark & Evaluation

This document details the evaluation methodology, benchmark queries, ground truth runbook documents, and mathematical metrics comparing **Lexical BM25**, **Dense Semantic**, and **Hybrid Reciprocal Rank Fusion (RRF)** retrieval in SentinelOps AI.

---

## 1. Evaluation Methodology

A common weakness in AI portfolios is asserting that RAG "works" without mathematical verification. In SentinelOps AI, retrieval quality is systematically measured using an automated benchmark harness (`backend/app/retrieval/evaluator.py`).

### Metrics Defined:
1. **Recall@K**:
   $$\text{Recall@K} = \frac{|\text{Retrieved Top-K} \cap \text{Relevant}|}{|\text{Relevant}|}$$
   Measures the fraction of relevant runbooks that appear within the top $K$ retrieved results.
2. **Precision@K**:
   $$\text{Precision@K} = \frac{|\text{Retrieved Top-K} \cap \text{Relevant}|}{K}$$
   Measures the density of relevant documents in the top $K$ results.
3. **Mean Reciprocal Rank (MRR)**:
   $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
   Evaluates how rapidly the user encounters the first relevant runbook. If the first relevant document is at rank 1, the reciprocal rank is $1.0$; if at rank 2, $0.5$.

---

## 2. Benchmark Query Suite

The evaluation suite consists of 10 realistic enterprise IT operational queries mapped to ground-truth runbook documents:

| Query ID | User Query | Expected Runbooks |
|---|---|---|
| Q1 | "HTTP 502 Bad Gateway and 500 internal server error spike after latest deployment" | `RB-5XX-001`, `RB-OPS-006` |
| Q2 | "database connection pool timeout QueuePool limit of size 20 overflow reached" | `RB-DB-002` |
| Q3 | "upstream connection timed out 110 high p95 latency on API gateway" | `RB-LAT-003` |
| Q4 | "JWT signature has expired 401 unauthorized token rotation failure" | `RB-AUTH-004` |
| Q5 | "worker queue backlog Celery pending tasks high memory consumption" | `RB-JOB-005` |
| Q6 | "abort production rollout and revert service to last stable release" | `RB-OPS-006` |
| Q7 | "Sev-1 critical outage communication cadence and on-call escalation SLA" | `RB-ESC-007` |
| Q8 | "null pointer exception crash loop in order database handler" | `RB-5XX-001`, `RB-DB-002` |
| Q9 | "scale worker pool background job queue starvation" | `RB-JOB-005` |
| Q10 | "expired service account LDAP credentials causing auth outage" | `RB-AUTH-004` |

---

## 3. Actual Benchmark Results

Evaluated on 10 benchmark queries against the 7 standard IT operating procedures:

| Retrieval Method | MRR | Recall@1 | Recall@3 | Precision@1 |
|---|---|---|---|---|
| **Lexical BM25** | 1.0000 | 0.9000 | 1.0000 | 1.0000 |
| **Dense Semantic** | 0.9333 | 0.8000 | 1.0000 | 0.9000 |
| **Hybrid (RRF Fusion)** | **1.0000** | **0.9000** | **1.0000** | **1.0000** |

*Raw JSON results are saved automatically to `docs/retrieval_evaluation_results.json`.*

### Observations & Trade-Off Analysis:
- **Exact Codes**: Lexical BM25 excels when the user searches for exact HTTP codes (`502`, `500`) or error strings (`QueuePool limit`).
- **Conceptual Queries**: Dense semantic retrieval succeeds when the user describes symptoms colloquially ("abort production rollout" matches SOP `RB-OPS-006` even without the word "rollback").
- **Hybrid Fusion**: Reciprocal Rank Fusion (RRF) ensures that neither method's weaknesses penalize the operator. It achieves an optimal balance with **MRR 1.0000** and **100% Recall@3**.

---

## 4. How to Run the Benchmark

From the project root:

```bash
cd backend
python -m app.scripts.run_eval
```
