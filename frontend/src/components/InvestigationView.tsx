import React, { useState, useEffect } from 'react';
import { Incident, Investigation } from '../types';
import { api } from '../api/client';
import {
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Clock,
  Layers,
  CheckCircle,
  HelpCircle,
  ArrowRight,
  Database,
  GitCommit,
  Terminal,
  Activity,
  Cpu,
} from 'lucide-react';

interface InvestigationViewProps {
  incidents: Incident[];
  selectedIncidentId: string | null;
  onSelectIncident: (id: string) => void;
  onNavigateRemediation: (incidentId: string, actionName: string, justification: string, riskLevel: string) => void;
}

export const InvestigationView: React.FC<InvestigationViewProps> = ({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  onNavigateRemediation,
}) => {
  const currentIncidentId = selectedIncidentId || (incidents[0]?.id ?? '');
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch latest investigation on mount or incident change
  useEffect(() => {
    if (!currentIncidentId) return;
    setError(null);
    setLoading(true);
    api
      .getInvestigations(currentIncidentId)
      .then((invs) => {
        if (invs.length > 0) {
          setInvestigation(invs[0]);
        } else {
          setInvestigation(null);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [currentIncidentId]);

  const handleRunInvestigation = async () => {
    if (!currentIncidentId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.triggerInvestigation(currentIncidentId);
      setInvestigation(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedIncident = incidents.find((i) => i.id === currentIncidentId);

  return (
    <div className="page-body">
      {/* Top Header Card */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#3b82f6',
            }}>
              <Sparkles size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '16px', color: '#fff' }}>
                AI Incident Investigation Assistant
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Automated multi-tool root cause analysis & citation-backed evidence synthesis
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Target Incident:</span>
              <select
                value={currentIncidentId}
                onChange={(e) => onSelectIncident(e.target.value)}
                style={{ fontWeight: 600, minWidth: '180px' }}
              >
                {incidents.map((inc) => (
                  <option key={inc.id} value={inc.id}>
                    {inc.id} - {inc.affected_service_id} ({inc.severity})
                  </option>
                ))}
              </select>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleRunInvestigation}
              disabled={loading}
              style={{ gap: '8px', padding: '8px 16px', fontWeight: 600 }}
            >
              <Cpu size={15} />
              {loading ? 'Analyzing Telemetry & Runbooks...' : 'Run Automated Investigation'}
            </button>
          </div>
        </div>

        {/* Engine Banner */}
        <div style={{
          marginTop: '14px',
          padding: '8px 12px',
          backgroundColor: 'rgba(6, 182, 212, 0.08)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#67e8f9',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldCheck size={15} />
            <span>Mode: <strong>LOCAL_DETERMINISTIC</strong> (Zero-hallucination ground truth engine)</span>
          </div>
          <span style={{ color: 'var(--text-muted)' }}>Evidence strict citation policy active</span>
        </div>
      </div>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #ef4444', color: '#f87171' }}>
          <strong>Investigation Error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ display: 'inline-block', marginBottom: '12px' }}>
            <Sparkles size={28} color="#3b82f6" className="spin" />
          </div>
          <div style={{ fontSize: '15px', fontWeight: 600, color: '#fff' }}>
            Gathering logs, metrics, deployments, and indexing IT runbooks...
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Correlating timestamps and synthesizing grounded citations...
          </div>
        </div>
      )}

      {!loading && !investigation && (
        <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-secondary)' }}>
          <AlertTriangle size={32} color="#f59e0b" style={{ margin: '0 auto 10px' }} />
          <div style={{ fontSize: '15px', fontWeight: 600, color: '#fff' }}>No Active Investigation Report Found</div>
          <div style={{ fontSize: '13px', margin: '6px 0 16px' }}>
            Click <strong>"Run Automated Investigation"</strong> to inspect logs, telemetry, and runbooks for {currentIncidentId}.
          </div>
          <button className="btn btn-primary" onClick={handleRunInvestigation}>
            Start Investigation
          </button>
        </div>
      )}

      {/* Investigation Report Display */}
      {!loading && investigation && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Executive Summary & Hypothesis */}
          <div className="card" style={{ borderLeft: '4px solid #3b82f6' }}>
            <div className="card-header">
              <div className="card-title">
                <FileText size={16} color="#3b82f6" />
                Root Cause Hypothesis & Executive Summary
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span className={`badge ${investigation.confidence === 'HIGH' ? 'badge-healthy' : 'badge-medium'}`}>
                  Confidence: {investigation.confidence}
                </span>
                <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Computed in {investigation.execution_time_ms} ms
                </span>
              </div>
            </div>

            <div style={{
              fontSize: '15px',
              fontWeight: 700,
              color: '#fff',
              backgroundColor: 'var(--bg-secondary)',
              padding: '12px 16px',
              borderRadius: '6px',
              marginBottom: '12px',
              border: '1px solid var(--border-color)',
            }}>
              {investigation.root_cause_hypothesis}
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {investigation.summary}
            </p>

            {investigation.confidence_justification && (
              <div style={{ marginTop: '12px', fontSize: '12px', color: '#93c5fd', backgroundColor: 'rgba(59, 130, 246, 0.1)', padding: '8px 12px', borderRadius: '4px' }}>
                <strong>Justification:</strong> {investigation.confidence_justification}
              </div>
            )}
          </div>

          {/* Key Findings & Corroborated Evidence Citations */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Findings List */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Layers size={16} color="#06b6d4" />
                  Correlated Telemetry Findings
                </div>
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {investigation.findings.map((finding, idx) => (
                  <li
                    key={idx}
                    style={{
                      padding: '8px 12px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '6px',
                      fontSize: '12px',
                      display: 'flex',
                      gap: '8px',
                      alignItems: 'flex-start',
                    }}
                  >
                    <CheckCircle size={14} color="#34d399" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span style={{ color: '#e5e7eb' }}>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Verifiable Evidence Citations */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Database size={16} color="#10b981" />
                  Verifiable Evidence Citations ({investigation.supporting_evidence.length})
                </div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Audit ground truth references</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
                {investigation.supporting_evidence.map((ev, idx) => {
                  const icon =
                    ev.source_type === 'DEPLOYMENT' ? <GitCommit size={14} color="#3b82f6" /> :
                    ev.source_type === 'LOG' ? <Terminal size={14} color="#f97316" /> :
                    ev.source_type === 'METRIC' ? <Activity size={14} color="#06b6d4" /> : <FileText size={14} color="#10b981" />;

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: '10px 12px',
                        backgroundColor: 'var(--bg-secondary)',
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {icon}
                          <span className="mono" style={{ fontSize: '11px', fontWeight: 700, color: '#93c5fd' }}>
                            [{ev.source_id}]
                          </span>
                        </div>
                        {ev.relevance_score !== null && (
                          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                            Score: {ev.relevance_score}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: '#fff' }}>{ev.summary}</div>
                      {ev.data_snippet && (
                        <div className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                          snippet: {ev.data_snippet}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recommended Remediation Action Banner */}
          <div className="card" style={{ border: '1px solid #3b82f6', backgroundColor: 'rgba(30, 41, 59, 0.8)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-high">Recommended Action</span>
                  <span className="badge badge-critical">Requires Human Approval</span>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                  Action: <span className="mono" style={{ color: '#60a5fa' }}>{investigation.suggested_remediation}</span>
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  {investigation.recommended_actions[0]?.description}
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={() =>
                  onNavigateRemediation(
                    investigation.incident_id,
                    investigation.suggested_remediation || 'restart_service',
                    investigation.root_cause_hypothesis,
                    investigation.recommended_actions[0]?.risk_level || 'HIGH'
                  )
                }
                style={{ gap: '6px', padding: '10px 18px', fontWeight: 600 }}
              >
                Proceed to Remediation Review
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Missing Information & Limitations */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <HelpCircle size={16} color="#f59e0b" />
                  Missing Evidence & Unobserved Signals
                </div>
              </div>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {investigation.missing_information.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <AlertTriangle size={16} color="#6b7280" />
                  Operational Assumptions & Limitations
                </div>
              </div>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {investigation.limitations.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
