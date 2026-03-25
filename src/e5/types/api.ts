/**
 * API 请求/响应类型定义
 * E5对外提供的接口契约
 */

import type { ThreadContext, ActionPlan, NextActionSuggestion } from './thread.js';
import type { RiskClassification, ClassifyRiskRequest } from './risk.js';

// ============ Planner API ============

export interface PlanRequest {
  threadContext: ThreadContext;
  forceRefresh?: boolean;
  usePack?: string;
}

export interface PlanResponse {
  plan: ActionPlan;
  nextSuggestion?: NextActionSuggestion;
  reasoning: string;
  modelUsed: string;
  processingTimeMs: number;
  cached: boolean;
}

export interface SuggestNextRequest {
  threadContext: ThreadContext;
  includeAlternatives?: boolean;
}

export interface SuggestNextResponse {
  suggestion: NextActionSuggestion;
  modelUsed: string;
  processingTimeMs: number;
}

// ============ Drafter API ============

export interface DraftMessageRequest {
  threadContext: ThreadContext;
  templateType?: 'email_proposal' | 'email_confirmation' | 'email_followup' | 'email_reminder';
  templateVariant?: 'default' | 'formal' | 'friendly';
  tone?: 'professional' | 'friendly' | 'concise' | 'detailed';
  length?: 'short' | 'medium' | 'long';
  specificInstructions?: string;
  targetRecipient?: {
    name?: string;
    role?: string;
    relationship?: string;
  };
}

export interface DraftMessageResponse {
  draft: {
    subject: string;
    content: string;
    contentType: 'text/plain' | 'text/html' | 'markdown';
  };
  suggestedEdits: string[];
  riskPreview?: RiskClassification;
  alternatives?: Array<{
    subject: string;
    content: string;
    variant: string;
  }>;
  modelUsed: string;
  processingTimeMs: number;
}

export interface GenerateTimeSlotsRequest {
  threadContext: ThreadContext;
  participants: Array<{
    id: string;
    name: string;
    email?: string;
    busySlots?: Array<{
      startTime: string;
      endTime: string;
    }>;
  }>;
  timeRangeStart: string;
  timeRangeEnd: string;
  meetingDurationMinutes: number;
  preferredTimeOfDay?: 'morning' | 'afternoon' | 'any';
  excludeDays?: number[]; // 0 = Sunday, 6 = Saturday
  maxSlots?: number;
}

export interface TimeSlot {
  id: string;
  startTime: string;
  endTime: string;
  allParticipantsAvailable: boolean;
  availabilityConfidence: number;
  conflicts?: string[];
}

export interface GenerateTimeSlotsResponse {
  slots: TimeSlot[];
  recommendedSlot?: TimeSlot;
  reasoning: string;
  processingTimeMs: number;
}

export interface GenerateChecklistRequest {
  threadContext: ThreadContext;
  checklistType?: 'document_collection' | 'meeting_prep' | 'onboarding';
}

export interface ChecklistItem {
  id: string;
  text: string;
  required: boolean;
  priority: 'low' | 'medium' | 'high';
  description?: string;
}

export interface GenerateChecklistResponse {
  checklist: ChecklistItem[];
  reasoning: string;
  modelUsed: string;
  processingTimeMs: number;
}

// ============ Risk API ============

export { ClassifyRiskRequest, RiskClassification };

export interface ClassifyRiskResponse {
  classification: RiskClassification;
  modelUsed: string;
  processingTimeMs: number;
  cached: boolean;
}

// ============ Summary API ============

export interface SummarizeThreadRequest {
  threadContext: ThreadContext;
  summaryLength?: 'short' | 'medium' | 'long';
  includeKeyDecisions?: boolean;
  highlightRiskPoints?: boolean;
}

export interface SummarizeThreadResponse {
  summary: {
    title: string;
    overview: string;
    currentStatus: string;
    nextSteps: string[];
    keyDecisions?: string[];
    riskPoints?: string[];
  };
  modelUsed: string;
  processingTimeMs: number;
}

// ============ Error Response ============

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
  requestId: string;
}
