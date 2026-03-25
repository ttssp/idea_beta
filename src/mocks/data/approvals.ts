import type { ApprovalRequest } from '@/lib/types/approval';

export const mockApprovals: ApprovalRequest[] = [
  {
    id: 'approval-1',
    threadId: 'thread-1',
    requestType: 'send_message',
    reasonCode: 'new_candidate_communication',
    reasonDescription: '向新候选人发送面试邀请',
    preview: {
      content:
        '您好李华，感谢您通过初试。我们想邀请您参加终面，下周三下午2点或周四上午10点您哪个时间方便？',
      recipient: '李华 <lihua@example.com>',
      channel: 'email',
    },
    triggeringRule: 'external_candidate_first_contact',
    riskReason: '首次与外部候选人沟通，建议人工确认',
    status: 'pending',
    createdAt: '2026-03-24T14:30:00Z',
  },
  {
    id: 'approval-2',
    threadId: 'thread-2',
    requestType: 'execute_action',
    reasonCode: 'scheduled_followup',
    reasonDescription: '发送跟进提醒',
    preview: {
      content: '提醒：请在明天中午前提交Q1项目报告，谢谢！',
      recipient: '团队成员',
      channel: 'internal',
    },
    triggeringRule: 'auto_followup_scheduled',
    status: 'pending',
    createdAt: '2026-03-24T10:00:00Z',
  },
];

export function getApprovalById(id: string): ApprovalRequest | undefined {
  return mockApprovals.find((a) => a.id === id);
}

export function getApprovalsByThreadId(threadId: string): ApprovalRequest[] {
  return mockApprovals.filter((a) => a.threadId === threadId);
}
