/**
 * Risk Rules - 规则兜底层
 * 高置信度的正则规则，快速路径
 */

import type { RiskTag, RiskLevel } from '../../types/index.js';

export interface RiskRuleMatch {
  ruleId: string;
  ruleName: string;
  tag: RiskTag;
  matched: boolean;
  confidence: number;
  reasoning: string;
  evidence: string[];
}

export interface RiskRule {
  id: string;
  name: string;
  tag: RiskTag;
  description: string;
  match: (content: string) => RiskRuleMatch;
}

const idCardRegex = /(^|[^\d])\d{17}[\dXx]([^\d]|$)/;
const bankCardRegex = /(^|[^\d])\d{16,19}([^\d]|$)/;
const phoneRegex = /(^|[^\d])1[3-9]\d{9}([^\d]|$)/;
const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;

const amountRegexes = [
  /(?:金额|价格|费用|报价|预算|支付|付款|折扣|优惠)(?:\s*[:：]\s*)?[¥￥$€£]?\s*\d+(?:[,.]\d+)*(?:\s*[万亿千百十元]*)?/gi,
  /[¥￥$€£]\s*\d+(?:[,.]\d+)*(?:\s*[万亿千百十元]*)?/g,
  /\d+(?:[,.]\d+)*\s*(?:元|美元|欧元|英镑|万|千|百)(?:?!月|日|年|个|人)/g,
];

const commitmentRegexes = [
  /(?:保证|承诺|担保|确保|约定|合同|协议|责任|违约)(?!金)/gi,
  /(?:必须|一定|务必|肯定)(?:\s+\w+){0,3}\s*(?:做|完成|实现)/gi,
  /(?:签字|签署|盖章|签订)(?:\s+\w+){0,3}\s*(?:合同|协议)/gi,
];

const conflictRegexes = [
  /(?:投诉|举报|不满|失望|生气|愤怒|恼火|可恶|过分)/gi,
  /(?:拒绝|不同意|不行|不要|反对|否决)/gi,
  /(?:争议|争论|争执|吵架|纠纷)/gi,
  /(?:责备|指责|怪罪|都是你的|怎么回事)/gi,
];

const legalRegexes = [
  /(?:起诉|诉讼|法院|法庭|律师|法务|法律顾问)/gi,
  /(?:法律|法规|违法|犯罪|刑事责任)/gi,
  /(?:保密|知识产权|专利|版权|商标)/gi,
];

const negativeEmotionRegexes = [
  /(?:糟糕|太差|不好|失望|沮丧|焦虑|担心|担忧)/gi,
  /(?:怎么回事|什么情况|搞什么|太过分了)/gi,
  /[!?！？]{2,}/g,
];

export const privacyRule: RiskRule = {
  id: 'privacy_sensitive_info',
  name: '隐私敏感信息检测',
  tag: 'privacy_exposed',
  description: '检测身份证号、银行卡号、手机号等敏感个人信息',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    if (idCardRegex.test(content)) {
      evidence.push('检测到身份证号格式');
    }
    if (bankCardRegex.test(content)) {
      evidence.push('检测到银行卡号格式');
    }
    if (phoneRegex.test(content)) {
      evidence.push('检测到手机号');
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'privacy_sensitive_info',
        ruleName: '隐私敏感信息检测',
        tag: 'privacy_exposed',
        matched: true,
        confidence: 0.999,
        reasoning: `检测到敏感个人信息：${evidence.join('、')}`,
        evidence,
      };
    }

    return {
      ruleId: 'privacy_sensitive_info',
      ruleName: '隐私敏感信息检测',
      tag: 'privacy_exposed',
      matched: false,
      confidence: 0,
      reasoning: '未检测到敏感个人信息',
      evidence: [],
    };
  },
};

export const amountRule: RiskRule = {
  id: 'amount_mentioned',
  name: '金额提及检测',
  tag: 'amount_mentioned',
  description: '检测金额、价格、费用等提及',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    for (const regex of amountRegexes) {
      const matches = content.match(regex);
      if (matches) {
        evidence.push(...matches.slice(0, 3));
      }
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'amount_mentioned',
        ruleName: '金额提及检测',
        tag: 'amount_mentioned',
        matched: true,
        confidence: 0.95,
        reasoning: `检测到金额相关内容：${evidence.slice(0, 2).join('、')}`,
        evidence: [...new Set(evidence)],
      };
    }

    return {
      ruleId: 'amount_mentioned',
      ruleName: '金额提及检测',
      tag: 'amount_mentioned',
      matched: false,
      confidence: 0,
      reasoning: '未检测到金额相关内容',
      evidence: [],
    };
  },
};

