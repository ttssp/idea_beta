'use client';

import { SSE_URL, SSE_RECONNECT_DELAY, SSE_MAX_RECONNECT_ATTEMPTS } from '@/lib/utils/constants';
import type { Thread, ApprovalRequest } from '@/lib/types';

type EventType = 'thread_update' | 'approval_update' | 'thread_created' | 'ping';
type EventHandlerMap = {
  thread_update: (thread: Thread) => void;
  approval_update: (approval: ApprovalRequest) => void;
  thread_created: (thread: Thread) => void;
  ping: () => void;
};

interface EventHandlers {
  onThreadUpdate?: (thread: Thread) => void;
  onApprovalUpdate?: (approval: ApprovalRequest) => void;
  onThreadCreated?: (thread: Thread) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private url: string;
  private handlers: EventHandlers = {};
  private isManualDisconnect = false;

  constructor(url: string = SSE_URL) {
    this.url = url;
  }

  connect(): void {
    if (this.eventSource?.readyState === EventSource.OPEN) {
      return;
    }

    this.isManualDisconnect = false;

    try {
      this.eventSource = new EventSource(this.url);

      this.eventSource.onopen = () => {
        this.reconnectAttempts = 0;
        this.handlers.onConnect?.();
      };

      this.eventSource.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.eventSource.addEventListener('thread_update', (event) => {
        try {
          const thread = JSON.parse(event.data) as Thread;
          this.handlers.onThreadUpdate?.(thread);
        } catch (e) {
          console.error('Failed to parse thread_update event:', e);
        }
      });

      this.eventSource.addEventListener('approval_update', (event) => {
        try {
          const approval = JSON.parse(event.data) as ApprovalRequest;
          this.handlers.onApprovalUpdate?.(approval);
        } catch (e) {
          console.error('Failed to parse approval_update event:', e);
        }
      });

      this.eventSource.addEventListener('thread_created', (event) => {
        try {
          const thread = JSON.parse(event.data) as Thread;
          this.handlers.onThreadCreated?.(thread);
        } catch (e) {
          console.error('Failed to parse thread_created event:', e);
        }
      });

      this.eventSource.addEventListener('ping', () => {
        // Keep-alive ping, do nothing
      });

      this.eventSource.onerror = (error) => {
        this.handleError(error);
      };
    } catch (error: unknown) {
      this.handleError(this.toError(error));
    }
  }

  disconnect(): void {
    this.isManualDisconnect = true;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.handlers.onDisconnect?.();
    }
  }

  on<T extends EventType>(event: T, handler: EventHandlerMap[T]): void {
    switch (event) {
      case 'thread_update':
        this.handlers.onThreadUpdate = handler as EventHandlerMap['thread_update'];
        break;
      case 'approval_update':
        this.handlers.onApprovalUpdate = handler as EventHandlerMap['approval_update'];
        break;
      case 'thread_created':
        this.handlers.onThreadCreated = handler as EventHandlerMap['thread_created'];
        break;
    }
  }

  off(event: EventType): void {
    switch (event) {
      case 'thread_update':
        this.handlers.onThreadUpdate = undefined;
        break;
      case 'approval_update':
        this.handlers.onApprovalUpdate = undefined;
        break;
      case 'thread_created':
        this.handlers.onThreadCreated = undefined;
        break;
    }
  }

  private handleMessage(data: string): void {
    try {
      const parsed = JSON.parse(data);
      console.log('SSE message received:', parsed);
    } catch (e) {
      console.error('Failed to parse SSE message:', e);
    }
  }

  private handleError(error: Event | Error): void {
    console.error('SSE connection error:', error);

    this.handlers.onError?.(error instanceof Error ? error : new Error('SSE connection error'));

    if (!this.isManualDisconnect && this.reconnectAttempts < SSE_MAX_RECONNECT_ATTEMPTS) {
      this.reconnectAttempts++;
      const delay = SSE_RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`);

      setTimeout(() => {
        if (!this.isManualDisconnect) {
          this.connect();
        }
      }, delay);
    }
  }

  private toError(error: unknown): Error {
    if (error instanceof Error) {
      return error;
    }
    return new Error('Unknown SSE error');
  }

  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

// Singleton instance
let sseClient: SSEClient | null = null;

export function getSSEClient(): SSEClient {
  if (!sseClient) {
    sseClient = new SSEClient();
  }
  return sseClient;
}
