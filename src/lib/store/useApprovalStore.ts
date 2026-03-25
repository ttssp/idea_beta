'use client';

import { create } from 'zustand';
import type { ApprovalRequest } from '@/lib/types/approval';

interface ApprovalState {
  approvals: ApprovalRequest[];
  loading: boolean;
  error: string | null;

  // Actions
  setApprovals: (approvals: ApprovalRequest[]) => void;
  updateApproval: (id: string, updates: Partial<ApprovalRequest>) => void;
  removeApproval: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useApprovalStore = create<ApprovalState>((set) => ({
  approvals: [],
  loading: false,
  error: null,

  setApprovals: (approvals) => set({ approvals }),
  updateApproval: (id, updates) =>
    set((state) => ({
      approvals: state.approvals.map((a) => (a.id === id ? { ...a, ...updates } : a)),
    })),
  removeApproval: (id) =>
    set((state) => ({
      approvals: state.approvals.filter((a) => a.id !== id),
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
