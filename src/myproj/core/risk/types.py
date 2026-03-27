"""
Risk types - Use frozen contracts where possible.

DO NOT redefine enums already in myproj.core.contracts.
Import from contracts instead.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from myproj.core.contracts import RiskLevel


class RiskFactor(StrEnum):
    """Risk factor categories."""

    CONTENT = "content"
    RELATIONSHIP = "relationship"
    ACTION = "action"
    EXTERNAL = "external"
    RECIPIENT = "recipient"


class RiskReason:
    """A specific risk reason with code and description."""

    def __init__(
        self,
        reason_code: str,
        factor: RiskFactor,
        description: str,
        severity: RiskLevel,
        metadata: dict[str, Any] | None = None,
    ):
        self.reason_code = reason_code
        self.factor = factor
        self.description = description
        self.severity = severity
        self.metadata = metadata or {}
        self.evaluated_at = datetime.utcnow()


class RiskEvaluation:
    """Complete risk evaluation result."""

    def __init__(
        self,
        overall_risk: RiskLevel,
        reasons: list[RiskReason],
        requires_approval: bool = False,
        requires_escalation: bool = False,
        summary: str | None = None,
    ):
        self.overall_risk = overall_risk
        self.reasons = reasons
        self.requires_approval = requires_approval
        self.requires_escalation = requires_escalation
        self.summary = summary
        self.evaluated_at = datetime.utcnow()

    @property
    def reason_codes(self) -> list[str]:
        """Get list of reason codes."""
        return [reason.reason_code for reason in self.reasons]

    @property
    def highest_severity(self) -> RiskLevel:
        """Get the highest severity from all reasons."""
        if not self.reasons:
            return RiskLevel.LOW

        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }

        return max(
            self.reasons,
            key=lambda r: risk_order[r.severity]
        ).severity
