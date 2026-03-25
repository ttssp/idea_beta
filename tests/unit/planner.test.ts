/**
 * Planner 单元测试
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GoalParser } from '../../src/e5/core/planner/goal_parser.js';

vi.mock('../../src/e5/llm/client.js', () => ({
  llmClient: {
    generate: vi.fn(),
  },
}));

describe('GoalParser', () => {
  let parser: GoalParser;

  beforeEach(() => {
    parser = new GoalParser();
  });

  describe('fallbackParse', () => {
    it('should detect time coordination pack', async () => {
      const result = await parser.parse('帮我协调一下面试时间', {});
      expect(result.suggestedPack).toBe('time_coordination');
    });

    it('should detect info collection pack', async () => {
      const result = await parser.parse('请收集一下候选人的资料', {});
      expect(result.suggestedPack).toBe('info_collection');
    });

    it('should detect follow up pack', async () => {
      const result = await parser.parse('帮我跟进一下供应商的进度', {});
      expect(result.suggestedPack).toBe('follow_up');
    });

    it('should use custom pack for unknown objectives', async () => {
      const result = await parser.parse('这是一个自定义任务', {});
      expect(result.suggestedPack).toBe('custom');
    });
  });
});
