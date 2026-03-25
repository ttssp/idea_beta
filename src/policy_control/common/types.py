
"""
Policy & Control Type Definitions
"""
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .constants import (
    Decision,
    RiskLevel,
)


@dataclass
class PolicyContext:
    """策略评估上下文"""

    thread_id: UUID
    action: str
    relationship_class: str | None = None
    delegation_profile_id: UUID | None = None
    thread_objective: str | None = None
    thread_status: str | None = None
    additional_context: dict[str, Any] | None = None


@dataclass
class RiskContext:
    """风险评估上下文"""

    thread_id: UUID
    action: str
    content: str | None = None
    relationship: dict[str, Any] | None = None
    relationship_class: str | None = None
    action_type: str | None = None
    historical_data: dict[str, Any] | None = None


@dataclass
class PolicyDecision:
    """策略决策结果"""

    decision: Decision
    reason: str
    matched_rules: list | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RiskDecision:
    """风险决策结果"""

    overall_risk_level: RiskLevel
    relationship_risk: int
    action_risk: int
    content_risk: int
    consequence_risk: int
    risk_factors: list
    recommendation: Decision
    reason: str
