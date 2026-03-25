'use client';

import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  notificationsOpen: boolean;
  activeBucket: string | null;

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleNotifications: () => void;
  setNotificationsOpen: (open: boolean) => void;
  setActiveBucket: (bucket: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  notificationsOpen: false,
  activeBucket: null,

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleNotifications: () => set((state) => ({ notificationsOpen: !state.notificationsOpen })),
  setNotificationsOpen: (open) => set({ notificationsOpen: open }),
  setActiveBucket: (bucket) => set({ activeBucket: bucket }),
}));
