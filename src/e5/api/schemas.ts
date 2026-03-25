/**
 * API Schema 定义
 * 使用 Zod 进行运行时验证
 */

import { z } from 'zod';

export const ThreadStateSchema = z.enum([
  'new',
  'planning',
  'active',
  'awaiting_external',
  'awaiting_approval',
  'blocked',
  'paused',
  'escalated',
  'completed',
  'cancelled',
]);

export const ParticipantSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().optional(),
  role: z.enum(['owner', 'participant', 'external']),
  relationshipClass: z.enum(['internal', 'candidate', 'client', 'vendor', 'personal']).optional(),
});

export const MessageSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  senderId: z.string(),
  content: z.string(),
  channel: z.enum(['email', 'internal', 'calendar']),
  authoredMode: z.enum([
    'human_authored_human_sent',
    'agent_drafted_human_sent',
    'agent_drafted_human_approved_sent',
    'agent_sent_within_policy',
  ]),
});

export const DelegationProfileSchema = z.object({
  id: z.string(),
  profileName: z.enum(['observe_only', 'draft_first', 'approve_to_send', 'bounded_auto', 'human_only']),
  allowedActions: z.array(z.string()),
  maxMessagesPerDay: z.number().optional(),
  escalationRules: z.array(z.string()),
});

export const ThreadEventSchema = z.object({
  id: z.string(),
  eventType: z.enum([
    'thread_created',
    'message_sent',
    'message_received',
    'action_executed',
    'approval_requested',
    'approval_resolved',
    'state_changed',
    'escalated',
    'takeover',
  ]),
  actor: z.string(),
  payload: z.record(z.unknown()),
  occurredAt: z.string(),
  causalRef: z.string().optional(),
});

export const ThreadContextSchema = z.object({
  threadId: z.string(),
  objective: z.string(),
  currentState: ThreadStateSchema,
  participants: z.array(ParticipantSchema),
  messageHistory: z.array(MessageSchema),
  delegationProfile: DelegationProfileSchema,
  eventLog: z.array(ThreadEventSchema),
  metadata: z.record(z.unknown()).optional(),
});

export const ActionStepSchema = z.object({
  id: z.string(),
  type: z.enum(['draft_message', 'send_message', 'wait', 'collect_info', 'escalate', 'schedule_calendar']),
  description: z.string(),
  dependencies: z.array(z.string()).optional(),
  suggestedTemplate: z.string().optional(),
  requiresApproval: z.boolean().optional(),
  estimatedDelayMinutes: z.number().optional(),
});

export const ActionPlanSchema = z.object({
  objective: z.string(),
  steps: z.array(ActionStepSchema),
  estimatedDuration: z.string().optional(),
  risks: z.array(z.string()).optional(),
  confidence: z.number(),
  suggestedPack: z.string().optional(),
});

export const NextActionSuggestionSchema = z.object({
  action: ActionStepSchema,
  reasoning: z.string(),
  urgency: z.enum(['low', 'medium', 'high']),
  alternatives: z.array(ActionStepSchema).optional(),
});

export const RiskTagSchema = z.enum([
  'amount_mentioned',
  'commitment_made',
  'conflict_detected',
  'privacy_exposed',
  'negative_emotion',
  'legal_terms',
  'uncertainty_high',
]);

export const RiskLevelSchema = z.enum(['low', 'medium', 'high', 'critical']);

export const RiskClassificationSchema = z.object({
  tags: z.array(RiskTagSchema),
  confidence: z.record(RiskTagSchema, z.number()),
  overallRiskLevel: RiskLevelSchema,
  reasoning: z.string(),
  suggestedAction: z.enum(['allow', 'draft_only', 'require_approval', 'escalate', 'deny']).optional(),
  ruleMatches: z.array(z.string()).optional(),
  modelUsed: z.string().optional(),
});

// ============ Request Schemas ============

export const PlanRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  forceRefresh: z.boolean().optional(),
  usePack: z.string().optional(),
});

export const SuggestNextRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  includeAlternatives: z.boolean().optional(),
});

export const DraftMessageRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  templateType: z.enum(['email_proposal', 'email_confirmation', 'email_followup', 'email_reminder']).optional(),
  templateVariant: z.enum(['default', 'formal', 'friendly']).optional(),
  tone: z.enum(['professional', 'friendly', 'concise', 'detailed']).optional(),
  length: z.enum(['short', 'medium', 'long']).optional(),
  specificInstructions: z.string().optional(),
  targetRecipient: z.object({
    name: z.string().optional(),
    role: z.string().optional(),
    relationship: z.string().optional(),
  }).optional(),
});

