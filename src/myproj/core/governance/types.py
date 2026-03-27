"""
Governance types - Use frozen contracts where possible.

DO NOT redefine enums already in myproj.core.contracts.
Import from contracts instead.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from myproj.core.contracts import (
    ActorRef,
    AuthorityGrant,
    DelegationMode,
    RiskLevel,
)


class GovernanceDecision(StrEnum):
    """Result of a governance evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class GovernanceResult:
    """Result of a governance check."""

    def __init__(
        self,
        decision: GovernanceDecision,
        reason_code: str,
        reason_description: str | None = None,
        risk_level: RiskLevel = RiskLevel.LOW,
        metadata: dict[str, Any] | None = None,
    ):
        self.decision = decision
        self.reason_code = reason_code
        self.reason_description = reason_description
        self.risk_level = risk_level
        self.metadata = metadata or {}
        self.evaluated_at = datetime.utcnow()

    @property
    def is_allowed(self) -> bool:
        return self.decision == GovernanceDecision.ALLOW

    @property
    def requires_approval(self) -> bool:
        return self.decision == GovernanceDecision.REQUIRE_APPROVAL

    @property
    def should_escalate(self) -> bool:
        return self.decision == GovernanceDecision.ESCALATE

    @property
    def is_denied(self) -> bool:
        return self.decision == GovernanceDecision.DENY
