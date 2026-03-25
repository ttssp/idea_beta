/**
 * Drafter API Routes (Placeholder)
 * 完整实现待Phase 1A
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import {
  DraftMessageRequestSchema,
  DraftMessageResponseSchema,
  GenerateTimeSlotsRequestSchema,
  GenerateTimeSlotsResponseSchema,
  GenerateChecklistRequestSchema,
  GenerateChecklistResponseSchema,
  type DraftMessageRequest,
  type DraftMessageResponse,
  type GenerateTimeSlotsRequest,
  type GenerateTimeSlotsResponse,
  type GenerateChecklistRequest,
  type GenerateChecklistResponse,
} from '../schemas.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';

export async function drafterRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.post<{
    Body: DraftMessageRequest;
    Reply: DraftMessageResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/draft-message',
    {
      schema: {
        body: DraftMessageRequestSchema,
        response: {
          200: DraftMessageResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: DraftMessageRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Draft message request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      const response: DraftMessageResponse = {
        draft: {
          subject: '关于' + request.body.threadContext.objective.substring(0, 20) + '...',
          content: '您好，\n\n关于' + request.body.threadContext.objective + '\n\n谢谢！',
          contentType: 'text/plain',
        },
        suggestedEdits: ['请根据实际情况调整内容'],
        modelUsed: 'template',
        processingTimeMs: Date.now() - startTime,
      };

      logger.info('Draft message request completed (template)', {
        requestId,
        processingTimeMs: response.processingTimeMs,
      });

      return reply.status(200).send(response);
    }
  );

  fastify.post<{
    Body: GenerateTimeSlotsRequest;
    Reply: GenerateTimeSlotsResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/generate-time-slots',
    {
      schema: {
        body: GenerateTimeSlotsRequestSchema,
        response: {
          200: GenerateTimeSlotsResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: GenerateTimeSlotsRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Generate time slots request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      const response: GenerateTimeSlotsResponse = {
        slots: [],
        reasoning: 'Time slot generation requires full implementation in Phase 1A',
        processingTimeMs: Date.now() - startTime,
      };

      return reply.status(200).send(response);
    }
  );

  fastify.post<{
    Body: GenerateChecklistRequest;
    Reply: GenerateChecklistResponse | { error: { code: string; message: string }; requestId: string };
  }>(
    '/generate-checklist',
    {
      schema: {
        body: GenerateChecklistRequestSchema,
        response: {
          200: GenerateChecklistResponseSchema,
          500: { $ref: 'ErrorResponseSchema' },
        },
      },
    },
    async (request: FastifyRequest<{ Body: GenerateChecklistRequest }>, reply: FastifyReply) => {
      const requestId = uuidv4();
      const startTime = Date.now();

      logger.info('Generate checklist request received', {
        requestId,
        threadId: request.body.threadContext.threadId,
      });

      const response: GenerateChecklistResponse = {
        checklist: [
          {
            id: '1',
            text: '明确目标',
            required: true,
            priority: 'high',
          },
        ],
        reasoning: 'Checklist generation requires full implementation in Phase 1A',
        modelUsed: config.llm.defaultModel,
        processingTimeMs: Date.now() - startTime,
      };

      return reply.status(200).send(response);
    }
  );
}

export default drafterRoutes;
