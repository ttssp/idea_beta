/**
 * Message Generator - 消息生成器
 */

import type { DraftMessageRequest, DraftMessageResponse } from '../../types/api.js';
import { llmClient } from '../../llm/client.js';
import { promptLibrary } from '../../prompts/library.js';
import { logger } from '../../utils/logger.js';
import { config } from '../../config/index.js';
import { riskEnsembleClassifier } from '../risk/index.js';

export class MessageGenerator {
  async generateEmail(request: DraftMessageRequest): Promise<DraftMessageResponse> {
    const startTime = Date.now();
    logger.debug('Generating email draft', {
      threadId: request.threadContext.threadId,
      templateType: request.templateType,
    });

    try {
      const template = promptLibrary.getTemplate('drafter.email_draft');
      if (!template) {
        throw new Error('Email draft template not found');
      }

      const rendered = promptLibrary.renderTemplate(template, {
        threadContext: request.threadContext,
        ...request,
        userInput: request.threadContext.objective,
      });

      const result = await llmClient.generate(
        [
          { role: 'system', content: rendered.system },
          { role: 'user', content: this.buildUserPrompt(request) },
        ],
        {
          model: config.llm.defaultModel,
          temperature: request.tone === 'creative' ? 0.9 : config.llm.temperature.drafting,
        }
      );

      const draft = this.parseEmailOutput(result.content);

      const riskPreview = await riskEnsembleClassifier.classify({
        content: draft.content,
        threadContext: request.threadContext,
      });

      const response: DraftMessageResponse = {
        draft,
        suggestedEdits: this.generateSuggestedEdits(draft),
        riskPreview,
        modelUsed: config.llm.defaultModel,
        processingTimeMs: Date.now() - startTime,
      };

      logger.info('Email draft generated', {
        threadId: request.threadContext.threadId,
        processingTimeMs: response.processingTimeMs,
        hasRiskPreview: !!riskPreview,
      });

      return response;
    } catch (error) {
      logger.error('Email generation failed, using fallback', { error });
      return this.fallbackGenerate(request, startTime);
    }
  }

  private buildUserPrompt(request: DraftMessageRequest): string {
    let prompt = `## 线程目标\n${request.threadContext.objective}\n\n`;

    if (request.specificInstructions) {
      prompt += `## 特殊指令\n${request.specificInstructions}\n\n`;
    }

    if (request.targetRecipient) {
      prompt += `## 收件人信息\n`;
      if (request.targetRecipient.name) prompt += `- 姓名: ${request.targetRecipient.name}\n`;
      if (request.targetRecipient.role) prompt += `- 角色: ${request.targetRecipient.role}\n`;
      if (request.targetRecipient.relationship) prompt += `- 关系: ${request.targetRecipient.relationship}\n`;
      prompt += '\n';
    }

    if (request.threadContext.messageHistory.length > 0) {
      prompt += `## 历史消息 (最近3条)\n`;
      const recent = request.threadContext.messageHistory.slice(-3);
      for (const msg of recent) {
        prompt += `[${msg.timestamp}] ${msg.senderId}: ${msg.content.substring(0, 150)}\n`;
      }
    }

    prompt += `\n请根据以上信息起草邮件。`;
    return prompt;
  }

  private parseEmailOutput(content: string): DraftMessageResponse['draft'] {
    const subjectMatch = content.match(/^Subject[:：]\s*(.+)$/im);
    const subject = subjectMatch ? subjectMatch[1].trim() : '关于' + content.substring(0, 30);

    let body = content
      .replace(/^Subject[:：].*$/im, '')
      .trim();

    if (!body) {
      body = content;
    }

    return {
      subject,
      content: body,
      contentType: 'text/plain',
    };
  }

  private generateSuggestedEdits(draft: DraftMessageResponse['draft']): string[] {
    const edits: string[] = [];

    if (draft.subject.length < 5) {
      edits.push('建议补充更明确的邮件主题');
    }

    if (draft.content.length < 50) {
      edits.push('建议补充更多细节');
    }

    if (!draft.content.includes('您好') && !draft.content.includes('你好')) {
      edits.push('建议添加适当的问候语');
    }

    if (!draft.content.includes('谢谢') && !draft.content.includes('感谢')) {
      edits.push('建议添加结束语');
    }

    return edits.slice(0, 3);
  }

  private fallbackGenerate(
    request: DraftMessageRequest,
    startTime: number
  ): DraftMessageResponse {
    const recipientName = request.targetRecipient?.name || '您好';

    let subject = '';
    let content = '';

    switch (request.templateType) {
      case 'email_proposal':
        subject = '关于' + request.threadContext.objective.substring(0, 15) + '的时间提议';
        content = `${recipientName}，\n\n关于${request.threadContext.objective}，我们建议以下时间：\n\n1. [请填写时间]\n2. [请填写时间]\n\n请您看看哪个时间比较合适？\n\n谢谢！\n`;
        break;

      case 'email_confirmation':
        subject = '确认：' + request.threadContext.objective.substring(0, 15);
        content = `${recipientName}，\n\n感谢您的确认！\n\n已为您安排：${request.threadContext.objective}\n\n如有任何变更，请随时告知。\n\n谢谢！\n`;
        break;

      case 'email_followup':
        subject = '跟进：' + request.threadContext.objective.substring(0, 15);
        content = `${recipientName}，\n\n想跟进一下关于${request.threadContext.objective}的进展。\n\n不知您那边是否方便提供更新？\n\n谢谢！\n`;
        break;

      case 'email_reminder':
        subject = '提醒：' + request.threadContext.objective.substring(0, 15);
        content = `${recipientName}，\n\n温馨提醒一下：\n\n- ${request.threadContext.objective}\n\n如有需要帮助的地方，请随时联系。\n\n谢谢！\n`;
        break;

      default:
        subject = '关于' + request.threadContext.objective.substring(0, 20);
        content = `${recipientName}，\n\n关于${request.threadContext.objective}\n\n[请在此处补充内容]\n\n谢谢！\n`;
    }

    return {
      draft: {
        subject,
        content,
        contentType: 'text/plain',
      },
      suggestedEdits: ['此为模板生成，请根据实际情况调整内容'],
      modelUsed: 'template',
      processingTimeMs: Date.now() - startTime,
    };
  }
}

export const messageGenerator = new MessageGenerator();
export default messageGenerator;
