/**
 * Risk Classification 相关类型定义
 * 与E2 Risk Engine对接
 */

export type RiskTag =
  | 'amount_mentioned'
  | 'commitment_made'
  | 'conflict_detected'
  | 'privacy_exposed'
  | 'negative_emotion'
  | 'legal_terms'
  | 'uncertainty_high';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface RiskClassification {
  tags: RiskTag[];
  confidence: Record<RiskTag, number>;
  overallRiskLevel: RiskLevel;
  reasoning: string;
  suggestedAction: 'allow' | 'draft_only' | 'require_approval' | 'escalate' | 'deny';
  ruleMatches?: string[];
  modelUsed?: string;
}

export interface ClassifyRiskRequest {
  content: string;
  threadContext?: Partial<import('./thread.js').ThreadContext>;
  contextType?: 'email' | 'message' | 'draft' | 'plan';
}

export interface RiskRuleMatch {
  ruleId: string;
  ruleName: string;
  matched: boolean;
  confidence: number;
  details?: string;
}

export interface SingleRiskClassifierResult {
  tag: RiskTag;
  detected: boolean;
  confidence: number;
  reasoning: string;
  evidence: string[];
}
