import type { DelegationProfile, RiskLevel } from './thread';

export type RelationshipClass =
  | 'internal_team'
  | 'external_candidate'
  | 'client'
  | 'vendor'
  | 'sensitive_personal'
  | 'other';

export interface RelationshipTemplate {
  id: string;
  name: string;
  description: string;
  relationshipClass: RelationshipClass;
  defaultProfile: DelegationProfile;
  defaultRiskLevel: RiskLevel;
  icon: string;
}

export interface DelegationBudget {
  maxMessagesPerDay: number;
  maxActionsPerDay: number;
  maxContinuousTouches: number;
  timeWindowMinutes: number;
}

export interface KillSwitchState {
  global: boolean;
  profile: Record<string, boolean>;
  thread: Record<string, boolean>;
}

export const RELATIONSHIP_CLASS_LABELS: Record<RelationshipClass, string> = {
  internal_team: '内部团队',
  external_candidate: '外部候选人',
  client: '客户',
  vendor: '服务方',
  sensitive_personal: '敏感个人',
  other: '其他',
};

export const RELATIONSHIP_TEMPLATES: RelationshipTemplate[] = [
  {
    id: 'internal_collab',
    name: '内部协作',
    description: '与团队成员的日常协作',
    relationshipClass: 'internal_team',
    defaultProfile: 'bounded_auto',
    defaultRiskLevel: 'low',
    icon: 'users',
  },
  {
    id: 'candidate_coordination',
    name: '候选人协调',
    description: '与招聘候选人的沟通',
    relationshipClass: 'external_candidate',
    defaultProfile: 'approve_to_send',
    defaultRiskLevel: 'medium',
    icon: 'user-plus',
  },
  {
    id: 'client_management',
    name: '客户管理',
    description: '与客户的沟通',
    relationshipClass: 'client',
    defaultProfile: 'draft_first',
    defaultRiskLevel: 'high',
    icon: 'briefcase',
  },
  {
    id: 'vendor_communication',
    name: '服务方沟通',
    description: '与供应商/服务方的沟通',
    relationshipClass: 'vendor',
    defaultProfile: 'approve_to_send',
    defaultRiskLevel: 'medium',
    icon: 'building',
  },
];

export const DEFAULT_BUDGET: DelegationBudget = {
  maxMessagesPerDay: 10,
  maxActionsPerDay: 5,
  maxContinuousTouches: 3,
  timeWindowMinutes: 60,
};
