# ER 图 - 核心对象模型

## 核心实体关系

```
┌─────────────┐         ┌─────────────┐
│  Principal  │         │  Principal  │
│  (from)     │◄────────┤   (to)      │
└──────┬──────┘         └──────┬──────┘
       │                         │
       │ 1                     1 │
       │                         │
       ▼                         ▼
┌───────────────────────────────────────┐
│          Relationship                  │
│  - relationship_class                  │
│  - sensitivity                         │
│  - default_delegation_profile          │
└───────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│                      Thread                        │
│  - id (PK)                                         │
│  - objective_title                                 │
│  - status (enum)                                   │
│  - risk_level (enum)                               │
│  - owner_id (FK → Principal)                      │
│  - responsible_principal_id (FK → Principal)      │
│  - participant_ids (JSON)                          │
│  - summary                                          │
│  - delegation_profile (JSON)                       │
└────────────────────────────────────────────────────┘
         │
         │ 1
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         │ N                │ N                │ N
         ▼                  ▼                  ▼
    ┌─────────┐       ┌─────────┐      ┌─────────────────┐
    │ Message │       │  Event  │      │ ExternalBinding │
    └─────────┘       └─────────┘      └─────────────────┘
```

## 实体详情

### Thread（线程）
- 系统一等公民
- 所有其他实体都围绕Thread组织
- 状态机驱动

### Principal（主体）
- 统一身份模型：human/agent/external/service
- 信任等级：trusted/known/unknown/blocked

### Relationship（关系）
- 表达"我如何看待这个对象"
- 5种关系类别：internal_colleague/external_candidate/customer/vendor/sensitive_personal
- 敏感度等级：low/medium/high/critical

### Message（消息）
- 4种创作模式
- 支持draft/sent/read状态
- 幂等发送支持

### ThreadEvent（事件）
- append-only
- 按thread + sequence_number排序
- 用于回放和审计

### ExternalBinding（外部绑定）
- 外部渠道映射：email/calendar等
- 去重和同步支持
