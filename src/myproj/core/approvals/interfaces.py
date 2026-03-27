"""
Approval service interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from myproj.core.contracts import ActionEnvelope
from myproj.core.approvals.types import (
    ApprovalAction,
    ApprovalRequest,
    ApprovalResolution,
    ApprovalStatus,
)


class ApprovalService(ABC):
    """Approval service interface."""

    @abstractmethod
    def create_request(
        self,
        envelope: ActionEnvelope,
        requester_principal_id: UUID,
        approver_principal_id: UUID,
        reason_code: str,
        reason_description: str | None = None,
        timeout_hours: int = 24,
    ) -> ApprovalRequest:
        """
        Create a new approval request.

        Args:
            envelope: The action envelope requiring approval
            requester_principal_id: Who is requesting approval
            approver_principal_id: Who needs to approve
            reason_code: Machine-readable reason code
            reason_description: Human-readable reason
            timeout_hours: How long before timeout

        Returns:
            Created ApprovalRequest
        """
        pass

    @abstractmethod
    def get_request(
        self,
        approval_id: UUID,
    ) -> ApprovalRequest | None:
        """
        Get an approval request by ID.

        Args:
            approval_id: The approval request ID

        Returns:
            ApprovalRequest if found
        """
        pass

    @abstractmethod
    def list_requests(
        self,
        approver_principal_id: UUID | None = None,
        thread_id: UUID | None = None,
        status: ApprovalStatus | None = None,
        limit: int = 100,
    ) -> list[ApprovalRequest]:
        """
        List approval requests with filters.

        Args:
            approver_principal_id: Filter by approver
            thread_id: Filter by thread
            status: Filter by status
            limit: Maximum number to return

        Returns:
            List of matching ApprovalRequest
        """
        pass

    @abstractmethod
    def resolve_request(
        self,
        approval_id: UUID,
        action: ApprovalAction,
        resolved_by_principal_id: UUID,
        comment: str | None = None,
        modified_envelope: ActionEnvelope | None = None,
    ) -> ApprovalRequest:
        """
        Resolve an approval request.

        Args:
            approval_id: The approval request to resolve
            action: What action to take
            resolved_by_principal_id: Who is resolving
            comment: Optional comment
            modified_envelope: Modified envelope if action is MODIFY

        Returns:
            Updated ApprovalRequest
        """
        pass

    @abstractmethod
    def approve(
        self,
        approval_id: UUID,
        approver_principal_id: UUID,
        comment: str | None = None,
    ) -> ApprovalRequest:
        """
        Approve a request (convenience method).

        Args:
            approval_id: The approval request
            approver_principal_id: Who is approving
            comment: Optional comment

        Returns:
            Updated ApprovalRequest
        """
        pass

    @abstractmethod
    def reject(
        self,
        approval_id: UUID,
        approver_principal_id: UUID,
        comment: str | None = None,
    ) -> ApprovalRequest:
        """
        Reject a request (convenience method).

        Args:
            approval_id: The approval request
            approver_principal_id: Who is rejecting
            comment: Optional comment

        Returns:
            Updated ApprovalRequest
        """
        pass

    @abstractmethod
    def take_over(
        self,
        approval_id: UUID,
        principal_id: UUID,
        comment: str | None = None,
    ) -> ApprovalRequest:
        """
        Take over a request (convenience method).

        Args:
            approval_id: The approval request
            principal_id: Who is taking over
            comment: Optional comment

        Returns:
            Updated ApprovalRequest
        """
        pass
