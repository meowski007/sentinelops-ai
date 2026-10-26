import React, { useState, useEffect } from 'react';
import { Incident, Remediation } from '../types';
import { api } from '../api/client';
import {
  Wrench,
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Play,
  RotateCcw,
  UserCheck,
  FileCheck,
  AlertOctagon,
} from 'lucide-react';

interface RemediationViewProps {
  incidents: Incident[];
  selectedIncidentId: string | null;
  proposedActionPrefill?: {
    actionName: string;
    justification: string;
    riskLevel: string;
  } | null;
  onRefreshAll: () => void;
}

export const RemediationView: React.FC<RemediationViewProps> = ({
  incidents,
  selectedIncidentId,
  proposedActionPrefill,
  onRefreshAll,
}) => {
  const currentIncidentId = selectedIncidentId || (incidents[0]?.id ?? '');
  const [remediations, setRemediations] = useState<Remediation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states for creating new proposal
  const [actionName, setActionName] = useState(proposedActionPrefill?.actionName || 'rollback_deployment');
  const [reason, setReason] = useState(
    proposedActionPrefill?.justification || 'Mitigate customer-facing HTTP 5xx errors caused by release regression'
  );
  const [expectedImpact, setExpectedImpact] = useState('Restores microservice stability and clears error spikes.');
  const [riskLevel, setRiskLevel] = useState(proposedActionPrefill?.riskLevel || 'HIGH');
  const [submitting, setSubmitting] = useState(false);

  // Approval/Execution actor inputs
  const [approverId, setApproverId] = useState('lead-operator@sentinelops.local');
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState<number | null>(null);

  const loadRemediations = () => {
    if (!currentIncidentId) return;
    setLoading(true);
    api
      .getIncidentRemediations(currentIncidentId)
      .then((rems) => setRemediations(rems))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadRemediations();
  }, [currentIncidentId]);

  const handlePropose = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentIncidentId) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.proposeRemediation(currentIncidentId, {
        proposed_action: actionName,
        reason_summary: reason,
        expected_impact: expectedImpact,
        risk_level: riskLevel,
        action_parameters: { incident_id: currentIncidentId },
      });
      loadRemediations();
      onRefreshAll();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleApprove = async (id: number) => {
    setError(null);
    try {
      await api.approveRemediation(id, approverId, 'Emergency stabilization sign-off');
      loadRemediations();
      onRefreshAll();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleReject = async (id: number) => {
    if (!rejectionReason.trim()) {
      alert('Please specify a rejection reason.');
      return;
    }
    setError(null);
    try {
      await api.rejectRemediation(id, approverId, rejectionReason);
      setShowRejectModal(null);
      setRejectionReason('');
      loadRemediations();
      onRefreshAll();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleExecute = async (id: number) => {
    setError(null);
    try {
      await api.executeRemediation(id, approverId);
      loadRemediations();
      onRefreshAll();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="page-body">
      {/* Header Guardrail Notice */}
      <div className="card" style={{ borderLeft: '4px solid #10b981', padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
          <ShieldCheck size={20} color="#10b981" />
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
            Approval-Controlled Remediation Gatekeeper
          </h2>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          All simulated state changes require explicit human-in-the-loop sign-off.
          The backend strictly blocks execution of unapproved requests, enforces role authorization,
          prevents replay attacks, and generates immutable audit trails.
        </p>
      </div>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #ef4444', color: '#f87171' }}>
          <strong>Remediation Gate Error:</strong> {error}
        </div>
      )}

      {/* Main Grid: Proposal Form (left) & Active Remediations (right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '20px' }}>
        {/* Propose Action Form */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Wrench size={16} color="#3b82f6" />
              Propose Simulated Remediation
            </div>
            <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Target: {currentIncidentId}
            </span>
          </div>

          <form onSubmit={handlePropose} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '6px', color: 'var(--text-secondary)' }}>
                Allowlisted Action
              </label>
              <select
                value={actionName}
                onChange={(e) => setActionName(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="rollback_deployment">rollback_deployment (Revert to last stable version)</option>
                <option value="drain_connection_pool">drain_connection_pool (Flush idle DB slots & locks)</option>
                <option value="scale_worker_pool">scale_worker_pool (Increase consumer concurrency)</option>
                <option value="refresh_service_credentials">refresh_service_credentials (Rotate cert & flush cache)</option>
                <option value="restart_service">restart_service (Graceful microservice reboot)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '6px', color: 'var(--text-secondary)' }}>
                Risk Classification
              </label>
              <select
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="HIGH">HIGH (Requires Senior Operator / Lead sign-off)</option>
                <option value="MEDIUM">MEDIUM (Requires Operator approval)</option>
                <option value="LOW">LOW (Safe diagnostic action)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '6px', color: 'var(--text-secondary)' }}>
                Operational Justification & Supporting Evidence
              </label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                style={{ width: '100%', resize: 'vertical' }}
                placeholder="Explain the root cause and evidence justifying this action..."
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '6px', color: 'var(--text-secondary)' }}>
                Expected System Impact
              </label>
              <input
                type="text"
                value={expectedImpact}
                onChange={(e) => setExpectedImpact(e.target.value)}
                style={{ width: '100%' }}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
              style={{ marginTop: '6px', padding: '10px', fontWeight: 600 }}
            >
              <FileCheck size={16} />
              {submitting ? 'Submitting Proposal...' : 'Submit Remediation Proposal'}
            </button>
          </form>
        </div>

        {/* Remediations List for Selected Incident */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <RotateCcw size={16} color="#f59e0b" />
              Remediation Action History ({remediations.length})
            </div>
            <button className="btn btn-secondary" onClick={loadRemediations} style={{ fontSize: '11px', padding: '3px 8px' }}>
              Refresh
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxHeight: '560px', overflowY: 'auto' }}>
            {remediations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                No remediation proposals submitted yet for {currentIncidentId}.
                Use the form on the left to submit a proposal.
              </div>
            ) : (
              remediations.map((rem) => {
                const isPending = rem.approval_status === 'PENDING_APPROVAL';
                const isApproved = rem.approval_status === 'APPROVED';
                const isExecuted = rem.execution_status === 'EXECUTED';
                const isRejected = rem.approval_status === 'REJECTED';

                return (
                  <div
                    key={rem.id}
                    style={{
                      padding: '16px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '8px',
                      border: isExecuted
                        ? '1px solid #10b981'
                        : isApproved
                        ? '1px solid #3b82f6'
                        : isRejected
                        ? '1px solid #ef4444'
                        : '1px solid var(--border-color)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="mono" style={{ fontWeight: 700, fontSize: '14px', color: '#fff' }}>
                          #{rem.id} {rem.proposed_action}
                        </span>
                        <span className={`badge badge-${rem.risk_level.toLowerCase()}`}>{rem.risk_level} RISK</span>
                      </div>
                      <span
                        className={`badge ${
                          isExecuted
                            ? 'badge-healthy'
                            : isApproved
                            ? 'badge-low'
                            : isRejected
                            ? 'badge-outage'
                            : 'badge-medium'
                        }`}
                      >
                        {isExecuted ? 'EXECUTED' : rem.approval_status}
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      <strong>Reason:</strong> {rem.reason_summary}
                    </div>

                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                      Impact: {rem.expected_impact} &bull; Created: {new Date(rem.created_at).toLocaleTimeString()}
                    </div>

                    {/* Executed Result Banner */}
                    {isExecuted && rem.execution_result && (
                      <div
                        style={{
                          padding: '10px 12px',
                          backgroundColor: 'rgba(16, 185, 129, 0.1)',
                          border: '1px solid rgba(16, 185, 129, 0.3)',
                          borderRadius: '6px',
                          fontSize: '12px',
                          color: '#34d399',
                          marginBottom: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <CheckCircle size={16} />
                        <div>{rem.execution_result}</div>
                      </div>
                    )}

                    {/* Rejection Banner */}
                    {isRejected && (
                      <div
                        style={{
                          padding: '8px 12px',
                          backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.3)',
                          borderRadius: '6px',
                          fontSize: '12px',
                          color: '#f87171',
                          marginBottom: '10px',
                        }}
                      >
                        {rem.execution_result}
                      </div>
                    )}

                    {/* Action Controls */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '10px', borderTop: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <UserCheck size={14} />
                        <span>Actor ID:</span>
                        <input
                          type="text"
                          value={approverId}
                          onChange={(e) => setApproverId(e.target.value)}
                          style={{ padding: '2px 6px', fontSize: '11px', width: '210px' }}
                        />
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        {isPending && (
                          <>
                            <button
                              className="btn btn-success"
                              onClick={() => handleApprove(rem.id)}
                              style={{ fontSize: '12px', padding: '5px 12px' }}
                            >
                              <CheckCircle size={14} /> Approve
                            </button>
                            <button
                              className="btn btn-danger"
                              onClick={() => setShowRejectModal(rem.id)}
                              style={{ fontSize: '12px', padding: '5px 12px' }}
                            >
                              <XCircle size={14} /> Reject
                            </button>
                          </>
                        )}

                        {isApproved && rem.execution_status === 'PENDING' && (
                          <button
                            className="btn btn-primary"
                            onClick={() => handleExecute(rem.id)}
                            style={{ fontSize: '12px', padding: '6px 14px', backgroundColor: '#10b981', borderColor: '#059669' }}
                          >
                            <Play size={14} /> Execute Simulated Remediation
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Rejection Modal Inline */}
                    {showRejectModal === rem.id && (
                      <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#0f172a', borderRadius: '6px', border: '1px solid #ef4444' }}>
                        <div style={{ fontSize: '12px', fontWeight: 600, color: '#f87171', marginBottom: '6px' }}>
                          Specify Reason for Rejection:
                        </div>
                        <input
                          type="text"
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          placeholder="e.g. Incompatible with upcoming scheduled database maintenance window"
                          style={{ width: '100%', marginBottom: '8px' }}
                        />
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                          <button className="btn btn-secondary" onClick={() => setShowRejectModal(null)} style={{ fontSize: '11px' }}>
                            Cancel
                          </button>
                          <button className="btn btn-danger" onClick={() => handleReject(rem.id)} style={{ fontSize: '11px' }}>
                            Confirm Rejection
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
