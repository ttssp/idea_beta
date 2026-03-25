/**
 * 日志工具
 */

import winston from 'winston';
import { config } from '../config/index.js';

const level = config.logging.level;

const format = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}] ${message}`;
    if (Object.keys(meta).length > 0) {
      msg += ' ' + JSON.stringify(meta);
    }
    return msg;
  })
);

export const logger = winston.createLogger({
  level,
  format,
  defaultMeta: { service: 'e5-ai-layer' },
  transports: [
    new winston.transports.Console({
      format: config.env === 'development' ? consoleFormat : format,
    }),
  ],
});

export const llmLogger = winston.createLogger({
  level: config.logging.enableLLMTrace ? 'debug' : 'info',
  format,
  defaultMeta: { service: 'e5-llm-client' },
  transports: [
    new winston.transports.Console({
      format: config.env === 'development' ? consoleFormat : format,
    }),
  ],
});

export default logger;
