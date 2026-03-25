import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { ThreadStatus, RiskLevel, DelegationProfile } from '@/lib/types/thread';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  return formatDate(d);
}

export function getStatusColor(status: ThreadStatus): string {
  const colors: Record<ThreadStatus, string> = {
    new: 'bg-slate-100 text-slate-700',
    planning: 'bg-blue-100 text-blue-700',
    active: 'bg-emerald-100 text-emerald-700',
    awaiting_external: 'bg-amber-100 text-amber-700',
    awaiting_approval: 'bg-orange-100 text-orange-700',
    blocked: 'bg-red-100 text-red-700',
    paused: 'bg-slate-200 text-slate-600',
    escalated: 'bg-rose-100 text-rose-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-slate-100 text-slate-500',
  };
  return colors[status] || 'bg-slate-100 text-slate-700';
}

export function getRiskColor(risk: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    low: 'bg-green-100 text-green-700 border-green-200',
    medium: 'bg-amber-100 text-amber-700 border-amber-200',
    high: 'bg-orange-100 text-orange-700 border-orange-200',
    critical: 'bg-red-100 text-red-700 border-red-200',
  };
  return colors[risk] || 'bg-slate-100 text-slate-700 border-slate-200';
}

export function getDelegationProfileColor(profile: DelegationProfile): string {
  const colors: Record<DelegationProfile, string> = {
    observe_only: 'bg-slate-100 text-slate-700',
    draft_first: 'bg-blue-100 text-blue-700',
    approve_to_send: 'bg-amber-100 text-amber-700',
    bounded_auto: 'bg-emerald-100 text-emerald-700',
    human_only: 'bg-rose-100 text-rose-700',
  };
  return colors[profile] || 'bg-slate-100 text-slate-700';
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export function capitalizeFirstLetter(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
