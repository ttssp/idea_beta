
"""
Policy Engine Core Logic

规则匹配、优先级排序、冲突解决
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..common.constants import PolicyEffect, PolicyScope, Decision
from ..common.exceptions import PolicyRuleConflictError
from ..common.types import PolicyContext, PolicyDecision
from .models import PolicyRule


class ConflictResolver:
    """
    策略冲突解决器

    冲突解决策略：
    1. DENY &gt; REQUIRE_APPROVAL &gt; ESCALATE &gt; ALLOW
    2. 同effect时，priority高的优先
    3. 同priority时，scope更具体的优先 (THREAD &gt; RELATIONSHIP &gt; PROFILE &gt; GLOBAL)
    """

    # Effect优先级（数值越大优先级越高）
    EFFECT_PRIORITY = {
        PolicyEffect.DENY: 100,
        PolicyEffect.REQUIRE_APPROVAL: 75,
        PolicyEffect.ESCALATE: 50,
        PolicyEffect.ALLOW: 25,
    }

    # Scope优先级（数值越大优先级越高）
    SCOPE_PRIORITY = {
        PolicyScope.THREAD: 100,
        PolicyScope.RELATIONSHIP: 75,
        PolicyScope.PROFILE: 50,
        PolicyScope.GLOBAL: 25,
    }

    def resolve(self, rules: List[PolicyRule]) -&gt; PolicyRule:
        """
        从冲突规则中选出获胜者

        Args:
            rules: 匹配的规则列表

        Returns:
            获胜的规则
        """
        if not rules:
            raise ValueError("No rules to resolve")

        if len(rules) == 1:
            return rules[0]

        # 按优先级排序
        sorted_rules = sorted(
            rules,
            key=lambda r: (
                self.EFFECT_PRIORITY.get(r.effect, 0),
                r.priority,
                self.SCOPE_PRIORITY.get(r.scope, 0),
            ),
            reverse=True,
        )

        return sorted_rules[0]


class PolicyEngine:
    """策略引擎"""

    def __init__(self):
        self._rules: Dict[UUID, PolicyRule] = {}
        self._conflict_resolver = ConflictResolver()

    def add_rule(self, rule: PolicyRule) -&gt; PolicyRule:
        """添加策略规则"""
        self._rules[rule.id] = rule
        return rule

    def get_rule(self, rule_id: UUID) -&gt; Optional[PolicyRule]:
        """获取策略规则"""
        return self._rules.get(rule_id)

    def update_rule(self, rule_id: UUID, **kwargs) -&gt; Optional[PolicyRule]:
        """更新策略规则"""
        rule = self._rules.get(rule_id)
        if not rule:
            return None

        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        rule.updated_at = datetime.utcnow()
        return rule

    def delete_rule(self, rule_id: UUID) -&gt; bool:
        """删除策略规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def list_rules(
        self,
        scope: Optional[PolicyScope] = None,
        scope_id: Optional[UUID] = None,
        active_only: bool = True,
    ) -&gt; List[PolicyRule]:
        """列出策略规则"""
        rules = list(self._rules.values())

        if active_only:
            rules = [r for r in rules if r.is_active]

        if scope:
            rules = [r for r in rules if r.scope == scope]

        if scope_id:
            rules = [r for r in rules if r.scope_id == scope_id]

        # 按优先级排序
        rules.sort(key=lambda r: r.priority, reverse=True)
        return rules

    def match_rules(
        self,
        context: Dict[str, Any],
        action: str,
        scope: Optional[PolicyScope] = None,
        scope_id: Optional[UUID] = None,
    ) -&gt; List[PolicyRule]:
        """
        匹配适用的策略规则

        Args:
            context: 上下文数据
            action: 动作类型
            scope: 作用域过滤
            scope_id: 作用域ID过滤

        Returns:
            匹配的规则列表
        """
        rules = self.list_rules(active_only=True)
        matched = []

        for rule in rules:
            # 检查action匹配
            if rule.action and rule.action != "*" and rule.action != action:
                continue

            # 检查scope过滤
            if scope and rule.scope != scope:
                continue
            if scope_id and rule.scope_id != scope_id:
                continue

            # 检查条件匹配
            if rule.matches(context):
                matched.append(rule)

        return matched

    def evaluate(
        self,
        policy_context: PolicyContext,
    ) -&gt; PolicyDecision:
        """
        策略评估（主要入口）

        Args:
            policy_context: 策略评估上下文

        Returns:
            策略决策结果
        """
        # 构建上下文
        context = {
            "thread_id": str(policy_context.thread_id),
            "action": policy_context.action,
            "relationship_class": policy_context.relationship_class,
            "delegation_profile_id": str(policy_context.delegation_profile_id) if policy_context.delegation_profile_id else None,
            "thread_objective": policy_context.thread_objective,
            "thread_status": policy_context.thread_status,
        }

        if policy_context.additional_context:
            context.update(policy_context.additional_context)

        # 收集匹配的规则
        matched_rules = self.match_rules(context, policy_context.action)

        if not matched_rules:
            # 默认：require_approval（保守策略）
            return PolicyDecision(
                decision=Decision.REQUIRE_APPROVAL,
                reason="No matching policy rules, defaulting to require approval",
                matched_rules=[],
            )

        # 冲突解决
        winning_rule = self._conflict_resolver.resolve(matched_rules)

        # 映射到决策
        decision = self._effect_to_decision(winning_rule.effect)

        return PolicyDecision(
            decision=decision,
            reason=f"Matched rule: {winning_rule.name}",
            matched_rules=[
                {
                    "id": str(r.id),
                    "name": r.name,
                    "effect": r.effect.value,
                    "priority": r.priority,
                }
                for r in matched_rules
            ],
            metadata={"winning_rule": str(winning_rule.id)},
        )

    def _effect_to_decision(self, effect: PolicyEffect) -&gt; Decision:
        """将PolicyEffect映射到Decision"""
        mapping = {
            PolicyEffect.ALLOW: Decision.ALLOW,
            PolicyEffect.DENY: Decision.DENY,
            PolicyEffect.REQUIRE_APPROVAL: Decision.REQUIRE_APPROVAL,
            PolicyEffect.ESCALATE: Decision.ESCALATE_TO_HUMAN,
        }
        return mapping.get(effect, Decision.REQUIRE_APPROVAL)
