"""Sender stack contracts for delegated communication."""

from typing import Any
from uuid import UUID

from pydantic import Field, model_validator

from myproj.core.contracts.common import ActorRef, ContractModel
from myproj.core.contracts.disclosure import DisclosureMode


class SenderStack(ContractModel):
    """Who is represented, who drafted, who approved, and who executed an action."""

    owner: ActorRef
    delegate: ActorRef | None = None
    author: ActorRef
    approver: ActorRef | None = None
    executor: ActorRef | None = None
    disclosure_mode: DisclosureMode
    authority_source: UUID
    authority_label: str | None = Field(None, max_length=200)
    representation_note: str | None = Field(None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_sender_stack(self) -> "SenderStack":
        if self.delegate and self.delegate.principal_id == self.owner.principal_id:
            raise ValueError("delegate must differ from owner when present")

        if self.author.principal_id == self.owner.principal_id and self.delegate is not None:
            return self

        return self

    def visible_actor_ids(self) -> list[UUID]:
        """Return the ordered actor identifiers currently attached to the stack."""
        actor_ids: list[UUID] = [self.owner.principal_id]
        for actor in (self.delegate, self.author, self.approver, self.executor):
            if actor is None:
                continue
            if actor.principal_id not in actor_ids:
                actor_ids.append(actor.principal_id)
        return actor_ids

