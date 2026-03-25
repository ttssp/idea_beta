
# Outbox/Inbox/ExternalBinding 数据库Schema设计

&gt; 文档用途：定义E3核心数据模型的数据库Schema设计

## 1. 设计原则

### 1.1 核心原则
- **幂等优先**: 所有外发操作必须有唯一幂等键
- **Append-Only**: 事件日志采用追加模式
- **可追溯**: 完整的状态变更历史
- **隔离失败**: 外部异常不污染内部状态

---

## 2. ActionRun 表

### 2.1 Schema定义

```sql
CREATE TYPE action_run_status AS ENUM (
    'created',
    'planned',
    'ready_for_approval',
    'approved',
    'executing',
    'sent',
    'acknowledged',
    'failed_retryable',
    'failed_terminal',
    'cancelled'
);

CREATE TYPE action_type AS ENUM (
    'send_email',
    'create_calendar_event',
    'update_calendar_event',
    'cancel_calendar_event',
    'send_followup'
);

CREATE TABLE action_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL,
    action_type action_type NOT NULL,
    status action_run_status NOT NULL DEFAULT 'created',

    -- 幂等控制
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,

    -- 输入输出
    input_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_payload JSONB,

    -- 风险与审批
    risk_decision VARCHAR(50),
    risk_reason TEXT,
    approval_request_id UUID,

    -- 执行元数据
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 5,
    last_error TEXT,
    last_attempted_at TIMESTAMPTZ,

    -- 外部追踪
    external_message_id VARCHAR(255),
    external_thread_id VARCHAR(255),

    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_for TIMESTAMPTZ,
    executed_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_action_runs_thread_id ON action_runs(thread_id);
CREATE INDEX idx_action_runs_status ON action_runs(status);
CREATE INDEX idx_action_runs_scheduled ON action_runs(scheduled_for) WHERE status IN ('approved', 'failed_retryable');
CREATE INDEX idx_action_runs_created_at ON action_runs(created_at DESC);
```

### 2.2 状态历史表

```sql
CREATE TABLE action_run_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_run_id UUID NOT NULL REFERENCES action_runs(id) ON DELETE CASCADE,
    from_status action_run_status,
    to_status action_run_status NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_payload JSONB,
    actor VARCHAR(100),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_action_run_history_action_run_id ON action_run_status_history(action_run_id);
CREATE INDEX idx_action_run_history_occurred_at ON action_run_status_history(occurred_at DESC);
```

---

## 3. OutboxMessage 表

### 3.1 Schema定义

```sql
CREATE TYPE outbox_status AS ENUM (
    'pending',
    'processing',
    'sent',
    'failed',
    'dead_letter'
);

CREATE TYPE channel_type AS ENUM (
    'email',
    'calendar',
    'task',
    'doc'
);

CREATE TABLE outbox_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,

    -- 关联
    thread_id UUID NOT NULL,
    action_run_id UUID NOT NULL REFERENCES action_runs(id),

    -- 渠道与类型
    channel_type channel_type NOT NULL,
    message_type VARCHAR(50) NOT NULL,

    -- 消息内容
    payload JSONB NOT NULL,

    -- 状态与重试
    status outbox_status NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 5,
    last_error TEXT,
    last_attempted_at TIMESTAMPTZ,

    -- 调度
    scheduled_for TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 外部结果
    external_response JSONB,
    external_message_id VARCHAR(255),

    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 索引（关键：按状态+调度时间查询）
CREATE INDEX idx_outbox_status_scheduled ON outbox_messages(status, scheduled_for);
CREATE INDEX idx_outbox_thread_id ON outbox_messages(thread_id);
CREATE INDEX idx_outbox_action_run_id ON outbox_messages(action_run_id);
CREATE INDEX idx_outbox_created_at ON outbox_messages(created_at DESC);

-- 触发函数：自动更新updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_outbox_updated_at BEFORE UPDATE ON outbox_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3.2 死信表

```sql
CREATE TABLE outbox_dead_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_outbox_id UUID NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL,
    thread_id UUID NOT NULL,
    action_run_id UUID NOT NULL,
    channel_type channel_type NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    last_error TEXT,
    retry_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    original_created_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT
);

CREATE INDEX idx_dead_letters_created_at ON outbox_dead_letters(created_at DESC);
```

---

## 4. InboxEvent 表

### 4.1 Schema定义

```sql
CREATE TYPE inbox_status AS ENUM (
    'pending',
    'processing',
    'processed',
    'failed',
    'ignored'
);

