
# ActionRun 状态机设计

&gt; 文档用途：定义ActionRun的状态、流转规则、触发条件和测试用例

## 1. 状态定义

### 1.1 状态枚举

```python
from enum import Enum

class ActionRunStatus(str, Enum):
    CREATED = "created"
    PLANNED = "planned"
    READY_FOR_APPROVAL = "ready_for_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    CANCELLED = "cancelled"
```

### 1.2 状态说明

| 状态 | 说明 | 是否终态 |
|------|------|----------|
| `created` | 动作已创建，尚未规划 | 否 |
| `planned` | 动作已规划，参数已完整 | 否 |
| `ready_for_approval` | 等待人工审批 | 否 |
| `approved` | 已获批准，可执行 | 否 |
| `executing` | 正在执行中 | 否 |
| `sent` | 已发送到外部渠道 | 否 |
| `acknowledged` | 外部已确认接收 | 是 |
| `failed_retryable` | 失败，可重试 | 否 |
| `failed_terminal` | 失败，不可重试 | 是 |
| `cancelled` | 已取消 | 是 |

---

## 2. 状态机图

```
                    ┌─────────┐
                    │ created │
                    └────┬────┘
                         │ plan
                         ▼
                    ┌─────────┐
                    │ planned │◄──────────────┐
                    └────┬────┘               │
                         │                      │
         ┌───────────────┼───────────────┐    │
         │               │               │    │
         │ submit_for    │               │    │
         │ _approval     │ cancel        │    │
         ▼               ▼               │    │
┌──────────────────┐  ┌───────────┐      │    │
│ ready_for_       │  │ cancelled │      │    │
│ approval         │  └───────────┘      │    │
└────────┬─────────┘                      │    │
         │                                │    │
    ┌────┴────┐                           │    │
    │         │                           │    │
approve    reject/cancel                  │    │
    │         │                           │    │
    ▼         ▼                           │    │
┌──────────┐ ┌───────────┐               │    │
│ approved │ │ cancelled │               │    │
└────┬─────┘ └───────────┘               │    │
     │                                     │    │
     │ start_execution                     │    │
     ▼                                     │    │
┌─────────────┐                            │    │
│  executing  │                            │    │
└──────┬──────┘                            │    │
       │                                   │    │
    ┌──┼──────────┬───────────┐           │    │
    │  │          │           │           │    │
send_ send_fail_ send_fail_  cancel       │    │
success retryable terminal   │           │    │
    │  │          │           │           │    │
    ▼  ▼          ▼           ▼           │    │
┌─────┐ ┌──────────────┐ ┌───────────────┐ │    │
│sent│ │failed_retryable││failed_terminal│ │    │
└──┬──┘ └───────┬──────┘ └───────────────┘ │    │
   │            │                           │    │
acknowledge   retry                         │    │
   │            │                           │    │
   ▼            └───────────────────────────┘    │
┌─────────────┐                      max_retries  │
│acknowledged │                      _exceeded     │
└─────────────┘                           │         │
                                          ▼         │
                                 ┌───────────────┐ │
                                 │failed_terminal│ │
                                 └───────────────┘ │
                                                   │
                              ┌────────────────────┘
                              │
                              ▼
                       ┌───────────┐
                       │ cancelled │
                       └───────────┘
```

---

## 3. 状态流转规则

### 3.1 流转定义

```json
{
  "state_machine": {
    "ActionRun": {
      "initial": "created",
      "states": {
        "created": {
          "on": {
            "plan": "planned"
          }
        },
        "planned": {
          "on": {
            "submit_for_approval": "ready_for_approval",
            "cancel": "cancelled"
          }
        },
        "ready_for_approval": {
          "on": {
            "approve": "approved",
            "reject": "cancelled",
            "cancel": "cancelled"
          }
        },
        "approved": {
          "on": {
            "start_execution": "executing",
            "cancel": "cancelled"
          }
        },
        "executing": {
          "on": {
            "send_success": "sent",
            "send_fail_retryable": "failed_retryable",
            "send_fail_terminal": "failed_terminal"
          }
        },
        "sent": {
          "on": {
            "acknowledge": "acknowledged"
          }
        },
        "failed_retryable": {
          "on": {
            "retry": "executing",
            "max_retries_exceeded": "failed_terminal"
          }
        },
        "acknowledged": {
          "type": "final"
        },
        "failed_terminal": {
          "type": "final"
        },
        "cancelled": {
          "type": "final"
        }
      }
    }
  }
}
```

