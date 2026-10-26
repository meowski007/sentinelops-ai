import React from 'react';
import { LayoutDashboard, AlertOctagon, Sparkles, Wrench, BookOpen, History } from 'lucide-react';

export type ActiveTab = 'overview' | 'incidents' | 'investigation' | 'remediation' | 'knowledge' | 'audit';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  openIncidentsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, openIncidentsCount }) => {
  const navItems = [
    { id: 'overview' as ActiveTab, label: 'Operations Overview', icon: LayoutDashboard },
    { id: 'incidents' as ActiveTab, label: 'Incident Explorer', icon: AlertOctagon, badge: openIncidentsCount },
    { id: 'investigation' as ActiveTab, label: 'AI Investigation', icon: Sparkles },
    { id: 'remediation' as ActiveTab, label: 'Remediation Review', icon: Wrench },
    { id: 'knowledge' as ActiveTab, label: 'Runbook Knowledge Base', icon: BookOpen },
    { id: 'audit' as ActiveTab, label: 'Audit & Compliance Log', icon: History },
  ];

  return (
    <aside className="sidebar">
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.8px' }}>
          Navigation
        </div>
      </div>

      <nav style={{ padding: '12px 10px', display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '6px',
                backgroundColor: isActive ? 'var(--bg-surface-hover)' : 'transparent',
                color: isActive ? '#fff' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '13px',
                border: isActive ? '1px solid var(--border-light)' : '1px solid transparent',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Icon size={16} color={isActive ? '#3b82f6' : 'currentColor'} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="badge badge-critical" style={{ fontSize: '10px', padding: '1px 6px' }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', fontSize: '11px', color: 'var(--text-muted)' }}>
        <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>Demo Sandbox</div>
        <div>Seed: 42 | Pure Local RAG</div>
        <div style={{ marginTop: '4px', color: '#60a5fa' }}>Portfolio Version 1.0</div>
      </div>
    </aside>
  );
};
