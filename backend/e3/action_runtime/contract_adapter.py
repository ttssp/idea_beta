"""
ActionEnvelope Adapter for E3

This module adapts the shared ActionEnvelope contract to the E3 action runtime.
"""

from typing import Any
from uuid import UUID

from pydantic import ValidationError

# Import from the shared contracts
from myproj.core.contracts.actions import (
    ActionEnvelope,
    ActionExecutionMode,
    ChannelKind,
)
from myproj.core.contracts.sender_stack import SenderStack
from myproj.core.contracts.disclosure import DisclosurePreview


class ActionEnvelopeAdapter:
    """Adapter for converting ActionEnvelope to/from E3 internal formats."""

    @staticmethod
    def validate_envelope(data: dict[str, Any]) -> ActionEnvelope:
        """
        Validate and parse an ActionEnvelope from raw data.

        Args:
            data: Raw dictionary data to parse

        Returns:
            Validated ActionEnvelope

        Raises:
            ValueError: If validation fails
        """
        try:
            return ActionEnvelope(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid ActionEnvelope: {e}")

    @staticmethod
    def extract_sender_stack(envelope: ActionEnvelope) -> dict[str, Any]:
        """
        Extract sender stack metadata for E3 execution.

        Args:
            envelope: The ActionEnvelope

        Returns:
            Dictionary with sender stack information
        """
        stack = envelope.sender_stack
        return {
            "owner_principal_id": str(stack.owner.principal_id),
            "delegate_principal_id": str(stack.delegate.principal_id) if stack.delegate else None,
            "author_principal_id": str(stack.author.principal_id),
            "approver_principal_id": str(stack.approver.principal_id) if stack.approver else None,
            "executor_principal_id": str(stack.executor.principal_id) if stack.executor else None,
            "disclosure_mode": stack.disclosure_mode.value,
            "authority_source": str(stack.authority_source),
            "authority_label": stack.authority_label,
            "representation_note": stack.representation_note,
        }

    @staticmethod
    def extract_disclosure_preview(envelope: ActionEnvelope) -> dict[str, Any]:
        """
        Extract disclosure preview information.

        Args:
            envelope: The ActionEnvelope

        Returns:
            Dictionary with disclosure preview
        """
        preview = envelope.disclosure_preview
        return {
            "policy_id": str(preview.policy_id),
            "resolved_mode": preview.resolved_mode.value,
            "visible_fields": [field.value for field in preview.visible_fields],
            "rendered_text": preview.rendered_text,
            "requires_recipient_notice": preview.requires_recipient_notice,
        }

    @staticmethod
    def envelope_to_action_input(envelope: ActionEnvelope) -> dict[str, Any]:
        """
        Convert ActionEnvelope to E3 action input format.

        Args:
            envelope: The ActionEnvelope

        Returns:
            Dictionary suitable for E3 action input
        """
        return {
            "envelope_id": str(envelope.envelope_id),
            "action_type": envelope.action_type,
            "action_label": envelope.action_label,
            "thread_id": str(envelope.thread.thread_id),
            "thread_objective": envelope.thread.objective,
            "thread_status": envelope.thread.thread_status,
            "participant_ids": [str(pid) for pid in envelope.thread.participant_ids],
            "relationship_ids": [str(pid) for pid in envelope.thread.relationship_ids],
            "channel": envelope.target.channel.value,
            "recipient_ids": [str(pid) for pid in envelope.target.recipient_ids],
            "recipient_handles": envelope.target.recipient_handles,
            "subject": envelope.target.subject,
            "risk_level": envelope.risk_posture.risk_level.value,
            "requires_approval": envelope.risk_posture.requires_approval,
            "risk_reason_codes": envelope.risk_posture.reason_codes,
            "risk_summary": envelope.risk_posture.summary,
            "execution_mode": envelope.execution_mode.value,
            "approval_request_id": str(envelope.approval_request_id) if envelope.approval_request_id else None,
            "idempotency_key": envelope.idempotency_key,
            "payload": envelope.payload,
            "metadata": envelope.metadata,
            "sender_stack": ActionEnvelopeAdapter.extract_sender_stack(envelope),
            "disclosure": ActionEnvelopeAdapter.extract_disclosure_preview(envelope),
        }

    @staticmethod
    def create_replay_event_payload(
        envelope: ActionEnvelope,
        action_run_id: UUID,
        status: str,
        output_payload: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a replay-friendly event payload from execution results.

        Args:
            envelope: The original ActionEnvelope
            action_run_id: The E3 action run ID
            status: Current execution status
            output_payload: Output from execution, if any
            error: Error message, if any

        Returns:
            Dictionary suitable for core replay events
        """
        return {
            "envelope_id": str(envelope.envelope_id),
            "action_run_id": str(action_run_id),
            "action_type": envelope.action_type,
            "status": status,
            "thread_id": str(envelope.thread.thread_id),
            "sender_stack": ActionEnvelopeAdapter.extract_sender_stack(envelope),
            "output_payload": output_payload,
            "error": error,
            "occurred_at": None,  # Will be set by event store
        }


class ExecutionResultEmitter:
    """
    Emits execution results in a format suitable for replay.

    This class helps E3 emit structured execution events that the core
    system can map into replay events.
    """

    def __init__(self, envelope: ActionEnvelope, action_run_id: UUID):
        self.envelope = envelope
        self.action_run_id = action_run_id
        self._events: list[dict[str, Any]] = []

    def emit_planned(self, plan_details: dict[str, Any]) -> None:
        """Emit an event when action is planned."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "planned",
                output_payload={"plan": plan_details},
            )
        )

    def emit_approval_required(self, reason: str) -> None:
        """Emit an event when approval is required."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "approval_required",
                output_payload={"reason": reason},
            )
        )

    def emit_executing(self) -> None:
        """Emit an event when execution starts."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "executing",
            )
        )

    def emit_sent(self, external_message_id: str | None = None) -> None:
        """Emit an event when message is sent."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "sent",
                output_payload={"external_message_id": external_message_id},
            )
        )

    def emit_acknowledged(self) -> None:
        """Emit an event when delivery is acknowledged."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "acknowledged",
            )
        )

    def emit_failed(self, error: str, retryable: bool = False) -> None:
        """Emit an event when execution fails."""
        status = "failed_retryable" if retryable else "failed_terminal"
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                status,
                error=error,
            )
        )

    def emit_completed(self, result: dict[str, Any]) -> None:
        """Emit an event when execution completes successfully."""
        self._events.append(
            ActionEnvelopeAdapter.create_replay_event_payload(
                self.envelope,
                self.action_run_id,
                "completed",
                output_payload=result,
            )
        )

    def get_events(self) -> list[dict[str, Any]]:
        """Get all emitted events."""
        return list(self._events)

    def clear_events(self) -> None:
        """Clear emitted events."""
        self._events.clear()
