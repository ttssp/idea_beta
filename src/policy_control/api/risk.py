
"""
Risk API

风险评估API
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from uuid import UUID

from ..common.types import RiskContext, RiskDecision
from ..risk.synthesizer import RiskSynthesizer


@dataclass
class RiskEvaluationRequest:
    thread_id: UUID
    action: UUID  # action_run_id
    content: Optional[str] = None
    relationship: Optional[Dict[str, Any]] = None
    relationship_class: Optional[str] = None
    action_type: Optional[str] = None
    historical_data: Optional[Dict[str, Any]] = None


class RiskAPI:
    """
    Risk API (Internal)

    Endpoints:
        POST /risk/evaluate
    """

    def __init__(self, risk_synthesizer: RiskSynthesizer):
        self.synthesizer = risk_synthesizer

    def evaluate_risk(
        self,
        request: RiskEvaluationRequest,
    ) -&gt; RiskDecision:
        """
        POST /risk/evaluate

        风险评估（输入动作 → 输出风险等级 + 决策建议）
        """
        context = RiskContext(
            thread_id=request.thread_id,
            action=request.action,
            content=request.content,
            relationship=request.relationship,
            relationship_class=request.relationship_class,
            action_type=request.action_type,
            historical_data=request.historical_data,
        )

        return self.synthesizer.evaluate(context)
