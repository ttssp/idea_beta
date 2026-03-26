
"""
ActionRun State Machine

Defines the state machine for ActionRun objects.
"""

from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from transitions import Machine


class ActionRunStatus(StrEnum):
    """ActionRun状态枚举"""
    CREATED = "created"
    PLANNED = "planned"
    READY_FOR_APPROVAL = "ready_for_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    CANCELLED = "cancelled"


class ActionRunStateMachine:
    """
    ActionRun状态机

    状态流转图:
        created → planned → ready_for_approval → approved → executing → sent → acknowledged
                      ↓                   ↓          ↓
                 cancelled           cancelled   failed_retryable ←→ failed_terminal
    """

    # 状态列表
    states = [s.value for s in ActionRunStatus]

    # 状态流转定义
    transitions = [
        {"trigger": "plan", "source": ActionRunStatus.CREATED.value, "dest": ActionRunStatus.PLANNED.value},
        {"trigger": "submit_for_approval", "source": ActionRunStatus.PLANNED.value, "dest": ActionRunStatus.READY_FOR_APPROVAL.value},
        {"trigger": "approve", "source": ActionRunStatus.READY_FOR_APPROVAL.value, "dest": ActionRunStatus.APPROVED.value},
        {"trigger": "reject", "source": ActionRunStatus.READY_FOR_APPROVAL.value, "dest": ActionRunStatus.CANCELLED.value},
        {"trigger": "start_execution", "source": ActionRunStatus.APPROVED.value, "dest": ActionRunStatus.EXECUTING.value},
        {"trigger": "send_success", "source": ActionRunStatus.EXECUTING.value, "dest": ActionRunStatus.SENT.value},
        {"trigger": "send_fail_retryable", "source": ActionRunStatus.EXECUTING.value, "dest": ActionRunStatus.FAILED_RETRYABLE.value},
        {"trigger": "send_fail_terminal", "source": ActionRunStatus.EXECUTING.value, "dest": ActionRunStatus.FAILED_TERMINAL.value},
        {"trigger": "acknowledge", "source": ActionRunStatus.SENT.value, "dest": ActionRunStatus.ACKNOWLEDGED.value},
        {"trigger": "retry", "source": ActionRunStatus.FAILED_RETRYABLE.value, "dest": ActionRunStatus.EXECUTING.value},
        {"trigger": "max_retries_exceeded", "source": ActionRunStatus.FAILED_RETRYABLE.value, "dest": ActionRunStatus.FAILED_TERMINAL.value},
        {
            "trigger": "cancel",
            "source": [
                ActionRunStatus.PLANNED.value,
                ActionRunStatus.READY_FOR_APPROVAL.value,
                ActionRunStatus.APPROVED.value,
            ],
            "dest": ActionRunStatus.CANCELLED.value,
        },
    ]

    def __init__(
        self,
        initial_state: ActionRunStatus | str = ActionRunStatus.CREATED,
        state_change_callback: Callable[[str | None, str], None] | None = None,
    ):
        """
        初始化状态机

        Args:
            initial_state: 初始状态
            state_change_callback: 状态变更回调函数 (from_state, to_state)
        """
        initial_value = initial_state.value if isinstance(initial_state, ActionRunStatus) else initial_state
        self._state = initial_value
        self.state_history: list[dict[str, Any]] = [
            {"state": initial_value, "timestamp": None}
        ]
        self.state_change_callback = state_change_callback

        # 初始化transitions库的Machine
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=initial_value,
            after_state_change="_on_state_change",
            auto_transitions=False
        )

    def _on_state_change(self):
        """状态变更时的内部回调"""
        self.state_history.append({
            "state": self.state,
            "timestamp": datetime.now(UTC).isoformat()
        })
        if self.state_change_callback:
            from_state = self.state_history[-2]["state"] if len(self.state_history) >= 2 else None
            self.state_change_callback(from_state, self.state)

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state

    @state.setter
    def state(self, value: ActionRunStatus | str):
        """设置状态（供transitions库使用）"""
        self._state = value.value if isinstance(value, ActionRunStatus) else value

    def can_transition_to(self, target_state: ActionRunStatus | str) -> bool:
        """检查是否可以转换到目标状态"""
        try:
            target_value = target_state.value if isinstance(target_state, ActionRunStatus) else target_state
            return bool(self.machine.get_transitions(dest=target_value, source=self._state))
        except Exception:
            return False

    @property
    def is_terminal(self) -> bool:
        """是否是终态"""
        return self.state in [
            ActionRunStatus.ACKNOWLEDGED,
            ActionRunStatus.FAILED_TERMINAL,
            ActionRunStatus.CANCELLED
        ]

    @property
    def can_cancel(self) -> bool:
        """是否可以取消"""
        return self.state in [
            ActionRunStatus.PLANNED,
            ActionRunStatus.READY_FOR_APPROVAL,
            ActionRunStatus.APPROVED
        ]

    @property
    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.state == ActionRunStatus.FAILED_RETRYABLE

    def get_available_triggers(self) -> list[str]:
        """获取当前状态下可用的触发器"""
        return self.machine.get_triggers(self._state)
