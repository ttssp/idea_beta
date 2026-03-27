"""Event 仓储"""

from uuid import UUID

from myproj.core.domain.event import (
    EventId,
    EventType,
    ThreadEvent,
    ThreadStatus,
)
from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import ThreadId
from myproj.core.repositories.base import BaseRepository
from myproj.infra.db.models import ThreadEventModel


class EventRepository(BaseRepository[EventId, ThreadEvent, ThreadEventModel]):
    """Event 仓储"""

    def _model_class(self):
        return ThreadEventModel

    def _to_id_value(self, entity_id: EventId) -> UUID:
        return entity_id.value

    def _get_entity_id(self, entity: ThreadEvent) -> EventId:
        return entity.id

    def _to_entity(self, model: ThreadEventModel) -> ThreadEvent:
        """将数据库模型转换为领域实体"""
        thread_status_before = None
        if model.thread_status_before:
            thread_status_before = ThreadStatus(model.thread_status_before)

        thread_status_after = None
        if model.thread_status_after:
            thread_status_after = ThreadStatus(model.thread_status_after)

        return ThreadEvent(
            id=EventId(value=model.id),
            thread_id=ThreadId(value=model.thread_id),
            event_type=EventType(model.event_type),
            occurred_at=model.occurred_at,
            sequence_number=model.sequence_number,
            actor_principal_id=PrincipalId(value=model.actor_principal_id)
            if model.actor_principal_id
            else None,
            actor_type=model.actor_type,
            causal_event_id=EventId(value=model.causal_event_id)
            if model.causal_event_id
            else None,
            causal_ref=model.causal_ref,
            title=model.title,
            description=model.description,
            payload=model.payload or {},
            thread_status_before=thread_status_before,
            thread_status_after=thread_status_after,
            idempotency_key=model.idempotency_key,
            is_replayed=model.is_replayed,
            is_visible=model.is_visible,
            created_at=model.created_at,
        )

    def _to_model(self, entity: ThreadEvent) -> ThreadEventModel:
        """将领域实体转换为数据库模型"""
        return ThreadEventModel(
            id=entity.id.value,
            thread_id=entity.thread_id.value,
            event_type=entity.event_type.value,
            occurred_at=entity.occurred_at,
            sequence_number=entity.sequence_number,
            actor_principal_id=entity.actor_principal_id.value
            if entity.actor_principal_id
            else None,
            actor_type=entity.actor_type,
            causal_event_id=entity.causal_event_id.value
            if entity.causal_event_id
            else None,
            causal_ref=entity.causal_ref,
            title=entity.title,
            description=entity.description,
            payload=entity.payload,
            thread_status_before=entity.thread_status_before.value
            if entity.thread_status_before
            else None,
            thread_status_after=entity.thread_status_after.value
            if entity.thread_status_after
            else None,
            idempotency_key=entity.idempotency_key,
            is_replayed=entity.is_replayed,
            is_visible=entity.is_visible,
            created_at=entity.created_at,
        )

    # Event 专用查询方法

    def find_by_thread(
        self,
        thread_id: ThreadId,
        event_type: EventType | None = None,
        include_hidden: bool = False,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ThreadEvent]:
        """按线程查询事件"""
        query = self.session.query(ThreadEventModel).filter(
            ThreadEventModel.thread_id == thread_id.value
        )

        if event_type:
            query = query.filter(ThreadEventModel.event_type == event_type.value)

        if not include_hidden:
            query = query.filter(ThreadEventModel.is_visible == True)

        models = query.order_by(ThreadEventModel.sequence_number.asc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def count_by_thread(self, thread_id: ThreadId) -> int:
        """统计线程事件数量"""
        return (
            self.session.query(ThreadEventModel)
            .filter(ThreadEventModel.thread_id == thread_id.value)
            .count()
        )

    def find_by_type(
        self,
        event_type: EventType,
        thread_id: ThreadId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ThreadEvent]:
        """按事件类型查询"""
        query = self.session.query(ThreadEventModel).filter(
            ThreadEventModel.event_type == event_type.value
        )

        if thread_id:
            query = query.filter(ThreadEventModel.thread_id == thread_id.value)

        models = query.order_by(ThreadEventModel.occurred_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> ThreadEvent | None:
        """按幂等键查询"""
        model = (
            self.session.query(ThreadEventModel)
            .filter(ThreadEventModel.idempotency_key == idempotency_key)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_causal_event(
        self,
        causal_event_id: EventId,
    ) -> list[ThreadEvent]:
        """查询因果事件"""
        models = (
            self.session.query(ThreadEventModel)
            .filter(ThreadEventModel.causal_event_id == causal_event_id.value)
            .order_by(ThreadEventModel.occurred_at.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_status_changes(
        self,
        thread_id: ThreadId,
        from_status: ThreadStatus | None = None,
        to_status: ThreadStatus | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ThreadEvent]:
        """查询状态变更事件"""
        query = self.session.query(ThreadEventModel).filter(
            ThreadEventModel.thread_id == thread_id.value,
            ThreadEventModel.event_type == EventType.THREAD_STATUS_CHANGED.value,
        )

        if from_status:
            query = query.filter(ThreadEventModel.thread_status_before == from_status.value)

        if to_status:
            query = query.filter(ThreadEventModel.thread_status_after == to_status.value)

        models = query.order_by(ThreadEventModel.occurred_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def get_next_sequence_number(self, thread_id: ThreadId) -> int:
        """获取下一个序列号"""
        from sqlalchemy import func

        result = (
            self.session.query(func.max(ThreadEventModel.sequence_number))
            .filter(ThreadEventModel.thread_id == thread_id.value)
            .scalar()
        )
        return (result or 0) + 1

    def find_replayed(
        self,
        thread_id: ThreadId,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ThreadEvent]:
        """查询回放事件"""
        models = (
            self.session.query(ThreadEventModel)
            .filter(ThreadEventModel.thread_id == thread_id.value)
            .filter(ThreadEventModel.is_replayed == True)
            .order_by(ThreadEventModel.sequence_number.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_actor(
        self,
        actor_principal_id: PrincipalId,
        thread_id: ThreadId | None = None,
        event_type: EventType | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ThreadEvent]:
        """按执行者查询事件"""
        query = self.session.query(ThreadEventModel).filter(
            ThreadEventModel.actor_principal_id == actor_principal_id.value
        )

        if thread_id:
            query = query.filter(ThreadEventModel.thread_id == thread_id.value)

        if event_type:
            query = query.filter(ThreadEventModel.event_type == event_type.value)

        models = query.order_by(ThreadEventModel.occurred_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]
