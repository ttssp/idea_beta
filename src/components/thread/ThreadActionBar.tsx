'use client';

import { Button } from '@/components/ui/button';
import {
  Pause,
  Play,
  User,
  ShieldAlert,
  RotateCcw,
  MoreHorizontal,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ThreadActionBarProps {
  threadId: string;
  isPaused?: boolean;
  onPause?: () => void;
  onResume?: () => void;
  onTakeover?: () => void;
  onKillSwitch?: () => void;
  className?: string;
}

export function ThreadActionBar({
  threadId,
  isPaused = false,
  onPause,
  onResume,
  onTakeover,
  onKillSwitch,
  className,
}: ThreadActionBarProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      {isPaused ? (
        <Button variant="outline" size="sm" onClick={onResume}>
          <Play className="h-4 w-4 mr-2" />
          恢复
        </Button>
      ) : (
        <Button variant="outline" size="sm" onClick={onPause}>
          <Pause className="h-4 w-4 mr-2" />
          暂停
        </Button>
      )}

      <Button variant="outline" size="sm" onClick={onTakeover}>
        <User className="h-4 w-4 mr-2" />
        接管
      </Button>

      <Button variant="destructive" size="sm" onClick={onKillSwitch}>
        <ShieldAlert className="h-4 w-4 mr-2" />
        Kill Switch
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem>
            <RotateCcw className="h-4 w-4 mr-2" />
            重置委托档位
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
