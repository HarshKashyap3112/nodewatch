import { apiClient } from './client';

export type ServerStatus = 'healthy' | 'warning' | 'critical' | 'offline';

export interface ServerItem {
  id: string;
  name: string;
  hostname?: string;
  ip_address?: string;
  os_info?: string;
  status: ServerStatus;
  last_seen_at?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface ApiKeyCreated {
  id: string;
  server_id: string;
  name: string;
  is_revoked: boolean;
  raw_api_key: string;
  created_at: string;
}

export interface ServerWithKey {
  server: ServerItem;
  api_key: ApiKeyCreated;
}

export const serversApi = {
  async listServers() {
    const res = await apiClient.get<ServerItem[]>('/servers');
    return res.data;
  },

  async getServer(serverId: string) {
    const res = await apiClient.get<ServerItem>(`/servers/${serverId}`);
    return res.data;
  },

  async createServer(payload: { name: string; hostname?: string; ip_address?: string; os_info?: string }) {
    const res = await apiClient.post<ServerWithKey>('/servers', payload);
    return res.data;
  },

  async deleteServer(serverId: string) {
    await apiClient.delete(`/servers/${serverId}`);
  },

  async createApiKey(serverId: string, name = 'custom') {
    const res = await apiClient.post<ApiKeyCreated>(`/servers/${serverId}/keys?name=${encodeURIComponent(name)}`);
    return res.data;
  },

  async revokeApiKey(keyId: string) {
    await apiClient.delete(`/servers/keys/${keyId}`);
  },
};
