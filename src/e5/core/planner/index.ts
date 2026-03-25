/**
 * Planner 模块导出
 */

export { GoalParser, goalParser } from './goal_parser.js';
export { ActionGenerator, actionGenerator } from './action_generator.js';

import type { ThreadContext, ActionPlan, NextActionSuggestion, ParsedGoal } from '../../types/index.js';
import { goalParser } from './goal_parser.js';
import { actionGenerator } from './action_generator.js';
import { logger } from '../../utils/logger.js';

export class ThreadPlanner {
  async plan(context: ThreadContext): Promise<{
    plan: ActionPlan;
    parsedGoal: ParsedGoal;
    reasoning: string;
  }> {
    const startTime = Date.now();
    logger.info('Planning thread', { threadId: context.threadId });

    const parsedGoal = await goalParser.parse(context.objective, context);
    const plan = await actionGenerator.generate(context, parsedGoal);

    return {
      plan,
      parsedGoal,
      reasoning: `基于目标分析，使用${parsedGoal.suggestedPack}策略生成了${plan.steps.length}步动作计划。`,
    };
  }

  async suggestNext(context: ThreadContext): Promise<NextActionSuggestion> {
    const plan = await actionGenerator.generate(context);
    const nextStep = plan.steps[0];

    if (!nextStep) {
      return {
        action: {
          id: 'wait',
          type: 'wait',
          description: '等待更多信息',
          requiresApproval: false,
        },
        reasoning: '当前没有明确的下一步动作，建议等待更多信息',
        urgency: 'low',
      };
    }

    return {
      action: nextStep,
      reasoning: '根据当前线程状态，建议执行此动作',
      urgency: this.calculateUrgency(context),
    };
  }

  private calculateUrgency(context: ThreadContext): 'low' | 'medium' | 'high' {
    const state = context.currentState;
    if (state === 'awaiting_approval') return 'high';
    if (state === 'blocked') return 'high';
    if (state === 'awaiting_external') return 'low';
    return 'medium';
  }
}

export const threadPlanner = new ThreadPlanner();
export default threadPlanner;
