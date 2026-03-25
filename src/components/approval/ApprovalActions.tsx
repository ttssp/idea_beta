'use client';

import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  XCircle,
  Edit3,
  User,
  MoreHorizontal,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ApprovalActionsProps {
  onApprove?: () => void;
  onReject?: () => void;
  onModify?: () => void;
  onTakeover?: () => void;
  isLoading?: boolean;
  className?: string;
}

export function ApprovalActions({
  onApprove,
  onReject,
  onModify,
  onTakeover,
  isLoading = false,
  className,
}: ApprovalActionsProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Button onClick={onApprove} disabled={isLoading} className="gap-2">
        <CheckCircle2 className="h-4 w-4" />
        批准
      </Button>
      <Button variant="secondary" onClick={onModify} disabled={isLoading} className="gap-2">
        <Edit3 className="h-4 w-4" />
        修改
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" disabled={isLoading}>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={onTakeover} className="gap-2">
            <User className="h-4 w-4" />
            接管
          </DropdownMenuItem>
          <DropdownMenuItem onClick={onReject} className="gap-2 text-destructive">
            <XCircle className="h-4 w-4" />
            拒绝
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