export const commitmentRule: RiskRule = {
  id: 'commitment_made',
  name: '承诺/合同检测',
  tag: 'commitment_made',
  description: '检测承诺、合同、法律相关内容',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    for (const regex of commitmentRegexes) {
      const matches = content.match(regex);
      if (matches) {
        evidence.push(...matches.slice(0, 3));
      }
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'commitment_made',
        ruleName: '承诺/合同检测',
        tag: 'commitment_made',
        matched: true,
        confidence: 0.9,
        reasoning: `检测到承诺/合同相关内容：${evidence.slice(0, 2).join('、')}`,
        evidence: [...new Set(evidence)],
      };
    }

    return {
      ruleId: 'commitment_made',
      ruleName: '承诺/合同检测',
      tag: 'commitment_made',
      matched: false,
      confidence: 0,
      reasoning: '未检测到承诺/合同相关内容',
      evidence: [],
    };
  },
};

export const conflictRule: RiskRule = {
  id: 'conflict_detected',
  name: '冲突/争议检测',
  tag: 'conflict_detected',
  description: '检测冲突、争议、投诉等内容',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    for (const regex of conflictRegexes) {
      const matches = content.match(regex);
      if (matches) {
        evidence.push(...matches.slice(0, 3));
      }
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'conflict_detected',
        ruleName: '冲突/争议检测',
        tag: 'conflict_detected',
        matched: true,
        confidence: 0.85,
        reasoning: `检测到冲突/争议相关内容：${evidence.slice(0, 2).join('、')}`,
        evidence: [...new Set(evidence)],
      };
    }

    return {
      ruleId: 'conflict_detected',
      ruleName: '冲突/争议检测',
      tag: 'conflict_detected',
      matched: false,
      confidence: 0,
      reasoning: '未检测到冲突/争议相关内容',
      evidence: [],
    };
  },
};

export const legalRule: RiskRule = {
  id: 'legal_terms',
  name: '法律条款检测',
  tag: 'legal_terms',
  description: '检测法律相关内容',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    for (const regex of legalRegexes) {
      const matches = content.match(regex);
      if (matches) {
        evidence.push(...matches.slice(0, 3));
      }
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'legal_terms',
        ruleName: '法律条款检测',
        tag: 'legal_terms',
        matched: true,
        confidence: 0.85,
        reasoning: `检测到法律相关内容：${evidence.slice(0, 2).join('、')}`,
        evidence: [...new Set(evidence)],
      };
    }

    return {
      ruleId: 'legal_terms',
      ruleName: '法律条款检测',
      tag: 'legal_terms',
      matched: false,
      confidence: 0,
      reasoning: '未检测到法律相关内容',
      evidence: [],
    };
  },
};

export const negativeEmotionRule: RiskRule = {
  id: 'negative_emotion',
  name: '负面情绪检测',
  tag: 'negative_emotion',
  description: '检测负面情绪表达',
  match: (content: string): RiskRuleMatch => {
    const evidence: string[] = [];

    for (const regex of negativeEmotionRegexes) {
      const matches = content.match(regex);
      if (matches) {
        evidence.push(...matches.slice(0, 3));
      }
    }

    if (evidence.length > 0) {
      return {
        ruleId: 'negative_emotion',
        ruleName: '负面情绪检测',
        tag: 'negative_emotion',
        matched: true,
        confidence: 0.7,
        reasoning: `检测到负面情绪表达：${evidence.slice(0, 2).join('、')}`,
        evidence: [...new Set(evidence)],
      };
    }

    return {
      ruleId: 'negative_emotion',
      ruleName: '负面情绪检测',
      tag: 'negative_emotion',
      matched: false,
      confidence: 0,
      reasoning: '未检测到负面情绪表达',
      evidence: [],
    };
  },
};

export const allRules: RiskRule[] = [
  privacyRule,
  amountRule,
  commitmentRule,
  conflictRule,
  legalRule,
  negativeEmotionRule,
];

export function applyAllRules(content: string): {
  highConfidenceMatches: RiskRuleMatch[];
  allMatches: RiskRuleMatch[];
  needsLLM: boolean;
} {
  const allMatches = allRules.map(rule => rule.match(content));
  const highConfidenceMatches = allMatches.filter(
    m => m.matched && m.confidence >= 0.9
  );

  const hasCriticalPrivacy = highConfidenceMatches.some(
    m => m.tag === 'privacy_exposed'
  );

  const needsLLM = !hasCriticalPrivacy && highConfidenceMatches.length === 0;

  return {
    highConfidenceMatches,
    allMatches,
    needsLLM,
  };
}

export function calculateOverallRiskLevel(
  tags: string[],
  confidences: Record<string, number>
): RiskLevel {
  if (tags.includes('privacy_exposed')) {
    return 'critical';
  }

  const highRiskTags = ['commitment_made', 'legal_terms', 'conflict_detected'];
  const hasHighRisk = tags.some(t => highRiskTags.includes(t) && confidences[t] >= 0.8);

  if (hasHighRisk) {
    return 'high';
  }

  if (tags.includes('amount_mentioned') || tags.includes('negative_emotion')) {
    return 'medium';
  }

  return 'low';
}

export function getSuggestedAction(riskLevel: RiskLevel): 'allow' | 'draft_only' | 'require_approval' | 'escalate' | 'deny' {
  switch (riskLevel) {
    case 'critical':
      return 'escalate';
    case 'high':
      return 'require_approval';
    case 'medium':
      return 'draft_only';
    case 'low':
      return 'allow';
  }
}
