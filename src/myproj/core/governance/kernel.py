"""
Governance Kernel - Unified entry point for governance services.

This class orchestrates all governance functionality:
- Delegation checks
- Policy evaluation
- Risk synthesis
- Approval coordination
"""

from typing import Any
from uuid import UUID

from myproj.core.contracts import (
    ActionEnvelope,
    AuthorityGrant,
    DelegationMode,
    RiskLevel,
    SenderStack,
)
from myproj.core.governance.interfaces import GovernanceService, DelegationService
from myproj.core.governance.types import GovernanceDecision, GovernanceResult


class GovernanceKernel:
    """
    Unified governance kernel for Communication OS.

    This is the main entry point for all governance operations.
    """

    def __init__(
        self,
        governance_service: GovernanceService,
        delegation_service: DelegationService,
    ):
        self.governance_service = governance_service
        self.delegation_service = delegation_service

    def evaluate_action_envelope(
        self,
        envelope: ActionEnvelope,
    ) -> GovernanceResult:
        """
        Evaluate a complete action envelope through the governance stack.

        This is the primary method for evaluating whether an action should proceed.

        Args:
            envelope: The action envelope to evaluate

        Returns:
            GovernanceResult with the final decision
        """
        # Delegate to the governance service for now
        # In the future, this will orchestrate policy, risk, delegation checks
        return self.governance_service.evaluate_action(envelope)

    def get_sender_stack_for_action(
        self,
        envelope: ActionEnvelope,
        grant: AuthorityGrant,
    ) -> SenderStack:
        """
        Build the sender stack for an action using a grant.

        Args:
            envelope: The action envelope
            grant: The authority grant to use

        Returns:
            Constructed SenderStack
        """
        return self.delegation_service.build_sender_stack(
            grant=grant,
            author_id=envelope.sender_stack.author.principal_id,
            approver_id=envelope.sender_stack.approver.principal_id
            if envelope.sender_stack.approver
            else None,
            executor_id=envelope.sender_stack.executor.principal_id
            if envelope.sender_stack.executor
            else None,
        )

    def check_auto_execution_allowed(
        self,
        envelope: ActionEnvelope,
    ) -> bool:
        """
        Check if auto-execution is allowed for this envelope.

        Args:
            envelope: The action envelope

        Returns:
            True if auto-execution is allowed
        """
        return self.governance_service.can_auto_execute(envelope)

    def get_active_grant(
        self,
        grantor_id: UUID,
        delegate_id: UUID,
        action_type: str | None = None,
    ) -> AuthorityGrant | None:
        """
        Get an active authority grant.

        Args:
            grantor_id: Who is granting authority
            delegate_id: Who is receiving authority
            action_type: Optional action type filter

        Returns:
            Active AuthorityGrant if one exists
        """
        return self.delegation_service.get_active_grant_for_delegate(
            grantor_id=grantor_id,
            delegate_id=delegate_id,
            action_type=action_type,
        )
