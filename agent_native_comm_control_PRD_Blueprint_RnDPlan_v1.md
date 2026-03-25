# 代理原生通信控制层｜PRD + 技术 Blueprint + 研发计划（V1.1 修订稿）

> 文档用途：用于内部立项、研发启动、技术对齐与阶段评审。  
> 文档定位：在原始版本基础上，补强产品定义、架构闭环、风控链路与研发落地顺序。  
> 文档原则：**不把它定义成“更聪明的聊天工具”，而把它定义成“可委托、可审计、可接管的通信控制平面”。**

---

## 0. 本次修订的核心判断

原稿的大方向是对的，而且判断非常前瞻：真正值得做的，不是让 AI 帮用户“润色消息”，而是把一部分高频事务型沟通，第一次变成一件**可以安全委托**的事情。

但要把这个方向做成产品和工程，必须把几条隐含前提显式写出来，否则研发很容易中途滑向另外两条错误路径：

1. 滑向“聊天 App + AI 助手”。
2. 滑向“Agent 自动化平台 + 若干沟通插件”。

本项目应坚持第三条路：

**它的本体是通信控制层（Communication Control Plane），产品外形可以是 messenger-shaped，但系统内核必须是 thread-first、policy-first、human-takeover-first。**

本次修订主要补强了 8 个关键点：

1. **明确产品本体**：它不是新 IM，也不是外挂工具，而是覆盖多渠道沟通的控制平面。
2. **明确入口策略**：V1 不追求自建社交网络，优先从 **Email + Calendar** 切入，内部轻量消息入口仅用于 demo / dogfood。
3. **明确“委托契约”**：比起直接让用户配置复杂策略，更适合抽象出 `Delegation Profile`（委托档位 / 关系模板 / 动作预算）。
4. **明确身份披露**：系统必须清晰区分“谁写的、谁批准的、谁发出的、对方看到了什么披露”。
5. **明确状态与归因**：不仅 thread 有状态，action / approval / external wait 也必须有独立状态和幂等控制。
6. **明确风控链路**：风险判断不能只靠语义分类，要形成“关系 × 动作 × 内容 × 结果”的组合决策链。
7. **明确上线顺序**：必须先经历 observe → draft → approve → bounded auto 的放权阶梯，而不是一上来做自动代发。
8. **明确成功标准**：北极星指标要保留，但必须补充“错误自动化率、误升级率、节省触点数、可持续复用率”。

---

## 1. 执行摘要

本项目拟研发一套“代理原生通信控制层”（Agent-Native Communication Control Layer）。

它的产品外形可以接近 messenger，但其本质不是聊天软件，而是一个以 **thread** 为核心、支持在明确边界内将沟通动作委托给代理执行、并允许用户在任何关键节点随时接管的**通信操作系统**。

系统要解决的核心问题不是“消息写得更漂亮”，而是：

> **高频事务型沟通，如何在不破坏信任、不牺牲责任边界的前提下，被安全地交给代理先推进。**

第一阶段不做熟人社交网络替代，不追求迁移微信 / iMessage / WhatsApp 的强关系网络，而聚焦于一个更可落地、价值密度更高的切口：

- 工作型事务协调
- 时间安排与改期
- 资料催办与收集
- 跟进、提醒、确认
- 对服务方 / 候选人 / 外部协同者的低风险推进

项目的真正 wedge 不在“会聊天”，而在三件事：

1. **把沟通线程化**：用户看到的不是消息流，而是“一个目标正在如何被推进”。
2. **把放权产品化**：授权、审批、回放、熔断、接管不是后台能力，而是主产品。
3. **把治理做成内核**：系统天然支持“先保守、后放权、可解释、可追责”。

因此，首个版本的北极星指标不是消息量、DAU 或对话轮数，而是：

> **每位活跃用户每周被代理先推进的线程数。**

但为了避免该指标被“低价值自动线程”污染，还必须配套以下约束指标：

- bounded auto thread 占比
- 人工接管前平均节省触点数
- 严重越界率 / 错误自动发送率
- 线程闭环率与平均关闭时长
- 次周复用率（同一用户是否继续委托）

---

## 2. 产品定义与战略边界

### 2.1 产品定义

**产品定义**：一个 messenger-shaped、thread-first、policy-first 的代理通信控制平面。

更准确地说，它是：

- 面向多种沟通渠道的统一线程内核
- 面向委托执行的动作控制层
- 面向放权与收权的治理界面
- 面向结果闭环的沟通 → 执行桥梁

### 2.2 它是什么

它是：

- 沟通线程的控制平面
- 用户与代理共享执行权的工作界面
- 一套可审计、可接管的通信运行时
- 一种把“沟通”转化为“可被委托执行的操作”的系统

### 2.3 它不是什么

它不是：

- 新的熟人社交 IM
- 泛陪伴型聊天产品
- 无边界自动回复工具
- 通用 AutoGPT 风格的开放式代理系统
- 依赖单一渠道生态的插件能力

### 2.4 核心战略判断

