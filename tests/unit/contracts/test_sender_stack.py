"""Sender stack contract tests."""

from uuid import uuid4

import pytest

from myproj.core.contracts.common import ActorRef, PrincipalKind
from myproj.core.contracts.disclosure import DisclosureMode
from myproj.core.contracts.sender_stack import SenderStack


def actor(name: str, kind: PrincipalKind) -> ActorRef:
    return ActorRef(principal_id=uuid4(), display_name=name, principal_kind=kind)


class TestSenderStack:
    def test_delegate_must_differ_from_owner(self):
        owner = actor("Owner", PrincipalKind.HUMAN)
        with pytest.raises(ValueError):
            SenderStack(
                owner=owner,
                delegate=owner,
                author=owner,
                disclosure_mode=DisclosureMode.SEMI,
                authority_source=uuid4(),
            )

    def test_visible_actor_ids_dedupes_order(self):
        owner = actor("Owner", PrincipalKind.HUMAN)
        delegate = actor("Delegate", PrincipalKind.PERSONAL_AGENT)
        stack = SenderStack(
            owner=owner,
            delegate=delegate,
            author=delegate,
            approver=owner,
            disclosure_mode=DisclosureMode.FULL,
            authority_source=uuid4(),
        )

        assert stack.visible_actor_ids() == [owner.principal_id, delegate.principal_id]

