"""Event Store 单元测试"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import pytest

from myproj.core.domain.thread import ThreadId, ThreadStatus
from myproj.core.domain.event import (
    ThreadEvent,
    EventId,
    EventType,
)
from myproj.core.services.event_store import EventStore, AppendOnlyStore


class TestAppendOnlyStore:
    """AppendOnlyStore 基础测试"""

    def setup_method(self):
        """每个测试前设置"""
        self.store = AppendOnlyStore()
        self.thread_id = ThreadId.generate()

    def create_event(self, thread_id: Optional[ThreadId] = None, **kwargs) -> ThreadEvent:
        """创建测试事件"""
        tid = thread_id or self.thread_id
        defaults = {
            "thread_id": tid,
            "event_type": EventType.THREAD_CREATED,
            "title": "Test Event",
        }
        defaults.update(kwargs)
        return ThreadEvent(**defaults)

    def test_append(self):
        """追加事件"""
        event = self.create_event()
        stored = self.store.append(event)

        assert stored.sequence_number == 1
        assert stored.id == event.id

    def test_append_assigns_sequence(self):
        """追加分配序列号"""
        event1 = self.create_event()
        event2 = self.create_event()

        stored1 = self.store.append(event1)
        stored2 = self.store.append(event2)

        assert stored1.sequence_number == 1
        assert stored2.sequence_number == 2

    def test_append_idempotency(self):
        """幂等性"""
        event = self.create_event()
        idempotency_key = "test-key-123"

        self.store.append(event, idempotency_key=idempotency_key)

        with pytest.raises(ValueError):
            self.store.append(event, idempotency_key=idempotency_key)

    def test_append_idempotency_check(self):
        """幂等键检查"""
        key = "test-key"
        assert not self.store.exists_by_idempotency_key(key)

        event = self.create_event()
        self.store.append(event, idempotency_key=key)

        assert self.store.exists_by_idempotency_key(key)

    def test_append_many(self):
        """批量追加"""
        thread_id = ThreadId.generate()
        events = [
            self.create_event(thread_id=thread_id, title="Event 1"),
            self.create_event(thread_id=thread_id, title="Event 2"),
            self.create_event(thread_id=thread_id, title="Event 3"),
        ]

        stored = self.store.append_many(events)

        assert len(stored) == 3
        assert stored[0].sequence_number == 1
        assert stored[2].sequence_number == 3

    def test_get_by_thread(self):
        """按Thread查询"""
        thread_id1 = ThreadId.generate()
        thread_id2 = ThreadId.generate()

        self.store.append(self.create_event(thread_id=thread_id1))
        self.store.append(self.create_event(thread_id=thread_id1))
        self.store.append(self.create_event(thread_id=thread_id2))

        events1 = self.store.get_by_thread(thread_id1)
        events2 = self.store.get_by_thread(thread_id2)

        assert len(events1) == 2
        assert len(events2) == 1

    def test_get_by_thread_sequence_range(self):
        """按序列号范围查询"""
        for i in range(10):
            self.store.append(self.create_event(title=f"Event {i}"))

        events = self.store.get_by_thread(
            self.thread_id,
            from_sequence=3,
            to_sequence=7,
        )

        assert len(events) == 5
        assert events[0].sequence_number == 3
        assert events[-1].sequence_number == 7

    def test_get_by_thread_event_types(self):
        """按事件类型过滤"""
        self.store.append(self.create_event(event_type=EventType.THREAD_CREATED))
        self.store.append(self.create_event(event_type=EventType.MESSAGE_SENT))
        self.store.append(self.create_event(event_type=EventType.THREAD_STATUS_CHANGED))
        self.store.append(self.create_event(event_type=EventType.MESSAGE_SENT))

        events = self.store.get_by_thread(
            self.thread_id,
            event_types=[EventType.MESSAGE_SENT],
        )

        assert len(events) == 2
        for e in events:
            assert e.event_type == EventType.MESSAGE_SENT

    def test_get_by_thread_limit(self):
        """数量限制"""
        for i in range(20):
            self.store.append(self.create_event(title=f"Event {i}"))

        events = self.store.get_by_thread(self.thread_id, limit=5)

        assert len(events) == 5

    def test_get_by_thread_reverse(self):
        """倒序"""
        for i in range(5):
            self.store.append(self.create_event(title=f"Event {i}"))

        events_forward = self.store.get_by_thread(self.thread_id, reverse=False)
        events_reverse = self.store.get_by_thread(self.thread_id, reverse=True)

        assert events_forward[0].sequence_number == 1
        assert events_reverse[0].sequence_number == 5

    def test_get_by_id(self):
        """按ID查询"""
        event = self.create_event()
        stored = self.store.append(event)

        retrieved = self.store.get_by_id(stored.id)

        assert retrieved is not None
        assert retrieved.id == stored.id

    def test_get_by_id_not_found(self):
        """ID不存在"""
        event_id = EventId.generate()
        retrieved = self.store.get_by_id(event_id)

        assert retrieved is None

    def test_get_latest_by_thread(self):
        """获取最新事件"""
        for i in range(5):
            self.store.append(self.create_event(title=f"Event {i}"))

        latest = self.store.get_latest_by_thread(self.thread_id)

        assert latest is not None
        assert latest.sequence_number == 5

    def test_get_latest_by_thread_empty(self):
        """没有事件时获取最新"""
        thread_id = ThreadId.generate()
        latest = self.store.get_latest_by_thread(thread_id)

        assert latest is None

    def test_get_sequence_number(self):
        """获取当前序列号"""
        assert self.store.get_sequence_number(self.thread_id) == 0

        self.store.append(self.create_event())
        assert self.store.get_sequence_number(self.thread_id) == 1

        self.store.append(self.create_event())
        assert self.store.get_sequence_number(self.thread_id) == 2

    def test_count_by_thread(self):
        """统计事件数量"""
        for i in range(7):
            self.store.append(self.create_event())

        count = self.store.count_by_thread(self.thread_id)

        assert count == 7

    def test_get_thread_ids(self):
        """获取所有有事件的Thread ID"""
        thread_id1 = ThreadId.generate()
        thread_id2 = ThreadId.generate()
        thread_id3 = ThreadId.generate()

        self.store.append(self.create_event(thread_id=thread_id1))
        self.store.append(self.create_event(thread_id=thread_id2))

        thread_ids = self.store.get_thread_ids()

        assert thread_id1 in thread_ids
        assert thread_id2 in thread_ids
        assert thread_id3 not in thread_ids

    def test_append_monotonic_time(self):
        """追加事件时间单调递增"""
        thread_id = ThreadId.generate()

        # 创建带旧时间的事件
        event1 = self.create_event(thread_id=thread_id)
        event2 = self.create_event(
            thread_id=thread_id,
            occurred_at=event1.occurred_at - timedelta(hours=1),
        )

        stored1 = self.store.append(event1)
        stored2 = self.store.append(event2)

        # 第二个事件的时间应该被调整为不早于第一个
        assert stored2.occurred_at >= stored1.occurred_at

    def test_visibility(self):
        """事件可见性"""
        event = self.create_event()
        stored = self.store.append(event)

        assert stored.is_visible

        # 查询时只返回可见事件
        events = self.store.get_by_thread(self.thread_id)
        assert len(events) == 1

        # 隐藏事件
        stored.hide()

        # 隐藏后应该不会被查询到
        events = self.store.get_by_thread(self.thread_id)
        assert len(events) == 0


class TestEventStore:
    """EventStore 高级功能测试"""

    def setup_method(self):
        """每个测试前设置"""
        self.store = EventStore()
        self.thread_id = ThreadId.generate()

    def create_event(self, event_type: EventType, **kwargs) -> ThreadEvent:
        """创建测试事件"""
        defaults = {
            "thread_id": self.thread_id,
            "event_type": event_type,
            "title": f"{event_type.value} event",
        }
        defaults.update(kwargs)
        return ThreadEvent(**defaults)

    def test_get_status_history(self):
        """获取状态变更历史"""
        self.store.append(self.create_event(EventType.THREAD_CREATED))
        self.store.append(self.create_event(
            EventType.THREAD_STATUS_CHANGED,
            thread_status_before=ThreadStatus.NEW,
            thread_status_after=ThreadStatus.PLANNING,
        ))
        self.store.append(self.create_event(
            EventType.THREAD_STATUS_CHANGED,
            thread_status_before=ThreadStatus.PLANNING,
            thread_status_after=ThreadStatus.ACTIVE,
        ))

        history = self.store.get_status_history(self.thread_id)

        assert len(history) == 2
        assert history[0]["from_status"] == "new"
        assert history[0]["to_status"] == "planning"
        assert history[1]["to_status"] == "active"

    def test_get_message_events(self):
        """获取消息相关事件"""
        self.store.append(self.create_event(EventType.THREAD_CREATED))
        self.store.append(self.create_event(EventType.MESSAGE_CREATED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))
        self.store.append(self.create_event(EventType.MESSAGE_READ))
        self.store.append(self.create_event(EventType.THREAD_STATUS_CHANGED))

        events = self.store.get_message_events(self.thread_id)

        assert len(events) == 3
        for e in events:
            assert e.event_type.value.startswith("message_")

    def test_get_approval_events(self):
        """获取审批相关事件"""
        self.store.append(self.create_event(EventType.APPROVAL_REQUESTED))
        self.store.append(self.create_event(EventType.APPROVAL_GRANTED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))

        events = self.store.get_approval_events(self.thread_id)

        assert len(events) == 2

    def test_get_risk_events(self):
        """获取风险相关事件"""
        self.store.append(self.create_event(EventType.RISK_DETECTED))
        self.store.append(self.create_event(EventType.RISK_LEVEL_CHANGED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))

        events = self.store.get_risk_events(self.thread_id)

        assert len(events) == 2

    def test_get_policy_events(self):
        """获取策略命中事件"""
        self.store.append(self.create_event(EventType.POLICY_HIT))
        self.store.append(self.create_event(EventType.POLICY_HIT))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))

        events = self.store.get_policy_events(self.thread_id)

        assert len(events) == 2

    def test_get_action_events(self):
        """获取动作执行事件"""
        self.store.append(self.create_event(EventType.ACTION_PLANNED))
        self.store.append(self.create_event(EventType.ACTION_EXECUTED))
        self.store.append(self.create_event(EventType.ACTION_FAILED))

        events = self.store.get_action_events(self.thread_id)

        assert len(events) == 3

    def test_get_ai_events(self):
        """获取AI相关事件"""
        self.store.append(self.create_event(EventType.AI_DRAFT_GENERATED))
        self.store.append(self.create_event(EventType.AI_SUGGESTION_PROVIDED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))

        events = self.store.get_ai_events(self.thread_id)

        assert len(events) == 2

    def test_get_error_events(self):
        """获取错误事件"""
        self.store.append(self.create_event(EventType.ERROR_OCCURRED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))

        events = self.store.get_error_events(self.thread_id)

        assert len(events) == 1

    def test_replay_events(self):
        """回放事件（包含不可见事件）"""
        event1 = self.create_event(EventType.THREAD_CREATED)
        event2 = self.create_event(EventType.MESSAGE_SENT)
        event3 = self.create_event(EventType.THREAD_COMPLETED)

        stored1 = self.store.append(event1)
        stored2 = self.store.append(event2)
        stored3 = self.store.append(event3)

        # 隐藏一个事件
        stored2.hide()

        # 普通查询不包含隐藏事件
        normal = self.store.get_by_thread(self.thread_id)
        assert len(normal) == 2

        # 回放包含所有事件
        replayed = self.store.replay_events(self.thread_id)
        assert len(replayed) == 3

    def test_replay_events_to_sequence(self):
        """回放到指定序列号"""
        for i in range(10):
            self.store.append(self.create_event(EventType.THREAD_UPDATED, title=f"Event {i}"))

        replayed = self.store.replay_events(self.thread_id, to_sequence=5)

        assert len(replayed) == 5
        assert replayed[-1].sequence_number == 5

    def test_get_timeline(self):
        """获取时间线视图"""
        self.store.append(self.create_event(EventType.THREAD_CREATED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))
        self.store.append(self.create_event(EventType.THREAD_COMPLETED))

        timeline = self.store.get_timeline(self.thread_id)

        assert len(timeline) == 3
        assert "id" in timeline[0]
        assert "type" in timeline[0]
        assert "occurred_at" in timeline[0]

    def test_get_summary(self):
        """获取事件摘要"""
        self.store.append(self.create_event(EventType.THREAD_CREATED))
        self.store.append(self.create_event(EventType.THREAD_STATUS_CHANGED))
        self.store.append(self.create_event(EventType.THREAD_STATUS_CHANGED))
        self.store.append(self.create_event(EventType.MESSAGE_SENT))
        self.store.append(self.create_event(EventType.MESSAGE_CREATED))
        self.store.append(self.create_event(EventType.APPROVAL_REQUESTED))
        self.store.append(self.create_event(EventType.RISK_DETECTED))

        summary = self.store.get_summary(self.thread_id)

        assert summary["total_events"] == 7
        assert summary["status_changes"] == 2
        assert summary["messages"] == 2
        assert summary["approvals"] == 1
        assert summary["risks"] == 1
        assert summary["first_event_at"] is not None
        assert summary["last_event_at"] is not None

    def test_get_summary_empty(self):
        """空Thread的摘要"""
        thread_id = ThreadId.generate()
        summary = self.store.get_summary(thread_id)

        assert summary["total_events"] == 0
        assert summary["first_event_at"] is None
        assert summary["last_event_at"] is None

    def test_exactly_once_guarantee(self):
        """exactly-once保证测试"""
        # 使用幂等键确保同一事件不会被处理两次
        thread_id = ThreadId.generate()
        idempotency_key = "unique-key-12345"

        event1 = self.create_event(
            thread_id=thread_id,
            event_type=EventType.MESSAGE_SENT,
        )

        # 第一次追加
        stored1 = self.store.append(event1, idempotency_key=idempotency_key)
        assert stored1.sequence_number == 1

        # 第二次追加（使用相同幂等键）应该失败
        event2 = self.create_event(
            thread_id=thread_id,
            event_type=EventType.MESSAGE_SENT,
        )

        with pytest.raises(ValueError):
            self.store.append(event2, idempotency_key=idempotency_key)

        # 验证只有一个事件
        count = self.store.count_by_thread(thread_id)
        assert count == 1
