# SentinelOps AI - Interview Preparation & Defense Guide

This guide is designed for technical internship and entry-level engineering interviews. It covers the core technical problems, architectural trade-offs, security controls, and design decisions in SentinelOps AI.

---

## 1. What problem does SentinelOps AI solve?

In modern cloud environments, microservices generate millions of logs and metrics per hour. When an outage occurs, on-call IT operators are overwhelmed with disjointed alerts, confusing logs, and buried runbooks. Finding root causes and knowing what standard operating procedure to follow often takes hours (high Mean Time to Resolution, or MTTR).

**SentinelOps AI solves this by:**
1. **Automating Telemetry Correlation**: Correlating deployment timestamps with error rate surges and exception traces.
2. **Retrieving Relevant Runbooks (RAG)**: Using hybrid retrieval to match symptoms against standard operating procedures.
3. **Formulating Grounded Diagnoses**: Producing structured hypotheses where every single evidence item resolves to an actual database log ID or metric.
4. **Enforcing Safe Human-in-the-Loop Remediation**: Ensuring simulated fixes (like rollbacks or worker scaling) cannot be executed without backend approval.

---

## 2. Why did you choose this architecture?

- **FastAPI Backend**: Chosen for high throughput, asynchronous I/O capabilities, automatic OpenAPI schema generation, and native integration with Pydantic v2 validation models.
- **SQLite (Dev) / PostgreSQL (Prod)**: SQLAlchemy 2.0 ORM allows zero-setup local development with an embedded file database while supporting drop-in production PostgreSQL configurations.
- **Hybrid Retrieval (BM25 + Dense Semantic)**: Standard keyword search misses conceptual queries ("database sluggish" vs "connection pool exhaustion"), while pure semantic search can fail on exact error codes (`HTTP 502`, `NullPointerException`, `RB-DB-002`). Combining them via Reciprocal Rank Fusion (RRF) gives the best of both worlds.
- **React + TypeScript Frontend**: Provides type safety, reusable dashboard components, interactive charts (Recharts), and a professional operations console experience.

---

## 3. How does incident detection work?

Incident detection uses an explainable, rule-based statistical approach rather than a black-box machine learning model:
- **Rolling Time Windows**: Evaluates 5-minute rolling averages, median (p50), and 95th percentile (p95) latency over 15-minute to 1-hour windows.
- **Explainable Thresholds**:
  - `ERROR_RATE_THRESHOLD_EXCEEDED`: Error rate > 5.0%
  - `LATENCY_P95_THRESHOLD_EXCEEDED`: p95 latency > 2000 ms
  - `QUEUE_DEPTH_THRESHOLD_EXCEEDED`: Backlog > 1,000 tasks
  - `AUTH_FAILURE_RATE_EXCEEDED`: 401 failure rate > 10.0%
- **Trigger Record**: Every detected incident stores the exact `trigger_rule` and metric value that initiated the alert, eliminating guesswork.

---

## 4. How does the RAG pipeline work and how do you measure its quality?

### The Pipeline:
1. **Corpus Ingestion**: Markdown runbooks in `knowledge/runbooks/` are parsed, preserving titles, IDs (`RB-5XX-001`), categories, and source paths.
2. **Lexical Indexing (BM25Okapi)**: Tokenizes text, strips stopwords, computes term frequencies and Inverse Document Frequency (IDF) with $k_1 = 1.5, b = 0.75$.
3. **Dense Semantic Indexing**: Generates normalized 256-dimensional subword and n-gram hash embeddings, capturing morphology and intent without network dependency.
4. **Reciprocal Rank Fusion (RRF)**: Combines rankings:
   $$RRF(d) = \frac{1}{60 + \text{rank}_{BM25}(d)} + \frac{1}{60 + \text{rank}_{Semantic}(d)}$$

