import { apiClient } from './client';

export interface CheckResult {
  id: string;
  server_id: string;
  check_name: string;
  check_type: 'process_running' | 'port_open' | 'disk_space' | 'custom';
  status: 'pass' | 'fail' | 'unknown';
  message?: string;
  timestamp: string;
}

export const checksApi = {
  async getLatestChecks(serverId: string) {
    const res = await apiClient.get<CheckResult[]>(`/checks/latest/${serverId}`);
    return res.data;
  },
};
