# SentinelOps AI - System Architecture

SentinelOps AI is an enterprise IT operations and incident response platform designed to simulate production observability, automated telemetry correlation, retrieval-augmented runbook triage, and approval-controlled remediation.

## High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client Layer
        UI["React + TypeScript Dashboard\n(Vite, Recharts, Lucide)"]
    end

    subgraph API Gateway & Core API
        FastAPI["FastAPI REST Engine\n(/api/services, /api/incidents, /api/remediations)"]
        Guardrails["Security & Input Sanitization Layer\n(Prompt Injection Defenses, Allowlist)"]
    end

    subgraph Monitoring & Detection
        Detector["Statistical Anomaly Detector\n(Rolling Window Error Rates, p95 Latency)"]
        Rules["Explainable Rule Engine\n(Thresholds, Trigger Identifiers)"]
    end

    subgraph AI Investigation Assistant
        Investigator["Incident Investigator Agent"]
        Tools["Allowlisted Read-Only Tools\n(Logs, Metrics, Deployments, Runbooks)"]
        Synthesizer["Deterministic Grounded Synthesizer\n(Zero-Hallucination Evidence Correlator)"]
    end

    subgraph Hybrid RAG Knowledge Engine
        BM25["Lexical BM25 Okapi Index"]
        DenseVec["Dense Semantic Vector Space\n(Subword Hashing & Cosine Similarity)"]
        RRF["Reciprocal Rank Fusion (RRF)"]
        Runbooks["IT Runbooks Corpus\n(Markdown Standard Operating Procedures)"]
    end

    subgraph Remediation & Safety Gates
        Gatekeeper["Approval Gatekeeper\n(Role Verification, State Machine)"]
        SimExec["Simulated Remediation Executor\n(Rollback, Drain Pool, Worker Scale)"]
    end

    subgraph Storage Layer
        DB[("Relational Database\n(SQLite Local / PostgreSQL Prod)")]
        AuditStore[("Immutable Audit Trail\n(Events, Actors, Resource IDs)")]
    end

    UI -->|REST Requests| FastAPI
    FastAPI --> Guardrails
    Guardrails --> Detector
    Guardrails --> Investigator
    Guardrails --> Gatekeeper

    Detector --> Rules
    Detector --> DB

    Investigator --> Tools
    Tools --> DB
    Tools --> RRF
    RRF --> BM25
    RRF --> DenseVec
    BM25 --> Runbooks
    DenseVec --> Runbooks
    Tools --> Synthesizer

    Gatekeeper --> SimExec
    SimExec --> DB
    SimExec --> AuditStore
    Investigator --> AuditStore
```

## Investigation & Remediation Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Operator as IT Operator / Responder
    participant UI as React Console
    participant API as FastAPI REST Gateway
    participant Agent as Investigation Agent
    participant RAG as Hybrid RAG Retriever
    participant Gate as Approval Gatekeeper
    participant DB as System Database

    Operator->>UI: Selects Incident INC-2026-001
    UI->>API: POST /api/incidents/{id}/investigate
    API->>Agent: Launch investigation pipeline
    Agent->>DB: get_incident_details, get_metrics, search_logs, get_deployments
    Agent->>RAG: search_runbooks("HTTP 502 Bad Gateway deployment")
    RAG-->>Agent: Top passages with citations (RB-5XX-001, RB-OPS-006)
    Agent->>Agent: Correlate deployment timestamp with 5xx error spike
    Agent->>Agent: Formulate root-cause hypothesis & grounded citations
    Agent->>DB: Persist Investigation & log AuditEvent
    Agent-->>UI: Return Structured Report with Citations & Recommended Action
    UI->>Operator: Displays Root Cause, Evidence Cards, Proposed Rollback
    Operator->>UI: Reviews & Submits Approval (lead-operator@sentinelops.local)
    UI->>API: POST /api/remediations/{id}/approve
    API->>Gate: Validate approver permissions & transition state to APPROVED
    Gate-->>UI: 200 OK (Status: APPROVED)
    Operator->>UI: Clicks "Execute Simulated Remediation"
    UI->>API: POST /api/remediations/{id}/execute
    API->>Gate: Verify state == APPROVED (Reject if unapproved)
    Gate->>DB: Apply simulated rollback (v2.4.0), update service to HEALTHY
    Gate->>DB: Update incident to RESOLVED & log AuditEvent
    Gate-->>UI: Execution Result & Recovery Confirmation
```

## Component Boundaries & Safety Guarantees

1. **Read-Only Telemetry Tools**: Investigation agents are granted strictly allowlisted, read-only tools. They cannot mutate state or invoke shell commands.
2. **Deterministic Grounded Output**: By default, SentinelOps uses a deterministic rule-grounded synthesizer that guarantees every citation (`[LOG-2]`, `[DEPLOY-1]`, `[RB-5XX-001]`) points to an actual record retrieved during the run.
3. **Approval Gating**: State changes (such as deployment rollbacks, worker pool scaling, or credential rotations) require human sign-off on the backend. Frontend buttons alone do not control access.