### Measuring Retrieval Quality:
We run an automated benchmark suite (`python -m app.scripts.run_eval`) against 10 ground-truth IT operational queries. The evaluated metrics are:
- **Mean Reciprocal Rank (MRR)**: Measures how high the first relevant document is ranked ($1/\text{rank}$). **Achieved: 1.0000**.
- **Recall@K**: Percentage of all relevant runbooks retrieved in the top K results. **Achieved Recall@1: 0.9000, Recall@3: 1.0000**.
- **Precision@K**: Percentage of top K results that are genuinely relevant. **Achieved Precision@1: 1.0000**.

---

## 5. How does the AI Assistant avoid hallucinations?

1. **Allowlisted, Read-Only Tools**: The assistant interacts with the database exclusively through 7 strongly-typed tools (`get_incident_details`, `get_service_metrics`, `search_logs`, `get_recent_deployments`, `search_runbooks`, `calculate_error_rate`, `get_related_incidents`).
2. **Deterministic Grounded Engine**: In default local mode, the assistant runs a deterministic correlation engine. Every citation (`[LOG-2]`, `[DEPLOY-1]`, `[METRIC-api-gateway-error_rate]`) is bound to the exact record retrieved by the tool.
3. **Structured Pydantic Validation**: Outputs must match the `InvestigationOut` schema. Uncorroborated claims are placed in the `hypotheses` list with explicit likelihood ratings, never stated as established facts.

---

## 6. Why is remediation approval-controlled?

In enterprise IT and SRE, automated remediation without guardrails is considered dangerous. A faulty diagnosis could cause an automated agent to restart the wrong database node, drop tables, or roll back a critical security fix.

**Security Controls Implemented:**
- **Allowlisted Actions**: Only pre-approved actions (`rollback_deployment`, `drain_connection_pool`, `scale_worker_pool`, `refresh_service_credentials`, `restart_service`) can be proposed.
- **Backend Authorization Enforcement**: Even if a user attempts to call `POST /api/remediations/{id}/execute` directly, the backend returns `403 Forbidden` unless the request has reached `APPROVED` status.
- **Replay & Duplicate Protection**: The state machine prevents executing an action twice or approving an already rejected request.
- **Immutable Audit Trail**: Every proposed, approved, rejected, or executed remediation is permanently logged with actor identifiers and timestamps.

---

## 7. What happens if the embedding model or LLM is offline?

SentinelOps AI was built with a **resilient zero-dependency fallback architecture**:
- **Offline Embeddings**: Uses dense subword n-gram hashing and cosine similarity that runs 100% locally with NumPy. No HuggingFace model download or GPU is required.
- **Offline Investigation**: When no external LLM API key (`OPENAI_API_KEY`) is configured, SentinelOps automatically runs in `LOCAL_DETERMINISTIC` mode. The platform remains fully functional for demonstration, triage, and remediation.

---

## 8. What are the key architectural trade-offs and remaining limitations?

1. **Local Simulation vs. Real Cloud Infrastructure**: The current system simulates microservices and telemetry using reproducible seeds. It intentionally does not connect to real AWS or Kubernetes clusters to prevent accidental cloud billing or security exposure during portfolio reviews.
2. **In-Memory Thread Safety**: In local testing, SQLite requires `StaticPool` when shared across multiple threads in FastAPI TestClient.
3. **Authentication Abstraction**: For portfolio clarity, authentication uses role/identifier strings (`operator@sentinelops.local`, `lead@sentinelops.local`) rather than full OAuth2/OIDC integration.

---

## 9. What would you build next with more time?

1. **OpenTelemetry Ingestion Pipeline**: Ingesting real OTLP traces and Jaeger span waterfalls.
2. **Fine-Tuned Small Language Model (SLM)**: Running a quantized local model (e.g., Llama-3-8B-Instruct or Phi-3) via llama.cpp or Ollama.
3. **Interactive Post-Mortem Generator**: Automatically generating Markdown incident post-mortems with timeline tables, root-cause summaries, and preventative action items.
