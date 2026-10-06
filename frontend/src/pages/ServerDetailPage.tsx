import React, { useEffect, useState } from 'react';
import { ServerItem } from '../api/servers';
import { metricsApi, MetricSeries, LatestMetricsSummary } from '../api/metrics';
import { checksApi, CheckResult } from '../api/checks';
import { alertsApi, AlertItem } from '../api/alerts';
import { StatusBadge } from '../components/StatusBadge';
import { MetricCard } from '../components/MetricCard';
import { MetricChart } from '../components/MetricChart';
import { formatLocalDateTime } from '../utils/date';
import { ArrowLeft, Cpu, HardDrive, Activity, Wifi, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';

interface ServerDetailPageProps {
  server: ServerItem;
  onBack: () => void;
}

export const ServerDetailPage: React.FC<ServerDetailPageProps> = ({ server, onBack }) => {
  const [timeRange, setTimeRange] = useState('1h');
  const [loading, setLoading] = useState(true);

  const [latestSummary, setLatestSummary] = useState<LatestMetricsSummary | null>(null);
  const [cpuSeries, setCpuSeries] = useState<MetricSeries | null>(null);
  const [memSeries, setMemSeries] = useState<MetricSeries | null>(null);
  const [diskSeries, setDiskSeries] = useState<MetricSeries | null>(null);
  const [netSentSeries, setNetSentSeries] = useState<MetricSeries | null>(null);
  const [checks, setChecks] = useState<CheckResult[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sum, cpu, mem, disk, netSent, checkList, alertList] = await Promise.all([
        metricsApi.getLatestMetrics(server.id),
        metricsApi.queryMetrics(server.id, 'cpu_usage_percent', timeRange),
        metricsApi.queryMetrics(server.id, 'memory_usage_percent', timeRange),
        metricsApi.queryMetrics(server.id, 'disk_usage_percent', timeRange),
        metricsApi.queryMetrics(server.id, 'net_bytes_sent', timeRange),
        checksApi.getLatestChecks(server.id),
        alertsApi.listAlerts(server.id),
      ]);

      setLatestSummary(sum);
      setCpuSeries(cpu);
      setMemSeries(mem);
      setDiskSeries(disk);
      setNetSentSeries(netSent);
      setChecks(checkList);
      setAlerts(alertList);
    } catch (err) {
      console.error('Error fetching server details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, [server.id, timeRange]);

  const currentCpu = latestSummary?.metrics['cpu_usage_percent'] ?? 0;
  const currentMem = latestSummary?.metrics['memory_usage_percent'] ?? 0;
  const currentDisk = latestSummary?.metrics['disk_usage_percent'] ?? 0;
  const currentNetSent = latestSummary?.metrics['net_bytes_sent'] ?? 0;
  const currentNetRecv = latestSummary?.metrics['net_bytes_recv'] ?? 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Detail Header */}
      <div className="panel-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={onBack}>
            <ArrowLeft size={16} />
            <span>Back to Fleet</span>
          </button>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-primary)' }}>{server.name}</h2>
              <StatusBadge status={server.status} />
            </div>
            <div className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              {server.hostname || 'No Hostname'} • IP: {server.ip_address || 'Unknown'} • OS: {server.os_info || 'Linux'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Range:</span>
          {['1h', '6h', '24h', '7d'].map((r) => (
            <button
              key={r}
              className={`btn ${timeRange === r ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
              onClick={() => setTimeRange(r)}
            >
              {r}
            </button>
          ))}
          <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={loadData} title="Reload">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Real-time KPI Metric Summary Cards */}
      <div className="grid-cols-4">
        <MetricCard
          title="CPU Utilization"
          value={currentCpu.toFixed(1)}
          unit="%"
          percent={currentCpu}
          icon={Cpu}
          color="#3b82f6"
        />

        <MetricCard
          title="Memory Utilization"
          value={currentMem.toFixed(1)}
          unit="%"
          percent={currentMem}
          icon={Activity}
          color="#10b981"
        />

        <MetricCard
          title="Disk Storage"
          value={currentDisk.toFixed(1)}
          unit="%"
          percent={currentDisk}
          icon={HardDrive}
          color="#f59e0b"
        />

        <MetricCard
          title="Network Traffic"
          value={(currentNetSent / 1024).toFixed(1)}
          unit="KB/s Out"
          subtext={`Recv: ${(currentNetRecv / 1024).toFixed(1)} KB/s`}
          icon={Wifi}
          color="#8b5cf6"
        />
      </div>

      {/* Time-Series Charts Grid */}
      <div className="grid-cols-2">
        <MetricChart
          title="CPU Usage Trend (%)"
          data={cpuSeries?.data_points || []}
          unit="%"
          color="#3b82f6"
        />

        <MetricChart
          title="Memory Usage Trend (%)"
          data={memSeries?.data_points || []}
          unit="%"
          color="#10b981"
        />

        <MetricChart
          title="Disk Space Usage (%)"
          data={diskSeries?.data_points || []}
          unit="%"
          color="#f59e0b"
        />

        <MetricChart
          title="Network Sent Rate (Bytes/sec)"
          data={netSentSeries?.data_points || []}
          unit="B/s"
          color="#8b5cf6"
        />
      </div>

      {/* Service Checks & Recent Alerts Split */}
      <div className="grid-cols-2">
        {/* Service Checks Table */}
        <div className="panel-card">
          <div className="panel-header">
            <h3 className="panel-title">
              <CheckCircle size={18} style={{ color: 'var(--color-healthy)' }} /> Service Checks
            </h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{checks.length} active checks</span>
          </div>

          {checks.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No service checks configured for this agent yet.
            </div>
          ) : (
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Check Name</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {checks.map((c) => (
                  <tr key={c.id}>
                    <td className="font-mono" style={{ fontSize: '0.825rem', fontWeight: 600 }}>{c.check_name}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.check_type}</td>
                    <td>
                      <span
                        className="status-pill"
                        style={{
                          fontSize: '0.7rem',
                          color: c.status === 'pass' ? 'var(--color-healthy)' : 'var(--color-critical)',
                          backgroundColor: c.status === 'pass' ? 'var(--color-healthy-bg)' : 'var(--color-critical-bg)'
                        }}
                      >
                        {c.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{c.message || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Server Alert Logs */}
        <div className="panel-card">
          <div className="panel-header">
            <h3 className="panel-title">
              <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} /> Recent Server Alerts
            </h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{alerts.length} historical alerts</span>
          </div>

          {alerts.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No alerts triggered for this server. All clear!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {alerts.map((a) => (
                <div
                  key={a.id}
                  style={{
                    padding: '12px 14px',
                    borderRadius: '8px',
                    backgroundColor: a.state === 'triggered' ? 'var(--color-critical-bg)' : 'var(--bg-primary)',
                    border: `1px solid ${a.state === 'triggered' ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-subtle)'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: a.state === 'triggered' ? 'var(--color-critical)' : 'var(--color-healthy)' }}>
                      {a.state.toUpperCase()}: {a.metric_name}
                    </span>
                    <span className="font-mono" style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      {formatLocalDateTime(a.triggered_at)}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{a.message}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
