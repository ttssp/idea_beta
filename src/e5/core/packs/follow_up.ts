/**
 * Follow Up Pack - 跟进催办能力包
 */

import type { ThreadContext, ActionPlan, ActionStep } from '../../types/index.js';
import type { CapabilityPack } from './time_coordination.js';

export class FollowUpPack implements CapabilityPack {
  readonly id = 'follow_up';
  readonly name = '跟进催办';

  canHandle(context: ThreadContext): number {
    const keywords = [
      '跟进', '催办', '提醒', 'follow', 'remind', '催促',
      '进度', '状态', '确认', 'update', 'status', 'check in'
    ];
    const lowerObjective = context.objective.toLowerCase();
    const hasKeyword = keywords.some(k =>
      lowerObjective.includes(k.toLowerCase())
    );
    return hasKeyword ? 0.9 : 0.1;
  }

  async generatePlan(context: ThreadContext): Promise<ActionPlan> {
    const steps: ActionStep[] = [
      {
        id: 'check_status',
        type: 'collect_info',
        description: '检查当前状态和SLA',
        dependencies: [],
        requiresApproval: false,
      },
      {
        id: 'draft_reminder_friendly',
        type: 'draft_message',
        description: '起草友好提醒（第一级）',
        dependencies: ['check_status'],
        suggestedTemplate: 'followup_friendly',
        requiresApproval: true,
      },
      {
        id: 'send_reminder_1',
        type: 'send_message',
        description: '发送友好提醒',
        dependencies: ['draft_reminder_friendly'],
        requiresApproval: true,
      },
      {
        id: 'wait_1',
        type: 'wait',
        description: '等待回复（24小时）',
        dependencies: ['send_reminder_1'],
        estimatedDelayMinutes: 1440,
        requiresApproval: false,
      },
      {
        id: 'draft_reminder_formal',
        type: 'draft_message',
        description: '起草正式提醒（第二级，语气升级）',
        dependencies: ['wait_1'],
        suggestedTemplate: 'followup_formal',
        requiresApproval: true,
      },
      {
        id: 'send_reminder_2',
        type: 'send_message',
        description: '发送正式提醒',
        dependencies: ['draft_reminder_formal'],
        requiresApproval: true,
      },
      {
        id: 'wait_2',
        type: 'wait',
        description: '等待回复（48小时）',
        dependencies: ['send_reminder_2'],
        estimatedDelayMinutes: 2880,
        requiresApproval: false,
      },
      {
        id: 'escalate_or_escalate',
        type: 'escalate',
        description: '升级给人工处理',
        dependencies: ['wait_2'],
        requiresApproval: false,
      },
    ];

    return {
      objective: context.objective,
      steps,
      estimatedDuration: '3-5天',
      risks: [
        '收件人一直不回复',
        '需要升级处理',
        '可能影响关系'
      ],
      confidence: 0.8,
      suggestedPack: this.id,
    };
  }

  getDraftTemplates(): string[] {
    return [
      'followup_friendly',
      'followup_formal',
      'followup_urgent',
      'status_check'
    ];
  }
}

export const followUpPack = new FollowUpPack();
export default followUpPack;
