'use client';

import { ThreadBucket } from '@/components/thread/ThreadBucket';
import { mockThreads } from '@/mocks';
import type { Thread, ThreadStatus } from '@/lib/types/thread';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

const bucketDefinitions = [
  {
    id: 'needs_approval',
    name: 'Needs Approval',
    description: '等待你审批的动作',
    statuses: ['awaiting_approval'] as ThreadStatus[],
  },
  {
    id: 'agent_running',
    name: 'Agent Running',
    description: '代理正在推进的线程',
    statuses: ['active', 'planning'] as ThreadStatus[],
  },
  {
    id: 'awaiting_external',
    name: 'Awaiting External',
    description: '等待外部回复',
    statuses: ['awaiting_external'] as ThreadStatus[],
  },
  {
    id: 'blocked_at_risk',
    name: 'Blocked / At Risk',
    description: '需要关注的问题线程',
    statuses: ['blocked', 'escalated', 'paused'] as ThreadStatus[],
  },
  {
    id: 'completed',
    name: 'Completed',
    description: '已完成的线程',
    statuses: ['completed', 'cancelled'] as ThreadStatus[],
    defaultCollapsed: true,
  },
];

function groupThreadsByBucket(threads: Thread[]) {
  const buckets: Record<string, Thread[]> = {};

  bucketDefinitions.forEach((bucket) => {
    buckets[bucket.id] = threads.filter((t) => bucket.statuses.includes(t.status));
  });

  return buckets;
}

export default function ThreadInboxPage() {
  const buckets = groupThreadsByBucket(mockThreads);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Thread Inbox</h1>
          <p className="text-muted-foreground mt-1">管理所有通信线程</p>
        </div>
        <Button asChild>
          <Link href="/threads/new">
            <Plus className="h-4 w-4 mr-2" />
            New Thread
          </Link>
        </Button>
      </div>

      <div className="space-y-8">
        {bucketDefinitions.map((bucket) => (
          <ThreadBucket
            key={bucket.id}
            id={bucket.id}
            name={bucket.name}
            description={bucket.description}
            threads={buckets[bucket.id]}
            defaultCollapsed={bucket.defaultCollapsed}
          />
        ))}
      </div>
    </div>
  );
}
