"""Thread 仓储"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_

from myproj.core.domain.thread import (
    Thread,
    ThreadId,
    ThreadStatus,
    ThreadObjective,
    DelegationProfile,
    DelegationLevel,
    RiskLevel,
)
from myproj.core.repositories.base import BaseRepository
from myproj.infra.db.models import ThreadModel


class ThreadRepository(BaseRepository[ThreadId, Thread, ThreadModel]):
    """Thread 仓储"""

    def _model_class(self):
        return ThreadModel

    def _to_id_value(self, entity_id: ThreadId) -> UUID:
        return entity_id.value

    def _get_entity_id(self, entity: Thread) -> ThreadId:
        return entity.id

    def _to_entity(self, model: ThreadModel) -> Thread:
        """将数据库模型转换为领域实体"""
        delegation_profile = None
        if model.delegation_profile_name:
            delegation_profile = DelegationProfile(
                profile_name=model.delegation_profile_name,
                level=DelegationLevel(model.delegation_level) if model.delegation_level else DelegationLevel.OBSERVE_ONLY,
                max_actions_per_hour=model.delegation_max_actions_per_hour or 10,
                max_messages_per_thread=model.delegation_max_messages_per_thread or 50,
                max_consecutive_touches=model.delegation_max_consecutive_touches or 3,
                allowed_actions=model.delegation_allowed_actions or [],
                escalation_rules=model.delegation_escalation_rules or {},
            )

        return Thread(
            id=ThreadId(value=model.id),
            objective=ThreadObjective(
                title=model.objective_title,
                description=model.objective_description,
                due_at=model.objective_due_at,
            ),
            status=ThreadStatus(model.status),
            risk_level=RiskLevel(model.risk_level),
            delegation_profile=delegation_profile or DelegationProfile.default_observe(),
            owner_id=model.owner_id,
            responsible_principal_id=model.responsible_principal_id,
            participant_ids=model.participant_ids or [],
            summary=model.summary,
            tags=model.tags or [],
            last_escalated_at=model.last_escalated_at,
            last_escalation_reason=model.last_escalation_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            version=model.version,
            context=model.context or {},
        )

    def _to_model(self, entity: Thread) -> ThreadModel:
        """将领域实体转换为数据库模型"""
        profile = entity.delegation_profile
        return ThreadModel(
            id=entity.id.value,
            objective_title=entity.objective.title,
            objective_description=entity.objective.description,
            objective_due_at=entity.objective.due_at,
            status=entity.status.value,
            risk_level=entity.risk_level.value,
            delegation_profile_name=profile.profile_name if profile else None,
            delegation_level=profile.level.value if profile else None,
            delegation_max_actions_per_hour=profile.max_actions_per_hour if profile else None,
            delegation_max_messages_per_thread=profile.max_messages_per_thread if profile else None,
            delegation_max_consecutive_touches=profile.max_consecutive_touches if profile else None,
            delegation_allowed_actions=profile.allowed_actions if profile else None,
            delegation_escalation_rules=profile.escalation_rules if profile else None,
            owner_id=entity.owner_id,
            responsible_principal_id=entity.responsible_principal_id,
            participant_ids=entity.participant_ids,
            summary=entity.summary,
            tags=entity.tags,
            last_escalated_at=entity.last_escalated_at,
            last_escalation_reason=entity.last_escalation_reason,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at,
            version=entity.version,
            context=entity.context,
        )

    # Thread 专用查询方法

    def find_by_owner(
        self,
        owner_id: UUID,
        statuses: Optional[List[ThreadStatus]] = None,
        risk_levels: Optional[List[RiskLevel]] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """按所有者查询"""
        query = self.session.query(ThreadModel).filter(ThreadModel.owner_id == owner_id)

        if statuses:
            query = query.filter(ThreadModel.status.in_([s.value for s in statuses]))

        if risk_levels:
            query = query.filter(ThreadModel.risk_level.in_([r.value for r in risk_levels]))

        models = (
            query.order_by(ThreadModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_owner(
        self,
        owner_id: UUID,
        statuses: Optional[List[ThreadStatus]] = None,
    ) -> int:
        """按所有者统计"""
        query = self.session.query(ThreadModel).filter(ThreadModel.owner_id == owner_id)

        if statuses:
            query = query.filter(ThreadModel.status.in_([s.value for s in statuses]))

        return query.count()

    def find_by_status(
        self,
        status: ThreadStatus,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """按状态查询"""
        models = (
            self.session.query(ThreadModel)
            .filter(ThreadModel.status == status.value)
            .order_by(ThreadModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_participant(
        self,
        principal_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """按参与者查询"""
        # PostgreSQL 的 JSONB 包含查询
        models = (
            self.session.query(ThreadModel)
            .filter(ThreadModel.participant_ids.contains([str(principal_id)]))
            .order_by(ThreadModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_tags(
        self,
        tags: List[str],
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """按标签查询"""
        query = self.session.query(ThreadModel)

        # 匹配任意一个标签
        conditions = [ThreadModel.tags.contains([tag]) for tag in tags]
        query = query.filter(or_(*conditions))

        models = (
            query.order_by(ThreadModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_needs_approval(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """查询需要审批的Thread"""
        return self.find_by_status(ThreadStatus.AWAITING_APPROVAL, offset, limit)

    def find_agent_running(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """查询代理正在运行的Thread"""
        return self.find_by_status(ThreadStatus.ACTIVE, offset, limit)

    def find_awaiting_external(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """查询等待外部回复的Thread"""
        return self.find_by_status(ThreadStatus.AWAITING_EXTERNAL, offset, limit)

    def find_blocked(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """查询被阻塞的Thread"""
        return self.find_by_status(ThreadStatus.BLOCKED, offset, limit)

    def find_completed(
        self,
        since: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Thread]:
        """查询已完成的Thread"""
        query = self.session.query(ThreadModel).filter(
            ThreadModel.status == ThreadStatus.COMPLETED.value
        )

        if since:
            query = query.filter(ThreadModel.completed_at >= since)

        models = (
            query.order_by(ThreadModel.completed_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]
