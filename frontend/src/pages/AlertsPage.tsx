import React, { useEffect, useState } from 'react';
import { alertsApi, AlertRule, AlertItem } from '../api/alerts';
import { ServerItem } from '../api/servers';
import { AddRuleModal } from '../components/AddRuleModal';
import { formatLocalDateTime } from '../utils/date';
import { Bell, Plus, Trash2, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';

interface AlertsPageProps {
  servers: ServerItem[];
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ servers }) => {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rList, aList] = await Promise.all([alertsApi.listRules(), alertsApi.listAlerts()]);
      setRules(rList);
      setAlerts(aList);
    } catch (err) {
      console.error('Failed to load alert rules/feed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this alert rule?')) return;
    try {
      await alertsApi.deleteRule(ruleId);
      loadData();
    } catch (err) {
      alert('Failed to delete rule');
    }
  };

  const handleToggleRule = async (rule: AlertRule) => {
    try {
      await alertsApi.updateRule(rule.id, { is_enabled: !rule.is_enabled });
      loadData();
    } catch (err) {
      alert('Failed to toggle rule state');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Alert Rules Section */}
      <div className="panel-card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bell size={20} style={{ color: 'var(--color-warning)' }} /> Threshold Alert Rules
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Automatic rule evaluation scheduled every 30 seconds
            </p>
          </div>

          <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
            <Plus size={16} />
            <span>Create Rule</span>
          </button>
        </div>

        {rules.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Bell size={36} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
            <div style={{ fontSize: '0.95rem', fontWeight: 500 }}>No alert rules configured</div>
            <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>
              Click "Create Rule" to define threshold monitoring rules (e.g. CPU &gt; 90%).
            </div>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Rule Name</th>
                <th>Target Metric</th>
                <th>Condition Threshold</th>
                <th>Target Server</th>
                <th>Webhook Destination</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => {
                const targetServer = servers.find((s) => s.id === rule.server_id);
                return (
                  <tr key={rule.id}>
                    <td>
                      <button
                        className={`status-pill ${rule.is_enabled ? 'status-healthy' : 'status-offline'}`}
                        style={{ cursor: 'pointer', border: 'none' }}
                        onClick={() => handleToggleRule(rule)}
                        title="Click to toggle rule"
                      >
                        {rule.is_enabled ? 'ACTIVE' : 'DISABLED'}
                      </button>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{rule.name}</td>
                    <td className="font-mono" style={{ fontSize: '0.825rem', color: 'var(--color-brand)' }}>
                      {rule.metric_name}
                    </td>
                    <td className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                      {rule.operator} {rule.threshold}
                    </td>
                    <td style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                      {rule.server_id ? targetServer?.name || 'Specific Server' : 'Global (All Servers)'}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {rule.webhook_url ? 'Configured Webhook' : 'Default Channel'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={() => handleDeleteRule(rule.id)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Active & Past Alerts History Feed */}
      <div className="panel-card">
        <div className="panel-header">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={20} style={{ color: 'var(--color-critical)' }} /> System Alert History & Feed
          </h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{alerts.length} events logged</span>
        </div>

        {alerts.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            No alerts triggered. System operating normally!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
            {alerts.map((alertItem) => {
              const targetServer = servers.find((s) => s.id === alertItem.server_id);
              const isTriggered = alertItem.state === 'triggered';
              return (
                <div
                  key={alertItem.id}
                  style={{
                    padding: '14px 18px',
                    borderRadius: '10px',
                    backgroundColor: isTriggered ? 'var(--color-critical-bg)' : 'var(--bg-secondary)',
                    border: `1px solid ${isTriggered ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-subtle)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '16px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        padding: '8px',
                        borderRadius: '50%',
                        backgroundColor: isTriggered ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                        color: isTriggered ? 'var(--color-critical)' : 'var(--color-healthy)'
                      }}
                    >
                      {isTriggered ? <ShieldAlert size={20} /> : <CheckCircle2 size={20} />}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                          Server: {targetServer?.name || alertItem.server_id}
                        </span>
                        <span
                          className="status-pill"
                          style={{
                            fontSize: '0.7rem',
                            color: isTriggered ? 'var(--color-critical)' : 'var(--color-healthy)',
                            backgroundColor: isTriggered ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)'
                          }}
                        >
                          {alertItem.state.toUpperCase()}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        {alertItem.message}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px' }}>
                    <div className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} />
                      Triggered: {formatLocalDateTime(alertItem.triggered_at)}
                    </div>
                    {alertItem.resolved_at && (
                      <div className="font-mono" style={{ fontSize: '0.725rem', color: 'var(--color-healthy)' }}>
                        Resolved: {formatLocalDateTime(alertItem.resolved_at)}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Alert Rule Modal */}
      <AddRuleModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadData}
        servers={servers}
      />
    </div>
  );
};
