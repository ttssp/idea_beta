
"""
Policy Engine Data Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..common.constants import PolicyEffect, PolicyScope


@dataclass
class PolicyRule:
    """策略规则模型"""

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: Optional[str] = None
    scope: PolicyScope = PolicyScope.GLOBAL
    scope_id: Optional[UUID] = None
    action: str = ""
    effect: PolicyEffect = PolicyEffect.ALLOW
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None

    def matches(self, context: Dict[str, Any]) -> bool:
        """
        检查规则是否匹配上下文

        简单的条件匹配逻辑，支持:
        - equals: 等于
        - in: 在列表中
        - not_in: 不在列表中
        - contains: 包含
        - greater_than: 大于
        - less_than: 小于
        """
        if not self.conditions:
            return True

        for key, condition in self.conditions.items():
            if isinstance(condition, dict):
                if "equals" in condition:
                    if context.get(key) != condition["equals"]:
                        return False
                elif "in" in condition:
                    if context.get(key) not in condition["in"]:
                        return False
                elif "not_in" in condition:
                    if context.get(key) in condition["not_in"]:
                        return False
                elif "contains" in condition:
                    value = context.get(key, "")
                    if condition["contains"] not in str(value):
                        return False
                elif "greater_than" in condition:
                    if context.get(key, 0) <= condition["greater_than"]:
                        return False
                elif "less_than" in condition:
                    if context.get(key, float("inf")) >= condition["less_than"]:
                        return False
            else:
                # 简单相等匹配
                if context.get(key) != condition:
                    return False
        return True
