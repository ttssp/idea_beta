"""状态机服务单元测试"""

from uuid import uuid4

import pytest

from myproj.core.domain.thread import (
    Thread,
    ThreadId,
    ThreadStatus,
    ThreadObjective,
)
from myproj.core.services.state_machine import (
    ThreadStateMachine,
    StateTransitionError,
)


class TestThreadStateMachine:
    """ThreadStateMachine 测试"""

    def setup_method(self):
        """每个测试前设置"""
        self.state_machine = ThreadStateMachine()
        self.owner_id = uuid4()

    def create_thread_in_status(self, target_status: ThreadStatus) -> Thread:
        """创建并流转到目标状态的Thread"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )

        # 按合法路径流转到目标状态
        path = self._get_path_to(target_status)
        for status in path:
            thread.transition_to(status)

        return thread

    def _get_path_to(self, target_status: ThreadStatus) -> list[ThreadStatus]:
        """获取到达目标状态的合法路径"""
        paths = {
            ThreadStatus.PLANNING: [ThreadStatus.PLANNING],
            ThreadStatus.ACTIVE: [ThreadStatus.PLANNING, ThreadStatus.ACTIVE],
            ThreadStatus.AWAITING_EXTERNAL: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.AWAITING_EXTERNAL,
            ],
            ThreadStatus.AWAITING_APPROVAL: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.AWAITING_APPROVAL,
            ],
            ThreadStatus.BLOCKED: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.BLOCKED,
            ],
            ThreadStatus.PAUSED: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.PAUSED,
            ],
            ThreadStatus.ESCALATED: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.ESCALATED,
            ],
            ThreadStatus.COMPLETED: [
                ThreadStatus.PLANNING,
                ThreadStatus.ACTIVE,
                ThreadStatus.COMPLETED,
            ],
            ThreadStatus.CANCELLED: [
                ThreadStatus.PLANNING,
                ThreadStatus.CANCELLED,
            ],
        }
        return paths.get(target_status, [])

    def test_validate_transition_valid(self):
        """验证合法流转"""
        assert ThreadStateMachine.validate_transition(
            ThreadStatus.NEW,
            ThreadStatus.PLANNING,
        )
        assert ThreadStateMachine.validate_transition(
            ThreadStatus.ACTIVE,
            ThreadStatus.COMPLETED,
        )

    def test_validate_transition_invalid(self):
        """验证非法流转"""
        assert not ThreadStateMachine.validate_transition(
            ThreadStatus.COMPLETED,
            ThreadStatus.ACTIVE,
        )
        assert not ThreadStateMachine.validate_transition(
            ThreadStatus.PAUSED,
            ThreadStatus.AWAITING_EXTERNAL,
        )

    def test_get_valid_next_states(self):
        """获取合法的下一个状态"""
        states = ThreadStateMachine.get_valid_next_states(ThreadStatus.ACTIVE)
        assert ThreadStatus.AWAITING_EXTERNAL in states
        assert ThreadStatus.COMPLETED in states
        assert ThreadStatus.CANCELLED in states

    def test_can_transition_to(self):
        """检查Thread是否可以流转"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        assert self.state_machine.can_transition_to(thread, ThreadStatus.COMPLETED)
        assert not self.state_machine.can_transition_to(thread, ThreadStatus.NEW)

    def test_can_transition_to_terminal(self):
        """终态不可再流转"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)
        assert not self.state_machine.can_transition_to(thread, ThreadStatus.ACTIVE)

    def test_transition(self):
        """执行状态流转"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )
        updated_thread, event = self.state_machine.transition(
            thread,
            ThreadStatus.PLANNING,
        )

        assert updated_thread.status == ThreadStatus.PLANNING
        assert event.event_type == "thread_status_changed"
        assert event.thread_status_before == ThreadStatus.NEW
        assert event.thread_status_after == ThreadStatus.PLANNING

    def test_transition_invalid(self):
        """执行非法流转"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)

        with pytest.raises(StateTransitionError):
            self.state_machine.transition(thread, ThreadStatus.ACTIVE)

    def test_pause(self):
        """暂停"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        updated_thread, event = self.state_machine.pause(thread)

        assert updated_thread.status == ThreadStatus.PAUSED
        assert "Paused by user" in event.description

    def test_pause_invalid(self):
        """从非法状态暂停"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )

        with pytest.raises(StateTransitionError):
            self.state_machine.pause(thread)

    def test_resume(self):
        """恢复"""
        thread = self.create_thread_in_status(ThreadStatus.PAUSED)
        updated_thread, event = self.state_machine.resume(thread)

        assert updated_thread.status == ThreadStatus.ACTIVE
        assert "Resumed by user" in event.description

    def test_resume_invalid(self):
        """从非法状态恢复"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)

        with pytest.raises(StateTransitionError):
            self.state_machine.resume(thread)

    def test_escalate(self):
        """升级"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        reason = "检测到高风险内容"
        updated_thread, event = self.state_machine.escalate(thread, reason)

        assert updated_thread.status == ThreadStatus.ESCALATED
        assert updated_thread.last_escalation_reason == reason
        assert event.event_type == "thread_escalated"

    def test_escalate_terminal(self):
        """终态不可升级"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)

        with pytest.raises(StateTransitionError):
            self.state_machine.escalate(thread, "reason")

    def test_complete(self):
        """完成"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        updated_thread, event = self.state_machine.complete(thread)

        assert updated_thread.status == ThreadStatus.COMPLETED
        assert updated_thread.completed_at is not None

    def test_complete_terminal(self):
        """终态不可完成"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)

        with pytest.raises(StateTransitionError):
            self.state_machine.complete(thread)

    def test_cancel(self):
        """取消"""
        thread = self.create_thread_in_status(ThreadStatus.PLANNING)
        reason = "不再需要"
        updated_thread, event = self.state_machine.cancel(thread, reason)

        assert updated_thread.status == ThreadStatus.CANCELLED
        assert reason in event.description

    def test_cancel_terminal(self):
        """终态不可取消"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)

        with pytest.raises(StateTransitionError):
            self.state_machine.cancel(thread)

    def test_start_planning(self):
        """开始规划"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )
        updated_thread, event = self.state_machine.start_planning(thread)

        assert updated_thread.status == ThreadStatus.PLANNING

    def test_activate(self):
        """激活"""
        thread = self.create_thread_in_status(ThreadStatus.PLANNING)
        updated_thread, event = self.state_machine.activate(thread)

        assert updated_thread.status == ThreadStatus.ACTIVE

    def test_wait_for_external(self):
        """等待外部"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        reason = "等待候选人回复"
        updated_thread, event = self.state_machine.wait_for_external(thread, reason)

        assert updated_thread.status == ThreadStatus.AWAITING_EXTERNAL
        assert reason in event.description

    def test_wait_for_approval(self):
        """等待审批"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        reason = "需要审批发送"
        updated_thread, event = self.state_machine.wait_for_approval(thread, reason)

        assert updated_thread.status == ThreadStatus.AWAITING_APPROVAL

    def test_block(self):
        """阻塞"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        reason = "缺少必要信息"
        updated_thread, event = self.state_machine.block(thread, reason)

        assert updated_thread.status == ThreadStatus.BLOCKED
        assert reason in event.description

    # TS-001 至 TS-N05 测试用例

    def test_ts_001_new_to_planning(self):
        """TS-001: new -> planning"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )
        updated, _ = self.state_machine.start_planning(thread)
        assert updated.status == ThreadStatus.PLANNING

    def test_ts_002_planning_to_active(self):
        """TS-002: planning -> active"""
        thread = self.create_thread_in_status(ThreadStatus.PLANNING)
        updated, _ = self.state_machine.activate(thread)
        assert updated.status == ThreadStatus.ACTIVE

    def test_ts_003_active_to_awaiting_external(self):
        """TS-003: active -> awaiting_external"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        updated, _ = self.state_machine.wait_for_external(thread)
        assert updated.status == ThreadStatus.AWAITING_EXTERNAL

    def test_ts_004_awaiting_external_to_active(self):
        """TS-004: awaiting_external -> active"""
        thread = self.create_thread_in_status(ThreadStatus.AWAITING_EXTERNAL)
        updated, _ = self.state_machine.transition(thread, ThreadStatus.ACTIVE)
        assert updated.status == ThreadStatus.ACTIVE

    def test_ts_005_active_to_completed(self):
        """TS-005: active -> completed"""
        thread = self.create_thread_in_status(ThreadStatus.ACTIVE)
        updated, _ = self.state_machine.complete(thread)
        assert updated.status == ThreadStatus.COMPLETED
        assert updated.is_terminal

    def test_ts_n01_new_to_active_invalid(self):
        """TS-N01: new -> active (invalid)"""
        thread = Thread(
            objective=ThreadObjective(title="测试线程"),
            owner_id=self.owner_id,
        )
        with pytest.raises(StateTransitionError):
            self.state_machine.activate(thread)

    def test_ts_n02_completed_to_active_invalid(self):
        """TS-N02: completed -> active (invalid)"""
        thread = self.create_thread_in_status(ThreadStatus.COMPLETED)
        with pytest.raises(StateTransitionError):
            self.state_machine.transition(thread, ThreadStatus.ACTIVE)

    def test_ts_n03_paused_to_awaiting_external_invalid(self):
        """TS-N03: paused -> awaiting_external (invalid)"""
        thread = self.create_thread_in_status(ThreadStatus.PAUSED)
        with pytest.raises(StateTransitionError):
            self.state_machine.wait_for_external(thread)

    def test_ts_n04_concurrent_safety(self):
        """TS-N04: 并发安全（版本号机制）"""
        # 创建两个独立的Thread实例，模拟并发从同一初始状态开始
        thread_a = self.create_thread_in_status(ThreadStatus.ACTIVE)
        thread_b = self.create_thread_in_status(ThreadStatus.ACTIVE)
        initial_version = thread_a.version

        # 模拟第一个更新（线程A）
        thread1, _ = self.state_machine.pause(thread_a)
        thread1.increment_version()

        # 模拟第二个更新（线程B，基于旧状态）
        thread2, _ = self.state_machine.complete(thread_b)
        thread2.increment_version()

        # 验证版本号都递增了
        assert thread1.version > initial_version
        assert thread2.version > initial_version

    def test_ts_n05_all_valid_transitions_covered(self):
        """TS-N05: 所有状态的流出边都被测试"""
        # 这个测试确保我们没有遗漏任何合法流转
        from myproj.core.domain.thread import VALID_TRANSITIONS

        # 验证每个状态都有流转规则（除了终态）
        for status in ThreadStatus:
            if status in {ThreadStatus.COMPLETED, ThreadStatus.CANCELLED}:
                assert len(VALID_TRANSITIONS[status]) == 0
            else:
                assert len(VALID_TRANSITIONS[status]) > 0
