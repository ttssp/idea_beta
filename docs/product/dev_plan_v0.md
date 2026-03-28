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

## 2. E1：后端工程师 - Thread Core（线程内核 + 数据层）

### 2.1 职责概述

E1 负责整个系统的"骨架"——Thread Engine 是系统的一等公民，所有模块都围绕 thread 运转。E1 还负责底层数据模型、事件存储和基础查询服务，是其他所有工程师的上游依赖。

### 2.2 核心交付物

| 模块 | 交付物 | 说明 |
|---|---|---|
| Thread Engine | Thread CRUD / 状态机 / 目标管理 / 参与者管理 / 摘要 / 责任方 | 系统一等公民 |
| 对象模型 | Thread / Principal / Relationship / Message / ThreadEvent / ExternalBinding 的 schema 与 ORM | 全局共享 |
| Event Store | append-only event log 的写入、读取、查询接口 | 回放基础 |
| 数据库基础设施 | Postgres schema / migration / 索引优化 | 全员依赖 |
| 基础 API | Thread 相关的所有 REST API | 前端依赖 |
| Identity & Principal | 统一主体模型（人 / 代理 / 外部方 / 服务方） | 全局共享 |
| Relationship Graph | 关系语义模型（关系类别 / 敏感度 / 默认档位） | E2 依赖 |

### 2.3 详细开发计划

#### Phase 0（第 0–2 周）：定义与冻结

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W0 | 设计完整对象模型（ER 图） | ER 图 + 字段说明文档 | 团队评审通过，所有工程师确认可用 |
| W0 | 设计 Thread 状态机 | 状态机图 + 流转规则文档 | 覆盖 10 种状态 + 所有合法/非法流转 |
| W1 | 设计 Event 模型与存储方案 | Event schema + 存储接口定义 | 支持 append-only + 按 thread 查询 |
| W1 | 设计 Principal / Relationship 模型 | schema 定义 | 覆盖 5 种关系类别 |
| W2 | 冻结接口契约 | OpenAPI spec（Thread 相关） | 前端 E4 和 AI E5 可基于 mock 开发 |
| W2 | 搭建项目基础框架 | 项目骨架 + CI/CD + DB migration 工具 | 全员可拉取并运行 |

#### Phase 1A（第 3–5 周）：Thread 内核实现

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W3 | 实现 Thread CRUD + 状态机核心 | Thread 创建/查询/状态流转 API | 单元测试覆盖所有合法/非法流转（TS-001 至 TS-N05） |
| W3 | 实现 Principal / Relationship 基础 | 身份与关系 CRUD | 5 种关系类别可创建查询 |
| W4 | 实现 Event Store | 事件写入/读取/按 thread 查询 | append-only 写入，顺序保证 |
| W4 | 实现 Message 模型 | 消息创建/查询，authored_mode 标注 | 4 种 authored_mode 正确记录 |
| W5 | 实现 Thread 摘要与责任方更新 | 状态变更时自动更新摘要和责任方 | 每次状态变更后摘要和责任方正确 |
| W5 | 实现 ExternalBinding 基础模型 | 外部线程/消息绑定 CRUD | 支持 email/calendar 绑定 |

#### Phase 1B（第 6–8 周）：完善与联调

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W6 | Thread 并发控制与乐观锁 | 并发安全的状态流转 | TS-N04 并发测试通过 |
| W6 | Thread Inbox 查询优化 | 按 bucket 分组查询 API | 支持 5 种 bucket 分类查询 |
| W7 | Event Store 性能优化 | 批量写入 + 索引优化 | 1000 事件查询 < 500ms |
| W7 | 与 E2 联调：策略结果写入 thread | 策略决策结果关联到 thread | 决策 trace 可查询 |
| W8 | 与 E3 联调：外部事件更新 thread | 外部回复正确更新 thread 状态 | EB-003 测试通过 |
| W8 | 与 E5 联调：AI 生成内容挂载到 thread | 草稿/建议关联到 thread | 生成内容可在 thread 上下文中查看 |

