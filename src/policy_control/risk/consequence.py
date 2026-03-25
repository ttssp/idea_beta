
"""
Consequence Risk Evaluator

结果风险评估器
"""

from ..common.constants import RiskLevel
from .models import RiskEvaluationResult


class ConsequenceRiskEvaluator:
    """
    结果风险评估器

    基于历史数据和规则的结果风险评估
    """

    def evaluate(
        self,
        historical_data: dict | None = None,
        relationship_risk: int = 1,
        action_risk: int = 1,
    ) -> RiskEvaluationResult:
        """
        评估结果风险

        Args:
            historical_data: 历史数据
            relationship_risk: 关系风险分数
            action_risk: 动作风险分数

        Returns:
            风险评估结果
        """
        risk_factors = []
        risk_score = 1

        # 基于关系和动作风险的基础分数
        base_risk = max(relationship_risk, action_risk)
        risk_score = base_risk

        # 检查历史数据
        if historical_data:
            # 历史错误率
            error_rate = historical_data.get("error_rate", 0)
            if error_rate > 0.5:
                risk_score = max(risk_score, 5)
                risk_factors.append("history:high_error_rate")
            elif error_rate > 0.2:
                risk_score = max(risk_score, 4)
                risk_factors.append("history:medium_error_rate")

            # 历史升级率
            escalation_rate = historical_data.get("escalation_rate", 0)
            if escalation_rate > 0.3:
                risk_score = max(risk_score, 4)
                risk_factors.append("history:high_escalation_rate")

            # 该线程的历史问题
            if historical_data.get("had_issues", False):
                risk_score = max(risk_score, 4)
                risk_factors.append("history:previous_issues")

        risk_level = self._score_to_level(risk_score)

        return RiskEvaluationResult(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            reason=f"Consequence risk -> {risk_level.value}",
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
