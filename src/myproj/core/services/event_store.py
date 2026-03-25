"""Event Store 服务 - append-only event log"""

from collections import defaultdict

from myproj.core.domain.event import EventId, EventType, ThreadEvent
from myproj.core.domain.thread import ThreadId


class AppendOnlyStore:
    """
    Append-only 事件存储接口

    保证：
    1. 事件只能追加，不能修改或删除
    2. 同一Thread内事件按序列号顺序排列
    3. 幂等性支持
    """

    def __init__(self) -> None:
        self._events: dict[ThreadId, list[ThreadEvent]] = defaultdict(list)
        self._sequence_counters: dict[ThreadId, int] = defaultdict(int)
        self._idempotency_keys: set[str] = set()
        self._events_by_id: dict[EventId, ThreadEvent] = {}

    def append(
        self,
        event: ThreadEvent,
        idempotency_key: str | None = None,
    ) -> ThreadEvent:
        """
        追加事件

        Args:
            event: 要追加的事件
            idempotency_key: 幂等键（可选）

        Returns:
            追加后的事件（包含分配的序列号）

        Raises:
            ValueError: 如果幂等键已存在
        """
        # 幂等性检查
        if idempotency_key:
            if idempotency_key in self._idempotency_keys:
                raise ValueError(f"Event with idempotency key {idempotency_key} already exists")
            self._idempotency_keys.add(idempotency_key)
            event.set_idempotency_key(idempotency_key)

        # 分配序列号
        sequence = self._sequence_counters[event.thread_id] + 1
        self._sequence_counters[event.thread_id] = sequence
        event.set_sequence_number(sequence)

        # 确保事件时间是单调递增的
        thread_events = self._events[event.thread_id]
        if thread_events:
            last_event = thread_events[-1]
            if event.occurred_at < last_event.occurred_at:
                event.occurred_at = last_event.occurred_at

        # 存储事件
        self._events[event.thread_id].append(event)
        self._events_by_id[event.id] = event

        return event

    def append_many(
        self,
        events: list[ThreadEvent],
        idempotency_key: str | None = None,
    ) -> list[ThreadEvent]:
        """批量追加事件"""
        if idempotency_key and idempotency_key in self._idempotency_keys:
            raise ValueError(f"Events with idempotency key {idempotency_key} already exist")

        if idempotency_key:
            self._idempotency_keys.add(idempotency_key)

        result = []
        for index, event in enumerate(events, start=1):
            batch_key = f"{idempotency_key}:{index}" if idempotency_key else None
            result.append(self.append(event, idempotency_key=batch_key))

        return result

    def get_by_thread(
        self,
        thread_id: ThreadId,
        from_sequence: int | None = None,
        to_sequence: int | None = None,
        event_types: list[EventType] | None = None,
        limit: int | None = None,
        reverse: bool = False,
    ) -> list[ThreadEvent]:
        """
        按Thread查询事件

        Args:
            thread_id: Thread ID
            from_sequence: 起始序列号（包含）
            to_sequence: 结束序列号（包含）
            event_types: 事件类型过滤
            limit: 返回数量限制
            reverse: 是否倒序

        Returns:
            事件列表
        """
        events = self._events.get(thread_id, [])

        # 序列号过滤
        if from_sequence is not None:
            events = [e for e in events if e.sequence_number >= from_sequence]
        if to_sequence is not None:
            events = [e for e in events if e.sequence_number <= to_sequence]

        # 事件类型过滤
        if event_types:
            events = [e for e in events if e.event_type in event_types]

        # 倒序
        if reverse:
            events = list(reversed(events))

        # 只返回可见事件
        events = [e for e in events if e.is_visible]

        # 数量限制
        if limit is not None:
            events = events[:limit]

        return events

    def get_by_id(self, event_id: EventId) -> ThreadEvent | None:
        """按ID查询事件"""
        return self._events_by_id.get(event_id)

    def get_latest_by_thread(self, thread_id: ThreadId) -> ThreadEvent | None:
        """获取Thread的最新事件"""
        events = self._events.get(thread_id, [])
        return events[-1] if events else None

    def get_sequence_number(self, thread_id: ThreadId) -> int:
        """获取Thread的当前序列号"""
        return self._sequence_counters.get(thread_id, 0)

    def exists_by_idempotency_key(self, key: str) -> bool:
        """检查幂等键是否存在"""
        return key in self._idempotency_keys

    def count_by_thread(self, thread_id: ThreadId) -> int:
        """统计Thread的事件数量"""
        return len(self._events.get(thread_id, []))

    def get_thread_ids(self) -> list[ThreadId]:
        """获取所有有事件的Thread ID"""
        return list(self._events.keys())