#### Phase 2（第 9–16 周）：扩展与优化

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W9–W10 | Thread 模板与场景化预设 | 3 类标准线程模板快速创建 |
| W11–W12 | Relationship Graph 扩展 | 关系导入/批量管理/历史记录 |
| W13–W14 | Event Store 高级查询 | 按事件类型/时间范围/actor 筛选 |
| W15–W16 | 性能压测与优化 | 50 并发 thread 场景下的性能基线 |

#### Phase 3（第 17–24 周）：稳定化

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W17–W18 | Thread 异常状态恢复机制 | 死锁检测 + 自动恢复 |
| W19–W20 | 数据归档与清理策略 | 已完成 thread 归档方案 |
| W21–W22 | 全量回归与边界修复 | 测试覆盖率 ≥ 90% |
| W23–W24 | 文档完善 + PMF 数据支撑 | 模块技术文档 + 性能报告 |

### 2.4 接口契约（E1 对外提供）

```
# Thread API
POST   /threads                     → 创建线程
GET    /threads                     → 查询线程列表（支持 bucket 筛选）
GET    /threads/{id}                → 查询线程详情
PATCH  /threads/{id}                → 更新线程（目标/参与者）
POST   /threads/{id}/pause          → 暂停线程
POST   /threads/{id}/resume         → 恢复线程
POST   /threads/{id}/takeover       → 接管线程

# Event API
GET    /threads/{id}/events         → 查询线程事件流
POST   /threads/{id}/events         → 写入事件（内部调用）

# Principal & Relationship API
POST   /principals                  → 创建主体
GET    /principals/{id}             → 查询主体
POST   /relationships               → 创建关系
GET    /relationships               → 查询关系列表

# Message API
POST   /threads/{id}/messages       → 创建消息
GET    /threads/{id}/messages        → 查询线程消息
```

### 2.5 质量要求

- 核心状态机单元测试覆盖率 ≥ 95%
- Event Store 写入保证 exactly-once
- Thread 查询 API P99 < 200ms
- 数据库 migration 支持前向/回滚

---

## 3. E2：后端工程师 - Policy & Control（策略引擎 + 审批 + 风控）

### 3.1 职责概述

E2 负责系统的"大脑和安全网"——策略引擎决定代理能做什么、不能做什么；审批引擎管理人机控制权切换；风险引擎确保越界动作被拦截。这是"可放心放权"的核心技术保障。

### 3.2 核心交付物

| 模块 | 交付物 | 说明 |
|---|---|---|
| Delegation Runtime | 委托档位管理、预算管理、策略命中逻辑 | 用户侧简单，系统侧细粒度 |
| Policy Engine | 策略规则 CRUD / 匹配 / 优先级 / 冲突解决 | 系统内部决策核心 |
| Approval Engine | 审批请求创建 / 审核 / 超时处理 / 批量操作 | 人机控制权切换中心 |
| Risk Engine | 四层风险判断 + 合成决策 + decision trace | 默认保守，宁可升级给人 |
| Kill Switch | 三层熔断（Global / Profile / Thread） | 安全底线 |
| Decision Trace | 每次决策的完整记录 | 可解释性基础 |

### 3.3 详细开发计划

#### Phase 0（第 0–2 周）：定义与冻结

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W0 | 设计 DelegationProfile 模型 | schema + 5 种档位定义 | 团队理解每种档位的行为边界 |
| W0 | 设计 PolicyRule 模型 | schema + 优先级机制 + 冲突解决规则 | 覆盖 scope/action/effect/conditions |
| W1 | 设计 Risk Engine 四层模型 | 风险分层文档 + 决策输出定义 | 6 种决策输出明确定义 |
| W1 | 设计 ApprovalRequest 模型 | schema + 状态流转 | 覆盖创建/审核/超时/失效 |
| W2 | 设计 Kill Switch 模型与行为规范 | 三层熔断规范 + 联动行为 | 明确每层熔断的影响范围 |
| W2 | 冻结对外接口 | OpenAPI spec（策略/审批/风控相关） | E3/E4/E5 可基于 mock 开发 |

