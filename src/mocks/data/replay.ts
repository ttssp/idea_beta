import type { ThreadEvent } from '@/lib/types/replay';
import { mockPrincipals } from './threads';

export const mockReplayEvents: ThreadEvent[] = [
  {
    id: 'event-1',
    threadId: 'thread-1',
    eventType: 'state_change',
    actor: mockPrincipals[0],
    payload: { newStatus: 'new', oldStatus: null },
    occurredAt: '2026-03-24T09:00:00Z',
    description: '创建线程',
  },
  {
    id: 'event-2',
    threadId: 'thread-1',
    eventType: 'decision',
    actor: mockPrincipals[1],
    payload: { action: 'analyze_objective' },
    occurredAt: '2026-03-24T09:01:00Z',
    description: '分析目标并制定计划',
    decisionTrace: {
      relationshipRisk: 'medium',
      actionRisk: 'low',
      contentRisk: 'low',
      consequenceRisk: 'low',
      finalDecision: 'draft_first',
      policyRulesHit: ['external_candidate_policy', 'first_contact_rule'],
      confidence: 0.85,
    },
  },
  {
    id: 'event-3',
    threadId: 'thread-1',
    eventType: 'message',
    actor: mockPrincipals[1],
    payload: { draftStatus: 'ready' },
    occurredAt: '2026-03-24T09:05:00Z',
    description: '生成邮件草稿',
  },
  {
    id: 'event-4',
    threadId: 'thread-1',
    eventType: 'approval',
    actor: mockPrincipals[1],
    payload: { approvalRequestId: 'approval-1' },
    occurredAt: '2026-03-24T14:30:00Z',
    description: '提交审批请求',
  },
];

export function getReplayEventsByThreadId(threadId: string): ThreadEvent[] {
  return mockReplayEvents.filter((e) => e.threadId === threadId);
}
