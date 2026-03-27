"""Frozen example payload tests."""

from myproj.core.contracts import (
    ACTION_ENVELOPE_PAYLOAD,
    ATTENTION_DECISION_PAYLOAD,
    AUTHORITY_GRANT_PAYLOAD,
    AUTHORITY_SEMANTICS_CHEAT_SHEET,
    DISCLOSURE_POLICY_PAYLOAD,
    FIELD_NAMING_RULES,
    SENDER_STACK_PAYLOAD,
    ActionEnvelope,
    AttentionDecision,
    AuthorityGrant,
    DisclosurePolicy,
    SenderStack,
)


class TestContractExamples:
    def test_examples_round_trip(self):
        assert AuthorityGrant.model_validate(AUTHORITY_GRANT_PAYLOAD).delegate.display_name
        assert DisclosurePolicy.model_validate(DISCLOSURE_POLICY_PAYLOAD).default_mode
        assert SenderStack.model_validate(SENDER_STACK_PAYLOAD).authority_source
        assert AttentionDecision.model_validate(ATTENTION_DECISION_PAYLOAD).summary
        assert ActionEnvelope.model_validate(ACTION_ENVELOPE_PAYLOAD).action_type == "send_message"

    def test_handoff_notes_cover_sender_roles(self):
        assert len(FIELD_NAMING_RULES) >= 5
        assert {"owner", "delegate", "author", "approver", "executor", "authority_source"} <= set(
            AUTHORITY_SEMANTICS_CHEAT_SHEET
        )