#### Phase 1A（第 3–5 周）：策略与审批核心

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W3 | 实现 DelegationProfile CRUD | 5 种档位的创建/查询/更新/绑定 | DP-001 至 DP-006 测试通过 |
| W3 | 实现 PolicyRule 匹配引擎 | 规则创建/匹配/优先级排序 | PL-001 至 PL-005 测试通过 |
| W4 | 实现 Approval Engine 核心 | 审批请求创建/审核(批准/拒绝/修改)/接管 | AP-001 至 AP-005 测试通过 |
| W4 | 实现档位切换逻辑 | 切换后立即生效 + 自动动作冻结/恢复 | DP-S01 至 DP-S04 测试通过 |
| W5 | 实现动作预算管理 | 预算计数/窗口重置/超限降级 | BG-001 至 BG-005 测试通过 |
| W5 | 实现策略决策链 | 从 thread context 到最终决策的完整链路 | 8 步决策链可执行 |

#### Phase 1B（第 6–8 周）：风控与熔断

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W6 | 实现 Risk Engine - Relationship Risk | 基于关系类别的风险评估 | RR-001 至 RR-005 测试通过 |
| W6 | 实现 Risk Engine - Action Risk | 基于动作类型的风险评估 | AK-001 至 AK-005 测试通过 |
| W7 | 实现 Risk Engine - Content Risk（规则层） | 基于关键词/模式的内容风险检测 | CR-001 至 CR-006 测试通过 |
| W7 | 实现 Risk Engine - Consequence Risk | 基于历史数据和规则的结果风险评估 | CQ-001 至 CQ-004 测试通过 |
| W7 | 实现综合风险决策合成器 | 四层风险合成 → 6 种决策输出 | RD-001 至 RD-006 测试通过 |
| W8 | 实现 Kill Switch（三层） | Global / Profile / Thread 熔断 | KS-001 至 KS-010 测试通过 |
| W8 | 实现 Decision Trace 写入 | 每次决策完整记录到 event log | RP-005 测试通过 |

#### Phase 2（第 9–16 周）：扩展与精细化

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W9–W10 | 关系模板驱动的默认策略 | 关系类型 → 默认委托档位自动绑定 |
| W11–W12 | 与 E5 联调 Content Risk（模型辅助） | 小模型辅助内容风险判断 + 规则兜底 |
| W13–W14 | 审批超时与自动降级 | 审批超时策略 + 提醒 + 降级 |
| W14–W15 | Bounded Auto 试点规则 | 特定场景下自动执行的策略包 |
| W15–W16 | 策略热更新与 A/B 机制 | 策略规则在线更新，不停服 |

#### Phase 3（第 17–24 周）：稳定化与运维

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W17–W18 | 风险热图与异常聚类 | 按关系/动作/内容维度的风险仪表板 |
| W19–W20 | 策略命中分析 | 哪些规则被频繁命中/从未命中 |
| W21–W22 | 误升级率优化 | 降低 false escalation，提升用户体验 |
| W23–W24 | 全量回归 + 红队测试 | 安全边界覆盖率 ≥ 95% |

### 3.4 接口契约（E2 对外提供）

```
# Delegation API
POST   /threads/{id}/delegation-profile     → 设置线程委托档位
POST   /relationships/{id}/delegation-profile → 设置关系默认档位
GET    /delegation-profiles                  → 查询可用档位

# Policy API (内部)
POST   /policy/evaluate                      → 策略评估（输入 context → 输出决策）

# Approval API
GET    /approvals                            → 查询待审列表
GET    /approvals/{id}                       → 查询审批详情
POST   /approvals/{id}:resolve               → 审批操作（approve/reject/modify/takeover）

# Risk API (内部)
POST   /risk/evaluate                        → 风险评估（输入动作 → 输出风险等级 + 决策建议）

# Kill Switch API
POST   /kill-switches                        → 创建熔断
DELETE /kill-switches/{id}                   → 解除熔断
GET    /kill-switches                        → 查询当前生效的熔断
```

### 3.5 质量要求

