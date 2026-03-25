
"""
Policy & Control Type Definitions
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

from .constants import (
    Decision,
    RiskLevel,
    DelegationLevel,
)


@dataclass
class PolicyContext:
    """策略评估上下文"""

    thread_id: UUID
    action: str
    relationship_class: Optional[str] = None
    delegation_profile_id: Optional[UUID] = None
    thread_objective: Optional[str] = None
    thread_status: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class RiskContext:
    """风险评估上下文"""

    thread_id: UUID
    action: str
    content: Optional[str] = None
    relationship: Optional[Dict[str, Any]] = None
    relationship_class: Optional[str] = None
    action_type: Optional[str] = None
    historical_data: Optional[Dict[str, Any]] = None


@dataclass
class PolicyDecision:
    """策略决策结果"""

    decision: Decision
    reason: str
    matched_rules: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None


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
