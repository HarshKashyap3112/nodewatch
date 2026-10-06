import { apiClient } from './client';

export type AlertState = 'triggered' | 'resolved' | 'acknowledged';
export type Operator = '>' | '>=' | '<' | '<=' | '==';

export interface AlertRule {
  id: string;
  name: string;
  server_id?: string;
  metric_name: string;
  operator: Operator;
  threshold: number;
  duration_seconds: number;
  is_enabled: boolean;
  webhook_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AlertItem {
  id: string;
  rule_id: string;
  server_id: string;
  state: AlertState;
  metric_name: string;
  current_value: number;
  threshold_value: number;
  message: string;
  triggered_at: string;
  resolved_at?: string;
  created_at: string;
}

export const alertsApi = {
  async listRules() {
    const res = await apiClient.get<AlertRule[]>('/alerts/rules');
    return res.data;
  },

  async createRule(payload: {
    name: string;
    server_id?: string;
    metric_name: string;
    operator: Operator;
    threshold: number;
    duration_seconds?: number;
    webhook_url?: string;
  }) {
    const res = await apiClient.post<AlertRule>('/alerts/rules', payload);
    return res.data;
  },

  async updateRule(ruleId: string, payload: Partial<AlertRule>) {
    const res = await apiClient.patch<AlertRule>(`/alerts/rules/${ruleId}`, payload);
    return res.data;
  },

  async deleteRule(ruleId: string) {
    await apiClient.delete(`/alerts/rules/${ruleId}`);
  },

  async listAlerts(serverId?: string, state?: AlertState) {
    let url = '/alerts';
    const params = new URLSearchParams();
    if (serverId) params.append('server_id', serverId);
    if (state) params.append('state', state);
    if (params.toString()) url += `?${params.toString()}`;

    const res = await apiClient.get<AlertItem[]>(url);
    return res.data;
  },
};
