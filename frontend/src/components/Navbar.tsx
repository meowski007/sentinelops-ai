import React from 'react';
import { ShieldAlert, Server, Cpu, CheckCircle, AlertTriangle } from 'lucide-react';

interface NavbarProps {
  healthStatus: { status: string; uptime_seconds: number; ai_engine_mode: string } | null;
  onRefresh: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ healthStatus, onRefresh }) => {
  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          backgroundColor: '#3b82f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff'
        }}>
          <ShieldAlert size={18} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.2px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            SentinelOps AI
            <span className="badge badge-low" style={{ fontSize: '10px' }}>v1.0</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Enterprise IT Operations & Incident Response</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
          <Cpu size={14} color="#06b6d4" />
          <span>AI Engine:</span>
          <span style={{ color: '#06b6d4', fontWeight: 600 }}>
            {healthStatus?.ai_engine_mode || 'LOCAL_DETERMINISTIC'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
          <Server size={14} />
          <span>Backend:</span>
          {healthStatus?.status === 'healthy' ? (
            <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
              <CheckCircle size={12} /> Connected
            </span>
          ) : (
            <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
              <AlertTriangle size={12} /> Offline / Connecting
            </span>
          )}
        </div>

        <button className="btn btn-secondary" onClick={onRefresh} style={{ padding: '4px 10px', fontSize: '12px' }}>
          Refresh Telemetry
        </button>
      </div>
    </header>
  );
};
