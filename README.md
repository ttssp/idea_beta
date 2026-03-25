# 代理原生通信控制层 - Thread Core (E1)

## 概述

这是"代理原生通信控制层"项目的Thread Core模块，由E1工程师负责开发。本模块是整个系统的骨架，提供：

- **Thread Engine**: 线程内核（CRUD、状态机、目标管理、参与者管理）
- **对象模型**: Thread/Principal/Relationship/Message/ThreadEvent/ExternalBinding
- **Event Store**: append-only事件日志
- **数据库基础设施**: Postgres schema + migration
- **基础API**: RESTful接口供其他模块调用

## 技术栈

- **语言**: Python 3.12+
- **Web框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 + Alembic
- **数据库**: PostgreSQL 16+
- **测试**: pytest + pytest-asyncio

## 快速开始

### 1. 环境设置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 2. 启动数据库

```bash
docker-compose up -d postgres
```

### 3. 运行数据库迁移

```bash
alembic upgrade head
```

### 4. 启动应用

```bash
uvicorn myproj.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发

### 代码质量

```bash
# 格式化
black src/ tests/

# Linting
ruff check src/ tests/
ruff fix src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest
pytest --cov=src  # 带覆盖率
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

# 代理原生通信控制层 - Policy &amp; Control 模块

这是"代理原生通信控制层"项目中E2工程师（Policy &amp; Control模块负责人）的实现代码。

## 模块概览

Policy &amp; Control模块负责系统的"大脑和安全网"：

- **Delegation Runtime**: 委托档位管理、预算管理、策略命中逻辑
- **Policy Engine**: 策略规则CRUD/匹配/优先级/冲突解决
- **Approval Engine**: 审批请求创建/审核/超时处理/批量操作
- **Risk Engine**: 四层风险判断 + 合成决策 + decision trace
- **Kill Switch**: 三层熔断（Global/Profile/Thread）
- **Decision Trace**: 每次决策的完整记录

## 项目结构

```
myproj/
├── src/myproj/
│   ├── core/              # 核心领域层
│   │   ├── domain/        # 领域模型
│   │   ├── services/      # 领域服务
│   │   └── repositories/  # 仓储接口
│   ├── infra/             # 基础设施层
│   │   ├── db/            # 数据库
│   │   └── di/            # 依赖注入
│   └── api/               # API层
│       └── v1/            # API v1端点
├── alembic/               # 数据库迁移
├── tests/                 # 测试
└── docs/                  # 文档

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

### Thread API
- `POST /api/v1/threads` - 创建线程
- `GET /api/v1/threads` - 查询线程列表
- `GET /api/v1/threads/{id}` - 查询线程详情
- `PATCH /api/v1/threads/{id}` - 更新线程
- `POST /api/v1/threads/{id}/pause` - 暂停线程
- `POST /api/v1/threads/{id}/resume` - 恢复线程
- `POST /api/v1/threads/{id}/takeover` - 接管线程

### Event API
- `GET /api/v1/threads/{id}/events` - 查询线程事件流
- `POST /api/v1/threads/{id}/events` - 写入事件（内部调用）

### Principal & Relationship API
- `POST /api/v1/principals` - 创建主体
- `GET /api/v1/principals/{id}` - 查询主体
- `POST /api/v1/relationships` - 创建关系
- `GET /api/v1/relationships` - 查询关系列表

### Message API
- `POST /api/v1/threads/{id}/messages` - 创建消息
- `GET /api/v1/threads/{id}/messages` - 查询线程消息

## Thread状态机

```
new → planning → active ─┬→ awaiting_external
                        ├→ awaiting_approval
                        ├→ blocked
                        ├→ paused
                        ├→ escalated
                        ├→ completed
                        └→ cancelled
