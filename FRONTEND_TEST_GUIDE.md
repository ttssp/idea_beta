# 前端测试指南

本文档指导你如何在前端界面中实际测试 Communication OS v1 的核心概念。

## 前置条件

确保前端开发服务器正在运行：
```bash
cd src
npm run dev
```

然后访问: http://localhost:3000

---

## 测试场景 1: Thread Over Message（线程优先）

**v1概念**: 线程是核心对象，消息只是线程内的一种事件类型。

### 测试步骤:

1. **打开首页** http://localhost:3000

2. **观察线程列表**:
   - ✅ 你看到的不是"消息列表"，而是"线程列表"
   - ✅ 每个线程有明确的目标（objective）
   - ✅ 每个线程有状态标签（planning/active/awaiting_approval等）
   - ✅ 每个线程有委托档位（draft_first/approve_to_send等）
   - ✅ 每个线程有风险级别（low/medium/high）

3. **点击任意线程**，进入线程详情页:
   - ✅ 顶部显示线程目标（objective）
   - ✅ 显示当前责任方（currentResponsible）
   - ✅ 显示委托档位（delegationProfile）
   - ✅ 显示时间线（Timeline），而不是简单的消息流

### 验证点:
- [ ] 没有"聊天窗口"的感觉
- [ ] 有"工作区"的感觉
- [ ] 重点在"目标如何被推进"，而不是"谁说了什么"

---

## 测试场景 2: Replayable Trust（可回放信任）

**v1概念**: 每个重要动作都必须可追踪，信任来自可回放性。

### 测试步骤:

1. **打开线程详情页**（比如"协调终面时间"）

2. **观察时间线（Timeline）**:
   - ✅ 每个事件都有明确的类型标签（state_change/decision/approval/message）
   - ✅ 每个事件都有actor（执行者）
   - ✅ 每个事件都有时间戳
   - ✅ 有决策追踪（Decision Trace）卡片

3. **查看决策追踪（Decision Trace）**:
   - ✅ 关系风险（relationshipRisk）
   - ✅ 动作风险（actionRisk）
   - ✅ 内容风险（contentRisk）
   - ✅ 结果风险（consequenceRisk）
   - ✅ 最终决策（finalDecision）

### 验证点:
- [ ] 你能看到"为什么"做了某个决策，而不只是"发生了什么"
- [ ] 所有的风险评估都记录在案
- [ ] 整个过程是可审计的

---

## 测试场景 3: Delegation Is Layered（分层委托）

**v1概念**: 委托不是二元的，支持多层级。

### 测试步骤:

1. **创建新线程**:
   - 点击左下角 "+ New Thread" 或首页的 "New Thread" 按钮

2. **填写表单**:
   - 标题: "测试委托档位"
   - 目标: "测试不同委托档位的行为"
   - **委托档位**: 观察有5个选项！

3. **测试5个委托档位**:
   - Observe Only - 只观察与建议
   - Draft First - 自动起草，需人工确认
   - Approve to Send - 低风险自动准备，一键审批
   - Bounded Auto - 明确边界内自动执行
   - Human Only - 禁止代理介入

4. **查看已有线程的委托档位**:
   - "协调终面时间": approve_to_send
   - "收集Q1项目报告": bounded_auto
   - "确认客户会议": draft_first
   - "跟进供应商报价": observe_only

### 验证点:
- [ ] 委托不是简单的"开/关"
- [ ] 有5个精细的档位选择
- [ ] 不同线程可以有不同的委托档位
- [ ] 委托档位在线程详情页清晰展示

---

## 测试场景 4: Identity First（身份优先）

**v1概念**: 始终先解决谁在说话、代表谁、披露什么。

### 测试步骤:

1. **查看线程参与者**:
   - 打开任意线程详情页
   - 查看"参与者"部分
   - 观察不同类型的principal:
     - Human（人类）: 张明
     - Agent（代理）: Agent Assistant
     - External（外部方）: 李华 (候选人), 王经理 (客户)

2. **观察时间线中的actor**:
   - 每个事件都明确显示是谁做的
   - 有avatar和显示名称
   - 你能区分"代理做的" vs "人做的"

### 验证点:
- [ ] 身份不是事后补充的元数据
- [ ] 身份是核心概念
- [ ] 你能清楚知道"谁"在"代表谁"

---

## 测试场景 5: Human Sovereignty（人类主权）

**v1概念**: 人类保留批准权、撤销权、中断权。

### 测试步骤:

1. **查看线程操作栏（ThreadActionBar）**:
   - 打开任意线程详情页
   - 观察顶部的操作按钮:
     - Pause / Resume - 暂停/恢复
     - Takeover - 接管
     - (以及其他控制按钮)

2. **理解"接管"概念**:
   - 当你点击"Takeover"时，你从代理手中拿回控制权
   - 这体现了"人类有最终决定权"

3. **查看审批概念**:
   - 看状态为"awaiting_approval"的线程
   - 这意味着代理在等待人类批准

### 验证点:
- [ ] 人类可以随时中断代理
- [ ] 人类可以接管控制权
- [ ] 高风险动作需要人类批准
- [ ] 代理永远是"助手"，不是"主人"

---

## 测试场景 6: Action Over Text（动作优先）

**v1概念**: 建模draft/propose/clarify/commit/approve/escalate/execute/resolve，而不是把所有沟通当作无差别的自由文本。

### 测试步骤:

1. **观察时间线中的事件类型**:
   - state_change - 状态变更
   - decision - 决策
   - message - 消息
   - approval - 审批
   - takeover - 接管

2. **理解这不是简单的消息**:
   - 每个事件都有明确的语义
   - 系统理解"发生了什么类型的动作"
   - 不只是"一串文本"

### 验证点:
- [ ] 系统理解动作的语义
- [ ] 不是所有内容都被当作"消息"
- [ ] 不同类型的事件有不同的视觉呈现

---

## 端到端测试：创建新线程

让我们完整测试一遍创建新线程的流程，验证所有概念:

### 步骤:

1. **点击 "New Thread"**
   - 验证: 打开新建线程页面
   - 验证: 有明确的"目标"字段，不只是"消息"

2. **填写表单**:
   - 标题: "安排团队周会"
   - 目标: "与团队确定下周周会时间"
   - 委托档位: 选择 "Draft First（先起草）"
   - 点击 "创建线程"

3. **验证创建成功**:
   - 验证: 跳转到新线程页面
   - 验证: 线程状态是 "planning"
   - 验证: 委托档位显示 "Draft First"
   - 验证: 当前责任方是你（人类）

4. **返回首页**:
   - 验证: 新线程出现在列表第一位
   - 验证: 显示正确的状态、委托档位、风险级别

---

## 总结

这6个测试场景验证了Communication OS v1的8大产品原则:

| 原则 | 测试场景 |
|------|---------|
| Identity First | 场景4 |
| Delegation Is Layered | 场景3 |
| Thread Over Message | 场景1 |
| Action Over Text | 场景6 |
| Replayable Trust | 场景2 |
| Human Sovereignty | 场景5 |
| Relationship-Aware Behavior | (通过关系类别和风险体现) |
| Transport-Agnostic Execution | (前端不关心Email/Calendar，只关心线程) |

前端看起来"简单"，但背后是完整的操作系统级概念！
