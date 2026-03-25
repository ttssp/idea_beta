# 代理原生通信控制层 - E5 AI/Agent 智能层

> 这是"代理原生通信控制层"项目的E5（AI/Agent工程师）模块。

## 项目概述

E5模块负责系统的"智能层"，包括：

- **Thread Planner**：目标理解、初始动作计划生成、下一步建议
- **Message Drafter**：邮件/消息起草、候选时间生成、Checklist生成
- **Risk Classifier**：内容风险分类辅助（金额/承诺/冲突/隐私/情绪）
- **Pack Logic**：场景化能力包（时间协调包/资料收集包/跟进催办包）
- **Prompt & Template Library**：Prompt工程、模板管理、版本控制

**关键原则**：LLM参与判断与起草，但真正的执行、状态变更、审批、发送必须落在确定性系统边界内。E5的输出永远是"建议"，最终决策由E1/E2的确定性逻辑执行。

## 快速开始

### 方式一：本地开发

```bash
# 1. 安装依赖
npm run setup

# 或手动安装
npm install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API keys

# 3. 启动开发服务器
npm run dev
```

### 方式二：Docker

```bash
# 构建并启动
npm run docker:up

# 查看日志
docker-compose logs -f e5

# 停止服务
npm run docker:down
```

## 环境变量

必需的环境变量：

```bash
# 至少配置一个LLM提供商
OPENAI_API_KEY=sk-...

# 可选：Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

完整配置请参考 `.env.example`。

## API 接口

### 健康检查

```bash
# 健康检查
GET /health

# 就绪检查
GET /ready
```

### Planner API

```bash
# 生成动作计划
POST /ai/plan
Content-Type: application/json

{
  "threadContext": { ... }
}

# 建议下一步
POST /ai/suggest-next
Content-Type: application/json

{
  "threadContext": { ... }
}
```

### Drafter API

```bash
# 起草消息
POST /ai/draft-message
Content-Type: application/json

{
  "threadContext": { ... },
  "templateType": "email_proposal"
}

# 生成候选时间
POST /ai/generate-time-slots
Content-Type: application/json

# 生成Checklist
POST /ai/generate-checklist
Content-Type: application/json
```

### Risk API

```bash
# 风险分类
POST /ai/classify-risk
Content-Type: application/json

{
  "content": "需要检测的内容..."
}
```

### Summary API

```bash
# 线程摘要
POST /ai/summarize-thread
Content-Type: application/json
```

完整的API文档请参考：`docs/api/e5-openapi.yaml`

## 项目结构

```
src/e5/
├── api/                    # API层
│   ├── routes/            # 路由
│   ├── schemas.ts         # Zod验证schema
│   └── app.ts             # Fastify应用入口
├── core/                   # 核心逻辑层
│   ├── planner/           # Planner模块
│   ├── drafter/           # Drafter模块
│   ├── risk/              # Risk Classifier模块
│   └── packs/             # 能力包
├── llm/                    # LLM抽象层
│   └── client.ts          # 多模型支持
├── prompts/                # Prompt库
│   ├── templates/         # Prompt模板
│   └── library.ts         # Prompt库管理
├── types/                  # 类型定义
├── config/                 # 配置
└── utils/                  # 工具
```

## 开发命令

```bash
# 开发模式
npm run dev

# 类型检查
npm run typecheck

# 测试
npm test

# 测试覆盖率
npm run test:coverage

# 构建
npm run build

# 启动生产服务
npm start

# 健康检查
npm run health
```

## 质量要求

- **Risk Classifier recall**: ≥ 95%（金额/承诺/隐私类 ≥ 99%）
- **Message Drafter 可用率**: ≥ 70%（人工评估）
- **Planner 建议合理率**: ≥ 80%（人工评估）
- **LLM API 调用 P99**: < 5s

## Demo Scripts

项目包含3条标准线程的Demo Script：

1. **时间协调线程**：协调终面时间
2. **资料收集线程**：收集候选人资料
3. **跟进催办线程**：跟进供应商报价

位置：`docs/demo_scripts/`

## 与其他工程师协作

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

## 开发阶段

### ✅ Phase 0（W0-W2）：定义与冻结
- [x] 接口契约定义
- [x] 数据模型设计
- [x] Prompt库初始化
- [x] 项目结构搭建

### 🚧 Phase 1A（W3-W5）：Planner + Drafter 核心
- [x] Goal Parser实现
- [x] Action Generator实现
- [x] Message Drafter实现
- [ ] 与E1联调

### Phase 1B（W6-W8）：Risk Classifier + Pack Logic
- [x] Risk Classifier规则层
- [x] 3个Capability Packs
- [ ] 与E2联调

### Phase 2-3（W9-W24）：扩展与优化
- [ ] 小模型训练
- [ ] Evaluation Framework
- [ ] Prompt灰度发布

## 技术栈

- **语言**：TypeScript + Node.js
- **Web框架**：Fastify
- **数据验证**：Zod
- **LLM SDK**：OpenAI SDK + Anthropic SDK
- **日志**：Winston
- **测试**：Vitest

## License

MIT
