'use client';

import {
  DELEGATION_PROFILE_LABELS,
  getDelegationProfileColor,
  cn,
} from '@/lib/utils';
import { StatusBadge } from '@/components/common/StatusBadge';
import { RiskLabel } from '@/components/common/RiskLabel';
import type { Thread } from '@/lib/types/thread';
import { Badge } from '@/components/ui/badge';

interface ThreadHeaderProps {
  thread: Thread;
  className?: string;
}

export function ThreadHeader({ thread, className }: ThreadHeaderProps) {
  return (
    <div className={cn('flex flex-col gap-4', className)}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold truncate">{thread.title}</h1>
          <p className="text-muted-foreground mt-1">{thread.objective}</p>
        </div>
        <div className="flex flex-wrap gap-2 flex-shrink-0">
          <StatusBadge status={thread.status} />
          <RiskLabel risk={thread.riskLevel} />
          <Badge
            variant="outline"
            className={cn(getDelegationProfileColor(thread.delegationProfile))}
          >
            {DELEGATION_PROFILE_LABELS[thread.delegationProfile]}
          </Badge>
        </div>
      </div>

      {thread.summary && (
        <div className="rounded-lg bg-muted/50 p-3 text-sm">
          <span className="font-medium">摘要：</span>
          {thread.summary}
        </div>
      )}
    </div>
  );
}
