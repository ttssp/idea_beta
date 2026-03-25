/**
 * E5 Fastify 应用入口
 */

import { randomUUID } from 'crypto';
import Fastify from 'fastify';
import {
  serializerCompiler,
  validatorCompiler,
  type ZodTypeProvider,
} from 'fastify-type-provider-zod';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';
import { promptLibrary } from '../prompts/library.js';
import { ErrorResponseSchema } from './schemas.js';
import plannerRoutes from './routes/planner.js';
import drafterRoutes from './routes/drafter.js';
import riskRoutes from './routes/risk.js';
import summaryRoutes from './routes/summary.js';

export async function createApp(): Promise<Fastify.FastifyInstance> {
  const fastify = Fastify({
    logger: false,
    disableRequestLogging: true,
    genReqId: () => randomUUID(),
  }).withTypeProvider<ZodTypeProvider>();

  // 注册 Zod 验证器和序列化器
  fastify.setValidatorCompiler(validatorCompiler);
  fastify.setSerializerCompiler(serializerCompiler);

  // 注册共享 schema
  fastify.addSchema({
    $id: 'ErrorResponseSchema',
    ...ErrorResponseSchema.shape,
  });

  fastify.addHook('onRequest', (request, reply, done) => {
    logger.debug('Request received', {
      method: request.method,
      url: request.url,
      requestId: request.id,
    });
    done();
  });

  fastify.addHook('onResponse', (request, reply, done) => {
    logger.debug('Response sent', {
      method: request.method,
      url: request.url,
      statusCode: reply.statusCode,
      requestId: request.id,
      responseTime: reply.elapsedTime,
    });
    done();
  });

  fastify.addHook('onError', (request, reply, error, done) => {
    logger.error('Request error', {
      method: request.method,
      url: request.url,
      error: error.message,
      stack: error.stack,
      requestId: request.id,
    });
    done();
  });

  fastify.get('/health', async () => {
    return {
      status: 'healthy',
      service: 'e5-ai-layer',
      timestamp: new Date().toISOString(),
    };
  });

  fastify.get('/ready', async () => {
    return {
      status: 'ready',
      service: 'e5-ai-layer',
      promptLibraryInitialized: promptLibrary.listTemplates().length > 0,
      timestamp: new Date().toISOString(),
    };
  });

  await fastify.register(plannerRoutes, { prefix: '/ai' });
  await fastify.register(drafterRoutes, { prefix: '/ai' });
  await fastify.register(riskRoutes, { prefix: '/ai' });
  await fastify.register(summaryRoutes, { prefix: '/ai' });

  return fastify;
}

async function startServer(): Promise<void> {
  logger.info('Starting E5 AI Layer...', {
    env: config.env,
    port: config.server.port,
  });

  await promptLibrary.initialize();

  const app = await createApp();

  try {
    await app.listen({
      port: config.server.port,
      host: config.server.host,
    });

    logger.info('E5 AI Layer started successfully', {
      port: config.server.port,
      host: config.server.host,
      url: `http://${config.server.host}:${config.server.port}`,
    });
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  startServer();
}

export { createApp, startServer };
