
"""
ActionRun Database Models
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from datetime import datetime
from uuid import UUID, uuid4

from ..core.database import Base


# 枚举类型定义
ActionRunStatusEnum = ENUM(
    'created',
    'planned',
    'ready_for_approval',
    'approved',
    'executing',
    'sent',
    'acknowledged',
    'failed_retryable',
    'failed_terminal',
    'cancelled',
    name='action_run_status',
    create_type=True
)

ActionTypeEnum = ENUM(
    'send_email',
    'create_calendar_event',
    'update_calendar_event',
    'cancel_calendar_event',
    'send_followup',
    name='action_type',
    create_type=True
)


class ActionRun(Base):
    """ActionRun - 动作执行记录"""

    __tablename__ = 'action_runs'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    thread_id = sa.Column(sa.UUID(as_uuid=True), nullable=False, index=True)
    action_type = sa.Column(ActionTypeEnum, nullable=False, index=True)
    status = sa.Column(ActionRunStatusEnum, nullable=False, default='created', index=True)

    # 幂等控制
    idempotency_key = sa.Column(sa.String(255), unique=True, nullable=False, index=True)

    # 输入输出
    input_payload = sa.Column(JSONB, nullable=False, default=dict)
    output_payload = sa.Column(JSONB)

    # 风险与审批
    risk_decision = sa.Column(sa.String(50))
    risk_reason = sa.Column(sa.Text)
    approval_request_id = sa.Column(sa.UUID(as_uuid=True), index=True)

    # 执行元数据
    retry_count = sa.Column(sa.Integer, nullable=False, default=0)
    max_retries = sa.Column(sa.Integer, nullable=False, default=5)
    last_error = sa.Column(sa.Text)
    last_attempted_at = sa.Column(sa.TIMESTAMP(timezone=True))

    # 外部追踪
    external_message_id = sa.Column(sa.String(255))
    external_thread_id = sa.Column(sa.String(255))

    # 时间戳
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_for = sa.Column(sa.TIMESTAMP(timezone=True), index=True)
    executed_at = sa.Column(sa.TIMESTAMP(timezone=True))

    __table_args__ = (
        sa.Index('idx_action_runs_scheduled', 'scheduled_for',
                 postgresql_where=sa.text("status IN ('approved', 'failed_retryable')")),
        sa.Index('idx_action_runs_created_desc', created_at.desc()),
    )


class ActionRunStatusHistory(Base):
    """ActionRun状态变更历史"""

    __tablename__ = 'action_run_status_history'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    action_run_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('action_runs.id', ondelete='CASCADE'), nullable=False, index=True)
    from_status = sa.Column(ActionRunStatusEnum)
    to_status = sa.Column(ActionRunStatusEnum, nullable=False)
    event_type = sa.Column(sa.String(50), nullable=False)
    event_payload = sa.Column(JSONB)
    actor = sa.Column(sa.String(100))
    occurred_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)