这个项目的真正护城河，不会来自“某次消息生成特别聪明”，而会来自以下复合能力：

1. **线程级控制语义**：普通 messenger 以 message 为中心，本系统以 thread objective 为中心。
2. **委托与治理数据闭环**：谁可以代发什么、在哪些边界内可自动化，会形成高价值结构化数据资产。
3. **人机接力体验**：大多数系统只解决“AI 能不能做”，本系统解决“AI 做到哪一步人最安心”。
4. **跨渠道的统一执行模型**：未来可覆盖 email、calendar、task、vendor API，甚至 agent-to-agent，但产品价值不依赖某个单一通道。

一句话总结：

> **这是“人 + 代理”时代的通信控制基础设施，而不是聊天界面的一个 AI 增强插件。**

---

## 3. 用户、场景与 JTBD

### 3.1 第一阶段目标用户

第一阶段必须高度聚焦，优先选择“放权意愿高、事务沟通密度高、ROI 容易证明”的用户。

| 用户类型 | 典型特征 | 核心痛点 | 为什么适合首发 |
|---|---|---|---|
| 创始人 / 负责人 | 内外部多线程协调；时间稀缺 | 大量低价值沟通挤占高价值判断时间 | 放权意愿高，单用户价值高 |
| PM / 运营 / EA | 高频推进、催办、确认 | 状态分散、容易遗漏、重复触达多 | 天然符合 thread + follow-up 模型 |
| 招聘 / 候选人协调角色 | 约面、改期、确认、提醒频繁 | 每一步都要手工跟进 | 时间协调与审批场景清晰 |
| 高频服务采购 / 协同者 | 经常与商家、服务方确认细节 | 渠道碎片、跟进成本高 | 易验证沟通闭环价值 |

### 3.2 第一阶段首发场景

首发只做高频、低风险、动作边界清晰的事务型沟通，不碰强情绪、强博弈、强承诺场景。

建议第一阶段聚焦三条标准线程：

1. **时间协调线程**：约时间、改期、确认、提醒、回写日历。
2. **资料收集线程**：向外部索取材料、确认缺项、催办补齐。
3. **跟进催办线程**：按目标和 SLA 做 follow-up、状态确认和升级。

### 3.3 用户 JTBD

用户真正要“买”的不是一个聊天框，而是以下工作结果：

1. 帮我先处理那些**目标明确、动作标准、风险较低**的沟通。
2. 当线程进入**承诺、支付、冲突、敏感表达**等节点时，立刻把控制权交还给我。
3. 让我在一个地方看到：**发生了什么、卡在哪里、下一步是谁的责任**。
4. 让我逐步增加对系统的信任，而不是一上来要求我“全自动”。

### 3.4 非目标（Out of Scope）

第一阶段明确不做：

- 强关系社交替代
- 陪伴型聊天 / 人设驱动产品
- 自动谈判、自动承诺、自动支付
- 合同、法务、价格博弈类高风险线程
- 覆盖所有渠道、行业与能力包
- “万物皆可交给代理”的无边界自动化

---

## 4. 核心产品主张与设计原则

### 4.1 产品主张

本系统的价值主张可以浓缩为一句话：

> **把“高频沟通”变成“可委托执行的线程”。**

用户不是在使用一套消息系统，而是在使用一套“委托推进系统”。

### 4.2 设计原则

1. **先做可委托，再做更智能**  
   没有放权和收权机制，再聪明的生成能力都不构成产品价值。

2. **先做 thread control，再做 social graph**  
   先把线程推进做好，再考虑关系链迁移。

3. **治理能力是主功能，不是后补功能**  
   approval、replay、kill switch 必须进入首页级体验。

4. **默认保守，而不是默认自动化**  
   先建立信任，再扩大自动化边界。

5. **底层做宽，上线做窄**  
   架构要通用，首发要极度克制。

6. **优先解决责任边界，再追求表面丝滑**  
   “能解释清楚”比“看起来像真人”更重要。

7. **把用户配置成本降到最低**  
   V1 不应该把策略引擎裸露给用户，而应以“委托档位 + 场景模板”表达。

### 4.3 一个关键优化：从 Policy Center 到 Delegation Profile

原稿里 `Policy Center` 的方向没问题，但直接让用户面对关系级、线程级、动作级策略配置，学习成本过高，也会拖慢 adoption。

建议产品层使用更易理解的抽象：

#### Delegation Profile（委托档位）

每个线程或关系默认挂一个委托档位：

- **Observe Only**：只观察与建议，不起草不发送。
- **Draft First**：自动起草，但所有消息需人工确认。
- **Approve to Send**：低风险动作自动准备，用户一键审批后发出。
- **Bounded Auto**：在明确预算和动作边界内自动执行。
- **Human Only**：该类关系或场景禁止代理主动介入。

对用户暴露的是“委托档位”和“关系模板”；
对系统内部保留完整的 Policy Engine 做细粒度决策。

这个改动很重要，因为它直接决定产品能不能被普通高价值用户快速理解和采用。

---

## 5. MVP 范围与入口策略

