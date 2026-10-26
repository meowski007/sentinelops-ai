export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentStatus = 'TRIGGERED' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'MITIGATED' | 'RESOLVED';
export type ServiceStatus = 'HEALTHY' | 'DEGRADED' | 'OUTAGE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type ApprovalStatus = 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'NOT_REQUIRED';
export type ExecutionStatus = 'PENDING' | 'EXECUTED' | 'FAILED' | 'CANCELLED';

export interface Service {
  id: string;
  name: string;
  environment: string;
  current_status: ServiceStatus;
  description: string;
  created_at: string;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  affected_service_id: string;
  detection_timestamp: string;
  resolution_timestamp?: string | null;
  source: string;
  trigger_rule?: string | null;
  created_at: string;
}

export interface TimelineItem {
  timestamp: string;
  type: string;
  title: string;
  description: string;
  severity?: string | null;
  source_id?: string | null;
}

export interface LogEntry {
  id: number;
  timestamp: string;
  service_id: string;
  log_level: string;
  message: string;
  metadata_json?: string | null;
  incident_id?: string | null;
}

export interface MetricSample {
  id: number;
  service_id: string;
  timestamp: string;
  metric_name: string;
  value: number;
  unit: string;
}

export interface ServiceMetricsOverview {
  service_id: string;
  service_name: string;
  status: ServiceStatus;
  error_rate: number;
  latency_p95_ms: number;
  cpu_percent: number;
  request_volume: number;
  queue_depth?: number | null;
  samples: MetricSample[];
}

export interface MetricsOverviewResponse {
  timestamp: string;
  services: ServiceMetricsOverview[];
  active_incidents_count: number;
  critical_count: number;
}

export interface EvidenceReference {
  source_type: string;
  source_id: string;
  summary: string;
  relevance_score?: number | null;
  data_snippet?: string | null;
}

export interface RootCauseHypothesis {
  hypothesis: string;
  likelihood: string;
  supporting_evidence_keys: string[];
  justification: string;
}

export interface RecommendedAction {
  action_name: string;
  action_type: string;
  risk_level: RiskLevel;
  requires_approval: boolean;
  description: string;
  suggested_params?: Record<string, any>;
}

export interface Investigation {
  id: number;
  incident_id: string;
  summary: string;
  severity: Severity;
  affected_service: string;
  timeline: string[];
  findings: string[];
  root_cause_hypothesis: string;
  hypotheses?: RootCauseHypothesis[];
  confidence: string;
  confidence_justification?: string;
  supporting_evidence: EvidenceReference[];
  recommended_actions: RecommendedAction[];
  suggested_remediation?: string;
  requires_approval: boolean;
  missing_information: string[];
  limitations: string[];
  investigation_mode: string;
  execution_time_ms: number;
  created_at: string;
}

export interface Remediation {
  id: number;
  incident_id: string;
  proposed_action: string;
  action_parameters_json?: string | null;
  reason_summary: string;
  expected_impact: string;
  risk_level: RiskLevel;
  approval_status: ApprovalStatus;
  approver_id?: string | null;
  execution_status: ExecutionStatus;
  execution_result?: string | null;
  created_at: string;
  executed_at?: string | null;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  content: string;
  source: string;
  version: string;
  created_at: string;
}

export interface KnowledgeSearchResult {
  id: string;
  title: string;
  category: string;
  snippet: string;
  source: string;
  relevance_score: number;
  retrieval_method: string;
}

export interface AuditEvent {
  id: number;
  event_type: string;
  actor: string;
  resource_type: string;
  resource_id: string;
  action_summary: string;
  timestamp: string;
  metadata_json?: string | null;
}
