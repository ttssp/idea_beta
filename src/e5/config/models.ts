/**
 * LLM 模型配置
 */

export interface ModelConfig {
  id: string;
  provider: 'openai' | 'anthropic';
  name: string;
  description: string;
  capabilities: {
    planning: boolean;
    drafting: boolean;
    classification: boolean;
    summary: boolean;
  };
  maxTokens: number;
  costPer1kInputTokens: number;
  costPer1kOutputTokens: number;
  estimatedLatencyMs: {
    p50: number;
    p95: number;
    p99: number;
  };
}

export const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'gpt-4o': {
    id: 'gpt-4o',
    provider: 'openai',
    name: 'GPT-4o',
    description: 'OpenAI GPT-4o - 主力模型，平衡质量和速度',
    capabilities: {
      planning: true,
      drafting: true,
      classification: true,
      summary: true,
    },
    maxTokens: 128000,
    costPer1kInputTokens: 0.01,
    costPer1kOutputTokens: 0.03,
    estimatedLatencyMs: {
      p50: 1500,
      p95: 3000,
      p99: 5000,
    },
  },

  'gpt-4o-mini': {
    id: 'gpt-4o-mini',
    provider: 'openai',
    name: 'GPT-4o Mini',
    description: 'OpenAI GPT-4o Mini - 分类和简单任务',
    capabilities: {
      planning: false,
      drafting: true,
      classification: true,
      summary: true,
    },
    maxTokens: 128000,
    costPer1kInputTokens: 0.00015,
    costPer1kOutputTokens: 0.0006,
    estimatedLatencyMs: {
      p50: 500,
      p95: 1500,
      p99: 2500,
    },
  },

  'claude-3-5-sonnet': {
    id: 'claude-3-5-sonnet',
    provider: 'anthropic',
    name: 'Claude 3.5 Sonnet',
    description: 'Anthropic Claude 3.5 Sonnet - 替代主力模型',
    capabilities: {
      planning: true,
      drafting: true,
      classification: true,
      summary: true,
    },
    maxTokens: 200000,
    costPer1kInputTokens: 0.003,
    costPer1kOutputTokens: 0.015,
    estimatedLatencyMs: {
      p50: 2000,
      p95: 4000,
      p99: 6000,
    },
  },
};

export function getModelForTask(task: 'planning' | 'drafting' | 'classification' | 'summary'): string {
  switch (task) {
    case 'planning':
      return 'gpt-4o';
    case 'drafting':
      return 'gpt-4o';
    case 'classification':
      return 'gpt-4o-mini';
    case 'summary':
      return 'gpt-4o-mini';
  }
}

export function getFallbackModel(primaryModel: string): string {
  const model = MODEL_CONFIGS[primaryModel];
  if (!model) return 'gpt-4o-mini';

  if (model.provider === 'openai') {
    return primaryModel === 'gpt-4o' ? 'gpt-4o-mini' : 'gpt-4o';
  }
  return 'gpt-4o-mini';
}
