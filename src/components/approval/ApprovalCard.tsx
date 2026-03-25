'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, ShieldAlert } from 'lucide-react';
import {
  APPROVAL_REQUEST_TYPE_LABELS,
  APPROVAL_STATUS_LABELS,
} from '@/lib/types/approval';
import { formatRelativeTime, truncateText } from '@/lib/utils';
import type { ApprovalRequest } from '@/lib/types/approval';
import Link from 'next/link';

interface ApprovalCardProps {
  approval: ApprovalRequest;
  className?: string;
  onClick?: () => void;
}

export function ApprovalCard({ approval, className, onClick }: ApprovalCardProps) {
  return (
    <Card className={cn('hover:border-primary/50 transition-colors', className)} onClick={onClick}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <CardTitle className="text-base truncate">
                {APPROVAL_REQUEST_TYPE_LABELS[approval.requestType]}
              </CardTitle>
              <Badge
                variant="outline"
                className={cn(
                  approval.status === 'pending'
                    ? 'bg-amber-50 text-amber-700 border-amber-200'
                    : approval.status === 'approved'
                      ? 'bg-green-50 text-green-700 border-green-200'
                      : 'bg-slate-50 text-slate-700 border-slate-200'
                )}
              >
                {APPROVAL_STATUS_LABELS[approval.status]}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{approval.reasonDescription}</p>
          </div>
          <span className="text-xs text-muted-foreground flex items-center gap-1 flex-shrink-0">
            <Clock className="h-3 w-3" />
            {formatRelativeTime(approval.createdAt)}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {approval.threadId && (
            <p className="text-sm">
              <span className="text-muted-foreground">线程：</span>
              <Link href={`/threads/${approval.threadId}`} className="hover:underline">
                查看线程详情
              </Link>
            </p>
          )}

          <div className="rounded-lg bg-muted/50 p-3 text-sm">
            <p className="text-xs text-muted-foreground mb-1">收件人：{approval.preview.recipient}</p>
            <p className="text-xs text-muted-foreground mb-2">渠道：{approval.preview.channel}</p>
            <p>{truncateText(approval.preview.content, 150)}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {approval.triggeringRule && (
              <Badge variant="outline" className="text-xs">
                规则：{approval.triggeringRule}
              </Badge>
            )}
            {approval.riskReason && (
              <Badge variant="outline" className="text-xs text-red-600 border-red-200 bg-red-50">
                <ShieldAlert className="h-3 w-3 mr-1" />
                {approval.riskReason}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
