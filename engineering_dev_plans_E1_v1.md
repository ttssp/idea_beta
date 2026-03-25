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