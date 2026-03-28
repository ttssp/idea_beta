"""
Tests for ActionEnvelope adapter in E3.

These tests verify that E3 correctly handles the shared ActionEnvelope contract.
"""

import pytest
from uuid import UUID, uuid4

from myproj.core.contracts.actions import (
    ActionEnvelope,
    ActionExecutionMode,
    ActionTarget,
    ChannelKind,
    RelationshipContextRef,
    RiskPosture,
    ThreadContextRef,
)
from myproj.core.contracts.common import RiskLevel, ActorRef, PrincipalKind
from myproj.core.contracts.disclosure import DisclosurePreview, DisclosureMode
from myproj.core.contracts.sender_stack import SenderStack

from e3.action_runtime.contract_adapter import (
    ActionEnvelopeAdapter,
    ExecutionResultEmitter,
)


def create_test_envelope(**kwargs) -> ActionEnvelope:
    """Create a test ActionEnvelope with default values."""
    thread_id = uuid4()
    owner_principal_id = uuid4()
    delegate_principal_id = uuid4()
    authority_source = uuid4()

    # Create sender stack
    owner = ActorRef(
        principal_id=owner_principal_id,
        display_name="Test Owner",
        principal_kind=PrincipalKind.HUMAN,
    )
    delegate = ActorRef(
        principal_id=delegate_principal_id,
        display_name="Test Agent",
        principal_kind=PrincipalKind.PERSONAL_AGENT,
    )
    author = ActorRef(
        principal_id=delegate_principal_id,
        display_name="Test Agent",
        principal_kind=PrincipalKind.PERSONAL_AGENT,
    )
    sender_stack = SenderStack(
        owner=owner,
        delegate=delegate,
        author=author,
        approver=None,
        executor=None,
        disclosure_mode=DisclosureMode.FULL,
        authority_source=authority_source,
    )

    # Create disclosure preview
    disclosure_preview = DisclosurePreview(
        policy_id=uuid4(),
        resolved_mode=DisclosureMode.FULL,
        visible_fields=[],
        requires_recipient_notice=True,
    )

    # Create target
    target = ActionTarget(
        channel=ChannelKind.EMAIL,
        recipient_ids=[uuid4()],
        recipient_handles=["test@example.com"],
        subject="Test Subject",
    )

    # Create thread context
    thread = ThreadContextRef(
        thread_id=thread_id,
        objective="Test objective",
        thread_status="active",
        participant_ids=[owner_principal_id],
    )

    # Create relationships context
    relationships = RelationshipContextRef(
        relationship_ids=[],
        relationship_classes=[],
        is_sensitive=False,
    )

    # Create risk posture
    risk_posture = RiskPosture(
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        reason_codes=[],
    )

    defaults = {
        "action_type": "send_email",
        "action_label": "Send Test Email",
        "thread": thread,
        "relationships": relationships,
        "sender_stack": sender_stack,
        "disclosure_preview": disclosure_preview,
        "target": target,
        "risk_posture": risk_posture,
        "execution_mode": ActionExecutionMode.PREPARE_ONLY,
        "payload": {"body": "Test email body"},
    }
    defaults.update(kwargs)

    return ActionEnvelope(**defaults)


class TestActionEnvelopeAdapter:
    """Tests for ActionEnvelopeAdapter."""

    def test_validate_envelope_success(self):
        """Can validate a valid envelope."""
        envelope = create_test_envelope()
        data = envelope.model_dump(mode="json")

        result = ActionEnvelopeAdapter.validate_envelope(data)

        assert result is not None
        assert result.envelope_id == envelope.envelope_id

    def test_validate_envelope_failure(self):
        """Invalid envelope raises ValueError."""
        invalid_data = {"missing": "fields"}

        with pytest.raises(ValueError):
            ActionEnvelopeAdapter.validate_envelope(invalid_data)

    def test_extract_sender_stack(self):
        """Can extract sender stack metadata."""
        envelope = create_test_envelope()

        result = ActionEnvelopeAdapter.extract_sender_stack(envelope)

        assert result["owner_principal_id"] is not None
        assert result["delegate_principal_id"] is not None

    def test_extract_disclosure_preview(self):
        """Can extract disclosure preview."""
        envelope = create_test_envelope()

        result = ActionEnvelopeAdapter.extract_disclosure_preview(envelope)

        assert result["resolved_mode"] == "full"
        assert result["requires_recipient_notice"] is True

    def test_envelope_to_action_input(self):
        """Can convert envelope to action input."""
        envelope = create_test_envelope()

        result = ActionEnvelopeAdapter.envelope_to_action_input(envelope)

        assert result["envelope_id"] == str(envelope.envelope_id)
        assert result["action_type"] == envelope.action_type
        assert result["thread_id"] == str(envelope.thread.thread_id)
        assert result["channel"] == "email"
        assert result["execution_mode"] == "prepare_only"
        assert "sender_stack" in result
        assert "disclosure" in result

    def test_create_replay_event_payload(self):
        """Can create replay event payload."""
        envelope = create_test_envelope()
        action_run_id = uuid4()

        result = ActionEnvelopeAdapter.create_replay_event_payload(
            envelope,
            action_run_id,
            "completed",
            output_payload={"status": "success"},
        )

        assert result["envelope_id"] == str(envelope.envelope_id)
        assert result["action_run_id"] == str(action_run_id)
        assert result["status"] == "completed"
        assert result["output_payload"] == {"status": "success"}
        assert "sender_stack" in result


class TestExecutionResultEmitter:
    """Tests for ExecutionResultEmitter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.envelope = create_test_envelope()
        self.action_run_id = uuid4()
        self.emitter = ExecutionResultEmitter(self.envelope, self.action_run_id)

    def test_emit_planned(self):
        """Can emit planned event."""
        self.emitter.emit_planned({"steps": ["step1", "step2"]})

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "planned"
        assert events[0]["output_payload"]["plan"]["steps"] == ["step1", "step2"]

    def test_emit_approval_required(self):
        """Can emit approval required event."""
        self.emitter.emit_approval_required("Need manager approval")

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "approval_required"

    def test_emit_executing(self):
        """Can emit executing event."""
        self.emitter.emit_executing()

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "executing"

    def test_emit_sent(self):
        """Can emit sent event."""
        self.emitter.emit_sent(external_message_id="msg-123")

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "sent"
        assert events[0]["output_payload"]["external_message_id"] == "msg-123"

    def test_emit_acknowledged(self):
        """Can emit acknowledged event."""
        self.emitter.emit_acknowledged()

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "acknowledged"

    def test_emit_failed(self):
        """Can emit failed event."""
        self.emitter.emit_failed("Network error", retryable=True)

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "failed_retryable"
        assert events[0]["error"] == "Network error"

    def test_emit_completed(self):
        """Can emit completed event."""
        self.emitter.emit_completed({"result": "success"})

        events = self.emitter.get_events()
        assert len(events) == 1
        assert events[0]["status"] == "completed"
        assert events[0]["output_payload"]["result"] == "success"

    def test_multiple_events(self):
        """Can emit multiple events."""
        self.emitter.emit_planned({"steps": []})
        self.emitter.emit_executing()
        self.emitter.emit_completed({"result": "done"})

        events = self.emitter.get_events()
        assert len(events) == 3
        assert events[0]["status"] == "planned"
        assert events[1]["status"] == "executing"
        assert events[2]["status"] == "completed"

    def test_clear_events(self):
        """Can clear events."""
        self.emitter.emit_planned({"steps": []})
        self.emitter.clear_events()

        events = self.emitter.get_events()
        assert len(events) == 0
