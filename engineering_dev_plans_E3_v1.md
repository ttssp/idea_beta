# 代理原生通信控制层｜工程师分工与详细开发计划 V1.0

> 文档用途：明确项目工程师配置、职责边界与各自的详细开发计划。  
> 关联文档：`agent_native_comm_control_PRD_Blueprint_RnDPlan_v3.md`、`test_plan_v1.md`

---

## 1. 团队评估与工程师配置

### 1.1 评估依据

基于 PRD 的架构分层（8 层逻辑架构）、技术复杂度、模块间依赖关系以及 6 个月的研发周期，经评估，本项目需要 **5 名工程师**并行开发。

**核心判断逻辑**：

1. **后端是绝对主战场**：Thread Engine、Policy Runtime、Risk Engine、Action Runtime、Audit/Replay、Ingress/Egress 六大核心模块全部在后端，占总工作量 60%+。需要 3 名后端工程师分工推进。
2. **前端是信任建设的关键界面**：Inbox、Thread Detail、Approval Center、Replay Center 不是简单的 CRUD 页面，而是"控制界面"——信息密度高、实时性要求强、交互模式复杂。需要 1 名资深前端工程师。
3. **AI/Agent 是差异化能力**：Planner、Risk Classifier、Message Drafter 是产品智能化的核心，但必须与后端确定性执行严格分离。需要 1 名 AI 工程师。

### 1.2 工程师配置表

| 编号 | 角色 | 职责域 | 核心模块 | 关键技能要求 |
|---|---|---|---|---|
| **E1** | 后端工程师 - Thread Core | 线程内核 + 数据层 | Thread Engine, Event Store, 对象模型, 数据库 | 状态机设计, 事件溯源, PostgreSQL |
| **E2** | 后端工程师 - Policy & Control | 策略引擎 + 审批 + 风控 | Delegation Runtime, Approval Engine, Risk Engine, Kill Switch | 规则引擎, 权限系统, 决策链 |
| **E3** | 后端工程师 - Integration & Action | 外部集成 + 动作执行 | Channel Adapters, Ingress/Egress Gateway, Action Runtime, Outbox/Inbox | API 集成, 消息队列, 幂等控制 |
| **E4** | 前端工程师 - Control Surface | 全部前端界面 | Inbox, Thread Detail, Approval Center, Replay Center, Delegation UI | React/Vue, 实时数据, 复杂交互 |
| **E5** | AI/Agent 工程师 - Intelligence | AI 推理与生成 | Planner, Risk Classifier, Message Drafter, Pack Logic | LLM 应用, Prompt Engineering, NLP |

### 1.3 模块依赖关系图

```
                    ┌─────────────┐
                    │   E4: 前端   │
                    │ Control     │
                    │ Surface     │
                    └──────┬──────┘
                           │ API 调用
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
   │ E1: Thread  │  │ E2: Policy │  │ E3: Integr │
   │ Core        │◄─┤ & Control  │  │ & Action   │
   │             │  │            │  │            │
   └──────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │               │
          │         ┌─────▼──────┐        │
          │         │ E5: AI/    │        │
          └─────────┤ Agent      ├────────┘
                    │ Intelligence│
                    └────────────┘
```

**关键依赖链**：
- E2、E3、E4 依赖 E1 的 Thread 数据模型和基础 API
- E5 依赖 E1 的 Thread 上下文和 E2 的策略接口
- E3 依赖 E2 的策略决策输出
- E4 依赖 E1/E2/E3 的所有后端 API

**并行策略**：Phase 0 统一定义接口契约后，各工程师可以基于 mock/stub 并行开发。
---

## 4. E3：后端工程师 - Integration & Action（外部集成 + 动作执行）

### 4.1 职责概述

E3 负责系统的"手脚"——Channel Adapter 连接外部世界（Email / Calendar），Action Runtime 执行具体动作（发邮件、回写日历、follow-up），Ingress/Egress Gateway 管理消息收发。这是系统与外部世界交互的唯一出口，幂等性和可靠性是第一要务。

### 4.2 核心交付物

| 模块 | 交付物 | 说明 |
|---|---|---|
| Channel Adapter - Email | Gmail/Outlook API 集成，收发邮件 | P0 集成 |
| Channel Adapter - Calendar | Google/Outlook Calendar API 集成 | P0 集成 |
| Ingress Gateway | Webhook 接收、去重、验签、路由到 Thread | 外部 → 内部 |
| Egress Gateway | 外发排队、幂等发送、重试、回执处理 | 内部 → 外部 |
| Action Runtime | ActionRun 状态机、执行引擎、动作类型注册 | 执行层核心 |
| Outbox/Inbox Pattern | 消息排队表、消费者、幂等控制 | 可靠性保障 |
| External Resolver | 外部消息 → 内部 Thread 的映射与去重 | 线程关联 |

### 4.3 详细开发计划

