
"""
Relationship Risk Evaluator

关系风险评估器
"""

from ..common.constants import RiskLevel
from .models import RiskEvaluationResult


class RelationshipRiskEvaluator:
    """
    关系风险评估器

    基于关系类别的风险评估
    """

    # 关系类别风险映射 (1-5)
    RELATIONSHIP_RISK_MAP = {
        "family": 5,  # 家人 - 极高风险
        "core_client": 5,  # 核心客户 - 极高风险
        "executive": 4,  # 高管 - 高风险
        "sensitive_contact": 4,  # 敏感联系人 - 高风险
        "client": 3,  # 普通客户 - 中风险
        "vendor": 3,  # 供应商 - 中风险
        "candidate": 2,  # 候选人 - 低风险
        "colleague": 2,  # 同事 - 低风险
        "team_member": 1,  # 团队成员 - 极低风险
        "internal_collaborator": 1,  # 内部协作者 - 极低风险
        "service_provider": 2,  # 服务提供方 - 低风险
        "unknown": 3,  # 未知关系 - 中风险（默认保守）
    }

    DEFAULT_RISK = 3  # 默认中风险

    def evaluate(
        self,
        relationship_class: str | None = None,
        relationship: dict | None = None,
    ) -> RiskEvaluationResult:
        """
        评估关系风险

        Args:
            relationship_class: 关系类别
            relationship: 关系详细信息

        Returns:
            风险评估结果
        """
        risk_factors = []
        risk_score = self.DEFAULT_RISK

        if relationship_class:
            risk_score = self.RELATIONSHIP_RISK_MAP.get(
                relationship_class,
                self.DEFAULT_RISK,
            )
            risk_factors.append(f"relationship_class:{relationship_class}")

        # 额外的关系属性检查
        if relationship:
            if relationship.get("is_sensitive", False):
                risk_score = max(risk_score, 4)
                risk_factors.append("flag:sensitive")

            if relationship.get("is_vip", False):
                risk_score = max(risk_score, 4)
                risk_factors.append("flag:vip")

            if relationship.get("is_new", True):
                risk_score = max(risk_score, 3)
                risk_factors.append("flag:new_relationship")

        risk_level = self._score_to_level(risk_score)

        return RiskEvaluationResult(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            reason=f"Relationship risk: {relationship_class or 'unknown'} -> {risk_level.value}",
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
