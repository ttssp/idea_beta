"""Authority grant contracts for delegated action rights."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from myproj.core.contracts.common import (
    ActorRef,
    ContractModel,
    DelegationMode,
    RiskLevel,
    dedupe_strings,
    dedupe_uuids,
    utc_now,
)
from myproj.core.contracts.disclosure import DisclosurePolicy


class AuthorityGrantStatus(StrEnum):
    """Lifecycle states for delegated authority."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class RelationshipScope(ContractModel):
    """The relationship slice in which a grant may be exercised."""

    include_all: bool = True
    relationship_ids: list[UUID] = Field(default_factory=list)
    relationship_classes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_scope(self) -> "RelationshipScope":
        self.relationship_ids = dedupe_uuids(self.relationship_ids)
        self.relationship_classes = dedupe_strings(self.relationship_classes)

        if self.include_all and (self.relationship_ids or self.relationship_classes):
            raise ValueError("Scoped relationship selectors must be empty when include_all is true")

        if not self.include_all and not (self.relationship_ids or self.relationship_classes):
            raise ValueError(
                "At least one relationship selector is required when include_all is false"
            )

        return self


class ThreadScope(ContractModel):
    """The thread slice in which a grant may be exercised."""

    include_all: bool = True
    thread_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_scope(self) -> "ThreadScope":
        self.thread_ids = dedupe_uuids(self.thread_ids)

        if self.include_all and self.thread_ids:
            raise ValueError("thread_ids must be empty when include_all is true")

        if not self.include_all and not self.thread_ids:
            raise ValueError("At least one thread_id is required when include_all is false")

        return self


class AuthorityGrant(ContractModel):
    """A first-class record of who may act on whose behalf and under what bounds."""

    authority_grant_id: UUID = Field(default_factory=uuid4)
    grantor: ActorRef
    delegate: ActorRef
    delegation_mode: DelegationMode
    allowed_actions: list[str] = Field(default_factory=list)
    requires_approval_for: list[str] = Field(default_factory=list)
    relationship_scope: RelationshipScope = Field(default_factory=RelationshipScope)
    thread_scope: ThreadScope = Field(default_factory=ThreadScope)
    max_risk_level: RiskLevel = RiskLevel.MEDIUM
    disclosure_policy: DisclosurePolicy
    granted_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    status: AuthorityGrantStatus = AuthorityGrantStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_grant(self) -> "AuthorityGrant":
        self.allowed_actions = dedupe_strings(self.allowed_actions)
        self.requires_approval_for = dedupe_strings(self.requires_approval_for)

        if self.grantor.principal_id == self.delegate.principal_id:
            raise ValueError("grantor and delegate must be different principals")

        delegated_modes = {
            DelegationMode.DRAFT_FIRST,
            DelegationMode.APPROVE_TO_SEND,
            DelegationMode.BOUNDED_AUTO,
        }
        if self.delegation_mode in delegated_modes and not self.allowed_actions:
            raise ValueError("allowed_actions are required for delegated execution modes")

        if set(self.requires_approval_for) - set(self.allowed_actions):
            raise ValueError("requires_approval_for must be a subset of allowed_actions")

        if self.expires_at and self.expires_at <= self.granted_at:
            raise ValueError("expires_at must be later than granted_at")

        if self.revoked_at and self.status == AuthorityGrantStatus.ACTIVE:
            raise ValueError("active grants cannot define revoked_at")

        return self

    @property
    def is_currently_active(self) -> bool:
        """Whether the grant is usable at the current time."""
        if self.status != AuthorityGrantStatus.ACTIVE:
            return False
        if self.expires_at and self.expires_at <= utc_now():
            return False
        return True

