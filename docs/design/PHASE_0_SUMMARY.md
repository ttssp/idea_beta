
# Phase 0 交付总结

&gt; Phase 0: 定义与冻结（W0-W2）

## 交付清单

### ✅ W0: API调研 + ActionRun状态机设计

| 交付物 | 路径 | 状态 |
|--------|------|------|
| API能力分析文档 | `docs/design/api-capability-analysis.md` | ✅ 完成 |
| ActionRun状态机设计 | `docs/design/actionrun-state-machine.md` | ✅ 完成 |
| ActionRun状态机实现 | `backend/e3/action_runtime/state_machine.py` | ✅ 完成 |

### ✅ W1: Outbox/Inbox模型 + ExternalBinding设计

| 交付物 | 路径 | 状态 |
|--------|------|------|
| 数据库Schema设计 | `docs/design/outbox-inbox-schema.md` | ✅ 完成 |
| External Binding设计 | `docs/design/external-binding.md` | ✅ 完成 |

### ✅ W2: Channel Adapter接口 + 接口契约冻结

| 交付物 | 路径 | 状态 |
|--------|------|------|
| Channel Adapter统一接口 | `backend/e3/channel_adapters/base.py` | ✅ 完成 |
| OpenAPI契约定义 | `docs/api/e3-openapi.yaml` | ✅ 完成 |

## 项目结构

```
myproj-feature-E3/
├── backend/
│   ├── e3/                           # E3职责域
│   │   ├── config/                   # 配置管理
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── core/                     # 核心基础设施
│   │   │   ├── __init__.py
│   │   │   └── idempotency.py
│   │   ├── action_runtime/           # ActionRuntime模块
│   │   │   ├── __init__.py
│   │   │   ├── state_machine.py
│   │   │   └── actions/
│   │   ├── outbox_inbox/             # Outbox/Inbox模式
│   │   ├── ingress/                  # Ingress Gateway
│   │   ├── egress/                   # Egress Gateway
│   │   ├── channel_adapters/         # Channel Adapters
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── email/
│   │   │   └── calendar/
│   │   ├── external_resolver/        # External Resolver
│   │   ├── api/                      # API层
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   ├── tests/                    # 测试
│   │   │   ├── __init__.py
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── e2e/
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   └── .env.example
│   ├── e1/                           # E1职责域（占位）
│   ├── e2/                           # E2职责域（占位）
│   └── shared/                       # 共享模块
│
├── docs/
│   ├── api/
│   │   └── e3-openapi.yaml           # OpenAPI契约
│   └── design/
│       ├── api-capability-analysis.md    # API能力分析
│       ├── actionrun-state-machine.md    # ActionRun状态机
│       ├── outbox-inbox-schema.md        # 数据库Schema
│       ├── external-binding.md            # External Binding设计
│       └── PHASE_0_SUMMARY.md             # 本文档
│
├── scripts/
│   └── setup-e3-dev.sh               # 开发环境设置脚本
│
├── .gitignore
└── README.md
```

## 核心设计决策

### 1. 技术栈选择
- **语言**: Python 3.11+ - API集成生态成熟，与AI层无缝衔接
- **框架**: FastAPI - 异步性能、类型安全、OpenAPI自动生成
- **数据库**: PostgreSQL 15+ - 事务支持、JSONB、成熟的幂等控制方案

### 2. 幂等性保障（三层）
1. **应用层**: Redis缓存幂等键
2. **数据库**: UNIQUE约束
3. **外部API**: Gmail threadId、Calendar iCalUID

### 3. 状态机设计
- 10种状态：created → planned → ready_for_approval → approved → executing → sent → acknowledged
- 失败重试：failed_retryable ↔ executing → failed_terminal
- 取消路径：planned/ready_for_approval/approved → cancelled

## 接口契约

### E3对外提供的API

```
# Action API
POST   /threads/{id}/actions:prepare
POST   /threads/{id}/actions:execute
POST   /threads/{id}/actions/{action_id}:cancel
GET    /threads/{id}/actions

# Message API
POST   /threads/{id}/messages:draft
POST   /threads/{id}/messages:send

# Ingress Webhook
POST   /ingress/email/gmail
POST   /ingress/email/outlook
POST   /ingress/calendar/google
POST   /ingress/calendar/outlook

# Delivery Status
POST   /delivery/status
GET    /delivery/{id}/status
```

完整OpenAPI spec: `docs/api/e3-openapi.yaml`

## 与其他工程师的协作点

### E3 → E1
- 获取Thread详情
- 添加Thread事件
- 更新Thread状态

### E3 ← E2
- E2批准后触发动作执行
- E3请求策略决策

### E3 ↔ E4
- 完整的Action/Messages/Delivery API

### E3 ↔ E5
- E3请求智能解析外部消息

## 下一步：Phase 1A

Phase 1A（W3-W5）将实现：
- ActionRun状态机核心（完成数据库模型、引擎）
- Idempotency Key机制（完成Redis集成）
- Outbox Pattern（完成生产者/消费者）
- Inbox Pattern（完成webhook处理）
- Ingress Gateway框架
- External Resolver

## 开发环境快速开始

```bash
# 1. 运行设置脚本
./scripts/setup-e3-dev.sh

# 2. 编辑配置
cd backend/e3
cp .env.example .env
# 编辑 .env

# 3. 启动依赖（PostgreSQL + Redis）
# 使用docker-compose或本地安装

# 4. 运行开发服务器
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

---

**Phase 0 完成时间**: 2026-03-24
**状态**: ✅ 所有交付物已完成，接口契约已冻结

