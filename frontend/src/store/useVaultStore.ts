import { create } from 'zustand';
import { apiClient } from '../api/axios';
import toast from 'react-hot-toast';
import axios from 'axios';

export type VaultItem = {
  id: string;
  title: string;
  description: string;
  item_type: string;
  file_size: number;
  mime_type: string;
  original_filename: string;
  is_encrypted: boolean;
  uploaded_at: string;
  tags: string[];
}

interface VaultState {
  items: VaultItem[];
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  fetch: () => Promise<void>;
  upload: (data: FormData) => Promise<void>;
  remove: (id: string) => Promise<void>;
  update: (id: string, data: Partial<VaultItem>) => Promise<void>;
}

export const useVaultStore = create<VaultState>((set) => ({
  items: [],
  isLoading: false,
  isUploading: false,
  error: null,

  fetch: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get('/vault/items/');
      const data = response.data?.data || response.data?.results || response.data;
      set({ items: Array.isArray(data) ? data : [], isLoading: false });
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Failed to load vault items');
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  },

  upload: async (formData) => {
    set({ isUploading: true, error: null });
    try {
      const response = await apiClient.post('/vault/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const newItem = response.data?.data || response.data;
      set((state) => ({ items: [newItem, ...state.items], isUploading: false }));
    } catch (err: unknown) {
      const msg = axios.isAxiosError(err) ? (err.response?.data?.error?.message || err.message) : (err instanceof Error ? err.message : 'Upload failed');
      set({ error: msg, isUploading: false });
      toast.error(msg);
      throw new Error(msg, { cause: err });
    }
  },

  remove: async (id) => {
    try {
      await apiClient.delete(`/vault/items/${id}/delete/`);
      set((state) => ({ items: state.items.filter((i) => i.id !== id) }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete item';
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  },

  update: async (id, data) => {
    set({ isLoading: true });
    try {
      await apiClient.patch(`/vault/items/${id}/`, data);
      set((state) => ({
        items: state.items.map(i => i.id === id ? { ...i, ...data } : i),
        isLoading: false
      }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update item';
      set({ error: msg, isLoading: false });
      toast.error(msg);
    }
  }
}));
