"""Message 仓储"""

from uuid import UUID

from myproj.core.domain.message import (
    AuthoredMode,
    ChannelType,
    DisclosurePayload,
    Message,
    MessageId,
)
from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import ThreadId
from myproj.core.repositories.base import BaseRepository
from myproj.infra.db.models import MessageModel


class MessageRepository(BaseRepository[MessageId, Message, MessageModel]):
    """Message 仓储"""

    def _model_class(self):
        return MessageModel

    def _to_id_value(self, entity_id: MessageId) -> UUID:
        return entity_id.value

    def _get_entity_id(self, entity: Message) -> MessageId:
        return entity.id

    def _to_entity(self, model: MessageModel) -> Message:
        """将数据库模型转换为领域实体"""
        disclosure = None
        if model.disclosure:
            disclosure = DisclosurePayload(**model.disclosure)

        return Message(
            id=MessageId(value=model.id),
            thread_id=ThreadId(value=model.thread_id),
            authored_mode=AuthoredMode(model.authored_mode),
            channel=ChannelType(model.channel),
            sender_principal_id=PrincipalId(value=model.sender_principal_id),
            author_principal_id=PrincipalId(value=model.author_principal_id)
            if model.author_principal_id
            else None,
            approver_principal_id=PrincipalId(value=model.approver_principal_id)
            if model.approver_principal_id
            else None,
            subject=model.subject,
            content=model.content,
            content_html=model.content_html,
            content_markdown=model.content_markdown,
            parent_message_id=MessageId(value=model.parent_message_id)
            if model.parent_message_id
            else None,
            reply_to_external_id=model.reply_to_external_id,
            external_message_id=model.external_message_id,
            approval_request_id=model.approval_request_id,
            disclosure=disclosure,
            attachments=model.attachments or [],
            is_draft=model.is_draft,
            is_sent=model.is_sent,
            is_read=model.is_read,
            read_at=model.read_at,
            sent_at=model.sent_at,
            delivered_at=model.delivered_at,
            delivery_status=model.delivery_status,
            delivery_error=model.delivery_error,
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
            metadata=model.meta_data or {},
        )

    def _to_model(self, entity: Message) -> MessageModel:
        """将领域实体转换为数据库模型"""
        disclosure = None
        if entity.disclosure:
            disclosure = entity.disclosure.model_dump(mode="json")

        return MessageModel(
            id=entity.id.value,
            thread_id=entity.thread_id.value,
            authored_mode=entity.authored_mode.value,
            channel=entity.channel.value,
            sender_principal_id=entity.sender_principal_id.value,
            author_principal_id=entity.author_principal_id.value
            if entity.author_principal_id
            else None,
            approver_principal_id=entity.approver_principal_id.value
            if entity.approver_principal_id
            else None,
            subject=entity.subject,
            content=entity.content,
            content_html=entity.content_html,
            content_markdown=entity.content_markdown,
            parent_message_id=entity.parent_message_id.value
            if entity.parent_message_id
            else None,
            reply_to_external_id=entity.reply_to_external_id,
            external_message_id=entity.external_message_id,
            approval_request_id=entity.approval_request_id,
            disclosure=disclosure,
            attachments=entity.attachments,
            is_draft=entity.is_draft,
            is_sent=entity.is_sent,
            is_read=entity.is_read,
            read_at=entity.read_at,
            sent_at=entity.sent_at,
            delivered_at=entity.delivered_at,
            delivery_status=entity.delivery_status,
            delivery_error=entity.delivery_error,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            version=entity.version,
            meta_data=entity.metadata,
        )

    # Message 专用查询方法

    def find_by_thread(
        self,
        thread_id: ThreadId,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """按线程查询消息"""
        models = (
            self.session.query(MessageModel)
            .filter(MessageModel.thread_id == thread_id.value)
            .order_by(MessageModel.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_thread(self, thread_id: ThreadId) -> int:
        """统计线程消息数量"""
        return (
            self.session.query(MessageModel)
            .filter(MessageModel.thread_id == thread_id.value)
            .count()
        )

    def find_drafts(
        self,
        thread_id: ThreadId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """查询草稿消息"""
        query = self.session.query(MessageModel).filter(MessageModel.is_draft == True)

        if thread_id:
            query = query.filter(MessageModel.thread_id == thread_id.value)

        models = query.order_by(MessageModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_sent(
        self,
        thread_id: ThreadId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """查询已发送消息"""
        query = self.session.query(MessageModel).filter(MessageModel.is_sent == True)

        if thread_id:
            query = query.filter(MessageModel.thread_id == thread_id.value)

        models = query.order_by(MessageModel.sent_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_by_external_id(
        self,
        external_message_id: str,
    ) -> Message | None:
        """按外部消息ID查询"""
        model = (
            self.session.query(MessageModel)
            .filter(MessageModel.external_message_id == external_message_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_authored_mode(
        self,
        mode: AuthoredMode,
        thread_id: ThreadId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """按创作模式查询"""
        query = self.session.query(MessageModel).filter(
            MessageModel.authored_mode == mode.value
        )

        if thread_id:
            query = query.filter(MessageModel.thread_id == thread_id.value)

        models = query.order_by(MessageModel.created_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_by_channel(
        self,
        channel: ChannelType,
        thread_id: ThreadId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """按渠道查询"""
        query = self.session.query(MessageModel).filter(MessageModel.channel == channel.value)

        if thread_id:
            query = query.filter(MessageModel.thread_id == thread_id.value)

        models = query.order_by(MessageModel.created_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]
