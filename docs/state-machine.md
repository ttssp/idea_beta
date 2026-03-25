# Thread 状态机设计

## 状态定义

| 状态 | 说明 |
|------|------|
| `new` | 线程新建，待初始化 |
| `planning` | 系统正在评估目标与生成初始动作计划 |
| `active` | 线程处于正常推进中 |
| `awaiting_external` | 等待外部方回复 |
| `awaiting_approval` | 存在待人工审批动作 |
| `blocked` | 缺少信息、外部失败或规则冲突 |
| `paused` | 用户主动暂停 |
| `escalated` | 已升级到人工主导 |
| `completed` | 目标达成，线程关闭 |
| `cancelled` | 用户主动终止或失去继续推进价值 |

## 状态流转图

```
    ┌───────┐
    │  new  │
    └───┬───┘
        │
        ▼
    ┌──────────┐
    │planning  │
    └───┬──────┘
        │
        ▼
    ┌─────────┐
    │ active  │◄─────────────────────────────────┐
    └────┬────┘                                  │
         │                                       │
    ┌────┼────┬───────┬───────┬────────┐       │
    │    │    │       │       │        │       │
    ▼    ▼    ▼       ▼       ▼        ▼       │
┌──────┐ ┌──────┐ ┌───────┐ ┌───────┐ ┌─────────┐│
│await │ │await │ │blocked│ │paused │ │escalated││
│_ext  │ │_appr │ │       │ │       │ │         ││
└──┬───┘ └──┬───┘ └───┬───┘ └───┬───┘ └────┬────┘│
   │         │         │          │           │     │
   └─────────┴─────────┴──────────┴───────────┴─────┘
                          │
                    ┌─────┴─────┐
                    │           │
                    ▼           ▼
              ┌──────────┐ ┌───────────┐
              │completed │ │cancelled  │
              └──────────┘ └───────────┘
```

## 合法流转规则

| 源状态 | 目标状态 |
|--------|----------|
| `new` | `planning`, `cancelled` |
| `planning` | `active`, `paused`, `cancelled` |
| `active` | `awaiting_external`, `awaiting_approval`, `blocked`, `paused`, `escalated`, `completed`, `cancelled` |
| `awaiting_external` | `active`, `awaiting_approval`, `blocked`, `paused`, `escalated`, `completed`, `cancelled` |
| `awaiting_approval` | `active`, `awaiting_external`, `blocked`, `paused`, `escalated`, `completed`, `cancelled` |
| `blocked` | `active`, `paused`, `escalated`, `completed`, `cancelled` |
| `paused` | `active`, `planning`, `cancelled` |
| `escalated` | `active`, `paused`, `completed`, `cancelled` |
| `completed` | - |
| `cancelled` | - |

## 终态

`completed` 和 `cancelled` 是终态，不可再流转。

## API 状态操作

| 操作 | 描述 |
|------|------|
| `POST /threads/{id}/pause` | 暂停线程 |
| `POST /threads/{id}/resume` | 恢复线程 |
| `POST /threads/{id}/takeover` | 接管线程（升级到人工） |
| `POST /threads/{id}/complete` | 完成线程 |
| `POST /threads/{id}/cancel` | 取消线程 |