- 策略引擎单元测试覆盖率 ≥ 95%
- 风险引擎默认保守兜底：异常情况一律 escalate
- 审批操作 P99 < 300ms
- Kill Switch 激活后 < 1s 所有动作冻结

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

## 5. E4：前端工程师 - Control Surface（控制界面）

### 5.1 职责概述

E4 负责整个产品的"面孔"——但这不是一个聊天界面，而是一个**控制界面**。用户在这里看到的不是消息流，而是"目标推进状态"；操作的不是发消息，而是"审批、接管、放权"。信息架构和交互设计的质量直接决定用户的信任建设速度。

### 5.2 核心交付物

| 模块 | 交付物 | 说明 |
|---|---|---|
| Thread Inbox | 工作队列视图（5 种 bucket 分组） | 主页面，不是消息列表 |
| Thread Detail | 目标推进视图（目标/状态/责任方/下一步/历史） | 围绕"目标推进"组织 |
| Approval Center | 共享控制界面（原因/预览/规则/操作） | 人机交互核心 |
| Replay Center | 可视化时间线 + 决策解释 | 信任基础设施 |
| Delegation Surface | 委托档位/关系模板/动作预算/Kill Switch | 放权产品化 |
| 实时更新 | WebSocket / SSE 实时推送 | 状态变化即时反映 |
| 通用组件库 | 状态徽标/风险标签/审批卡片/时间线组件 | 全局复用 |

### 5.3 详细开发计划

#### Phase 0（第 0–2 周）：定义与冻结

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W0 | 信息架构设计 | 页面结构图 + 导航方案 | 覆盖 5 大核心页面 |
| W0 | 选型与基础搭建 | 技术栈确定（React/Next.js + 状态管理） | 项目骨架可运行 |
| W1 | UI 规范与组件库初始化 | 设计系统基础（颜色/字体/间距/组件） | 基础组件可用 |
| W1 | Mock API 层搭建 | 基于 E1/E2/E3 接口契约的 mock 服务 | 前端可独立开发 |
| W2 | 线框图评审 | 5 个核心页面的 wireframe | 产品/设计评审通过 |
| W2 | 实时通信方案设计 | WebSocket/SSE 方案 + 消息格式 | 支持 thread 状态实时推送 |

#### Phase 1A（第 3–5 周）：核心页面骨架

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W3 | Thread Inbox - 基础结构 | 5 种 bucket 分组展示 + 排序 | UI-001 至 UI-004 基础通过 |
| W3 | Thread 创建流程 | 创建 thread 表单（目标/参与者/档位） | 可创建 3 类标准线程 |
| W4 | Thread Detail - 基础结构 | 目标/状态/责任方/下一步/历史展示 | UI-005 至 UI-008 基础通过 |
| W4 | 消息展示组件 | 区分 authored_mode 的消息气泡 | 4 种 authored_mode 可视化区分 |
| W5 | Approval Center - 基础结构 | 待审列表 + 审批详情 + 操作按钮 | UI-009 至 UI-011 基础通过 |
| W5 | 实时推送接入 | WebSocket 连接 + 状态变化实时刷新 | thread 状态变更 < 1s 反映到 UI |

#### Phase 1B（第 6–8 周）：交互完善与联调

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W6 | Approval 交互完善 | 批准/拒绝/修改/接管的完整交互 | 包含确认弹窗、加载状态、错误处理 |
| W6 | Thread Detail 动作展示 | ActionRun 状态可视化 + 取消操作 | 每个 action 状态清晰可见 |
| W7 | Replay Center - 基础版 | Thread 时间线可视化 | UI-013 至 UI-015 基础通过 |
| W7 | Delegation Surface - 基础版 | 委托档位选择 + Kill Switch 开关 | 5 种档位可切换，3 层 Kill Switch 可操作 |
| W8 | 对接真实 API（替换 mock） | 全部页面接入后端真实 API | E2E 流程可走通 |
| W8 | 错误处理与空状态 | 全局错误提示 + 各页面空状态 | 用户不会遇到白屏 |

