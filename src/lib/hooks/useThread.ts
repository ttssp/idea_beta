'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { threadsApi } from '@/lib/api';
import type { Thread } from '@/lib/types/thread';

export function useThreads() {
  return useQuery({
    queryKey: ['threads'],
    queryFn: threadsApi.getThreads,
  });
}

export function useThread(id: string | null) {
  return useQuery({
    queryKey: ['thread', id],
    queryFn: () => (id ? threadsApi.getThread(id) : undefined),
    enabled: !!id,
  });
}

export function useThreadEvents(threadId: string | null) {
  return useQuery({
    queryKey: ['threadEvents', threadId],
    queryFn: () => (threadId ? threadsApi.getThreadEvents(threadId) : []),
    enabled: !!threadId,
  });
}

export function useCreateThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threadsApi.createThread,
    onSuccess: (newThread) => {
      queryClient.setQueryData(['threads'], (old: Thread[] = []) => [newThread, ...old]);
    },
  });
}

export function useUpdateThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Thread> }) =>
      threadsApi.updateThread(id, data),
    onSuccess: (updatedThread) => {
      queryClient.setQueryData(['thread', updatedThread.id], updatedThread);
      queryClient.setQueryData(['threads'], (old: Thread[] = []) =>
        old.map((t) => (t.id === updatedThread.id ? updatedThread : t))
      );
    },
  });
}

export function usePauseThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threadsApi.pauseThread,
    onSuccess: (updatedThread) => {
      queryClient.setQueryData(['thread', updatedThread.id], updatedThread);
      queryClient.setQueryData(['threads'], (old: Thread[] = []) =>
        old.map((t) => (t.id === updatedThread.id ? updatedThread : t))
      );
    },
  });
}

export function useResumeThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threadsApi.resumeThread,
    onSuccess: (updatedThread) => {
      queryClient.setQueryData(['thread', updatedThread.id], updatedThread);
      queryClient.setQueryData(['threads'], (old: Thread[] = []) =>
        old.map((t) => (t.id === updatedThread.id ? updatedThread : t))
      );
    },
  });
}

export function useTakeoverThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threadsApi.takeoverThread,
    onSuccess: (updatedThread) => {
      queryClient.setQueryData(['thread', updatedThread.id], updatedThread);
      queryClient.setQueryData(['threads'], (old: Thread[] = []) =>
        old.map((t) => (t.id === updatedThread.id ? updatedThread : t))
      );
    },
  });
}
