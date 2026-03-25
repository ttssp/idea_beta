'use client';

import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { RiskLabel } from '@/components/common/RiskLabel';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DELEGATION_PROFILE_LABELS,
  getDelegationProfileColor,
  formatRelativeTime,
  truncateText,
  cn,
} from '@/lib/utils';
import type { Thread } from '@/lib/types/thread';
import { Users, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface ThreadCardProps {
  thread: Thread;
  className?: string;
}

export function ThreadCard({ thread, className }: ThreadCardProps) {
  return (
    <Link href={`/threads/${thread.id}`}>
      <Card className={cn('hover:border-primary/50 transition-colors cursor-pointer', className)}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <CardTitle className="text-base truncate">{thread.title}</CardTitle>
                <StatusBadge status={thread.status} showLabel={false} />
              </div>
              <CardDescription className="text-sm line-clamp-2">
                {truncateText(thread.objective, 120)}
              </CardDescription>
            </div>
            <ChevronRight className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex -space-x-2">
                {thread.participants.slice(0, 3).map((p) => (
                  <Avatar key={p.id} className="h-7 w-7 border-2 border-background">
                    <AvatarImage src={p.avatarUrl} />
                    <AvatarFallback className="text-xs">
                      {p.displayName.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                ))}
                {thread.participants.length > 3 && (
                  <div className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-background bg-muted text-xs">
                    +{thread.participants.length - 3}
                  </div>
                )}
              </div>
              <Badge
                variant="outline"
                className={cn('text-xs', getDelegationProfileColor(thread.delegationProfile))}
              >
                {DELEGATION_PROFILE_LABELS[thread.delegationProfile]}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <RiskLabel risk={thread.riskLevel} showIcon={false} />
              <span className="text-xs text-muted-foreground">
                {formatRelativeTime(thread.updatedAt)}
              </span>
            </div>
          </div>
          {thread.nextStep && (
            <div className="mt-3 flex items-start gap-2 rounded-lg bg-muted/50 p-2 text-sm">
              <span className="text-muted-foreground">下一步：</span>
              <span className="flex-1">{thread.nextStep}</span>
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
