# Sprint 1 详细执行计划

**Duration**: 5-7 天
**Status**: 📋 Ready to Start
**Phase 0 Status**: ✅ COMPLETE - Contracts Frozen

---

## 概述

Sprint 1 的目标是在合同冻结的基础上，并行推进 5 个工程工作流，最终构建出 Communication OS 的核心内核。

### 前提条件 ✅

- [x] Phase 0 合同冻结完成
- [x] 所有合同文档已交付
- [x] 写作用域已锁定
- [x] JSON fixtures 已生成
- [x] TypeScript 类型已创建
- [x] 27 个测试全部通过

---

## 合并顺序

根据 PARALLEL_ENGINEERING_PLANS.md 第 7 章：

1. ✅ Engineer 1 contracts (已完成)
2. Engineer 3 governance landing zones
3. Engineer 2 repositories and API migration
4. Engineer 4 E3 action contract changes
5. Engineer 5 frontend integration
6. Optional Engineer 6 E5 integration
7. Lead final integration

**Reason**:
- contracts first
- core semantics next
- persistence before UI wiring
- execution fabric before end-to-end replay

---

## 每日同步节奏

### 每日站会 (15分钟)

**时间**: 每日上午 10:00
**参与者**: 所有工程师 + Lead
**议程**:
- 昨天完成了什么
- 今天计划做什么
- 有什么阻塞
- 需要 Lead 协调什么

### 按工程师一对一 (15-30分钟)

**时间**: 根据需要预约
**参与者**: Lead + 单个工程师
**目的**: 深入讨论技术问题、设计决策、阻塞解决

### 集成检查点 (每周 2/4/5)

**时间**: 周二、周四、周五下午
**参与者**: 所有工程师
**目的**:
- 展示阶段性成果
- 识别集成风险
- 调整优先级

---

## Engineer 2: Core Persistence And API Engineer

### 目标

移除演示风格的可变 API 状态，为非线程路由系列建立仓储支持的流程。

### 每日分解

#### Day 1: Repository 接口设计与实现

**上午**:
- [ ] 创建 `MessageRepository` 接口和实现
  - 位置: `src/myproj/core/repositories/message_repository.py`
  - 继承 `BaseRepository`
  - 实现 `_to_entity()` / `_to_model()` 映射
  - 添加查询方法: `get_by_thread()`, `get_drafts()`, `get_sent()`
- [ ] 创建 `PrincipalRepository` 接口和实现
  - 位置: `src/myproj/core/repositories/principal_repository.py`
  - 添加查询方法: `get_by_email()`, `get_by_type()`, `get_trusted()`

**下午**:
- [ ] 创建 `RelationshipRepository` 接口和实现
  - 位置: `src/myproj/core/repositories/relationship_repository.py`
  - 添加查询方法: `get_by_principal()`, `get_by_class()`, `get_sensitive()`
- [ ] 创建 `EventRepository` 接口和实现
  - 位置: `src/myproj/core/repositories/event_repository.py`
  - 添加查询方法: `get_by_thread()`, `get_by_type()`, `get_replay_chain()`
- [ ] 更新 `src/myproj/core/repositories/__init__.py` 导出

**验收**:
- 所有 Repository 实现继承 BaseRepository
- 所有查询方法有类型注解
- 单元测试覆盖基本 CRUD

#### Day 2: 数据库模型映射与扩展

**上午**:
- [ ] 审查/扩展 `src/myproj/infra/db/models.py`
  - [ ] 确保 Message 模型完整
  - [ ] 确保 Principal 模型完整
  - [ ] 确保 Relationship 模型完整
  - [ ] 确保 Event 模型支持新的 contract 字段
  - **注意**: 此文件需 Lead 审核
- [ ] 创建 DB 模型 ↔ Domain 实体映射层
  - 位置: `src/myproj/infra/db/mappings.py`
  - 为每个实体创建双向映射函数

**下午**:
- [ ] 为 Message/Principal/Relationship/Event 添加测试数据生成器
- [ ] 编写 Repository 集成测试
  - 位置: `tests/integration/test_repositories.py`
- [ ] 验证 Repository 可以正确持久化和检索

**验收**:
- Repository 集成测试通过
- 映射层双向转换正确
- 测试数据生成器工作正常

