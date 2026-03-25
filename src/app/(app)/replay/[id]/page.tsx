'use client';

import { notFound } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { mockThreads, mockReplayEvents } from '@/mocks';
import { ArrowLeft, Clock } from 'lucide-react';
import Link from 'next/link';
import { formatRelativeTime } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';

interface ReplayDetailPageProps {
  params: { id: string };
}

export default function ReplayDetailPage({ params }: ReplayDetailPageProps) {
  const thread = mockThreads.find((t) => t.id === params.id);
  const events = mockReplayEvents.filter((e) => e.threadId === params.id);

  if (!thread) {
    notFound();
  }

  return (
    <div className="h-full flex flex-col">
      <div className="border-b p-4">
        <div className="flex items-center gap-4 mb-2">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/replay">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <h1 className="text-xl font-bold truncate">{thread.title}</h1>
          <StatusBadge status={thread.status} />
        </div>
        <p className="text-sm text-muted-foreground pl-12">{thread.objective}</p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          <div className="relative pl-8">
            {/* Timeline line */}
            <div className="absolute left-3 top-4 bottom-4 w-0.5 bg-border" />

            {events.map((event) => (
              <div key={event.id} className="relative pb-8">
                {/* Dot */}
                <div className="absolute left-[-20px] top-1 flex h-6 w-6 items-center justify-center rounded-full border-2 border-background bg-muted">
                  {event.eventType === 'decision' ? (
                    <div className="h-2 w-2 rounded-full bg-blue-500" />
                  ) : event.eventType === 'approval' ? (
                    <div className="h-2 w-2 rounded-full bg-amber-500" />
                  ) : (
                    <div className="h-2 w-2 rounded-full bg-slate-400" />
                  )}
                </div>

                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={event.actor.avatarUrl} />
                          <AvatarFallback className="text-xs">
                            {event.actor.displayName.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <CardTitle className="text-sm">{event.actor.displayName}</CardTitle>
                          <p className="text-xs text-muted-foreground">{event.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {event.eventType}
                        </Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatRelativeTime(event.occurredAt)}
                        </span>
                      </div>
                    </div>
                  </CardHeader>
                  {event.decisionTrace && (
                    <CardContent className="pt-0">
                      <Separator className="my-2" />
                      <div className="mt-2 space-y-2 rounded-lg bg-muted/50 p-3 text-sm">
                        <p className="font-medium">决策追踪</p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <span className="text-muted-foreground">关系风险：</span>
                            {event.decisionTrace.relationshipRisk}
                          </div>
                          <div>
                            <span className="text-muted-foreground">动作风险：</span>
                            {event.decisionTrace.actionRisk}
                          </div>
                          <div>
                            <span className="text-muted-foreground">内容风险：</span>
                            {event.decisionTrace.contentRisk}
                          </div>
                          <div>
                            <span className="text-muted-foreground">结果风险：</span>
                            {event.decisionTrace.consequenceRisk}
                          </div>
                        </div>
                        <div className="mt-2">
                          <span className="text-muted-foreground text-xs">最终决策：</span>
                          <span className="text-xs font-medium ml-1">{event.decisionTrace.finalDecision}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground text-xs">命中规则：</span>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {event.decisionTrace.policyRulesHit.map((rule) => (
                              <Badge key={rule} variant="outline" className="text-xs">
                                {rule}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  )}
                </Card>
              </div>
            ))}

            {events.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                暂无事件记录
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