### 3.2 触发事件说明

| 事件 | 触发条件 |
|------|----------|
| `plan` | 系统完成动作参数规划 |
| `submit_for_approval` | 策略引擎判定需要审批 |
| `approve` | 用户在审批中心点击批准 |
| `reject` | 用户在审批中心点击拒绝 |
| `cancel` | 用户或系统取消动作 |
| `start_execution` | 执行引擎开始执行 |
| `send_success` | 外部API调用成功返回 |
| `send_fail_retryable` | 网络超时、5xx错误等 |
| `send_fail_terminal` | 400错误、认证失败等 |
| `acknowledge` | 收到外部送达回执 |
| `retry` | 指数退避后重试 |
| `max_retries_exceeded` | 超过最大重试次数（默认5次） |

---

## 4. 测试用例

### 4.1 正常流程测试（AR-001 至 AR-004）

**AR-001: 完整成功流程**
```
Input: created → plan → submit_for_approval → approve → start_execution → send_success → acknowledge
Expected: acknowledged
```

**AR-002: 无需审批的成功流程**
```
Input: created → plan → start_execution → send_success → acknowledge
Expected: acknowledged
```

**AR-003: Planned状态取消**
```
Input: created → plan → cancel
Expected: cancelled
```

**AR-004: Approval阶段拒绝**
```
Input: created → plan → submit_for_approval → reject
Expected: cancelled
```

### 4.2 失败重试测试（AR-005 至 AR-008）

**AR-005: 单次重试后成功**
```
Input: created → plan → start_execution → send_fail_retryable → retry → send_success → acknowledge
Expected: acknowledged
```

**AR-006: 多次重试后成功**
```
Input: created → plan → start_execution → send_fail_retryable → retry → send_fail_retryable → retry → send_success → acknowledge
Expected: acknowledged
```

**AR-007: 超过最大重试次数**
```
Input: created → plan → start_execution → send_fail_retryable → (retry × 5) → max_retries_exceeded
Expected: failed_terminal
```

**AR-008: 终端失败**
```
Input: created → plan → start_execution → send_fail_terminal
Expected: failed_terminal
```

### 4.3 边界场景测试（AR-009 至 AR-011）

**AR-009: Approved状态取消**
```
Input: created → plan → submit_for_approval → approve → cancel
Expected: cancelled
```

**AR-010: 无效的状态转换（从sent到executing）**
```
Input: sent → start_execution
Expected: TransitionError, state remains sent
```

**AR-011: 终态后尝试转换**
```
Input: acknowledged → plan
Expected: TransitionError, state remains acknowledged
```

### 4.4 幂等性测试（AR-I01 至 AR-I04）

**AR-I01: 相同幂等键重复请求**
```
Test: 同一动作连续两次execute调用
Expected: 只执行一次，第二次返回已有结果
```

**AR-I02: 不同幂等键独立处理**
```
Test: 两个不同动作使用不同幂等键
Expected: 各自独立执行，互不干扰
```

**AR-I03: 幂等键过期后重新执行**
```
Test: 24小时后使用相同幂等键
Expected: 允许重新执行（TTL已过期）
```

**AR-I04: 并发请求幂等保证**
```
Test: 10个并发请求使用相同幂等键
Expected: 只有1个成功执行，其余返回已有结果
```

---

## 5. 动作类型

| 动作类型 | 说明 | 渠道 |
|----------|------|------|
| `send_email` | 发送邮件 | email |
| `create_calendar_event` | 创建日历事件 | calendar |
| `update_calendar_event` | 更新日历事件 | calendar |
| `cancel_calendar_event` | 取消日历事件 | calendar |
| `send_followup` | 发送跟进提醒 | email |

---

## 6. ActionRun对象模型

```python
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ActionRun(BaseModel):
    id: UUID
    thread_id: UUID
    action_type: str
    status: ActionRunStatus

    # 幂等控制
    idempotency_key: str

    # 输入输出
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]]

    # 风险与审批
    risk_decision: Optional[str]
    approval_request_id: Optional[UUID]

    # 执行元数据
    retry_count: int = 0
    max_retries: int = 5
    last_error: Optional[str]

    # 外部追踪
    external_message_id: Optional[str]
    external_thread_id: Optional[str]

    # 时间戳
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime]
    executed_at: Optional[datetime]
```

