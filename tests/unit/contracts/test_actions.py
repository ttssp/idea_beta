"""Action envelope contract tests."""

from uuid import uuid4

import pytest

from myproj.core.contracts.actions import (
    ActionEnvelope,
    ActionExecutionMode,
    ActionTarget,
    ChannelKind,
    RiskPosture,
    ThreadContextRef,
)
from myproj.core.contracts.common import ActorRef, PrincipalKind, RiskLevel
from myproj.core.contracts.disclosure import DisclosureMode, DisclosurePolicy, DisclosurePreview
from myproj.core.contracts.sender_stack import SenderStack


def actor(name: str, kind: PrincipalKind) -> ActorRef:
    return ActorRef(principal_id=uuid4(), display_name=name, principal_kind=kind)


def sender_stack() -> SenderStack:
    owner = actor("Owner", PrincipalKind.HUMAN)
    delegate = actor("Delegate", PrincipalKind.PERSONAL_AGENT)
    return SenderStack(
        owner=owner,
        delegate=delegate,
        author=delegate,
        disclosure_mode=DisclosureMode.SEMI,
        authority_source=uuid4(),
    )


def disclosure_preview() -> DisclosurePreview:
    return DisclosurePreview.from_policy(
        DisclosurePolicy(),
        is_external=True,
        is_sensitive_relationship=False,
        risk_level=RiskLevel.MEDIUM,
    )


class TestActionTarget:
    def test_target_requires_recipients(self):
        with pytest.raises(ValueError):
            ActionTarget(channel=ChannelKind.EMAIL)


class TestActionEnvelope:
    def test_execute_after_approval_requires_gate(self):
        with pytest.raises(ValueError):
            ActionEnvelope(
                action_type="send_message",
                thread=ThreadContextRef(thread_id=uuid4()),
                sender_stack=sender_stack(),
                disclosure_preview=disclosure_preview(),
                target=ActionTarget(
                    channel=ChannelKind.EMAIL,
                    recipient_handles=["candidate@example.com"],
                ),
                risk_posture=RiskPosture(risk_level=RiskLevel.MEDIUM),
                execution_mode=ActionExecutionMode.EXECUTE_AFTER_APPROVAL,
            )

    def test_envelope_serializes_json_safely(self):
        envelope = ActionEnvelope(
            action_type="send_message",
            thread=ThreadContextRef(thread_id=uuid4()),
            sender_stack=sender_stack(),
            disclosure_preview=disclosure_preview(),
            target=ActionTarget(
                channel=ChannelKind.EMAIL,
                recipient_handles=["candidate@example.com"],
            ),
            risk_posture=RiskPosture(risk_level=RiskLevel.MEDIUM, requires_approval=True),
            execution_mode=ActionExecutionMode.EXECUTE_AFTER_APPROVAL,
            approval_request_id=uuid4(),
        )

        payload = envelope.model_dump(mode="json")
        assert payload["action_type"] == "send_message"
        assert payload["execution_mode"] == "execute_after_approval"
        assert payload["sender_stack"]["owner"]["display_name"] == "Owner"

