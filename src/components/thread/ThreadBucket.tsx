'use client';

import { useState } from 'react';
import { ThreadCard } from './ThreadCard';
import { EmptyState } from '@/components/common/EmptyState';
import { cn } from '@/lib/utils';
import type { Thread } from '@/lib/types/thread';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface ThreadBucketProps {
  id: string;
  name: string;
  description: string;
  threads: Thread[];
  priority?: number;
  showCount?: boolean;
  defaultCollapsed?: boolean;
  className?: string;
  onNewThread?: () => void;
}

const bucketIcons: Record<string, React.ReactNode> = {
  needs_approval: (
    <div className="h-6 w-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center">
      <span className="text-xs font-bold">!</span>
    </div>
  ),
  agent_running: (
    <div className="h-6 w-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center animate-pulse-soft">
      <span className="text-xs font-bold">▶</span>
    </div>
  ),
  awaiting_external: (
    <div className="h-6 w-6 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center">
      <span className="text-xs font-bold">⏳</span>
    </div>
  ),
  blocked_at_risk: (
    <div className="h-6 w-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
      <span className="text-xs font-bold">✕</span>
    </div>
  ),
  completed: (
    <div className="h-6 w-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
      <span className="text-xs font-bold">✓</span>
    </div>
  ),
};

export function ThreadBucket({
  id,
  name,
  description,
  threads,
  showCount = true,
  defaultCollapsed = false,
  className,
  onNewThread,
}: ThreadBucketProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);

  return (
    <div className={cn('space-y-3', className)}>
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex w-full items-center justify-between text-left"
      >
        <div className="flex items-center gap-3">
          {bucketIcons[id] || null}
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{name}</h3>
              {showCount && (
                <span className="text-sm text-muted-foreground">({threads.length})</span>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
        {collapsed ? (
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        ) : (
          <ChevronUp className="h-5 w-5 text-muted-foreground" />
        )}
      </button>

      {!collapsed && (
        <div className="space-y-3 pl-9">
          {threads.length === 0 ? (
            <EmptyState
              title="暂无线程"
              description={`${name}中暂无线程`}
              icon="inbox"
              action={onNewThread ? { label: '新建线程', onClick: onNewThread } : undefined}
            />
          ) : (
            threads.map((thread) => <ThreadCard key={thread.id} thread={thread} />)
          )}
        </div>
      )}
    </div>
  );
}
