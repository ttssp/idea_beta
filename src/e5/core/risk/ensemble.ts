/**
 * Risk Ensemble Classifier - 风险分类器集成
 * 混合架构：规则优先 + LLM辅助
 */

import type {
  ClassifyRiskRequest,
  RiskClassification,
  RiskTag,
  SingleRiskClassifierResult,
} from '../../types/index.js';
import { llmClient } from '../../llm/client.js';
import { promptLibrary } from '../../prompts/library.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';
import {
  applyAllRules,
  calculateOverallRiskLevel,
  getSuggestedAction,
  type RiskRuleMatch,
} from './rules.js';

interface LLMClassificationResult {
  tags: RiskTag[];
  confidence: Record<RiskTag, number>;
  reasoning: string;
  evidence: string[];
}

export class RiskEnsembleClassifier {
  async classify(request: ClassifyRiskRequest): Promise<RiskClassification> {
    const startTime = Date.now();
    const content = request.content;

    logger.debug('Classifying risk', { contentLength: content.length });

    const ruleResults = applyAllRules(content);

    if (ruleResults.highConfidenceMatches.length > 0) {
      logger.debug('Rule-based fast path', {
        matches: ruleResults.highConfidenceMatches.map(m => m.tag),
      });
      return this.buildResultFromRules(ruleResults.highConfidenceMatches, startTime);
    }

    if (!ruleResults.needsLLM) {
      logger.debug('Rule-based result (no LLM needed)', {
        matches: ruleResults.allMatches.filter(m => m.matched).map(m => m.tag),
      });
      return this.buildResultFromRules(
        ruleResults.allMatches.filter(m => m.matched),
        startTime
      );
    }

    logger.debug('Using LLM for classification');
    try {
      const llmResult = await this.classifyWithLLM(request);
      return this.buildResultFromLLM(llmResult, ruleResults.allMatches, startTime);
    } catch (error) {
      logger.error('LLM classification failed, falling back to rules', { error });
      return this.buildResultFromRules(
        ruleResults.allMatches.filter(m => m.matched),
        startTime
      );
    }
  }

  private async classifyWithLLM(request: ClassifyRiskRequest): Promise<LLMClassificationResult> {
    const template = promptLibrary.getTemplate('risk.classifier');
    if (!template) {
      throw new Error('Risk classifier template not found');
    }

    const rendered = promptLibrary.renderTemplate(template, {
      content: request.content,
      threadContext: request.threadContext,
      userInput: request.content,
    });

    const result = await llmClient.generate(
      [
        { role: 'system', content: rendered.system },
        { role: 'user', content: `请分析以下内容的风险：\n\n${request.content}` },
      ],
      {
        model: config.llm.fallbackModel,
        temperature: config.llm.temperature.classification,
        responseFormat: { type: 'json_object' },
      }
    );

    return this.parseLLMOutput(result.content);
  }

  private parseLLMOutput(content: string): LLMClassificationResult {
    try {
      const parsed = JSON.parse(content);

      const defaultConfidence: Record<RiskTag, number> = {
        amount_mentioned: 0,
        commitment_made: 0,
        conflict_detected: 0,
        privacy_exposed: 0,
        negative_emotion: 0,
        legal_terms: 0,
        uncertainty_high: 0,
      };

      return {
        tags: parsed.tags || [],
        confidence: { ...defaultConfidence, ...parsed.confidence },
        reasoning: parsed.reasoning || '',
        evidence: parsed.evidence || [],
      };
    } catch (error) {
      logger.warn('Failed to parse LLM classification output', { error });
      return {
        tags: [],
        confidence: {
          amount_mentioned: 0,
          commitment_made: 0,
          conflict_detected: 0,
          privacy_exposed: 0,
          negative_emotion: 0,
          legal_terms: 0,
          uncertainty_high: 0,
        },
        reasoning: '分类失败，无法解析模型输出',
        evidence: [],
      };
    }
  }

  private buildResultFromRules(
    matches: RiskRuleMatch[],
    startTime: number
  ): RiskClassification {
    const tags = matches.map(m => m.tag) as RiskTag[];
    const confidence: Record<RiskTag, number> = {
      amount_mentioned: 0,
      commitment_made: 0,
      conflict_detected: 0,
      privacy_exposed: 0,
      negative_emotion: 0,
      legal_terms: 0,
      uncertainty_high: 0,
    };

    for (const match of matches) {
      confidence[match.tag] = match.confidence;
    }

    const overallRiskLevel = calculateOverallRiskLevel(tags, confidence);
    const ruleNames = matches.map(m => m.ruleName);

    return {
      tags,
      confidence,
      overallRiskLevel,
      reasoning: `基于规则检测：${ruleNames.join('、')}`,
      suggestedAction: getSuggestedAction(overallRiskLevel),
      ruleMatches: ruleNames,
      modelUsed: 'rules',
    };
  }

  private buildResultFromLLM(
    llmResult: LLMClassificationResult,
    ruleMatches: RiskRuleMatch[],
    startTime: number
  ): RiskClassification {
    const tags = llmResult.tags;
    const confidence = llmResult.confidence;

    for (const rule of ruleMatches) {
      if (rule.matched && rule.confidence > confidence[rule.tag]) {
        confidence[rule.tag] = rule.confidence;
        if (!tags.includes(rule.tag)) {
          tags.push(rule.tag);
        }
      }
    }

    const overallRiskLevel = calculateOverallRiskLevel(tags, confidence);

    return {
      tags,
      confidence,
      overallRiskLevel,
      reasoning: llmResult.reasoning,
      suggestedAction: getSuggestedAction(overallRiskLevel),
      modelUsed: config.llm.fallbackModel,
    };
  }
}

export const riskEnsembleClassifier = new RiskEnsembleClassifier();
export default riskEnsembleClassifier;