#### Day 3-4: API 路由迁移

**上午 (Day 3)**:
- [ ] 迁移 `src/myproj/api/v1/messages.py`
  - 移除模块级 `_messages` 字典
  - 注入 `MessageRepository`
  - 更新所有端点使用 repository
  - 保持 API 兼容性不变
- [ ] 迁移 `src/myproj/api/v1/principals.py`
  - 移除模块级可变状态
  - 注入 `PrincipalRepository`
  - 更新所有端点

**下午 (Day 3)**:
- [ ] 迁移 `src/myproj/api/v1/relationships.py`
  - 移除模块级可变状态
  - 注入 `RelationshipRepository`
  - 更新所有端点
- [ ] 迁移 `src/myproj/api/v1/events.py`
  - 移除模块级可变状态
  - 注入 `EventRepository`
  - 更新所有端点

**上午 (Day 4)**:
- [ ] 添加 API 集成测试
  - 位置: `tests/integration/test_api_v1.py`
  - 覆盖所有迁移的端点
  - 验证跨进程重启一致性
- [ ] 添加回归测试套件
  - 确保现有行为不变
  - 验证分页、过滤等功能

**下午 (Day 4)**:
- [ ] 性能检查和优化
- [ ] 文档更新
- [ ] 代码审查准备

**验收**:
- 所有 API 端点测试通过
- 跨进程重启数据保持一致
- 回归测试套件通过

#### Day 5-7: 缓冲与集成

- [ ] 与 Engineer 3 协调 governance 集成点
- [ ] 与 Engineer 4 协调 E3 事件集成
- [ ] 修复发现的 bug
- [ ] 补充文档和测试
- [ ] PR 准备和代码审查

### 关键文件

**Owned Write Scope**:
- `src/myproj/core/repositories/**`
- `src/myproj/infra/db/models.py` (仅在 Lead 批准后)
- `src/myproj/api/v1/messages.py`
- `src/myproj/api/v1/principals.py`
- `src/myproj/api/v1/relationships.py`
- `src/myproj/api/v1/events.py`
- `tests/conftest.py`
- `tests/unit/test_api_endpoints.py`

**Forbidden**:
- ❌ Do NOT modify `src/policy_control/**`
- ❌ Do NOT modify `backend/e3/**`
- ❌ Do NOT modify frontend code
- ❌ Do NOT modify contracts without Lead approval

### 依赖关系

- **无前置依赖** - 可以独立开始
- **需要协调**: 与 Engineer 3 在 governance landing zones 上协调
- **为他人提供**: 稳定的 repository 接口供其他工程师使用

---

## Engineer 3: Governance Kernel Engineer

### 目标

创建 governance 逻辑的未来家园，减少 E1 和 E2 之间的架构分裂。

### 每日分解

#### Day 1: 创建 Landing Zones

**上午**:
- [ ] 创建 `src/myproj/core/governance/` 包结构
  - `__init__.py` - 导出接口
  - `types.py` - 共享类型（从 contracts 导入）
  - `interfaces.py` - 服务接口定义
  - `exceptions.py` - 治理相关异常
- [ ] 创建 `src/myproj/core/approvals/` 包结构
  - `__init__.py`
  - `types.py`
  - `interfaces.py`
- [ ] 创建 `src/myproj/core/risk/` 包结构
  - `__init__.py`
  - `types.py`
  - `interfaces.py`

**下午**:
- [ ] 设计并定义核心服务接口
  - `GovernanceService` 接口
  - `ApprovalService` 接口
  - `RiskSynthesizer` 接口
  - `DelegationService` 接口
- [ ] 从 frozen contracts 导入类型
  - 使用 `myproj.core.contracts` 中的类型
  - **不**重新定义枚举
- [ ] 编写接口文档和使用示例

**验收**:
- 所有包结构创建完成
- 接口定义完整且类型安全
- 使用 frozen contracts 中的类型

#### Day 2: 迁移 Delegation 逻辑

**上午**:
- [ ] 分析 `src/policy_control/delegation/`
  - `models.py` - 数据模型
  - `service.py` - 服务逻辑
  - `constants.py` - 枚举和常量