class EventStore(AppendOnlyStore):
    """
    事件存储服务

    在AppendOnlyStore基础上提供更丰富的查询和聚合能力
    """

    def get_status_history(self, thread_id: ThreadId) -> list[dict]:
        """获取状态变更历史"""
        events = self.get_by_thread(thread_id, event_types=[EventType.THREAD_STATUS_CHANGED])
        return [
            {
                "from_status": e.thread_status_before.value if e.thread_status_before else None,
                "to_status": e.thread_status_after.value if e.thread_status_after else None,
                "occurred_at": e.occurred_at,
                "actor": e.actor_principal_id,
                "reason": e.description,
            }
            for e in events
        ]

    def get_message_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取消息相关事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[
                EventType.MESSAGE_CREATED,
                EventType.MESSAGE_SENT,
                EventType.MESSAGE_READ,
                EventType.MESSAGE_APPROVED,
                EventType.MESSAGE_REJECTED,
            ],
        )

    def get_approval_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取审批相关事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[
                EventType.APPROVAL_REQUESTED,
                EventType.APPROVAL_GRANTED,
                EventType.APPROVAL_DENIED,
                EventType.APPROVAL_MODIFIED,
            ],
        )

    def get_risk_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取风险相关事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[
                EventType.RISK_DETECTED,
                EventType.RISK_LEVEL_CHANGED,
            ],
        )

    def get_policy_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取策略命中事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[EventType.POLICY_HIT],
        )

    def get_action_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取动作执行事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[
                EventType.ACTION_PLANNED,
                EventType.ACTION_EXECUTED,
                EventType.ACTION_FAILED,
                EventType.ACTION_CANCELLED,
            ],
        )

    def get_ai_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取AI相关事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[
                EventType.AI_DRAFT_GENERATED,
                EventType.AI_SUGGESTION_PROVIDED,
                EventType.AI_PLAN_GENERATED,
            ],
        )

    def get_error_events(self, thread_id: ThreadId) -> list[ThreadEvent]:
        """获取错误事件"""
        return self.get_by_thread(
            thread_id,
            event_types=[EventType.ERROR_OCCURRED],
        )

    def replay_events(
        self,
        thread_id: ThreadId,
        to_sequence: int | None = None,
    ) -> list[ThreadEvent]:
        """
        回放事件（用于重建状态）

        所有事件都会被返回，包括is_visible=False的事件
        """
        events = self._events.get(thread_id, [])
        if to_sequence is not None:
            events = [e for e in events if e.sequence_number <= to_sequence]
        return events

    def get_timeline(
        self,
        thread_id: ThreadId,
        limit: int | None = 100,
    ) -> list[dict]:
        """获取时间线视图"""
        events = self.get_by_thread(thread_id, limit=limit, reverse=True)
        return [
            {
                "id": str(e.id.value),
                "type": e.event_type.value,
                "title": e.title,
                "description": e.description,
                "occurred_at": e.occurred_at.isoformat(),
                "actor": str(e.actor_principal_id.value) if e.actor_principal_id else None,
                "sequence": e.sequence_number,
            }
            for e in events
        ]

    def get_summary(
        self,
        thread_id: ThreadId,
    ) -> dict:
        """获取事件摘要"""
        all_events = self.get_by_thread(thread_id)
        status_changes = [e for e in all_events if e.event_type == EventType.THREAD_STATUS_CHANGED]
        messages = [e for e in all_events if e.event_type.value.startswith("message_")]
        approvals = [e for e in all_events if e.event_type.value.startswith("approval_")]
        risks = [e for e in all_events if e.event_type.value.startswith("risk_")]

        return {
            "total_events": len(all_events),
            "status_changes": len(status_changes),
            "messages": len(messages),
            "approvals": len(approvals),
            "risks": len(risks),
            "first_event_at": all_events[0].occurred_at.isoformat() if all_events else None,
            "last_event_at": all_events[-1].occurred_at.isoformat() if all_events else None,
        }
