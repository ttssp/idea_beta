"""
Delegation Service implementation.

This is a placeholder implementation that will be filled with
logic migrated from src/policy_control/delegation/.
"""

from typing import Any
from uuid import UUID

from myproj.core.contracts import (
    ActorRef,
    AuthorityGrant,
    DelegationMode,
    DisclosureMode,
    PrincipalKind,
    RiskLevel,
    SenderStack,
)
from myproj.core.governance.interfaces import DelegationService
from myproj.core.governance.types import GovernanceDecision, GovernanceResult


class DelegationServiceImpl(DelegationService):
    """
    Delegation service implementation.

    TODO: Migrate implementation from policy_control/delegation/
    """

    def __init__(self):
        # Temporary in-memory storage - will use repository later
        self._grants: dict[UUID, AuthorityGrant] = {}

    def get_active_grant_for_delegate(
        self,
        grantor_id: UUID,
        delegate_id: UUID,
        action_type: str | None = None,
    ) -> AuthorityGrant | None:
        """
        Get the active authority grant between grantor and delegate.

        TODO: Implement with proper repository lookup
        """
        for grant in self._grants.values():
            if (
                grant.is_currently_active
                and grant.grantor.principal_id == grantor_id
                and grant.delegate.principal_id == delegate_id
            ):
                if action_type:
                    if action_type not in grant.allowed_actions:
                        continue
                return grant
        return None

    def validate_grant_for_action(
        self,
        grant: AuthorityGrant,
        action_type: str,
        risk_level: RiskLevel,
    ) -> GovernanceResult:
        """
        Validate if a grant allows a specific action.

        TODO: Implement full validation logic
        """
        if not grant.is_currently_active:
            return GovernanceResult(
                decision=GovernanceDecision.DENY,
                reason_code="grant_inactive",
                reason_description="The authority grant is not active",
            )

        if action_type not in grant.allowed_actions:
            return GovernanceResult(
                decision=GovernanceDecision.DENY,
                reason_code="action_not_allowed",
                reason_description=f"Action '{action_type}' not allowed by this grant",
            )

        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }

        if risk_order[risk_level] > risk_order[grant.max_risk_level]:
            return GovernanceResult(
                decision=GovernanceDecision.DENY,
                reason_code="risk_exceeded",
                reason_description=f"Risk {risk_level} exceeds max {grant.max_risk_level}",
            )

        if action_type in grant.requires_approval_for:
            return GovernanceResult(
                decision=GovernanceDecision.REQUIRE_APPROVAL,
                reason_code="approval_required",
                reason_description=f"Action '{action_type}' requires approval",
                risk_level=risk_level,
            )

        return GovernanceResult(
            decision=GovernanceDecision.ALLOW,
            reason_code="allowed",
            reason_description="Action is allowed by this grant",
            risk_level=risk_level,
        )

    def build_sender_stack(
        self,
        grant: AuthorityGrant,
        author_id: UUID,
        approver_id: UUID | None = None,
        executor_id: UUID | None = None,
    ) -> SenderStack:
        """
        Build a sender stack from an authority grant.

        TODO: Implement with proper ActorRef lookup
        """
        # Create minimal ActorRefs - in real implementation, these would be
        # looked up from a principal repository
        author_ref = ActorRef(
            principal_id=author_id,
            display_name="Author",
            principal_kind=PrincipalKind.PERSONAL_AGENT,
            is_human_controlled=False,
        )

        approver_ref: ActorRef | None = None
        if approver_id:
            approver_ref = ActorRef(
                principal_id=approver_id,
                display_name="Approver",
                principal_kind=PrincipalKind.HUMAN,
                is_human_controlled=True,
            )

        executor_ref: ActorRef | None = None
        if executor_id:
            executor_ref = ActorRef(
                principal_id=executor_id,
                display_name="Executor",
                principal_kind=PrincipalKind.SERVICE_AGENT,
                is_human_controlled=False,
            )

        return SenderStack(
            owner=grant.grantor,
            delegate=grant.delegate,
            author=author_ref,
            approver=approver_ref,
            executor=executor_ref,
            disclosure_mode=grant.disclosure_policy.default_mode,
            authority_source=grant.authority_grant_id,
        )

    def add_grant(self, grant: AuthorityGrant) -> None:
        """Add a grant (temporary method for testing)."""
        self._grants[grant.authority_grant_id] = grant
