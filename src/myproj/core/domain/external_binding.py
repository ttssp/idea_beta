"""ExternalBinding 领域模型 - 外部渠道映射"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from myproj.core.domain.message import MessageId
from myproj.core.domain.thread import ThreadId

# ============================================
# 值对象 (Value Objects)
# ============================================

class BindingId(BaseModel):
    """Binding ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "BindingId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BindingId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class ChannelType(str, Enum):
    """外部渠道类型"""
    EMAIL = "email"
    CALENDAR = "calendar"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    CUSTOM = "custom"


class SyncState(str, Enum):
    """同步状态"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    OUT_OF_SYNC = "out_of_sync"


# ============================================
# ExternalBinding 实体
# ============================================

class ExternalBinding(BaseModel):
    """外部绑定实体 - 解决线程关联与去重"""
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: BindingId = Field(default_factory=BindingId.generate)

    # 所属线程
    thread_id: ThreadId

    # 渠道信息
    channel: ChannelType
    channel_account_id: str | None = Field(None, max_length=255)

    # 外部线程/消息标识
    external_thread_key: str | None = Field(None, max_length=500)
    external_message_key: str | None = Field(None, max_length=500)

    # 关联的消息
    message_id: MessageId | None = None

    # 同步状态
    sync_state: SyncState = SyncState.PENDING
    last_synced_at: datetime | None = None
    sync_error: str | None = Field(None, max_length=1000)

    # 方向
    is_inbound: bool = False
    is_outbound: bool = True

    # 元数据
    is_active: bool = True
    is_primary: bool = False
    sync_direction: str = Field(default="bidirectional", max_length=50)  # inbound, outbound, bidirectional

    # 外部数据快照
    external_metadata: dict[str, Any] = Field(default_factory=dict)
    external_subject: str | None = Field(None, max_length=500)
    external_sender: str | None = Field(None, max_length=500)
    external_recipients: list[str] = Field(default_factory=list)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    external_created_at: datetime | None = None
    external_updated_at: datetime | None = None

    # 乐观锁
    version: int = 1

    # 扩展数据
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_email_binding(
        cls,
        thread_id: ThreadId,
        external_thread_key: str,
        external_message_key: str | None = None,
        message_id: MessageId | None = None,
        is_inbound: bool = False,
    ) -> "ExternalBinding":
        """创建Email绑定"""
        return cls(
            thread_id=thread_id,
            channel=ChannelType.EMAIL,
            external_thread_key=external_thread_key,
            external_message_key=external_message_key,
            message_id=message_id,
            is_inbound=is_inbound,
            is_outbound=not is_inbound,
        )

    @classmethod
    def create_calendar_binding(
        cls,
        thread_id: ThreadId,
        external_thread_key: str,
        external_message_key: str | None = None,
        message_id: MessageId | None = None,
    ) -> "ExternalBinding":
        """创建Calendar绑定"""
        return cls(
            thread_id=thread_id,
            channel=ChannelType.CALENDAR,
            external_thread_key=external_thread_key,
            external_message_key=external_message_key,
            message_id=message_id,
            is_inbound=False,
            is_outbound=True,
        )

    @property
    def is_email(self) -> bool:
        return self.channel == ChannelType.EMAIL

    @property
    def is_calendar(self) -> bool:
        return self.channel == ChannelType.CALENDAR

    @property
    def is_synced(self) -> bool:
        return self.sync_state == SyncState.SYNCED

    @property
    def needs_sync(self) -> bool:
        return self.sync_state in {SyncState.PENDING, SyncState.OUT_OF_SYNC, SyncState.FAILED}

    def mark_syncing(self) -> None:
        """标记为同步中"""
        self.sync_state = SyncState.SYNCING
        self.updated_at = datetime.utcnow()

    def mark_synced(self, external_updated_at: datetime | None = None) -> None:
        """标记为已同步"""
        self.sync_state = SyncState.SYNCED
        self.last_synced_at = datetime.utcnow()
        self.external_updated_at = external_updated_at
        self.sync_error = None
        self.updated_at = datetime.utcnow()

    def mark_sync_failed(self, error: str) -> None:
        """标记为同步失败"""
        self.sync_state = SyncState.FAILED
        self.sync_error = error[:1000]
        self.updated_at = datetime.utcnow()

    def mark_out_of_sync(self) -> None:
        """标记为不同步"""
        self.sync_state = SyncState.OUT_OF_SYNC
        self.updated_at = datetime.utcnow()

    def update_external_subject(self, subject: str) -> None:
        """更新外部主题"""
        self.external_subject = subject[:500]
        self.updated_at = datetime.utcnow()

    def update_external_sender(self, sender: str) -> None:
        """更新外部发送者"""
        self.external_sender = sender[:500]
        self.updated_at = datetime.utcnow()

    def add_external_recipient(self, recipient: str) -> None:
        """添加外部收件人"""
        if recipient not in self.external_recipients:
            self.external_recipients.append(recipient)
            self.updated_at = datetime.utcnow()

    def update_external_metadata(self, metadata: dict[str, Any]) -> None:
        """更新外部元数据"""
        self.external_metadata.update(metadata)
        self.updated_at = datetime.utcnow()

    def set_primary(self) -> None:
        """设置为主绑定"""
        self.is_primary = True
        self.updated_at = datetime.utcnow()

    def unset_primary(self) -> None:
        """取消主绑定"""
        self.is_primary = False
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """停用绑定"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """启用绑定"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def increment_version(self) -> None:
        """版本号递增"""
        self.version += 1
