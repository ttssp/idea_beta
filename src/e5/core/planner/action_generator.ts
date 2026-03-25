/**
 * Action Generator - 动作计划生成器
 */

import type { ThreadContext, ActionPlan, ActionStep, ParsedGoal } from '../../types/index.js';
import { llmClient } from '../../llm/client.js';
import { promptLibrary } from '../../prompts/library.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';

export class ActionGenerator {
  async generate(
    context: ThreadContext,
    parsedGoal?: ParsedGoal
  ): Promise<ActionPlan> {
    const startTime = Date.now();
    logger.debug('Generating action plan', { threadId: context.threadId });

    try {
      const template = promptLibrary.getTemplate('planner.action_generator');
      if (!template) {
        throw new Error('Action generator template not found');
      }

      const rendered = promptLibrary.renderTemplate(template, {
        threadContext: context,
        parsedGoal,
        userInput: context.objective,
      });

      const result = await llmClient.generate(
        [
          { role: 'system', content: rendered.system },
          { role: 'user', content: this.buildUserPrompt(context, parsedGoal) },
        ],
        {
          model: config.llm.defaultModel,
          temperature: config.llm.temperature.planning,
          responseFormat: { type: 'json_object' },
        }
      );

      const plan = this.validateAndParse(result.content, context.objective);

      logger.info('Action plan generated', {
        threadId: context.threadId,
        stepsCount: plan.steps.length,
        confidence: plan.confidence,
        latencyMs: Date.now() - startTime,
      });

      return plan;
    } catch (error) {
      logger.error('Action plan generation failed', { error, threadId: context.threadId });
      return this.fallbackGenerate(context, parsedGoal);
    }
  }

  private buildUserPrompt(context: ThreadContext, parsedGoal?: ParsedGoal): string {
    let prompt = `## 线程目标\n${context.objective}\n\n`;

    if (parsedGoal) {
      prompt += `## 解析后的目标\n${JSON.stringify(parsedGoal, null, 2)}\n\n`;
    }

    prompt += `## 当前状态\n${context.currentState}\n\n`;

    if (context.messageHistory.length > 0) {
      prompt += `## 历史消息 (最近5条)\n`;
      const recentMessages = context.messageHistory.slice(-5);
      for (const msg of recentMessages) {
        prompt += `- [${msg.timestamp}] ${msg.senderId}: ${msg.content.substring(0, 100)}\n`;
      }
    }

    prompt += `\n请基于以上信息生成动作计划。`;
    return prompt;
  }

  private validateAndParse(content: string, objective: string): ActionPlan {
    try {
      const parsed = JSON.parse(content) as {
        objective?: string;
        steps?: Array<{
          id?: string;
          type?: ActionStep['type'];
          description?: string;
          dependencies?: string[];
          suggestedTemplate?: string;
          requiresApproval?: boolean;
          estimatedDelayMinutes?: number;
        }>;
        estimatedDuration?: string;
        risks?: string[];
        confidence?: number;
        suggestedPack?: string;
      };

      const steps: ActionStep[] = (parsed.steps || []).map((step, index) => ({
        id: step.id || `step_${index + 1}`,
        type: step.type || 'draft_message',
        description: step.description || '',
        dependencies: step.dependencies || [],
        suggestedTemplate: step.suggestedTemplate,
        requiresApproval: step.requiresApproval !== false,
        estimatedDelayMinutes: step.estimatedDelayMinutes,
      }));

      return {
        objective: parsed.objective || objective,
        steps,
        estimatedDuration: parsed.estimatedDuration,
        risks: parsed.risks || [],
        confidence: parsed.confidence || 0.7,
        suggestedPack: parsed.suggestedPack,
      };
    } catch (error) {
      logger.warn('Failed to parse LLM output, using structure', { error });
      throw error;
    }
  }

  private fallbackGenerate(context: ThreadContext, parsedGoal?: ParsedGoal): ActionPlan {
    const pack = parsedGoal?.suggestedPack || 'custom';

    let steps: ActionStep[];

    switch (pack) {
      case 'time_coordination':
        steps = this.getTimeCoordinationSteps();
        break;
      case 'info_collection':
        steps = this.getInfoCollectionSteps();
        break;
      case 'follow_up':
        steps = this.getFollowUpSteps();
        break;
      default:
        steps = this.getDefaultSteps();
    }

    return {
      objective: context.objective,
      steps,
      estimatedDuration: '3-5天',
      risks: ['需要人工确认关键步骤'],
      confidence: 0.6,
      suggestedPack: pack,
    };
  }

  private getTimeCoordinationSteps(): ActionStep[] {
    return [
      {
        id: 'collect_calendars',
        type: 'collect_info',
        description: '收集所有参与者的日历可用时间',
        dependencies: [],
        requiresApproval: false,
      },
      {
        id: 'generate_proposal',
        type: 'draft_message',
        description: '起草包含候选时间的邮件',
        dependencies: ['collect_calendars'],
        suggestedTemplate: 'time_proposal',
        requiresApproval: true,
      },
      {
        id: 'send_proposal',
        type: 'send_message',
        description: '发送时间提议邮件',
        dependencies: ['generate_proposal'],
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
    ];
  }

  private getInfoCollectionSteps(): ActionStep[] {
    return [
      {
        id: 'draft_request',
        type: 'draft_message',
        description: '起草资料请求邮件',
        dependencies: [],
        suggestedTemplate: 'info_request',
        requiresApproval: true,
      },
      {
        id: 'send_request',
        type: 'send_message',
        description: '发送资料请求',
        dependencies: ['draft_request'],
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
    ];
  }

  private getFollowUpSteps(): ActionStep[] {
    return [
      {
        id: 'check_status',
        type: 'collect_info',
        description: '检查当前状态',
        dependencies: [],
        requiresApproval: false,
      },
      {
        id: 'draft_reminder',
        type: 'draft_message',
        description: '起草提醒邮件',
        dependencies: ['check_status'],
        suggestedTemplate: 'followup_reminder',
        requiresApproval: true,
      },
      {
        id: 'send_reminder',
        type: 'send_message',
        description: '发送提醒',
        dependencies: ['draft_reminder'],
        requiresApproval: true,
      },
    ];
  }

  private getDefaultSteps(): ActionStep[] {
    return [
      {
        id: 'understand',
        type: 'collect_info',
        description: '理解需求并收集必要信息',
        dependencies: [],
        requiresApproval: false,
      },
      {
        id: 'draft',
        type: 'draft_message',
        description: '起草沟通内容',
        dependencies: ['understand'],
        requiresApproval: true,
      },
    ];
  }
}

export const actionGenerator = new ActionGenerator();
export default actionGenerator;
