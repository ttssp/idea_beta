import type { Thread } from './thread';

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'modified' | 'takeover';

export type ApprovalRequestType = 'send_message' | 'execute_action' | 'modify_profile';

export interface ApprovalRequest {
  id: string;
  threadId: string;
  requestType: ApprovalRequestType;
  reasonCode: string;
  reasonDescription: string;
  preview: {
    content: string;
    recipient: string;
    channel: string;
  };
  triggeringRule?: string;
  riskReason?: string;
  status: ApprovalStatus;
  approverId?: string;
  createdAt: string;
  resolvedAt?: string;
  thread?: Thread;
}

export const APPROVAL_STATUS_LABELS: Record<ApprovalStatus, string> = {
  pending: '待处理',
  approved: '已批准',
  rejected: '已拒绝',
  modified: '已修改',
  takeover: '已接管',
};

export const APPROVAL_REQUEST_TYPE_LABELS: Record<ApprovalRequestType, string> = {
  send_message: '发送消息',
  execute_action: '执行动作',
  modify_profile: '修改配置',
};

export interface ApprovalResolution {
  status: Exclude<ApprovalStatus, 'pending'>;
  modifiedContent?: string;
  comment?: string;
}
