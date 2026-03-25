
"""
Decision Recorder

决策记录器
"""
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime
from contextlib import contextmanager
from time import time

from ..common.constants import Decision
from .models import DecisionTrace, DecisionStep


class DecisionRecorder:
    """
    决策记录器

    负责记录8步决策链的每一步
    """

    def __init__(self):
        self._traces: Dict[UUID, DecisionTrace] = {}
        self._thread_traces: Dict[UUID, List[UUID]] = {}

    def start_trace(
        self,
        thread_id: UUID,
        action_run_id: Optional[UUID] = None,
    ) -> DecisionTrace:
        """
        开始记录决策追踪

        Args:
            thread_id: 线程ID
            action_run_id: 动作运行ID

        Returns:
            决策追踪对象
        """
        trace = DecisionTrace(
            thread_id=thread_id,
            action_run_id=action_run_id,
            created_at=datetime.utcnow(),
        )
        self._traces[trace.id] = trace

        if thread_id not in self._thread_traces:
            self._thread_traces[thread_id] = []
        self._thread_traces[thread_id].append(trace.id)

        return trace

    @contextmanager
    def record_step(
        self,
        trace: DecisionTrace,
        step_number: int,
        step_name: str,
        description: str,
        input_data: Optional[Dict] = None,
    ):
        """
        记录单个决策步骤（上下文管理器）

        Usage:
            with recorder.record_step(trace, 1, "Read Thread", "Reading thread state", input):
                # ... do work ...
                output = some_result
                return output
        """
        start_time = time()
        output_data = None

        try:
            yield lambda out: setattr(self, '_output', out)
            if hasattr(self, '_output'):
                output_data = self._output
        finally:
            duration_ms = int((time() - start_time) * 1000)
            trace.add_step(
                step_number=step_number,
                step_name=step_name,
                description=description,
                input_data=input_data,
                output_data=output_data,
                duration_ms=duration_ms,
            )

    def record_step_sync(
        self,
        trace: DecisionTrace,
        step_number: int,
        step_name: str,
        description: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        duration_ms: Optional[int] = None,
    ):
        """
        同步记录单个决策步骤
        """
        trace.add_step(
            step_number=step_number,
            step_name=step_name,
            description=description,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
        )

    def complete_trace(
        self,
        trace: DecisionTrace,
        decision: Decision,
        decision_reason: str,
        policy_hits: Optional[List[Dict]] = None,
        risk_assessment_id: Optional[UUID] = None,
        kill_switch_affected: bool = False,
    ) -> DecisionTrace:
        """
        完成决策追踪记录

        Args:
            trace: 决策追踪对象
            decision: 最终决策
            decision_reason: 决策原因
            policy_hits: 命中的策略
            risk_assessment_id: 风险评估ID
            kill_switch_affected: 是否受熔断影响

        Returns:
            完成的决策追踪对象
        """
        trace.decision = decision
        trace.decision_reason = decision_reason
        trace.policy_hits = policy_hits
        trace.risk_assessment_id = risk_assessment_id
        trace.kill_switch_affected = kill_switch_affected

        return trace

    def get_trace(self, trace_id: UUID) -> Optional[DecisionTrace]:
        """获取决策追踪"""
        return self._traces.get(trace_id)

    def get_traces_for_thread(self, thread_id: UUID, limit: int = 100) -> List[DecisionTrace]:
        """获取线程的所有决策追踪"""
        trace_ids = self._thread_traces.get(thread_id, [])
        traces = [self._traces.get(tid) for tid in trace_ids if tid in self._traces]
        traces.sort(key=lambda t: t.created_at, reverse=True)
        return traces[:limit]

    def record_8_step_decision(
        self,
        thread_id: UUID,
        action_run_id: Optional[UUID],
        decision: Decision,
        decision_reason: str,
        step_data: List[Dict[str, Any]],
        policy_hits: Optional[List[Dict]] = None,
        risk_assessment_id: Optional[UUID] = None,
        kill_switch_affected: bool = False,
    ) -> DecisionTrace:
        """
        记录完整的8步决策链

        Args:
            thread_id: 线程ID
            action_run_id: 动作运行ID
            decision: 最终决策
            decision_reason: 决策原因
            step_data: 每一步的数据 [{'name': '', 'description': '', 'input': {}, 'output': {}}, ...]
            policy_hits: 命中的策略
            risk_assessment_id: 风险评估ID
            kill_switch_affected: 是否受熔断影响

        Returns:
            决策追踪对象
        """
        trace = self.start_trace(thread_id, action_run_id)

        for i, step in enumerate(step_data, 1):
            self.record_step_sync(
                trace=trace,
                step_number=i,
                step_name=step.get('name', f'Step {i}'),
                description=step.get('description', ''),
                input_data=step.get('input'),
                output_data=step.get('output'),
                duration_ms=step.get('duration_ms'),
            )

        self.complete_trace(
            trace=trace,
            decision=decision,
            decision_reason=decision_reason,
            policy_hits=policy_hits,
            risk_assessment_id=risk_assessment_id,
            kill_switch_affected=kill_switch_affected,
        )

        return trace
