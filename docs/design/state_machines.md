
# 状态机设计

## ApprovalRequest 状态机

```
PENDING -&gt; APPROVED
PENDING -&gt; REJECTED
PENDING -&gt; MODIFIED
PENDING -&gt; TAKEN_OVER
PENDING -&gt; CANCELLED
PENDING -&gt; TIMEOUT
```

### 状态说明

| 状态 | 说明 |
|------|------|
| PENDING | 待审批 |
| APPROVED | 已批准 |
| REJECTED | 已拒绝 |
| MODIFIED | 已修改后批准 |
| TAKEN_OVER | 已接管 |
| CANCELLED | 已取消 |
| TIMEOUT | 已超时 |

### 终态
- APPROVED, REJECTED, MODIFIED, TAKEN_OVER, CANCELLED, TIMEOUT 都是终态，不允许再变更

---

## DelegationProfile 档位级别

| 档位 | 说明 | 允许的动作 |
|------|------|-----------|
| OBSERVE_ONLY | 只观察与建议，不起草不发送 | [] |
| DRAFT_FIRST | 自动起草，但所有消息需人工确认 | ["draft_message"] |
| APPROVE_TO_SEND | 低风险动作自动准备，用户一键审批后发出 | ["draft_message", "prepare_action"] |
| BOUNDED_AUTO | 在明确预算和动作边界内自动执行 | ["draft_message", "send_message", "schedule_followup"] |
| HUMAN_ONLY | 该类关系或场景禁止代理主动介入 | [] |

---

## Risk Level 映射

| 分数 | 等级 | 决策建议 |
|------|------|---------|
| 1 | LOW | ALLOW |
| 2 | LOW | ALLOW / DRAFT_ONLY |
| 3 | MEDIUM | REQUIRE_APPROVAL |
| 4 | HIGH | ESCALATE_TO_HUMAN |
| 5 | CRITICAL | DENY |

---

## Conflict Resolution 优先级

### Effect 优先级（数值越大优先级越高）
- DENY: 100
- REQUIRE_APPROVAL: 75
- ESCALATE: 50
- ALLOW: 25

### Scope 优先级（数值越大优先级越高）
- THREAD: 100
- RELATIONSHIP: 75
- PROFILE: 50
- GLOBAL: 25

### Delegation 优先级（数值越大优先级越高）
- Thread: 100
- Relationship: 50
- User Default: 20
- System Default: 10
