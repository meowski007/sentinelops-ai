import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';

describe('Navbar Component', () => {
  it('renders application title and AI Engine mode', () => {
    const health = {
      status: 'healthy',
      uptime_seconds: 120,
      ai_engine_mode: 'LOCAL_DETERMINISTIC',
    };

    render(<Navbar healthStatus={health} onRefresh={vi.fn()} />);

    expect(screen.getByText('SentinelOps AI')).toBeInTheDocument();
    expect(screen.getByText('LOCAL_DETERMINISTIC')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });
});

describe('Sidebar Component', () => {
  it('renders all navigation tabs with incident badge count', () => {
    render(
      <Sidebar
        activeTab="overview"
        setActiveTab={vi.fn()}
        openIncidentsCount={4}
      />
    );

    expect(screen.getByText('Operations Overview')).toBeInTheDocument();
    expect(screen.getByText('Incident Explorer')).toBeInTheDocument();
    expect(screen.getByText('AI Investigation')).toBeInTheDocument();
    expect(screen.getByText('Remediation Review')).toBeInTheDocument();
    expect(screen.getByText('Runbook Knowledge Base')).toBeInTheDocument();
    expect(screen.getByText('Audit & Compliance Log')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument(); // Badge count
  });
});
