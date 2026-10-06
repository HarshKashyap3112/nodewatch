import React, { useState } from 'react';
import { X, Copy, Check, Terminal, Server } from 'lucide-react';
import { ServerWithKey, serversApi } from '../api/servers';

interface AddServerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddServerModal: React.FC<AddServerModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [hostname, setHostname] = useState('');
  const [loading, setLoading] = useState(false);
  const [createdResult, setCreatedResult] = useState<ServerWithKey | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await serversApi.createServer({ name, hostname });
      setCreatedResult(res);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create server');
    } finally {
      setLoading(false);
    }
  };

  const getAgentCommand = () => {
    if (!createdResult) return '';
    const serverUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/api\/v1\/?$/, '');
    return `python agent/main.py --server ${serverUrl} --api-key ${createdResult.api_key.raw_api_key} --interval 30`;
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(getAgentCommand());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={20} style={{ color: 'var(--color-brand)' }} />
            Add Monitored Server
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

        {!createdResult ? (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Server Name *
              </label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. prod-db-primary"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Hostname / FQDN (Optional)
              </label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. db01.infra.local"
                value={hostname}
                onChange={(e) => setHostname(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '12px' }}>
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Creating...' : 'Register Server & Issue Key'}
              </button>
            </div>
          </form>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: 'var(--color-healthy-bg)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--color-healthy)', fontSize: '0.875rem' }}>
              Server registered successfully! API key generated.
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                Generated Agent API Key (Save key - shown once)
              </label>
              <input
                type="text"
                readOnly
                className="input-field font-mono"
                value={createdResult.api_key.raw_api_key}
                style={{ color: 'var(--color-brand)' }}
              />
            </div>

            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 500 }}>
                <Terminal size={16} /> Run Agent CLI Command on Server
              </label>
              <div
                className="font-mono"
                style={{
                  padding: '12px',
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  color: '#e5e7eb',
                  wordBreak: 'break-all',
                  position: 'relative'
                }}
              >
                {getAgentCommand()}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
              <button className="btn btn-secondary" onClick={copyToClipboard}>
                {copied ? <Check size={16} style={{ color: 'var(--color-healthy)' }} /> : <Copy size={16} />}
                <span>{copied ? 'Copied Command!' : 'Copy Launch Command'}</span>
              </button>
              <button className="btn btn-primary" onClick={onClose}>
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