- [ ] 设计新的 `DelegationService` 实现
  - 位置: `src/myproj/core/governance/delegation_service.py`
  - 使用 `AuthorityGrant` contract
  - 保持与现有 API 兼容性

**下午**:
- [ ] 实现新的 `DelegationService`
- [ ] 创建兼容性 shim
  - 位置: `src/policy_control/delegation/__init__.py`
  - 重新导出新实现
  - 保持旧导入路径工作
- [ ] 编写单元测试
  - 位置: `tests/unit/governance/test_delegation.py`

**验收**:
- 新 DelegationService 实现完整
- 兼容性 shim 工作正常
- 旧导入路径仍然可用

#### Day 3: 迁移 Approval 逻辑

**上午**:
- [ ] 分析 `src/policy_control/approval/`
  - `models.py` - ApprovalRequest, ApprovalResolution
  - `service.py` - ApprovalService
  - `state_machine.py` - 状态机
- [ ] 设计新的 `ApprovalService` 实现
  - 位置: `src/myproj/core/approvals/approval_service.py`
  - 集成 `ActionEnvelope` 和 `SenderStack`
  - 支持 approval payloads 中包含 sender stack
- [ ] 设计 approval preview 合约
  - 包含 sender stack 预览
  - 包含 action impact 信息
  - 包含 risk rationale

**下午**:
- [ ] 实现新的 `ApprovalService`
- [ ] 创建兼容性 shim
  - 位置: `src/policy_control/approval/__init__.py`
- [ ] 编写单元测试
  - 位置: `tests/unit/approvals/test_approval_service.py`
- [ ] 测试与 contracts 的集成

**验收**:
- ApprovalService 支持 sender stack
- Approval preview 包含所有必要信息
- 兼容性 shim 工作正常

#### Day 4: 迁移 Risk 和 Policy 逻辑

**上午**:
- [ ] 分析 `src/policy_control/risk/`
  - `models.py` - 风险模型
  - `synthesizer.py` - 风险合成
  - `action.py`, `relationship.py`, `content.py`, `consequence.py`
- [ ] 设计新的 `RiskSynthesizer`
  - 位置: `src/myproj/core/risk/synthesizer.py`
  - 输出 `RiskPosture` contract
  - 集成 `ActionEnvelope` 上下文
- [ ] 分析 `src/policy_control/policy/`
  - `models.py`
  - `engine.py`
  - `evaluator.py`

**下午**:
- [ ] 实现新的 `RiskSynthesizer`
- [ ] 实现 Policy 相关逻辑的迁移
- [ ] 创建兼容性 shims
- [ ] 编写单元测试
  - 位置: `tests/unit/risk/test_synthesizer.py`

**验收**:
- RiskSynthesizer 输出 RiskPosture contract
- 所有风险评估功能保持一致
- 兼容性 shim 工作正常

#### Day 5: 整合与清理

**上午**:
- [ ] 整合所有 governance 服务
- [ ] 创建统一的 `GovernanceKernel` 入口点
  - 位置: `src/myproj/core/governance/kernel.py`
  - 组合所有服务
  - 提供简化的 API
- [ ] 实现 Kill Switch 迁移
  - 位置: `src/myproj/core/governance/kill_switch.py`

**下午**:
- [ ] 清理 `src/policy_control/`
  - 确保所有实现已迁移
  - 确保所有 shims 已就位
  - 更新文档
- [ ] 编写集成测试
  - 位置: `tests/integration/test_governance.py`
- [ ] 端到端治理流程测试

**验收**:
- GovernanceKernel 可以协调所有服务
- 端到端测试通过
- policy_control 只是兼容性层

#### Day 6-7: 缓冲与集成

- [ ] 与 Engineer 2 协调 repository 集成
- [ ] 与 Engineer 4 协调 E3 execution 集成
- [ ] 修复发现的 bug
- [ ] 补充文档和测试
- [ ] PR 准备和代码审查

### 关键文件

**Owned Write Scope**:
- `src/myproj/core/governance/**`
- `src/myproj/core/approvals/**`
- `src/myproj/core/risk/**`
- `src/policy_control/**` (可修改，但优先移动到 myproj)

**Forbidden**:
- ❌ Do NOT modify `src/myproj/api/v1/**` without Lead approval
- ❌ Do NOT modify `backend/e3/**`
- ❌ Do NOT modify frontend code
- ❌ Do NOT modify contracts without Lead approval

