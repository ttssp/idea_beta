/**
 * LLM 客户端抽象层
 * 支持多模型、重试、缓存、降级
 */

import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { config } from '../config/index.js';
import { MODEL_CONFIGS, getModelForTask, getFallbackModel, type ModelConfig } from '../config/models.js';
import { llmLogger } from '../utils/logger.js';
import { createHash } from 'crypto';

export interface LLMMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  toolCallId?: string;
}

export interface LLMGenerateOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  responseFormat?: { type: 'text' | 'json_object' };
  stop?: string[];
  timeoutMs?: number;
  useCache?: boolean;
  useFallback?: boolean;
}

export interface LLMGenerateResult {
  content: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  latencyMs: number;
  cached: boolean;
}

export interface LLMClient {
  generate(
    messages: LLMMessage[],
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult>;
}

export class MultiModelLLMClient implements LLMClient {
  private openaiClient: OpenAI | null = null;
  private anthropicClient: Anthropic | null = null;
  private cache: LLMResponseCache | null = null;

  constructor() {
    this.initializeClients();
    if (config.cache.enabled) {
      this.cache = new LLMResponseCache();
    }
  }

  private initializeClients(): void {
    if (config.llm.openai.apiKey) {
      this.openaiClient = new OpenAI({
        apiKey: config.llm.openai.apiKey,
        baseURL: config.llm.openai.baseURL,
      });
      llmLogger.info('OpenAI client initialized');
    }

    if (config.llm.anthropic.apiKey) {
      this.anthropicClient = new Anthropic({
        apiKey: config.llm.anthropic.apiKey,
        baseURL: config.llm.anthropic.baseURL,
      });
      llmLogger.info('Anthropic client initialized');
    }
  }

  async generate(
    messages: LLMMessage[],
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult> {
    const startTime = Date.now();
    const modelId = options?.model || config.llm.defaultModel;
    const modelConfig = MODEL_CONFIGS[modelId];

    if (!modelConfig) {
      throw new Error(`Unknown model: ${modelId}`);
    }

    const cacheKey = options?.useCache !== false
      ? this.getCacheKey(messages, { ...options, model: modelId })
      : null;

    if (cacheKey && this.cache) {
      const cached = await this.cache.get(cacheKey);
      if (cached) {
        llmLogger.debug('LLM cache hit', { model: modelId, key: cacheKey });
        return {
          ...cached,
          latencyMs: Date.now() - startTime,
          cached: true,
        };
      }
    }

    try {
      const result = await this.generateWithRetry(messages, modelId, modelConfig, options);

      if (cacheKey && this.cache) {
        await this.cache.set(cacheKey, result);
      }

      return {
        ...result,
        latencyMs: Date.now() - startTime,
        cached: false,
      };
    } catch (error) {
      if (options?.useFallback !== false) {
        const fallbackModel = getFallbackModel(modelId);
        if (fallbackModel !== modelId) {
          llmLogger.warn('Falling back to backup model', {
            primary: modelId,
            fallback: fallbackModel,
            error,
          });
          return this.generate(messages, {
            ...options,
            model: fallbackModel,
            useFallback: false,
          });
        }
      }
      throw error;
    }
  }

  private async generateWithRetry(
    messages: LLMMessage[],
    modelId: string,
    modelConfig: ModelConfig,
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult> {
    const maxRetries = config.llm.retry.maxRetries;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await this.generateOnce(messages, modelId, modelConfig, options);
      } catch (error) {
        lastError = error as Error;
        if (attempt < maxRetries) {
          const delay = Math.min(
            config.llm.retry.initialDelayMs * Math.pow(2, attempt),
            config.llm.retry.maxDelayMs
          );
          llmLogger.warn('LLM retry', {
            model: modelId,
            attempt,
            delayMs: delay,
            error: lastError.message,
          });
          await this.sleep(delay);
        }
      }
    }

    throw lastError;
  }

  private async generateOnce(
    messages: LLMMessage[],
    modelId: string,
    modelConfig: ModelConfig,
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult> {
    const startTime = Date.now();

    if (modelConfig.provider === 'openai') {
      return this.generateWithOpenAI(messages, modelId, options);
    } else if (modelConfig.provider === 'anthropic') {
      return this.generateWithAnthropic(messages, modelId, options);
    }

    throw new Error(`Unsupported provider: ${modelConfig.provider}`);
  }

  private async generateWithOpenAI(
    messages: LLMMessage[],
    modelId: string,
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult> {
    if (!this.openaiClient) {
      throw new Error('OpenAI client not initialized');
    }

    const response = await this.openaiClient.chat.completions.create({
      model: modelId,
      messages: messages.map(m => ({
        role: m.role === 'tool' ? 'assistant' : m.role,
        content: m.content,
      })),
      temperature: options?.temperature,
      max_tokens: options?.maxTokens,
      response_format: options?.responseFormat,
      stop: options?.stop,
    });

    const choice = response.choices[0];
    if (!choice.message?.content) {
      throw new Error('Empty response from OpenAI');
    }

    return {
      content: choice.message.content,
      model: response.model,
      usage: {
        promptTokens: response.usage?.prompt_tokens || 0,
        completionTokens: response.usage?.completion_tokens || 0,
        totalTokens: response.usage?.total_tokens || 0,
      },
      latencyMs: 0,
      cached: false,
    };
  }

  private async generateWithAnthropic(
    messages: LLMMessage[],
    modelId: string,
    options?: LLMGenerateOptions
  ): Promise<LLMGenerateResult> {
    if (!this.anthropicClient) {
      throw new Error('Anthropic client not initialized');
    }

    const systemMessage = messages.find(m => m.role === 'system');
    const userMessages = messages.filter(m => m.role !== 'system');

    const response = await this.anthropicClient.messages.create({
      model: modelId,
      system: systemMessage?.content,
      messages: userMessages.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      })),
      temperature: options?.temperature,
      max_tokens: options?.maxTokens || 4096,
      stop_sequences: options?.stop,
    });

    const contentBlock = response.content[0];
    if (contentBlock?.type !== 'text') {
      throw new Error('Unexpected response type from Anthropic');
    }

    return {
      content: contentBlock.text,
      model: response.model,
      usage: {
        promptTokens: response.usage.input_tokens,
        completionTokens: response.usage.output_tokens,
        totalTokens: response.usage.input_tokens + response.usage.output_tokens,
      },
      latencyMs: 0,
      cached: false,
    };
  }

  private getCacheKey(messages: LLMMessage[], options: Record<string, unknown>): string {
    const input = JSON.stringify({ messages, options });
    return createHash('sha256').update(input).digest('hex');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class LLMResponseCache {
  private cache: Map<string, { value: LLMGenerateResult; expiresAt: number }> = new Map();

  async get(key: string): Promise<LLMGenerateResult | null> {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.value;
  }

  async set(key: string, value: LLMGenerateResult, ttlSeconds = 3600): Promise<void> {
    this.cache.set(key, {
      value,
      expiresAt: Date.now() + ttlSeconds * 1000,
    });
  }
}

export const llmClient = new MultiModelLLMClient();
export default llmClient;
