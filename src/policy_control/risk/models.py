
"""
Risk Engine Data Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..common.constants import RiskLevel, Decision


@dataclass
class RiskAssessment:
    """风险评估记录"""

    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: Optional[UUID] = None
    relationship_risk: int = 1
    action_risk: int = 1
    content_risk: int = 1
    consequence_risk: int = 1
    overall_risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    decision_recommendation: Decision = Decision.ALLOW
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskEvaluationResult:
    """风险评估结果"""

    risk_score: int  # 1-5
    risk_level: RiskLevel
    risk_factors: List[str]
    reason: str
