
"""
Unit Tests: ActionRun State Machine

Tests for AR-001 to AR-011
"""

from ...action_runtime.state_machine import ActionRunStateMachine, ActionRunStatus


class TestActionRunStateMachine:
    """ActionRun状态机测试"""

    def test_ar_001_complete_success_flow(self):
        """AR-001: 完整成功流程"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)

        sm.plan()
        assert sm.state == ActionRunStatus.PLANNED

        sm.submit_for_approval()
        assert sm.state == ActionRunStatus.READY_FOR_APPROVAL

        sm.approve()
        assert sm.state == ActionRunStatus.APPROVED

        sm.start_execution()
        assert sm.state == ActionRunStatus.EXECUTING

        sm.send_success()
        assert sm.state == ActionRunStatus.SENT

        sm.acknowledge()
        assert sm.state == ActionRunStatus.ACKNOWLEDGED
        assert sm.is_terminal is True

    def test_ar_002_plan_then_cancel(self):
        """AR-002: Planned状态取消"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)
        sm.plan()
        assert sm.state == ActionRunStatus.PLANNED

        sm.cancel()
        assert sm.state == ActionRunStatus.CANCELLED
        assert sm.is_terminal is True

    def test_ar_003_approval_then_reject(self):
        """AR-003: 审批阶段拒绝"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)
        sm.plan()
        sm.submit_for_approval()
        assert sm.state == ActionRunStatus.READY_FOR_APPROVAL

        sm.reject()
        assert sm.state == ActionRunStatus.CANCELLED

    def test_ar_005_retry_after_failure(self):
        """AR-005: 失败后重试"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)
        sm.plan()
        sm.submit_for_approval()
        sm.approve()
        sm.start_execution()

        sm.send_fail_retryable()
        assert sm.state == ActionRunStatus.FAILED_RETRYABLE
        assert sm.can_retry is True

        sm.retry()
        assert sm.state == ActionRunStatus.EXECUTING

        sm.send_success()
        sm.acknowledge()
        assert sm.state == ActionRunStatus.ACKNOWLEDGED

    def test_ar_007_max_retries_exceeded(self):
        """AR-007: 超过最大重试次数"""
        sm = ActionRunStateMachine(ActionRunStatus.FAILED_RETRYABLE)
        sm.max_retries_exceeded()
        assert sm.state == ActionRunStatus.FAILED_TERMINAL
        assert sm.is_terminal is True

    def test_ar_009_cancel_from_approved(self):
        """AR-009: Approved状态取消"""
        sm = ActionRunStateMachine(ActionRunStatus.APPROVED)
        assert sm.can_cancel is True
        sm.cancel()
        assert sm.state == ActionRunStatus.CANCELLED

    def test_state_history(self):
        """测试状态历史记录"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)
        sm.plan()
        sm.submit_for_approval()

        assert len(sm.state_history) == 3
        assert sm.state_history[0]["state"] == ActionRunStatus.CREATED
        assert sm.state_history[-1]["state"] == ActionRunStatus.READY_FOR_APPROVAL

    def test_available_triggers(self):
        """测试可用触发器"""
        sm = ActionRunStateMachine(ActionRunStatus.CREATED)
        assert "plan" in sm.get_available_triggers()

        sm.plan()
        triggers = sm.get_available_triggers()
        assert "submit_for_approval" in triggers
        assert "cancel" in triggers

    def test_cannot_cancel_from_executing(self):
        """测试不能从executing状态取消"""
        sm = ActionRunStateMachine(ActionRunStatus.EXECUTING)
        assert sm.can_cancel is False

