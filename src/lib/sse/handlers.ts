'use client';

import { useEffect, useCallback, useRef } from 'react';
import { getSSEClient, type SSEClient } from './client';
import { useThreadStore, useApprovalStore } from '@/lib/store';
import type { Thread, ApprovalRequest } from '@/lib/types';

export function useRealtime() {
  const sseClientRef = useRef<SSEClient | null>(null);
  const updateThread = useThreadStore((state) => state.updateThread);
  const addThread = useThreadStore((state) => state.addThread);
  const updateApproval = useApprovalStore((state) => state.updateApproval);

  const handleThreadUpdate = useCallback(
    (thread: Thread) => {
      updateThread(thread.id, thread);
    },
    [updateThread]
  );

  const handleThreadCreated = useCallback(
    (thread: Thread) => {
      addThread(thread);
    },
    [addThread]
  );

  const handleApprovalUpdate = useCallback(
    (approval: ApprovalRequest) => {
      updateApproval(approval.id, approval);
    },
    [updateApproval]
  );

  const connect = useCallback(() => {
    if (!sseClientRef.current) {
      sseClientRef.current = getSSEClient();
    }

    const client = sseClientRef.current;

    client.on('thread_update', handleThreadUpdate);
    client.on('thread_created', handleThreadCreated);
    client.on('approval_update', handleApprovalUpdate);

    client.connect();
  }, [handleThreadUpdate, handleThreadCreated, handleApprovalUpdate]);

  const disconnect = useCallback(() => {
    if (sseClientRef.current) {
      sseClientRef.current.off('thread_update');
      sseClientRef.current.off('thread_created');
      sseClientRef.current.off('approval_update');
      sseClientRef.current.disconnect();
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    isConnected: () => sseClientRef.current?.isConnected() ?? false,
  };
}

export function useThreadRealtime(threadId: string | null) {
  const sseClientRef = useRef<SSEClient | null>(null);
  const updateThread = useThreadStore((state) => state.updateThread);

  const handleThreadUpdate = useCallback(
    (thread: Thread) => {
      if (thread.id === threadId) {
        updateThread(thread.id, thread);
      }
    },
    [threadId, updateThread]
  );

  useEffect(() => {
    if (!threadId) return;

    if (!sseClientRef.current) {
      sseClientRef.current = getSSEClient();
    }

    const client = sseClientRef.current;
    client.on('thread_update', handleThreadUpdate);
    client.connect();

    return () => {
      client.off('thread_update');
    };
  }, [threadId, handleThreadUpdate]);
}
