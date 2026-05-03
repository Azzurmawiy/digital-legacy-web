import { create } from 'zustand';
import { apiClient } from '../api/axios';
import toast from 'react-hot-toast';
import axios from 'axios';

interface DmsState {
  config: Record<string, unknown> | null;
  isLoading: boolean;
  error: string | null;
  fetchConfig: () => Promise<void>;
  updateConfig: (data: Record<string, unknown>) => Promise<void>;
  sendHeartbeat: () => Promise<void>;
}

export const useDmsStore = create<DmsState>((set) => ({
  config: null,
  isLoading: false,
  error: null,

  fetchConfig: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get('/dms/config/');
      const data = response.data?.data || response.data;
      set({ config: data, isLoading: false });
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to fetch DMS config');
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  },

  updateConfig: async (configData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.patch('/dms/config/', configData);
      const data = response.data?.data || response.data;
      set({ config: data, isLoading: false });
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to update DMS config');
      set({ error: msg, isLoading: false });
      toast.error(msg);
      throw err;
    }
  },

  sendHeartbeat: async () => {
    try {
      await apiClient.post('/dms/heartbeat/', { source: 'web' });
      // Refresh config to reflect updated status
      const response = await apiClient.get('/dms/config/');
      const data = response.data?.data || response.data;
      set({ config: data });
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to send heartbeat');
      set({ error: msg });
      toast.error(msg);
      throw err;
    }
  }
}));
