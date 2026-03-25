"""Message API 端点"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from myproj.api.deps import Pagination, get_message_id, get_thread_id
from myproj.api.exceptions import NotFoundError
from myproj.core.domain.message import (
    Message,
    MessageId,
    AuthoredMode,
    ChannelType,
)
from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import ThreadId

router = APIRouter(prefix="/threads/{thread_id}/messages", tags=["messages"])

# ============================================
# Pydantic Schemas
# ============================================

class MessageCreateSchema(BaseModel):
    """创建Message请求"""
    sender_principal_id: UUID
    content: str = Field(..., min_length=1)
    subject: Optional[str] = Field(None, max_length=500)
    channel: ChannelType = ChannelType.INTERNAL
    authored_mode: AuthoredMode = AuthoredMode.HUMAN_AUTHORED_HUMAN_SENT
    parent_message_id: Optional[UUID] = None
    attachments: List[dict] = Field(default_factory=list)


class MessageUpdateSchema(BaseModel):
    """更新Message请求（仅草稿可更新）"""
    content: Optional[str] = Field(None, min_length=1)
    subject: Optional[str] = Field(None, max_length=500)


class MessageResponseSchema(BaseModel):
    """Message响应"""
    id: UUID
    thread_id: UUID
    authored_mode: AuthoredMode
    channel: ChannelType
    sender_principal_id: UUID
    author_principal_id: Optional[UUID]
    approver_principal_id: Optional[UUID]
    subject: Optional[str]
    content: str
    parent_message_id: Optional[UUID]
    external_message_id: Optional[str]
    is_draft: bool
    is_sent: bool
    is_read: bool
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    delivery_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_domain(cls, msg: Message) -> "MessageResponseSchema":
        return cls(
            id=msg.id.value,
            thread_id=msg.thread_id.value,
            authored_mode=msg.authored_mode,
            channel=msg.channel,
            sender_principal_id=msg.sender_principal_id.value,
            author_principal_id=msg.author_principal_id.value if msg.author_principal_id else None,
            approver_principal_id=msg.approver_principal_id.value if msg.approver_principal_id else None,
            subject=msg.subject,
            content=msg.content,
            parent_message_id=msg.parent_message_id.value if msg.parent_message_id else None,
            external_message_id=msg.external_message_id,
            is_draft=msg.is_draft,
            is_sent=msg.is_sent,
            is_read=msg.is_read,
            sent_at=msg.sent_at,
            delivered_at=msg.delivered_at,
            delivery_status=msg.delivery_status,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            version=msg.version,
        )


class MessageListResponseSchema(BaseModel):
    """Message列表响应"""
    items: List[MessageResponseSchema]
    total: int
    offset: int
    limit: int


# ============================================
# 内存存储（临时，后续替换为数据库仓储）
# ============================================

_messages: dict[MessageId, Message] = {}


# ============================================
# API 端点
# ============================================

@router.post(
    "",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="创建消息",
)
async def create_message(
    data: MessageCreateSchema,
    thread_id: UUID = Depends(get_thread_id),
) -> MessageResponseSchema:
    """创建新的Message"""
    message = Message(
        thread_id=ThreadId(value=thread_id),
        authored_mode=data.authored_mode,
        channel=data.channel,
        sender_principal_id=PrincipalId(value=data.sender_principal_id),
        author_principal_id=PrincipalId(value=data.sender_principal_id),
        content=data.content,
        subject=data.subject,
        parent_message_id=MessageId(value=data.parent_message_id) if data.parent_message_id else None,
        attachments=data.attachments,
        is_draft=True,
    )

    _messages[message.id] = message
    return MessageResponseSchema.from_domain(message)


@router.get(
    "",
    response_model=MessageListResponseSchema,
    summary="查询线程消息列表",
)
async def list_messages(
    thread_id: UUID = Depends(get_thread_id),
    channel: Optional[List[ChannelType]] = Query(None, description="渠道过滤"),
    authored_mode: Optional[List[AuthoredMode]] = Query(None, description="创作模式过滤"),
    is_draft: Optional[bool] = Query(None, description="是否草稿过滤"),
    is_sent: Optional[bool] = Query(None, description="是否已发送过滤"),
    pagination: Pagination = Depends(),
) -> MessageListResponseSchema:
    """查询Thread的Message列表"""
    tid = ThreadId(value=thread_id)
    messages = [m for m in _messages.values() if m.thread_id == tid]

    if channel:
        messages = [m for m in messages if m.channel in channel]

    if authored_mode:
        messages = [m for m in messages if m.authored_mode in authored_mode]

    if is_draft is not None:
        messages = [m for m in messages if m.is_draft == is_draft]

    if is_sent is not None:
        messages = [m for m in messages if m.is_sent == is_sent]

    # 按创建时间正序
    messages.sort(key=lambda m: m.created_at)

    total = len(messages)
    items = messages[pagination.offset : pagination.offset + pagination.limit]

    return MessageListResponseSchema(
        items=[MessageResponseSchema.from_domain(m) for m in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{message_id}",
    response_model=MessageResponseSchema,
    summary="查询消息详情",
)
async def get_message(
    thread_id: UUID = Depends(get_thread_id),
    message_id: UUID = Depends(get_message_id),
) -> MessageResponseSchema:
    """获取Message详情"""
    mid = MessageId(value=message_id)
    message = _messages.get(mid)
    if not message:
        raise NotFoundError(f"Message not found: {message_id}")

    if message.thread_id.value != thread_id:
        raise NotFoundError(f"Message not found in thread: {thread_id}")

    return MessageResponseSchema.from_domain(message)


@router.patch(
    "/{message_id}",
    response_model=MessageResponseSchema,
    summary="更新消息（仅草稿）",
)
async def update_message(
    data: MessageUpdateSchema,
    thread_id: UUID = Depends(get_thread_id),
    message_id: UUID = Depends(get_message_id),
) -> MessageResponseSchema:
    """更新Message（仅草稿可更新）"""
    mid = MessageId(value=message_id)
    message = _messages.get(mid)
    if not message:
        raise NotFoundError(f"Message not found: {message_id}")

    if message.thread_id.value != thread_id:
        raise NotFoundError(f"Message not found in thread: {thread_id}")

    if not message.is_draft:
        from myproj.api.exceptions import ValidationError
        raise ValidationError("Cannot update non-draft message")

    if data.content is not None:
        message.update_content(data.content)

    if data.subject is not None:
        message.update_subject(data.subject)

    message.increment_version()
    return MessageResponseSchema.from_domain(message)


@router.post(
    "/{message_id}/send",
    response_model=MessageResponseSchema,
    summary="发送消息",
)
async def send_message(
    external_message_id: Optional[str] = None,
    thread_id: UUID = Depends(get_thread_id),
    message_id: UUID = Depends(get_message_id),
) -> MessageResponseSchema:
    """发送Message"""
    mid = MessageId(value=message_id)
    message = _messages.get(mid)
    if not message:
        raise NotFoundError(f"Message not found: {message_id}")

    if message.thread_id.value != thread_id:
        raise NotFoundError(f"Message not found in thread: {thread_id}")

    if message.is_sent:
        from myproj.api.exceptions import ValidationError
        raise ValidationError("Message already sent")

    message.mark_as_sent(external_message_id)
    message.increment_version()
    return MessageResponseSchema.from_domain(message)


@router.post(
    "/{message_id}/read",
    response_model=MessageResponseSchema,
    summary="标记为已读",
)
async def mark_message_read(
    thread_id: UUID = Depends(get_thread_id),
    message_id: UUID = Depends(get_message_id),
) -> MessageResponseSchema:
    """标记Message为已读"""
    mid = MessageId(value=message_id)
    message = _messages.get(mid)
    if not message:
        raise NotFoundError(f"Message not found: {message_id}")

    if message.thread_id.value != thread_id:
        raise NotFoundError(f"Message not found in thread: {thread_id}")

    message.mark_as_read()
    message.increment_version()
    return MessageResponseSchema.from_domain(message)
