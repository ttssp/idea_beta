'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Clock, Users, Eye, Shield } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';
import type { ThreadEvent } from '@/lib/types/replay';

interface ReplayTimelineProps {
  events: ThreadEvent[];
  className?: string;
}

export function ReplayTimeline({ events, className }: ReplayTimelineProps) {
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
                  {event.senderStack && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge variant="outline" className="text-xs gap-1">
                            <Users className="h-3 w-3" />
                            Sender Stack
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent className="w-80">
                          <SenderStackTooltip senderStack={event.senderStack} />
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
                  {event.disclosurePreview && (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge variant="outline" className="text-xs gap-1">
                            <Eye className="h-3 w-3" />
                            {event.disclosurePreview.resolved_mode}
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>
                          <DisclosureTooltip preview={event.disclosurePreview} />
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  )}
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

            {/* Responsibility Stages */}
            {event.responsibilityStages && event.responsibilityStages.length > 0 && (
              <CardContent className="pb-2 pt-0">
                <div className="flex flex-wrap gap-2">
                  {event.responsibilityStages.map((stage, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs gap-1">
                      <Shield className="h-3 w-3" />
                      {stage.role}: {stage.principal.displayName}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            )}

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
    </div>
  );
}

/**
 * Tooltip showing sender stack details
 */
function SenderStackTooltip({ senderStack }: { senderStack: any }) {
  return (
    <div className="space-y-2">
      <p className="font-medium text-sm">Sender Stack</p>
      <div className="space-y-1">
        {senderStack.owner && (
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">OWNER</Badge>
            <span>{senderStack.owner.display_name}</span>
          </div>
        )}
        {senderStack.delegate && (
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">DELEGATE</Badge>
            <span>{senderStack.delegate.display_name}</span>
          </div>
        )}
        {senderStack.author && (
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">AUTHOR</Badge>
            <span>{senderStack.author.display_name}</span>
          </div>
        )}
        {senderStack.approver && (
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">APPROVER</Badge>
            <span>{senderStack.approver.display_name}</span>
          </div>
        )}
        {senderStack.executor && (
          <div className="flex items-center gap-2 text-xs">
            <Badge variant="outline" className="text-[10px]">EXECUTOR</Badge>
            <span>{senderStack.executor.display_name}</span>
          </div>
        )}
      </div>
      {senderStack.authority_label && (
        <p className="text-xs text-muted-foreground">
          Authority: {senderStack.authority_label}
        </p>
      )}
      {senderStack.representation_note && (
        <p className="text-xs text-muted-foreground">
          Note: {senderStack.representation_note}
        </p>
      )}
    </div>
  );
}

/**
 * Tooltip showing disclosure preview details
 */
function DisclosureTooltip({ preview }: { preview: any }) {
  return (
    <div className="space-y-2">
      <p className="font-medium text-sm">Disclosure Preview</p>
      <div className="space-y-1 text-xs">
        <div>
          <span className="text-muted-foreground">Mode:</span>{' '}
          <span className="font-medium">{preview.resolved_mode}</span>
        </div>
        <div>
          <span className="text-muted-foreground">Visible Fields:</span>{' '}
          {preview.visible_fields?.length > 0 ? (
            <span>{preview.visible_fields.join(', ')}</span>
          ) : (
            <span className="text-muted-foreground">None</span>
          )}
        </div>
        <div>
          <span className="text-muted-foreground">Requires Notice:</span>{' '}
          <span>{preview.requires_recipient_notice ? 'Yes' : 'No'}</span>
        </div>
        {preview.rendered_text && (
          <div>
            <span className="text-muted-foreground">Template:</span>{' '}
            <span className="line-clamp-2">{preview.rendered_text}</span>
          </div>
        )}
      </div>
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
