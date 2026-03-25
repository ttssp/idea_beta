'use client';

import { Badge } from '@/components/ui/badge';
import { RISK_LEVEL_LABELS, type RiskLevel } from '@/lib/types/thread';
import { getRiskColor } from '@/lib/utils';
import { AlertTriangle, AlertCircle, ShieldAlert, ShieldCheck } from 'lucide-react';

interface RiskLabelProps {
  risk: RiskLevel;
  className?: string;
  showIcon?: boolean;
}

const RiskIcons: Record<RiskLevel, typeof ShieldCheck> = {
  low: ShieldCheck,
  medium: AlertTriangle,
  high: AlertCircle,
  critical: ShieldAlert,
};

export function RiskLabel({ risk, className, showIcon = true }: RiskLabelProps) {
  const label = RISK_LEVEL_LABELS[risk];
  const colorClass = getRiskColor(risk);
  const Icon = RiskIcons[risk];

  return (
    <Badge variant="outline" className={cn('flex items-center gap-1 border', colorClass, className)}>
      {showIcon && <Icon className="h-3 w-3" />}
      {label}
    </Badge>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}
