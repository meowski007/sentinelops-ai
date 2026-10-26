# SentinelOps AI - Data Dictionary & Schema Reference

This document describes the relational database schema, entities, fields, constraints, and relationships in SentinelOps AI.

---

## 1. `services`
Monitored enterprise microservices and infrastructure components.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | String(50) | PRIMARY KEY | Unique service identifier (e.g., `api-gateway`, `order-db`) |
| `name` | String(100) | NOT NULL | Human-readable service name |
| `environment` | String(50) | NOT NULL, DEFAULT 'production' | Deployment environment |
| `current_status` | String(20) | NOT NULL, DEFAULT 'HEALTHY' | `HEALTHY`, `DEGRADED`, or `OUTAGE` |
| `description` | Text | NULLABLE | Service purpose and architecture notes |
| `created_at` | DateTime | NOT NULL | Service registration timestamp |

---

## 2. `incidents`
Tracks service anomalies, alerts, and operational investigations.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | String(50) | PRIMARY KEY | Incident identifier (e.g., `INC-2026-001`) |
| `title` | String(200) | NOT NULL | Short summary of the outage |
| `description` | Text | NOT NULL | Detailed incident symptoms and observed impact |
| `severity` | String(20) | NOT NULL | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `status` | String(20) | NOT NULL | `TRIGGERED`, `ACKNOWLEDGED`, `INVESTIGATING`, `MITIGATED`, `RESOLVED` |
| `affected_service_id` | String(50) | FOREIGN KEY (`services.id`) | Service suffering the anomaly |
| `detection_timestamp` | DateTime | NOT NULL | Timestamp when rule triggered alert |
| `resolution_timestamp`| DateTime | NULLABLE | Timestamp when incident was marked resolved |
| `source` | String(100) | NOT NULL | Detector or alert origin |
| `trigger_rule` | String(100) | NULLABLE | Specific detection rule name (e.g. `ERROR_RATE_THRESHOLD_EXCEEDED`) |
| `created_at` | DateTime | NOT NULL | Record creation timestamp |

---

## 3. `log_entries`
Application and error logs collected across services.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Unique log entry ID |
| `timestamp` | DateTime | NOT NULL, INDEXED | Log emission timestamp |
| `service_id` | String(50) | FOREIGN KEY (`services.id`) | Emitting service identifier |
| `log_level` | String(20) | NOT NULL, INDEXED | `INFO`, `WARN`, `ERROR`, `FATAL` |
| `message` | Text | NOT NULL | Raw log message and stack trace |
| `metadata_json` | Text | NULLABLE | JSON context (status codes, trace ID, route) |
| `incident_id` | String(50) | FOREIGN KEY (`incidents.id`), NULLABLE | Associated incident if known |

---

## 4. `metric_samples`
Time-series measurements of throughput, latency, queue depths, and resource utilization.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Unique metric sample ID |
| `service_id` | String(50) | FOREIGN KEY (`services.id`) | Monitored service identifier |
| `timestamp` | DateTime | NOT NULL, INDEXED | Observation timestamp (5m intervals) |
| `metric_name` | String(50) | NOT NULL, INDEXED | `error_rate`, `latency_p95`, `cpu_percent`, `queue_depth`, etc. |
| `value` | Float | NOT NULL | Measured numeric value |
| `unit` | String(20) | NOT NULL | Unit of measure (`percent`, `ms`, `count`) |

---

## 5. `deployment_events`
Software rollouts, configuration updates, and database migrations.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Unique deployment record ID |
| `service_id` | String(50) | FOREIGN KEY (`services.id`) | Target service identifier |
| `deployment_timestamp` | DateTime | NOT NULL, INDEXED | Deployment completion timestamp |
| `version` | String(50) | NOT NULL | Version or git tag (e.g., `v2.4.1`) |
| `change_description` | Text | NOT NULL | Pull request / commit summary |
| `deployment_status` | String(20) | NOT NULL | `SUCCESS`, `FAILED`, `ROLLED_BACK` |

---

## 6. `investigations`
Automated AI investigation reports containing grounded findings and citations.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Unique report ID |
| `incident_id` | String(50) | FOREIGN KEY (`incidents.id`) | Investigated incident ID |
| `summary` | Text | NOT NULL | Executive diagnosis summary |
| `findings` | Text (JSON) | NOT NULL | JSON array of observed anomalies |
| `root_cause_hypothesis`| Text | NOT NULL | Primary technical hypothesis |
| `confidence` | String(20) | NOT NULL | `HIGH`, `MEDIUM`, `LOW` |
| `confidence_justification` | Text | NULLABLE | Rationale for confidence assignment |
| `supporting_evidence` | Text (JSON) | NOT NULL | JSON array of verified citation references |
| `recommended_actions` | Text (JSON) | NOT NULL | JSON array of proposed next steps |
| `missing_information` | Text (JSON) | NULLABLE | JSON array of missing telemetry |
| `limitations` | Text (JSON) | NULLABLE | JSON array of simulation boundaries |
| `investigation_mode` | String(50) | NOT NULL | `LOCAL_DETERMINISTIC` or `EXTERNAL_LLM` |
| `execution_time_ms` | Float | NOT NULL | Runtime analysis duration |
| `created_at` | DateTime | NOT NULL | Report timestamp |

---

## 7. `remediation_requests`
Approval-gated action proposals and execution results.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Remediation request ID |
| `incident_id` | String(50) | FOREIGN KEY (`incidents.id`) | Associated incident ID |
| `proposed_action` | String(100) | NOT NULL | Action from allowlist |
| `action_parameters_json` | Text | NULLABLE | JSON parameters for execution |
| `reason_summary` | Text | NOT NULL | Operational justification |
| `expected_impact` | Text | NOT NULL | Expected service recovery result |
| `risk_level` | String(20) | NOT NULL | `HIGH`, `MEDIUM`, `LOW` |
| `approval_status` | String(30) | NOT NULL | `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `NOT_REQUIRED` |
| `approver_id` | String(100) | NULLABLE | Sign-off actor identifier |
| `execution_status` | String(30) | NOT NULL | `PENDING`, `EXECUTED`, `FAILED`, `CANCELLED` |
| `execution_result` | Text | NULLABLE | Simulated outcome message |
| `created_at` | DateTime | NOT NULL | Proposal submission time |
| `executed_at` | DateTime | NULLABLE | Action execution timestamp |

---

## 8. `audit_events`
Immutable operational activity trail.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTOINCREMENT | Unique audit event ID |
| `event_type` | String(50) | NOT NULL, INDEXED | e.g. `REMEDIATION_APPROVED` |
| `actor` | String(100) | NOT NULL, INDEXED | Performing user or automated agent |
| `resource_type` | String(50) | NOT NULL | `incident`, `remediation`, etc. |
| `resource_id` | String(100) | NOT NULL | Resource ID acted upon |
| `action_summary` | Text | NOT NULL | Concise log summary |
| `timestamp` | DateTime | NOT NULL, INDEXED | UTC timestamp |
| `metadata_json` | Text | NULLABLE | Extra JSON context |