### 依赖关系

- **前置依赖**: Engineer 1 contracts (已完成)
- **需要协调**: 与 Engineer 2 在 repository 上协调
- **为他人提供**: 稳定的 governance 服务接口

---

## Engineer 4: Execution Fabric Engineer

### 目标

使 E3 与共享 contracts 和 replay 预期兼容。

### 每日分解

#### Day 1: ActionEnvelope 集成

**上午**:
- [ ] 分析当前 E3 API 和模型
  - `backend/e3/api/v1/actions.py`
  - `backend/e3/action_runtime/models.py`
  - `backend/e3/action_runtime/engine.py`
- [ ] 设计 ActionEnvelope 集成点
  - 定义 E3 如何消费 ActionEnvelope
  - 定义 E3 如何发出可 replay 的事件
  - 确保 sender stack 在执行生命周期中传递

**下午**:
- [ ] 更新 E3 API 端点接受 ActionEnvelope
  - 修改 `backend/e3/api/v1/actions.py`
  - 添加 `/envelope` 端点接受 ActionEnvelope
  - 保持现有端点兼容性
- [ ] 更新 ActionRun 模型存储 contract 数据
  - 存储 sender_stack JSON
  - 存储 disclosure_preview JSON
  - 存储完整的 envelope 引用
- [ ] 添加 contract 导入和类型

**验收**:
- E3 API 可以接受 ActionEnvelope
- ActionRun 模型存储 contract 数据
- 现有端点保持工作

#### Day 2: Sender Stack 传递

**上午**:
- [ ] 更新 ActionRuntime 携带 sender stack
  - 位置: `backend/e3/action_runtime/engine.py`
  - 在所有阶段传递 sender_stack
  - 确保审计日志包含 sender_stack
- [ ] 更新状态机记录 sender 信息
  - 位置: `backend/e3/action_runtime/state_machine.py`
  - 在状态转换中记录 actor
  - 为 replay 保存完整上下文

**下午**:
- [ ] 实现执行结果事件
  - 定义 execution_event 结构
  - 包含 delivery 里程碑
  - 包含 acknowledgement 信息
- [ ] 设计 E3 → Core 事件桥接
  - 如何将执行结果反馈给 Core
  - 如何映射到 ThreadEvent
  - 如何保持幂等性
- [ ] 编写单元测试

**验收**:
- Sender stack 在执行生命周期中传递
- 执行结果可以映射回 Core 事件
- 所有阶段有审计日志

#### Day 3: Replay-friendly 输出

**上午**:
- [ ] 设计 replay 事件格式
  - 与 Core 事件格式对齐
  - 包含 authority/approval 元数据
  - 包含执行里程碑
- [ ] 实现 execution 事件发射器
  - 位置: `backend/e3/action_runtime/events.py`
  - 发出结构化事件
  - 支持多种输出格式 (日志, API, 消息队列)

**下午**:
- [ ] 添加 delivery acknowledgement 追踪
  - 追踪发送状态
  - 追踪送达确认
  - 追踪错误重试
- [ ] 保持幂等性保证
  - 验证 idempotency_key 使用
  - 确保重复安全处理
- [ ] 编写集成测试

**验收**:
- Execution 事件格式与 Core 对齐
- Delivery 追踪完整
- 幂等性保证保持

#### Day 4: E3 测试通过

**上午**:
- [ ] 运行 E3 测试套件
  - `backend/e3/tests/`
  - 修复任何破损的测试
  - 添加新的 contract 集成测试
- [ ] 添加 contract 兼容性测试
  - 位置: `backend/e3/tests/test_contracts.py`
  - 验证 ActionEnvelope 消费
  - 验证事件输出格式

**下午**:
- [ ] 端到端执行流程测试
  - ActionEnvelope → E3 → Execution → Result Events
  - 验证完整流程
  - 验证 replay 链完整性
- [ ] 性能和可靠性测试
  - 错误重试测试
  - 幂等性测试
  - 并发执行测试

**验收**:
- 所有 E3 测试通过
- Contract 兼容性测试通过
- 端到端流程正常工作

#### Day 5-7: 缓冲与集成