### 5.1 MVP 最小闭环

第一版必须围绕以下闭环设计：

> 创建 thread → 系统理解目标 → 代理起草 / 准备动作 → 低风险动作审批或执行 → 等待外部回复 → 继续推进 → 关键节点升级给人 → 线程完成 → 全程可回放

### 5.2 首发能力边界

| 模块 | MVP 内容 | 为什么必须做 | 暂不做 |
|---|---|---|---|
| Thread Kernel | 创建 thread、目标、参与者、状态机、摘要、责任方 | 没有 thread 就没有“控制层” | 群社区、社交图谱 |
| Agent Drafting | 起草消息、建议下一步、生成候选时间 / checklist | 让系统真正开始“推进线程” | 高风险复杂谈判 |
| Approval & Takeover | 待审队列、原因解释、一键批准/拒绝/修改/接管 | 建立放权心智 | 多级审批编排 |
| Replay & Audit | 线程时间线、动作记录、策略命中、升级点 | 建立信任与复盘能力 | 企业级合规套件 |
| Integration | Calendar + Email 最小集成 | 形成真实闭环 | 多渠道同时铺开 |
| Policy Runtime | 委托档位、关系模板、动作预算 | 放权必须产品化 | 高自由度策略 DSL |

### 5.3 入口策略：先做 Email + Calendar，而不是“内部聊天”

这是原稿最值得补强的一点。

如果一开始做一个完整内部消息入口，团队很容易不自觉滑向“自建聊天应用”。这会稀释真正的 wedge。

建议：

- **对外生产入口：Email + Calendar**
- **对内验证入口：轻量 sandbox / internal message lane（仅供 demo 与 dogfood）**

原因：

1. 邮件天然承载大量事务型沟通。
2. 日历是时间协调最关键的结果系统。
3. 两者都具备明确 API 和结构化闭环。
4. 足以验证“代理先推进线程”的核心价值。
5. 能在不迁移社交关系链的情况下验证 PMF。

### 5.4 放权路径：必须分阶段上线

V1 不能直接让用户进入自动代发模式，而应该采用四段式放权阶梯：

1. **Observe**：系统只理解线程、生成建议、不触达外部。
2. **Draft**：系统起草消息与动作，用户人工确认。
3. **Approve**：系统主动推进，关键动作进入待审队列。
4. **Bounded Auto**：在预设预算、关系和动作边界内自动执行。

这不仅是体验设计，更是产品成败的关键机制。

---

## 6. 关键用户流程

### 6.1 标准线程流程

1. 用户创建一个 thread，并定义目标，例如“协调终面时间”。
2. 系统识别参与者、关系类别、可用渠道与推荐委托档位。
3. 系统生成初始行动计划，例如：
   - 提出候选时间
   - 起草邮件
   - 等待回复
   - 超时 follow-up
4. 若动作处于低风险且在边界内，系统自动进入 draft / approval / bounded execution 流程。
5. 外部回复到达后，系统更新 thread 摘要、状态与下一责任方。
6. 若检测到承诺、冲突、目标漂移、预算越界或不确定性升高，系统立刻升级给人。
7. 用户批准、修改或接管后，系统继续推进，直至线程完成。

### 6.2 接管点（必须产品化，不可隐含）

以下情况必须触发人工介入：

- 涉及金钱、支付、报价、折扣、补偿
- 涉及合同、法律承诺、时间承诺升级
- 涉及敏感关系（家人、核心客户、首次重要联系人）
- 涉及强情绪、拒绝、投诉、终止、责备、争议
- 线程目标出现漂移或歧义
- 需要读取或发送高敏感隐私内容
- 动作超出预算 / 档位 / 策略边界
- 系统无法高置信度判断下一步动作

### 6.3 页面与信息架构

#### 1）Thread Inbox
不是消息列表，而是“工作队列”。

必须回答：

- 哪些线程正在被代理推进？
- 哪些线程在等我审批？
- 哪些线程已卡住或异常？
- 哪些线程值得我现在优先接管？

建议按以下 bucket 组织：

- Needs Approval
- Agent Running
- Awaiting External
- Blocked / At Risk
- Completed

#### 2）Thread Detail
必须围绕“目标推进”而不是“消息时间线”组织。

必须展示：

- thread 目标
- 当前状态
- 当前责任方
- 下一步动作
- 历史消息与动作
- 风险解释
- 授权档位
- 最近一次升级 / 接管原因

#### 3）Approval Center
不是简单的待办列表，而是用户与代理的“共享控制界面”。

每个待审项必须清楚展示：

- 为什么需要你审批
- 代理准备做什么
- 对外会看到什么内容
- 这一步触发了哪条规则 / 风险原因
- 批准后会改变什么状态

#### 4）Replay Center
这是系统信任的基础设施，不是 debug 页面。

必须支持查看：

- 消息发生了什么
- 系统判断了什么
- 命中了什么策略
- 为什么自动做 / 没自动做
- 人在何处接管
- 最终结果如何形成

