"""Thread 领域服务"""

from datetime import datetime
from uuid import UUID

from myproj.core.domain.event import EventType, ThreadEvent
from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.thread import (
    DelegationProfile,
    RiskLevel,
    Thread,
    ThreadId,
    ThreadObjective,
    ThreadStatus,
)
from myproj.core.services.event_store import EventStore
from myproj.core.services.state_machine import ThreadStateMachine


class ThreadService:
    """Thread 服务 - Thread生命周期管理"""

    def __init__(
        self,
        state_machine: ThreadStateMachine | None = None,
        event_store: EventStore | None = None,
    ) -> None:
        self.state_machine = state_machine or ThreadStateMachine()
        self.event_store = event_store or EventStore()
        self._threads: dict[ThreadId, Thread] = {}

    def create_thread(
        self,
        title: str,
        owner_id: UUID,
        description: str | None = None,
        due_at: datetime | None = None,
        delegation_profile: DelegationProfile | None = None,
        participant_ids: list[UUID] | None = None,
        tags: list[str] | None = None,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """
        创建新Thread

        Returns:
            (创建的Thread, 创建事件)
        """
        objective = ThreadObjective(
            title=title,
            description=description,
            due_at=due_at,
        )

        thread = Thread(
            objective=objective,
            owner_id=owner_id,
            responsible_principal_id=owner_id,
            delegation_profile=delegation_profile or DelegationProfile.default_observe(),
            participant_ids=participant_ids or [],
            tags=tags or [],
        )

        # 存储
        self._threads[thread.id] = thread

        # 创建并存储事件
        event = ThreadEvent.create_thread_created(
            thread_id=thread.id,
            actor_id=actor_id,
            objective=title,
        )
        self.event_store.append(event)

        return thread, event

    def get_thread(self, thread_id: ThreadId) -> Thread | None:
        """获取Thread"""
        return self._threads.get(thread_id)

    def get_thread_by_uuid(self, thread_uuid: UUID) -> Thread | None:
        """通过UUID获取Thread"""
        thread_id = ThreadId(value=thread_uuid)
        return self.get_thread(thread_id)

    def list_threads(
        self,
        owner_id: UUID | None = None,
        statuses: list[ThreadStatus] | None = None,
        risk_levels: list[RiskLevel] | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Thread]:
        """
        查询Thread列表

        Args:
            owner_id: 所有者过滤
            statuses: 状态过滤
            risk_levels: 风险等级过滤
            tags: 标签过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            Thread列表
        """
        threads = list(self._threads.values())

        if owner_id is not None:
            threads = [t for t in threads if t.owner_id == owner_id]

        if statuses:
            threads = [t for t in threads if t.status in statuses]

        if risk_levels:
            threads = [t for t in threads if t.risk_level in risk_levels]

        if tags:
            threads = [t for t in threads if any(tag in t.tags for tag in tags)]

        # 按更新时间倒序
        threads.sort(key=lambda t: t.updated_at, reverse=True)

        return threads[offset : offset + limit]

    def count_threads(
        self,
        owner_id: UUID | None = None,
        statuses: list[ThreadStatus] | None = None,
    ) -> int:
        """统计Thread数量"""
        threads = list(self._threads.values())

        if owner_id is not None:
            threads = [t for t in threads if t.owner_id == owner_id]

        if statuses:
            threads = [t for t in threads if t.status in statuses]

        return len(threads)

    def update_objective(
        self,
        thread_id: ThreadId,
        title: str | None = None,
        description: str | None = None,
        due_at: datetime | None = None,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """更新Thread目标"""
        thread = self._get_existing_thread(thread_id)

        if title is not None:
            thread.objective.title = title
        if description is not None:
            thread.objective.description = description
        if due_at is not None:
            thread.objective.due_at = due_at

        thread.update_objective(thread.objective.model_copy(deep=True))

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.OBJECTIVE_UPDATED,
            actor_principal_id=actor_id,
            title="Objective updated",
            payload={
                "title": title,
                "description": description,
                "due_at": due_at.isoformat() if due_at else None,
            },
        )
        self.event_store.append(event)

        return thread, event

    def update_summary(
        self,
        thread_id: ThreadId,
        summary: str,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """更新Thread摘要"""
        thread = self._get_existing_thread(thread_id)
        thread.update_summary(summary)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.SUMMARY_UPDATED,
            actor_principal_id=actor_id,
            title="Summary updated",
            description=summary[:200],
        )
        self.event_store.append(event)

        return thread, event

    def update_risk_level(
        self,
        thread_id: ThreadId,
        risk_level: RiskLevel,
        reason: str,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """更新风险等级"""
        thread = self._get_existing_thread(thread_id)
        thread.set_risk_level(risk_level)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.RISK_LEVEL_CHANGED,
            actor_principal_id=actor_id,
            title=f"Risk level changed to {risk_level.value}",
            description=reason,
            payload={"risk_level": risk_level.value, "reason": reason},
        )
        self.event_store.append(event)

        return thread, event

    def update_delegation_profile(
        self,
        thread_id: ThreadId,
        profile: DelegationProfile,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """更新委托档位"""
        thread = self._get_existing_thread(thread_id)
        thread.set_delegation_profile(profile)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.DELEGATION_PROFILE_CHANGED,
            actor_principal_id=actor_id,
            title=f"Delegation profile changed to {profile.profile_name}",
            payload={"profile_name": profile.profile_name, "level": profile.level.value},
        )
        self.event_store.append(event)

        return thread, event

    def add_participant(
        self,
        thread_id: ThreadId,
        principal_id: UUID,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """添加参与者"""
        thread = self._get_existing_thread(thread_id)
        thread.add_participant(principal_id)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.PARTICIPANT_ADDED,
            actor_principal_id=actor_id,
            title="Participant added",
            payload={"principal_id": str(principal_id)},
        )
        self.event_store.append(event)

        return thread, event

    def remove_participant(
        self,
        thread_id: ThreadId,
        principal_id: UUID,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """移除参与者"""
        thread = self._get_existing_thread(thread_id)
        thread.remove_participant(principal_id)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.PARTICIPANT_REMOVED,
            actor_principal_id=actor_id,
            title="Participant removed",
            payload={"principal_id": str(principal_id)},
        )
        self.event_store.append(event)

        return thread, event

    def set_responsible(
        self,
        thread_id: ThreadId,
        principal_id: UUID,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """设置责任方"""
        thread = self._get_existing_thread(thread_id)
        thread.set_responsible(principal_id)

        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.RESPONSIBLE_CHANGED,
            actor_principal_id=actor_id,
            title="Responsible principal changed",
            payload={"principal_id": str(principal_id)},
        )
        self.event_store.append(event)

        return thread, event

    # 状态流转方法

    def start_planning(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """开始规划"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.start_planning(thread, actor_id)
        self.event_store.append(event)
        return thread, event

    def activate(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """激活"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.activate(thread, actor_id)
        self.event_store.append(event)
        return thread, event

    def pause(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """暂停"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.pause(thread, actor_id)
        self.event_store.append(event)
        return thread, event

    def resume(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """恢复"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.resume(thread, actor_id)
        self.event_store.append(event)
        return thread, event

    def wait_for_external(
        self,
        thread_id: ThreadId,
        reason: str | None = None,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """等待外部回复"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.wait_for_external(thread, actor_id, reason)
        self.event_store.append(event)
        return thread, event

    def wait_for_approval(
        self,
        thread_id: ThreadId,
        reason: str | None = None,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """等待审批"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.wait_for_approval(thread, actor_id, reason)
        self.event_store.append(event)
        return thread, event

    def block(
        self,
        thread_id: ThreadId,
        reason: str,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """阻塞"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.block(thread, reason, actor_id)
        self.event_store.append(event)
        return thread, event

    def escalate(
        self,
        thread_id: ThreadId,
        reason: str,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """升级到人工"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.escalate(thread, reason, actor_id)
        self.event_store.append(event)
        return thread, event

    def complete(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """完成"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.complete(thread, actor_id)
        self.event_store.append(event)
        return thread, event

    def cancel(
        self,
        thread_id: ThreadId,
        reason: str | None = None,
        actor_id: PrincipalId | None = None,
    ) -> tuple[Thread, ThreadEvent]:
        """取消"""
        thread = self._get_existing_thread(thread_id)
        thread, event = self.state_machine.cancel(thread, actor_id, reason)
        self.event_store.append(event)
        return thread, event

    def takeover(
        self,
        thread_id: ThreadId,
        actor_id: PrincipalId,
        reason: str = "User took over",
    ) -> tuple[Thread, ThreadEvent]:
        """接管线程"""
        thread = self._get_existing_thread(thread_id)

        # 创建接管事件
        event = ThreadEvent(
            thread_id=thread_id,
            event_type=EventType.THREAD_TAKEOVER,
            actor_principal_id=actor_id,
            title="Thread taken over by user",
            description=reason,
            payload={"reason": reason},
        )
        self.event_store.append(event)

        # 升级到escalated状态
        thread, status_event = self.escalate(thread_id, reason, actor_id)

        return thread, event

    # 辅助方法

    def _get_existing_thread(self, thread_id: ThreadId) -> Thread:
        thread = self._threads.get(thread_id)
        if not thread:
            raise ValueError(f"Thread not found: {thread_id}")
        return thread

    def get_event_store(self) -> EventStore:
        """获取事件存储"""
        return self.event_store

    def get_state_machine(self) -> ThreadStateMachine:
        """获取状态机"""
        return self.state_machine
