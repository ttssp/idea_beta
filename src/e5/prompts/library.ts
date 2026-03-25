/**
 * Prompt 库管理
 */

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface PromptTemplate {
  id: string;
  version: string;
  name: string;
  description: string;
  systemPrompt: string;
  fewShotExamples?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface RenderedPrompt {
  system: string;
  user: string;
}

export class PromptLibrary {
  private templates: Map<string, PromptTemplate> = new Map();
  private templateDir: string;

  constructor(templateDir?: string) {
    this.templateDir = templateDir || join(__dirname, 'templates');
  }

  async initialize(): Promise<void> {
    logger.info('Initializing prompt library', { dir: this.templateDir });
    await this.loadBuiltInTemplates();
  }

  private async loadBuiltInTemplates(): Promise<void> {
    const templateDefinitions: Array<{ id: string; path: string; name: string; description: string }> = [
      {
        id: 'planner.goal_parser',
        path: 'planner/goal_parser.system.md',
        name: 'Goal Parser',
        description: '解析线程目标',
      },
      {
        id: 'planner.action_generator',
        path: 'planner/action_generator.system.md',
        name: 'Action Generator',
        description: '生成动作计划',
      },
      {
        id: 'drafter.email_draft',
        path: 'drafter/email_draft.system.md',
        name: 'Email Drafter',
        description: '起草邮件',
      },
      {
        id: 'risk.classifier',
        path: 'risk/classifier.system.md',
        name: 'Risk Classifier',
        description: '风险分类',
      },
    ];

    for (const def of templateDefinitions) {
      try {
        const content = await readFile(join(this.templateDir, def.path), 'utf-8');
        const template: PromptTemplate = {
          id: def.id,
          version: '1.0.0',
          name: def.name,
          description: def.description,
          systemPrompt: content,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        this.templates.set(def.id, template);
        logger.debug('Loaded prompt template', { id: def.id });
      } catch (error) {
        logger.warn('Failed to load prompt template', { id: def.id, error });
      }
    }

    logger.info('Prompt library initialized', { count: this.templates.size });
  }

  getTemplate(id: string, variant?: string): PromptTemplate | undefined {
    const key = variant ? `${id}.${variant}` : id;
    let template = this.templates.get(key);

    if (!template && variant) {
      template = this.templates.get(id);
    }

    return template;
  }

  renderTemplate(template: PromptTemplate, context: Record<string, unknown>): RenderedPrompt {
    const systemPrompt = this.interpolate(template.systemPrompt, context);

    return {
      system: systemPrompt,
      user: this.buildUserPrompt(context),
    };
  }

  private interpolate(template: string, context: Record<string, unknown>): string {
    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      const value = context[key];
      return value !== undefined ? String(value) : match;
    });
  }

  private buildUserPrompt(context: Record<string, unknown>): string {
    const userInput = context['userInput'] || context['content'] || context['objective'] || '';
    const threadContext = context['threadContext'];

    let prompt = String(userInput);

    if (threadContext) {
      prompt = `## 线程上下文\n${JSON.stringify(threadContext, null, 2)}\n\n## 用户输入\n${prompt}`;
    }

    return prompt;
  }

  listTemplates(): PromptTemplate[] {
    return Array.from(this.templates.values());
  }
}

export const promptLibrary = new PromptLibrary();
export default promptLibrary;
