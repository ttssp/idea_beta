
"""
Outbox/Inbox Database Models
"""

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from ..core.database import Base

# 枚举类型定义
OutboxStatusEnum = ENUM(
    'pending',
    'processing',
    'sent',
    'failed',
    'dead_letter',
    name='outbox_status',
    create_type=True
)

InboxStatusEnum = ENUM(
    'pending',
    'processing',
    'processed',
    'failed',
    'ignored',
    name='inbox_status',
    create_type=True
)

ChannelTypeEnum = ENUM(
    'email',
    'calendar',
    'task',
    'doc',
    name='channel_type',
    create_type=True
)

BindingTypeEnum = ENUM(
    'primary',
    'reply',
    'related',
    name='binding_type',
    create_type=True
)

SyncStateEnum = ENUM(
    'active',
    'paused',
    'archived',
    name='sync_state',
    create_type=True
)


class OutboxMessage(Base):
    """OutboxMessage - 外发消息排队表"""

    __tablename__ = 'outbox_messages'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    idempotency_key = sa.Column(sa.String(255), unique=True, nullable=False, index=True)

    # 关联
    thread_id = sa.Column(sa.UUID(as_uuid=True), nullable=False, index=True)
    action_run_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('action_runs.id'), nullable=False, index=True)

    # 渠道与类型
    channel_type = sa.Column(ChannelTypeEnum, nullable=False)
    message_type = sa.Column(sa.String(50), nullable=False)

    # 消息内容
    payload = sa.Column(JSONB, nullable=False)

    # 状态与重试
    status = sa.Column(OutboxStatusEnum, nullable=False, default='pending', index=True)
    retry_count = sa.Column(sa.Integer, nullable=False, default=0)
    max_retries = sa.Column(sa.Integer, nullable=False, default=5)
    last_error = sa.Column(sa.Text)
    last_attempted_at = sa.Column(sa.TIMESTAMP(timezone=True))

    # 调度
    scheduled_for = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # 外部结果
    external_response = sa.Column(JSONB)
    external_message_id = sa.Column(sa.String(255))

    # 时间戳
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        sa.Index('idx_outbox_status_scheduled', 'status', 'scheduled_for'),
    )


class OutboxDeadLetter(Base):
    """OutboxDeadLetter - 死信表"""

    __tablename__ = 'outbox_dead_letters'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    original_outbox_id = sa.Column(sa.UUID(as_uuid=True), nullable=False)
    idempotency_key = sa.Column(sa.String(255), nullable=False, index=True)
    thread_id = sa.Column(sa.UUID(as_uuid=True), nullable=False, index=True)
    action_run_id = sa.Column(sa.UUID(as_uuid=True), nullable=False)
    channel_type = sa.Column(ChannelTypeEnum, nullable=False)
    message_type = sa.Column(sa.String(50), nullable=False)
    payload = sa.Column(JSONB, nullable=False)
    last_error = sa.Column(sa.Text)
    retry_count = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    original_created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    resolved_at = sa.Column(sa.TIMESTAMP(timezone=True))
    resolution_notes = sa.Column(sa.Text)


class InboxEvent(Base):
    """InboxEvent - 接收事件表"""

    __tablename__ = 'inbox_events'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    idempotency_key = sa.Column(sa.String(255), unique=True, nullable=False, index=True)

    # 渠道信息
    channel_type = sa.Column(ChannelTypeEnum, nullable=False)
    event_type = sa.Column(sa.String(50), nullable=False)

    # 外部标识符
    external_thread_key = sa.Column(sa.String(255), index=True)
    external_message_key = sa.Column(sa.String(255), unique=True, index=True)

    # 事件内容
    payload = sa.Column(JSONB, nullable=False)
    raw_payload = sa.Column(sa.LargeBinary)

    # 处理状态
    status = sa.Column(InboxStatusEnum, nullable=False, default='pending', index=True)
    resolved_thread_id = sa.Column(sa.UUID(as_uuid=True), index=True)
    error_message = sa.Column(sa.Text)

    # Webhook元数据
    webhook_signature = sa.Column(sa.String(255))
    webhook_timestamp = sa.Column(sa.TIMESTAMP(timezone=True))

    # 时间戳
    received_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    processed_at = sa.Column(sa.TIMESTAMP(timezone=True))
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExternalBinding(Base):
    """ExternalBinding - 外部线程映射表"""

    __tablename__ = 'external_bindings'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    thread_id = sa.Column(sa.UUID(as_uuid=True), nullable=False, index=True)

    # 渠道与外部标识
    channel_type = sa.Column(ChannelTypeEnum, nullable=False)
    external_thread_key = sa.Column(sa.String(255), nullable=False)
    external_message_key = sa.Column(sa.String(255))

    # 绑定类型
    binding_type = sa.Column(BindingTypeEnum, nullable=False, default='primary')

    # 同步状态
    sync_state = sa.Column(SyncStateEnum, nullable=False, default='active', index=True)
    sync_token = sa.Column(sa.String(255))
    last_synced_at = sa.Column(sa.TIMESTAMP(timezone=True))

    # 元数据
    metadata = sa.Column(JSONB, nullable=False, default=dict)

    # 时间戳
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        sa.UniqueConstraint('channel_type', 'external_thread_key', name='uix_channel_external_thread'),
        sa.Index('idx_external_binding_channel', 'channel_type', 'external_thread_key'),
    )

