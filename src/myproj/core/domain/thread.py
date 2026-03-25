"""Thread 领域模型 - 系统一等公民"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

# ============================================
# 值对象 (Value Objects)
# ============================================

class ThreadId(BaseModel):
    """Thread ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "ThreadId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ThreadId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class ThreadStatus(str, Enum):
    """Thread 状态枚举 - 10种状态"""
    NEW = "new"
    PLANNING = "planning"
    ACTIVE = "active"
    AWAITING_EXTERNAL = "awaiting_external"
    AWAITING_APPROVAL = "awaiting_approval"
    BLOCKED = "blocked"
    PAUSED = "paused"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def is_terminal(cls, status: "ThreadStatus") -> bool:
        """判断是否为终态"""
        return status in {cls.COMPLETED, cls.CANCELLED}


class DelegationLevel(str, Enum):
    """委托档位"""
    OBSERVE_ONLY = "observe_only"
    DRAFT_FIRST = "draft_first"
    APPROVE_TO_SEND = "approve_to_send"
    BOUNDED_AUTO = "bounded_auto"
    HUMAN_ONLY = "human_only"


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreadObjective(BaseModel):
    """Thread 目标值对象"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    due_at: datetime | None = None

    def __str__(self) -> str:
        return self.title


class DelegationProfile(BaseModel):
    """委托档位值对象 - 产品层主抽象"""
    profile_name: str = Field(..., min_length=1, max_length=100)
    level: DelegationLevel = DelegationLevel.OBSERVE_ONLY

    # 动作预算
    max_actions_per_hour: int = 10
    max_messages_per_thread: int = 50
    max_consecutive_touches: int = 3

    # 允许的动作类型
    allowed_actions: list[str] = Field(default_factory=list)

    # 升级规则
    escalation_rules: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def default_observe(cls) -> "DelegationProfile":
        return cls(
            profile_name="Default - Observe Only",
            level=DelegationLevel.OBSERVE_ONLY,
        )

    @classmethod
    def default_draft(cls) -> "DelegationProfile":
        return cls(
            profile_name="Default - Draft First",
            level=DelegationLevel.DRAFT_FIRST,
        )

    @classmethod
    def default_approve(cls) -> "DelegationProfile":
        return cls(
            profile_name="Default - Approve to Send",
            level=DelegationLevel.APPROVE_TO_SEND,
        )


# ============================================
# 状态机流转规则
# ============================================

VALID_TRANSITIONS: dict[ThreadStatus, set[ThreadStatus]] = {
    ThreadStatus.NEW: {
        ThreadStatus.PLANNING,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.PLANNING: {
        ThreadStatus.ACTIVE,
        ThreadStatus.PAUSED,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.ACTIVE: {
        ThreadStatus.AWAITING_EXTERNAL,
        ThreadStatus.AWAITING_APPROVAL,
        ThreadStatus.BLOCKED,
        ThreadStatus.PAUSED,
        ThreadStatus.ESCALATED,
        ThreadStatus.COMPLETED,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.AWAITING_EXTERNAL: {
        ThreadStatus.ACTIVE,
        ThreadStatus.AWAITING_APPROVAL,
        ThreadStatus.BLOCKED,
        ThreadStatus.PAUSED,
        ThreadStatus.ESCALATED,
        ThreadStatus.COMPLETED,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.AWAITING_APPROVAL: {
        ThreadStatus.ACTIVE,
        ThreadStatus.AWAITING_EXTERNAL,
        ThreadStatus.BLOCKED,
        ThreadStatus.PAUSED,
        ThreadStatus.ESCALATED,
        ThreadStatus.COMPLETED,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.BLOCKED: {
        ThreadStatus.ACTIVE,
        ThreadStatus.PAUSED,
        ThreadStatus.ESCALATED,
        ThreadStatus.COMPLETED,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.PAUSED: {
        ThreadStatus.ACTIVE,
        ThreadStatus.PLANNING,
        ThreadStatus.CANCELLED,
    },
    ThreadStatus.ESCALATED: {
        ThreadStatus.ACTIVE,
        ThreadStatus.PAUSED,
        ThreadStatus.COMPLETED,
        ThreadStatus.CANCELLED,
    },
    # 终态不可流转
    ThreadStatus.COMPLETED: set(),
    ThreadStatus.CANCELLED: set(),
}


def can_transition(from_status: ThreadStatus, to_status: ThreadStatus) -> bool:
    """检查状态流转是否合法"""
    return to_status in VALID_TRANSITIONS.get(from_status, set())


# ============================================
# Thread 实体 (Aggregate Root)
# ============================================

class Thread(BaseModel):
    """Thread 聚合根 - 系统一等公民"""
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: ThreadId = Field(default_factory=ThreadId.generate)

    # 核心属性
    objective: ThreadObjective
    status: ThreadStatus = ThreadStatus.NEW
    risk_level: RiskLevel = RiskLevel.LOW

    # 委托配置
    delegation_profile: DelegationProfile = Field(default_factory=DelegationProfile.default_observe)

    # 责任人与参与者
    owner_id: UUID
    responsible_principal_id: UUID | None = None
    participant_ids: list[UUID] = Field(default_factory=list)

    # 摘要与元数据
    summary: str | None = Field(None, max_length=500)
    current_step: str | None = Field(None, max_length=500)
    tags: list[str] = Field(default_factory=list)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    last_escalated_at: datetime | None = None
    last_escalation_reason: str | None = None

    # 乐观锁
    version: int = 1

    # 上下文数据
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, v: datetime, info: Any) -> datetime:
        if "created_at" in info.data and v < info.data["created_at"]:
            raise ValueError("updated_at cannot be before created_at")
        return v

    @model_validator(mode="after")
    def set_default_responsible(self) -> "Thread":
        """设置默认责任方为owner"""
        if self.responsible_principal_id is None:
            self.responsible_principal_id = self.owner_id
        return self

    @property
    def is_terminal(self) -> bool:
        """是否为终态"""
        return ThreadStatus.is_terminal(self.status)

    @property
    def can_be_paused(self) -> bool:
        """是否可以暂停"""
        return self.status in {
            ThreadStatus.ACTIVE,
            ThreadStatus.AWAITING_EXTERNAL,
            ThreadStatus.AWAITING_APPROVAL,
            ThreadStatus.BLOCKED,
        }

    @property
    def can_be_resumed(self) -> bool:
        """是否可以恢复"""
        return self.status == ThreadStatus.PAUSED

    @property
    def needs_approval(self) -> bool:
        """是否需要审批"""
        return self.status == ThreadStatus.AWAITING_APPROVAL

    def transition_to(self, new_status: ThreadStatus) -> None:
        """状态流转"""
        if self.is_terminal:
            raise ValueError(f"Cannot transition from terminal status: {self.status}")

        if not can_transition(self.status, new_status):
            raise ValueError(f"Invalid transition: {self.status} -> {new_status}")

        self.status = new_status
        self._mark_updated()

        if new_status == ThreadStatus.COMPLETED:
            self.completed_at = datetime.utcnow()

    def pause(self) -> None:
        """暂停线程"""
        if not self.can_be_paused:
            raise ValueError(f"Cannot pause thread in status: {self.status}")
        self.transition_to(ThreadStatus.PAUSED)

    def resume(self) -> None:
        """恢复线程"""
        if not self.can_be_resumed:
            raise ValueError(f"Cannot resume thread in status: {self.status}")
        self.transition_to(ThreadStatus.ACTIVE)

    def escalate(self, reason: str) -> None:
        """升级到人工"""
        if self.is_terminal:
            raise ValueError("Cannot escalate terminal thread")
        self.transition_to(ThreadStatus.ESCALATED)
        self.last_escalated_at = datetime.utcnow()
        self.last_escalation_reason = reason

    def complete(self) -> None:
        """完成线程"""
        if self.is_terminal:
            raise ValueError("Thread is already terminal")
        self.transition_to(ThreadStatus.COMPLETED)

    def cancel(self) -> None:
        """取消线程"""
        if self.is_terminal:
            raise ValueError("Thread is already terminal")
        self.transition_to(ThreadStatus.CANCELLED)

    def update_summary(self, summary: str) -> None:
        """更新摘要"""
        self.summary = summary[:500]
        self._mark_updated()

    def update_objective(self, objective: ThreadObjective) -> None:
        """更新目标信息"""
        self.objective = objective
        self._mark_updated()

    def set_risk_level(self, risk_level: RiskLevel) -> None:
        """更新风险等级"""
        self.risk_level = risk_level
        self._mark_updated()

    def set_delegation_profile(self, profile: DelegationProfile) -> None:
        """更新委托档位"""
        self.delegation_profile = profile
        self._mark_updated()

    def set_responsible(self, principal_id: UUID) -> None:
        """设置责任方"""
        self.responsible_principal_id = principal_id
        self._mark_updated()

    def add_participant(self, principal_id: UUID) -> None:
        """添加参与者"""
        if principal_id not in self.participant_ids:
            self.participant_ids.append(principal_id)
            self._mark_updated()

    def remove_participant(self, principal_id: UUID) -> None:
        """移除参与者"""
        if principal_id in self.participant_ids:
            self.participant_ids.remove(principal_id)
            self._mark_updated()

    def increment_version(self) -> None:
        """版本号递增（乐观锁）"""
        self.version += 1

    def _mark_updated(self) -> None:
        """统一维护更新时间和乐观锁版本。"""
        self.updated_at = datetime.utcnow()
        self.increment_version()
