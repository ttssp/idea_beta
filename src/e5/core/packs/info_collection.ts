/**
 * Info Collection Pack - 资料收集能力包
 */

import type { ThreadContext, ActionPlan, ActionStep } from '../../types/index.js';
import type { CapabilityPack } from './time_coordination.js';

export class InfoCollectionPack implements CapabilityPack {
  readonly id = 'info_collection';
  readonly name = '资料收集';

  canHandle(context: ThreadContext): number {
    const keywords = [
      '资料', '收集', '文件', '文档', '简历', '作品集', '推荐信',
      '索取', '提供', '提交', '发送', 'material', 'document', 'collect',
      'resume', 'portfolio', 'reference'
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
        id: 'list_requirements',
        type: 'draft_message',
        description: '明确需要收集的资料清单',
        dependencies: [],
        suggestedTemplate: 'info_list',
        requiresApproval: true,
      },
      {
        id: 'send_request',
        type: 'send_message',
        description: '发送资料请求',
        dependencies: ['list_requirements'],
        requiresApproval: true,
      },
      {
        id: 'wait_reply',
        type: 'wait',
        description: '等待回复',
        dependencies: ['send_request'],
        estimatedDelayMinutes: 4320,
        requiresApproval: false,
      },
      {
        id: 'check_received',
        type: 'collect_info',
        description: '检查收到的资料',
        dependencies: ['wait_reply'],
        requiresApproval: false,
      },
      {
        id: 'confirm_or_remind',
        type: 'draft_message',
        description: '确认收到或催办缺项',
        dependencies: ['check_received'],
        suggestedTemplate: 'info_confirm',
        requiresApproval: true,
      },
    ];

    return {
      objective: context.objective,
      steps,
      estimatedDuration: '5-7天',
      risks: [
        '部分资料缺失',
        '收件人无法及时提供',
        '需要多轮催办'
      ],
      confidence: 0.85,
      suggestedPack: this.id,
    };
  }

  getDraftTemplates(): string[] {
    return ['info_list', 'info_request', 'info_confirm', 'info_reminder'];
  }
}

export const infoCollectionPack = new InfoCollectionPack();
export default infoCollectionPack;
