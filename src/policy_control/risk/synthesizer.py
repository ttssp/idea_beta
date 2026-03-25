
"""
Risk Synthesizer

合成决策器：四层风险合成 → 6种决策输出
"""
from datetime import datetime
from uuid import UUID

from ..common.constants import Decision, RiskLevel
from ..common.types import RiskContext, RiskDecision
from .action import ActionRiskEvaluator
from .consequence import ConsequenceRiskEvaluator
from .content import ContentRiskEvaluator
from .models import RiskAssessment, RiskEvaluationResult
from .relationship import RelationshipRiskEvaluator


class RiskSynthesizer:
    """
    风险合成决策器

    执行流程：
    1. 分别评估四层风险
    2. 合成决策（加权平均 + 最大风险优先）
    3. 映射到6种决策输出
    """

    # 风险权重
    WEIGHTS = {
        "relationship": 0.35,
        "action": 0.30,
        "content": 0.20,
        "consequence": 0.15,
    }

    # 决策阈值
    DECISION_THRESHOLDS = {
        RiskLevel.LOW: Decision.ALLOW,
        RiskLevel.MEDIUM: Decision.REQUIRE_APPROVAL,
        RiskLevel.HIGH: Decision.ESCALATE_TO_HUMAN,
        RiskLevel.CRITICAL: Decision.DENY,
    }

    def __init__(self):
        self.relationship_risk = RelationshipRiskEvaluator()
        self.action_risk = ActionRiskEvaluator()
        self.content_risk = ContentRiskEvaluator()
        self.consequence_risk = ConsequenceRiskEvaluator()
        self._assessments: dict[UUID, RiskAssessment] = {}

    def evaluate(
        self,
        context: RiskContext,
    ) -> RiskDecision:
        """
        风险评估主入口

        Args:
            context: 风险评估上下文

        Returns:
            风险决策结果
        """
        # 1. 分别评估四层风险
        rel_result = self.relationship_risk.evaluate(
            relationship_class=context.relationship_class,
            relationship=context.relationship,
        )
        act_result = self.action_risk.evaluate(
            action_type=context.action_type,
        )
        con_result = self.content_risk.evaluate(
            content=context.content,
        )
        conq_result = self.consequence_risk.evaluate(
            historical_data=context.historical_data,
            relationship_risk=rel_result.risk_score,
            action_risk=act_result.risk_score,
        )

        # 2. 合成决策
        overall_score, overall_level = self._synthesize(
            rel_result,
            act_result,
            con_result,
            conq_result,
        )

        # 3. 映射到决策输出
        recommendation = self._risk_to_decision(
            overall_level,
            rel_result,
            act_result,
            con_result,
        )

        # 4. 收集所有风险因子
        all_factors = (
            rel_result.risk_factors
            + act_result.risk_factors
            + con_result.risk_factors
            + conq_result.risk_factors
        )

        # 5. 构建决策原因
        reason = self._build_reason(
            overall_level,
            rel_result,
            act_result,
            con_result,
            conq_result,
            recommendation,
        )

        # 6. 保存评估记录
        assessment = RiskAssessment(
            thread_id=context.thread_id,
            action_run_id=context.action,
            relationship_risk=rel_result.risk_score,
            action_risk=act_result.risk_score,
            content_risk=con_result.risk_score,
            consequence_risk=conq_result.risk_score,
            overall_risk_level=overall_level,
            risk_factors=all_factors,
            decision_recommendation=recommendation,
            created_at=datetime.utcnow(),
        )
        self._assessments[assessment.id] = assessment

        return RiskDecision(
            overall_risk_level=overall_level,
            relationship_risk=rel_result.risk_score,
            action_risk=act_result.risk_score,
            content_risk=con_result.risk_score,
            consequence_risk=conq_result.risk_score,
            risk_factors=all_factors,
            recommendation=recommendation,
            reason=reason,
        )

    def _synthesize(
        self,
        rel_result: RiskEvaluationResult,
        act_result: RiskEvaluationResult,
        con_result: RiskEvaluationResult,
        conq_result: RiskEvaluationResult,
    ) -> tuple[int, RiskLevel]:
        """
        合成风险评估

        策略：加权平均 + 最大风险优先
        """
        # 加权平均
        weighted_score = (
            rel_result.risk_score * self.WEIGHTS["relationship"]
            + act_result.risk_score * self.WEIGHTS["action"]
            + con_result.risk_score * self.WEIGHTS["content"]
            + conq_result.risk_score * self.WEIGHTS["consequence"]
        )

        # 最大风险优先（如果任一风险是CRITICAL或HIGH，整体升级）
        max_score = max(
            rel_result.risk_score,
            act_result.risk_score,
            con_result.risk_score,
            conq_result.risk_score,
        )

        if max_score >= 5:
            overall_score = 5
        elif max_score >= 4:
            overall_score = max(4, int(weighted_score))
        else:
            overall_score = int(weighted_score)

        overall_level = self._score_to_level(overall_score)
        return overall_score, overall_level

    def _risk_to_decision(
        self,
        overall_level: RiskLevel,
        rel_result: RiskEvaluationResult,
        act_result: RiskEvaluationResult,
        con_result: RiskEvaluationResult,
    ) -> Decision:
        """
        将风险等级映射到决策

        策略：
        - LOW -> ALLOW / BOUNDED_EXECUTION
        - MEDIUM -> REQUIRE_APPROVAL / DRAFT_ONLY
        - HIGH -> ESCALATE_TO_HUMAN
        - CRITICAL -> DENY
        """
        # 先按总体风险等级
        base_decision = self.DECISION_THRESHOLDS.get(
            overall_level,
            Decision.REQUIRE_APPROVAL,
        )

        # 内容风险特殊处理
        if con_result.risk_score >= 3 and base_decision == Decision.ALLOW:
            return Decision.DRAFT_ONLY

        # 关系风险特殊处理
        if rel_result.risk_score >= 4 and base_decision == Decision.REQUIRE_APPROVAL:
            return Decision.ESCALATE_TO_HUMAN

        # 动作风险特殊处理
        if act_result.risk_score >= 4:
            return Decision.ESCALATE_TO_HUMAN

        return base_decision

    def _build_reason(
        self,
        overall_level: RiskLevel,
        rel_result: RiskEvaluationResult,
        act_result: RiskEvaluationResult,
        con_result: RiskEvaluationResult,
        conq_result: RiskEvaluationResult,
        recommendation: Decision,
    ) -> str:
        """构建决策原因说明"""
        reasons = [
            f"Overall: {overall_level.value}",
            f"Relationship: {rel_result.risk_level.value}({rel_result.risk_score})",
            f"Action: {act_result.risk_level.value}({act_result.risk_score})",
            f"Content: {con_result.risk_level.value}({con_result.risk_score})",
            f"Consequence: {conq_result.risk_level.value}({conq_result.risk_score})",
            f"Decision: {recommendation.value}",
        ]
        return " | ".join(reasons)

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

    def get_assessment(self, assessment_id: UUID) -> RiskAssessment | None:
        """获取风险评估记录"""
        return self._assessments.get(assessment_id)
