import React from 'react';
import { MetricsOverviewResponse, Incident, AuditEvent } from '../types';
import { AlertCircle, Activity, Server, Clock, GitCommit, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface OverviewViewProps {
  metrics: MetricsOverviewResponse | null;
  incidents: Incident[];
  auditEvents: AuditEvent[];
  onSelectIncident: (incidentId: string) => void;
  onNavigateTab: (tab: any) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  metrics,
  incidents,
  auditEvents,
  onSelectIncident,
  onNavigateTab,
}) => {
  const activeIncidents = incidents.filter((i) => i.status !== 'RESOLVED');
  const criticalCount = activeIncidents.filter((i) => i.severity === 'CRITICAL').length;
  const highCount = activeIncidents.filter((i) => i.severity === 'HIGH').length;

  // Prepare chart series from service samples
  const chartData = (metrics?.services[0]?.samples || []).map((sample, idx) => {
    const point: any = { time: new Date(sample.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    metrics?.services.forEach((s) => {
      const sSample = s.samples[idx];
      if (sSample) {
        point[s.service_id] = sSample.value;
      }
    });
    return point;
  });

  return (
    <div className="page-body">
      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="card" style={{ borderLeft: '4px solid #ef4444' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '12px', fontWeight: 600 }}>ACTIVE INCIDENTS</span>
            <AlertCircle size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, margin: '8px 0 4px', color: '#fff' }}>
            {activeIncidents.length}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            <span style={{ color: '#f87171', fontWeight: 600 }}>{criticalCount} Critical</span> &bull; {highCount} High
          </div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid #3b82f6' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '12px', fontWeight: 600 }}>MONITORED SERVICES</span>
            <Server size={18} color="#3b82f6" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, margin: '8px 0 4px', color: '#fff' }}>
            {metrics?.services.length || 5}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Production microservices fleet
          </div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '12px', fontWeight: 600 }}>API GATEWAY ERROR RATE</span>
            <Activity size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, margin: '8px 0 4px', color: '#f59e0b' }}>
            {metrics?.services.find((s) => s.service_id === 'api-gateway')?.error_rate.toFixed(1) || '14.8'}%
          </div>
          <div style={{ fontSize: '12px', color: '#f87171' }}>
            Threshold violation (&gt; 5.0%)
          </div>
        </div>

        <div className="card" style={{ borderLeft: '4px solid #10b981' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '12px', fontWeight: 600 }}>AI INVESTIGATION MODE</span>
            <ShieldCheck size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, margin: '12px 0 4px', color: '#34d399' }}>
            Deterministic Grounded
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Verifiable evidence citations only
          </div>
        </div>
      </div>

      {/* Services Health Grid */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Server size={16} color="#3b82f6" />
            Monitored Enterprise Services & Telemetry
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Updated real-time from simulated metrics</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
          {(metrics?.services || []).map((srv) => {
            const statusClass =
              srv.status === 'HEALTHY' ? 'badge-healthy' : srv.status === 'DEGRADED' ? 'badge-degraded' : 'badge-outage';
            return (
              <div
                key={srv.service_id}
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>{srv.service_name}</div>
                  <span className={`badge ${statusClass}`}>{srv.status}</span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '12px' }}>
                  ID: {srv.service_id}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', fontSize: '12px' }}>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Error Rate</div>
                    <div style={{ fontWeight: 600, color: srv.error_rate > 5 ? '#f87171' : 'var(--text-primary)' }}>
                      {srv.error_rate.toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>p95 Latency</div>
                    <div style={{ fontWeight: 600, color: srv.latency_p95_ms > 2000 ? '#f87171' : 'var(--text-primary)' }}>
                      {srv.latency_p95_ms.toFixed(0)} ms
                    </div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>CPU Usage</div>
                    <div style={{ fontWeight: 600 }}>{srv.cpu_percent.toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Telemetry Charts & Recent Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Error Rate Trends Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Activity size={16} color="#f97316" />
              Service Error Rate & Anomaly Spikes
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Last 2 Hours (Rolling 5m)</span>
          </div>
          <div style={{ height: '260px', width: '100%' }}>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
                  <XAxis dataKey="time" stroke="#6b7280" fontSize={11} />
                  <YAxis stroke="#6b7280" fontSize={11} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#171f30', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
                  />
                  <Line type="monotone" dataKey="api-gateway" stroke="#ef4444" strokeWidth={2} dot={false} name="API Gateway" />
                  <Line type="monotone" dataKey="order-db" stroke="#f59e0b" strokeWidth={2} dot={false} name="Order DB" />
                  <Line type="monotone" dataKey="notification-service" stroke="#10b981" strokeWidth={1.5} dot={false} name="Notification" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                No time-series data available.
              </div>
            )}
          </div>
        </div>

        {/* Active Incidents Ticker */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <AlertCircle size={16} color="#ef4444" />
              Active Incident Queue
            </div>
            <button className="btn btn-secondary" onClick={() => onNavigateTab('incidents')} style={{ fontSize: '11px', padding: '3px 8px' }}>
              View All
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {activeIncidents.slice(0, 4).map((inc) => (
              <div
                key={inc.id}
                onClick={() => {
                  onSelectIncident(inc.id);
                  onNavigateTab('investigation');
                }}
                style={{
                  padding: '10px 12px',
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '6px',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className={`badge badge-${inc.severity.toLowerCase()}`}>{inc.severity}</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {new Date(inc.detection_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div style={{ fontWeight: 600, fontSize: '13px', color: '#fff', marginBottom: '4px' }}>
                  {inc.title}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                  Service: <span className="mono">{inc.affected_service_id}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Log Stream */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Clock size={16} color="#06b6d4" />
            Recent Audit & Operational Actions
          </div>
          <button className="btn btn-secondary" onClick={() => onNavigateTab('audit')} style={{ fontSize: '11px', padding: '3px 8px' }}>
            Full Audit Log
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>Actor</th>
                <th>Resource</th>
                <th>Action Summary</th>
              </tr>
            </thead>
            <tbody>
              {auditEvents.slice(0, 5).map((evt) => (
                <tr key={evt.id}>
                  <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </td>
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: '10px' }}>
                      {evt.event_type}
                    </span>
                  </td>
                  <td className="mono" style={{ fontSize: '12px' }}>{evt.actor}</td>
                  <td className="mono" style={{ fontSize: '12px' }}>{evt.resource_type}:{evt.resource_id}</td>
                  <td>{evt.action_summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
