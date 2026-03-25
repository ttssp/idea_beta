
"""
Outbox Pattern - Producer

Implements the outbox pattern for reliable message delivery.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.idempotency import IdempotencyManager
from .models import OutboxDeadLetter, OutboxMessage, OutboxStatusEnum


class OutboxProducer:
    """
    Outbox生产者

    负责将消息写入Outbox表（在同一事务中）
    """

    def __init__(self, db: AsyncSession, idempotency: IdempotencyManager | None = None):
        self.db = db
        self.idempotency = idempotency

    async def enqueue(
        self,
        thread_id: UUID,
        action_run_id: UUID,
        channel_type: str,
        message_type: str,
        payload: dict[str, Any],
        idempotency_key: str,
        scheduled_for: datetime | None = None,
        max_retries: int = 5
    ) -> OutboxMessage:
        """
        将消息写入Outbox表

        注意：此方法应该在与业务逻辑相同的事务中调用

        Args:
            thread_id: Thread ID
            action_run_id: ActionRun ID
            channel_type: 渠道类型
            message_type: 消息类型
            payload: 消息内容
            idempotency_key: 幂等键
            scheduled_for: 调度时间
            max_retries: 最大重试次数

        Returns:
            创建的OutboxMessage
        """
        if scheduled_for is None:
            scheduled_for = datetime.now(UTC)

        # 检查幂等
        existing = await self.db.execute(
            select(OutboxMessage).where(OutboxMessage.idempotency_key == idempotency_key)
        )
        existing_msg = existing.scalar_one_or_none()
        if existing_msg:
            return existing_msg

        outbox_msg = OutboxMessage(
            idempotency_key=idempotency_key,
            thread_id=thread_id,
            action_run_id=action_run_id,
            channel_type=channel_type,
            message_type=message_type,
            payload=payload,
            status=OutboxStatusEnum.PENDING,
            scheduled_for=scheduled_for,
            max_retries=max_retries
        )
        self.db.add(outbox_msg)
        await self.db.commit()
        await self.db.refresh(outbox_msg)
        return outbox_msg

    async def get_pending_messages(
        self,
        limit: int = 100,
        channel_type: str | None = None
    ) -> list[OutboxMessage]:
        """
        获取待处理的消息

        Args:
            limit: 最多获取数量
            channel_type: 可选的渠道过滤

        Returns:
            OutboxMessage列表
        """
        query = (
            select(OutboxMessage)
            .where(
                OutboxMessage.status == OutboxStatusEnum.PENDING,
                OutboxMessage.scheduled_for <= datetime.now(UTC)
            )
            .order_by(OutboxMessage.scheduled_for.asc())
            .limit(limit)
        )
        if channel_type:
            query = query.where(OutboxMessage.channel_type == channel_type)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_processing(self, outbox_id: UUID) -> OutboxMessage | None:
        """标记消息为处理中（使用FOR UPDATE SKIP LOCKED）"""
        result = await self.db.execute(
            select(OutboxMessage)
            .where(
                OutboxMessage.id == outbox_id,
                OutboxMessage.status == OutboxStatusEnum.PENDING
            )
            .with_for_update(skip_locked=True)
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.status = OutboxStatusEnum.PROCESSING
            msg.last_attempted_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(msg)
        return msg

    async def mark_sent(
        self,
        outbox_id: UUID,
        external_response: dict[str, Any] | None = None,
        external_message_id: str | None = None
    ) -> OutboxMessage:
        """标记消息为已发送"""
        result = await self.db.execute(
            select(OutboxMessage).where(OutboxMessage.id == outbox_id)
        )
        msg = result.scalar_one()
        msg.status = OutboxStatusEnum.SENT
        if external_response:
            msg.external_response = external_response
        if external_message_id:
            msg.external_message_id = external_message_id
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def mark_failed(
        self,
        outbox_id: UUID,
        error: str,
        retry_delay_seconds: int | None = None
    ) -> OutboxMessage:
        """
        标记消息为失败

        如果还有重试次数，重新排队；否则移入死信
        """
        result = await self.db.execute(
            select(OutboxMessage).where(OutboxMessage.id == outbox_id)
        )
        msg = result.scalar_one()

        msg.retry_count += 1
        msg.last_error = error
        msg.last_attempted_at = datetime.now(UTC)

        if msg.retry_count >= msg.max_retries:
            # 超过最大重试次数，移入死信
            await self._move_to_dead_letter(msg, error)
            msg.status = OutboxStatusEnum.DEAD_LETTER
        else:
            # 重新排队
            msg.status = OutboxStatusEnum.PENDING
            if retry_delay_seconds is None:
                # 指数退避: 2^retry_count * 60秒
                retry_delay_seconds = 2 ** msg.retry_count * 60
            msg.scheduled_for = datetime.now(UTC) + timedelta(seconds=retry_delay_seconds)

        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def _move_to_dead_letter(self, msg: OutboxMessage, error: str):
        """将消息移入死信表"""
        dead_letter = OutboxDeadLetter(
            original_outbox_id=msg.id,
            idempotency_key=msg.idempotency_key,
            thread_id=msg.thread_id,
            action_run_id=msg.action_run_id,
            channel_type=msg.channel_type,
            message_type=msg.message_type,
            payload=msg.payload,
            last_error=error,
            retry_count=msg.retry_count,
            original_created_at=msg.created_at
        )
        self.db.add(dead_letter)

    async def get_outbox_message(self, outbox_id: UUID) -> OutboxMessage | None:
        """获取Outbox消息"""
        result = await self.db.execute(
            select(OutboxMessage).where(OutboxMessage.id == outbox_id)
        )
        return result.scalar_one_or_none()

    async def get_queue_depth(self, channel_type: str | None = None) -> int:
        """获取队列深度"""
        query = select(func.count(OutboxMessage.id)).where(
            OutboxMessage.status == OutboxStatusEnum.PENDING
        )
        if channel_type:
            query = query.where(OutboxMessage.channel_type == channel_type)
        result = await self.db.execute(query)
        return result.scalar() or 0
