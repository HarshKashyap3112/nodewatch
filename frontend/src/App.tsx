import React, { useEffect, useState } from 'react';
import { User, authApi } from './api/auth';
import { ServerItem, serversApi } from './api/servers';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { AddServerModal } from './components/AddServerModal';
import { EditProfileModal } from './components/EditProfileModal';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { OverviewPage } from './pages/OverviewPage';
import { ServerDetailPage } from './pages/ServerDetailPage';
import { AlertsPage } from './pages/AlertsPage';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [loadingUser, setLoadingUser] = useState(true);

  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedServer, setSelectedServer] = useState<ServerItem | null>(null);
  const [servers, setServers] = useState<ServerItem[]>([]);
  const [isAddServerOpen, setIsAddServerOpen] = useState(false);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);

  const checkAuth = async () => {
    const token = localStorage.getItem('smp_access_token');
    if (!token) {
      setUser(null);
      setLoadingUser(false);
      return;
    }

    try {
      const u = await authApi.getMe();
      setUser(u);
      fetchServers();
    } catch (err) {
      setUser(null);
    } finally {
      setLoadingUser(false);
    }
  };

  const fetchServers = async () => {
    try {
      const list = await serversApi.listServers();
      setServers(list);
    } catch (err) {
      console.error('Failed to fetch servers list:', err);
    }
  };

  useEffect(() => {
    checkAuth();

    const handleUnauthorized = () => {
      setUser(null);
    };
    window.addEventListener('smp_unauthorized', handleUnauthorized);
    return () => window.removeEventListener('smp_unauthorized', handleUnauthorized);
  }, []);

  useEffect(() => {
    if (!user) return;
    const interval = setInterval(fetchServers, 10000);
    return () => clearInterval(interval);
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem('smp_access_token');
    setUser(null);
    setSelectedServer(null);
  };

  const handleDeleteServer = async (serverId: string) => {
    try {
      await serversApi.deleteServer(serverId);
      if (selectedServer?.id === serverId) {
        setSelectedServer(null);
      }
      fetchServers();
    } catch (err) {
      alert('Failed to remove server');
    }
  };

  if (loadingUser) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-primary)', color: 'var(--text-muted)' }}>
        <div style={{ fontSize: '1rem', fontWeight: 500 }}>Connecting to NodeWatch Core...</div>
      </div>
    );
  }

  if (!user) {
    if (authMode === 'login') {
      return (
        <LoginPage
          onLoginSuccess={checkAuth}
          onSwitchToRegister={() => setAuthMode('register')}
        />
      );
    } else {
      return (
        <RegisterPage
          onRegisterSuccess={checkAuth}
          onSwitchToLogin={() => setAuthMode('login')}
        />
      );
    }
  }

  const getPageTitle = () => {
    if (selectedServer) {
      return `Server Details: ${selectedServer.name}`;
    }
    switch (activeTab) {
      case 'overview':
        return 'Infrastructure Fleet Overview';
      case 'alerts':
        return 'Alert Threshold Rules';
      case 'active-alerts':
        return 'Active & Historical Alerts';
      default:
        return 'Dashboard';
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        activeTab={selectedServer ? '' : activeTab}
        setActiveTab={(tab) => {
          setSelectedServer(null);
          setActiveTab(tab);
        }}
      />

      <div className="main-content">
        <TopBar
          user={user}
          onLogout={handleLogout}
          onRefresh={fetchServers}
          onAddServer={() => setIsAddServerOpen(true)}
          onEditProfile={() => setIsEditProfileOpen(true)}
          title={getPageTitle()}
        />

        <main className="page-container">
          {selectedServer ? (
            <ServerDetailPage
              server={selectedServer}
              onBack={() => setSelectedServer(null)}
            />
          ) : activeTab === 'overview' ? (
            <OverviewPage
              servers={servers}
              onSelectServer={(s) => setSelectedServer(s)}
              onDeleteServer={handleDeleteServer}
            />
          ) : (
            <AlertsPage servers={servers} />
          )}
        </main>
      </div>

      <AddServerModal
        isOpen={isAddServerOpen}
        onClose={() => setIsAddServerOpen(false)}
        onSuccess={fetchServers}
      />

      <EditProfileModal
        isOpen={isEditProfileOpen}
        user={user}
        onClose={() => setIsEditProfileOpen(false)}
        onSuccess={(updatedUser) => {
          setUser(updatedUser);
        }}
      />
    </div>
  );
};

export default App;
