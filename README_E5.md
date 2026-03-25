# E5 - AI/Agent Intelligence Layer

代理原生通信控制层 - AI/Agent智能层模块

## 概述

E5模块负责系统的"智能层"，包括：
- **Thread Planner**：目标理解、动作计划生成、下一步建议
- **Message Drafter**：邮件/消息起草、候选时间生成、Checklist生成
- **Risk Classifier**：内容风险分类辅助（金额/承诺/冲突/隐私/情绪）
- **Pack Logic**：场景化能力包（时间协调包/资料收集包/跟进催办包）
- **Prompt & Template Library**：Prompt工程、模板管理、版本控制
- **Evaluation Framework**：LLM输出质量评估、回归测试集

## 关键原则

> LLM参与判断与起草，但真正的执行、状态变更、审批、发送必须落在确定性系统边界内。E5的输出永远是"建议"，最终决策由E1/E2的确定性逻辑执行。

## 项目结构

```
src/e5/
├── api/                    # API层
│   ├── routes/            # 路由
│   │   ├── planner.ts     # Planner API
│   │   ├── drafter.ts     # Drafter API
│   │   ├── risk.ts        # Risk Classifier API
│   │   └── summary.ts     # Thread Summary API
│   ├── schemas.ts         # Zod验证schema
│   └── app.ts             # Fastify应用入口
│
├── core/                   # 核心逻辑层
│   ├── planner/           # Planner模块
│   │   ├── goal_parser.ts
│   │   ├── action_generator.ts
│   │   └── index.ts
│   ├── risk/              # Risk Classifier模块
│   │   ├── rules.ts       # 规则兜底层
│   │   ├── ensemble.ts    # 分类器集成
│   │   └── index.ts
│   └── packs/             # 能力包
│       ├── time_coordination.ts
│       └── index.ts
│
├── llm/                    # LLM抽象层
│   └── client.ts          # 多模型支持、重试、缓存
│
├── prompts/                # Prompt库
│   ├── templates/          # Prompt模板
│   └── library.ts         # Prompt库管理
│
├── types/                  # 类型定义
│   ├── thread.ts
│   ├── risk.ts
│   ├── api.ts
│   └── index.ts
│
├── config/                 # 配置
│   ├── index.ts
│   └── models.ts
│
└── utils/                  # 工具
    └── logger.ts
```

## API接口

### Planner API

```
POST   /ai/plan                → 输入 thread context → 输出 action plan
POST   /ai/suggest-next        → 输入 thread state → 输出下一步建议
```

### Drafter API

```
POST   /ai/draft-message       → 输入 context + template → 输出 draft
POST   /ai/generate-time-slots → 输入 calendar data → 输出候选时间
POST   /ai/generate-checklist  → 输入 objective → 输出 checklist
```

### Risk Classifier API

```
POST   /ai/classify-risk       → 输入 content → 输出 risk tags + confidence
```

### Thread Summary API

```
POST   /ai/summarize-thread    → 输入 event log → 输出 summary
```

## 质量要求

- Risk Classifier recall ≥ 95%（金额/承诺/隐私类 ≥ 99%）
- Message Drafter 可用率 ≥ 70%（人工评估）
- Planner 建议合理率 ≥ 80%（人工评估）
- LLM API 调用 P99 < 5s

## 技术栈

- **语言**：TypeScript + Node.js
- **Web框架**：Fastify
- **数据验证**：Zod
- **LLM SDK**：OpenAI SDK + Anthropic SDK
- **日志**：Winston
- **测试**：Vitest

## 开发阶段

### Phase 0（W0-W2）：定义与冻结 ✅
- [x] 接口契约定义
- [x] 数据模型设计
- [x] Prompt库初始化
- [x] 项目结构搭建

### Phase 1A（W3-W5）：Planner + Drafter 核心
- [ ] Goal Parser完整实现
- [ ] Action Generator完整实现
- [ ] Message Drafter完整实现
- [ ] 与E1联调

### Phase 1B（W6-W8）：Risk Classifier + Pack Logic
- [ ] Risk Classifier完整实现
- [ ] 3个Capability Pack实现
- [ ] 与E2联调
- [ ] 3类线程E2E

### Phase 2-3（W9-W24）：扩展与优化
- [ ] 小模型训练
- [ ] Evaluation Framework
- [ ] Prompt灰度发布
- [ ] LLM降级方案

## 与其他工程师的协作

### E1（Thread Core）
- 消费：ThreadContext数据结构
- 提供：ActionPlan、NextSuggestion

### E2（Policy & Control）
- 消费：RiskClassification输入
- 提供：RiskClassification结果（仅建议，不决策）

### E3（Integration & Action）
- 消费：Calendar数据、Draft消息格式
- 提供：候选时间、Checklist

### E4（Frontend）
- 提供：完整OpenAPI spec + Mock服务器

## 环境变量

```bash
NODE_ENV=development
E5_PORT=8085
E5_HOST=0.0.0.0

# LLM配置
OPENAI_API_KEY=sk-...
E5_DEFAULT_MODEL=gpt-4o
E5_FALLBACK_MODEL=gpt-4o-mini

# 可选：Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# 缓存配置
E5_CACHE_ENABLED=true
E5_REDIS_URL=redis://localhost:6379

# 日志配置
E5_LOG_LEVEL=info
```

## 本地开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 类型检查
npm run typecheck

# 测试
npm test

# 构建
npm run build
```

## License

MIT
