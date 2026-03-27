"""Action envelope contracts shared by core, UI, and execution fabric."""

from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from myproj.core.contracts.common import ContractModel, RiskLevel, dedupe_strings, dedupe_uuids
from myproj.core.contracts.disclosure import DisclosurePreview
from myproj.core.contracts.sender_stack import SenderStack


class ChannelKind(StrEnum):
    """Execution channels supported by action envelopes."""

    INTERNAL = "internal"
    EMAIL = "email"
    CALENDAR = "calendar"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    CUSTOM = "custom"


class ActionExecutionMode(StrEnum):
    """Whether an action is being prepared, auto-run, or waiting on approval."""

    PREPARE_ONLY = "prepare_only"
    EXECUTE_IMMEDIATELY = "execute_immediately"
    EXECUTE_AFTER_APPROVAL = "execute_after_approval"


class ThreadContextRef(ContractModel):
    """Thread context needed by downstream systems."""

    thread_id: UUID
    objective: str | None = Field(None, max_length=2000)
    thread_status: str | None = Field(None, max_length=100)
    participant_ids: list[UUID] = Field(default_factory=list)
    relationship_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def _normalize_lists(self) -> "ThreadContextRef":
        self.participant_ids = dedupe_uuids(self.participant_ids)
        self.relationship_ids = dedupe_uuids(self.relationship_ids)
        return self


class RelationshipContextRef(ContractModel):
    """Relationship context for policy and risk evaluation."""

    relationship_ids: list[UUID] = Field(default_factory=list)
    relationship_classes: list[str] = Field(default_factory=list)
    is_sensitive: bool = False

    @model_validator(mode="after")
    def _normalize_lists(self) -> "RelationshipContextRef":
        self.relationship_ids = dedupe_uuids(self.relationship_ids)
        self.relationship_classes = dedupe_strings(self.relationship_classes)
        return self


class ActionTarget(ContractModel):
    """Who or what the action is aimed at."""

    channel: ChannelKind
    recipient_ids: list[UUID] = Field(default_factory=list)
    recipient_handles: list[str] = Field(default_factory=list)
    subject: str | None = Field(None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_target(self) -> "ActionTarget":
        self.recipient_ids = dedupe_uuids(self.recipient_ids)
        self.recipient_handles = dedupe_strings(self.recipient_handles)

        if not self.recipient_ids and not self.recipient_handles:
            raise ValueError("At least one recipient identifier is required")

        return self


class RiskPosture(ContractModel):
    """Risk information attached to a proposed action."""

    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    summary: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def _normalize_reason_codes(self) -> "RiskPosture":
        self.reason_codes = dedupe_strings(self.reason_codes)
        return self


class ActionEnvelope(ContractModel):
    """A stable action contract shared across planning, approval, and execution."""

    envelope_id: UUID = Field(default_factory=uuid4)
    action_type: str = Field(..., min_length=1, max_length=100)
    action_label: str | None = Field(None, max_length=200)
    thread: ThreadContextRef
    relationships: RelationshipContextRef = Field(default_factory=RelationshipContextRef)
    sender_stack: SenderStack
    disclosure_preview: DisclosurePreview
    target: ActionTarget
    risk_posture: RiskPosture = Field(default_factory=RiskPosture)
    execution_mode: ActionExecutionMode = ActionExecutionMode.PREPARE_ONLY
    approval_request_id: UUID | None = None
    idempotency_key: str | None = Field(None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_envelope(self) -> "ActionEnvelope":
        if (
            self.execution_mode == ActionExecutionMode.EXECUTE_AFTER_APPROVAL
            and not self.risk_posture.requires_approval
            and self.approval_request_id is None
        ):
            raise ValueError(
                "execute_after_approval requires risk_posture.requires_approval or approval_request_id"
            )

        return self

