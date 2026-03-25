
# 8步决策链

## 概述

每次动作执行前，都走以下8步决策流程：

```
1. 读取 thread objective 与当前状态
   ↓
2. 读取 relationship class 与 delegation profile
   ↓
3. 生成候选动作
   ↓
4. 进行规则命中与预算检查（包括熔断检查）
   ↓
5. 进行内容/语义风险评估
   ↓
6. 进行结果代价评估
   ↓
7. 决定：自动执行/进入审批/升级人工或拒绝
   ↓
8. 记录完整 decision trace 进入 replay
```

---

## 详细步骤

### Step 1: 读取 thread objective 与当前状态

- 输入: thread_id
- 输出: thread_objective, thread_status, thread_context

### Step 2: 读取 relationship class 与 delegation profile

- 输入: thread_id, relationship_id
- 输出: delegation_profile (优先级: Thread &gt; Relationship &gt; User Default &gt; System Default)

### Step 3: 生成候选动作

- 输入: thread_context, delegation_profile
- 输出: candidate_action

### Step 4: 进行规则命中与预算检查

#### 4.1 检查熔断
- Global Kill Switch?
- Profile Kill Switch?
- Thread Kill Switch?

#### 4.2 规则匹配
- 收集所有适用规则
- 按优先级排序
- 冲突解决

#### 4.3 预算检查
- 是否在预算范围内?
- 是否需要重置窗口?

### Step 5: 进行内容/语义风险评估

四层风险评估:
1. **Relationship Risk**: 这是对谁说话?
2. **Action Risk**: 准备做什么动作?
3. **Content Risk**: 这段内容是否涉及承诺/冲突/隐私/不确定性?
4. **Consequence Risk**: 如果发出后出错，代价有多高?

### Step 6: 进行结果代价评估

- 历史错误率
- 历史升级率
- 该线程的历史问题

### Step 7: 合成最终决策

决策输出:
- `allow` - 允许自动执行
- `draft_only` - 仅允许起草
- `require_approval` - 需要审批后才能执行
- `bounded_execution` - 在边界内自动执行
- `escalate_to_human` - 升级给人工处理
- `deny` - 拒绝执行

**默认保守策略**: 异常情况一律 escalate_to_human

### Step 8: 记录完整 decision trace

记录:
- 每一步的输入/输出
- 耗时
- 命中的策略
- 风险评估结果
- 是否受熔断影响
- 最终决策和原因

---

## 决策合成策略

### 最保守优先原则

优先级:
1. DENY
2. ESCALATE_TO_HUMAN
3. REQUIRE_APPROVAL
4. DRAFT_ONLY
5. BOUNDED_EXECUTION
6. ALLOW

### 委托档位调整

- **Draft First**: 即使策略允许，也只能draft
- **Approve to Send**: 自动执行降级为需要审批
- **Bounded Auto**: 可以自动执行低风险动作

---

## 风险评估权重

| 维度 | 权重 |
|------|------|
| Relationship | 35% |
| Action | 30% |
| Content | 20% |
| Consequence | 15% |

**最大风险优先**: 如果任一风险是CRITICAL或HIGH，整体升级。
