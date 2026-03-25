import { apiClient } from './client';
import type { Thread } from '@/lib/types/thread';
import type { ThreadEvent } from '@/lib/types/replay';
import { mockThreads, mockReplayEvents } from '@/mocks';
import { USE_MOCK_API } from '@/lib/utils/constants';

// Mock implementation
const mockApi = {
  getThreads: async (): Promise<Thread[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockThreads;
  },

  getThread: async (id: string): Promise<Thread | undefined> => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockThreads.find((t) => t.id === id);
  },

  createThread: async (data: Partial<Thread>): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const newThread: Thread = {
      id: `thread-${Date.now()}`,
      title: data.title || 'New Thread',
      objective: data.objective || '',
      status: 'new',
      ownerId: 'user-1',
      delegationProfile: data.delegationProfile || 'draft_first',
      riskLevel: 'low',
      currentResponsible: 'user-1',
      participants: data.participants || [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...data,
    };
    return newThread;
  },

  updateThread: async (id: string, data: Partial<Thread>): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const thread = mockThreads.find((t) => t.id === id);
    if (!thread) throw new Error('Thread not found');
    return { ...thread, ...data, updatedAt: new Date().toISOString() };
  },

  getThreadEvents: async (threadId: string): Promise<ThreadEvent[]> => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockReplayEvents.filter((e) => e.threadId === threadId);
  },

  pauseThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const thread = mockThreads.find((t) => t.id === id);
    if (!thread) throw new Error('Thread not found');
    return { ...thread, status: 'paused', updatedAt: new Date().toISOString() };
  },

  resumeThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const thread = mockThreads.find((t) => t.id === id);
    if (!thread) throw new Error('Thread not found');
    return { ...thread, status: 'active', updatedAt: new Date().toISOString() };
  },

  takeoverThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const thread = mockThreads.find((t) => t.id === id);
    if (!thread) throw new Error('Thread not found');
    return { ...thread, status: 'escalated', updatedAt: new Date().toISOString() };
  },
};

// Real API implementation (placeholder)
const realApi = {
  getThreads: async (): Promise<Thread[]> => {
    return apiClient.get<Thread[]>('/threads');
  },

  getThread: async (id: string): Promise<Thread> => {
    return apiClient.get<Thread>(`/threads/${id}`);
  },

  createThread: async (data: Partial<Thread>): Promise<Thread> => {
    return apiClient.post<Thread>('/threads', data);
  },

  updateThread: async (id: string, data: Partial<Thread>): Promise<Thread> => {
    return apiClient.patch<Thread>(`/threads/${id}`, data);
  },

  getThreadEvents: async (threadId: string): Promise<ThreadEvent[]> => {
    return apiClient.get<ThreadEvent[]>(`/threads/${threadId}/events`);
  },

  pauseThread: async (id: string): Promise<Thread> => {
    return apiClient.post<Thread>(`/threads/${id}/pause`);
  },

  resumeThread: async (id: string): Promise<Thread> => {
    return apiClient.post<Thread>(`/threads/${id}/resume`);
  },

  takeoverThread: async (id: string): Promise<Thread> => {
    return apiClient.post<Thread>(`/threads/${id}/takeover`);
  },
};

export const threadsApi = USE_MOCK_API ? mockApi : realApi;