- [ ] 与 Engineer 3 协调 governance 集成
- [ ] 与 Engineer 2 协调 Core event 集成
- [ ] 实现 E3 → Core 事件桥接
- [ ] 修复发现的 bug
- [ ] 补充文档和测试
- [ ] PR 准备和代码审查

### 关键文件

**Owned Write Scope**:
- `backend/e3/**`
- `backend/e3/tests/**`

**Forbidden**:
- ❌ Do NOT modify `src/myproj/api/v1/**` without Lead approval
- ❌ Do NOT modify `src/policy_control/**`
- ❌ Do NOT modify frontend code
- ❌ Do NOT modify contracts without Lead approval

### 依赖关系

- **前置依赖**: Engineer 1 contracts (已完成)
- **需要协调**: 与 Engineer 3 在 governance 上协调
- **为他人提供**: 稳定的 E3 contract 接口

---

## Engineer 5: Frontend Operator Console Engineer

### 目标

使产品在视觉和概念上都成为一个 Communication OS。

### 每日分解

#### Day 1: Thread Workspace 重新设计

**上午**:
- [ ] 分析当前 thread detail 页面
  - `src/app/(app)/threads/[id]/page.tsx`
  - 理解现有数据流
  - 识别需要增强的区域
- [ ] 设计新的 Thread Workspace 布局
  - Thread Objective 区域
  - Delegation Summary 卡片
  - Next Action Preview 区域
  - Replay Timeline 面板
  - Approval & Control 操作区
- [ ] 创建组件结构
  - `src/components/thread/ThreadWorkspace.tsx`
  - `src/components/thread/ThreadObjective.tsx`
  - `src/components/thread/DelegationSummary.tsx`

**下午**:
- [ ] 实现 ThreadObjective 组件
  - 显示 thread objective
  - 显示状态和风险等级
  - 可编辑的 objective
- [ ] 实现 DelegationSummary 组件
  - 显示当前 delegation mode
  - 显示 active authority grant
  - 链接到 authority 配置
- [ ] 使用 JSON fixtures 开发
  - 从 `tests/fixtures/contracts/` 加载
  - 无需等待后端集成

**验收**:
- Thread Workspace 布局完整
- Objective 和 Delegation 组件工作
- 使用 fixtures 可以正常渲染

#### Day 2: Approval Inbox 增强

**上午**:
- [ ] 分析当前 approval 页面
  - `src/app/(app)/approvals/page.tsx`
  - `src/app/(app)/approvals/[id]/page.tsx`
- [ ] 设计增强的 Approval Card
  - 包含 Sender Stack 预览
  - 包含 Action Preview
  - 包含 Risk Explanation
  - Approve/Modify/Reject/Take-over 控件
- [ ] 创建 approval 组件
  - `src/components/approval/ApprovalCard.tsx`
  - `src/components/approval/SenderStackPreview.tsx`
  - `src/components/approval/ActionPreview.tsx`

**下午**:
- [ ] 实现 SenderStackPreview 组件
  - 显示 owner/delegate/author/approver/executor
  - 使用 disclosure mode 决定显示内容
  - 悬停显示详细信息
- [ ] 实现 ActionPreview 组件
  - 显示 action type 和 label
  - 显示 target recipients
  - 显示 payload 摘要
- [ ] 更新 approval inbox 页面
  - 使用新的 ApprovalCard
  - 添加过滤和排序
  - 添加批量操作

**验收**:
- Approval Card 显示所有 contract 信息
- Sender Stack 预览工作正常
- Action Preview 显示内容正确

#### Day 3: Replay Timeline 升级

**上午**:
- [ ] 分析当前 replay 页面
  - `src/app/(app)/replay/page.tsx`
  - `src/app/(app)/replay/[id]/page.tsx`
- [ ] 设计升级的 Replay Timeline
  - 按决策链阶段分组
  - Authority 和 Disclosure 可见性
  - Execution 里程碑显示
  - 时间线导航和搜索
- [ ] 创建 replay 组件
  - `src/components/replay/ReplayTimeline.tsx`
  - `src/components/replay/DecisionStage.tsx`
  - `src/components/replay/AuthorityBadge.tsx`

**下午**:
- [ ] 实现决策链阶段分组
  - Thread Creation → Planning → Approval → Execution → Completion
  - 每个阶段清晰分隔
  - 可折叠/展开阶段
