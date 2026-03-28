# PRD 版本核心区别分析

## 概述

本文档对比分析第一版PRD (`PRD_v0.md`) 和当前版本PRD (`COMMUNICATION_OS_V1_SPEC.md`) 的核心区别，以及对应的开发计划差异。

---

## 一、产品定位的核心区别

### 第一版PRD (v0)
**产品定位**：代理原生通信控制层（Agent-Native Communication Control Layer）

- 强调"不把它定义成'更聪明的聊天工具'，而把它定义成'可委托、可审计、可接管的通信控制平面'"
- 产品外形可以接近 messenger，但本质是控制平面
- 入口策略：优先从 **Email + Calendar** 切入，内部轻量消息入口仅用于 demo/dogfood
- 定位更偏向"控制层"和"插件"的概念

### 当前版本PRD (v1)
**产品定位**：Communication OS - thread-first, identity-aware, delegation-governed communication and collaboration operating system

- 强调"它不是更聪明的信使，而是一个系统"
- 定位为**操作系统**，而不是控制平面或插件
- "This product sits between categories: messenger, workflow engine, approval system, external communication layer, AI delegation runtime, collaboration operating system"
- 最接近的未来类别标签：`Delegated Communication and Collaboration OS`

**核心转变**：从"控制层/插件" → "完整的操作系统"

---

## 二、核心概念模型的区别

### 第一版PRD (v0) 的核心概念
1. **Delegation Profile（委托档位）** - 5个档位：
   - Observe Only
   - Draft First
   - Approve to Send
   - Bounded Auto
   - Human Only

2. **8层逻辑架构**：
   - Thread Kernel
   - Policy Runtime
   - Risk Engine
   - Action Runtime
   - Audit/Replay
   - Ingress/Egress
   - AI/Agent Intelligence
   - Control Surface (Frontend)

3. **放权路径**：四段式放权阶梯（Observe → Draft → Approve → Bounded Auto）

### 当前版本PRD (v1) 的核心概念
1. **5大核心契约（Contracts）**：
   - `AuthorityGrant` - 权威授予
   - `SenderStack` - 发送者栈
   - `DisclosurePolicy` - 披露策略
   - `AttentionDecision` - 注意力决策
   - `ActionEnvelope` - 动作信封

2. **9大核心实体**：
   - Identity
   - Authority Grant
   - Relationship
   - Thread
   - Action
   - Approval
   - Event
   - Replay
   - Attention Firewall

3. **8大产品原则**：
   - Identity First
   - Delegation Is Layered
   - Thread Over Message
   - Action Over Text
   - Replayable Trust
   - Human Sovereignty
   - Relationship-Aware Behavior
   - Transport-Agnostic Execution

**核心转变**：从"档位/架构层" → "契约/实体/原则"的操作系统级抽象

---

## 三、开发计划的区别

### 第一版开发计划 (dev_plan_v0.md)
**团队配置**：5名工程师，6个月周期

| 角色 | 职责域 | 核心模块 |
|------|--------|----------|
| E1 | Thread Core | Thread Engine, Event Store, 数据层 |
| E2 | Policy & Control | Delegation Runtime, Approval Engine, Risk Engine, Kill Switch |
| E3 | Integration & Action | Channel Adapters, Ingress/Egress, Action Runtime, Outbox/Inbox |
| E4 | Control Surface | 全部前端界面 |
| E5 | AI/Agent Intelligence | Planner, Risk Classifier, Message Drafter |

**特点**：
- 非常详细的周次计划（24周，6个月）
- 大量的测试用例编号（TS-001, DP-001等）
- 完整的接口契约定义
- 强调质量要求（测试覆盖率、P99延迟等）

### 当前版本开发计划 (NEXT_PHASE_IMPLEMENTATION_BACKLOG.md)
**目标**：将当前demo变成连贯的Communication OS内核

**Phase结构**：
- **Phase 0**: Contract Freeze - 锁定产品和工程词汇表
- **Phase 1**: Product Kernel Foundations - 引入缺失的领域对象
- **Phase 2**: Persistence And Core API Unification - 用repository-backed运行时替换demo风格的可变状态
- **Phase 3**: Governance Merge - 让E1和E2成为一个逻辑运行时
- **Phase 4**: Core <-> E3 Integration - 用正式的action fabric契约替换ad hoc动作执行
- **Phase 5**: Operator Console Upgrade - 在UI中反映真实产品模型
- **Phase 6**: Hardening And End-to-End Validation - 证明内核是连贯的

**特点**：
- 更敏捷，4周时间框架
- 强调"契约冻结"作为第一步
- 聚焦于统一内核，而不是从头构建
- 明确的Definition Of Done
- P0/P1/P2优先级划分

**核心转变**：从"6个月大而全的计划" → "4周内核重构计划"，从"5人团队" → "整合现有代码库"

---

## 四、MVP范围的区别

### 第一版PRD (v0) MVP范围
| 模块 | MVP内容 |
|------|---------|
| Thread Kernel | 创建thread、目标、参与者、状态机、摘要、责任方 |
| Agent Drafting | 起草消息、建议下一步、生成候选时间/checklist |
| Approval & Takeover | 待审队列、原因解释、一键批准/拒绝/修改/接管 |
| Replay & Audit | 线程时间线、动作记录、策略命中、升级点 |
| Integration | Calendar + Email 最小集成 |
| Policy Runtime | 委托档位、关系模板、动作预算 |

**首发场景**：
1. 时间协调线程
2. 资料收集线程
3. 跟进催办线程

