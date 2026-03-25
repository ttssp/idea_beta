'use client';

import { Badge } from '@/components/ui/badge';
import {
  THREAD_STATUS_LABELS,
  type ThreadStatus,
} from '@/lib/types/thread';
import { getStatusColor } from '@/lib/utils';

interface StatusBadgeProps {
  status: ThreadStatus;
  className?: string;
  showLabel?: boolean;
}

export function StatusBadge({ status, className, showLabel = true }: StatusBadgeProps) {
  const label = THREAD_STATUS_LABELS[status];
  const colorClass = getStatusColor(status);

  return (
    <Badge variant="outline" className={cn('border-0 font-medium', colorClass, className)}>
      {showLabel ? label : label.charAt(0)}
    </Badge>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
