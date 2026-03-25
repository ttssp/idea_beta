
"""
Policy Evaluator

策略评估器 - 整合Delegation Profile和Policy Engine
"""
from typing import Optional
from uuid import UUID

from ..common.constants import Decision, DelegationLevel
from ..common.types import PolicyContext, PolicyDecision
from ..delegation.service import DelegationService
from .engine import PolicyEngine


class PolicyEvaluator:
    """
    策略评估器

    整合Delegation Profile和Policy Engine，提供统一的评估接口
    """

    def __init__(
        self,
        delegation_service: DelegationService,
        policy_engine: PolicyEngine,
    ):
        self.delegation_service = delegation_service
        self.policy_engine = policy_engine

    def evaluate(
        self,
        context: PolicyContext,
        thread_id: Optional[UUID] = None,
        relationship_id: Optional[UUID] = None,
    ) -&gt; PolicyDecision:
        """
        完整的策略评估

        执行流程：
        1. 获取有效委托档位
        2. 检查档位是否允许该动作
        3. 检查预算
        4. 执行策略引擎评估
        5. 返回最终决策
        """
        # 1. 获取有效委托档位
        profile = self.delegation_service.get_effective_profile(
            thread_id=thread_id,
            relationship_id=relationship_id,
        )

        # 2. 根据档位快速决策
        if profile.profile_level == DelegationLevel.HUMAN_ONLY:
            return PolicyDecision(
                decision=Decision.DENY,
                reason="Human only mode - agent not allowed to intervene",
                metadata={"profile": profile.name},
            )

        if profile.profile_level == DelegationLevel.OBSERVE_ONLY:
            return PolicyDecision(
                decision=Decision.DRAFT_ONLY,
                reason="Observe only mode - can draft but not send",
                metadata={"profile": profile.name},
            )

        # 3. 检查动作是否被允许
        if not profile.can_perform_action(context.action):
            return PolicyDecision(
                decision=Decision.REQUIRE_APPROVAL,
                reason=f"Action {context.action} not allowed in profile {profile.name}",
                metadata={"profile": profile.name},
            )

        # 4. 检查预算
        if thread_id and not self.delegation_service.check_budget(
            thread_id=thread_id,
            action_type=context.action,
            profile=profile,
        ):
            return PolicyDecision(
                decision=Decision.ESCALATE_TO_HUMAN,
                reason="Budget exceeded",
                metadata={"profile": profile.name},
            )

        # 5. 执行策略引擎评估
        context.delegation_profile_id = profile.id
        policy_decision = self.policy_engine.evaluate(context)

        # 6. 根据档位调整决策
        final_decision = self._adjust_decision_for_profile(
            policy_decision.decision,
            profile.profile_level,
        )

        return PolicyDecision(
            decision=final_decision,
            reason=policy_decision.reason,
            matched_rules=policy_decision.matched_rules,
            metadata={
                **(policy_decision.metadata or {}),
                "profile": profile.name,
                "profile_level": profile.profile_level.value,
            },
        )

    def _adjust_decision_for_profile(
        self,
        decision: Decision,
        profile_level: DelegationLevel,
    ) -&gt; Decision:
        """
        根据委托档位调整决策

        - Draft First: 即使策略允许，也只能draft
        - Approve to Send: 自动执行降级为需要审批
        - Bounded Auto: 可以自动执行低风险动作
        """
        if profile_level == DelegationLevel.DRAFT_FIRST:
            # 只能draft，不能自动发送
            if decision == Decision.ALLOW:
                return Decision.DRAFT_ONLY
            if decision == Decision.BOUNDED_EXECUTION:
                return Decision.REQUIRE_APPROVAL

        elif profile_level == DelegationLevel.APPROVE_TO_SEND:
            # 需要审批才能发送
            if decision == Decision.ALLOW:
                return Decision.REQUIRE_APPROVAL
            if decision == Decision.BOUNDED_EXECUTION:
                return Decision.REQUIRE_APPROVAL

        elif profile_level == DelegationLevel.BOUNDED_AUTO:
            # 边界内自动执行
            if decision == Decision.ALLOW:
                return Decision.BOUNDED_EXECUTION

        return decision
