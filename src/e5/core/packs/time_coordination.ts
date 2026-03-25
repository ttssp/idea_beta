/**
 * Time Coordination Pack - 时间协调能力包
 */

import type { ThreadContext, ActionPlan, ActionStep } from '../../types/index.js';

export interface CapabilityPack {
  readonly id: string;
  readonly name: string;
  canHandle(context: ThreadContext): number;
  generatePlan(context: ThreadContext): Promise<ActionPlan>;
  getDraftTemplates(): string[];
}

export class TimeCoordinationPack implements CapabilityPack {
  readonly id = 'time_coordination';
  readonly name = '时间协调';

  canHandle(context: ThreadContext): number {
    const keywords = [
      '时间', '约见', '会议', '日程', 'schedule', 'meeting',
      '安排', '协调', '改期', '确认', 'calendar'
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
        id: 'collect_calendars',
        type: 'collect_info',
        description: '收集所有参与者的日历可用时间',
        dependencies: [],
        requiresApproval: false,
      },
      {
        id: 'generate_slots',
        type: 'draft_message',
        description: '生成候选时间提议',
        dependencies: ['collect_calendars'],
        suggestedTemplate: 'time_proposal',
        requiresApproval: true,
      },
      {
        id: 'send_proposal',
        type: 'send_message',
        description: '发送时间提议',
        dependencies: ['generate_slots'],
        requiresApproval: true,
      },
      {
        id: 'wait_reply',
        type: 'wait',
        description: '等待回复',
        dependencies: ['send_proposal'],
        estimatedDelayMinutes: 2880,
        requiresApproval: false,
      },
      {
        id: 'confirm_or_adjust',
        type: 'draft_message',
        description: '确认最终时间或提出调整',
        dependencies: ['wait_reply'],
        suggestedTemplate: 'time_confirmation',
        requiresApproval: true,
      },
    ];

    return {
      objective: context.objective,
      steps,
      estimatedDuration: '3-5天',
      risks: [
        '参与者时间冲突',
        '部分参与者无法及时回复',
        '需要多轮调整'
      ],
      confidence: 0.85,
      suggestedPack: this.id,
    };
  }

  getDraftTemplates(): string[] {
    return ['time_proposal', 'time_confirmation', 'time_reschedule'];
  }
}

export const timeCoordinationPack = new TimeCoordinationPack();
export default timeCoordinationPack;
