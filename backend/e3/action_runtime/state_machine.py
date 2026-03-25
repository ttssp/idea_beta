
"""
ActionRun State Machine

Defines the state machine for ActionRun objects.
"""

from enum import Enum
from typing import Callable, Optional, List, Dict, Any
from transitions import Machine


class ActionRunStatus(str, Enum):
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
        {"trigger": "plan", "source": ActionRunStatus.CREATED, "dest": ActionRunStatus.PLANNED},
        {"trigger": "submit_for_approval", "source": ActionRunStatus.PLANNED, "dest": ActionRunStatus.READY_FOR_APPROVAL},
        {"trigger": "approve", "source": ActionRunStatus.READY_FOR_APPROVAL, "dest": ActionRunStatus.APPROVED},
        {"trigger": "reject", "source": ActionRunStatus.READY_FOR_APPROVAL, "dest": ActionRunStatus.CANCELLED},
        {"trigger": "start_execution", "source": ActionRunStatus.APPROVED, "dest": ActionRunStatus.EXECUTING},
        {"trigger": "send_success", "source": ActionRunStatus.EXECUTING, "dest": ActionRunStatus.SENT},
        {"trigger": "send_fail_retryable", "source": ActionRunStatus.EXECUTING, "dest": ActionRunStatus.FAILED_RETRYABLE},
        {"trigger": "send_fail_terminal", "source": ActionRunStatus.EXECUTING, "dest": ActionRunStatus.FAILED_TERMINAL},
        {"trigger": "acknowledge", "source": ActionRunStatus.SENT, "dest": ActionRunStatus.ACKNOWLEDGED},
        {"trigger": "retry", "source": ActionRunStatus.FAILED_RETRYABLE, "dest": ActionRunStatus.EXECUTING},
        {"trigger": "max_retries_exceeded", "source": ActionRunStatus.FAILED_RETRYABLE, "dest": ActionRunStatus.FAILED_TERMINAL},
        {"trigger": "cancel", "source": [ActionRunStatus.PLANNED, ActionRunStatus.READY_FOR_APPROVAL, ActionRunStatus.APPROVED], "dest": ActionRunStatus.CANCELLED},
    ]

    def __init__(
        self,
        initial_state: str = ActionRunStatus.CREATED,
        state_change_callback: Optional[Callable[[str, str], None]] = None
    ):
        """
        初始化状态机

        Args:
            initial_state: 初始状态
            state_change_callback: 状态变更回调函数 (from_state, to_state)
        """
        self._state = initial_state
        self.state_history: List[Dict[str, Any]] = [{"state": initial_state, "timestamp": None}]
        self.state_change_callback = state_change_callback

        # 初始化transitions库的Machine
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=initial_state,
            after_state_change="_on_state_change",
            auto_transitions=False
        )

    def _on_state_change(self):
        """状态变更时的内部回调"""
        from datetime import datetime
        self.state_history.append({
            "state": self.state,
            "timestamp": datetime.utcnow().isoformat()
        })
        if self.state_change_callback:
            from_state = self.state_history[-2]["state"] if len(self.state_history) >= 2 else None
            self.state_change_callback(from_state, self.state)

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state

    @state.setter
    def state(self, value: str):
        """设置状态（供transitions库使用）"""
        self._state = value

    def can_transition_to(self, target_state: str) -> bool:
        """检查是否可以转换到目标状态"""
        try:
            return self.machine.get_transitions(dest=target_state, source=self.state) is not None
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

    def get_available_triggers(self) -> List[str]:
        """获取当前状态下可用的触发器"""
        return self.machine.get_triggers(self.state)

