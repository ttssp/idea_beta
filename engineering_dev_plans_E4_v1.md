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

> 本文档随项目迭代持续更新。每个 Phase 结束时需评审进度并调整下阶段计划。
