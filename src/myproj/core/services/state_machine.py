"""Thread 状态机服务"""

from datetime import datetime
from typing import Optional

from myproj.core.domain.thread import (
    Thread,
    ThreadStatus,
    can_transition,
)
from myproj.core.domain.event import (
    ThreadEvent,
    EventType,
)


class StateTransitionError(Exception):
    """状态流转错误"""
    pass


class ThreadStateMachine:
    """Thread 状态机引擎"""

    def __init__(self) -> None:
        self._transition_handlers: dict = {}

    @classmethod
    def validate_transition(
        cls,
        from_status: ThreadStatus,
        to_status: ThreadStatus,
    ) -> bool:
        """验证状态流转是否合法"""
        return can_transition(from_status, to_status)

    @classmethod
    def get_valid_next_states(cls, from_status: ThreadStatus) -> set[ThreadStatus]:
        """获取所有合法的下一个状态"""
        from myproj.core.domain.thread import VALID_TRANSITIONS
        return VALID_TRANSITIONS.get(from_status, set())

    @classmethod
    def can_transition_to(cls, thread: Thread, to_status: ThreadStatus) -> bool:
        """检查Thread是否可以流转到目标状态"""
        if thread.is_terminal:
            return False
        return cls.validate_transition(thread.status, to_status)

    def transition(
        self,
        thread: Thread,
        to_status: ThreadStatus,
        reason: Optional[str] = None,
    ) -> tuple[Thread, ThreadEvent]:
        """
        执行状态流转

        Returns:
            (更新后的Thread, 状态变更事件)
        """
        if not self.can_transition_to(thread, to_status):
            raise StateTransitionError(
                f"Invalid transition: {thread.status} -> {to_status}"
            )

        from_status = thread.status
        thread.transition_to(to_status)

        # 创建状态变更事件
        event = ThreadEvent.create_status_changed(
            thread_id=thread.id,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
        )

        return thread, event

    def pause(
        self,
        thread: Thread,
    ) -> tuple[Thread, ThreadEvent]:
        """暂停线程"""
        if not thread.can_be_paused:
            raise StateTransitionError(f"Cannot pause thread in status: {thread.status}")

        return self.transition(thread, ThreadStatus.PAUSED, "Paused by user")

    def resume(
        self,
        thread: Thread,
    ) -> tuple[Thread, ThreadEvent]:
        """恢复线程"""
        if not thread.can_be_resumed:
            raise StateTransitionError(f"Cannot resume thread in status: {thread.status}")

        return self.transition(thread, ThreadStatus.ACTIVE, "Resumed by user")

    def escalate(
        self,
        thread: Thread,
        reason: str,
    ) -> tuple[Thread, ThreadEvent]:
        """升级到人工"""
        if thread.is_terminal:
            raise StateTransitionError("Cannot escalate terminal thread")

        thread.escalate(reason)

        event = ThreadEvent.create_escalated(
            thread_id=thread.id,
            reason=reason,
        )

        return thread, event

    def complete(
        self,
        thread: Thread,
    ) -> tuple[Thread, ThreadEvent]:
        """完成线程"""
        if thread.is_terminal:
            raise StateTransitionError("Thread is already terminal")

        return self.transition(thread, ThreadStatus.COMPLETED, "Thread completed")

    def cancel(
        self,
        thread: Thread,
        reason: Optional[str] = None,
    ) -> tuple[Thread, ThreadEvent]:
        """取消线程"""
        if thread.is_terminal:
            raise StateTransitionError("Thread is already terminal")

        return self.transition(thread, ThreadStatus.CANCELLED, reason or "Thread cancelled")

    def start_planning(
        self,
        thread: Thread,
    ) -> tuple[Thread, ThreadEvent]:
        """开始规划"""
        return self.transition(thread, ThreadStatus.PLANNING, "Started planning")

    def activate(
        self,
        thread: Thread,
    ) -> tuple[Thread, ThreadEvent]:
        """激活线程"""
        return self.transition(thread, ThreadStatus.ACTIVE, "Thread activated")

    def wait_for_external(
        self,
        thread: Thread,
        reason: Optional[str] = None,
    ) -> tuple[Thread, ThreadEvent]:
        """等待外部回复"""
        return self.transition(
            thread,
            ThreadStatus.AWAITING_EXTERNAL,
            reason or "Waiting for external response",
        )

    def wait_for_approval(
        self,
        thread: Thread,
        reason: Optional[str] = None,
    ) -> tuple[Thread, ThreadEvent]:
        """等待审批"""
        return self.transition(
            thread,
            ThreadStatus.AWAITING_APPROVAL,
            reason or "Waiting for approval",
        )

    def block(
        self,
        thread: Thread,
        reason: str,
    ) -> tuple[Thread, ThreadEvent]:
        """阻塞线程"""
        return self.transition(
            thread,
            ThreadStatus.BLOCKED,
            f"Blocked: {reason}",
        )
