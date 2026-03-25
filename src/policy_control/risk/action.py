
"""
Action Risk Evaluator

动作风险评估器
"""

from ..common.constants import RiskLevel
from .models import RiskEvaluationResult


class ActionRiskEvaluator:
    """
    动作风险评估器

    基于动作类型的风险评估
    """

    # 动作类型风险映射 (1-5)
    ACTION_RISK_MAP = {
        # 高风险动作
        "make_payment": 5,
        "sign_contract": 5,
        "make_commitment": 5,
        "offer_discount": 5,
        "negotiate_price": 5,
        "terminate_relationship": 5,
        # 中高风险
        "send_negative_message": 4,
        "escalate": 4,
        "request_sensitive_info": 4,
        "make_promise": 4,
        # 中风险
        "send_message": 3,
        "schedule_meeting": 3,
        "propose_time": 3,
        "request_info": 3,
        "follow_up": 3,
        # 低风险
        "draft_message": 2,
        "suggest_action": 2,
        "remind": 2,
        "confirm": 2,
        # 极低风险
        "observe": 1,
        "summarize": 1,
        "analyze": 1,
    }

    DEFAULT_RISK = 3  # 默认中风险

    def evaluate(
        self,
        action_type: str | None = None,
    ) -> RiskEvaluationResult:
        """
        评估动作风险

        Args:
            action_type: 动作类型

        Returns:
            风险评估结果
        """
        risk_factors = []
        risk_score = self.DEFAULT_RISK

        if action_type:
            risk_score = self.ACTION_RISK_MAP.get(
                action_type,
                self.DEFAULT_RISK,
            )
            risk_factors.append(f"action_type:{action_type}")

        risk_level = self._score_to_level(risk_score)

        return RiskEvaluationResult(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            reason=f"Action risk: {action_type or 'unknown'} -> {risk_level.value}",
        )

    def _score_to_level(self, score: int) -> RiskLevel:
        """将风险分数转换为风险等级"""
        if score <= 1:
            return RiskLevel.LOW
        elif score <= 2:
            return RiskLevel.LOW
        elif score <= 3:
            return RiskLevel.MEDIUM
        elif score <= 4:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