- [ ] 实现 authority 和 disclosure 可见性
  - 在事件上显示 authority badges
  - 显示 disclosure mode
  - 显示 sender stack 快照
- [ ] 实现 execution 里程碑
  - 显示 delivery 状态
  - 显示 acknowledgement
  - 显示重试和错误

**验收**:
- Replay Timeline 按阶段分组
- Authority 和 Disclosure 可见
- Execution 里程碑显示正确

#### Day 4: Relationship & Authority 管理界面

**上午**:
- [ ] 创建 Relationship Console 页面
  - 位置: `src/app/(app)/relationships/page.tsx`
  - 关系列表和过滤器
  - 关系策略预设
  - 关系详情编辑
- [ ] 创建 relationship 组件
  - `src/components/relationship/RelationshipList.tsx`
  - `src/components/relationship/RelationshipPolicyEditor.tsx`
  - `src/components/relationship/RelationshipClassSelector.tsx`

**下午**:
- [ ] 创建 Identity & Authority Console 页面
  - 位置: `src/app/(app)/authority/page.tsx`
  - Authority grants 列表
  - Authority grant 创建/编辑
  - Disclosure defaults 配置
  - Escalation rules 配置
  - Kill switch 控件
- [ ] 创建 authority 组件
  - `src/components/authority/AuthorityGrantCard.tsx`
  - `src/components/authority/AuthorityGrantEditor.tsx`
  - `src/components/authority/DisclosureConfig.tsx`
- [ ] 使用 TypeScript types
  - 从 `@/lib/types/contracts` 导入
  - 完全类型安全

**验收**:
- Relationship Console 页面完整
- Authority Console 页面完整
- 所有组件使用正确的 types

#### Day 5: UI/Backend 集成

**上午**:
- [ ] 创建 API hooks 对接 contracts
  - 位置: `src/lib/api/contracts.ts`
  - useActionEnvelope
  - useApprovalWithSenderStack
  - useReplayWithAuthority
- [ ] 集成 Thread Workspace
  - 连接真实 API
  - 移除 fixtures
  - 处理加载和错误状态
- [ ] 集成 Approval Inbox
  - 连接 approval API
  - 实现 approve/modify/reject/take-over
  - 实时更新

**下午**:
- [ ] 集成 Replay Center
  - 连接 events API
  - 加载完整 replay 链
  - 搜索和过滤
- [ ] 集成 Relationship/Authority Console
  - 连接相应的 API
  - 实现 CRUD 操作
  - 实时验证
- [ ] 端到端 UI 测试
  - 完整流程测试
  - 跨页面导航测试
  - 错误处理测试

**验收**:
- 所有页面连接真实 API
- 端到端流程正常工作
- 错误处理优雅

#### Day 6-7: 缓冲与打磨

- [ ] 与 Engineer 2/3/4 协调 API 集成
- [ ] 性能优化
- [ ] 可访问性改进
- [ ] 响应式设计调整
- [ ] 补充文档和测试
- [ ] PR 准备和代码审查

### 关键文件

**Owned Write Scope**:
- `src/app/(app)/threads/**`
- `src/app/(app)/approvals/**`
- `src/app/(app)/replay/**`
- `src/app/(app)/settings/**`
- `src/components/approval/**`
- `src/components/replay/**`
- `src/components/thread/**`
- `src/lib/types/**`
- `src/lib/api/**`

**Forbidden**:
- ❌ Do NOT modify `backend/e3/**`
- ❌ Do NOT modify `src/policy_control/**`
- ❌ Do NOT modify repository and DB files
- ❌ Do NOT modify contracts without Lead approval

### 依赖关系

- **前置依赖**: Engineer 1 contracts (已完成)
- **可以并行**: 使用 fixtures 先开发 UI
- **需要协调**: 与所有后端工程师在 API 上协调

---

## Lead / Integrator: 每日职责

### Day 1-2: 启动与监督

**上午**:
- [ ] 主持每日站会
- [ ] 审查各工程师的分支边界
- [ ] 解决早期阻塞问题
- [ ] 检查 contracts 没有被意外修改

