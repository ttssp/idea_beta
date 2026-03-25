'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Bot, User, ShieldCheck, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

export type AuthoredMode =
  | 'human_authored_human_sent'
  | 'agent_drafted_human_sent'
  | 'agent_drafted_human_approved_sent'
  | 'agent_sent_within_policy';

interface MessageBubbleProps {
  content: string;
  author: {
    name: string;
    avatarUrl?: string;
  };
  authoredMode: AuthoredMode;
  timestamp: string;
  isOutgoing?: boolean;
  className?: string;
}

const modeConfig: Record<
  AuthoredMode,
  { label: string; icon: typeof Bot; variant: 'default' | 'outline' | 'secondary' }
> = {
  human_authored_human_sent: {
    label: '人工撰写',
    icon: User,
    variant: 'secondary',
  },
  agent_drafted_human_sent: {
    label: '代理起草 · 人工发送',
    icon: Eye,
    variant: 'outline',
  },
  agent_drafted_human_approved_sent: {
    label: '代理起草 · 审批发送',
    icon: ShieldCheck,
    variant: 'outline',
  },
  agent_sent_within_policy: {
    label: '代理自动发送',
    icon: Bot,
    variant: 'default',
  },
};

export function MessageBubble({
  content,
  author,
  authoredMode,
  timestamp,
  isOutgoing = false,
  className,
}: MessageBubbleProps) {
  const config = modeConfig[authoredMode];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'flex gap-3 max-w-3xl',
        isOutgoing ? 'flex-row-reverse ml-auto' : '',
        className
      )}
    >
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarImage src={author.avatarUrl} />
        <AvatarFallback className="text-xs">{author.name.charAt(0)}</AvatarFallback>
      </Avatar>

      <div className={cn('flex-1 min-w-0', isOutgoing ? 'items-end' : '')}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">{author.name}</span>
          <Badge variant={config.variant} className="text-xs gap-1 h-5">
            <Icon className="h-3 w-3" />
            {config.label}
          </Badge>
          <span className="text-xs text-muted-foreground">{timestamp}</span>
        </div>

        <Card
          className={cn(
            'inline-block',
            isOutgoing ? 'bg-primary text-primary-foreground' : ''
          )}
        >
          <CardContent className="p-3">{content}</CardContent>
        </Card>
      </div>
    </div>
  );
}
