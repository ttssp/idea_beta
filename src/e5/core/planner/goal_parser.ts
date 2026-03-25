/**
 * Goal Parser - 目标解析器
 */

import { z } from 'zod';
import type { ThreadContext, ParsedGoal } from '../../types/index.js';
import { llmClient } from '../../llm/client.js';
import { promptLibrary } from '../../prompts/library.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';

const GoalSchema = z.object({
  objective: z.string(),
  keyConstraints: z.array(z.string()),
  successCriteria: z.array(z.string()),
  estimatedComplexity: z.enum(['low', 'medium', 'high']),
  suggestedPack: z.enum(['time_coordination', 'info_collection', 'follow_up', 'custom']),
});

export class GoalParser {
  async parse(
    objective: string,
    context?: Partial<ThreadContext>
  ): Promise<ParsedGoal> {
    const startTime = Date.now();
    logger.debug('Parsing goal', { objective, hasContext: !!context });

    try {
      const template = promptLibrary.getTemplate('planner.goal_parser');
      if (!template) {
        throw new Error('Goal parser template not found');
      }

      const rendered = promptLibrary.renderTemplate(template, {
        objective,
        threadContext: context,
        userInput: objective,
      });

      const result = await llmClient.generate(
        [
          { role: 'system', content: rendered.system },
          { role: 'user', content: rendered.user },
        ],
        {
          model: config.llm.defaultModel,
          temperature: config.llm.temperature.planning,
          responseFormat: { type: 'json_object' },
        }
      );

      const parsed = this.validateAndParse(result.content);

      logger.info('Goal parsed successfully', {
        objective: parsed.objective,
        complexity: parsed.estimatedComplexity,
        pack: parsed.suggestedPack,
        latencyMs: Date.now() - startTime,
      });

      return parsed;
    } catch (error) {
      logger.error('Goal parsing failed', { error, objective });
      return this.fallbackParse(objective);
    }
  }

  private validateAndParse(content: string): ParsedGoal {
    try {
      const parsed = JSON.parse(content);
      return GoalSchema.parse(parsed);
    } catch (error) {
      logger.warn('LLM output validation failed, attempting to fix', { error });
      const fixed = this.tryFixJson(content);
      return GoalSchema.parse(fixed);
    }
  }

  private tryFixJson(content: string): unknown {
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('Cannot extract valid JSON from LLM output');
  }

  private fallbackParse(objective: string): ParsedGoal {
    const lowerObjective = objective.toLowerCase();

    let suggestedPack: ParsedGoal['suggestedPack'] = 'custom';
    if (lowerObjective.includes('时间') || lowerObjective.includes('约') || lowerObjective.includes('meeting')) {
      suggestedPack = 'time_coordination';
    } else if (lowerObjective.includes('资料') || lowerObjective.includes('收集') || lowerObjective.includes('文件')) {
      suggestedPack = 'info_collection';
    } else if (lowerObjective.includes('跟进') || lowerObjective.includes('提醒') || lowerObjective.includes('催')) {
      suggestedPack = 'follow_up';
    }

    return {
      objective,
      keyConstraints: [],
      successCriteria: ['完成目标'],
      estimatedComplexity: 'medium',
      suggestedPack,
    };
  }
}

export const goalParser = new GoalParser();
export default goalParser;
