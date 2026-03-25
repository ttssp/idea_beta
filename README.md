
# 代理原生通信控制层 - E3模块

&gt; E3: Integration &amp; Action（外部集成 + 动作执行）

## 概述

E3负责系统的"手脚"——Channel Adapter连接外部世界（Email/Calendar），Action Runtime执行具体动作，Ingress/Egress Gateway管理消息收发。

## 技术栈

- **语言**: Python 3.11+
- **框架**: FastAPI
- **数据库**: PostgreSQL 15+
- **缓存/队列**: Redis + Celery
- **状态机**: transitions
- **熔断器**: pybreaker

## 目录结构

```
backend/e3/
├── config/              # 配置管理
├── core/                # 核心基础设施（DB/Redis/Idempotency）
├── action_runtime/      # ActionRuntime模块
│   ├── state_machine.py # 状态机
│   ├── engine.py        # 执行引擎
│   ├── models.py        # 数据库模型
│   └── registry.py      # 动作注册器
├── outbox_inbox/        # Outbox/Inbox模式
│   ├── outbox.py        # Outbox生产者
│   ├── inbox.py         # Inbox处理器
│   └── models.py        # 数据库模型
├── ingress/             # Ingress Gateway
├── egress/              # Egress Gateway
├── channel_adapters/    # Channel Adapters
│   ├── base.py          # 统一接口
│   ├── circuit_breaker.py # 熔断器
│   ├── email/
│   │   └── gmail.py     # Gmail Adapter
│   └── calendar/
│       └── google.py    # Google Calendar Adapter
├── external_resolver/   # External Resolver
│   └── resolver.py      # 解析器
├── api/                 # API层
│   ├── deps.py          # 依赖注入
│   └── v1/
│       ├── actions.py   # Actions API
│       ├── messages.py  # Messages API
│       ├── ingress.py   # Ingress Webhook
│       └── delivery.py  # Delivery Status
├── tests/               # 测试
│   ├── unit/
│   │   ├── test_action_state_machine.py
│   │   └── test_idempotency.py
│   └── integration/
│       ├── test_email_adapter.py
│       └── test_calendar_adapter.py
├── main.py              # FastAPI主应用
├── requirements.txt
└── .env.example
```

## 核心模块

### 1. Action Runtime
- ActionRun状态机（10种状态）
- 动作执行引擎（完整生命周期管理）
- 幂等控制（三层保障）

### 2. Outbox/Inbox Pattern
- 外发消息排队
- 接收事件去重
- 死信队列
- 指数退避重试

### 3. Channel Adapters
- Gmail Adapter（发送/接收邮件）
- Google Calendar Adapter（创建/更新/查询事件）
- 熔断器（Circuit Breaker）- 异常隔离

### 4. External Resolver
- 外部消息→内部Thread映射
- ExternalBinding管理
- 解析策略

### 5. API
- Actions API（准备/执行/取消/查询）
- Messages API（起草/发送）
- Ingress Webhook API
- Delivery Status API

## 快速开始

### 环境设置

```bash
# 1. 运行设置脚本
./scripts/setup-e3-dev.sh

# 2. 或手动设置
cd backend/e3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 复制环境变量
cp .env.example .env
# 编辑.env填入配置

# 4. 启动服务
uvicorn main:app --reload --port 8000

# 5. 访问API文档
open http://localhost:8000/docs
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/
```

## 交付状态

### ✅ Phase 0: 定义与冻结（W0-W2）
- ✅ API调研文档 (`docs/design/api-capability-analysis.md`)
- ✅ ActionRun状态机设计 (`docs/design/actionrun-state-machine.md`)
- ✅ 数据库Schema设计 (`docs/design/outbox-inbox-schema.md`)
- ✅ External Binding设计 (`docs/design/external-binding.md`)
- ✅ Channel Adapter接口 (`backend/e3/channel_adapters/base.py`)
- ✅ OpenAPI契约 (`docs/api/e3-openapi.yaml`)

### ✅ Phase 1A: ActionRun + Outbox/Inbox（W3-W5）
- ✅ 数据库模型（ActionRun/Outbox/Inbox/ExternalBinding）
- ✅ ActionRun状态机实现
- ✅ ActionRun执行引擎
- ✅ Outbox生产者
- ✅ Inbox处理器
- ✅ External Resolver
- ✅ 完整API（Actions/Messages/Ingress/Delivery）
- ✅ FastAPI主应用
- ✅ 单元测试框架

### ✅ Phase 1B: Email + Calendar集成（W6-W8）
- ✅ Gmail Adapter - 收件/发件
- ✅ Email异常隔离（熔断器）
- ✅ Google Calendar Adapter - 读取/写入
- ✅ Calendar幂等与去重
- ✅ 集成测试

## Channel Adapter使用示例

### 发送邮件

```python
from backend.e3.channel_adapters.email.gmail import GmailAdapter

adapter = GmailAdapter(credentials)

result = await adapter.send_message(
    payload={
        'to': 'recipient@example.com',
        'subject': 'Meeting Tomorrow',
        'body': 'Hi, let\'s meet tomorrow at 10am.',
        'in_reply_to': '&lt;prev-msg-id@example.com&gt;'
    },
    idempotency_key='unique-key-123'
)

print(result['external_message_id'])
```

### 创建日历事件

```python
from backend.e3.channel_adapters.calendar.google import GoogleCalendarAdapter
from datetime import datetime, timedelta

adapter = GoogleCalendarAdapter(credentials)

result = await adapter.send_message(
    payload={
        'action': 'create',
        'calendar_id': 'primary',
        'event': {
            'summary': 'Team Meeting',
            'description': 'Weekly sync',
            'start': {'dateTime': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'},
            'end': {'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat() + 'Z'},
            'attendees': [{'email': 'colleague@example.com'}]
        }
    },
    idempotency_key='meeting-123'
)

print(result['html_link'])
```

## API端点

### Actions API
```
POST   /api/v1/threads/{id}/actions:prepare
POST   /api/v1/threads/{id}/actions:execute
POST   /api/v1/threads/{id}/actions/{action_id}:cancel
GET    /api/v1/threads/{id}/actions
```

### Messages API
```
POST   /api/v1/threads/{id}/messages:draft
POST   /api/v1/threads/{id}/messages:send
```

### Ingress API
```
POST   /api/v1/ingress/email/gmail
POST   /api/v1/ingress/email/outlook
POST   /api/v1/ingress/calendar/google
POST   /api/v1/ingress/calendar/outlook
```

### Delivery API
```
POST   /api/v1/delivery/status
GET    /api/v1/delivery/{id}/status
```

## 与其他模块的接口

- **E1 (Thread Core)**: 获取/更新Thread状态
- **E2 (Policy &amp; Control)**: 策略决策、审批触发执行
- **E4 (前端)**: Action/Messages/Delivery API
- **E5 (AI/Agent)**: 智能解析请求

## 文档

- [Phase 0 总结](docs/design/PHASE_0_SUMMARY.md)
- [Phase 1A 总结](docs/design/PHASE_1A_SUMMARY.md)
- [Phase 1B 总结](docs/design/PHASE_1B_SUMMARY.md)
- [API能力分析](docs/design/api-capability-analysis.md)
- [ActionRun状态机](docs/design/actionrun-state-machine.md)
- [数据库Schema](docs/design/outbox-inbox-schema.md)
- [External Binding设计](docs/design/external-binding.md)
- [OpenAPI Spec](docs/api/e3-openapi.yaml)

## License

Internal use only.

