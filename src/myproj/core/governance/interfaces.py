"""
Governance service interfaces - Defines the contract for governance services.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from myproj.core.contracts import (
    ActionEnvelope,
    AuthorityGrant,
    DelegationMode,
    RiskLevel,
    SenderStack,
)
from myproj.core.governance.types import GovernanceDecision, GovernanceResult


class GovernanceService(ABC):
    """Main governance service interface."""

    @abstractmethod
    def evaluate_action(
        self,
        envelope: ActionEnvelope,
    ) -> GovernanceResult:
        """
        Evaluate whether an action should be allowed, denied, or need approval.

        Args:
            envelope: The action envelope containing all context

        Returns:
            GovernanceResult with the decision
        """
        pass

    @abstractmethod
    def can_auto_execute(
        self,
        envelope: ActionEnvelope,
    ) -> bool:
        """
        Check if an action can be auto-executed without approval.

        Args:
            envelope: The action envelope

        Returns:
            True if auto-execution is allowed
        """
        pass


class DelegationService(ABC):
    """Delegation service interface."""

    @abstractmethod
    def get_active_grant_for_delegate(
        self,
        grantor_id: UUID,
        delegate_id: UUID,
        action_type: str | None = None,
    ) -> AuthorityGrant | None:
        """
        Get the active authority grant between grantor and delegate.

        Args:
            grantor_id: Who is granting authority
            delegate_id: Who is receiving authority
            action_type: Optional action type filter

        Returns:
            Active AuthorityGrant if one exists
        """
        pass

    @abstractmethod
    def validate_grant_for_action(
        self,
        grant: AuthorityGrant,
        action_type: str,
        risk_level: RiskLevel,
    ) -> GovernanceResult:
        """
        Validate if a grant allows a specific action.

        Args:
            grant: The authority grant to check
            action_type: The action being performed
            risk_level: Risk level of the action

        Returns:
            GovernanceResult with validation outcome
        """
        pass

    @abstractmethod
    def build_sender_stack(
        self,
        grant: AuthorityGrant,
        author_id: UUID,
        approver_id: UUID | None = None,
        executor_id: UUID | None = None,
    ) -> SenderStack:
        """
        Build a sender stack from an authority grant.

        Args:
            grant: The authority grant
            author_id: Who authored the content
            approver_id: Who approved (optional)
            executor_id: Who will execute (optional)

        Returns:
            Constructed SenderStack
        """
        pass