#### Phase 2（第 9–16 周）：体验提升

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W9–W10 | Replay Center 增强 | 决策点高亮 + 策略命中弹窗 + 筛选 |
| W11–W12 | Thread Detail 增强 | 外部消息预览 + 风险解释卡片 |
| W13–W14 | 移动端适配 | 响应式布局 + 审批操作移动端优化 |
| W15–W16 | 指标仪表板 | metrics 数据可视化（线程闭环率/节省触点数） |

#### Phase 3（第 17–24 周）：打磨与稳定化

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W17–W18 | Ops Console（运维后台） | 全局 thread 监控 + Kill Switch 管理 |
| W19–W20 | 无障碍与国际化基础 | a11y 合规 + i18n 框架搭建 |
| W21–W22 | 性能优化 | 首屏加载 < 2s，列表虚拟滚动 |
| W23–W24 | 全量 UI 回归 + 用户体验报告 | 所有页面回归通过 |

### 5.4 页面信息架构

```
App Shell
├── Thread Inbox（主页）
│   ├── Bucket: Needs Approval    → 数量 badge
│   ├── Bucket: Agent Running     → 数量 badge
│   ├── Bucket: Awaiting External → 数量 badge
│   ├── Bucket: Blocked / At Risk → 数量 badge + 告警色
│   └── Bucket: Completed         → 可折叠
│
├── Thread Detail（点击某个 thread）
│   ├── Header: 目标 + 状态 + 责任方 + 档位
│   ├── Action Bar: 接管 / 暂停 / 恢复 / Kill Switch
│   ├── Timeline: 消息 + 动作 + 系统事件（按时间序）
│   ├── Next Step: 代理建议 + 用户操作
│   └── Side Panel: 参与者 / 关系 / 策略 / 风险
│
├── Approval Center
│   ├── 待审列表（按紧急度排序）
│   └── 审批详情卡片
│       ├── 为什么需要审批
│       ├── 代理准备做什么
│       ├── 对外预览
│       ├── 触发规则/风险原因
│       └── 操作: 批准 / 拒绝 / 修改 / 接管
│
├── Replay Center
│   ├── Thread 选择器
│   └── 可视化时间线
│       ├── 事件节点（颜色区分类型）
│       ├── 决策点标注
│       └── 点击展开 decision trace
│
└── Settings
    ├── 委托档位管理
    ├── 关系模板管理
    ├── 动作预算设置
    └── Kill Switch 控制面板
```

### 5.5 质量要求

- 核心页面首屏加载 < 2s
- 实时状态推送延迟 < 1s
- 所有交互操作有 loading/success/error 反馈
- 支持 Chrome / Safari / Firefox 最新 2 个版本
- 前端组件测试覆盖率 ≥ 80%

---

## 6. E5：AI/Agent 工程师 - Intelligence（AI 推理与生成）

### 6.1 职责概述

E5 负责系统的"智能层"——Planner 负责理解目标并生成动作计划，Risk Classifier 辅助内容风险判断，Message Drafter 负责起草消息。**关键原则**：LLM 参与判断与起草，但真正的执行、状态变更、审批、发送必须落在确定性系统边界内。E5 的输出永远是"建议"，最终决策由 E1/E2 的确定性逻辑执行。

### 6.2 核心交付物

| 模块 | 交付物 | 说明 |
|---|---|---|
| Thread Planner | 目标理解 + 初始动作计划生成 + 下一步建议 | 线程推进的智能核心 |
| Message Drafter | 邮件/消息起草 + 候选时间生成 + checklist 生成 | 生成层 |
| Risk Classifier | 内容风险分类辅助（金额/承诺/冲突/隐私/情绪） | E2 Risk Engine 的 ML 辅助层 |
| Pack Logic | 场景化能力包（时间协调包/资料收集包/跟进催办包） | 场景化智能 |
| Prompt & Template Library | Prompt 工程 + 模板管理 + 版本控制 | 可维护的 prompt 资产 |
| Evaluation Framework | LLM 输出质量评估 + 回归测试集 | 质量保障 |

### 6.3 详细开发计划

