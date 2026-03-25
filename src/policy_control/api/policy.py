
"""
Policy API

策略评估API
"""
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from ..common.types import PolicyContext, PolicyDecision
from ..policy.evaluator import PolicyEvaluator


@dataclass
class PolicyEvaluationRequest:
    thread_id: UUID
    action: str
    relationship_class: str | None = None
    thread_objective: str | None = None
    thread_status: str | None = None
    additional_context: dict[str, Any] | None = None


class PolicyAPI:
    """
    Policy API (Internal)

    Endpoints:
        POST /policy/evaluate
    """

    def __init__(self, policy_evaluator: PolicyEvaluator):
        self.evaluator = policy_evaluator

    def evaluate_policy(
        self,
        request: PolicyEvaluationRequest,
        relationship_id: UUID | None = None,
    ) -> PolicyDecision:
        """
        POST /policy/evaluate

        策略评估（输入 context → 输出决策）
        """
        context = PolicyContext(
            thread_id=request.thread_id,
            action=request.action,
            relationship_class=request.relationship_class,
            thread_objective=request.thread_objective,
            thread_status=request.thread_status,
            additional_context=request.additional_context,
        )

        return self.evaluator.evaluate(
            context=context,
            thread_id=request.thread_id,
            relationship_id=relationship_id,
        )