#### 5）Delegation / Policy Surface
V1 产品表层建议弱化“策略中心”概念，改为：

- 关系模板
- 场景模板
- 委托档位
- 动作预算
- Kill Switch

高级策略可保留在后台管理端，不必一开始完全暴露给普通用户。

---

## 7. 指标体系与成功标准

### 7.1 北极星指标

> **每位活跃用户每周被代理先推进的线程数**

这个指标保留，因为它最能体现用户是否真的愿意放权。

### 7.2 但必须配套四类约束指标

#### 使用层

- 活跃线程数
- 每周新建线程数
- 周复用率
- 首次委托成功率

#### 信任层

- 委托档位启用率（Draft / Approve / Bounded Auto）
- 审批通过率
- 人工接管率
- Kill Switch 使用率
- 次周继续放权率

#### 闭环层

- 线程闭环率
- 平均关闭时长
- 平均节省触点数（saved touches per thread）
- 平均节省人工操作分钟数

#### 安全层

- 严重越界率
- 错误自动发送率（per 10k actions）
- 高风险漏拦截率
- 误升级率（false escalation）
- 外部集成失败污染 thread 的比例

### 7.3 分阶段 Go / No-Go 标准

#### MVP 阶段

- 至少 3 类标准线程形成完整闭环
- 无 P0 越界事故
- 内部 dogfood 用户愿意持续使用 approve 模式

#### Beta 阶段

- 10–20 位种子用户形成周复用
- bounded auto 在特定场景下开始成立
- replay 能显著降低“我不敢放权”的心理阻力

#### V1 阶段

- 至少一类线程成为用户的默认委托行为
- 错误自动发送率控制在极低水平
- 线程闭环率与节省触点数达到可对外讲述的水平

---

## 8. 技术 Blueprint

## 8.1 技术设计目标

技术架构必须服务于以下五个核心目标：

1. **以 thread 为系统一等公民**，而不是把消息拼接成线程。
2. **天然支持审计与回放**，而不是事后补日志。
3. **把放权与收权做成运行时语义**，而不是 UI 层补丁。
4. **优先支持结构化执行与幂等控制**，而不是以 prompt 驱动一切。
5. **支持未来扩展到 agent-to-agent / 多工具协议**，但系统价值不依赖任何单一协议。

### 8.2 架构总原则

- Thread-first
- Event-driven
- Policy-first
- Human-takeover-first
- API-first, computer-use-last
- Explicit identity and disclosure
- Deterministic execution around nondeterministic reasoning

这最后一点非常关键：

> **LLM 可以参与判断与起草，但真正的执行、状态变更、审批、发送、回放，必须落在可确定、可追踪的系统边界内。**

### 8.3 逻辑架构

建议架构分为 8 层：

1. **Channel Adapters**  
   Email、Calendar、Task、Doc、外部服务 API、内部 sandbox。

2. **Ingress / Egress Gateway**  
   负责收发消息、webhook、去重、映射、重试、签名校验。

3. **Thread Engine**  
   管理 thread 对象、状态机、责任方、摘要、目标推进。

4. **Delegation & Policy Runtime**  
   负责关系模板、委托档位、动作预算、审批规则、例外覆盖。

5. **Planning / Risk / Decision Layer**  
   负责下一步建议、风险分层、是否升级、是否进入审批。

6. **Action Runtime**  
   负责 draft、send、schedule、follow-up、collect-info 等执行动作。

7. **Audit / Replay / Analytics**  
   负责事件流、回放、指标、异常聚类。

8. **Control Surface**  
   Inbox、Thread Detail、Approval、Replay、Delegation、Ops Console。

### 8.4 核心模块说明

| 模块 | 职责 | 关键设计点 |
|---|---|---|
| Thread Engine | 管理线程对象、目标、状态机、责任方、摘要 | thread 是系统一等公民；message 只是 thread 内事件 |
| Identity & Principal | 统一我、代理、外部方、服务方身份 | 必须明确“谁在说话、谁批准、谁执行” |
| Relationship Graph | 表达用户与联系人之间的关系语义 | 放权应默认绑定到关系类型，而不是抽象全局开关 |
| Delegation Runtime | 管理委托档位、预算、策略命中、覆盖规则 | 对用户简单，对系统细粒度 |
| Approval Engine | 管理人工确认、修改、拒绝、接管 | 是人机控制权切换中心 |
| Risk Engine | 判断敏感语义、越界、目标漂移、置信不足 | 默认保守，宁可升级给人 |
| Action Runtime | 执行起草、代发、改期、提醒、收集、回写等动作 | 每个动作必须可重试、可中止、可追踪 |
| Channel Adapters | 对接 Email / Calendar / Task / External APIs | 统一外部线程映射、去重与签名校验 |
| Audit & Replay | 保存事件流、构建回放与解释视图 | append-only event log，天然可解释 |
| Analytics & Ops | 指标、异常聚类、风险热图、策略命中分析 | 为迭代委托边界提供数据基础 |

---

## 9. 对象模型与状态设计

