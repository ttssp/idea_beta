"""ThreadEvent 领域模型 - 事件流"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import ThreadId, ThreadStatus

# ============================================
# 值对象 (Value Objects)
# ============================================

class EventId(BaseModel):
    """Event ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "EventId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EventId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class EventType(StrEnum):
    """事件类型"""
    # Thread生命周期
    THREAD_CREATED = "thread_created"
    THREAD_UPDATED = "thread_updated"
    THREAD_STATUS_CHANGED = "thread_status_changed"
    THREAD_PAUSED = "thread_paused"
    THREAD_RESUMED = "thread_resumed"
    THREAD_ESCALATED = "thread_escalated"
    THREAD_COMPLETED = "thread_completed"
    THREAD_CANCELLED = "thread_cancelled"
    THREAD_TAKEOVER = "thread_takeover"

    # 消息相关
    MESSAGE_CREATED = "message_created"
    MESSAGE_SENT = "message_sent"
    MESSAGE_READ = "message_read"
    MESSAGE_APPROVED = "message_approved"
    MESSAGE_REJECTED = "message_rejected"

    # 参与者
    PARTICIPANT_ADDED = "participant_added"
    PARTICIPANT_REMOVED = "participant_removed"
    RESPONSIBLE_CHANGED = "responsible_changed"

    # 目标与摘要
    OBJECTIVE_UPDATED = "objective_updated"
    SUMMARY_UPDATED = "summary_updated"

    # 委托与策略
    DELEGATION_PROFILE_CHANGED = "delegation_profile_changed"
    POLICY_HIT = "policy_hit"

    # 风控
    RISK_DETECTED = "risk_detected"
    RISK_LEVEL_CHANGED = "risk_level_changed"

    # 审批
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    APPROVAL_MODIFIED = "approval_modified"

    # 外部集成
    EXTERNAL_MESSAGE_RECEIVED = "external_message_received"
    EXTERNAL_SYNC_COMPLETED = "external_sync_completed"
    EXTERNAL_SYNC_FAILED = "external_sync_failed"

    # 动作执行
    ACTION_PLANNED = "action_planned"
    ACTION_EXECUTED = "action_executed"
    ACTION_FAILED = "action_failed"
    ACTION_CANCELLED = "action_cancelled"

    # AI相关
    AI_DRAFT_GENERATED = "ai_draft_generated"
    AI_SUGGESTION_PROVIDED = "ai_suggestion_provided"
    AI_PLAN_GENERATED = "ai_plan_generated"

    # 系统
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"


# ============================================
# ThreadEvent 实体
# ============================================

class ThreadEvent(BaseModel):
    """线程事件实体 - append-only event log"""
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: EventId = Field(default_factory=EventId.generate)

    # 所属线程
    thread_id: ThreadId

    # 事件元数据
    event_type: EventType
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    # 事件顺序（用于保证顺序）
    sequence_number: int = 0

    # 执行者
    actor_principal_id: PrincipalId | None = None
    actor_type: str | None = Field(None, max_length=50)

    # 因果关系
    causal_event_id: EventId | None = None
    causal_ref: str | None = Field(None, max_length=255)

    # 事件内容
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=2000)

    # 结构化数据
    payload: dict[str, Any] = Field(default_factory=dict)

    # 状态快照（可选，用于回放）
    thread_status_before: ThreadStatus | None = None
    thread_status_after: ThreadStatus | None = None

    # 幂等性
    idempotency_key: str | None = Field(None, max_length=255)

    # 元数据
    is_replayed: bool = False
    is_visible: bool = True

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def create_thread_created(
        cls,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
        objective: str | None = None,
    ) -> "ThreadEvent":
        """创建线程创建事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.THREAD_CREATED,
            actor_principal_id=actor_id,
            title="Thread created",
            description=objective,
            payload={"objective": objective} if objective else {},
        )

    @classmethod
    def create_status_changed(
        cls,
        thread_id: ThreadId,
        from_status: ThreadStatus,
        to_status: ThreadStatus,
        actor_id: PrincipalId | None = None,
        reason: str | None = None,
    ) -> "ThreadEvent":
        """创建状态变更事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.THREAD_STATUS_CHANGED,
            actor_principal_id=actor_id,
            title=f"Status changed: {from_status} → {to_status}",
            description=reason,
            payload={
                "from_status": from_status.value,
                "to_status": to_status.value,
                "reason": reason,
            },
            thread_status_before=from_status,
            thread_status_after=to_status,
        )

    @classmethod
    def create_message_sent(
        cls,
        thread_id: ThreadId,
        message_id: UUID,
        actor_id: PrincipalId | None = None,
        authored_mode: str | None = None,
    ) -> "ThreadEvent":
        """创建消息发送事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.MESSAGE_SENT,
            actor_principal_id=actor_id,
            title="Message sent",
            payload={
                "message_id": str(message_id),
                "authored_mode": authored_mode,
            },
        )

    @classmethod
    def create_escalated(
        cls,
        thread_id: ThreadId,
        reason: str,
        actor_id: PrincipalId | None = None,
    ) -> "ThreadEvent":
        """创建升级事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.THREAD_ESCALATED,
            actor_principal_id=actor_id,
            title="Thread escalated to human",
            description=reason,
            payload={"reason": reason},
        )

    @classmethod
    def create_policy_hit(
        cls,
        thread_id: ThreadId,
        policy_id: str,
        policy_name: str,
        decision: str,
        actor_id: PrincipalId | None = None,
    ) -> "ThreadEvent":
        """创建策略命中事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.POLICY_HIT,
            actor_principal_id=actor_id,
            title=f"Policy hit: {policy_name}",
            payload={
                "policy_id": policy_id,
                "policy_name": policy_name,
                "decision": decision,
            },
        )

    @classmethod
    def create_risk_detected(
        cls,
        thread_id: ThreadId,
        risk_level: str,
        risk_reason: str,
        actor_id: PrincipalId | None = None,
    ) -> "ThreadEvent":
        """创建风险检测事件"""
        return cls(
            thread_id=thread_id,
            event_type=EventType.RISK_DETECTED,
            actor_principal_id=actor_id,
            title=f"Risk detected: {risk_level}",
            description=risk_reason,
            payload={
                "risk_level": risk_level,
                "risk_reason": risk_reason,
            },
        )

    @property
    def is_status_change(self) -> bool:
        return self.event_type == EventType.THREAD_STATUS_CHANGED

    @property
    def is_message_event(self) -> bool:
        return self.event_type.value.startswith("message_")

    @property
    def is_approval_event(self) -> bool:
        return self.event_type.value.startswith("approval_")

    @property
    def is_action_event(self) -> bool:
        return self.event_type.value.startswith("action_")

    def set_sequence_number(self, number: int) -> None:
        """设置序列号"""
        self.sequence_number = number

    def set_idempotency_key(self, key: str) -> None:
        """设置幂等键"""
        self.idempotency_key = key[:255]

    def mark_as_replayed(self) -> None:
        """标记为回放事件"""
        self.is_replayed = True

    def hide(self) -> None:
        """隐藏事件"""
        self.is_visible = False