#### Phase 0（第 0–2 周）：定义与冻结

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W0 | 调研 LLM 选型 | 模型评估报告（GPT-4 / Claude / 开源模型） | 延迟/成本/质量权衡明确 |
| W0 | 设计 Planner 接口契约 | 输入（thread context）→ 输出（action plan）定义 | E1/E2 确认可对接 |
| W1 | 设计 Drafter 接口契约 | 输入（context + template）→ 输出（draft message）定义 | E3 确认可对接 |
| W1 | 设计 Risk Classifier 接口 | 输入（content）→ 输出（risk tags + confidence）定义 | E2 确认可对接 |
| W2 | 编写 3 条标准线程的 demo script | 时间协调/资料收集/跟进催办的完整对话流 | 可作为开发参考和测试基线 |
| W2 | 初始化 prompt 库 | 基础 prompt 模板（planner/drafter/classifier） | 版本化管理 |

#### Phase 1A（第 3–5 周）：Planner + Drafter 核心

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W3 | 实现 Thread Planner 核心 | 输入 thread objective → 输出初始动作计划 | 3 类标准线程可生成合理计划 |
| W3 | 实现下一步建议引擎 | 基于 thread 当前状态推荐下一步 | 建议准确率 ≥ 80%（人工评估） |
| W4 | 实现 Message Drafter - 邮件 | 基于 context 起草事务邮件 | 可用率 ≥ 70%（无需大改即可发出） |
| W4 | 实现候选时间生成 | 基于日历信息生成候选时间 | 不与已有日程冲突 |
| W5 | 实现 Checklist 生成 | 资料收集场景的缺项清单 | 列表完整性 ≥ 85% |
| W5 | Prompt 优化与 few-shot 调试 | 优化后的 prompt + 评估数据集 | 各场景输出质量达标 |

#### Phase 1B（第 6–8 周）：Risk Classifier + Pack Logic

| 周次 | 任务 | 交付物 | 验收标准 |
|---|---|---|---|
| W6 | 实现 Risk Classifier - 金额/报价 | 检测包含金额/报价/折扣的内容 | recall ≥ 95%（宁可多报不漏报） |
| W6 | 实现 Risk Classifier - 承诺/合同 | 检测法律/合同/时间承诺 | recall ≥ 95% |
| W7 | 实现 Risk Classifier - 情绪/冲突 | 检测投诉/拒绝/争议/强情绪 | recall ≥ 90% |
| W7 | 实现 Risk Classifier - 隐私 | 检测身份证/银行卡/敏感个人信息 | recall ≥ 99% |
| W8 | 实现时间协调 Pack | 约时间/改期/确认/提醒完整能力包 | 时间协调线程 E2E 可走通 |
| W8 | 实现资料收集 Pack（基础） | 催办/确认缺项/汇总基础能力 | 资料收集线程 E2E 可走通 |

#### Phase 2（第 9–16 周）：扩展与优化

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W9–W10 | 跟进催办 Pack | follow-up 节奏/语气升级/SLA 检测 |
| W11–W12 | Risk Classifier 小模型训练 | 用积累数据训练轻量分类器，降低延迟和成本 |
| W13–W14 | Thread 摘要自动生成优化 | 基于 event log 的高质量摘要 |
| W15–W16 | Evaluation Framework 完善 | 自动化评估流水线 + 回归测试集 |

#### Phase 3（第 17–24 周）：稳定化与洞察

| 周次范围 | 任务 | 交付物 |
|---|---|---|
| W17–W18 | 失败线程分析 | 分析代理推进失败的模式和原因 |
| W19–W20 | Prompt 版本管理与灰度 | prompt 更新灰度发布机制 |
| W21–W22 | LLM 降级方案 | LLM 不可用时的降级策略 |
| W23–W24 | 质量报告 + 模型选型建议 | 各场景质量数据 + V2 模型建议 |

### 6.4 接口契约（E5 对外提供）