export const GenerateTimeSlotsRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  participants: z.array(z.object({
    id: z.string(),
    name: z.string(),
    email: z.string().optional(),
    busySlots: z.array(z.object({
      startTime: z.string(),
      endTime: z.string(),
    })).optional(),
  })),
  timeRangeStart: z.string(),
  timeRangeEnd: z.string(),
  meetingDurationMinutes: z.number(),
  preferredTimeOfDay: z.enum(['morning', 'afternoon', 'any']).optional(),
  excludeDays: z.array(z.number()).optional(),
  maxSlots: z.number().optional(),
});

export const GenerateChecklistRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  checklistType: z.enum(['document_collection', 'meeting_prep', 'onboarding']).optional(),
});

export const ClassifyRiskRequestSchema = z.object({
  content: z.string(),
  threadContext: ThreadContextSchema.partial().optional(),
  contextType: z.enum(['email', 'message', 'draft', 'plan']).optional(),
});

export const SummarizeThreadRequestSchema = z.object({
  threadContext: ThreadContextSchema,
  summaryLength: z.enum(['short', 'medium', 'long']).optional(),
  includeKeyDecisions: z.boolean().optional(),
  highlightRiskPoints: z.boolean().optional(),
});

// ============ Response Schemas ============

export const PlanResponseSchema = z.object({
  plan: ActionPlanSchema,
  nextSuggestion: NextActionSuggestionSchema.optional(),
  reasoning: z.string(),
  modelUsed: z.string(),
  processingTimeMs: z.number(),
  cached: z.boolean(),
});

export const SuggestNextResponseSchema = z.object({
  suggestion: NextActionSuggestionSchema,
  modelUsed: z.string(),
  processingTimeMs: z.number(),
});

export const DraftMessageResponseSchema = z.object({
  draft: z.object({
    subject: z.string(),
    content: z.string(),
    contentType: z.enum(['text/plain', 'text/html', 'markdown']),
  }),
  suggestedEdits: z.array(z.string()),
  riskPreview: RiskClassificationSchema.optional(),
  alternatives: z.array(z.object({
    subject: z.string(),
    content: z.string(),
    variant: z.string(),
  })).optional(),
  modelUsed: z.string(),
  processingTimeMs: z.number(),
});

export const TimeSlotSchema = z.object({
  id: z.string(),
  startTime: z.string(),
  endTime: z.string(),
  allParticipantsAvailable: z.boolean(),
  availabilityConfidence: z.number(),
  conflicts: z.array(z.string()).optional(),
});

export const GenerateTimeSlotsResponseSchema = z.object({
  slots: z.array(TimeSlotSchema),
  recommendedSlot: TimeSlotSchema.optional(),
  reasoning: z.string(),
  processingTimeMs: z.number(),
});

export const ChecklistItemSchema = z.object({
  id: z.string(),
  text: z.string(),
  required: z.boolean(),
  priority: z.enum(['low', 'medium', 'high']),
  description: z.string().optional(),
});

export const GenerateChecklistResponseSchema = z.object({
  checklist: z.array(ChecklistItemSchema),
  reasoning: z.string(),
  modelUsed: z.string(),
  processingTimeMs: z.number(),
});

export const ClassifyRiskResponseSchema = z.object({
  classification: RiskClassificationSchema,
  modelUsed: z.string(),
  processingTimeMs: z.number(),
  cached: z.boolean(),
});

export const SummarizeThreadResponseSchema = z.object({
  summary: z.object({
    title: z.string(),
    overview: z.string(),
    currentStatus: z.string(),
    nextSteps: z.array(z.string()),
    keyDecisions: z.array(z.string()).optional(),
    riskPoints: z.array(z.string()).optional(),
  }),
  modelUsed: z.string(),
  processingTimeMs: z.number(),
});

export const ErrorResponseSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.unknown().optional(),
  }),
  requestId: z.string(),
});

export type {
  ThreadContext,
  ActionPlan,
  ActionStep,
  NextActionSuggestion,
  RiskClassification,
  RiskTag,
  RiskLevel,
} from '../types/index.js';