```

10种状态：`new`, `planning`, `active`, `awaiting_external`, `awaiting_approval`, `blocked`, `paused`, `escalated`, `completed`, `cancelled`

## 质量要求

- 核心状态机单元测试覆盖率 ≥ 95%
- Event Store写入保证exactly-once
- Thread查询API P99 < 200ms
- 数据库migration支持前向/回滚

## License

Proprietary
src/policy_control/
├── __init__.py
├── __main__.py              # 示例入口
├── controller.py            # 主控制器
├── common/                  # 通用模块
│   ├── constants.py         # 常量与枚举
│   ├── exceptions.py        # 异常定义
│   └── types.py             # 类型定义
├── delegation/              # Delegation Runtime
│   ├── models.py
│   ├── service.py
│   └── constants.py
├── policy/                  # Policy Engine
│   ├── models.py
│   ├── engine.py
│   └── evaluator.py
├── approval/                # Approval Engine
│   ├── models.py
│   ├── service.py
│   └── state_machine.py
├── risk/                    # Risk Engine
│   ├── models.py
│   ├── relationship.py
│   ├── action.py
│   ├── content.py
│   ├── consequence.py
│   └── synthesizer.py
├── kill_switch/             # Kill Switch
│   ├── models.py
│   └── service.py
├── decision_trace/          # Decision Trace
│   ├── models.py
│   └── recorder.py
└── api/                     # API层
    ├── delegation.py
    ├── policy.py
    ├── approval.py
    ├── risk.py
    └── kill_switch.py
```

## 核心概念

### Delegation Profile（委托档位）

| 档位 | 说明 |
|------|------|
| Observe Only | 只观察与建议，不起草不发送 |
| Draft First | 自动起草，但所有消息需人工确认 |
| Approve to Send | 低风险动作自动准备，用户一键审批后发出 |
| Bounded Auto | 在明确预算和动作边界内自动执行 |
| Human Only | 该类关系或场景禁止代理主动介入 |

### Risk Engine 四层模型

1. **Relationship Risk**: 这是对谁说话？
2. **Action Risk**: 准备做什么动作？
3. **Content Risk**: 这段内容是否涉及承诺/冲突/隐私/不确定性？
4. **Consequence Risk**: 如果发出后出错，代价有多高？

### 决策输出（6种）

- `allow` - 允许自动执行
- `draft_only` - 仅允许起草
- `require_approval` - 需要审批后才能执行
- `bounded_execution` - 在边界内自动执行
- `escalate_to_human` - 升级给人工处理
- `deny` - 拒绝执行

### 8步决策链

1. 读取 thread objective 与当前状态
2. 读取 relationship class 与 delegation profile
3. 生成候选动作
4. 进行规则命中与预算检查
5. 进行内容/语义风险评估
6. 进行结果代价评估
7. 决定：自动执行/进入审批/升级人工或拒绝
8. 记录完整 decision trace

## 快速开始

```python
from uuid import uuid4
from policy_control.controller import PolicyControlController

# 创建控制器
controller = PolicyControlController()

# 评估动作
thread_id = uuid4()
result = controller.evaluate_action(
    thread_id=thread_id,
    action="send_message",
    action_type="send_message",
    content="Hi, just checking in.",
    relationship_class="colleague",
)

print(f"Decision: {result['decision'].value}")
print(f"Reason: {result['decision_reason']}")
```

或者直接运行示例：

```bash
python -m src.policy_control
```

## API接口

### Delegation API
- `POST /threads/{id}/delegation-profile` - 设置线程委托档位
- `POST /relationships/{id}/delegation-profile` - 设置关系默认档位
- `GET /delegation-profiles` - 查询可用档位

### Policy API (内部)
- `POST /policy/evaluate` - 策略评估

### Approval API
- `GET /approvals` - 查询待审批列表
- `GET /approvals/{id}` - 查询审批详情
- `POST /approvals/{id}:resolve` - 审批操作

### Risk API (内部)
- `POST /risk/evaluate` - 风险评估

### Kill Switch API
- `POST /kill-switches` - 激活熔断
- `DELETE /kill-switches/{id}` - 解除熔断
- `GET /kill-switches` - 查询当前生效的熔断

详见 [API文档](docs/api/openapi.yaml)

## 文档

- [数据模型设计](docs/design/data_models.md)
- [状态机设计](docs/design/state_machines.md)
- [8步决策链](docs/design/decision_chain.md)
- [测试用例清单](docs/testing/test_cases.md)

## 质量要求

- 策略引擎单元测试覆盖率 ≥ 95%
- 风险引擎默认保守兜底：异常情况一律 escalate
- 审批操作 P99 &lt; 300ms
- Kill Switch 激活后 &lt; 1s 所有动作冻结
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

