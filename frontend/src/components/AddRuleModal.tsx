import React, { useState } from 'react';
import { X, Bell } from 'lucide-react';
import { alertsApi, Operator } from '../api/alerts';
import { ServerItem } from '../api/servers';

interface AddRuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  servers: ServerItem[];
}

export const AddRuleModal: React.FC<AddRuleModalProps> = ({ isOpen, onClose, onSuccess, servers }) => {
  const [name, setName] = useState('');
  const [serverId, setServerId] = useState<string>('');
  const [metricName, setMetricName] = useState('cpu_usage_percent');
  const [operator, setOperator] = useState<Operator>('>');
  const [threshold, setThreshold] = useState<number>(85);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError('');

    try {
      await alertsApi.createRule({
        name,
        server_id: serverId || undefined,
        metric_name: metricName,
        operator,
        threshold: Number(threshold),
        webhook_url: webhookUrl || undefined,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create alert rule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={20} style={{ color: 'var(--color-warning)' }} />
            Create Threshold Alert Rule
          </h2>
          <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '10px 14px', borderRadius: '8px', backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical)', fontSize: '0.85rem', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
              Rule Name *
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. High CPU Threshold Alert"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Target Server
              </label>
              <select className="input-field" value={serverId} onChange={(e) => setServerId(e.target.value)}>
                <option value="">All Servers (Global Rule)</option>
                {servers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.hostname || 'No Hostname'})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Metric Target
              </label>
              <select className="input-field" value={metricName} onChange={(e) => setMetricName(e.target.value)}>
                <option value="cpu_usage_percent">CPU Usage (%)</option>
                <option value="memory_usage_percent">Memory Usage (%)</option>
                <option value="disk_usage_percent">Disk Usage (%)</option>
                <option value="net_bytes_sent">Network Sent (B/s)</option>
                <option value="net_bytes_recv">Network Received (B/s)</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Operator
              </label>
              <select className="input-field" value={operator} onChange={(e) => setOperator(e.target.value as Operator)}>
                <option value=">">Greater than (&gt;)</option>
                <option value=">=">Greater or equal (&gt;=)</option>
                <option value="<">Less than (&lt;)</option>
                <option value="<=">Less or equal (&lt;=)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Threshold Value *
              </label>
              <input
                type="number"
                step="any"
                className="input-field"
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
              Webhook Notification URL (Optional, Slack/Telegram/Discord)
            </label>
            <input
              type="url"
              className="input-field"
              placeholder="https://hooks.slack.com/services/..."
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
