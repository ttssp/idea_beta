'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Users, UserPlus, Briefcase, Building, Globe, Settings2 } from 'lucide-react';
import {
  DELEGATION_PROFILE_LABELS,
  getDelegationProfileColor,
} from '@/lib/utils';
import type { DelegationProfile, RelationshipClass } from '@/lib/types/thread';

const profileIcons: Record<RelationshipClass, typeof Users> = {
  internal_team: Users,
  external_candidate: UserPlus,
  client: Briefcase,
  vendor: Building,
  sensitive_personal: Globe,
  other: Globe,
};

interface ProfileCardProps {
  id: string;
  name: string;
  description: string;
  relationshipClass: RelationshipClass;
  defaultProfile: DelegationProfile;
  enabled?: boolean;
  onEnableChange?: (enabled: boolean) => void;
  onConfigure?: () => void;
  className?: string;
}

export function ProfileCard({
  name,
  description,
  relationshipClass,
  defaultProfile,
  enabled = true,
  onEnableChange,
  onConfigure,
  className,
}: ProfileCardProps) {
  const Icon = profileIcons[relationshipClass];

  return (
    <Card className={cn('hover:border-primary/50 transition-colors', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
              <Icon className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base">{name}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-4 flex-shrink-0">
            <Badge variant="outline" className={getDelegationProfileColor(defaultProfile)}>
              {DELEGATION_PROFILE_LABELS[defaultProfile]}
            </Badge>
            {onEnableChange && (
              <div className="flex items-center gap-2">
                <Switch id={`enable-${name}`} checked={enabled} onCheckedChange={onEnableChange} />
                <Label htmlFor={`enable-${name}`} className="sr-only">
                  启用
                </Label>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {onConfigure && (
          <div className="flex justify-end">
            <Button variant="ghost" size="sm" onClick={onConfigure}>
              <Settings2 className="h-4 w-4 mr-2" />
              配置
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
