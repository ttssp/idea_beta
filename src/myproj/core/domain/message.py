"""Message 领域模型 - 消息对象"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import ThreadId

# ============================================
# 值对象 (Value Objects)
# ============================================

class MessageId(BaseModel):
    """Message ID 值对象"""
    value: UUID

    @classmethod
    def generate(cls) -> "MessageId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MessageId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class AuthoredMode(str, Enum):
    """消息创作/发送模式 - 4种模式"""
    HUMAN_AUTHORED_HUMAN_SENT = "human_authored_human_sent"
    AGENT_DRAFTED_HUMAN_SENT = "agent_drafted_human_sent"
    AGENT_DRAFTED_HUMAN_APPROVED_SENT = "agent_drafted_human_approved_sent"
    AGENT_SENT_WITHIN_POLICY = "agent_sent_within_policy"

    @property
    def is_human_authored(self) -> bool:
        return self == self.HUMAN_AUTHORED_HUMAN_SENT

    @property
    def is_agent_drafted(self) -> bool:
        return self in {
            self.AGENT_DRAFTED_HUMAN_SENT,
            self.AGENT_DRAFTED_HUMAN_APPROVED_SENT,
            self.AGENT_SENT_WITHIN_POLICY,
        }

    @property
    def requires_approval(self) -> bool:
        return self in {
            self.HUMAN_AUTHORED_HUMAN_SENT,
            self.AGENT_DRAFTED_HUMAN_SENT,
            self.AGENT_DRAFTED_HUMAN_APPROVED_SENT,
        }


class ChannelType(str, Enum):
    """渠道类型"""
    INTERNAL = "internal"
    EMAIL = "email"
    CALENDAR = "calendar"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    CUSTOM = "custom"


class DisclosurePayload(BaseModel):
    """身份披露载荷"""
    mode: str
    display_text: str | None = None
    template_id: str | None = None


# ============================================
# Message 实体
# ============================================

class Message(BaseModel):
    """消息实体 - 解决"谁写、谁批、谁发、对方看到什么" """
    model_config = {"arbitrary_types_allowed": True}

    # 标识
    id: MessageId = Field(default_factory=MessageId.generate)

    # 所属线程
    thread_id: ThreadId

    # 创作与发送信息
    authored_mode: AuthoredMode
    channel: ChannelType = ChannelType.INTERNAL

    # 主体信息
    sender_principal_id: PrincipalId
    author_principal_id: PrincipalId | None = None
    approver_principal_id: PrincipalId | None = None

    # 内容
    subject: str | None = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    content_html: str | None = None
    content_markdown: str | None = None

    # 引用与回复
    parent_message_id: MessageId | None = None
    reply_to_external_id: str | None = Field(None, max_length=255)
    external_message_id: str | None = Field(None, max_length=255)

    # 审批关联
    approval_request_id: UUID | None = None

    # 身份披露
    disclosure: DisclosurePayload | None = None

    # 附件
    attachments: list[dict[str, Any]] = Field(default_factory=list)

    # 元数据
    is_draft: bool = False
    is_sent: bool = False
    is_read: bool = False
    read_at: datetime | None = None

    # 发送状态
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    delivery_status: str | None = Field(None, max_length=50)
    delivery_error: str | None = None

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 乐观锁
    version: int = 1

    # 扩展数据
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_human_message(
        cls,
        thread_id: ThreadId,
        sender_principal_id: PrincipalId,
        content: str,
        subject: str | None = None,
        channel: ChannelType = ChannelType.INTERNAL,
    ) -> "Message":
        """创建人类创作的消息"""
        return cls(
            thread_id=thread_id,
            authored_mode=AuthoredMode.HUMAN_AUTHORED_HUMAN_SENT,
            sender_principal_id=sender_principal_id,
            author_principal_id=sender_principal_id,
            content=content,
            subject=subject,
            channel=channel,
            is_draft=True,
        )

    @classmethod
    def create_agent_draft(
        cls,
        thread_id: ThreadId,
        agent_principal_id: PrincipalId,
        content: str,
        subject: str | None = None,
        channel: ChannelType = ChannelType.INTERNAL,
    ) -> "Message":
        """创建代理起草的消息"""
        return cls(
            thread_id=thread_id,
            authored_mode=AuthoredMode.AGENT_DRAFTED_HUMAN_SENT,
            sender_principal_id=agent_principal_id,
            author_principal_id=agent_principal_id,
            content=content,
            subject=subject,
            channel=channel,
            is_draft=True,
        )

    @classmethod
    def create_agent_auto_message(
        cls,
        thread_id: ThreadId,
        agent_principal_id: PrincipalId,
        content: str,
        subject: str | None = None,
        channel: ChannelType = ChannelType.INTERNAL,
    ) -> "Message":
        """创建策略范围内自动发送的代理消息"""
        return cls(
            thread_id=thread_id,
            authored_mode=AuthoredMode.AGENT_SENT_WITHIN_POLICY,
            sender_principal_id=agent_principal_id,
            author_principal_id=agent_principal_id,
            content=content,
            subject=subject,
            channel=channel,
            is_draft=False,
            is_sent=True,
            sent_at=datetime.utcnow(),
        )

    @property
    def is_human_authored(self) -> bool:
        return self.authored_mode.is_human_authored

    @property
    def is_agent_drafted(self) -> bool:
        return self.authored_mode.is_agent_drafted

    @property
    def needs_approval(self) -> bool:
        return self.authored_mode.requires_approval and not self.is_sent

    def update_content(self, content: str) -> None:
        """更新内容"""
        if self.is_sent:
            raise ValueError("Cannot update sent message")
        self.content = content
        self._mark_updated()

    def update_subject(self, subject: str) -> None:
        """更新主题"""
        if self.is_sent:
            raise ValueError("Cannot update sent message")
        self.subject = subject[:500]
        self._mark_updated()

    def mark_as_approved(self, approver_id: PrincipalId) -> None:
        """标记为已批准"""
        if self.is_sent:
            raise ValueError("Message already sent")
        self.approver_principal_id = approver_id
        self.authored_mode = AuthoredMode.AGENT_DRAFTED_HUMAN_APPROVED_SENT
        self._mark_updated()

    def mark_as_sent(
        self,
        external_message_id: str | None = None,
    ) -> None:
        """标记为已发送"""
        if self.is_sent:
            raise ValueError("Message already sent")
        self.is_sent = True
        self.is_draft = False
        self.sent_at = datetime.utcnow()
        self.external_message_id = external_message_id
        self._mark_updated()

    def mark_as_read(self) -> None:
        """标记为已读"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self._mark_updated()

    def mark_as_delivered(self) -> None:
        """标记为已送达"""
        self.delivered_at = datetime.utcnow()
        self.delivery_status = "delivered"
        self._mark_updated()

    def mark_delivery_failed(self, error: str) -> None:
        """标记为发送失败"""
        self.delivery_status = "failed"
        self.delivery_error = error[:500]
        self._mark_updated()

    def set_disclosure(self, disclosure: DisclosurePayload) -> None:
        """设置披露信息"""
        self.disclosure = disclosure
        self._mark_updated()

    def add_attachment(self, attachment: dict[str, Any]) -> None:
        """添加附件"""
        self.attachments.append(attachment)
        self._mark_updated()

    def increment_version(self) -> None:
        """版本号递增"""
        self.version += 1

    def _mark_updated(self) -> None:
        """统一维护更新时间和版本号。"""
        self.updated_at = datetime.utcnow()
        self.increment_version()
