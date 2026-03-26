'use client';

import { notFound, useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import {
  DELEGATION_PROFILE_LABELS,
  getDelegationProfileColor,
  formatDate,
  cn,
} from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ThreadHeader, ThreadTimeline, ThreadActionBar } from '@/components/thread';
import { mockThreads, mockReplayEvents } from '@/mocks';

export default function ThreadDetailPage() {
  const params = useParams<{ id: string }>();
  const threadId = typeof params.id === 'string' ? params.id : '';
  const thread = mockThreads.find((t) => t.id === threadId);
  const events = mockReplayEvents.filter((e) => e.threadId === threadId);

  if (!thread) {
    notFound();
  }

  return (
    <div className="h-full flex flex-col">
      <div className="border-b p-4">
        <div className="flex items-center gap-4 mb-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <ThreadHeader thread={thread} />
        </div>
        <ThreadActionBar
          threadId={thread.id}
          isPaused={thread.status === 'paused'}
        />
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header Info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">线程信息</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-muted-foreground">委托档位</span>
                  <Badge
                    variant="outline"
                    className={cn('ml-2', getDelegationProfileColor(thread.delegationProfile))}
                  >
                    {DELEGATION_PROFILE_LABELS[thread.delegationProfile]}
                  </Badge>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">当前责任方</span>
                  <p className="font-medium">{thread.currentResponsible}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">创建时间</span>
                  <p className="font-medium">{formatDate(thread.createdAt)}</p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-muted-foreground">参与者</span>
                  <div className="flex gap-2 mt-1">
                    {thread.participants.map((p) => (
                      <div key={p.id} className="flex items-center gap-2">
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={p.avatarUrl} />
                          <AvatarFallback className="text-xs">{p.displayName.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <span className="text-sm">{p.displayName}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {thread.nextStep && (
                  <div>
                    <span className="text-sm text-muted-foreground">下一步</span>
                    <p className="font-medium text-amber-700">{thread.nextStep}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">时间线</CardTitle>
            </CardHeader>
            <CardContent>
              <ThreadTimeline events={events} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