### 9.1 一个重要补强：不仅 Thread 有状态，Action 也必须有状态

原稿中 thread 状态机是正确方向，但如果只有 thread 状态，没有 action / approval / external-wait 的独立状态，工程上会很快出现归因混乱、重复发送和恢复困难的问题。

因此建议采用四层状态体系：

1. **Thread State**：线程整体推进状态
2. **ActionRun State**：每个动作执行状态
3. **Approval State**：审批对象状态
4. **External Delivery State**：外部发送 / 回执 / webhook 状态

### 9.2 关键对象模型

| 对象 | 作用 | 关键字段 | 说明 |
|---|---|---|---|
| Thread | 事务容器 | title / objective / status / owner / delegation_profile / risk_level | 系统一等公民 |
| Principal | 主体对象 | principal_type / display_name / trust_tier / disclosure_mode | 统一“人 / 代理 / 外部方 / 服务方” |
| Relationship | 关系语义 | relationship_class / sensitivity / default_profile | 表达“我如何看待这个对象” |
| Message | 消息对象 | channel / authored_mode / sender_principal / approval_ref / disclosure_payload | 解决“谁写、谁批、谁发、对方看到什么” |
| ActionRun | 动作执行记录 | action_type / status / idempotency_key / input / output / risk_decision | 执行层核心对象 |
| ApprovalRequest | 待审请求 | request_type / reason_code / preview / resolution / approver | 放权与收权的关键纽带 |
| PolicyRule | 细粒度策略 | scope / action / effect / conditions / priority | 系统内部规则层 |
| DelegationProfile | 用户可理解的委托档位 | profile_name / allowed_actions / budget / escalation_rules | 产品层主抽象 |
| ThreadEvent | 事件流 | event_type / actor / payload / occurred_at / causal_ref | 用于回放与解释 |
| ExternalBinding | 外部渠道映射 | channel / external_thread_key / external_message_key / sync_state | 解决线程关联与去重 |

### 9.3 建议的 Thread 状态机

- `new`：线程新建，待初始化
- `planning`：系统正在评估目标与生成初始动作计划
- `active`：线程处于正常推进中
- `awaiting_external`：等待外部方回复
- `awaiting_approval`：存在待人工审批动作
- `blocked`：缺少信息、外部失败或规则冲突
- `paused`：用户主动暂停
- `escalated`：已升级到人工主导
- `completed`：目标达成，线程关闭
- `cancelled`：用户主动终止或失去继续推进价值

### 9.4 ActionRun 状态机

- `created`
- `planned`
- `ready_for_approval`
- `approved`
- `executing`
- `sent`
- `acknowledged`
- `failed_retryable`
- `failed_terminal`
- `cancelled`

这个状态机是保障幂等、重试和回放完整性的关键。

### 9.5 建议的数据持久化模型

采用：

> **关系型当前态 + append-only event log + outbox/inbox 消息表**

推荐：

- **Postgres**：当前态、业务对象、查询视图、审批数据
- **Event Log**：完整状态变化、系统判断、动作轨迹
- **Outbox Pattern**：外发动作统一排队与幂等发送
- **Inbox / Webhook Event Store**：接收外部回复、回执与去重

原因：

1. 当前态适合产品查询与前台展示。
2. 事件流适合回放、解释和复盘。
3. outbox / inbox 能显著降低重复执行与外部不一致问题。

---

## 10. 决策链、风险控制与身份披露

### 10.1 风险判断不能只做“语义分类”

原稿中的 risk engine 提法正确，但如果只做“检测钱 / 冲突 / 敏感关系”，实际会不够稳。

建议把风控决策拆成四层：

1. **Relationship Risk**：这是对谁说话？
2. **Action Risk**：准备做什么动作？
3. **Content Risk**：这段内容是否涉及承诺 / 冲突 / 隐私 / 不确定性？
4. **Consequence Risk**：如果发出后出错，代价有多高？

最终由一个合成决策器输出：

- allow
- draft_only
- require_approval
- bounded_execution
- escalate_to_human
- deny

### 10.2 推荐决策链

每次动作执行前，都走以下流程：

1. 读取 thread objective 与当前状态
2. 读取 relationship class 与 delegation profile
3. 生成候选动作
4. 进行规则命中与预算检查
5. 进行内容 / 语义风险评估
6. 进行结果代价评估
7. 决定：自动执行、进入审批、升级人工或拒绝
8. 记录完整 decision trace 进入 replay

### 10.3 身份披露要求（必须写进产品定义）

任何对外动作都必须显式区分以下 authored / sent 模式：

- `human_authored_human_sent`
- `agent_drafted_human_sent`
- `agent_drafted_human_approved_sent`
- `agent_sent_within_policy`

并且系统必须支持披露策略，例如：

- 完全显式披露：由代理代为协调
- 半显式披露：代表某用户进行安排 / 跟进
- 企业模板披露：由团队助理系统发送

**原则**：披露方式可以因场景不同而不同，但不能让系统内部都分不清到底是谁在承担责任。

### 10.4 一键熔断与接管

