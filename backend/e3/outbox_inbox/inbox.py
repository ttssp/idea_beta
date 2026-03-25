
"""
Inbox Pattern - Processor

Implements the inbox pattern for receiving external events.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.idempotency import IdempotencyManager
from .models import InboxEvent, InboxStatusEnum


class InboxProcessor:
    """
    Inbox处理器

    负责接收外部事件，去重，写入Inbox表
    """

    def __init__(self, db: AsyncSession, idempotency: IdempotencyManager):
        self.db = db
        self.idempotency = idempotency

    async def receive(
        self,
        channel_type: str,
        event_type: str,
        external_thread_key: str | None,
        external_message_key: str,
        payload: dict[str, Any],
        raw_payload: bytes | None = None,
        webhook_signature: str | None = None,
        webhook_timestamp: datetime | None = None,
    ) -> tuple[InboxEvent, bool]:
        """
        接收外部事件，写入Inbox

        Args:
            channel_type: 渠道类型
            event_type: 事件类型
            external_thread_key: 外部线程Key
            external_message_key: 外部消息Key（唯一）
            payload: 事件内容
            raw_payload: 原始payload（可选）
            webhook_signature: Webhook签名（可选）
            webhook_timestamp: Webhook时间戳（可选）

        Returns:
            (InboxEvent, 是否是新事件)
        """
        # 1. 检查幂等（数据库层）
        existing = await self.db.execute(
            select(InboxEvent).where(
                InboxEvent.external_message_key == external_message_key
            )
        )
        existing_event = existing.scalar_one_or_none()
        if existing_event:
            return existing_event, False

        # 2. 检查幂等（Redis层）
        idempotency_key = self.idempotency.generate_key(
            channel_type, external_message_key
        )
        can_proceed, previous_result = await self.idempotency.check_and_set(idempotency_key)
        if not can_proceed:
            # 再次查数据库（可能有并发）
            existing = await self.db.execute(
                select(InboxEvent).where(
                    InboxEvent.external_message_key == external_message_key
                )
            )
            existing_event = existing.scalar_one_or_none()
            if existing_event:
                return existing_event, False

        # 3. 创建InboxEvent
        event = InboxEvent(
            idempotency_key=idempotency_key,
            channel_type=channel_type,
            event_type=event_type,
            external_thread_key=external_thread_key,
            external_message_key=external_message_key,
            payload=payload,
            raw_payload=raw_payload,
            status=InboxStatusEnum.PENDING,
            webhook_signature=webhook_signature,
            webhook_timestamp=webhook_timestamp,
            received_at=datetime.now(UTC)
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return event, True

    async def mark_processing(self, event_id: UUID) -> InboxEvent | None:
        """标记事件为处理中"""
        result = await self.db.execute(
            select(InboxEvent)
            .where(
                InboxEvent.id == event_id,
                InboxEvent.status == InboxStatusEnum.PENDING
            )
            .with_for_update(skip_locked=True)
        )
        event = result.scalar_one_or_none()
        if event:
            event.status = InboxStatusEnum.PROCESSING
            await self.db.commit()
            await self.db.refresh(event)
        return event

    async def mark_processed(
        self,
        event_id: UUID,
        resolved_thread_id: UUID | None = None
    ) -> InboxEvent:
        """标记事件为已处理"""
        result = await self.db.execute(
            select(InboxEvent).where(InboxEvent.id == event_id)
        )
        event = result.scalar_one()
        event.status = InboxStatusEnum.PROCESSED
        event.resolved_thread_id = resolved_thread_id
        event.processed_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def mark_failed(
        self,
        event_id: UUID,
        error_message: str
    ) -> InboxEvent:
        """标记事件为失败"""
        result = await self.db.execute(
            select(InboxEvent).where(InboxEvent.id == event_id)
        )
        event = result.scalar_one()
        event.status = InboxStatusEnum.FAILED
        event.error_message = error_message
        event.processed_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def mark_ignored(self, event_id: UUID) -> InboxEvent:
        """标记事件为忽略"""
        result = await self.db.execute(
            select(InboxEvent).where(InboxEvent.id == event_id)
        )
        event = result.scalar_one()
        event.status = InboxStatusEnum.IGNORED
        event.processed_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_pending_events(
        self,
        limit: int = 100,
        channel_type: str | None = None
    ) -> list[InboxEvent]:
        """获取待处理的事件"""
        query = (
            select(InboxEvent)
            .where(InboxEvent.status == InboxStatusEnum.PENDING)
            .order_by(InboxEvent.received_at.asc())
            .limit(limit)
        )
        if channel_type:
            query = query.where(InboxEvent.channel_type == channel_type)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_inbox_event(self, event_id: UUID) -> InboxEvent | None:
        """获取Inbox事件"""
        result = await self.db.execute(
            select(InboxEvent).where(InboxEvent.id == event_id)
        )
        return result.scalar_one_or_none()
