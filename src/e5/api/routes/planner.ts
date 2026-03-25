/**
 * Planner API Routes
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import {
  PlanRequestSchema,
  PlanResponseSchema,
  SuggestNextRequestSchema,
  SuggestNextResponseSchema,
  type PlanRequest,
  type PlanResponse,
  type SuggestNextRequest,
  type SuggestNextResponse,
} from '../schemas.js';
import { threadPlanner } from '../../core/planner/index.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';

export async function plannerRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.post<{
    Body: PlanRequest;
    Reply: PlanResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/plan',
    {
      schema: {
        body: PlanRequestSchema,
        response: {
          200: PlanResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: PlanRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Planning request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      try {
        const result = await threadPlanner.plan(request.body.threadContext);

        const response: PlanResponse = {
          plan: result.plan,
          nextSuggestion: await threadPlanner.suggestNext(request.body.threadContext),
          reasoning: result.reasoning,
          modelUsed: config.llm.defaultModel,
          processingTimeMs: Date.now() - startTime,
          cached: false,
        };

        logger.info('Planning request completed', {
          requestId,
          stepsCount: result.plan.steps.length,
          processingTimeMs: response.processingTimeMs,
        });

        return reply.status(200).send(response);
      } catch (error) {
        logger.error('Planning request failed', {
          requestId,
          error,
        });

        return reply.status(500).send({
          error: {
            code: 'PLANNING_FAILED',
            message: error instanceof Error ? error.message : 'Unknown error',
          },
          requestId,
        });
      }
    }
  );

  fastify.post<{
    Body: SuggestNextRequest;
    Reply: SuggestNextResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/suggest-next',
    {
      schema: {
        body: SuggestNextRequestSchema,
        response: {
          200: SuggestNextResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: SuggestNextRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Suggest next request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      try {
        const suggestion = await threadPlanner.suggestNext(request.body.threadContext);

        const response: SuggestNextResponse = {
          suggestion,
          modelUsed: config.llm.defaultModel,
          processingTimeMs: Date.now() - startTime,
        };

        logger.info('Suggest next request completed', {
          requestId,
          actionType: suggestion.action.type,
          processingTimeMs: response.processingTimeMs,
        });

        return reply.status(200).send(response);
      } catch (error) {
        logger.error('Suggest next request failed', {
          requestId,
          error,
        });

        return reply.status(500).send({
          error: {
            code: 'SUGGESTION_FAILED',
            message: error instanceof Error ? error.message : 'Unknown error',
          },
          requestId,
        });
      }
    }
  );
}

export default plannerRoutes;