必须支持三层 kill switch：

- **Global Kill Switch**：全局停机
- **Profile Kill Switch**：某类关系 / 某类动作停机
- **Thread Kill Switch**：单线程停机与接管

且在接管发生后：

- 所有未执行自动动作立即冻结
- 待审项自动失效或重算
- 后续动作默认转为 human-led 模式

---

## 11. 集成与执行运行时

### 11.1 API-first，computer-use-last

这个原则必须保留，而且要更明确：

- 只要有结构化 API，就不要用 GUI 自动化
- 只要能在系统内做确定性状态变更，就不要把关键执行依赖在浏览器操作上
- GUI / computer use 只作为无 API 场景的后备执行面，而且必须运行在隔离沙箱里

### 11.2 V1 集成优先级

| 集成对象 | 优先级 | 作用 | 原因 |
|---|---|---|---|
| Calendar | P0 | 候选时间生成、冲突判断、确认回写 | 时间协调最有代表性 |
| Email | P0 | 对外沟通入口、回复收集、线程承载 | 事务型沟通覆盖最广 |
| Task / Doc | P1 | 将 thread 沉淀为可执行结果 | 沟通闭环后的价值延伸 |
| External Service APIs | P1 / P2 | 服务方状态同步、流程推进 | 随真实机会逐步扩展 |
| GUI Automation | P2 | 填补极少数无 API 场景 | 不可作为主路径 |

### 11.3 Channel Adapter 的关键职责

每个 adapter 至少要解决以下问题：

- 外部 thread / message 唯一标识映射
- webhook / polling 去重
- 外部发送幂等
- 回执与失败归因
- 权限 / token 管理
- 外部异常不污染内部 thread 状态

### 11.4 一个容易被忽略但非常关键的问题：线程关联

如果没有统一的 `ExternalBinding` 模型，系统很容易出现：

- 同一封邮件被识别成多个 thread
- 一个外部回复找不到正确 thread
- 重发动作与历史动作混淆

因此必须在技术方案里明确：

- 内部 thread id 永远独立存在
- 外部 thread key / message key 仅作为绑定对象
- 所有外部事件先进入 ingress，再由 resolver 映射到内部 thread

---

## 12. API 草图（修订版）

### 12.1 Thread 与 Planning

- `POST /threads`  
  创建 thread，输入 objective、participants、initial_context、suggested_profile

- `POST /threads/{id}/plan`  
  生成下一步建议与动作候选

- `POST /threads/{id}/pause`
- `POST /threads/{id}/resume`
- `POST /threads/{id}/takeover`

### 12.2 Message 与 Action

- `POST /threads/{id}/messages:draft`
- `POST /threads/{id}/messages:send`
- `POST /threads/{id}/actions:prepare`
- `POST /threads/{id}/actions:execute`
- `POST /threads/{id}/actions/{action_id}:cancel`

### 12.3 Approval 与 Delegation

- `POST /approvals/{id}:resolve`
- `POST /threads/{id}/delegation-profile`
- `POST /relationships/{id}/delegation-profile`
- `POST /kill-switches`

### 12.4 Replay 与 Analytics

- `GET /threads/{id}/replay`
- `GET /threads/{id}/decision-trace`
- `GET /metrics/threads`
- `GET /metrics/risk`

### 12.5 Channel Webhooks

- `POST /ingress/email`
- `POST /ingress/calendar`
- `POST /delivery/status`

建议 API 设计中显式区分：

- 规划（plan）
- 准备（prepare）
- 审批（approve）
- 执行（execute）
- 接管（takeover）

这样可以显著降低“LLM 推理阶段”和“系统执行阶段”纠缠不清的问题。

---

## 13. 研发计划

## 13.1 研发目标

首轮研发周期建议仍按 6 个月规划，但要更强调**“信任闭环优先于能力扩张”**。

阶段原则：

> 先定义线程内核与接管机制，再验证低风险线程闭环，再扩关系模板与动作包，最后扩集成与自动化深度。

### 13.2 分阶段目标

| 阶段 | 周期 | 核心目标 | 关键交付 | Go / No-Go 标准 |
|---|---|---|---|---|
| Phase 0 | 第 0–2 周 | 冻结产品定义、对象模型、状态机、委托模型 | PRD、state machine、schema、3 条 demo thread、delegation model | 团队对“通信控制层而非聊天 app”达成一致 |
| Phase 1 | 第 3–8 周 | 跑通 MVP 闭环（observe / draft / approve） | thread kernel、approval、replay、email + calendar 最小集成 | 3 类线程可跑通；无严重越界 |
| Phase 2 | 第 9–16 周 | 扩展关系模板、能力包、指标与 bounded auto 试点 | relationship-based profiles、follow-up pack、doc/task 之一、metrics | 10–20 位种子用户稳定复用 |
| Phase 3 | 第 17–24 周 | Beta 稳定化、风险治理、运维后台、立项复盘 | 异常聚类、风险热图、ops console、PMF 评估 | 至少一类线程形成默认委托习惯 |

