import React, { useState, useEffect } from 'react';
import { api } from './api/client';
import { Incident, MetricsOverviewResponse, AuditEvent } from './types';
import { Navbar } from './components/Navbar';
import { Sidebar, ActiveTab } from './components/Sidebar';
import { OverviewView } from './components/OverviewView';
import { IncidentExplorerView } from './components/IncidentExplorerView';
import { InvestigationView } from './components/InvestigationView';
import { RemediationView } from './components/RemediationView';
import { KnowledgeBaseView } from './components/KnowledgeBaseView';
import { AuditHistoryView } from './components/AuditHistoryView';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [metrics, setMetrics] = useState<MetricsOverviewResponse | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [health, setHealth] = useState<{ status: string; uptime_seconds: number; ai_engine_mode: string } | null>(null);

  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [remediationPrefill, setRemediationPrefill] = useState<{
    actionName: string;
    justification: string;
    riskLevel: string;
  } | null>(null);

  const [initialLoading, setInitialLoading] = useState(true);

  const loadData = async () => {
    try {
      const [h, incs, m, aud] = await Promise.all([
        api.getHealth().catch(() => ({ status: 'degraded', uptime_seconds: 0, ai_engine_mode: 'LOCAL_DETERMINISTIC' })),
        api.getIncidents().catch(() => []),
        api.getMetricsOverview().catch(() => null),
        api.getAuditEvents().catch(() => []),
      ]);
      setHealth(h);
      setIncidents(incs);
      setMetrics(m);
      setAuditEvents(aud);
      if (incs.length > 0 && !selectedIncidentId) {
        setSelectedIncidentId(incs[0].id);
      }
    } finally {
      setInitialLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Auto-refresh telemetry every 30s
    const timer = setInterval(loadData, 30000);
    return () => clearInterval(timer);
  }, []);

  const openIncidentsCount = incidents.filter((i) => i.status !== 'RESOLVED').length;

  const handleNavigateInvestigation = (incidentId: string) => {
    setSelectedIncidentId(incidentId);
    setActiveTab('investigation');
  };

  const handleNavigateRemediation = (
    incidentId: string,
    actionName: string,
    justification: string,
    riskLevel: string
  ) => {
    setSelectedIncidentId(incidentId);
    setRemediationPrefill({ actionName, justification, riskLevel });
    setActiveTab('remediation');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Synthetic Environment Notice Banner */}
      <div className="synthetic-banner">
        <div>
          <strong>SIMULATED ENTERPRISE IT ENVIRONMENT:</strong> Telemetry, logs, incidents, and runbooks are synthetic demo records generated with fixed seed 42. No real cloud resources are modified.
        </div>
        <div style={{ color: '#a5b4fc', fontSize: '11px' }}>
          Grounded Citations Enforced &bull; Approval Gates Active
        </div>
      </div>

      <Navbar healthStatus={health} onRefresh={loadData} />

      <div className="app-container" style={{ flex: 1 }}>
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          openIncidentsCount={openIncidentsCount}
        />

        <main className="main-content">
          {initialLoading && (
            <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Loading SentinelOps Telemetry & Incident State...
            </div>
          )}

          {!initialLoading && (
            <>
              {activeTab === 'overview' && (
                <OverviewView
                  metrics={metrics}
                  incidents={incidents}
                  auditEvents={auditEvents}
                  onSelectIncident={(id) => setSelectedIncidentId(id)}
                  onNavigateTab={setActiveTab}
                />
              )}

              {activeTab === 'incidents' && (
                <IncidentExplorerView
                  incidents={incidents}
                  selectedIncidentId={selectedIncidentId}
                  onSelectIncident={(id) => setSelectedIncidentId(id)}
                  onNavigateInvestigation={handleNavigateInvestigation}
                  onRefresh={loadData}
                />
              )}

              {activeTab === 'investigation' && (
                <InvestigationView
                  incidents={incidents}
                  selectedIncidentId={selectedIncidentId}
                  onSelectIncident={(id) => setSelectedIncidentId(id)}
                  onNavigateRemediation={handleNavigateRemediation}
                />
              )}

              {activeTab === 'remediation' && (
                <RemediationView
                  incidents={incidents}
                  selectedIncidentId={selectedIncidentId}
                  proposedActionPrefill={remediationPrefill}
                  onRefreshAll={loadData}
                />
              )}

              {activeTab === 'knowledge' && <KnowledgeBaseView />}

              {activeTab === 'audit' && <AuditHistoryView />}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