#### Phase 0（第 0–2 周）：定义与冻结

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W0 | 调研 Email/Calendar API | API 能力清单 + 限制说明 | 确认 Gmail + Google Calendar 为首发 |
| W0 | 设计 ActionRun 状态机 | 状态机图 + 流转规则 | 覆盖 10 种状态 |
| W1 | 设计 Outbox/Inbox 模型 | schema + 消费逻辑 + 幂等方案 | 保证 exactly-once 语义 |
| W1 | 设计 ExternalBinding 映射方案 | 映射规则 + 去重策略 | 覆盖 email thread/message ID 映射 |
| W2 | 设计 Channel Adapter 接口规范 | 统一适配器接口定义 | 新增渠道只需实现接口 |
| W2 | 冻结接口契约 | OpenAPI spec（Action/Ingress/Egress） | E1/E2/E4 可基于 mock 开发 |

#### Phase 1A（第 3–5 周）：ActionRun + Outbox/Inbox

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W3 | 实现 ActionRun 状态机核心 | 动作创建/状态流转/幂等控制 | AR-001 至 AR-011 测试通过 |
| W3 | 实现 Idempotency Key 机制 | 幂等键生成/校验/去重 | AR-I01 至 AR-I04 测试通过 |
| W4 | 实现 Outbox Pattern | 消息排队表 + 消费者 + 定时重试 | 不重复发送，断点恢复 |
| W4 | 实现 Inbox Pattern | Webhook 事件接收表 + 去重 + 消费 | 重复 webhook 去重 |
| W5 | 实现 Ingress Gateway 框架 | Webhook 路由 + 验签 + 分发 | 支持 email/calendar webhook |
| W5 | 实现 External Resolver | 外部消息 → 内部 Thread 映射 | EB-001 至 EB-005 测试通过 |

#### Phase 1B（第 6–8 周）：Email + Calendar 集成

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W6 | 实现 Email Adapter - 收件 | Gmail API Pub/Sub → Ingress | EM-R01 至 EM-R05 测试通过 |
| W6 | 实现 Email Adapter - 发件 | Egress → Gmail API 发送 | EM-S01 至 EM-S04 测试通过 |
| W7 | 实现 Email 异常隔离 | API 异常/token 过期处理 | EM-E01 至 EM-E03 测试通过 |
| W7 | 实现 Calendar Adapter - 读取 | 空闲时间查询/冲突检测 | CA-R01 至 CA-R03 测试通过 |
| W8 | 实现 Calendar Adapter - 写入 | 创建/更新/取消日历事件 | CA-W01 至 CA-W04 测试通过 |
| W8 | 实现 Calendar 幂等与去重 | 日历事件幂等操作 | CA-I01 至 CA-I02 测试通过 |

#### Phase 2（第 9–16 周）：扩展与可靠性

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W9–W10 | Egress 重试策略优化 | 指数退避 + 最大重试 + 死信队列 |
| W11–W12 | OAuth Token 管理服务 | 自动刷新/撤销/多账户支持 |
| W13–W14 | Task/Doc 集成（二选一） | 至少一个 P1 集成完成 |
| W15–W16 | 集成监控与告警 | 外部 API 调用成功率/延迟/错误分布 |

#### Phase 3（第 17–24 周）：稳定化与扩展准备

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W17–W18 | 混沌测试（网络抖动/API 降级） | 异常场景覆盖 + 修复 |
| W19–W20 | Channel Adapter 抽象层完善 | 新渠道集成指南 + 测试框架 |
| W21–W22 | Outbox/Inbox 性能压测 | 1000 msg/min 吞吐验证 |
| W23–W24 | 全量回归 + 集成稳定性报告 | 集成可靠性 ≥ 99.5% |

### 4.4 接口契约（E3 对外提供）

```
# Action API
POST   /threads/{id}/actions:prepare          → 准备动作（生成 ActionRun）
POST   /threads/{id}/actions:execute           → 执行动作
POST   /threads/{id}/actions/{action_id}:cancel → 取消动作
GET    /threads/{id}/actions                    → 查询动作列表

# Message Send API
POST   /threads/{id}/messages:draft             → 起草消息（挂载到 thread）
POST   /threads/{id}/messages:send              → 发送消息（通过 egress）

# Ingress Webhook
POST   /ingress/email                           → Email webhook 入口
POST   /ingress/calendar                        → Calendar webhook 入口

# Delivery Status
POST   /delivery/status                         → 外部回执回调
GET    /delivery/{id}/status                     → 查询发送状态
```

### 4.5 质量要求

- ActionRun 幂等性测试 100% 通过
- 外部 API 调用重试不超过 3 次
- Outbox 消息处理延迟 P99 < 5s
- 外部异常不污染内部 Thread 状态（100% 隔离）
- OAuth token 自动刷新成功率 ≥ 99.9%

---

> 本文档随项目迭代持续更新。每个 Phase 结束时需评审进度并调整下阶段计划。