### 13.3 比原稿更稳的一点：把“Shadow Mode”单独设为 Phase 1 关键里程碑

建议把 Phase 1 再拆成两个子阶段：

#### Phase 1A：Shadow / Observe

- 系统只理解线程、生成建议、做风险判断
- 不触达外部
- 打磨状态机、摘要、下一步推荐、replay

#### Phase 1B：Approve / Execute

- 在低风险范围内允许 draft 与 approval
- 部分动作可进入 bounded execution
- 开始验证真实放权

这是必要的，因为：

1. 可以先验证 thread value，而不是一上来承担发送风险。
2. 有利于积累 risk engine 与 replay 训练数据。
3. 能显著降低早期 dogfood 心理阻力。

---

## 14. 团队配置建议

| 职能 | 建议人数 | 第一阶段职责 | 说明 |
|---|---|---|---|
| 产品 | 1–2 | PRD、场景收敛、委托模型、审批体验、用户访谈 | 必须强控边界 |
| 后端 / 平台 | 2–3 | thread engine、event store、delegation runtime、API、outbox/inbox | MVP 最关键投入 |
| 前端 / 应用 | 2 | Inbox、Thread Detail、Approval、Replay、Ops Surface | UI 必须是“控制界面”而非聊天界面 |
| Agent / AI | 1–2 | planner、risk classifier、message drafting、pack logic | 不要单独造“万能智能体”团队 |
| Infra / Security | 0.5–1 | 审计、权限、部署、可观测性、token 安全 | 早期可由平台兼任 |
| Design / Research | 0.5–1 | 信息架构、线程界面、信任感设计、种子用户研究 | 决定 adoption 速度 |

### 14.1 新增建议：设立一个“运营型 PM / Dogfood Owner”角色

这个角色可以由产品或设计兼任，但职责必须明确：

- 跟踪失败线程
- 记录用户不敢放权的真实原因
- 整理 replay 与异常案例
- 驱动规则热修和策略迭代

因为这个产品早期的核心，不是模型 benchmark，而是“信任建立速度”。

---

## 15. 详细里程碑

### 15.1 Phase 0：定义与冻结（第 0–2 周）

必须冻结以下内容：

- 产品定义：通信控制层，而非聊天 App
- 首发场景：时间协调 / 资料收集 / 跟进催办
- 对象模型：Thread / Principal / Relationship / DelegationProfile / ActionRun / Approval / ThreadEvent / ExternalBinding
- 状态机：thread + action + approval
- UI 骨架：Inbox / Thread Detail / Approval / Replay / Delegation
- 技术基线：Postgres + event log + outbox/inbox + service API

**交付物**：

- PRD V1.1
- ER / schema 草图
- 状态机图
- 3 条标准线程 demo script
- 决策链说明（allow / approval / escalate）

### 15.2 Phase 1：MVP 闭环（第 3–8 周）

必须完成：

- thread 创建、摘要、状态流转
- observe / draft / approval 三种运行模式
- email + calendar 最小集成
- 基础 replay
- 基础 risk engine（规则优先 + 小模型辅助）
- 委托档位与关系模板最小实现
- 5–8 位内部用户 dogfood

**验收标准**：

- 3 类标准 thread 可从创建走到关闭
- 外部事件可正确回到原 thread
- 无重复发送 / 无不可解释动作
- 审批与接管机制可用

### 15.3 Phase 2：Beta 扩张（第 9–16 周）

新增：

- follow-up pack
- info collection pack
- bounded auto 在窄场景试点
- relationship-based defaults
- task / doc 其一集成
- metrics dashboard
- 10–20 位高意愿种子用户

**验收标准**：

- 至少一类线程形成可重复使用习惯
- bounded auto 在线程中占有真实比例
- replay 能有效支持异常分析与用户解释

### 15.4 Phase 3：稳定化与 PMF 复盘（第 17–24 周）

新增：

- 风险热图
- 失败线程聚类
- 管理后台 / Ops Console
- 更细粒度的 replay 解释
- kill switch 与 profile override 完整实现
- PMF 复盘与 V1 扩张建议

**最终交付**：

- PMF 评估文档
- 越界事故复盘库
- 推荐扩展渠道 / 行业 / 能力包路线图

---

## 16. 测试、质量与上线治理

### 16.1 质量建设的核心原则

这个项目不是“模型答得像不像人”，而是“用户敢不敢把一段沟通交给系统”。

因此测试体系必须围绕**可放心放权**展开。

### 16.2 测试维度

