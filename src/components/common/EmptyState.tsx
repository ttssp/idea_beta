'use client';

import { Button } from '@/components/ui/button';
import { Inbox, Search, AlertCircle } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: 'inbox' | 'search' | 'error';
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const EmptyIcons = {
  inbox: Inbox,
  search: Search,
  error: AlertCircle,
};

export function EmptyState({
  title,
  description,
  icon = 'inbox',
  action,
  className,
}: EmptyStateProps) {
  const Icon = EmptyIcons[icon];

  return (
    <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
      <div className="mb-4 rounded-full bg-muted p-4">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      {description && <p className="mb-6 max-w-sm text-sm text-muted-foreground">{description}</p>}
      {action && (
        <Button onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
