import { create } from 'zustand';
import { apiClient } from '../api/axios';

export interface AuditEntry {
  id: number;
  action: string;
  detail: string;
  time: string;
  status: string;
  icon: string;
}

interface NotificationState {
  logs: AuditEntry[];
  isLoading: boolean;
  fetchLogs: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  logs: [],
  isLoading: false,
  fetchLogs: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get('/notifications/history/');
      const data = response.data?.data || [];
      set({ logs: data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch audit logs', err);
      set({ isLoading: false });
    }
  }
}));
