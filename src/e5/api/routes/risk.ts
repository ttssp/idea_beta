/**
 * Risk API Routes
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import {
  ClassifyRiskRequestSchema,
  ClassifyRiskResponseSchema,
  type ClassifyRiskRequest,
  type ClassifyRiskResponse,
} from '../schemas.js';
import { riskEnsembleClassifier } from '../../core/risk/index.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';

export async function riskRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.post<{
    Body: ClassifyRiskRequest;
    Reply: ClassifyRiskResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/classify-risk',
    {
      schema: {
        body: ClassifyRiskRequestSchema,
        response: {
          200: ClassifyRiskResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: ClassifyRiskRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.debug('Risk classification request received', {
        requestId,
        contentLength: request.body.content.length,
      });

      try {
        const classification = await riskEnsembleClassifier.classify(request.body);

        const response: ClassifyRiskResponse = {
          classification,
          modelUsed: classification.modelUsed || config.llm.fallbackModel,
          processingTimeMs: Date.now() - startTime,
          cached: false,
        };

        logger.info('Risk classification completed', {
          requestId,
          tags: classification.tags,
          overallRiskLevel: classification.overallRiskLevel,
          processingTimeMs: response.processingTimeMs,
        });

        return reply.status(200).send(response);
      } catch (error) {
        logger.error('Risk classification failed', {
          requestId,
          error,
        });

        return reply.status(500).send({
          error: {
            code: 'CLASSIFICATION_FAILED',
            message: error instanceof Error ? error.message : 'Unknown error',
          },
          requestId,
        });
      }
    }
  );
}

export default riskRoutes;
