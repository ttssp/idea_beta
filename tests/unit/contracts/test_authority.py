"""Authority grant contract tests."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from myproj.core.contracts.authority import (
    AuthorityGrant,
    RelationshipScope,
    ThreadScope,
)
from myproj.core.contracts.common import ActorRef, DelegationMode, PrincipalKind, RiskLevel
from myproj.core.contracts.disclosure import DisclosurePolicy


def actor(name: str, kind: PrincipalKind) -> ActorRef:
    return ActorRef(principal_id=uuid4(), display_name=name, principal_kind=kind)


class TestRelationshipScope:
    def test_include_all_rejects_selectors(self):
        with pytest.raises(ValueError):
            RelationshipScope(include_all=True, relationship_classes=["candidate"])

    def test_scoped_mode_requires_selector(self):
        with pytest.raises(ValueError):
            RelationshipScope(include_all=False)


class TestThreadScope:
    def test_scoped_threads_require_ids(self):
        with pytest.raises(ValueError):
            ThreadScope(include_all=False)


class TestAuthorityGrant:
    def test_delegated_modes_require_allowed_actions(self):
        with pytest.raises(ValueError):
            AuthorityGrant(
                grantor=actor("Owner", PrincipalKind.HUMAN),
                delegate=actor("Agent", PrincipalKind.PERSONAL_AGENT),
                delegation_mode=DelegationMode.APPROVE_TO_SEND,
                disclosure_policy=DisclosurePolicy(),
            )

    def test_approval_subset_must_match_allowed_actions(self):
        with pytest.raises(ValueError):
            AuthorityGrant(
                grantor=actor("Owner", PrincipalKind.HUMAN),
                delegate=actor("Agent", PrincipalKind.PERSONAL_AGENT),
                delegation_mode=DelegationMode.BOUNDED_AUTO,
                allowed_actions=["draft_message"],
                requires_approval_for=["send_message"],
                disclosure_policy=DisclosurePolicy(),
            )

    def test_expires_at_must_follow_granted_at(self):
        now = datetime.now(UTC)
        with pytest.raises(ValueError):
            AuthorityGrant(
                grantor=actor("Owner", PrincipalKind.HUMAN),
                delegate=actor("Agent", PrincipalKind.PERSONAL_AGENT),
                delegation_mode=DelegationMode.DRAFT_FIRST,
                allowed_actions=["draft_message"],
                disclosure_policy=DisclosurePolicy(),
                granted_at=now,
                expires_at=now - timedelta(minutes=1),
            )

    def test_active_grant_reports_currently_active(self):
        grant = AuthorityGrant(
            grantor=actor("Owner", PrincipalKind.HUMAN),
            delegate=actor("Agent", PrincipalKind.PERSONAL_AGENT),
            delegation_mode=DelegationMode.DRAFT_FIRST,
            allowed_actions=["draft_message"],
            max_risk_level=RiskLevel.MEDIUM,
            disclosure_policy=DisclosurePolicy(),
        )

        assert grant.is_currently_active

