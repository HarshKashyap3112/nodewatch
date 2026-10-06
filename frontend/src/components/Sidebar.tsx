import React from 'react';
import { Server, Bell, Key, Activity, ShieldAlert } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'overview', label: 'Fleet Overview', icon: Server },
    { id: 'alerts', label: 'Alert Rules', icon: Bell },
    { id: 'active-alerts', label: 'Active Alerts', icon: ShieldAlert },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <Activity className="w-6 h-6 text-blue-500" style={{ color: '#3b82f6' }} />
        <span className="brand-title">NodeWatch SMP</span>
      </div>

      <nav className="nav-section">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ marginTop: 'auto', padding: '16px', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <div>Server Monitoring Platform</div>
          <div className="font-mono" style={{ marginTop: '2px', color: 'var(--text-secondary)' }}>v1.0.0 (Phase 1)</div>
        </div>
      </div>
    </aside>
  );
};
