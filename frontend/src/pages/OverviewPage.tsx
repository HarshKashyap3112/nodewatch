import React, { useState } from 'react';
import { ServerItem } from '../api/servers';
import { StatusBadge } from '../components/StatusBadge';
import { formatLocalTime } from '../utils/date';
import { Server, Search, Cpu, HardDrive, Activity, ChevronRight, Trash2, ShieldCheck, AlertTriangle } from 'lucide-react';

interface OverviewPageProps {
  servers: ServerItem[];
  onSelectServer: (server: ServerItem) => void;
  onDeleteServer: (serverId: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ servers, onSelectServer, onDeleteServer }) => {
  const [search, setSearch] = useState('');

  const counts = {
    total: servers.length,
    healthy: servers.filter((s) => s.status === 'healthy').length,
    warning: servers.filter((s) => s.status === 'warning').length,
    critical: servers.filter((s) => s.status === 'critical').length,
    offline: servers.filter((s) => s.status === 'offline').length,
  };

  const filteredServers = servers.filter((s) =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    (s.hostname && s.hostname.toLowerCase().includes(search.toLowerCase())) ||
    (s.ip_address && s.ip_address.includes(search))
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Fleet Summary KPI Grid */}
      <div className="grid-cols-4">
        <div className="panel-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'var(--bg-accent)', color: 'var(--color-brand)' }}>
            <Server size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Monitored</div>
            <div className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {counts.total}
            </div>
          </div>
        </div>

        <div className="panel-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'var(--color-healthy-bg)', color: 'var(--color-healthy)' }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Healthy</div>
            <div className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-healthy)' }}>
              {counts.healthy}
            </div>
          </div>
        </div>

        <div className="panel-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical)' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Critical / Warning</div>
            <div className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-critical)' }}>
              {counts.critical + counts.warning}
            </div>
          </div>
        </div>

        <div className="panel-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'var(--color-offline-bg)', color: 'var(--color-offline)' }}>
            <Activity size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Offline</div>
            <div className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--color-offline)' }}>
              {counts.offline}
            </div>
          </div>
        </div>
      </div>

      {/* Filter and List Section */}
      <div className="panel-card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ position: 'relative', width: '320px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              className="input-field"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '0.85rem' }}
              placeholder="Search by server name, hostname, IP..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <span style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
            Showing {filteredServers.length} of {servers.length} servers
          </span>
        </div>

        {filteredServers.length === 0 ? (
          <div style={{ padding: '48px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Server size={36} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
            <div style={{ fontSize: '0.95rem', fontWeight: 500 }}>No servers found</div>
            <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>
              {servers.length === 0 ? 'Click "Add Server" in the top bar to connect your first agent.' : 'No servers match your search query.'}
            </div>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Server Name</th>
                <th>Hostname / IP</th>
                <th>OS Environment</th>
                <th>Last Heartbeat</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredServers.map((server) => (
                <tr key={server.id} style={{ cursor: 'pointer' }} onClick={() => onSelectServer(server)}>
                  <td>
                    <StatusBadge status={server.status} size="sm" />
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{server.name}</div>
                  </td>
                  <td>
                    <div className="font-mono" style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                      {server.hostname || 'N/A'} {server.ip_address ? `(${server.ip_address})` : ''}
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                      {server.os_info || 'Unknown OS'}
                    </div>
                  </td>
                  <td>
                    <div className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {formatLocalTime(server.last_seen_at)}
                    </div>
                  </td>
                  <td style={{ textAlign: 'right' }} onClick={(e) => e.stopPropagation()}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={() => onSelectServer(server)}
                      >
                        <span>Inspect</span>
                        <ChevronRight size={14} />
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={() => {
                          if (confirm(`Remove server '${server.name}'?`)) {
                            onDeleteServer(server.id);
                          }
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
