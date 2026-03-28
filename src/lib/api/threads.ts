import { apiClient } from './client';
import type { Thread, ThreadStatus } from '@/lib/types/thread';
import type { ThreadEvent } from '@/lib/types/replay';
import { mockThreads, mockPrincipals, mockReplayEvents } from '@/mocks';
import { USE_MOCK_API } from '@/lib/utils/constants';

// In-memory array to hold created threads
let localMockThreads = [...mockThreads];

// Mock implementation
const mockApi = {
  getThreads: async (): Promise<Thread[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return localMockThreads;
  },

  getThread: async (id: string): Promise<Thread | undefined> => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return localMockThreads.find((t) => t.id === id);
  },

  createThread: async (data: Partial<Thread>): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const newThread: Thread = {
      id: `thread-${Date.now()}`,
      title: data.title || 'New Thread',
      objective: data.objective || '',
      status: 'planning' as ThreadStatus,
      ownerId: 'user-1',
      delegationProfile: data.delegationProfile || 'draft_first',
      riskLevel: 'low',
      currentResponsible: 'user-1',
      participants: data.participants || [mockPrincipals[0]],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...data,
    };
    // Add to the beginning of the array so it shows up first
    localMockThreads = [newThread, ...localMockThreads];
    return newThread;
  },

  updateThread: async (id: string, data: Partial<Thread>): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const threadIndex = localMockThreads.findIndex((t) => t.id === id);
    if (threadIndex === -1) throw new Error('Thread not found');
    const updatedThread = { ...localMockThreads[threadIndex], ...data, updatedAt: new Date().toISOString() } as Thread;
    localMockThreads[threadIndex] = updatedThread;
    return updatedThread;
  },

  getThreadEvents: async (threadId: string): Promise<ThreadEvent[]> => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockReplayEvents.filter((e) => e.threadId === threadId);
  },

  pauseThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const threadIndex = localMockThreads.findIndex((t) => t.id === id);
    if (threadIndex === -1) throw new Error('Thread not found');
    const updatedThread = { ...localMockThreads[threadIndex], status: 'paused' as ThreadStatus, updatedAt: new Date().toISOString() } as Thread;
    localMockThreads[threadIndex] = updatedThread;
    return updatedThread;
  },

  resumeThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const threadIndex = localMockThreads.findIndex((t) => t.id === id);
    if (threadIndex === -1) throw new Error('Thread not found');
    const updatedThread = { ...localMockThreads[threadIndex], status: 'active' as ThreadStatus, updatedAt: new Date().toISOString() } as Thread;
    localMockThreads[threadIndex] = updatedThread;
    return updatedThread;
  },

  takeoverThread: async (id: string): Promise<Thread> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    const threadIndex = localMockThreads.findIndex((t) => t.id === id);
    if (threadIndex === -1) throw new Error('Thread not found');
    const updatedThread = { ...localMockThreads[threadIndex], status: 'escalated' as ThreadStatus, updatedAt: new Date().toISOString() } as Thread;
    localMockThreads[threadIndex] = updatedThread;
    return updatedThread;
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

