import React, { useState, useEffect } from 'react';
import { Incident, LogEntry, MetricSample, TimelineItem } from '../types';
import { api } from '../api/client';
import {
  Search,
  Filter,
  AlertOctagon,
  Sparkles,
  CheckCircle2,
  Clock,
  Terminal,
  Activity,
  GitCommit,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';

interface IncidentExplorerViewProps {
  incidents: Incident[];
  selectedIncidentId: string | null;
  onSelectIncident: (id: string) => void;
  onNavigateInvestigation: (id: string) => void;
  onRefresh: () => void;
}

export const IncidentExplorerView: React.FC<IncidentExplorerViewProps> = ({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  onNavigateInvestigation,
  onRefresh,
}) => {
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [activeTab, setActiveTab] = useState<'timeline' | 'logs' | 'metrics'>('timeline');

  // Detail drawer state
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [metrics, setMetrics] = useState<MetricSample[]>([]);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId) || incidents[0] || null;

  // Load details whenever selectedIncident changes
  useEffect(() => {
    if (!selectedIncident) return;
    setLoadingDetails(true);
    Promise.all([
      api.getIncidentTimeline(selectedIncident.id).catch(() => []),
      api.getIncidentLogs(selectedIncident.id).catch(() => []),
      api.getIncidentMetrics(selectedIncident.id).catch(() => []),
    ])
      .then(([tl, lg, mt]) => {
        setTimeline(tl);
        setLogs(lg);
        setMetrics(mt);
      })
      .finally(() => setLoadingDetails(false));
  }, [selectedIncident?.id]);

  // Filtered incidents
  const filtered = incidents.filter((inc) => {
    if (severityFilter !== 'ALL' && inc.severity !== severityFilter) return false;
    if (statusFilter !== 'ALL' && inc.status !== statusFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchText = `${inc.id} ${inc.title} ${inc.description} ${inc.affected_service_id}`.toLowerCase();
      if (!matchText.includes(q)) return false;
    }
    return true;
  });

  const handleAcknowledge = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setUpdatingStatus(true);
    try {
      await api.updateIncidentStatus(id, 'ACKNOWLEDGED');
      onRefresh();
    } catch (err: any) {
      alert(`Failed to acknowledge incident: ${err.message}`);
    } finally {
      setUpdatingStatus(false);
    }
  };

  return (
    <div className="page-body">
      {/* Top Filter Bar */}
      <div className="card" style={{ padding: '14px 18px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: '260px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <Search size={15} color="#9ca3af" style={{ position: 'absolute', left: '10px', top: '10px' }} />
              <input
                type="text"
                placeholder="Search incidents by ID, service, error message..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ width: '100%', paddingLeft: '32px' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              <Filter size={14} /> Severity:
            </div>
            <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)', marginLeft: '6px' }}>
              Status:
            </div>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="ALL">All Statuses</option>
              <option value="TRIGGERED">Triggered</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Split Layout: Table (left) & Detail Drawer (right) */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedIncident ? '1fr 1fr' : '1fr', gap: '20px' }}>
        {/* Incident List Table */}
        <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontWeight: 600, fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertOctagon size={16} color="#ef4444" />
              Incidents ({filtered.length})
            </div>
          </div>

          <div className="table-container" style={{ maxHeight: '680px', overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Incident</th>
                  <th>Service</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((inc) => {
                  const isSelected = selectedIncident?.id === inc.id;
                  return (
                    <tr
                      key={inc.id}
                      onClick={() => onSelectIncident(inc.id)}
                      style={{
                        backgroundColor: isSelected ? 'var(--bg-surface-hover)' : 'transparent',
                        cursor: 'pointer',
                      }}
                    >
                      <td>
                        <span className={`badge badge-${inc.severity.toLowerCase()}`}>{inc.severity}</span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: '13px', color: '#fff' }}>{inc.title}</div>
                        <div className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          {inc.id} &bull; {new Date(inc.detection_timestamp).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="mono" style={{ fontSize: '12px' }}>{inc.affected_service_id}</td>
                      <td>
                        <span className={`badge ${inc.status === 'RESOLVED' ? 'badge-healthy' : 'badge-neutral'}`}>
                          {inc.status}
                        </span>
                      </td>
                      <td>
                        {inc.status === 'TRIGGERED' ? (
                          <button
                            className="btn btn-secondary"
                            onClick={(e) => handleAcknowledge(inc.id, e)}
                            disabled={updatingStatus}
                            style={{ fontSize: '11px', padding: '3px 8px' }}
                          >
                            Acknowledge
                          </button>
                        ) : (
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>--</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Incident Detail Drawer */}
        {selectedIncident && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Header info */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px' }}>
                    <span className="mono" style={{ fontSize: '12px', color: '#60a5fa', fontWeight: 600 }}>
                      {selectedIncident.id}
                    </span>
                    <span className={`badge badge-${selectedIncident.severity.toLowerCase()}`}>
                      {selectedIncident.severity}
                    </span>
                    <span className="badge badge-neutral">{selectedIncident.status}</span>
                  </div>
                  <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{selectedIncident.title}</h3>
                </div>

                <button
                  className="btn btn-primary"
                  onClick={() => onNavigateInvestigation(selectedIncident.id)}
                  style={{ gap: '6px' }}
                >
                  <Sparkles size={14} />
                  Investigate with AI
                  <ArrowRight size={13} />
                </button>
              </div>

              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                {selectedIncident.description}
              </p>

              <div style={{ display: 'flex', gap: '16px', marginTop: '10px', fontSize: '12px', color: 'var(--text-muted)' }}>
                <div>Service: <span className="mono" style={{ color: 'var(--text-primary)' }}>{selectedIncident.affected_service_id}</span></div>
                <div>Trigger: <span className="mono" style={{ color: '#fb923c' }}>{selectedIncident.trigger_rule || selectedIncident.source}</span></div>
              </div>
            </div>

            {/* Sub-tabs */}
            <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', gap: '8px' }}>
              <button
                className="btn"
                onClick={() => setActiveTab('timeline')}
                style={{
                  borderBottom: activeTab === 'timeline' ? '2px solid #3b82f6' : '2px solid transparent',
                  borderRadius: 0,
                  color: activeTab === 'timeline' ? '#fff' : 'var(--text-secondary)',
                  padding: '6px 12px',
                }}
              >
                <Clock size={14} /> Chronological Timeline ({timeline.length})
              </button>
              <button
                className="btn"
                onClick={() => setActiveTab('logs')}
                style={{
                  borderBottom: activeTab === 'logs' ? '2px solid #3b82f6' : '2px solid transparent',
                  borderRadius: 0,
                  color: activeTab === 'logs' ? '#fff' : 'var(--text-secondary)',
                  padding: '6px 12px',
                }}
              >
                <Terminal size={14} /> Raw Logs ({logs.length})
              </button>
              <button
                className="btn"
                onClick={() => setActiveTab('metrics')}
                style={{
                  borderBottom: activeTab === 'metrics' ? '2px solid #3b82f6' : '2px solid transparent',
                  borderRadius: 0,
                  color: activeTab === 'metrics' ? '#fff' : 'var(--text-secondary)',
                  padding: '6px 12px',
                }}
              >
                <Activity size={14} /> Metrics ({metrics.length})
              </button>
            </div>

            {/* Tab 1: Timeline */}
            {activeTab === 'timeline' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '450px', overflowY: 'auto' }}>
                {timeline.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      gap: '12px',
                      padding: '10px 12px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '6px',
                      borderLeft: item.type === 'DETECTION' ? '3px solid #ef4444' : item.type === 'DEPLOYMENT' ? '3px solid #3b82f6' : '3px solid #f59e0b',
                    }}
                  >
                    <div style={{ marginTop: '2px' }}>
                      {item.type === 'DEPLOYMENT' ? <GitCommit size={15} color="#3b82f6" /> : item.type === 'DETECTION' ? <AlertTriangle size={15} color="#ef4444" /> : <Terminal size={15} color="#f59e0b" />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, fontSize: '13px', color: '#fff' }}>{item.title}</span>
                        <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        {item.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 2: Logs */}
            {activeTab === 'logs' && (
              <div style={{ maxHeight: '450px', overflowY: 'auto', backgroundColor: '#06090e', borderRadius: '6px', padding: '12px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                {logs.map((log) => (
                  <div key={log.id} style={{ marginBottom: '8px', borderBottom: '1px solid #1f293d', paddingBottom: '6px' }}>
                    <div style={{ display: 'flex', gap: '8px', color: 'var(--text-muted)', fontSize: '11px' }}>
                      <span>{new Date(log.timestamp).toISOString()}</span>
                      <span style={{ color: log.log_level === 'ERROR' ? '#f87171' : log.log_level === 'WARN' ? '#fbbf24' : '#60a5fa', fontWeight: 700 }}>
                        [{log.log_level}]
                      </span>
                      <span>service={log.service_id}</span>
                    </div>
                    <div style={{ color: '#e2e8f0', marginTop: '2px' }}>{log.message}</div>
                    {log.metadata_json && (
                      <div style={{ color: '#64748b', fontSize: '11px', marginTop: '2px' }}>
                        meta: {log.metadata_json}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Tab 3: Metrics */}
            {activeTab === 'metrics' && (
              <div style={{ maxHeight: '450px', overflowY: 'auto' }}>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Unit</th>
                        <th>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.slice(-15).map((m) => (
                        <tr key={m.id}>
                          <td className="mono">{m.metric_name}</td>
                          <td style={{ fontWeight: 600 }}>{m.value}</td>
                          <td>{m.unit}</td>
                          <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                            {new Date(m.timestamp).toLocaleTimeString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
