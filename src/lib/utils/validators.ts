import { z } from 'zod';

export const createThreadSchema = z.object({
  title: z.string().min(1, '标题不能为空').max(200, '标题不能超过200个字符'),
  objective: z.string().min(1, '目标不能为空').max(2000, '目标不能超过2000个字符'),
  participants: z.array(z.string()).min(1, '至少需要一个参与者'),
  delegationProfile: z.enum([
    'observe_only',
    'draft_first',
    'approve_to_send',
    'bounded_auto',
    'human_only',
  ]),
});

export const approvalResolutionSchema = z.object({
  status: z.enum(['approved', 'rejected', 'modified', 'takeover']),
  modifiedContent: z.string().optional(),
  comment: z.string().optional(),
});

export const delegationProfileSchema = z.object({
  profileName: z.string().min(1, '名称不能为空'),
  allowedActions: z.array(z.string()).min(1, '至少允许一个动作'),
  budget: z.object({
    maxMessagesPerDay: z.number().min(0),
    maxActionsPerDay: z.number().min(0),
    maxContinuousTouches: z.number().min(0),
    timeWindowMinutes: z.number().min(1),
  }),
  escalationRules: z.array(z.string()),
});

export type CreateThreadInput = z.infer<typeof createThreadSchema>;
export type ApprovalResolutionInput = z.infer<typeof approvalResolutionSchema>;
export type DelegationProfileInput = z.infer<typeof delegationProfileSchema>;
