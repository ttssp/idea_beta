'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { mockThreads, mockReplayEvents } from '@/mocks';
import { StatusBadge } from '@/components/common/StatusBadge';
import { History, Clock } from 'lucide-react';
import { formatRelativeTime, truncateText } from '@/lib/utils';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function ReplayPage() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Replay Center</h1>
        <p className="text-muted-foreground mt-1">回放和复盘已完成的线程</p>
      </div>

      <div className="grid gap-4">
        {mockThreads.map((thread) => {
          const events = mockReplayEvents.filter((e) => e.threadId === thread.id);

          return (
            <Link key={thread.id} href={`/replay/${thread.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <CardTitle className="text-base truncate">{thread.title}</CardTitle>
                        <StatusBadge status={thread.status} />
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {truncateText(thread.objective, 120)}
                      </p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <History className="h-4 w-4 mr-2" />
                      回放
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <History className="h-4 w-4" />
                      {events.length} 个事件
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {formatRelativeTime(thread.updatedAt)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
