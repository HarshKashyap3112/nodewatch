import React from 'react';
import { ServerStatus } from '../api/servers';

interface StatusBadgeProps {
  status: ServerStatus;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const getStatusClass = () => {
    switch (status) {
      case 'healthy':
        return 'status-healthy';
      case 'warning':
        return 'status-warning';
      case 'critical':
        return 'status-critical';
      case 'offline':
      default:
        return 'status-offline';
    }
  };

  const getLabel = () => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <span className={`status-pill ${getStatusClass()}`} style={{ fontSize: size === 'sm' ? '0.7rem' : '0.75rem' }}>
      <span className="pulse-dot" />
      {getLabel()}
    </span>
  );
};
