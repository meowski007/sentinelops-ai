import React, { useState, useEffect } from 'react';
import { AuditEvent } from '../types';
import { api } from '../api/client';
import { History, Shield, Filter, Search, ChevronDown, ChevronRight, RefreshCw } from 'lucide-react';

export const AuditHistoryView: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const loadEvents = () => {
    setLoading(true);
    api
      .getAuditEvents()
      .then((data) => setEvents(data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const filtered = events.filter((evt) => {
    if (typeFilter !== 'ALL' && evt.event_type !== typeFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const match = `${evt.actor} ${evt.resource_type} ${evt.resource_id} ${evt.action_summary}`.toLowerCase();
      if (!match.includes(q)) return false;
    }
    return true;
  });

  return (
    <div className="page-body">
      <div className="card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <History size={18} color="#06b6d4" />
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>
                Immutable Audit Trail & Compliance Log
              </h2>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Complete record of automated detections, investigator findings, approval gates, and remediation executions.
            </div>
          </div>

          <button className="btn btn-secondary" onClick={loadEvents} disabled={loading} style={{ fontSize: '12px', gap: '6px' }}>
            <RefreshCw size={13} className={loading ? 'spin' : ''} />
            Refresh Log
          </button>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '220px' }}>
            <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search by actor, resource ID, or keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '100%', paddingLeft: '32px' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Event Type:</span>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="ALL">All Event Types</option>
              <option value="INCIDENT_DETECTED">INCIDENT_DETECTED</option>
              <option value="INCIDENT_ACKNOWLEDGED">INCIDENT_ACKNOWLEDGED</option>
              <option value="INVESTIGATION_COMPLETED">INVESTIGATION_COMPLETED</option>
              <option value="REMEDIATION_PROPOSED">REMEDIATION_PROPOSED</option>
              <option value="REMEDIATION_APPROVED">REMEDIATION_APPROVED</option>
              <option value="REMEDIATION_REJECTED">REMEDIATION_REJECTED</option>
              <option value="REMEDIATION_EXECUTED">REMEDIATION_EXECUTED</option>
            </select>
          </div>
        </div>
      </div>

      {/* Events Table */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={{ width: '30px' }}></th>
                <th>Timestamp (UTC)</th>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Resource Target</th>
                <th>Action Summary</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((evt) => {
                const isExpanded = expandedId === evt.id;
                const isApproval = evt.event_type.includes('APPROVED');
                const isExecuted = evt.event_type.includes('EXECUTED');
                const isRejected = evt.event_type.includes('REJECTED');
                const isDetected = evt.event_type.includes('DETECTED');

                const badgeClass = isExecuted
                  ? 'badge-healthy'
                  : isApproval
                  ? 'badge-low'
                  : isRejected
                  ? 'badge-outage'
                  : isDetected
                  ? 'badge-critical'
                  : 'badge-neutral';

                return (
                  <React.Fragment key={evt.id}>
                    <tr
                      onClick={() => setExpandedId(isExpanded ? null : evt.id)}
                      style={{ cursor: 'pointer', backgroundColor: isExpanded ? 'var(--bg-surface-hover)' : 'transparent' }}
                    >
                      <td style={{ textAlign: 'center', padding: '8px' }}>
                        {isExpanded ? <ChevronDown size={14} color="#9ca3af" /> : <ChevronRight size={14} color="#9ca3af" />}
                      </td>
                      <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        {new Date(evt.timestamp).toISOString()}
                      </td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{evt.event_type}</span>
                      </td>
                      <td className="mono" style={{ fontSize: '12px' }}>{evt.actor}</td>
                      <td className="mono" style={{ fontSize: '12px' }}>
                        {evt.resource_type}:{evt.resource_id}
                      </td>
                      <td style={{ fontSize: '13px' }}>{evt.action_summary}</td>
                    </tr>

                    {/* Expandable JSON Metadata Inspector */}
                    {isExpanded && (
                      <tr>
                        <td colSpan={6} style={{ backgroundColor: '#070b14', padding: '14px 20px', borderBottom: '1px solid var(--border-color)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 600, color: '#93c5fd', marginBottom: '4px' }}>
                            EVENT AUDIT METADATA:
                          </div>
                          <pre
                            style={{
                              fontFamily: 'var(--font-mono)',
                              fontSize: '11px',
                              color: '#cbd5e1',
                              backgroundColor: '#0f172a',
                              padding: '10px 14px',
                              borderRadius: '6px',
                              overflowX: 'auto',
                              border: '1px solid var(--border-color)',
                            }}
                          >
                            {evt.metadata_json
                              ? JSON.stringify(JSON.parse(evt.metadata_json), null, 2)
                              : '{\n  "status": "standard_event_logged"\n}'}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