| 测试维度 | 要测什么 | 验收标准 | 说明 |
|---|---|---|---|
| 流程测试 | thread / action / approval 状态流转 | 无死锁、无脏状态、可恢复 | 状态机是系统主骨架 |
| 权限测试 | 关系 / 线程 / 动作三级策略命中 | 越界动作必被拦或升级 | 覆盖不同委托档位 |
| 消息测试 | authored_mode / disclosure / approval trace | 所有外发都可追溯 | 直接影响信任 |
| 风险测试 | 高风险语义与高代价动作降级 | 宁可保守，不可漏拦 | recall 优先于 precision |
| 幂等测试 | 重试、重复 webhook、网络抖动 | 不重复发送、不重复推进 | 是生产可用性的关键 |
| 集成测试 | email / calendar / doc / task 接口稳定性 | 外部故障不污染内核 | adapter 必须隔离失败 |
| 回放测试 | 决策路径和关键动作是否可解释 | thread timeline 可读、可复盘 | replay 是主产品能力 |
| 人工接管测试 | takeover 后系统行为是否收敛 | 自动化立即停止或重算 | 不能与人工抢控制权 |

### 16.3 上线治理建议

任何自动发送能力上线前，必须经过：

1. Shadow mode 数据积累
2. 规则红队与高风险样本测试
3. 人工审批模式稳定运行
4. 极窄边界下的 bounded auto 试点
5. 可一键停机的运维预案

---

## 17. 核心风险与应对

| 风险 | 级别 | 具体表现 | 缓解策略 |
|---|---|---|---|
| 产品定义漂移 | 高 | 团队滑向“聊天 App + AI” | 所有评审都回到北极星：可委托线程数 |
| 放权过深 | 高 | 过早开放自动代发与复杂执行 | observe → draft → approve → bounded auto 分阶段放权 |
| 场景过宽 | 高 | 线程类型膨胀，研发失控 | 首发只做 3 条标准线程 |
| 策略复杂度过高 | 中高 | 用户不会配、团队难维护 | 对用户暴露 Delegation Profile，对系统保留细粒度 Policy |
| 集成过重 | 中 | 为多平台适配拖垮核心体验 | V1 只打通 Email + Calendar |
| 用户不敢放权 | 高 | 始终停留在 suggest_only / draft_only | 强化 replay、审批体验和接管可控性 |
| 外部归因错误 | 高 | 回复回错 thread、重复发送、状态混乱 | ExternalBinding + inbox/outbox + idempotency key |
| 长尾异常过多 | 中高 | 边缘线程大量失效 | 失败线程聚类 + 快速规则热修 |
| 模型“看起来能做”，系统“实际上不稳” | 高 | demo 很强，生产频繁翻车 | 严格把执行层做成确定性系统 |

---

## 18. 经营与立项建议

从经营角度，第一轮研发的成功标准绝不是“大而全”，而是建立一个足够强的 wedge：

> **让用户第一次在某类高频沟通里，形成“默认先让代理推进”的习惯。**

只要这个习惯建立起来，系统才有资格从“事务沟通控制层”扩展到更广义的“人机协同操作系统”。

因此经营与立项上建议坚持四条铁律：

1. **先赢一个高频 thread，不要先赢整个通信市场。**
2. **先建立信任，不要先堆自动化能力。**
3. **先把 replay / approval / takeover 做成主产品，再谈更强智能。**
4. **先用 10–20 位高价值用户证明可委托闭环，再决定是否扩渠道、扩行业、扩能力包。**

---

## 19. 已冻结决策与待解问题

### 19.1 建议冻结的决策

- 产品本体是“代理原生通信控制层”，不是新社交 IM
- 首发场景聚焦工作型事务协调
- 首发入口优先 Email + Calendar
- 底层采用通用 thread kernel，不按场景重造烟囱
- 治理能力（授权、审批、回放、熔断）是主产品能力
- 采用 Postgres + append-only event log + outbox/inbox 的混合持久化策略
- 用户侧以 Delegation Profile 为主抽象，不直接暴露复杂策略 DSL

### 19.2 待解问题

1. V1 的内部 sandbox 消息入口做多轻？  
   建议：只用于 demo / dogfood，不做产品主入口。

2. risk engine 初版采用什么范式？  
   建议：**规则优先，小模型辅助，决策合成可解释。**

3. relationship class 的最小集合如何定义？  
   建议从极简集合开始，例如：内部协作 / 外部候选人 / 客户 / 服务方 / 敏感个人联系人。

4. bounded auto 的预算如何表达？  
   建议从“动作类型 + 对象范围 + 时间窗口 + 最大连续触达次数”四元组开始。

5. 何时开放 agent-to-agent 或外部代理协议？  
   建议：在单代理闭环稳定后再做，不纳入 V1 关键路径。

---

## 20. 最终结论

这份方案最有价值的地方，在于它抓住了一个真正属于“人机共存社会”的基础命题：

> **未来真正重要的，不只是 AI 会不会说话，而是人类是否拥有一套能够安全委托、随时收权、完整回放的通信控制机制。**

如果继续按这个方向推进，我的判断是：

- **产品方向正确，而且足够前瞻；**
- **真正需要补强的不是“想法”，而是“从 idea 到系统闭环的严密性”；**
- **只要把入口收窄、放权分级、状态归因、风险决策链和 replay 主产品化这几件事做扎实，这个项目有机会从一个功能型产品，成长为下一代 agent-native 基础设施。**

一句话收束：

> **不要把它做成会聊天的工具。要把它做成人与代理共享执行权的通信操作系统。**

