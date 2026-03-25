'use client';

import {
  DELEGATION_PROFILE_LABELS,
  DELEGATION_PROFILE_DESCRIPTIONS,
  getDelegationProfileColor,
} from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import type { DelegationProfile } from '@/lib/types/thread';
import { Eye, FileText, ShieldCheck, Zap, UserX } from 'lucide-react';

interface DelegationSliderProps {
  value: DelegationProfile;
  onChange?: (value: DelegationProfile) => void;
  disabled?: boolean;
  className?: string;
}

const profiles: DelegationProfile[] = [
  'human_only',
  'observe_only',
  'draft_first',
  'approve_to_send',
  'bounded_auto',
];

const profileIcons: Record<DelegationProfile, typeof Eye> = {
  observe_only: Eye,
  draft_first: FileText,
  approve_to_send: ShieldCheck,
  bounded_auto: Zap,
  human_only: UserX,
};

export function DelegationSlider({
  value,
  onChange,
  disabled = false,
  className,
}: DelegationSliderProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">委托档位</h4>
        <Badge variant="outline" className={getDelegationProfileColor(value)}>
          {DELEGATION_PROFILE_LABELS[value]}
        </Badge>
      </div>

      <div className="relative">
        <div className="flex items-center justify-between gap-2">
          {profiles.map((profile) => {
            const Icon = profileIcons[profile];
            const isActive = profile === value;
            const isPast = profiles.indexOf(profile) <= profiles.indexOf(value);

            return (
              <button
                key={profile}
                type="button"
                onClick={() => !disabled && onChange?.(profile)}
                disabled={disabled}
                className={cn(
                  'flex flex-col items-center gap-2 flex-1 py-3 rounded-lg transition-all',
                  disabled ? 'cursor-not-allowed opacity-50' : 'hover:bg-muted cursor-pointer',
                  isActive ? 'bg-muted ring-2 ring-primary' : ''
                )}
              >
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : isPast
                        ? 'bg-muted-foreground/20 text-muted-foreground'
                        : 'bg-muted text-muted-foreground/50'
                  )}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-xs text-center font-medium">
                  {DELEGATION_PROFILE_LABELS[profile]}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="rounded-lg bg-muted/50 p-3 text-sm">
        <p className="text-muted-foreground">{DELEGATION_PROFILE_DESCRIPTIONS[value]}</p>
      </div>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
