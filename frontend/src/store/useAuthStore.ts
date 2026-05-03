import { create } from 'zustand';
import { apiClient } from '../api/axios';
import toast from 'react-hot-toast';
import axios from 'axios';

interface AuthState {
  isAuthenticated: boolean;
  user: Record<string, unknown> | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: Record<string, unknown>) => Promise<void>;
  register: (data: Record<string, unknown>) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  user: null,
  isLoading: false,
  error: null,

  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      // Adjusted to use standard JWT auth logic structure
      const response = await apiClient.post('/auth/login/', credentials);
      const data = response.data;
      
      // Assumes DRF returns standard { access, refresh } or wrapped { success: true, data: { access, refresh } }
      const access = data.access || data.data?.access;
      const refresh = data.refresh || data.data?.refresh;
      
      if (access && refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        set({ isAuthenticated: true, isLoading: false });
      } else {
        set({ error: 'Invalid response from server', isLoading: false });
      }
    } catch (err: unknown) {
      const message = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.response?.data?.detail || 'Login failed') : (err instanceof Error ? err.message : 'Login failed');
      set({ error: message, isLoading: false });
      toast.error(message);
      throw err;
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.post('/auth/register/', userData);
      set({ isLoading: false });
    } catch (err: unknown) {
      const message = axios.isAxiosError(err) ? (err.response?.data?.detail || 'Registration failed') : (err instanceof Error ? err.message : 'Registration failed');
      set({ error: message, isLoading: false });
      toast.error(message);
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ isAuthenticated: false, user: null });
  },

  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    set({ isAuthenticated: !!token });
  }
}));
