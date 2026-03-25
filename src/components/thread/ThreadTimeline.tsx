'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Clock } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';
import type { ThreadEvent } from '@/lib/types/replay';

interface ThreadTimelineProps {
  events: ThreadEvent[];
  className?: string;
}

export function ThreadTimeline({ events, className }: ThreadTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        暂无事件记录
      </div>
    );
  }

  return (
    <div className={cn('relative pl-8', className)}>
      <div className="absolute left-3 top-4 bottom-4 w-0.5 bg-border" />

      {events.map((event) => (
        <div key={event.id} className="relative pb-8">
          <div className="absolute left-[-20px] top-1 flex h-6 w-6 items-center justify-center rounded-full border-2 border-background bg-muted">
            <div className={cn('h-2 w-2 rounded-full', getEventDotColor(event.eventType))} />
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
                    <p className="text-sm font-medium">{event.actor.displayName}</p>
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
                </div>
              </CardContent>
            )}
          </Card>
        </div>
      ))}
    </div>
  );
}

function getEventDotColor(eventType: string) {
  switch (eventType) {
    case 'decision':
      return 'bg-blue-500';
    case 'approval':
      return 'bg-amber-500';
    case 'takeover':
      return 'bg-red-500';
    case 'state_change':
      return 'bg-emerald-500';
    default:
      return 'bg-slate-400';
  }
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