```
# Planner API (内部)
POST   /ai/plan                → 输入 thread context → 输出 action plan
POST   /ai/suggest-next        → 输入 thread state → 输出下一步建议

# Drafter API (内部)
POST   /ai/draft-message       → 输入 context + template → 输出 draft
POST   /ai/generate-time-slots → 输入 calendar data → 输出候选时间
POST   /ai/generate-checklist  → 输入 objective → 输出 checklist

# Risk Classifier API (内部)
POST   /ai/classify-risk       → 输入 content → 输出 risk tags + confidence

# Thread Summary API (内部)
POST   /ai/summarize-thread    → 输入 event log → 输出 summary
```

### 6.5 质量要求

- Risk Classifier recall ≥ 95%（金额/承诺/隐私类 ≥ 99%）
- Message Drafter 可用率 ≥ 70%（人工评估）
- Planner 建议合理率 ≥ 80%（人工评估）
- LLM API 调用 P99 < 5s
- 所有 AI 输出不直接触发系统执行，必须经过确定性逻辑

---

## 7. 跨工程师协作计划

### 7.1 协作时间线

```
     W0    W2    W4    W6    W8    W10   W12   W14   W16   W18   W20   W22   W24
     │     │     │     │     │     │     │     │     │     │     │     │     │
E1 ──┤ P0  ├──── P1A ─├─── P1B ──├──── P2 ──────────────├──── P3 ────────────┤
     │冻结  │Thread │并发/联调│关系扩展 │性能优化           │异常恢复 │归档      │
     │     │内核   │       │模板化  │                   │       │         │
E2 ──┤ P0  ├──── P1A ─├─── P1B ──├──── P2 ──────────────├──── P3 ────────────┤
     │冻结  │策略/  │风控/   │关系模板 │Bounded Auto      │风险热图 │红队测试  │
     │     │审批   │熔断   │       │策略热更新           │       │         │
E3 ──┤ P0  ├──── P1A ─├─── P1B ──├──── P2 ──────────────├──── P3 ────────────┤
     │冻结  │Action │Email/ │Task/Doc│重试优化            │混沌测试 │压测     │
     │     │Outbox │Cal   │       │监控告警             │       │         │
E4 ──┤ P0  ├──── P1A ─├─── P1B ──├──── P2 ──────────────├──── P3 ────────────┤
     │冻结  │核心页面│联调/  │Replay │移动端              │Ops    │性能优化  │
     │     │骨架   │交互   │增强   │仪表板              │Console│         │
E5 ──┤ P0  ├──── P1A ─├─── P1B ──├──── P2 ──────────────├──── P3 ────────────┤
     │冻结  │Planner│Risk  │Follow │小模型训练           │失败分析│质量报告  │
     │     │Drafter│Class │-up Pack│评估框架             │       │         │
```

### 7.2 关键联调节点

| 时间点 | 联调内容 | 参与者 | 验收标准 |
|---|---|---|---|
| W5 末 | Thread 创建 → Planning → Draft | E1 + E5 | Thread 创建后自动生成计划和草稿 |
| W5 末 | 策略评估 → 审批创建 | E1 + E2 | 动作触发正确的审批流程 |
| W6 | Inbox + Thread Detail 接入真实 API | E1 + E4 | 前端页面展示真实数据 |
| W7 | Email 收发 → Thread 更新 | E1 + E3 | 外部邮件正确关联到 thread |
| W7 | Approval Center 接入真实审批 | E2 + E4 | 审批操作可走通 |
| W8 | 风险评估 → 策略决策 → 动作执行 | E2 + E3 + E5 | 完整决策链可执行 |
| W8 | 3 类标准线程 E2E 走通 | 全员 | MVP 验收 |
| W12 | Risk Classifier 对接 Risk Engine | E2 + E5 | 模型辅助 + 规则兜底 |
| W16 | Bounded Auto 完整链路 | E2 + E3 + E5 | 自动执行链路验证 |

### 7.3 每周同步机制

| 频率 | 形式 | 内容 |
|---|---|---|
| 每日 | 15 min 站会 | 进度/阻塞/依赖 |
| 每周一 | 1h 周计划会 | 本周目标 + 跨模块依赖确认 |
| 每周五 | 30 min Demo | 本周交付物演示 |
| 每 Phase 结束 | 2h 评审会 | Go/No-Go 评审 + 下阶段计划 |

