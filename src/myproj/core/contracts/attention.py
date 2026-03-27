"""Attention firewall contracts for Communication OS."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from myproj.core.contracts.common import ContractModel


class AttentionDisposition(StrEnum):
    """How the system wants a human to handle a communication outcome."""

    MUST_REVIEW_NOW = "must_review_now"
    APPROVAL_REQUIRED = "approval_required"
    INFORMATIONAL_ONLY = "informational_only"
    SUMMARY_ONLY = "summary_only"
    AUTO_RESOLVABLE = "auto_resolvable"
    DIRECT_HUMAN_REQUIRED = "direct_human_required"


class AttentionDecision(ContractModel):
    """A structured result from the future inbox or attention firewall."""

    decision_id: UUID = Field(default_factory=uuid4)
    target_principal_id: UUID
    disposition: AttentionDisposition
    reason_code: str = Field(..., min_length=1, max_length=100)
    summary: str = Field(..., min_length=1, max_length=500)
    related_thread_id: UUID | None = None
    related_action_id: UUID | None = None
    requires_human_action: bool = False
    notify_now: bool = True
    due_at: datetime | None = None
    suppress_until: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_attention(self) -> "AttentionDecision":
        human_required = {
            AttentionDisposition.MUST_REVIEW_NOW,
            AttentionDisposition.APPROVAL_REQUIRED,
            AttentionDisposition.DIRECT_HUMAN_REQUIRED,
        }

        if self.disposition in human_required and not self.requires_human_action:
            raise ValueError("requires_human_action must be true for human-gated dispositions")

        if self.disposition == AttentionDisposition.AUTO_RESOLVABLE and self.requires_human_action:
            raise ValueError("auto_resolvable decisions cannot require human action")

        if self.suppress_until and self.due_at and self.suppress_until > self.due_at:
            raise ValueError("suppress_until cannot be later than due_at")

        return self

