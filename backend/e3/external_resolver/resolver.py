
"""
External Resolver

Resolves external messages to internal Threads.
"""

from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import ExternalBinding, BindingTypeEnum, SyncStateEnum, ChannelTypeEnum
from ..outbox_inbox.models import InboxEvent


class ExternalResolver:
    """
    外部消息解析器

    负责将外部消息映射到内部Thread
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve(
        self,
        channel_type: str,
        external_thread_key: str,
        external_message_key: Optional[str] = None,
    ) -> Tuple[Optional[UUID], bool]:
        """
        解析外部消息到内部Thread

        Args:
            channel_type: 渠道类型
            external_thread_key: 外部线程Key
            external_message_key: 外部消息Key（可选）

        Returns:
            (thread_id, 是否新建了绑定)
        """
        # 1. 查找已有的绑定
        existing_binding = await self.db.execute(
            select(ExternalBinding).where(
                ExternalBinding.channel_type == channel_type,
                ExternalBinding.external_thread_key == external_thread_key,
                ExternalBinding.sync_state == SyncStateEnum.ACTIVE
            )
        )
        binding = existing_binding.scalar_one_or_none()

        if binding:
            return binding.thread_id, False

        # 2. 通过Message查找关联的Thread（如通过In-Reply-To）
        if external_message_key:
            related_thread_id = await self._resolve_by_message_relation(
                channel_type, external_message_key
            )
            if related_thread_id:
                return related_thread_id, False

        # 3. 无法解析，返回None
        return None, False

    async def bind(
        self,
        thread_id: UUID,
        channel_type: str,
        external_thread_key: str,
        external_message_key: Optional[str] = None,
        binding_type: str = "primary",
        sync_token: Optional[str] = None
    ) -> ExternalBinding:
        """
        创建外部绑定

        Args:
            thread_id: Thread ID
            channel_type: 渠道类型
            external_thread_key: 外部线程Key
            external_message_key: 外部消息Key（可选）
            binding_type: 绑定类型
            sync_token: 同步token（可选）

        Returns:
            创建的ExternalBinding
        """
        # 检查是否已存在
        existing = await self.db.execute(
            select(ExternalBinding).where(
                ExternalBinding.channel_type == channel_type,
                ExternalBinding.external_thread_key == external_thread_key
            )
        )
        existing_binding = existing.scalar_one_or_none()
        if existing_binding:
            # 更新已存在的绑定
            existing_binding.thread_id = thread_id
            existing_binding.sync_state = SyncStateEnum.ACTIVE
            if sync_token:
                existing_binding.sync_token = sync_token
            await self.db.commit()
            await self.db.refresh(existing_binding)
            return existing_binding

        # 创建新绑定
        binding = ExternalBinding(
            thread_id=thread_id,
            channel_type=channel_type,
            external_thread_key=external_thread_key,
            external_message_key=external_message_key,
            binding_type=binding_type,
            sync_token=sync_token
        )
        self.db.add(binding)
        await self.db.commit()
        await self.db.refresh(binding)
        return binding

    async def get_binding(
        self,
        channel_type: str,
        external_thread_key: str
    ) -> Optional[ExternalBinding]:
        """获取绑定"""
        result = await self.db.execute(
            select(ExternalBinding).where(
                ExternalBinding.channel_type == channel_type,
                ExternalBinding.external_thread_key == external_thread_key
            )
        )
        return result.scalar_one_or_none()

    async def get_bindings_by_thread(
        self,
        thread_id: UUID
    ) -> list[ExternalBinding]:
        """获取Thread的所有绑定"""
        result = await self.db.execute(
            select(ExternalBinding).where(ExternalBinding.thread_id == thread_id)
        )
        return list(result.scalars().all())

    async def pause_binding(
        self,
        binding_id: UUID
    ) -> Optional[ExternalBinding]:
        """暂停绑定"""
        result = await self.db.execute(
            select(ExternalBinding).where(ExternalBinding.id == binding_id)
        )
        binding = result.scalar_one_or_none()
        if binding:
            binding.sync_state = SyncStateEnum.PAUSED
            await self.db.commit()
            await self.db.refresh(binding)
        return binding

    async def resume_binding(
        self,
        binding_id: UUID
    ) -> Optional[ExternalBinding]:
        """恢复绑定"""
        result = await self.db.execute(
            select(ExternalBinding).where(ExternalBinding.id == binding_id)
        )
        binding = result.scalar_one_or_none()
        if binding:
            binding.sync_state = SyncStateEnum.ACTIVE
            await self.db.commit()
            await self.db.refresh(binding)
        return binding

    async def archive_binding(
        self,
        binding_id: UUID
    ) -> Optional[ExternalBinding]:
        """归档绑定"""
        result = await self.db.execute(
            select(ExternalBinding).where(ExternalBinding.id == binding_id)
        )
        binding = result.scalar_one_or_none()
        if binding:
            binding.sync_state = SyncStateEnum.ARCHIVED
            await self.db.commit()
            await self.db.refresh(binding)
        return binding

    async def update_last_synced(
        self,
        binding_id: UUID,
        sync_token: Optional[str] = None
    ) -> Optional[ExternalBinding]:
        """更新最后同步时间"""
        from datetime import datetime
        result = await self.db.execute(
            select(ExternalBinding).where(ExternalBinding.id == binding_id)
        )
        binding = result.scalar_one_or_none()
        if binding:
            binding.last_synced_at = datetime.utcnow()
            if sync_token:
                binding.sync_token = sync_token
            await self.db.commit()
            await self.db.refresh(binding)
        return binding

    async def _resolve_by_message_relation(
        self,
        channel_type: str,
        external_message_key: str
    ) -> Optional[UUID]:
        """通过消息关联查找Thread"""
        # 查找是否有其他绑定使用了这个message_key
        result = await self.db.execute(
            select(ExternalBinding.thread_id).where(
                ExternalBinding.channel_type == channel_type,
                ExternalBinding.external_message_key == external_message_key
            )
        )
        thread_id = result.scalar_one_or_none()
        if thread_id:
            return thread_id

        # 也可以通过InboxEvent查找
        inbox_result = await self.db.execute(
            select(InboxEvent.resolved_thread_id).where(
                InboxEvent.channel_type == channel_type,
                InboxEvent.external_message_key == external_message_key,
                InboxEvent.resolved_thread_id.isnot(None)
            )
        )
        return inbox_result.scalar_one_or_none()

