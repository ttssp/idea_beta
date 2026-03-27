"""Shared contract primitives for Communication OS."""

from collections.abc import Iterable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def dedupe_strings(values: Iterable[str]) -> list[str]:
    """Preserve order while removing duplicate strings."""
    return list(dict.fromkeys(values))


def dedupe_uuids(values: Iterable[UUID]) -> list[UUID]:
    """Preserve order while removing duplicate UUIDs."""
    return list(dict.fromkeys(values))


class ContractModel(BaseModel):
    """Base class for product-facing contracts."""

    model_config = ConfigDict(extra="forbid")


class PrincipalKind(StrEnum):
    """High-level principal categories used by contract objects."""

    HUMAN = "human"
    PERSONAL_AGENT = "personal_agent"
    ORGANIZATION_AGENT = "organization_agent"
    SERVICE_AGENT = "service_agent"
    EXTERNAL_PARTICIPANT = "external_participant"
    PUBLIC_SERVICE_AGENT = "public_service_agent"


class DelegationMode(StrEnum):
    """Delegation levels shared across product contracts."""

    OBSERVE_ONLY = "observe_only"
    DRAFT_FIRST = "draft_first"
    APPROVE_TO_SEND = "approve_to_send"
    BOUNDED_AUTO = "bounded_auto"
    HUMAN_ONLY = "human_only"


class RiskLevel(StrEnum):
    """Risk posture shared across contract surfaces."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.CRITICAL: 3,
}


class ActorRef(ContractModel):
    """A stable actor reference used across sender, authority, and action contracts."""

    principal_id: UUID
    display_name: str = Field(..., min_length=1, max_length=200)
    principal_kind: PrincipalKind
    affiliation_id: UUID | None = None
    affiliation_name: str | None = Field(None, max_length=200)
    is_human_controlled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_agent(self) -> bool:
        """Whether the actor is some form of delegated or autonomous agent."""
        return self.principal_kind in {
            PrincipalKind.PERSONAL_AGENT,
            PrincipalKind.ORGANIZATION_AGENT,
            PrincipalKind.SERVICE_AGENT,
            PrincipalKind.PUBLIC_SERVICE_AGENT,
        }

