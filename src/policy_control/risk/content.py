
"""
Content Risk Evaluator

内容风险评估器（规则层：关键词/模式匹配）
"""
import re
from typing import List, Optional
from ..common.constants import RiskLevel
from .models import RiskEvaluationResult


class ContentRiskEvaluator:
    """
    内容风险评估器

    基于关键词/模式的内容风险检测
    """

    # 高风险关键词（触发CRITICAL风险）
    CRITICAL_KEYWORDS = [
        r"\$[\d,]+(\.\d{2})?",  # 金钱金额
        r"€[\d,]+(\.\d{2})?",
        r"¥[\d,]+(\.\d{2})?",
        r"price",
        r"discount",
        r"payment",
        r"contract",
        r"agreement",
        r"legally binding",
        r"guarantee",
        r"warranty",
        r"commit to",
        r"promise",
        r"we will",
        r"i promise",
    ]

    # 高风险关键词（触发HIGH风险）
    HIGH_KEYWORDS = [
        r"terminate",
        r"cancel",
        r"end the relationship",
        r"complain",
        r"complaint",
        r"frustrated",
        r"disappointed",
        r"angry",
        r"upset",
        r"refuse",
        r"reject",
        r"deny",
        r"confidential",
        r"private",
        r"secret",
        r"ssn",
        r"social security",
        r"credit card",
        r"bank account",
        r"password",
    ]

    # 中风险关键词（触发MEDIUM风险）
    MEDIUM_KEYWORDS = [
        r"need to confirm",
        r"please confirm",
        r"can you confirm",
        r"urgent",
        r"asap",
        r"important",
        r"critical",
    ]

    def __init__(self):
        # 预编译正则表达式
        self._critical_patterns = [re.compile(p, re.IGNORECASE) for p in self.CRITICAL_KEYWORDS]
        self._high_patterns = [re.compile(p, re.IGNORECASE) for p in self.HIGH_KEYWORDS]
        self._medium_patterns = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_KEYWORDS]

    def evaluate(
        self,
        content: Optional[str] = None,
    ) -&gt; RiskEvaluationResult:
        """
        评估内容风险

        Args:
            content: 待评估的内容

        Returns:
            风险评估结果
        """
        risk_factors = []
        risk_score = 1  # 默认低风险

        if not content or not content.strip():
            return RiskEvaluationResult(
                risk_score=1,
                risk_level=RiskLevel.LOW,
                risk_factors=[],
                reason="No content to evaluate",
            )

        # 检查CRITICAL关键词
        for pattern in self._critical_patterns:
            if pattern.search(content):
                risk_score = max(risk_score, 5)
                risk_factors.append(f"critical_pattern:{pattern.pattern[:20]}")

        # 检查HIGH关键词
        for pattern in self._high_patterns:
            if pattern.search(content):
                risk_score = max(risk_score, 4)
                risk_factors.append(f"high_pattern:{pattern.pattern[:20]}")

        # 检查MEDIUM关键词
        for pattern in self._medium_patterns:
            if pattern.search(content):
                risk_score = max(risk_score, 3)
                risk_factors.append(f"medium_pattern:{pattern.pattern[:20]}")

        risk_level = self._score_to_level(risk_score)

        return RiskEvaluationResult(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            reason=f"Content risk -&gt; {risk_level.value} (factors: {len(risk_factors)})",
        )

    def _score_to_level(self, score: int) -&gt; RiskLevel:
        """将风险分数转换为风险等级"""
        if score &lt;= 1:
            return RiskLevel.LOW
        elif score &lt;= 2:
            return RiskLevel.LOW
        elif score &lt;= 3:
            return RiskLevel.MEDIUM
        elif score &lt;= 4:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