**下午**:
- [ ] 创建集成分支 `feature/contract-integration`
- [ ] 设置分支保护规则
- [ ] 与每位工程师一对一
- [ ] 审查初始提交

### Day 3-4: 集成协调

**上午**:
- [ ] 主持每日站会
- [ ] 检查各工程师的进度
- [ ] 识别集成风险
- [ ] 解决跨工程师的设计问题

**下午**:
- [ ] 维护集成分支
- [ ] 开始合并早期完成的工作
- [ ] 协调 Engineer 2-3-4-5 的集成点
- [ ] 与每位工程师一对一

### Day 5-6: 合并与解决

**上午**:
- [ ] 按顺序合并 PRs
  1. Engineer 3 governance landing zones
  2. Engineer 2 repositories
  3. Engineer 4 E3 changes
  4. Engineer 5 frontend
- [ ] 解决合并冲突
- [ ] 修复 schema mismatches

**下午**:
- [ ] 添加端到端测试
- [ ] 打磨 replay 和 approval 接缝
- [ ] 与各工程师协调解决问题
- [ ] 准备验收演示

### Day 7: 验收与演示

**上午**:
- [ ] 运行完整测试套件
- [ ] 端到端流程验证
- [ ] 最终文档检查
- [ ] 准备演示材料

**下午**:
- [ ] 主持验收演示
- [ ] 收集反馈
- [ ] 记录已知问题
- [ ] 规划下一阶段

### Lead 关键文件

**Owned Write Scope (Only Lead can modify)**:
- `src/myproj/core/contracts/**/*.py`
- `src/myproj/core/contracts/__init__.py`
- `src/myproj/infra/db/models.py`
- `docs/product/**/*.md`
- `docs/engineering/**/*.md`

---

## 风险与缓解

### Risk 1: Contract 需要修改

**可能性**: 中
**影响**: 高
**缓解**:
- 所有 contract 修改必须经过 Lead
- 使用严格的变更请求流程
- 最小化变更，只在真正必要时

### Risk 2: 集成点不匹配

**可能性**: 高
**影响**: 中
**缓解**:
- 早做 API 设计评审
- 使用 fixtures 和 mocks 提前集成
- 每日检查点识别不匹配

### Risk 3: 一位工程师阻塞其他人

**可能性**: 中
**影响**: 高
**缓解**:
- 明确依赖关系
- 缓冲时间
- Lead 可以介入帮助
- 并行工作流设计最小化阻塞

### Risk 4: UI 超越后端语义

**可能性**: 中
**影响**: 中
**缓解**:
- 早期就 API contracts 达成一致
- 前端可以用 typed mock payloads 原型化
- Lead 每周两次集成检查

---

## 成功标准

### Sprint 1 完成标准

- [ ] Engineer 2: 所有 API routes 使用 repository-backed 流程
- [ ] Engineer 3: Governance 逻辑移至 `src/myproj`，policy_control 是 shim
- [ ] Engineer 4: E3 消费 ActionEnvelope，发出 replay-friendly 事件
- [ ] Engineer 5: UI 展示 thread/action/approval/replay 故事
- [ ] Lead: 集成分支工作，端到端流程通过
- [ ] 所有测试通过
- [ ] 文档完整

### 验收演示场景

1. **面试调度**: Thread → Delegation → Draft → Approval → Execution → Replay
2. **客户跟进**: Relationship-aware policy → Escalation triggers → Human intervention
3. **审批受限外部通信**: Sender stack visible → Approval inbox → Execution → Full replay chain

---

## 沟通计划

### Slack Channels

- `#sprint1-general` - 所有更新
- `#sprint1-eng2` - Engineer 2 专用
- `#sprint1-eng3` - Engineer 3 专用
- `#sprint1-eng4` - Engineer 4 专用
- `#sprint1-eng5` - Engineer 5 专用

### 文档位置

- 所有计划: `docs/engineering/`
- 所有产品文档: `docs/product/`
- Contract 快速入门: `docs/product/QUICKSTART_CONTRACTS.md`

### 紧急联系

- 阻塞问题: @lead 立即
- 合同问题: 只有 Lead 可以决定
- 范围问题: 先查 `WRITE_SCOPE_LOCK.md`

---

**Plan Version**: 1.0
**Last Updated**: 2026-03-27
**Status**: Ready to Start
