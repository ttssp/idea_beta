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

> 本文档随项目迭代持续更新。每个 Phase 结束时需评审进度并调整下阶段计划。
