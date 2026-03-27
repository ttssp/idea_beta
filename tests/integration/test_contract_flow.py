"""
End-to-end contract flow integration tests.

Tests the complete thread -> approval -> execution -> replay flow
using the frozen contracts from Phase 0.
"""

import pytest

from myproj.core.contracts import (
    ActionEnvelope,
    ActionExecutionMode,
    ActionTarget,
    ActorRef,
    AttentionDecision,
    AttentionDisposition,
    AuthorityGrant,
    AuthorityGrantStatus,
    ChannelKind,
    DelegationMode,
    DisclosureMode,
    DisclosurePolicy,
    DisclosurePreview,
    PrincipalKind,
    RelationshipContextRef,
    RelationshipScope,
    RiskLevel,
    RiskPosture,
    SenderStack,
    ThreadContextRef,
    ThreadScope,
)
from myproj.core.contracts.examples import (
    ACTION_ENVELOPE_EXAMPLE,
    ATTENTION_DECISION_EXAMPLE,
    AUTHORITY_GRANT_EXAMPLE,
    DISCLOSURE_POLICY_EXAMPLE,
    DISCLOSURE_PREVIEW_EXAMPLE,
    SENDER_STACK_EXAMPLE,
)


class TestEndToEndContractFlow:
    """Test the complete end-to-end flow using contracts."""

    def test_authority_grant_creation(self):
        """Phase 1: Create an authority grant."""
        grant = AUTHORITY_GRANT_EXAMPLE.model_copy(deep=True)

        # Verify grant is active and valid
        assert grant.status == AuthorityGrantStatus.ACTIVE
        assert grant.is_currently_active
        assert grant.grantor != grant.delegate
        assert grant.delegation_mode == DelegationMode.APPROVE_TO_SEND

    def test_sender_stack_construction(self):
        """Phase 2: Build a sender stack from the grant."""
        stack = SENDER_STACK_EXAMPLE.model_copy(deep=True)

        # Verify stack references the authority grant
        assert stack.authority_source == AUTHORITY_GRANT_EXAMPLE.authority_grant_id
        assert stack.owner.principal_kind == PrincipalKind.HUMAN
        assert stack.delegate is not None
        assert stack.delegate.is_agent

    def test_disclosure_preview_resolution(self):
        """Phase 3: Resolve disclosure based on context."""
        policy = DISCLOSURE_POLICY_EXAMPLE.model_copy(deep=True)
        preview = DisclosurePreview.from_policy(
            policy,
            is_external=True,
            is_sensitive_relationship=False,
            risk_level=RiskLevel.MEDIUM,
            rendered_text="Sent on behalf with delegated assistance.",
        )

        # External communication should be at least SEMI
        assert preview.resolved_mode in {DisclosureMode.SEMI, DisclosureMode.FULL}
        assert preview.requires_recipient_notice

    def test_attention_decision_generation(self):
        """Phase 4: Determine if human attention is needed."""
        decision = ATTENTION_DECISION_EXAMPLE.model_copy(deep=True)

        # Approval required should trigger human action
        assert decision.disposition == AttentionDisposition.APPROVAL_REQUIRED
        assert decision.requires_human_action
        assert decision.notify_now

    def test_action_envelope_construction(self):
        """Phase 5: Build the complete action envelope."""
        envelope = ACTION_ENVELOPE_EXAMPLE.model_copy(deep=True)

        # Envelope should contain all necessary context
        assert envelope.thread.thread_id is not None
        assert envelope.sender_stack is not None
        assert envelope.disclosure_preview is not None
        assert envelope.risk_posture is not None
        assert envelope.target is not None

        # Approval-gated flow
        assert envelope.execution_mode == ActionExecutionMode.EXECUTE_AFTER_APPROVAL
        assert envelope.risk_posture.requires_approval

    def test_round_trip_serialization(self):
        """All contracts should serialize and deserialize safely."""
        # AuthorityGrant round-trip
        grant_json = AUTHORITY_GRANT_EXAMPLE.model_dump(mode="json")
        grant_restored = AuthorityGrant.model_validate(grant_json)
        assert grant_restored.authority_grant_id == AUTHORITY_GRANT_EXAMPLE.authority_grant_id

        # SenderStack round-trip
        stack_json = SENDER_STACK_EXAMPLE.model_dump(mode="json")
        stack_restored = SenderStack.model_validate(stack_json)
        assert stack_restored.owner.principal_id == SENDER_STACK_EXAMPLE.owner.principal_id

        # DisclosurePreview round-trip
        preview_json = DISCLOSURE_PREVIEW_EXAMPLE.model_dump(mode="json")
        preview_restored = DisclosurePreview.model_validate(preview_json)
        assert preview_restored.resolved_mode == DISCLOSURE_PREVIEW_EXAMPLE.resolved_mode

        # AttentionDecision round-trip
        decision_json = ATTENTION_DECISION_EXAMPLE.model_dump(mode="json")
        decision_restored = AttentionDecision.model_validate(decision_json)
        assert decision_restored.disposition == ATTENTION_DECISION_EXAMPLE.disposition

        # ActionEnvelope round-trip
        envelope_json = ACTION_ENVELOPE_EXAMPLE.model_dump(mode="json")
        envelope_restored = ActionEnvelope.model_validate(envelope_json)
        assert envelope_restored.envelope_id == ACTION_ENVELOPE_EXAMPLE.envelope_id

    def test_complete_interview_scheduling_scenario(self):
        """End-to-end: Interview scheduling scenario from product spec."""
        # 1. Create authority grant for scheduling
        grant = AUTHORITY_GRANT_EXAMPLE.model_copy(deep=True)
        grant.allowed_actions = ["draft_message", "send_message", "propose_time"]
        grant.requires_approval_for = ["send_message"]

        # 2. Build sender stack for scheduling agent
        stack = SENDER_STACK_EXAMPLE.model_copy(deep=True)
        stack.authority_source = grant.authority_grant_id
        stack.authority_label = "candidate_scheduling_policy_v1"

        # 3. Resolve disclosure for external candidate
        policy = DISCLOSURE_POLICY_EXAMPLE.model_copy(deep=True)
        preview = DisclosurePreview.from_policy(
            policy,
            is_external=True,
            is_sensitive_relationship=False,
            risk_level=RiskLevel.MEDIUM,
            rendered_text="Sent on behalf of Alicia with scheduling assistance from her delegate agent.",
        )

        # 4. Determine attention needs (approval required)
        decision = AttentionDecision(
            target_principal_id=grant.grantor.principal_id,
            disposition=AttentionDisposition.APPROVAL_REQUIRED,
            reason_code="approval_gate",
            summary="This interview scheduling message requires human approval before send.",
            related_thread_id=ACTION_ENVELOPE_EXAMPLE.thread.thread_id,
            requires_human_action=True,
            notify_now=True,
        )

        # 5. Build action envelope
        envelope = ActionEnvelope(
            action_type="send_message",
            action_label="Send candidate scheduling proposal",
            thread=ThreadContextRef(
                thread_id=ACTION_ENVELOPE_EXAMPLE.thread.thread_id,
                objective="Coordinate final-round interview times",
                thread_status="awaiting_approval",
                participant_ids=[grant.grantor.principal_id],
            ),
            relationships=RelationshipContextRef(
                relationship_classes=["candidate"],
                is_sensitive=False,
            ),
            sender_stack=stack,
            disclosure_preview=preview,
            target=ActionTarget(
                channel=ChannelKind.EMAIL,
                recipient_handles=["candidate@example.com"],
                subject="Interview scheduling options",
            ),
            risk_posture=RiskPosture(
                risk_level=RiskLevel.MEDIUM,
                requires_approval=True,
                reason_codes=["external_send", "candidate_thread"],
                summary="External candidate communication requires human approval.",
            ),
            execution_mode=ActionExecutionMode.EXECUTE_AFTER_APPROVAL,
            approval_request_id=decision.decision_id,
            payload={
                "content": "Here are three scheduling windows that work on our side.",
                "content_type": "text/plain",
            },
        )

        # Verify the complete flow
        assert envelope.execution_mode == ActionExecutionMode.EXECUTE_AFTER_APPROVAL
        assert envelope.risk_posture.requires_approval
        assert envelope.disclosure_preview.requires_recipient_notice
        assert envelope.sender_stack.authority_source == grant.authority_grant_id
