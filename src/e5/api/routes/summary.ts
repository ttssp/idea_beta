/**
 * Summary API Routes (Placeholder)
 * 完整实现待Phase 2
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import {
  SummarizeThreadRequestSchema,
  SummarizeThreadResponseSchema,
  type SummarizeThreadRequest,
  type SummarizeThreadResponse,
} from '../schemas.js';
import { logger } from '../../utils/logger.js';

export async function summaryRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.post<{
    Body: SummarizeThreadRequest;
    Reply: SummarizeThreadResponse;
  }>(
    '/summarize-thread',
    {
      schema: {
        body: SummarizeThreadRequestSchema,
        response: {
          200: SummarizeThreadResponseSchema,
        },
      },
    },
    async (request: FastifyRequest<{ Body: SummarizeThreadRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Summarize thread request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      const response: SummarizeThreadResponse = {
        summary: {
          title: request.body.threadContext.objective.substring(0, 50),
          overview: request.body.threadContext.objective,
          currentStatus: request.body.threadContext.currentState,
          nextSteps: [],
        },
        modelUsed: 'template',
        processingTimeMs: Date.now() - startTime,
      };

      return reply.status(200).send(response);
    }
  );
}

export default summaryRoutes;
