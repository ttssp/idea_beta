'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Inbox,
  CheckSquare,
  History,
  Settings,
  Plus,
  ShieldAlert,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navItems = [
  {
    title: 'Thread Inbox',
    href: '/',
    icon: Inbox,
  },
  {
    title: 'Approval Center',
    href: '/approvals',
    icon: CheckSquare,
    badge: 3,
  },
  {
    title: 'Replay Center',
    href: '/replay',
    icon: History,
  },
  {
    title: 'Settings',
    href: '/settings/delegation',
    icon: Settings,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className={cn('flex h-full flex-col border-r bg-sidebar', className)}>
      <div className="flex h-16 items-center border-b px-4">
        <div className="flex items-center gap-2 font-semibold">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <ShieldAlert className="h-5 w-5 text-primary-foreground" />
          </div>
          <span>Comm Control</span>
        </div>
      </div>

      <div className="flex-1 overflow-auto py-4 scrollbar-thin">
        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            const Icon = item.icon;

            return (
              <Link key={item.href} href={item.href}>
                <span
                  className={cn(
                    'group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                  )}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  <span className="flex-1">{item.title}</span>
                  {item.badge && (
                    <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-sidebar-primary px-1.5 text-xs text-sidebar-primary-foreground">
                      {item.badge}
                    </span>
                  )}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t p-4">
        <Button className="w-full gap-2">
          <Plus className="h-4 w-4" />
          New Thread
        </Button>
      </div>
    </div>
  );
}
