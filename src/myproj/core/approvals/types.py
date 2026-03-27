"""
Approval types - Use frozen contracts where possible.

DO NOT redefine enums already in myproj.core.contracts.
Import from contracts instead.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from myproj.core.contracts import (
    ActionEnvelope,
    DisclosurePreview,
    RiskPosture,
    SenderStack,
)


class ApprovalStatus(StrEnum):
    """Lifecycle states for an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TAKEN_OVER = "taken_over"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"


class ApprovalAction(StrEnum):
    """Actions that can be taken on an approval request."""

    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    TAKE_OVER = "take_over"
    CANCEL = "cancel"
    ESCALATE = "escalate"


class ApprovalRequest(BaseModel):
    """An approval request with sender stack and action preview."""

    model_config = {"extra": "forbid"}

    approval_id: UUID = Field(default_factory=uuid4)
    thread_id: UUID
    action_envelope: ActionEnvelope | None = None

    # Sender stack preview
    sender_stack: SenderStack | None = None

    # Disclosure preview
    disclosure_preview: DisclosurePreview | None = None

    # Risk posture
    risk_posture: RiskPosture | None = None

    # Request metadata
    requester_principal_id: UUID
    approver_principal_id: UUID
    reason_code: str = Field(..., min_length=1, max_length=100)
    reason_description: str | None = Field(None, max_length=500)

    # Lifecycle
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None
    timeout_at: datetime | None = None

    # Resolution
    resolution: "ApprovalResolution | None" = None

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    @property
    def is_resolved(self) -> bool:
        return self.status in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.MODIFIED,
            ApprovalStatus.TAKEN_OVER,
            ApprovalStatus.CANCELLED,
            ApprovalStatus.ESCALATED,
        }

    @property
    def is_approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED


class ApprovalResolution(BaseModel):
    """The resolution of an approval request."""

    model_config = {"extra": "forbid"}

    action: ApprovalAction
    resolved_by_principal_id: UUID
    resolved_at: datetime = Field(default_factory=datetime.utcnow)
    comment: str | None = Field(None, max_length=1000)
    modified_envelope: ActionEnvelope | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# Rebuild ApprovalRequest to include ApprovalResolution
ApprovalRequest.model_rebuild()
