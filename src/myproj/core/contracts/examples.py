"""Frozen examples and handoff notes for Communication OS contracts."""

from uuid import UUID

from myproj.core.contracts.actions import (
    ActionEnvelope,
    ActionExecutionMode,
    ActionTarget,
    ChannelKind,
    RelationshipContextRef,
    RiskPosture,
    ThreadContextRef,
)
from myproj.core.contracts.attention import AttentionDecision, AttentionDisposition
from myproj.core.contracts.authority import AuthorityGrant, RelationshipScope, ThreadScope
from myproj.core.contracts.common import ActorRef, DelegationMode, PrincipalKind, RiskLevel
from myproj.core.contracts.disclosure import (
    DisclosureMode,
    DisclosurePolicy,
    DisclosurePreview,
)
from myproj.core.contracts.sender_stack import SenderStack

EXAMPLE_IDS = {
    "owner": UUID("11111111-1111-1111-1111-111111111111"),
    "delegate": UUID("22222222-2222-2222-2222-222222222222"),
    "approver": UUID("33333333-3333-3333-3333-333333333333"),
    "executor": UUID("44444444-4444-4444-4444-444444444444"),
    "authority_grant": UUID("55555555-5555-5555-5555-555555555555"),
    "thread": UUID("66666666-6666-6666-6666-666666666666"),
    "relationship": UUID("77777777-7777-7777-7777-777777777777"),
    "approval_request": UUID("88888888-8888-8888-8888-888888888888"),
}


FIELD_NAMING_RULES = (
    "Use owner/delegate/author/approver/executor exactly; do not invent synonyms.",
    "Use *_id or *_ids for UUID-bearing fields and keep them stable across contracts.",
    "Use *_mode for enum-based behavioral switches such as disclosure_mode and execution_mode.",
    "Use risk_level for the resolved posture and reason_codes for machine-readable causes.",
    "Use authority_source to point at the AuthorityGrant that permitted an action.",
)


AUTHORITY_SEMANTICS_CHEAT_SHEET = {
    "owner": "The human or organization ultimately represented by the communication.",
    "delegate": "The agent acting on behalf of the owner at runtime.",
    "author": "Who actually drafted the content or prepared the action payload.",
    "approver": "The human or delegated authority that explicitly approved the action.",
    "executor": "The system or service that physically delivered or enacted the action.",
    "authority_source": "The AuthorityGrant identifier that made the delegated action legal.",
}


OWNER_REF = ActorRef(
    principal_id=EXAMPLE_IDS["owner"],
    display_name="Alicia Chen",
    principal_kind=PrincipalKind.HUMAN,
)

DELEGATE_REF = ActorRef(
    principal_id=EXAMPLE_IDS["delegate"],
    display_name="Alicia Scheduling Agent",
    principal_kind=PrincipalKind.PERSONAL_AGENT,
    is_human_controlled=False,
)

APPROVER_REF = ActorRef(
    principal_id=EXAMPLE_IDS["approver"],
    display_name="Alicia Chen",
    principal_kind=PrincipalKind.HUMAN,
)

EXECUTOR_REF = ActorRef(
    principal_id=EXAMPLE_IDS["executor"],
    display_name="Org Mail Delivery Agent",
    principal_kind=PrincipalKind.ORGANIZATION_AGENT,
    affiliation_name="Acme Talent",
    is_human_controlled=False,
)


DISCLOSURE_POLICY_EXAMPLE = DisclosurePolicy(
    policy_id=UUID("99999999-9999-9999-9999-999999999999"),
    default_mode=DisclosureMode.SEMI,
)


AUTHORITY_GRANT_EXAMPLE = AuthorityGrant(
    authority_grant_id=EXAMPLE_IDS["authority_grant"],
    grantor=OWNER_REF,
    delegate=DELEGATE_REF,
    delegation_mode=DelegationMode.APPROVE_TO_SEND,
    allowed_actions=["draft_message", "send_message", "propose_time"],
    requires_approval_for=["send_message"],
    relationship_scope=RelationshipScope(
        include_all=False,
        relationship_ids=[EXAMPLE_IDS["relationship"]],
        relationship_classes=["candidate"],
    ),
    thread_scope=ThreadScope(include_all=True),
    max_risk_level=RiskLevel.MEDIUM,
    disclosure_policy=DISCLOSURE_POLICY_EXAMPLE,
)


SENDER_STACK_EXAMPLE = SenderStack(
    owner=OWNER_REF,
    delegate=DELEGATE_REF,
    author=DELEGATE_REF,
    approver=APPROVER_REF,
    executor=EXECUTOR_REF,
    disclosure_mode=DISCLOSURE_POLICY_EXAMPLE.default_mode,
    authority_source=AUTHORITY_GRANT_EXAMPLE.authority_grant_id,
    authority_label="candidate_scheduling_policy_v1",
)


DISCLOSURE_PREVIEW_EXAMPLE = DisclosurePreview.from_policy(
    DISCLOSURE_POLICY_EXAMPLE,
    is_external=True,
    is_sensitive_relationship=False,
    risk_level=RiskLevel.MEDIUM,
    rendered_text="Sent on behalf of Alicia with scheduling assistance from her delegate agent.",
)


ATTENTION_DECISION_EXAMPLE = AttentionDecision(
    target_principal_id=EXAMPLE_IDS["owner"],
    disposition=AttentionDisposition.APPROVAL_REQUIRED,
    reason_code="approval_gate",
    summary="This interview scheduling message requires human approval before send.",
    related_thread_id=EXAMPLE_IDS["thread"],
    related_action_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    requires_human_action=True,
    notify_now=True,
)


ACTION_ENVELOPE_EXAMPLE = ActionEnvelope(
    envelope_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    action_type="send_message",
    action_label="Send candidate scheduling proposal",
    thread=ThreadContextRef(
        thread_id=EXAMPLE_IDS["thread"],
        objective="Coordinate final-round interview times",
        thread_status="awaiting_approval",
        participant_ids=[EXAMPLE_IDS["owner"], EXAMPLE_IDS["relationship"]],
        relationship_ids=[EXAMPLE_IDS["relationship"]],
    ),
    relationships=RelationshipContextRef(
        relationship_ids=[EXAMPLE_IDS["relationship"]],
        relationship_classes=["candidate"],
        is_sensitive=False,
    ),
    sender_stack=SENDER_STACK_EXAMPLE,
    disclosure_preview=DISCLOSURE_PREVIEW_EXAMPLE,
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
    approval_request_id=EXAMPLE_IDS["approval_request"],
    idempotency_key="thread-66666666-send-message-1",
    payload={
        "content": "Here are three scheduling windows that work on our side.",
        "content_type": "text/plain",
    },
)


AUTHORITY_GRANT_PAYLOAD = AUTHORITY_GRANT_EXAMPLE.model_dump(mode="json")
DISCLOSURE_POLICY_PAYLOAD = DISCLOSURE_POLICY_EXAMPLE.model_dump(mode="json")
SENDER_STACK_PAYLOAD = SENDER_STACK_EXAMPLE.model_dump(mode="json")
DISCLOSURE_PREVIEW_PAYLOAD = DISCLOSURE_PREVIEW_EXAMPLE.model_dump(mode="json")
ATTENTION_DECISION_PAYLOAD = ATTENTION_DECISION_EXAMPLE.model_dump(mode="json")
ACTION_ENVELOPE_PAYLOAD = ACTION_ENVELOPE_EXAMPLE.model_dump(mode="json")
