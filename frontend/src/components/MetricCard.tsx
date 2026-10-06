import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number | string;
  unit: string;
  icon: LucideIcon;
  subtext?: string;
  percent?: number;
  color?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  icon: Icon,
  subtext,
  percent,
  color = '#3b82f6'
}) => {
  return (
    <div className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.825rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{title}</span>
        <div
          style={{
            padding: '6px',
            borderRadius: '6px',
            backgroundColor: 'var(--bg-accent)',
            color: color
          }}
        >
          <Icon size={18} />
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
        <span className="font-mono" style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {value}
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{unit}</span>
      </div>

      {percent !== undefined && (
        <div style={{ marginTop: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.725rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            <span>Utilization</span>
            <span className="font-mono">{percent.toFixed(1)}%</span>
          </div>
          <div style={{ height: '6px', backgroundColor: 'var(--bg-primary)', borderRadius: '3px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${Math.min(Math.max(percent, 0), 100)}%`,
                backgroundColor: percent > 85 ? 'var(--color-critical)' : percent > 70 ? 'var(--color-warning)' : color,
                borderRadius: '3px',
                transition: 'width 0.4s ease'
              }}
            />
          </div>
        </div>
      )}

      {subtext && !percent && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 'auto' }}>
          {subtext}
        </div>
      )}
    </div>
  );
};
