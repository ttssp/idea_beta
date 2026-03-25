"""Thread 领域模型单元测试"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from myproj.core.domain.thread import (
    Thread,
    ThreadId,
    ThreadStatus,
    ThreadObjective,
    DelegationProfile,
    DelegationLevel,
    RiskLevel,
    can_transition,
    VALID_TRANSITIONS,
)
from myproj.core.domain.principal import PrincipalId


class TestThreadId:
    """ThreadId 值对象测试"""

    def test_generate(self):
        """生成ThreadId"""
        thread_id = ThreadId.generate()
        assert thread_id.value is not None

    def test_equality(self):
        """相等性比较"""
        uuid = uuid4()
        id1 = ThreadId(value=uuid)
        id2 = ThreadId(value=uuid)
        id3 = ThreadId.generate()

        assert id1 == id2
        assert id1 != id3

    def test_hash(self):
        """哈希值"""
        uuid = uuid4()
        thread_id = ThreadId(value=uuid)
        assert hash(thread_id) == hash(uuid)


class TestThreadObjective:
    """ThreadObjective 值对象测试"""

    def test_create(self):
        """创建目标"""
        objective = ThreadObjective(
            title="协调终面时间",
            description="与候选人和面试官协调终面时间",
        )
        assert objective.title == "协调终面时间"
        assert objective.description is not None

    def test_title_required(self):
        """标题必填"""
        with pytest.raises(ValueError):
            ThreadObjective(title="", description="test")

    def test_title_max_length(self):
        """标题最大长度"""
        with pytest.raises(ValueError):
            ThreadObjective(title="x" * 201)


class TestThreadStatus:
    """ThreadStatus 枚举测试"""

    def test_is_terminal(self):
        """判断终态"""
        assert ThreadStatus.is_terminal(ThreadStatus.COMPLETED)
        assert ThreadStatus.is_terminal(ThreadStatus.CANCELLED)
        assert not ThreadStatus.is_terminal(ThreadStatus.ACTIVE)
        assert not ThreadStatus.is_terminal(ThreadStatus.PAUSED)


class TestStateTransitions:
    """状态流转规则测试"""

    def test_all_statuses_covered(self):
        """所有状态都有流转规则"""
        all_statuses = set(ThreadStatus)
        covered_statuses = set(VALID_TRANSITIONS.keys())
        assert all_statuses == covered_statuses

    def test_valid_transitions(self):
        """合法流转"""
        assert can_transition(ThreadStatus.NEW, ThreadStatus.PLANNING)
        assert can_transition(ThreadStatus.ACTIVE, ThreadStatus.AWAITING_EXTERNAL)
        assert can_transition(ThreadStatus.ACTIVE, ThreadStatus.COMPLETED)

    def test_invalid_transitions(self):
        """非法流转"""
        assert not can_transition(ThreadStatus.COMPLETED, ThreadStatus.ACTIVE)
        assert not can_transition(ThreadStatus.CANCELLED, ThreadStatus.ACTIVE)
        assert not can_transition(ThreadStatus.PAUSED, ThreadStatus.AWAITING_EXTERNAL)

    def test_terminal_no_outgoing(self):
        """终态没有流出边"""
        assert len(VALID_TRANSITIONS[ThreadStatus.COMPLETED]) == 0
        assert len(VALID_TRANSITIONS[ThreadStatus.CANCELLED]) == 0


class TestDelegationProfile:
    """DelegationProfile 值对象测试"""

    def test_default_observe(self):
        """默认观察模式"""
        profile = DelegationProfile.default_observe()
        assert profile.level == DelegationLevel.OBSERVE_ONLY

    def test_default_draft(self):
        """默认起草模式"""
        profile = DelegationProfile.default_draft()
        assert profile.level == DelegationLevel.DRAFT_FIRST

    def test_default_approve(self):
        """默认审批模式"""
        profile = DelegationProfile.default_approve()
        assert profile.level == DelegationLevel.APPROVE_TO_SEND


class TestThread:
    """Thread 聚合根测试"""

    def create_thread(self, **kwargs):
        """辅助方法：创建测试Thread"""
        defaults = {
            "objective": ThreadObjective(title="测试线程"),
            "owner_id": uuid4(),
        }
        defaults.update(kwargs)
        return Thread(**defaults)

    def test_create(self):
        """创建Thread"""
        owner_id = uuid4()
        thread = self.create_thread(owner_id=owner_id)

        assert thread.id is not None
        assert thread.status == ThreadStatus.NEW
        assert thread.risk_level == RiskLevel.LOW
        assert thread.owner_id == owner_id
        assert thread.responsible_principal_id == owner_id
        assert not thread.is_terminal
        assert thread.version == 1

    def test_transition_valid(self):
        """合法状态流转"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        assert thread.status == ThreadStatus.PLANNING

    def test_transition_invalid(self):
        """非法状态流转"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)
        thread.transition_to(ThreadStatus.COMPLETED)

        with pytest.raises(ValueError):
            thread.transition_to(ThreadStatus.ACTIVE)

    def test_transition_terminal(self):
        """终态不可流转"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)
        thread.transition_to(ThreadStatus.COMPLETED)

        with pytest.raises(ValueError):
            thread.transition_to(ThreadStatus.ACTIVE)

    def test_pause(self):
        """暂停线程"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)

        thread.pause()
        assert thread.status == ThreadStatus.PAUSED
        assert thread.can_be_resumed

    def test_pause_from_invalid_state(self):
        """从非法状态暂停"""
        thread = self.create_thread()
        with pytest.raises(ValueError):
            thread.pause()

    def test_resume(self):
        """恢复线程"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)
        thread.pause()

        thread.resume()
        assert thread.status == ThreadStatus.ACTIVE

    def test_resume_from_invalid_state(self):
        """从非法状态恢复"""
        thread = self.create_thread()
        with pytest.raises(ValueError):
            thread.resume()

    def test_escalate(self):
        """升级到人工"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)

        reason = "检测到高风险内容"
        thread.escalate(reason)

        assert thread.status == ThreadStatus.ESCALATED
        assert thread.last_escalation_reason == reason
        assert thread.last_escalated_at is not None

    def test_escalate_terminal(self):
        """终态不可升级"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)
        thread.transition_to(ThreadStatus.COMPLETED)

        with pytest.raises(ValueError):
            thread.escalate("test")

    def test_complete(self):
        """完成线程"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)
        thread.transition_to(ThreadStatus.ACTIVE)

        thread.complete()

        assert thread.status == ThreadStatus.COMPLETED
        assert thread.completed_at is not None
        assert thread.is_terminal

    def test_cancel(self):
        """取消线程"""
        thread = self.create_thread()
        thread.transition_to(ThreadStatus.PLANNING)

        thread.cancel()

        assert thread.status == ThreadStatus.CANCELLED
        assert thread.is_terminal

    def test_update_summary(self):
        """更新摘要"""
        thread = self.create_thread()
        summary = "正在协调时间，等待候选人回复"
        thread.update_summary(summary)

        assert thread.summary == summary
        assert thread.updated_at > thread.created_at

    def test_update_summary_truncated(self):
        """摘要过长被截断"""
        thread = self.create_thread()
        summary = "x" * 1000
        thread.update_summary(summary)

        assert len(thread.summary) == 500

    def test_set_responsible(self):
        """设置责任方"""
        thread = self.create_thread()
        principal_id = uuid4()
        thread.set_responsible(principal_id)

        assert thread.responsible_principal_id == principal_id

    def test_add_participant(self):
        """添加参与者"""
        thread = self.create_thread()
        principal_id = uuid4()
        thread.add_participant(principal_id)

        assert principal_id in thread.participant_ids

    def test_add_participant_duplicate(self):
        """重复添加参与者"""
        thread = self.create_thread()
        principal_id = uuid4()
        thread.add_participant(principal_id)
        thread.add_participant(principal_id)

        assert thread.participant_ids.count(principal_id) == 1

    def test_remove_participant(self):
        """移除参与者"""
        thread = self.create_thread()
        principal_id = uuid4()
        thread.add_participant(principal_id)
        thread.remove_participant(principal_id)

        assert principal_id not in thread.participant_ids

    def test_remove_participant_not_present(self):
        """移除不存在的参与者"""
        thread = self.create_thread()
        principal_id = uuid4()
        # 不应抛出异常
        thread.remove_participant(principal_id)

    def test_increment_version(self):
        """版本号递增"""
        thread = self.create_thread()
        initial_version = thread.version
        thread.increment_version()

        assert thread.version == initial_version + 1

    def test_updated_at_on_transition(self):
        """状态流转更新时间戳"""
        thread = self.create_thread()
        initial_updated_at = thread.updated_at

        # 确保时间不同
        import time
        time.sleep(0.001)

        thread.transition_to(ThreadStatus.PLANNING)

        assert thread.updated_at > initial_updated_at

    def test_tags(self):
        """标签"""
        thread = self.create_thread(tags=["招聘", "面试"])
        assert "招聘" in thread.tags
        assert "面试" in thread.tags

    def test_due_at(self):
        """截止时间"""
        due_at = datetime.utcnow() + timedelta(days=7)
        objective = ThreadObjective(
            title="测试",
            due_at=due_at,
        )
        thread = self.create_thread(objective=objective)
        assert thread.objective.due_at == due_at
