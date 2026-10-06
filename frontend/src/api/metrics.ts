import { apiClient } from './client';

export interface DataPoint {
  timestamp: string;
  value: number;
}

export interface MetricSeries {
  server_id: string;
  metric_name: string;
  data_points: DataPoint[];
}

export interface LatestMetricsSummary {
  server_id: string;
  metrics: Record<string, number>;
  last_updated?: string;
}

export const metricsApi = {
  async queryMetrics(serverId: string, metricName: string, range = '1h') {
    const res = await apiClient.get<MetricSeries>(
      `/metrics/query?server_id=${serverId}&metric_name=${metricName}&range=${range}`
    );
    return res.data;
  },

  async getLatestMetrics(serverId: string) {
    const res = await apiClient.get<LatestMetricsSummary>(`/metrics/latest/${serverId}`);
    return res.data;
  },
};