### 7.4 接口契约管理

- 所有接口契约在 Phase 0 冻结，统一维护在 OpenAPI spec 中
- 契约变更需提交 RFC，经受影响方评审后合并
- CI 中集成合约测试，防止契约被意外破坏
- 每个工程师维护自己模块的 mock 服务，供上下游使用

---

## 8. 风险管理与应对

### 8.1 开发风险

| 风险 | 影响 | 责任人 | 应对策略 |
|---|---|---|---|
| E1 Thread 内核延期 | 阻塞所有下游 | E1 | Phase 0 优先冻结 Thread 接口，下游先用 mock |
| 外部 API 限制超预期 | 集成功能缩水 | E3 | 提前调研 API 限制，准备降级方案 |
| LLM 输出质量不达标 | 用户体验差 | E5 | 准备 fallback 模板，人工编辑兜底 |
| 风控规则覆盖不全 | 越界事故 | E2 | 默认保守策略 + 红队持续测试 |
| 前端交互复杂度超预期 | 体验打折 | E4 | 分阶段交付，MVP 先保证核心流程 |

### 8.2 里程碑 Check-in

| 时间点 | Check-in 内容 | Go/No-Go 标准 |
|---|---|---|
| W2 末 | Phase 0 完成度 | 所有接口契约冻结，demo script 可执行 |
| W5 末 | Phase 1A 完成度 | Thread 内核 + 策略核心 + AI 核心可独立运行 |
| W8 末 | Phase 1B 完成度 | 3 类线程 E2E 走通，无 P0 bug |
| W12 末 | Phase 2 中期 | 10+ 种子用户开始使用 |
| W16 末 | Phase 2 完成度 | Bounded Auto 试点可用 |
| W20 末 | Phase 3 中期 | Ops Console 可用，风险热图可读 |
| W24 末 | Phase 3 完成度 | PMF 评估数据就绪 |

---

## 9. 技术栈建议

| 层级 | 推荐技术 | 理由 |
|---|---|---|
| 后端语言 | TypeScript (Node.js) 或 Python (FastAPI) | 团队熟悉度优先；TypeScript 前后端统一 |
| 数据库 | PostgreSQL | 当前态 + 关系查询 + JSONB 灵活性 |
| Event Store | PostgreSQL (events 表) → 后期可迁移 Kafka | 初期简化架构，保持扩展性 |
| 消息队列 | BullMQ (Redis) 或 SQS | Outbox 消费 + 异步任务 |
| 前端 | React + Next.js + TailwindCSS | 控制界面复杂度适配 |
| 实时通信 | WebSocket (Socket.io) | 状态推送 |
| LLM | OpenAI GPT-4o / Claude 3.5 | 主力模型；小模型可用 GPT-4o-mini |
| CI/CD | GitHub Actions + Docker | 自动化测试与部署 |
| 监控 | Prometheus + Grafana + Sentry | 指标 + 日志 + 异常 |

---

## 附录 A：各工程师核心 KPI

| 工程师 | Phase 1 KPI | Phase 2 KPI | Phase 3 KPI |
|---|---|---|---|
| E1 | Thread 状态机 100% 正确；API P99 < 200ms | 50 并发 thread 无异常 | 测试覆盖率 ≥ 90% |
| E2 | 0 越界事故；审批 P99 < 300ms | Bounded Auto 试点无事故 | 误升级率 < 5% |
| E3 | 0 重复发送；外部异常 100% 隔离 | 集成可靠性 ≥ 99.5% | 混沌测试全部通过 |
| E4 | 核心页面可用；实时推送 < 1s | 移动端适配完成 | 首屏 < 2s |
| E5 | Drafter 可用率 ≥ 70%；Classifier recall ≥ 95% | 小模型部署完成 | LLM 降级方案可用 |

---

> 本文档随项目迭代持续更新。每个 Phase 结束时需评审进度并调整下阶段计划。
