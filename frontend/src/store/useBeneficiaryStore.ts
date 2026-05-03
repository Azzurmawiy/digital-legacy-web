import { create } from 'zustand';
import { apiClient } from '../api/axios';
import toast from 'react-hot-toast';
import axios from 'axios';

interface Beneficiary {
  id: string;
  name: string;
  email: string;
  relationship: string;
  permissions: Record<string, boolean>;
  created_at: string;
}

interface BeneficiaryState {
  beneficiaries: Beneficiary[];
  isLoading: boolean;
  error: string | null;
  fetch: () => Promise<void>;
  add: (data: Omit<Beneficiary, 'id' | 'created_at'>) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

export const useBeneficiaryStore = create<BeneficiaryState>((set) => ({
  beneficiaries: [],
  isLoading: false,
  error: null,

  fetch: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get('/beneficiaries/');
      const data = response.data?.data || response.data?.results || response.data;
      set({ beneficiaries: Array.isArray(data) ? data : [], isLoading: false });
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to load beneficiaries');
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  },

  add: async (formData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.post('/beneficiaries/', formData);
      const newItem = response.data?.data || response.data;
      set((state) => ({ beneficiaries: [newItem, ...state.beneficiaries], isLoading: false }));
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to add beneficiary');
      set({ error: msg, isLoading: false });
      toast.error(msg);
      throw new Error(msg, { cause: err });
    }
  },

  remove: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.delete(`/beneficiaries/${id}/`);
      set((state) => ({ beneficiaries: state.beneficiaries.filter((b) => b.id !== id), isLoading: false }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to remove beneficiary';
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  }
}));
