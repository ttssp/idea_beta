export type ThreadStatus =
  | 'new'
  | 'planning'
  | 'active'
  | 'awaiting_external'
  | 'awaiting_approval'
  | 'blocked'
  | 'paused'
  | 'escalated'
  | 'completed'
  | 'cancelled';

export type DelegationProfile =
  | 'observe_only'
  | 'draft_first'
  | 'approve_to_send'
  | 'bounded_auto'
  | 'human_only';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Principal {
  id: string;
  type: 'human' | 'agent' | 'external' | 'service';
  displayName: string;
  trustTier: number;
  disclosureMode: string;
  avatarUrl?: string;
}

export interface Thread {
  id: string;
  title: string;
  objective: string;
  status: ThreadStatus;
  ownerId: string;
  delegationProfile: DelegationProfile;
  riskLevel: RiskLevel;
  currentResponsible: string;
  nextStep?: string;
  participants: Principal[];
  createdAt: string;
  updatedAt: string;
  lastEscalationReason?: string;
  summary?: string;
}

export interface ThreadBucket {
  id: string;
  name: string;
  description: string;
  threads: Thread[];
  count: number;
  priority: number;
}

export const THREAD_STATUS_LABELS: Record<ThreadStatus, string> = {
  new: '新建',
  planning: '规划中',
  active: '进行中',
  awaiting_external: '等待外部',
  awaiting_approval: '待审批',
  blocked: '已阻塞',
  paused: '已暂停',
  escalated: '已升级',
  completed: '已完成',
  cancelled: '已取消',
};

export const DELEGATION_PROFILE_LABELS: Record<DelegationProfile, string> = {
  observe_only: '仅观察',
  draft_first: '先起草',
  approve_to_send: '审批发送',
  bounded_auto: '有限自动',
  human_only: '仅人工',
};

export const DELEGATION_PROFILE_DESCRIPTIONS: Record<DelegationProfile, string> = {
  observe_only: '系统只观察与建议，不起草不发送',
  draft_first: '自动起草，但所有消息需人工确认',
  approve_to_send: '低风险动作自动准备，用户一键审批后发出',
  bounded_auto: '在明确预算和动作边界内自动执行',
  human_only: '该类关系或场景禁止代理主动介入',
};

export const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '严重风险',
};

export const BUCKET_IDS = {
  NEEDS_APPROVAL: 'needs_approval',
  AGENT_RUNNING: 'agent_running',
  AWAITING_EXTERNAL: 'awaiting_external',
  BLOCKED_AT_RISK: 'blocked_at_risk',
  COMPLETED: 'completed',
} as const;

export type BucketId = (typeof BUCKET_IDS)[keyof typeof BUCKET_IDS];