CREATE TABLE inbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,

    -- 渠道信息
    channel_type channel_type NOT NULL,
    event_type VARCHAR(50) NOT NULL,

    -- 外部标识符
    external_thread_key VARCHAR(255),
    external_message_key VARCHAR(255) UNIQUE,

    -- 事件内容
    payload JSONB NOT NULL,
    raw_payload BYTEA,

    -- 处理状态
    status inbox_status NOT NULL DEFAULT 'pending',
    resolved_thread_id UUID,
    error_message TEXT,

    -- Webhook元数据
    webhook_signature VARCHAR(255),
    webhook_timestamp TIMESTAMPTZ,

    -- 时间戳
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_inbox_external_keys ON inbox_events(external_thread_key, external_message_key);
CREATE INDEX idx_inbox_status ON inbox_events(status);
CREATE INDEX idx_inbox_received_at ON inbox_events(received_at DESC);
CREATE INDEX idx_inbox_resolved_thread ON inbox_events(resolved_thread_id) WHERE resolved_thread_id IS NOT NULL;

CREATE TRIGGER update_inbox_updated_at BEFORE UPDATE ON inbox_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 5. ExternalBinding 表

### 5.1 Schema定义

```sql
CREATE TYPE binding_type AS ENUM (
    'primary',
    'reply',
    'related'
);

CREATE TYPE sync_state AS ENUM (
    'active',
    'paused',
    'archived'
);

CREATE TABLE external_bindings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL,

    -- 渠道与外部标识
    channel_type channel_type NOT NULL,
    external_thread_key VARCHAR(255) NOT NULL,
    external_message_key VARCHAR(255),  -- 初始消息的外部ID

    -- 绑定类型
    binding_type binding_type NOT NULL DEFAULT 'primary',

    -- 同步状态
    sync_state sync_state NOT NULL DEFAULT 'active',
    sync_token VARCHAR(255),  -- Google Calendar syncToken等
    last_synced_at TIMESTAMPTZ,

    -- 元数据
    metadata JSONB DEFAULT '{}'::jsonb,

    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 唯一约束：同一渠道的external_thread_key只能绑定一次
    UNIQUE(channel_type, external_thread_key)
);

-- 索引
CREATE INDEX idx_external_binding_thread_id ON external_bindings(thread_id);
CREATE INDEX idx_external_binding_channel ON external_bindings(channel_type, external_thread_key);
CREATE INDEX idx_external_binding_sync_state ON external_bindings(sync_state);

CREATE TRIGGER update_external_binding_updated_at BEFORE UPDATE ON external_bindings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 6. UserOAuthCredentials 表

### 6.1 Schema定义

```sql
CREATE TABLE user_oauth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- 'gmail', 'outlook', 'google_calendar', 'outlook_calendar'
    provider_user_id VARCHAR(255) NOT NULL,

    -- Token（加密存储）
    access_token_encrypted BYTEA NOT NULL,
    refresh_token_encrypted BYTEA,
    expires_at TIMESTAMPTZ NOT NULL,
    scopes TEXT[] NOT NULL,

    -- 状态
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    last_refreshed_at TIMESTAMPTZ,

    -- 元数据
    metadata JSONB DEFAULT '{}'::jsonb,

    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 唯一约束：每个用户每个provider只有一个有效token
    UNIQUE(user_id, provider)
);

CREATE INDEX idx_oauth_user_provider ON user_oauth_credentials(user_id, provider);
CREATE INDEX idx_oauth_expires_at ON user_oauth_credentials(expires_at);
CREATE INDEX idx_oauth_is_valid ON user_oauth_credentials(is_valid);

CREATE TRIGGER update_oauth_updated_at BEFORE UPDATE ON user_oauth_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 7. 查询优化

### 7.1 关键查询模式

**Outbox调度查询（高频）:**
```sql
SELECT id FROM outbox_messages
WHERE status = 'pending'
  AND scheduled_for &lt;= NOW()
ORDER BY scheduled_for ASC
LIMIT 100 FOR UPDATE SKIP LOCKED;
```

**ExternalBinding查找（高频）:**
```sql
SELECT thread_id FROM external_bindings
WHERE channel_type = $1
  AND external_thread_key = $2
  AND sync_state = 'active';
```

**ActionRun状态查询:**
```sql
SELECT * FROM action_runs
WHERE thread_id = $1
ORDER BY created_at DESC;
```

### 7.2 分区策略（可选，Phase 3）

对于大规模部署，考虑按时间分区：

```sql
-- 按月分区（示例）
CREATE TABLE outbox_messages_partitioned (
    ... 同上 ...
) PARTITION BY RANGE (created_at);

CREATE TABLE outbox_messages_2024_01 PARTITION OF outbox_messages_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

---

## 8. 数据库迁移顺序

| 版本 | 迁移内容 | 依赖 |
|------|----------|------|
| 001 | 创建ENUM类型 | - |
| 002 | 创建action_runs表 | 001 |
| 003 | 创建action_run_status_history表 | 002 |
| 004 | 创建outbox_messages表 | 001 |
| 005 | 创建outbox_dead_letters表 | 004 |
| 006 | 创建inbox_events表 | 001 |
| 007 | 创建external_bindings表 | 001 |
| 008 | 创建user_oauth_credentials表 | - |
| 009 | 创建索引和触发器 | 002-008 |

