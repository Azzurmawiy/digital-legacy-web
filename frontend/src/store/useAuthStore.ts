import { create } from 'zustand';
import { apiClient } from '../api/axios';
import toast from 'react-hot-toast';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
}

interface ActivityItem {
  icon: string;
  title: string;
  sub: string;
  time: string;
}

interface DashboardStats {
  vault_count: number;
  vault_size_mb: number;
  beneficiary_count: number;
  dms_status: string;
  dms_days_left: number;
  dms_threshold: number;
  memories_count: number;
  safety_score: number;
  recent_activity?: ActivityItem[];
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  stats: DashboardStats | null;
  isLoading: boolean;
  isInitializing: boolean;
  error: string | null;
  login: (credentials: Record<string, unknown>) => Promise<any>;
  register: (data: Record<string, unknown>) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  fetchStats: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  user: null,
  stats: null,
  isLoading: false,
  isInitializing: true,
  error: null,

  fetchStats: async () => {
    try {
      const response = await apiClient.get('/auth/stats/');
      set({ stats: response.data?.data || response.data });
    } catch (err) {
      console.error('Failed to fetch stats', err);
    }
  },

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
        set({ 
          isAuthenticated: true, 
          user: data.user || data.data?.user, 
          isLoading: false 
        });
      } else {
        set({ isLoading: false });
      }
      return data.data || data;
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
    set({ isAuthenticated: false, user: null, stats: null });
  },

  fetchUser: async () => {
    try {
      const response = await apiClient.get('/auth/profile/');
      const userData = response.data?.data || response.data;
      set({ user: userData, isAuthenticated: true });
    } catch (err) {
      console.error('Failed to fetch user', err);
      // If we can't fetch the user, the token is likely invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ isAuthenticated: false, user: null });
    }
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null, isInitializing: false });
      return;
    }

    // Attempt to fetch user to verify token
    try {
      const response = await apiClient.get('/auth/profile/');
      const userData = response.data?.data || response.data;
      set({ user: userData, isAuthenticated: true, isInitializing: false });
    } catch (err) {
      console.error('CheckAuth failed:', err);
      set({ isAuthenticated: false, user: null, isInitializing: false });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }
}));
