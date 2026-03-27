import type { Principal } from './thread';
import type { SenderStack, DisclosurePreview } from './contracts';

export type ThreadEventType =
  | 'message'
  | 'action'
  | 'decision'
  | 'state_change'
  | 'approval'
  | 'takeover'
  | 'external_reply';

export interface DecisionTrace {
  relationshipRisk: string;
  actionRisk: string;
  contentRisk: string;
  consequenceRisk: string;
  finalDecision: string;
  policyRulesHit: string[];
  confidence: number;
}

/**
 * Responsibility stage for replay timeline
 * Shows which part of the sender stack was active at this event
 */
export interface ResponsibilityStage {
  role: 'owner' | 'delegate' | 'author' | 'approver' | 'executor';
  principal: Principal;
  action: string;
}

export interface ThreadEvent {
  id: string;
  threadId: string;
  eventType: ThreadEventType;
  actor: Principal;
  payload: Record<string, unknown>;
  occurredAt: string;
  causalRef?: string;
  decisionTrace?: DecisionTrace;
  description: string;
  // Sender stack and responsibility tracking for replay
  senderStack?: SenderStack;
  disclosurePreview?: DisclosurePreview;
  responsibilityStages?: ResponsibilityStage[];
}

export const THREAD_EVENT_TYPE_LABELS: Record<ThreadEventType, string> = {
  message: '消息',
  action: '动作',
  decision: '决策',
  state_change: '状态变更',
  approval: '审批',
  takeover: '接管',
  external_reply: '外部回复',
};
