import { apiClient } from './client';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'owner' | 'viewer';
  created_at: string;
  updated_at: string;
}

export const authApi = {
  async register(data: { email: string; password: string; full_name?: string }) {
    const res = await apiClient.post<User>('/auth/register', data);
    return res.data;
  },

  async login(data: { email: string; password: string }) {
    const res = await apiClient.post<{ access_token: string }>('/auth/login', data);
    return res.data;
  },

  async getMe() {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  async updateMe(data: { full_name?: string; password?: string }) {
    const res = await apiClient.patch<User>('/auth/me', data);
    return res.data;
  },

  async resetPassword(data: { email: string; reset_secret_key: string; new_password: string }) {
    const res = await apiClient.post<User>('/auth/reset-password', data);
    return res.data;
  },
};
