
"""
Action Execution Engine

Core engine for managing ActionRun lifecycle.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .models import ActionRun, ActionRunStatusHistory
from .state_machine import ActionRunStateMachine, ActionRunStatus
from ..core.idempotency import IdempotencyManager


class ActionRunEngine:
    """
    ActionRun执行引擎

    负责ActionRun的完整生命周期管理：
    - 创建和规划动作
    - 状态机流转
    - 执行动作
    - 状态历史记录
    """

    def __init__(
        self,
        db: AsyncSession,
        idempotency: Optional[IdempotencyManager] = None
    ):
        self.db = db
        self.idempotency = idempotency

    async def create_action_run(
        self,
        thread_id: UUID,
        action_type: str,
        input_payload: Dict[str, Any],
        idempotency_key: str,
        scheduled_for: Optional[datetime] = None
    ) -&gt; ActionRun:
        """
        创建新的ActionRun

        Args:
            thread_id: Thread ID
            action_type: 动作类型
            input_payload: 输入参数
            idempotency_key: 幂等键
            scheduled_for: 调度时间

        Returns:
            创建的ActionRun对象
        """
        # 检查幂等
        existing = await self.db.execute(
            select(ActionRun).where(ActionRun.idempotency_key == idempotency_key)
        )
        if existing.scalar_one_or_none():
            return existing.scalar_one()

        # 创建ActionRun
        action_run = ActionRun(
            thread_id=thread_id,
            action_type=action_type,
            status=ActionRunStatus.CREATED,
            idempotency_key=idempotency_key,
            input_payload=input_payload,
            scheduled_for=scheduled_for
        )
        self.db.add(action_run)
        await self.db.commit()
        await self.db.refresh(action_run)

        # 记录历史
        await self._record_state_change(
            action_run.id,
            None,
            ActionRunStatus.CREATED,
            "create",
            {"thread_id": str(thread_id), "action_type": action_type}
        )

        return action_run

    async def plan_action(self, action_run_id: UUID, input_payload: Optional[Dict[str, Any]] = None) -&gt; ActionRun:
        """
        规划动作：created → planned

        Args:
            action_run_id: ActionRun ID
            input_payload: 可选的更新输入参数

        Returns:
            更新后的ActionRun
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)

        if not sm.can_transition_to(ActionRunStatus.PLANNED):
            raise ValueError(f"Cannot transition from {action_run.status} to planned")

        sm.plan()

        if input_payload:
            action_run.input_payload = {**action_run.input_payload, **input_payload}

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.CREATED,
            ActionRunStatus.PLANNED,
            "plan",
            {}
        )

        return action_run

    async def submit_for_approval(self, action_run_id: UUID) -&gt; ActionRun:
        """
        提交审批：planned → ready_for_approval
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.submit_for_approval()

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.PLANNED,
            ActionRunStatus.READY_FOR_APPROVAL,
            "submit_for_approval",
            {}
        )

        return action_run

    async def approve(self, action_run_id: UUID) -&gt; ActionRun:
        """
        批准：ready_for_approval → approved
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.approve()

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.READY_FOR_APPROVAL,
            ActionRunStatus.APPROVED,
            "approve",
            {}
        )

        return action_run

    async def reject(self, action_run_id: UUID) -&gt; ActionRun:
        """
        拒绝：ready_for_approval → cancelled
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.reject()

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.READY_FOR_APPROVAL,
            ActionRunStatus.CANCELLED,
            "reject",
            {}
        )

        return action_run

    async def start_execution(self, action_run_id: UUID) -&gt; ActionRun:
        """
        开始执行：approved → executing
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.start_execution()

        action_run.status = sm.state
        action_run.executed_at = datetime.utcnow()
        action_run.last_attempted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.APPROVED,
            ActionRunStatus.EXECUTING,
            "start_execution",
            {}
        )

        return action_run

    async def mark_send_success(
        self,
        action_run_id: UUID,
        output_payload: Optional[Dict[str, Any]] = None,
        external_message_id: Optional[str] = None,
        external_thread_id: Optional[str] = None
    ) -&gt; ActionRun:
        """
        标记发送成功：executing → sent
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.send_success()

        action_run.status = sm.state
        if output_payload:
            action_run.output_payload = output_payload
        if external_message_id:
            action_run.external_message_id = external_message_id
        if external_thread_id:
            action_run.external_thread_id = external_thread_id
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.EXECUTING,
            ActionRunStatus.SENT,
            "send_success",
            {"external_message_id": external_message_id}
        )

        return action_run

    async def mark_send_failed_retryable(
        self,
        action_run_id: UUID,
        error: str
    ) -&gt; ActionRun:
        """
        标记可重试失败：executing → failed_retryable
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.send_fail_retryable()

        action_run.status = sm.state
        action_run.retry_count += 1
        action_run.last_error = error
        action_run.last_attempted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.EXECUTING,
            ActionRunStatus.FAILED_RETRYABLE,
            "send_fail_retryable",
            {"error": error, "retry_count": action_run.retry_count}
        )

        return action_run

    async def mark_send_failed_terminal(
        self,
        action_run_id: UUID,
        error: str
    ) -&gt; ActionRun:
        """
        标记终端失败：executing → failed_terminal
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.send_fail_terminal()

        action_run.status = sm.state
        action_run.last_error = error
        action_run.last_attempted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.EXECUTING,
            ActionRunStatus.FAILED_TERMINAL,
            "send_fail_terminal",
            {"error": error}
        )

        return action_run

    async def retry(self, action_run_id: UUID) -&gt; ActionRun:
        """
        重试：failed_retryable → executing
        """
        action_run = await self._get_action_run(action_run_id)

        # 检查是否超过最大重试次数
        if action_run.retry_count &gt;= action_run.max_retries:
            sm = ActionRunStateMachine(action_run.status)
            sm.max_retries_exceeded()
            action_run.status = sm.state
            await self.db.commit()
            await self.db.refresh(action_run)

            await self._record_state_change(
                action_run.id,
                ActionRunStatus.FAILED_RETRYABLE,
                ActionRunStatus.FAILED_TERMINAL,
                "max_retries_exceeded",
                {}
            )
            return action_run

        sm = ActionRunStateMachine(action_run.status)
        sm.retry()

        action_run.status = sm.state
        action_run.last_attempted_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.FAILED_RETRYABLE,
            ActionRunStatus.EXECUTING,
            "retry",
            {"retry_count": action_run.retry_count}
        )

        return action_run

    async def acknowledge(self, action_run_id: UUID) -&gt; ActionRun:
        """
        确认接收：sent → acknowledged
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)
        sm.acknowledge()

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            ActionRunStatus.SENT,
            ActionRunStatus.ACKNOWLEDGED,
            "acknowledge",
            {}
        )

        return action_run

    async def cancel(self, action_run_id: UUID) -&gt; ActionRun:
        """
        取消动作
        """
        action_run = await self._get_action_run(action_run_id)
        sm = ActionRunStateMachine(action_run.status)

        if not sm.can_cancel:
            raise ValueError(f"Cannot cancel action in state {action_run.status}")

        from_status = action_run.status
        sm.cancel()

        action_run.status = sm.state
        await self.db.commit()
        await self.db.refresh(action_run)

        await self._record_state_change(
            action_run.id,
            from_status,
            ActionRunStatus.CANCELLED,
            "cancel",
            {}
        )

        return action_run

    async def get_action_run(self, action_run_id: UUID) -&gt; Optional[ActionRun]:
        """获取ActionRun"""
        return await self._get_action_run(action_run_id)

    async def list_by_thread(
        self,
        thread_id: UUID,
        status: Optional[str] = None,
        limit: int = 50
    ) -&gt; list[ActionRun]:
        """列出Thread的所有ActionRun"""
        query = select(ActionRun).where(ActionRun.thread_id == thread_id)
        if status:
            query = query.where(ActionRun.status == status)
        query = query.order_by(ActionRun.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # Internal methods
    async def _get_action_run(self, action_run_id: UUID) -&gt; ActionRun:
        result = await self.db.execute(
            select(ActionRun).where(ActionRun.id == action_run_id)
        )
        action_run = result.scalar_one_or_none()
        if not action_run:
            raise ValueError(f"ActionRun {action_run_id} not found")
        return action_run

    async def _record_state_change(
        self,
        action_run_id: UUID,
        from_status: Optional[str],
        to_status: str,
        event_type: str,
        event_payload: Dict[str, Any],
        actor: Optional[str] = None
    ):
        """记录状态变更历史"""
        history = ActionRunStatusHistory(
            action_run_id=action_run_id,
            from_status=from_status,
            to_status=to_status,
            event_type=event_type,
            event_payload=event_payload,
            actor=actor
        )
        self.db.add(history)
        await self.db.commit()

