import {
  Service,
  Incident,
  TimelineItem,
  LogEntry,
  MetricSample,
  MetricsOverviewResponse,
  Investigation,
  Remediation,
  KnowledgeDocument,
  KnowledgeSearchResult,
  AuditEvent,
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  // Services
  getServices: (): Promise<Service[]> =>
    fetch(`${API_BASE}/api/services`).then(handleResponse<Service[]>),

  // Incidents
  getIncidents: (params?: { severity?: string; status?: string; service_id?: string; search?: string }): Promise<Incident[]> => {
    const q = new URLSearchParams();
    if (params?.severity) q.set('severity', params.severity);
    if (params?.status) q.set('status', params.status);
    if (params?.service_id) q.set('service_id', params.service_id);
    if (params?.search) q.set('search', params.search);
    return fetch(`${API_BASE}/api/incidents?${q.toString()}`).then(handleResponse<Incident[]>);
  },

  getIncident: (id: string): Promise<Incident> =>
    fetch(`${API_BASE}/api/incidents/${id}`).then(handleResponse<Incident>),

  updateIncidentStatus: (id: string, status: string): Promise<Incident> =>
    fetch(`${API_BASE}/api/incidents/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    }).then(handleResponse<Incident>),

  getIncidentLogs: (id: string, level?: string): Promise<LogEntry[]> => {
    const url = level ? `${API_BASE}/api/incidents/${id}/logs?level=${level}` : `${API_BASE}/api/incidents/${id}/logs`;
    return fetch(url).then(handleResponse<LogEntry[]>);
  },

  getIncidentTimeline: (id: string): Promise<TimelineItem[]> =>
    fetch(`${API_BASE}/api/incidents/${id}/timeline`).then(handleResponse<TimelineItem[]>),

  getIncidentMetrics: (id: string): Promise<MetricSample[]> =>
    fetch(`${API_BASE}/api/incidents/${id}/metrics`).then(handleResponse<MetricSample[]>),

  // AI Investigation
  triggerInvestigation: (id: string): Promise<Investigation> =>
    fetch(`${API_BASE}/api/incidents/${id}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }).then(handleResponse<Investigation>),

  getInvestigations: (id: string): Promise<Investigation[]> =>
    fetch(`${API_BASE}/api/incidents/${id}/investigations`).then(handleResponse<Investigation[]>),

  // Remediation
  proposeRemediation: (incidentId: string, payload: {
    proposed_action: string;
    reason_summary: string;
    expected_impact: string;
    risk_level: string;
    action_parameters?: Record<string, any>;
  }): Promise<Remediation> =>
    fetch(`${API_BASE}/api/incidents/${incidentId}/remediations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(handleResponse<Remediation>),

  approveRemediation: (remediationId: number, approverId: string, approvalNotes?: string): Promise<Remediation> =>
    fetch(`${API_BASE}/api/remediations/${remediationId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approver_id: approverId, approval_notes: approvalNotes }),
    }).then(handleResponse<Remediation>),

  rejectRemediation: (remediationId: number, approverId: string, rejectionReason: string): Promise<Remediation> =>
    fetch(`${API_BASE}/api/remediations/${remediationId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approver_id: approverId, rejection_reason: rejectionReason }),
    }).then(handleResponse<Remediation>),

  executeRemediation: (remediationId: number, operatorId: string): Promise<Remediation> =>
    fetch(`${API_BASE}/api/remediations/${remediationId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operator_id: operatorId }),
    }).then(handleResponse<Remediation>),

  getIncidentRemediations: (incidentId: string): Promise<Remediation[]> =>
    fetch(`${API_BASE}/api/incidents/${incidentId}/remediation-history`).then(handleResponse<Remediation[]>),

  // Telemetry Overview
  getMetricsOverview: (): Promise<MetricsOverviewResponse> =>
    fetch(`${API_BASE}/api/metrics/overview`).then(handleResponse<MetricsOverviewResponse>),

  // Knowledge Base & Runbooks
  searchKnowledge: (query: string, method: string = 'HYBRID', topK: number = 3): Promise<KnowledgeSearchResult[]> =>
    fetch(`${API_BASE}/api/knowledge/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, method, top_k: topK }),
    }).then(handleResponse<KnowledgeSearchResult[]>),

  getRunbooks: (): Promise<KnowledgeDocument[]> =>
    fetch(`${API_BASE}/api/knowledge/runbooks`).then(handleResponse<KnowledgeDocument[]>),

  // Audit Events
  getAuditEvents: (): Promise<AuditEvent[]> =>
    fetch(`${API_BASE}/api/audit-events`).then(handleResponse<AuditEvent[]>),

  // Health
  getHealth: (): Promise<{ status: string; uptime_seconds: number; ai_engine_mode: string }> =>
    fetch(`${API_BASE}/health`).then(handleResponse<{ status: string; uptime_seconds: number; ai_engine_mode: string }>),
};
