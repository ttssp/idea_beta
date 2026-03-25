/**
 * Risk Classifier 单元测试
 */

import { describe, it, expect } from 'vitest';
import {
  privacyRule,
  amountRule,
  commitmentRule,
  applyAllRules,
  calculateOverallRiskLevel,
  getSuggestedAction,
} from '../../src/e5/core/risk/rules.js';

describe('Risk Rules', () => {
  describe('privacyRule', () => {
    it('should detect ID card number', () => {
      const result = privacyRule.match('我的身份证号是110101199001011234');
      expect(result.matched).toBe(true);
      expect(result.tag).toBe('privacy_exposed');
      expect(result.confidence).toBeGreaterThan(0.9);
    });

    it('should detect bank card number', () => {
      const result = privacyRule.match('请转账到6222021234567890123');
      expect(result.matched).toBe(true);
      expect(result.tag).toBe('privacy_exposed');
    });

    it('should not flag normal content', () => {
      const result = privacyRule.match('你好，我们什么时候见面？');
      expect(result.matched).toBe(false);
    });
  });

  describe('amountRule', () => {
    it('should detect amount with currency symbol', () => {
      const result = amountRule.match('这个项目的价格是¥50000');
      expect(result.matched).toBe(true);
      expect(result.tag).toBe('amount_mentioned');
    });

    it('should detect amount with Chinese units', () => {
      const result = amountRule.match('费用大约是5万元');
      expect(result.matched).toBe(true);
    });
  });

  describe('commitmentRule', () => {
    it('should detect commitment words', () => {
      const result = commitmentRule.match('我保证明天一定完成');
      expect(result.matched).toBe(true);
      expect(result.tag).toBe('commitment_made');
    });
  });

  describe('applyAllRules', () => {
    it('should apply all rules and return matches', () => {
      const result = applyAllRules('我的身份证号是110101199001011234');
      expect(result.highConfidenceMatches.length).toBeGreaterThan(0);
      expect(result.needsLLM).toBe(false);
    });

    it('should need LLM for ambiguous content', () => {
      const result = applyAllRules('你好，我们可以聊聊吗？');
      expect(result.needsLLM).toBe(true);
    });
  });

  describe('calculateOverallRiskLevel', () => {
    it('should return critical for privacy exposure', () => {
      const level = calculateOverallRiskLevel(
        ['privacy_exposed'],
        { privacy_exposed: 0.99 }
      );
      expect(level).toBe('critical');
    });

    it('should return high for commitment + amount', () => {
      const level = calculateOverallRiskLevel(
        ['commitment_made', 'amount_mentioned'],
        { commitment_made: 0.9, amount_mentioned: 0.8 }
      );
      expect(level).toBe('high');
    });

    it('should return low for no risks', () => {
      const level = calculateOverallRiskLevel([], {});
      expect(level).toBe('low');
    });
  });

  describe('getSuggestedAction', () => {
    it('should escalate for critical risk', () => {
      expect(getSuggestedAction('critical')).toBe('escalate');
    });

    it('should require approval for high risk', () => {
      expect(getSuggestedAction('high')).toBe('require_approval');
    });

    it('should allow for low risk', () => {
      expect(getSuggestedAction('low')).toBe('allow');
    });
  });
});
