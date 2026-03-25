/**
 * Thread 相关核心类型定义
 * 与E1保持一致的接口契约
 */

export type ThreadState =
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

export interface Participant {
  id: string;
  name: string;
  email?: string;
  role: 'owner' | 'participant' | 'external';
  relationshipClass?: 'internal' | 'candidate' | 'client' | 'vendor' | 'personal';
}

export interface Message {
  id: string;
  timestamp: string;
  senderId: string;
  content: string;
  channel: 'email' | 'internal' | 'calendar';
  authoredMode:
    | 'human_authored_human_sent'
    | 'agent_drafted_human_sent'
    | 'agent_drafted_human_approved_sent'
    | 'agent_sent_within_policy';
}

export interface DelegationProfile {
  id: string;
  profileName: 'observe_only' | 'draft_first' | 'approve_to_send' | 'bounded_auto' | 'human_only';
  allowedActions: string[];
  maxMessagesPerDay?: number;
  escalationRules: string[];
}

export interface ThreadEvent {
  id: string;
  eventType:
    | 'thread_created'
    | 'message_sent'
    | 'message_received'
    | 'action_executed'
    | 'approval_requested'
    | 'approval_resolved'
    | 'state_changed'
    | 'escalated'
    | 'takeover';
  actor: string;
  payload: Record<string, unknown>;
  occurredAt: string;
  causalRef?: string;
}

export interface ThreadContext {
  threadId: string;
  objective: string;
  currentState: ThreadState;
  participants: Participant[];
  messageHistory: Message[];
  delegationProfile: DelegationProfile;
  eventLog: ThreadEvent[];
  metadata?: Record<string, unknown>;
}

export interface ActionStep {
  id: string;
  type: 'draft_message' | 'send_message' | 'wait' | 'collect_info' | 'escalate' | 'schedule_calendar';
  description: string;
  dependencies?: string[];
  suggestedTemplate?: string;
  estimatedDelayMinutes?: number;
  requiresApproval?: boolean;
}

export interface ActionPlan {
  objective: string;
  steps: ActionStep[];
  estimatedDuration?: string;
  risks?: string[];
  confidence: number;
  suggestedPack?: string;
}

export interface ParsedGoal {
  objective: string;
  keyConstraints: string[];
  successCriteria: string[];
  estimatedComplexity: 'low' | 'medium' | 'high';
  suggestedPack: 'time_coordination' | 'info_collection' | 'follow_up' | 'custom';
}

export interface NextActionSuggestion {
  action: ActionStep;
  reasoning: string;
  urgency: 'low' | 'medium' | 'high';
  alternatives?: ActionStep[];
}
