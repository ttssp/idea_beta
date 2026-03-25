'use client';

import { create } from 'zustand';
import type { Thread } from '@/lib/types/thread';

interface ThreadState {
  threads: Thread[];
  selectedThreadId: string | null;
  loading: boolean;
  error: string | null;

  // Actions
  setThreads: (threads: Thread[]) => void;
  setSelectedThreadId: (id: string | null) => void;
  updateThread: (id: string, updates: Partial<Thread>) => void;
  addThread: (thread: Thread) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useThreadStore = create<ThreadState>((set) => ({
  threads: [],
  selectedThreadId: null,
  loading: false,
  error: null,

  setThreads: (threads) => set({ threads }),
  setSelectedThreadId: (id) => set({ selectedThreadId: id }),
  updateThread: (id, updates) =>
    set((state) => ({
      threads: state.threads.map((t) => (t.id === id ? { ...t, ...updates } : t)),
    })),
  addThread: (thread) => set((state) => ({ threads: [thread, ...state.threads] })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