### 当前版本PRD (v1) MVP范围
**Must Have**:
- thread creation and state management
- participant and relationship objects
- delegation profiles
- approval inbox
- outbound message draft and send flow
- replay timeline
- external email/calendar execution for narrow scenarios

**Should Have**:
- sender stack UI
- explicit disclosure templates
- action planning
- kill switch controls
- relationship-specific policy presets

**v1 Narrow Scenarios**:
1. Interview Scheduling
2. Vendor or Customer Follow-up
3. Approval-Gated External Communication

**核心转变**：范围更聚焦，明确区分Must Have/Should Have/Later，强调"narrow scenarios"

---

## 五、核心价值观的演变

### 第一版PRD (v0) 的7个设计原则
1. 先做可委托，再做更智能
2. 先做thread control，再做social graph
3. 治理能力是主功能，不是后补功能
4. 默认保守，而不是默认自动化
5. 底层做宽，上线做窄
6. 优先解决责任边界，再追求表面丝滑
7. 把用户配置成本降到最低

### 当前版本PRD (v1) 的8大产品原则
1. **Identity First** - 始终先解决谁在说话、代表谁、披露什么
2. **Delegation Is Layered** - 委托不是二元的，支持多层级
3. **Thread Over Message** - 线程是核心对象，消息只是线程内的一种事件类型
4. **Action Over Text** - 建模draft、propose、clarify、commit、approve、escalate、execute、resolve
5. **Replayable Trust** - 每个重要动作都必须可追踪
6. **Human Sovereignty** - 人类保留批准权、撤销权、中断权
7. **Relationship-Aware Behavior** - 相同动作在不同关系中可能有不同接受度
8. **Transport-Agnostic Execution** - Email、calendar、messaging集成是执行通道，不是主要心智模型

**核心转变**：从"实用主义的7原则" → "操作系统级的8原则"，更强调身份、线程、动作、可重播信任等基础概念

---

## 六、世界假设的对比

### 第一版PRD (v0)
- 隐含假设：这是一个过渡性系统，需要从Email+Calendar切入
- 强调"不做熟人社交网络替代"
- 强调"放权路径必须分阶段上线"

### 当前版本PRD (v1)
明确提出3大世界假设：

**3.1 Multi-Actor Reality**
未来通信将涉及：
- human -> human
- human -> agent
- human -> agent -> human
- human -> agent -> agent -> human
- agent -> agent
- organization agent -> personal agent
- public service agent -> human

**3.2 Transport Is Not Truth**
WhatsApp、WeChat、email、SMS、Slack和calendar系统将继续存在，但它们成为传输边缘而不是真相系统。真相源移至：
- identity graph
- delegated authority
- relationship context
- thread state
- event log
- approval chain
- execution trace

**3.3 Human Attention Is the Scarce Resource**
未来的收件箱不是按时间排序的队列，而是一个责任过滤器。人类只应该因为以下事情被打断：
- approvals
- exceptions
- high-risk actions
- relationship-sensitive moments
- unresolved ambiguity
- moments that ethically require direct human presence

**核心转变**：从"实用主义的切入点选择" → "前瞻性的世界观和系统定位"

---

## 七、总结：核心区别总览

| 维度 | 第一版PRD (v0) | 当前版本PRD (v1) |
|------|-----------------|-------------------|
| **产品定位** | 代理原生通信控制层 | Communication OS（操作系统） |
| **核心概念** | Delegation Profile（5档位） | 5大契约 + 9大实体 + 8大原则 |
| **团队规模** | 5名工程师 | 整合现有代码库 |
| **时间周期** | 6个月（24周） | 4周内核重构 |
| **计划风格** | 详细的周次计划+测试用例 | Phase-based，强调契约冻结 |
| **世界观** | 隐含的，从Email+Calendar切入 | 明确的3大世界假设 |
| **范围** | 大而全的8层架构 | 聚焦内核统一 |
| **切入点** | Email+Calendar优先，内部仅demo | Thread-first，传输无关 |
| **核心价值** | "把高频沟通变成可委托执行的线程" | "Delegated communication can be more than automation. It can be a governed, legible, replayable system." |

---

## 八、从v0到v1的关键演进路径

1. **定位升级**：Control Layer → OS - 从"控制层/插件"升级为"操作系统"
2. **概念深化**：Delegation Profile → Contracts/Entities/Principles - 从实用抽象升级为操作系统级抽象
3. **计划收缩**：6个月大计划 → 4周内核重构 - 从"从头构建"转向"整合统一"
4. **视野扩展**：Email+Calendar切入 → Transport-agnostic - 从特定渠道转向传输无关
5. **世界观明确**：隐含假设 → 3大世界假设 - 从实用主义转向前瞻性系统设计

---

## 九、对当前代码库的影响

当前代码库（ad9d003 "Sprint 3 Complete"）已经反映了v1 PRD的核心思想：

✅ **已实现的v1概念**：
- `AuthorityGrant`, `SenderStack`, `DisclosurePolicy`, `AttentionDecision`, `ActionEnvelope` 契约已定义
- 完整的governance landing zones（governance, approvals, risk包）
- Repository实现（message, principal, relationship, event）
- E3 ActionEnvelope集成
- 前端关系和权限管理界面
- 完整的测试套件（166个测试通过）

这表明团队已经成功地从v0的"大计划"转向v1的"内核统一"方法，并在3个Sprint后交付了一个连贯的Communication OS内核。
