import React from 'react';
import { User } from '../api/auth';
import { LogOut, RefreshCw, Plus, User as UserIcon, Settings } from 'lucide-react';

interface TopBarProps {
  user: User | null;
  onLogout: () => void;
  onRefresh: () => void;
  onAddServer: () => void;
  onEditProfile?: () => void;
  title: string;
}

export const TopBar: React.FC<TopBarProps> = ({
  user,
  onLogout,
  onRefresh,
  onAddServer,
  onEditProfile,
  title,
}) => {
  return (
    <header className="top-bar">
      <h1 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h1>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button className="btn btn-secondary" onClick={onRefresh} title="Refresh Data">
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>

        <button className="btn btn-primary" onClick={onAddServer}>
          <Plus size={16} />
          <span>Add Server</span>
        </button>

        <div style={{ height: '24px', width: '1px', backgroundColor: 'var(--border-color)', margin: '0 4px' }} />

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={onEditProfile}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                padding: '4px 8px',
                borderRadius: '8px',
                transition: 'background-color 0.15s ease',
              }}
              className="user-profile-btn"
              title="Edit Profile & Account Settings"
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--bg-accent)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-brand)',
                }}
              >
                <UserIcon size={18} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', fontSize: '0.825rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {user.full_name || user.email.split('@')[0]}
                  <Settings size={12} style={{ color: 'var(--text-muted)' }} />
                </span>
                <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>{user.role}</span>
              </div>
            </button>

            <button
              className="btn btn-secondary"
              onClick={onLogout}
              style={{ padding: '6px 10px', marginLeft: '4px' }}
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
