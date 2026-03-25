/**
 * E5 配置管理
 */

import { z } from 'zod';

const ConfigSchema = z.object({
  env: z.enum(['development', 'test', 'staging', 'production']).default('development'),

  server: z.object({
    port: z.coerce.number().default(8085),
    host: z.string().default('0.0.0.0'),
  }),

  llm: z.object({
    defaultModel: z.string().default('gpt-4o'),
    fallbackModel: z.string().default('gpt-4o-mini'),

    openai: z.object({
      apiKey: z.string().optional(),
      baseURL: z.string().optional(),
    }),

    anthropic: z.object({
      apiKey: z.string().optional(),
      baseURL: z.string().optional(),
    }),

    temperature: z.object({
      planning: z.number().default(0.1),
      drafting: z.number().default(0.7),
      classification: z.number().default(0.1),
    }),

    retry: z.object({
      maxRetries: z.number().default(3),
      initialDelayMs: z.number().default(1000),
      maxDelayMs: z.number().default(10000),
    }),

    timeoutMs: z.number().default(30000),
  }),

  cache: z.object({
    enabled: z.coerce.boolean().default(true),
    redisUrl: z.string().default('redis://localhost:6379'),
    ttlSeconds: z.object({
      planning: z.number().default(3600),
      drafting: z.number().default(1800),
      classification: z.number().default(3600),
    }),
  }),

  logging: z.object({
    level: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
    enableLLMTrace: z.coerce.boolean().default(false),
  }),

  evaluation: z.object({
    enableHumanEvaluation: z.coerce.boolean().default(false),
    autoSaveEvaluations: z.coerce.boolean().default(true),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;

function loadConfig(): Config {
  const env = process.env.NODE_ENV || 'development';

  const config = {
    env,
    server: {
      port: process.env.E5_PORT || 8085,
      host: process.env.E5_HOST || '0.0.0.0',
    },
    llm: {
      defaultModel: process.env.E5_DEFAULT_MODEL || 'gpt-4o',
      fallbackModel: process.env.E5_FALLBACK_MODEL || 'gpt-4o-mini',
      openai: {
        apiKey: process.env.OPENAI_API_KEY,
        baseURL: process.env.OPENAI_BASE_URL,
      },
      anthropic: {
        apiKey: process.env.ANTHROPIC_API_KEY,
        baseURL: process.env.ANTHROPIC_BASE_URL,
      },
      temperature: {
        planning: 0.1,
        drafting: 0.7,
        classification: 0.1,
      },
      retry: {
        maxRetries: 3,
        initialDelayMs: 1000,
        maxDelayMs: 10000,
      },
      timeoutMs: 30000,
    },
    cache: {
      enabled: process.env.E5_CACHE_ENABLED !== 'false',
      redisUrl: process.env.E5_REDIS_URL || 'redis://localhost:6379',
      ttlSeconds: {
        planning: 3600,
        drafting: 1800,
        classification: 3600,
      },
    },
    logging: {
      level: process.env.E5_LOG_LEVEL || 'info',
      enableLLMTrace: process.env.E5_ENABLE_LLM_TRACE === 'true',
    },
    evaluation: {
      enableHumanEvaluation: process.env.E5_ENABLE_HUMAN_EVAL === 'true',
      autoSaveEvaluations: process.env.E5_AUTO_SAVE_EVALS !== 'false',
    },
  };

  return ConfigSchema.parse(config);
}

export const config = loadConfig();

export default config;
