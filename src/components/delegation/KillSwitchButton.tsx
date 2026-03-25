'use client';

import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { ShieldAlert, ShieldX, ShieldCheck } from 'lucide-react';
import { useState } from 'react';

type KillSwitchLevel = 'global' | 'profile' | 'thread';

interface KillSwitchButtonProps {
  level: KillSwitchLevel;
  isActive?: boolean;
  label?: string;
  description?: string;
  onToggle?: (active: boolean) => void;
  className?: string;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary';
}

const levelLabels: Record<KillSwitchLevel, string> = {
  global: '全局停机',
  profile: '档位停机',
  thread: '线程停机',
};

const levelDescriptions: Record<KillSwitchLevel, string> = {
  global: '这将立即停止所有自动化操作',
  profile: '这将停止该类关系的所有自动化操作',
  thread: '这将停止该线程的所有自动化操作',
};

export function KillSwitchButton({
  level,
  isActive = false,
  label,
  description,
  onToggle,
  className,
  variant = 'destructive',
}: KillSwitchButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleConfirm = () => {
    onToggle?.(!isActive);
    setIsDialogOpen(false);
  };

  const Icon = isActive ? ShieldX : ShieldAlert;

  return (
    <AlertDialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <AlertDialogTrigger asChild>
        <Button
          variant={isActive ? 'secondary' : variant}
          className={cn('gap-2', className)}
        >
          <Icon className="h-4 w-4" />
          {label || (isActive ? '已停机' : levelLabels[level])}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-destructive" />
            {isActive ? '解除 Kill Switch' : '确认启用 Kill Switch'}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {description || (isActive
              ? '这将重新启用自动化操作，请确认。'
              : levelDescriptions[level])}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>取消</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            className={cn(isActive ? '' : 'bg-destructive hover:bg-destructive/90')}
          >
            {isActive ? '解除' : '确认停机'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
