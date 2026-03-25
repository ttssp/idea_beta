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
